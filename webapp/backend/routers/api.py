from fastapi import APIRouter, HTTPException
from fastapi.responses import Response

from backend import database
from backend.schemas import AnalyticsSummary, PredictRequest, PredictResponse, RecommendationBlock, TopPrediction
from backend.services.analytics import build_analytics_summary
from backend.services.llm import enhance_recommendations_async
from backend.services.ml import artifacts_ready, get_symptom_list, predict_from_symptoms
from backend.services.recommendations import build_recommendations
from backend.services.reports import build_health_report_excel, build_health_report_pdf
from backend.services.risk import compute_risk_assessment

router = APIRouter(prefix="/api")


@router.get("/health")
async def health():
    return {"status": "ok", "model_ready": artifacts_ready()}


@router.get("/symptoms")
async def symptoms():
    if not artifacts_ready():
        raise HTTPException(
            503,
            detail="Model not trained. Run python scripts/train_model.py after adding the CSV to webapp/data/",
        )
    return {"symptoms": get_symptom_list()}


@router.post("/predict", response_model=PredictResponse)
async def predict(body: PredictRequest):
    if not artifacts_ready():
        raise HTTPException(503, detail="Model artifacts missing. Train the model first.")

    valid = {s.lower() for s in get_symptom_list()}
    unknown = [s for s in body.symptoms if s.lower() not in valid]
    if unknown:
        raise HTTPException(400, detail=f"Unknown symptoms: {unknown[:5]}")

    disease, confidence, top = predict_from_symptoms(body.symptoms)
    assessment = compute_risk_assessment(disease, confidence, len(body.symptoms), body.age)
    risk = str(assessment["risk_level"])
    severity = float(assessment["severity_score"])
    rec = build_recommendations(disease, risk, body.symptoms)
    rec = await enhance_recommendations_async(disease, risk, rec)
    rec_to_store = {**rec, "severity_score": severity}

    cid = await database.save_consultation(
        patient_name=body.patient_name,
        age=body.age,
        symptoms=body.symptoms,
        predicted_disease=disease,
        confidence=confidence,
        risk_level=risk,
        severity_score=severity,
        recommendations=rec_to_store,
    )

    return PredictResponse(
        consultation_id=cid,
        predicted_disease=disease,
        confidence=confidence,
        risk_level=risk,
        severity_score=severity,
        top_predictions=[TopPrediction(disease=d, confidence=c) for d, c in top],
        recommendations=RecommendationBlock(**rec),
    )


@router.get("/analytics", response_model=AnalyticsSummary)
async def analytics():
    data = await build_analytics_summary()
    return AnalyticsSummary(
        total_consultations=data["total_consultations"],
        disease_counts=data["disease_counts"],
        risk_distribution=data["risk_distribution"],
        symptom_trends=data["symptom_trends"],
        model_ready=data["model_ready"],
    )


@router.get("/analytics/full")
async def analytics_full():
    return await build_analytics_summary()


@router.get("/reports/{consultation_id}/pdf")
async def report_pdf(consultation_id: int):
    try:
        content = await build_health_report_pdf(consultation_id)
    except ValueError as e:
        msg = str(e)
        code = 404 if "not found" in msg.lower() else 500
        raise HTTPException(code, detail=msg) from e
    except Exception as e:
        raise HTTPException(500, detail=f"PDF build error: {type(e).__name__}: {e}") from e
    filename = f"MedAssist_report_{consultation_id}.pdf"
    return Response(
        content=content,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Content-Length": str(len(content)),
            "Cache-Control": "no-store",
        },
    )


@router.get("/reports/{consultation_id}/excel")
async def report_excel(consultation_id: int):
    try:
        content = await build_health_report_excel(consultation_id)
    except ValueError as e:
        raise HTTPException(404, detail=str(e)) from e
    return Response(
        content=content,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="health_report_{consultation_id}.xlsx"'},
    )
