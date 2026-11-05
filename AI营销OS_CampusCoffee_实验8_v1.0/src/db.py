"""SQLite 初始化与可追溯数据落库。"""

from __future__ import annotations

import csv
import json
import sqlite3
from pathlib import Path
from typing import Iterable


SCHEMA = """
CREATE TABLE IF NOT EXISTS runs (
  run_id TEXT PRIMARY KEY,
  version TEXT NOT NULL,
  started_at TEXT NOT NULL,
  status TEXT NOT NULL,
  input_manifest TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS brand_profile (
  brand TEXT PRIMARY KEY,
  version TEXT NOT NULL,
  profile_json TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS consumer_feedback (
  feedback_id TEXT PRIMARY KEY,
  segment TEXT, topic TEXT, sentiment TEXT, rating REAL,
  evidence_quote TEXT, source TEXT, consent_status TEXT, is_mock INTEGER
);
CREATE TABLE IF NOT EXISTS competitor_snapshot (
  competitor TEXT PRIMARY KEY, category TEXT, availability_score REAL,
  price_index REAL, brand_heat_index REAL, content_coverage_pct REAL,
  student_fit_score REAL, source TEXT, is_mock INTEGER
);
CREATE TABLE IF NOT EXISTS experiment_result (
  user_id TEXT PRIMARY KEY, variant TEXT, clicked_coupon INTEGER,
  purchased INTEGER, order_value_rmb REAL, feedback_score REAL,
  trial_intent REAL, purchase_intent REAL, brand_fit REAL,
  consent_status TEXT, is_mock INTEGER
);
CREATE TABLE IF NOT EXISTS evidence_trace (
  evidence_id TEXT PRIMARY KEY, module TEXT NOT NULL,
  source TEXT NOT NULL, claim TEXT NOT NULL, verification_status TEXT NOT NULL
);
"""


def _bool(value: str | bool | int) -> int:
    return int(value is True or str(value).lower() in {"1", "true", "yes"})


def init_db(
    db_path: Path,
    brand: dict,
    feedback: Iterable[dict[str, str]],
    competitors: Iterable[dict[str, str]],
    ab_rows: Iterable[dict[str, str]],
    questionnaire: dict[str, dict[str, str]],
    run_id: str,
    started_at: str,
) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    try:
        conn.executescript(SCHEMA)
        conn.execute(
            "INSERT OR REPLACE INTO runs VALUES (?, ?, ?, ?, ?)",
            (run_id, "v1.0", started_at, "success", json.dumps({"brand": brand["brand"]}, ensure_ascii=False)),
        )
        conn.execute(
            "INSERT OR REPLACE INTO brand_profile VALUES (?, ?, ?)",
            (brand["brand"], brand["version"], json.dumps(brand, ensure_ascii=False)),
        )
        conn.executemany(
            "INSERT OR REPLACE INTO consumer_feedback VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            [
                (r["feedback_id"], r["segment"], r["topic"], r["sentiment"], float(r["rating"]), r["evidence_quote"], r["source"], r["consent_status"], _bool(r["is_mock"]))
                for r in feedback
            ],
        )
        conn.executemany(
            "INSERT OR REPLACE INTO competitor_snapshot VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            [
                (r["competitor"], r["category"], float(r["availability_score"]), float(r["price_index"]), float(r["brand_heat_index"]), float(r["content_coverage_pct"]), float(r["student_fit_score"]), r["source"], _bool(r["is_mock"]))
                for r in competitors
            ],
        )
        questionnaire_by_user = questionnaire
        experiment_values = []
        for row in ab_rows:
            q = questionnaire_by_user.get(row["user_id"], {})
            experiment_values.append(
                (row["user_id"], row["variant"], int(row["clicked_coupon"]), int(row["purchased"]), float(row["order_value_rmb"]), float(row["feedback_score"]), float(q.get("trial_intent_1_5", 0)), float(q.get("purchase_intent_1_5", 0)), float(q.get("brand_fit_1_5", 0)), row["consent_status"], _bool(row["is_mock"]))
            )
        conn.executemany("INSERT OR REPLACE INTO experiment_result VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", experiment_values)
        conn.commit()
    finally:
        conn.close()


def count_rows(db_path: Path, table: str) -> int:
    if table not in {"runs", "brand_profile", "consumer_feedback", "competitor_snapshot", "experiment_result", "evidence_trace"}:
        raise ValueError("unsupported table")
    conn = sqlite3.connect(db_path)
    try:
        return int(conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0])
    finally:
        conn.close()
