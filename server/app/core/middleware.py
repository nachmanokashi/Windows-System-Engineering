from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from .config import Settings

def add_middlewares(app: FastAPI, settings: Settings) -> None:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOW_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(_: Request, exc: HTTPException):
        return JSONResponse(status_code=exc.status_code, content={"error": exc.detail})

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(_: Request, exc: Exception):
        return JSONResponse(status_code=500, content={"error": "Internal Server Error"})
