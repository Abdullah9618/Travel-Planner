"""Database-backed persistence for app datasets.

This module stores JSON-like datasets inside a SQL database via SQLAlchemy.
It supports MySQL (via pymysql) or SQLite fallback through DATABASE_URL.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any, Optional

from sqlalchemy import Column, String, Text, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()


class AppData(Base):
    __tablename__ = "app_data"

    key = Column(String(120), primary_key=True)
    payload = Column(Text, nullable=False)


@dataclass
class Persistence:
    engine: Any
    SessionLocal: Any


def get_dataset_key(filepath: str) -> str:
    return os.path.splitext(os.path.basename(filepath))[0]


def build_persistence(base_dir: str) -> Persistence:
    database_url = os.getenv("DATABASE_URL", f"sqlite:///{os.path.join(base_dir, 'travelbuddy.db')}")
    engine = create_engine(database_url, future=True)
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
    return Persistence(engine=engine, SessionLocal=SessionLocal)


def db_load_json(persistence: Persistence, filepath: str) -> Optional[Any]:
    dataset_key = get_dataset_key(filepath)
    with persistence.SessionLocal() as session:
        row = session.get(AppData, dataset_key)
        if not row:
            return None
        try:
            return json.loads(row.payload)
        except json.JSONDecodeError:
            return None


def db_save_json(persistence: Persistence, filepath: str, data: Any) -> None:
    dataset_key = get_dataset_key(filepath)
    payload = json.dumps(data, ensure_ascii=False)
    with persistence.SessionLocal() as session:
        row = session.get(AppData, dataset_key)
        if row:
            row.payload = payload
        else:
            row = AppData(key=dataset_key, payload=payload)
            session.add(row)
        session.commit()


def seed_from_file_if_missing(persistence: Persistence, filepath: str) -> None:
    existing = db_load_json(persistence, filepath)
    if existing is not None:
        return

    if not os.path.exists(filepath):
        return

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            parsed = json.load(f)
    except (json.JSONDecodeError, OSError):
        return

    db_save_json(persistence, filepath, parsed)
