import json
from io import BytesIO
from pathlib import Path

from fpdf import FPDF
from openpyxl import Workbook

from backend.database import get_consultation


def _parse_row(row: dict) -> dict:
    symptoms = json.loads(row["symptoms_json"])
    rec = json.loads(row["recommendations_json"])
    return {
        "id": row["id"],
        "patient_name": row["patient_name"],
        "age": row["age"],
        "symptoms": symptoms,
        "predicted_disease": row["predicted_disease"],
        "confidence": row["confidence"],
        "risk_level": row["risk_level"],
        "recommendations": rec,
        "created_at": row["created_at"],
    }


async def build_health_report_pdf(consultation_id: int) -> bytes:
    row = await get_consultation(consultation_id)
    if not row:
        raise ValueError("Consultation not found")
    data = _parse_row(row)

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "Patient Health Summary Report", ln=True)
    pdf.set_font("Helvetica", size=11)
    pdf.ln(4)
    pdf.multi_cell(
        0,
        6,
        f"Patient: {data['patient_name']}  |  Age: {data['age'] or 'N/A'}  |  ID: {data['id']}",
    )
    pdf.multi_cell(0, 6, f"Generated (UTC): {data['created_at']}")
    pdf.ln(4)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Prediction", ln=True)
    pdf.set_font("Helvetica", size=11)
    pdf.multi_cell(
        0,
        6,
        f"Disease: {data['predicted_disease']}\n"
        f"Confidence: {data['confidence']:.1%}\n"
        f"Risk level: {data['risk_level']}",
    )
    pdf.ln(2)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Symptoms reported", ln=True)
    pdf.set_font("Helvetica", size=11)
    pdf.multi_cell(0, 6, ", ".join(data["symptoms"]))
    rec = data["recommendations"]
    for title, key in [
        ("Preventive care", "preventive_care"),
        ("Lifestyle advice", "lifestyle_advice"),
        ("Follow-up guidance", "follow_up_guidance"),
    ]:
        pdf.ln(2)
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 8, title, ln=True)
        pdf.set_font("Helvetica", size=11)
        for item in rec.get(key, []):
            pdf.multi_cell(0, 6, f"- {item}")
    if rec.get("llm_summary"):
        pdf.ln(2)
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 8, "Additional notes", ln=True)
        pdf.set_font("Helvetica", size=11)
        pdf.multi_cell(0, 6, rec["llm_summary"])

    pdf.ln(6)
    pdf.set_font("Helvetica", "I", 9)
    pdf.multi_cell(
        0,
        5,
        "Disclaimer: For educational use only. Not a substitute for professional medical advice.",
    )
    out = pdf.output()
    return out if isinstance(out, bytes) else out.encode("latin-1")


async def build_health_report_excel(consultation_id: int) -> bytes:
    row = await get_consultation(consultation_id)
    if not row:
        raise ValueError("Consultation not found")
    data = _parse_row(row)

    wb = Workbook()
    ws = wb.active
    ws.title = "Health Report"
    ws.append(["Field", "Value"])
    ws.append(["Consultation ID", data["id"]])
    ws.append(["Patient", data["patient_name"]])
    ws.append(["Age", data["age"]])
    ws.append(["Predicted disease", data["predicted_disease"]])
    ws.append(["Confidence", round(data["confidence"], 4)])
    ws.append(["Risk level", data["risk_level"]])
    ws.append(["Symptoms", ", ".join(data["symptoms"])])
    ws.append([])
    rec = data["recommendations"]
    for section in ("preventive_care", "lifestyle_advice", "follow_up_guidance"):
        ws.append([section.replace("_", " ").title()])
        for item in rec.get(section, []):
            ws.append(["", item])
        ws.append([])

    buf = BytesIO()
    wb.save(buf)
    return buf.getvalue()
