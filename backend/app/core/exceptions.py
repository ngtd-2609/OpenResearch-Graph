from fastapi import FastAPI, Request
from fastapi.responses import ORJSONResponse


class AppError(Exception):
    def __init__(self, message: str, status_code: int = 400) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code


def install_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def handle_app_error(_: Request, exc: AppError) -> ORJSONResponse:
        return ORJSONResponse(status_code=exc.status_code, content={"detail": exc.message})
