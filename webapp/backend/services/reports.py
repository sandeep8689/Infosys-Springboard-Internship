import json
import re
from datetime import datetime, timezone
from io import BytesIO

from fpdf import FPDF
from openpyxl import Workbook

from backend.database import get_consultation


def _safe_text(text: str) -> str:
    if not text:
        return ""
    text = str(text)
    text = text.replace("\u2013", "-").replace("\u2014", "-").replace("\u2019", "'")
    text = text.encode("latin-1", errors="replace").decode("latin-1")
    return re.sub(r"[^\x00-\xff]", "?", text)


def _parse_row(row: dict) -> dict:
    symptoms = json.loads(row["symptoms_json"])
    rec_raw = row["recommendations_json"]
    rec = json.loads(rec_raw) if isinstance(rec_raw, str) else rec_raw
    if not isinstance(rec, dict):
        rec = {}
    severity = row.get("severity_score")
    if severity is None:
        severity = rec.get("severity_score")
    return {
        "id": row["id"],
        "patient_name": row["patient_name"],
        "age": row["age"],
        "symptoms": symptoms,
        "predicted_disease": row["predicted_disease"],
        "confidence": float(row["confidence"]),
        "risk_level": row["risk_level"],
        "severity_score": float(severity) if severity is not None else 0.0,
        "recommendations": rec,
        "created_at": row.get("created_at") or datetime.now(timezone.utc).isoformat(),
    }


def _pdf_bytes(pdf: FPDF) -> bytes:
    """Return raw PDF bytes (compatible with fpdf2 on Linux/Docker)."""
    result = pdf.output()
    if isinstance(result, bytearray):
        data = bytes(result)
    elif isinstance(result, bytes):
        data = result
    elif isinstance(result, str):
        data = result.encode("latin-1", errors="replace")
    else:
        buffer = BytesIO()
        pdf.output(buffer)
        data = buffer.getvalue()
    if not data.startswith(b"%PDF"):
        raise ValueError("Invalid PDF document generated")
    return data


def build_pdf_from_data(data: dict) -> bytes:
    """Build PDF from a plain dict (no database required)."""
    pdf = FPDF(format="A4")
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    pdf.set_font("Helvetica", "B", 16)
    pdf.set_text_color(0, 128, 128)
    pdf.cell(0, 10, "MedAssist", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(60, 60, 60)
    pdf.cell(
        0,
        6,
        _safe_text("AI Medical Symptom Analysis - Health Summary Report"),
        new_x="LMARGIN",
        new_y="NEXT",
    )
    pdf.ln(4)
    pdf.set_text_color(0, 0, 0)

    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 7, "Patient information", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    age_txt = str(data["age"]) if data.get("age") is not None else "N/A"
    cid = data.get("id") or data.get("consultation_id") or "N/A"
    pdf.multi_cell(
        0,
        5,
        _safe_text(
            f"Name: {data.get('patient_name', 'Patient')}\n"
            f"Age: {age_txt}\n"
            f"Consultation ID: {cid}\n"
            f"Generated (UTC): {data.get('created_at', datetime.now(timezone.utc).isoformat())}"
        ),
    )
    pdf.ln(2)

    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 7, "Prediction, risk and severity", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    sev = float(data.get("severity_score") or 0)
    conf = float(data.get("confidence") or 0)
    pdf.multi_cell(
        0,
        5,
        _safe_text(
            f"Disease: {data.get('predicted_disease', 'Unknown')}\n"
            f"Confidence: {conf:.1%}\n"
            f"Risk level: {data.get('risk_level', 'N/A')}\n"
            f"Severity score: {sev:.1f} / 100"
        ),
    )
    pdf.ln(2)

    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 7, "Symptoms reported", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    symptoms = data.get("symptoms") or []
    pdf.multi_cell(0, 5, _safe_text(", ".join(symptoms) if symptoms else "None listed"))
    pdf.ln(2)

    rec = data.get("recommendations") or {}
    if isinstance(rec, dict) and hasattr(rec, "model_dump"):
        rec = rec.model_dump()

    for title, key in [
        ("Preventive care", "preventive_care"),
        ("Lifestyle advice", "lifestyle_advice"),
        ("Follow-up guidance", "follow_up_guidance"),
    ]:
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(0, 7, title, new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 10)
        items = rec.get(key) or []
        if not items:
            pdf.multi_cell(0, 5, _safe_text("  - No items recorded."))
        for item in items:
            pdf.multi_cell(0, 5, _safe_text(f"  - {item}"))

    llm = rec.get("llm_summary")
    if llm:
        pdf.ln(2)
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(0, 7, "Additional notes", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 10)
        pdf.multi_cell(0, 5, _safe_text(str(llm)))

    pdf.ln(4)
    pdf.set_font("Helvetica", "I", 8)
    pdf.multi_cell(
        0,
        4,
        _safe_text(
            "Disclaimer: MedAssist is for educational use only. "
            "Not a substitute for professional medical advice."
        ),
    )

    return _pdf_bytes(pdf)


async def build_health_report_pdf(consultation_id: int) -> bytes:
    row = await get_consultation(consultation_id)
    if not row:
        raise ValueError("Consultation not found")
    data = _parse_row(row)
    return build_pdf_from_data(data)


async def build_health_report_excel(consultation_id: int) -> bytes:
    row = await get_consultation(consultation_id)
    if not row:
        raise ValueError("Consultation not found")
    data = _parse_row(row)

    wb = Workbook()
    ws = wb.active
    ws.title = "MedAssist Report"
    ws.append(["MedAssist - Health Summary"])
    ws.append(["Field", "Value"])
    ws.append(["Consultation ID", data["id"]])
    ws.append(["Patient", data["patient_name"]])
    ws.append(["Age", data["age"]])
    ws.append(["Predicted disease", data["predicted_disease"]])
    ws.append(["Confidence", round(data["confidence"], 4)])
    ws.append(["Risk level", data["risk_level"]])
    ws.append(["Severity score (0-100)", data["severity_score"]])
    ws.append(["Symptoms", ", ".join(data["symptoms"])])
    ws.append([])
    rec = data["recommendations"]
    for section in ("preventive_care", "lifestyle_advice", "follow_up_guidance"):
        ws.append([section.replace("_", " ").title()])
        for item in rec.get(section, []) or []:
            ws.append(["", item])
        ws.append([])

    buf = BytesIO()
    wb.save(buf)
    return buf.getvalue()
