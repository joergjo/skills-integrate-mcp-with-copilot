"""High School Management System API."""

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

try:
    from .db import DEFAULT_DB_PATH, initialize_database, seed_database_if_empty
    from .repository import (
        ActivityNotFoundError,
        ActivityRepository,
        RegistrationError,
    )
except ImportError:
    from db import DEFAULT_DB_PATH, initialize_database, seed_database_if_empty
    from repository import ActivityNotFoundError, ActivityRepository, RegistrationError


def create_app(db_path: Path | None = None) -> FastAPI:
    app = FastAPI(
        title="Mergington High School API",
        description="API for viewing and signing up for extracurricular activities",
    )

    repository = ActivityRepository(db_path or DEFAULT_DB_PATH)
    static_dir = Path(__file__).parent / "static"
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

    @app.on_event("startup")
    def setup_database() -> None:
        initialize_database(repository.db_path)
        seed_database_if_empty(repository.db_path)

    @app.get("/")
    def root() -> RedirectResponse:
        return RedirectResponse(url="/static/index.html")

    @app.get("/activities")
    def get_activities() -> dict[str, dict[str, object]]:
        return repository.list_activities()

    @app.post("/activities/{activity_name}/signup")
    def signup_for_activity(activity_name: str, email: str) -> dict[str, str]:
        try:
            repository.signup(activity_name, email)
        except ActivityNotFoundError:
            raise HTTPException(status_code=404, detail="Activity not found") from None
        except RegistrationError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from None

        return {"message": f"Signed up {email} for {activity_name}"}

    @app.delete("/activities/{activity_name}/unregister")
    def unregister_from_activity(activity_name: str, email: str) -> dict[str, str]:
        try:
            repository.unregister(activity_name, email)
        except ActivityNotFoundError:
            raise HTTPException(status_code=404, detail="Activity not found") from None
        except RegistrationError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from None

        return {"message": f"Unregistered {email} from {activity_name}"}

    return app


app = create_app()
