from fastapi import FastAPI, HTTPException, status, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from datetime import datetime, timezone


def create_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "statusCode": exc.status_code,
                "message": exc.detail if isinstance(exc.detail, str) else "Đã xảy ra lỗi",
                "data": None,
                "error": exc.detail,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "path": request.url.path
            },
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "statusCode": 422,
                "message": "Dữ liệu đầu vào không hợp lệ",
                "data": None,
                "error": exc.errors(),
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "path": request.url.path
            },
        )

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "statusCode": 500,
                "message": "Lỗi hệ thống",
                "data": None,
                "error": str(exc),
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "path": request.url.path
            },
        )
