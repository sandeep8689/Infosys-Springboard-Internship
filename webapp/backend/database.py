import json
from datetime import datetime, timezone
from pathlib import Path

import aiosqlite

from backend.config import settings


async def init_db() -> None:
    settings.database_path.parent.mkdir(parents=True, exist_ok=True)
    async with aiosqlite.connect(settings.database_path) as db:
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS consultations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_name TEXT NOT NULL,
                age INTEGER,
                symptoms_json TEXT NOT NULL,
                predicted_disease TEXT NOT NULL,
                confidence REAL NOT NULL,
                risk_level TEXT NOT NULL,
                recommendations_json TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        await db.commit()


async def save_consultation(
    *,
    patient_name: str,
    age: int | None,
    symptoms: list[str],
    predicted_disease: str,
    confidence: float,
    risk_level: str,
    recommendations: dict,
) -> int:
    async with aiosqlite.connect(settings.database_path) as db:
        cursor = await db.execute(
            """
            INSERT INTO consultations
            (patient_name, age, symptoms_json, predicted_disease, confidence,
             risk_level, recommendations_json, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                patient_name,
                age,
                json.dumps(symptoms),
                predicted_disease,
                confidence,
                risk_level,
                json.dumps(recommendations),
                datetime.now(timezone.utc).isoformat(),
            ),
        )
        await db.commit()
        return int(cursor.lastrowid)


async def list_consultations(limit: int = 500) -> list[dict]:
    async with aiosqlite.connect(settings.database_path) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            """
            SELECT id, patient_name, age, symptoms_json, predicted_disease,
                   confidence, risk_level, recommendations_json, created_at
            FROM consultations
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        )
        rows = await cursor.fetchall()
    return [dict(row) for row in rows]


async def get_consultation(consultation_id: int) -> dict | None:
    async with aiosqlite.connect(settings.database_path) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM consultations WHERE id = ?",
            (consultation_id,),
        )
        row = await cursor.fetchone()
    return dict(row) if row else None
