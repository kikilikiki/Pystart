"""Base de donnees de progression (SQLite).

Concept Python illustre : le module `sqlite3` de la bibliotheque standard.
SQLite est une base de donnees complete rangee dans un seul fichier. Pas de
serveur a installer : parfait pour une application desktop hors ligne.

Concept illustre : les *migrations*. Le schema de la base peut evoluer entre
deux versions de Pystart. On garde un numero `schema_version` et on applique
les changements un par un. Ainsi les donnees existantes ne sont jamais
perdues (Database v1 -> migration -> Database v2).
"""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from app.core import paths

# Version courante du schema. On l'incremente a chaque migration.
SCHEMA_VERSION = 1


@dataclass
class Profile:
    id: int
    name: str
    level: str
    created_at: str


@dataclass
class CourseStats:
    course_id: str
    exercises_done: int
    total_exercises: int
    completed: bool

    @property
    def percent(self) -> int:
        if self.total_exercises == 0:
            return 100 if self.completed else 0
        return round(100 * self.exercises_done / self.total_exercises)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class ProgressStore:
    """Acces a la base de progression. Une instance = une connexion."""

    def __init__(self, db_path: Path | None = None) -> None:
        self.db_path = db_path or paths.database_path()
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(self.db_path)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA foreign_keys = ON")
        self._migrate()

    # --- Cycle de vie -----------------------------------------------------
    def close(self) -> None:
        self._conn.close()

    @contextmanager
    def _tx(self):
        try:
            yield self._conn
            self._conn.commit()
        except Exception:
            self._conn.rollback()
            raise

    # --- Migrations -----------------------------------------------------
    def _migrate(self) -> None:
        current = self._conn.execute("PRAGMA user_version").fetchone()[0]
        if current >= SCHEMA_VERSION:
            return
        with self._tx() as conn:
            if current < 1:
                self._migration_1(conn)
            conn.execute(f"PRAGMA user_version = {SCHEMA_VERSION}")

    @staticmethod
    def _migration_1(conn: sqlite3.Connection) -> None:
        """Schema initial (v1)."""
        conn.executescript(
            """
            CREATE TABLE profiles (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                name        TEXT NOT NULL,
                level       TEXT NOT NULL DEFAULT 'debutant',
                created_at  TEXT NOT NULL
            );

            CREATE TABLE exercise_progress (
                profile_id   INTEGER NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
                exercise_id  TEXT NOT NULL,
                course_id    TEXT NOT NULL,
                status       TEXT NOT NULL DEFAULT 'seen',  -- seen | passed
                attempts     INTEGER NOT NULL DEFAULT 0,
                hints_used   INTEGER NOT NULL DEFAULT 0,
                updated_at   TEXT NOT NULL,
                PRIMARY KEY (profile_id, exercise_id)
            );

            CREATE TABLE course_completion (
                profile_id  INTEGER NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
                course_id   TEXT NOT NULL,
                completed_at TEXT NOT NULL,
                PRIMARY KEY (profile_id, course_id)
            );

            CREATE TABLE activity_log (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                profile_id  INTEGER NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
                kind        TEXT NOT NULL,
                detail      TEXT NOT NULL DEFAULT '',
                at          TEXT NOT NULL
            );
            """
        )

    # --- Profils -------------------------------------------------------
    def create_profile(self, name: str, level: str = "debutant") -> Profile:
        with self._tx() as conn:
            cursor = conn.execute(
                "INSERT INTO profiles (name, level, created_at) VALUES (?, ?, ?)",
                (name.strip() or "Moi", level, _now()),
            )
            profile_id = int(cursor.lastrowid)
        return self.get_profile(profile_id)

    def get_profile(self, profile_id: int) -> Profile:
        row = self._conn.execute(
            "SELECT * FROM profiles WHERE id = ?", (profile_id,)
        ).fetchone()
        if row is None:
            raise KeyError(f"Profil introuvable : {profile_id}")
        return Profile(row["id"], row["name"], row["level"], row["created_at"])

    def list_profiles(self) -> list[Profile]:
        rows = self._conn.execute("SELECT * FROM profiles ORDER BY id").fetchall()
        return [Profile(r["id"], r["name"], r["level"], r["created_at"]) for r in rows]

    def ensure_default_profile(self) -> Profile:
        """Renvoie le premier profil, en en creant un si la base est vide."""
        profiles = self.list_profiles()
        return profiles[0] if profiles else self.create_profile("Moi")

    # --- Progression des exercices -----------------------------------
    def mark_exercise_seen(self, profile_id: int, exercise_id: str, course_id: str) -> None:
        with self._tx() as conn:
            conn.execute(
                """
                INSERT INTO exercise_progress
                    (profile_id, exercise_id, course_id, status, updated_at)
                VALUES (?, ?, ?, 'seen', ?)
                ON CONFLICT(profile_id, exercise_id) DO NOTHING
                """,
                (profile_id, exercise_id, course_id, _now()),
            )

    def record_attempt(
        self, profile_id: int, exercise_id: str, course_id: str, *, passed: bool
    ) -> None:
        status = "passed" if passed else "seen"
        with self._tx() as conn:
            conn.execute(
                """
                INSERT INTO exercise_progress
                    (profile_id, exercise_id, course_id, status, attempts, updated_at)
                VALUES (?, ?, ?, ?, 1, ?)
                ON CONFLICT(profile_id, exercise_id) DO UPDATE SET
                    attempts = attempts + 1,
                    status = CASE WHEN exercise_progress.status = 'passed'
                                  THEN 'passed' ELSE excluded.status END,
                    updated_at = excluded.updated_at
                """,
                (profile_id, exercise_id, course_id, status, _now()),
            )
            conn.execute(
                "INSERT INTO activity_log (profile_id, kind, detail, at) VALUES (?, ?, ?, ?)",
                (profile_id, "attempt", f"{exercise_id}:{'ok' if passed else 'ko'}", _now()),
            )

    def record_hint_used(self, profile_id: int, exercise_id: str, course_id: str) -> None:
        with self._tx() as conn:
            conn.execute(
                """
                INSERT INTO exercise_progress
                    (profile_id, exercise_id, course_id, hints_used, updated_at)
                VALUES (?, ?, ?, 1, ?)
                ON CONFLICT(profile_id, exercise_id) DO UPDATE SET
                    hints_used = exercise_progress.hints_used + 1,
                    updated_at = excluded.updated_at
                """,
                (profile_id, exercise_id, course_id, _now()),
            )

    def is_exercise_passed(self, profile_id: int, exercise_id: str) -> bool:
        row = self._conn.execute(
            "SELECT status FROM exercise_progress WHERE profile_id = ? AND exercise_id = ?",
            (profile_id, exercise_id),
        ).fetchone()
        return bool(row and row["status"] == "passed")

    def passed_exercise_ids(self, profile_id: int) -> set[str]:
        rows = self._conn.execute(
            "SELECT exercise_id FROM exercise_progress WHERE profile_id = ? AND status = 'passed'",
            (profile_id,),
        ).fetchall()
        return {r["exercise_id"] for r in rows}

    # --- Cours -------------------------------------------------------
    def course_stats(
        self, profile_id: int, course_id: str, total_exercises: int
    ) -> CourseStats:
        row = self._conn.execute(
            """
            SELECT COUNT(*) AS done FROM exercise_progress
            WHERE profile_id = ? AND course_id = ? AND status = 'passed'
            """,
            (profile_id, course_id),
        ).fetchone()
        done = int(row["done"])
        completed = total_exercises > 0 and done >= total_exercises
        if completed:
            self._mark_course_completed(profile_id, course_id)
        return CourseStats(course_id, done, total_exercises, completed)

    def _mark_course_completed(self, profile_id: int, course_id: str) -> None:
        with self._tx() as conn:
            conn.execute(
                """
                INSERT INTO course_completion (profile_id, course_id, completed_at)
                VALUES (?, ?, ?)
                ON CONFLICT(profile_id, course_id) DO NOTHING
                """,
                (profile_id, course_id, _now()),
            )

    def overall_progress(self, profile_id: int, total_exercises: int) -> int:
        """Pourcentage global : exercices reussis / total, entre 0 et 100."""
        if total_exercises <= 0:
            return 0
        done = len(self.passed_exercise_ids(profile_id))
        return min(100, round(100 * done / total_exercises))

    def recent_activity(self, profile_id: int, limit: int = 20) -> list[tuple[str, str, str]]:
        rows = self._conn.execute(
            "SELECT kind, detail, at FROM activity_log WHERE profile_id = ? ORDER BY id DESC LIMIT ?",
            (profile_id, limit),
        ).fetchall()
        return [(r["kind"], r["detail"], r["at"]) for r in rows]
