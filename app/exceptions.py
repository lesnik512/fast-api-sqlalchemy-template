from advanced_alchemy.exceptions import ForeignKeyError
from fastapi.responses import JSONResponse
from starlette import status
from starlette.requests import Request


async def foreign_key_error_handler(_: Request, exc: ForeignKeyError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.detail},
    )
