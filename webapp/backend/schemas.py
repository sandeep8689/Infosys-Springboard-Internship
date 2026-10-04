from pydantic import BaseModel, Field


class PredictRequest(BaseModel):
    patient_name: str = Field(default="Patient", min_length=1, max_length=120)
    age: int | None = Field(default=None, ge=0, le=120)
    symptoms: list[str] = Field(min_length=1)


class TopPrediction(BaseModel):
    disease: str
    confidence: float


class RecommendationBlock(BaseModel):
    preventive_care: list[str]
    lifestyle_advice: list[str]
    follow_up_guidance: list[str]
    llm_summary: str | None = None


class PredictResponse(BaseModel):
    consultation_id: int
    predicted_disease: str
    confidence: float
    risk_level: str
    severity_score: float
    top_predictions: list[TopPrediction]
    recommendations: RecommendationBlock


class ReportExportRequest(BaseModel):
    """Generate PDF/Excel without relying on SQLite (reliable on cloud deploy)."""
    patient_name: str = "Patient"
    age: int | None = None
    consultation_id: int | None = None
    predicted_disease: str
    confidence: float
    risk_level: str
    severity_score: float
    symptoms: list[str]
    recommendations: RecommendationBlock


class AnalyticsSummary(BaseModel):
    total_consultations: int
    disease_counts: dict[str, int]
    risk_distribution: dict[str, int]
    symptom_trends: list[dict]
    model_ready: bool
