from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import logging

logger = logging.getLogger(__name__)

class PaperBrainException(Exception):
    def __init__(self, code: str, message: str, status_code: int = 400, details: dict = None):
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)

class NotFoundException(PaperBrainException):
    def __init__(self, message: str = "Resource not found", code: str = "NOT_FOUND", details: dict = None):
        super().__init__(code=code, message=message, status_code=404, details=details)

class BadRequestException(PaperBrainException):
    def __init__(self, message: str = "Bad request", code: str = "BAD_REQUEST", details: dict = None):
        super().__init__(code=code, message=message, status_code=400, details=details)

class UnauthorizedException(PaperBrainException):
    def __init__(self, message: str = "Unauthorized", code: str = "UNAUTHORIZED", details: dict = None):
        super().__init__(code=code, message=message, status_code=401, details=details)

class ForbiddenException(PaperBrainException):
    def __init__(self, message: str = "Forbidden", code: str = "FORBIDDEN", details: dict = None):
        super().__init__(code=code, message=message, status_code=403, details=details)

async def paperbrain_exception_handler(request: Request, exc: PaperBrainException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
                "details": exc.details
            }
        }
    )

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    details = {str(err["loc"][-1]): err["msg"] for err in exc.errors()}
    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Input validation failed",
                "details": details
            }
        }
    )

async def generic_exception_handler(request: Request, exc: Exception):
    logger.exception("An unhandled exception occurred")
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred",
                "details": {}
            }
        }
    )
