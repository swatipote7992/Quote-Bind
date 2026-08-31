from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from app.repositories.quote_repository import UnknownProductIdError

async def unknown_product_id_handler(request: Request, exc: UnknownProductIdError):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": f"Unknown product_id: {exc.product_id}"},
    )

async def unhandled_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal Server Error"},
    )
#Note: app.add_exception_handler(exc_type, handler) is the plain-function
#equivalent of the @app.exception_handler(exc_type) decorator — same
#effect, just usable outside of main.py.
def register_exception_handler(app: FastAPI) -> None:
    app.add_exception_handler(UnknownProductIdError, unknown_product_id_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)

