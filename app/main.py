from fastapi import Depends, FastAPI

from app import exceptions
from app.apps.decks.views import router as decks_router
from app.config import settings
from app.db.deps import set_db
from app.db.exceptions import DatabaseValidationError


def get_app() -> FastAPI:
    _app = FastAPI(
        title=settings.SERVICE_NAME,
        debug=settings.DEBUG,
        dependencies=[Depends(set_db)],
    )

    _app.include_router(decks_router, prefix="/api")

    _app.add_exception_handler(
        DatabaseValidationError,
        exceptions.database_validation_exception_handler,
    )

    return _app


app = get_app()
