from pathlib import Path

from fastapi.testclient import TestClient

from src.app import create_app
from src.db import initialize_database, seed_database_if_empty


def _new_client(db_path: Path) -> TestClient:
    app = create_app(db_path=db_path)
    return TestClient(app)


def test_get_activities_returns_seed_data(tmp_path: Path) -> None:
    db_path = tmp_path / "test.db"

    with _new_client(db_path) as client:
        response = client.get("/activities")

    assert response.status_code == 200
    activities = response.json()
    assert "Chess Club" in activities
    assert activities["Chess Club"]["participants"] == [
        "michael@mergington.edu",
        "daniel@mergington.edu",
    ]


def test_signup_and_unregister_flow(tmp_path: Path) -> None:
    db_path = tmp_path / "test.db"

    with _new_client(db_path) as client:
        signup_response = client.post(
            "/activities/Chess Club/signup",
            params={"email": "newstudent@mergington.edu"},
        )
        assert signup_response.status_code == 200

        duplicate_response = client.post(
            "/activities/Chess Club/signup",
            params={"email": "newstudent@mergington.edu"},
        )
        assert duplicate_response.status_code == 400
        assert duplicate_response.json()["detail"] == "Student is already signed up"

        unregister_response = client.delete(
            "/activities/Chess Club/unregister",
            params={"email": "newstudent@mergington.edu"},
        )
        assert unregister_response.status_code == 200

        missing_response = client.delete(
            "/activities/Chess Club/unregister",
            params={"email": "newstudent@mergington.edu"},
        )
        assert missing_response.status_code == 400
        assert (
            missing_response.json()["detail"]
            == "Student is not signed up for this activity"
        )


def test_data_persists_after_restart(tmp_path: Path) -> None:
    db_path = tmp_path / "test.db"

    with _new_client(db_path) as client:
        response = client.post(
            "/activities/Programming%20Class/signup",
            params={"email": "persisted@mergington.edu"},
        )
        assert response.status_code == 200

    # Simulate app restart by creating a new app and TestClient on the same DB.
    with _new_client(db_path) as new_client:
        activities_response = new_client.get("/activities")

    participants = activities_response.json()["Programming Class"]["participants"]
    assert "persisted@mergington.edu" in participants


def test_seed_is_idempotent(tmp_path: Path) -> None:
    db_path = tmp_path / "test.db"

    initialize_database(db_path)
    seed_database_if_empty(db_path)
    seed_database_if_empty(db_path)

    with _new_client(db_path) as client:
        activities = client.get("/activities").json()

    assert len(activities) == 9
