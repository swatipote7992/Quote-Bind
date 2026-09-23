import logging

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError
from app.repositories.quote_repository import UnknownProductIdError

logger = logging.getLogger(__name__)

# use PUT /quotes/Q001 request with this input - {
#     "product_id": 5,
#     "applicant": {
#       "applicant_id": 1001,
#       "first_name": "John",
#       "last_name": "Smith",
#       "email": "john.smith@example.com",
#       "phone": "7700900123",
#       "date_of_birth": "1990-03-22"
#     }
# }
async def unknown_product_id_handler(request: Request, exc: UnknownProductIdError):
    logger.warning(
        "Unknown product_id %s on %s %s", exc.product_id, request.method, request.url.path
    )
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": f"Unknown product_id: {exc.product_id}"},
    )

async def integrity_error_handler(request: Request, exc: IntegrityError):
    logger.warning("IntegrityError on %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": "Cannot delete: this record is still referenced by another record"},
    )

async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled error on %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal Server Error"},
    )
#Note: app.add_exception_handler(exc_type, handler) is the plain-function
#equivalent of the @app.exception_handler(exc_type) decorator — same
#effect, just usable outside of main.py.
def register_exception_handler(app: FastAPI) -> None:
    app.add_exception_handler(UnknownProductIdError, unknown_product_id_handler)
    app.add_exception_handler(IntegrityError, integrity_error_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)

