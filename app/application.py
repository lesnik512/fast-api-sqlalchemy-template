import contextlib
import typing

import fastapi
from fastapi.middleware.cors import CORSMiddleware
import modern_di_fastapi
from advanced_alchemy.exceptions import DuplicateKeyError

from app import exceptions, ioc
from app.api.decks import ROUTER
from app.settings import settings

ALLOWED_ORIGINS = [
    "http://localhost:5173",
    # YOUR ALLOWED ORIGINS HERE
]

def include_routers(app: fastapi.FastAPI) -> None:
    app.include_router(ROUTER, prefix="/api")


class AppBuilder:
    def __init__(self) -> None:
        self.app: fastapi.FastAPI = fastapi.FastAPI(
            title=settings.service_name,
            debug=settings.debug,
            lifespan=self.lifespan_manager,
        )
        self.di_container = modern_di_fastapi.setup_di(self.app)
        include_routers(self.app)
        self.app.add_exception_handler(
            DuplicateKeyError,
            exceptions.duplicate_key_error_handler,  # type: ignore[arg-type]
        )
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=ALLOWED_ORIGINS,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    @contextlib.asynccontextmanager
    async def lifespan_manager(self, _: fastapi.FastAPI) -> typing.AsyncIterator[dict[str, typing.Any]]:
        async with self.di_container:
            await ioc.Dependencies.async_resolve_creators(self.di_container)
            yield {}


application = AppBuilder().app
