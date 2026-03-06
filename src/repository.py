"""Data access layer for activities and registrations."""

from __future__ import annotations

import sqlite3
from pathlib import Path


class ActivityNotFoundError(Exception):
    """Raised when an activity does not exist."""


class RegistrationError(Exception):
    """Raised when a registration operation is invalid."""


class ActivityRepository:
    def __init__(self, db_path: Path):
        self.db_path = Path(db_path)

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    def list_activities(self) -> dict[str, dict[str, object]]:
        with self._connect() as connection:
            activity_rows = connection.execute(
                """
                SELECT id, name, description, schedule, max_participants
                FROM activities
                ORDER BY id
                """
            ).fetchall()

            result: dict[str, dict[str, object]] = {}
            for row in activity_rows:
                participants = connection.execute(
                    """
                    SELECT users.email
                    FROM registrations
                    JOIN users ON users.id = registrations.user_id
                    WHERE registrations.activity_id = ?
                    ORDER BY registrations.id
                    """,
                    (row["id"],),
                ).fetchall()

                result[row["name"]] = {
                    "description": row["description"],
                    "schedule": row["schedule"],
                    "max_participants": row["max_participants"],
                    "participants": [participant["email"] for participant in participants],
                }

            return result

    def signup(self, activity_name: str, email: str) -> None:
        with self._connect() as connection:
            activity = connection.execute(
                "SELECT id FROM activities WHERE name = ?",
                (activity_name,),
            ).fetchone()
            if activity is None:
                raise ActivityNotFoundError()

            connection.execute(
                "INSERT OR IGNORE INTO users (email) VALUES (?)",
                (email,),
            )
            user = connection.execute(
                "SELECT id FROM users WHERE email = ?",
                (email,),
            ).fetchone()

            existing_registration = connection.execute(
                """
                SELECT id
                FROM registrations
                WHERE activity_id = ? AND user_id = ?
                """,
                (activity["id"], user["id"]),
            ).fetchone()
            if existing_registration is not None:
                raise RegistrationError("Student is already signed up")

            connection.execute(
                """
                INSERT INTO registrations (activity_id, user_id)
                VALUES (?, ?)
                """,
                (activity["id"], user["id"]),
            )
            connection.commit()

    def unregister(self, activity_name: str, email: str) -> None:
        with self._connect() as connection:
            activity = connection.execute(
                "SELECT id FROM activities WHERE name = ?",
                (activity_name,),
            ).fetchone()
            if activity is None:
                raise ActivityNotFoundError()

            user = connection.execute(
                "SELECT id FROM users WHERE email = ?",
                (email,),
            ).fetchone()
            if user is None:
                raise RegistrationError("Student is not signed up for this activity")

            registration = connection.execute(
                """
                SELECT id
                FROM registrations
                WHERE activity_id = ? AND user_id = ?
                """,
                (activity["id"], user["id"]),
            ).fetchone()
            if registration is None:
                raise RegistrationError("Student is not signed up for this activity")

            connection.execute(
                "DELETE FROM registrations WHERE id = ?",
                (registration["id"],),
            )
            connection.commit()
