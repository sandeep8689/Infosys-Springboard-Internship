import json
from datetime import datetime, timezone

import aiosqlite

from backend.config import settings


async def _migrate(db: aiosqlite.Connection) -> None:
    cursor = await db.execute("PRAGMA table_info(consultations)")
    rows = await cursor.fetchall()
    columns = {row[1] for row in rows}
    if "severity_score" not in columns:
        await db.execute(
            "ALTER TABLE consultations ADD COLUMN severity_score REAL DEFAULT 0"
        )


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
                severity_score REAL DEFAULT 0,
                recommendations_json TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        await _migrate(db)
        await db.commit()


async def save_consultation(
    *,
    patient_name: str,
    age: int | None,
    symptoms: list[str],
    predicted_disease: str,
    confidence: float,
    risk_level: str,
    severity_score: float,
    recommendations: dict,
) -> int:
    async with aiosqlite.connect(settings.database_path) as db:
        await _migrate(db)
        cursor = await db.execute(
            """
            INSERT INTO consultations
            (patient_name, age, symptoms_json, predicted_disease, confidence,
             risk_level, severity_score, recommendations_json, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                patient_name,
                age,
                json.dumps(symptoms),
                predicted_disease,
                confidence,
                risk_level,
                severity_score,
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
                   confidence, risk_level, severity_score, recommendations_json, created_at
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
