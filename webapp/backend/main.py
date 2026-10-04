from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from backend.database import init_db
from backend.routers.api import router
from backend.services.ml import load_artifacts


@asynccontextmanager
async def lifespan(_app: FastAPI):
    await init_db()
    load_artifacts()
    yield


app = FastAPI(
    title="AI Medical Symptom Analysis",
    description="Prediction, risk, recommendations, reports, and analytics (Week 2)",
    lifespan=lifespan,
)
app.include_router(router)

frontend = Path(__file__).resolve().parents[1] / "frontend"
app.mount("/", StaticFiles(directory=frontend, html=True), name="frontend")
