import json
import re
from io import BytesIO

from fpdf import FPDF
from openpyxl import Workbook

from backend.database import get_consultation


def _safe_text(text: str) -> str:
    """FPDF core fonts are Latin-1; strip/replace unsupported characters."""
    if not text:
        return ""
    text = text.replace("\u2013", "-").replace("\u2014", "-").replace("\u2019", "'")
    text = text.encode("latin-1", errors="replace").decode("latin-1")
    return re.sub(r"[^\x00-\xff]", "?", text)


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


class MedAssistPDF(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 14)
        self.set_text_color(0, 120, 140)
        self.cell(0, 8, "MedAssist", ln=True)
        self.set_font("Helvetica", "", 9)
        self.set_text_color(80, 80, 80)
        self.cell(0, 5, "AI Medical Symptom Analysis - Health Summary Report", ln=True)
        self.ln(3)


async def build_health_report_pdf(consultation_id: int) -> bytes:
    row = await get_consultation(consultation_id)
    if not row:
        raise ValueError("Consultation not found")
    data = _parse_row(row)

    pdf = MedAssistPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_text_color(0, 0, 0)

    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Patient information", ln=True)
    pdf.set_font("Helvetica", size=10)
    pdf.multi_cell(
        0,
        6,
        _safe_text(
            f"Name: {data['patient_name']}\n"
            f"Age: {data['age'] or 'N/A'}\n"
            f"Consultation ID: {data['id']}\n"
            f"Generated (UTC): {data['created_at']}"
        ),
    )
    pdf.ln(3)

    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Prediction & risk", ln=True)
    pdf.set_font("Helvetica", size=10)
    pdf.multi_cell(
        0,
        6,
        _safe_text(
            f"Disease: {data['predicted_disease']}\n"
            f"Confidence: {data['confidence']:.1%}\n"
            f"Risk level: {data['risk_level']}"
        ),
    )
    pdf.ln(2)

    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Symptoms reported", ln=True)
    pdf.set_font("Helvetica", size=10)
    pdf.multi_cell(0, 6, _safe_text(", ".join(data["symptoms"])))

    rec = data["recommendations"]
    for title, key in [
        ("Preventive care", "preventive_care"),
        ("Lifestyle advice", "lifestyle_advice"),
        ("Follow-up guidance", "follow_up_guidance"),
    ]:
        pdf.ln(3)
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(0, 7, title, ln=True)
        pdf.set_font("Helvetica", size=10)
        for item in rec.get(key, []):
            pdf.multi_cell(0, 5, _safe_text(f"  - {item}"))

    if rec.get("llm_summary"):
        pdf.ln(3)
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(0, 7, "Additional notes", ln=True)
        pdf.set_font("Helvetica", size=10)
        pdf.multi_cell(0, 5, _safe_text(rec["llm_summary"]))

    pdf.ln(5)
    pdf.set_font("Helvetica", "I", 8)
    pdf.multi_cell(
        0,
        4,
        _safe_text(
            "Disclaimer: MedAssist is for educational use only. "
            "Not a substitute for professional medical advice, diagnosis, or treatment."
        ),
    )

    raw = pdf.output(dest="S")
    if isinstance(raw, (bytes, bytearray)):
        data = bytes(raw)
    else:
        data = str(raw).encode("latin-1", errors="replace")
    if not data.startswith(b"%PDF"):
        raise ValueError("PDF generation failed")
    return data


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
