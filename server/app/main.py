from fastapi import FastAPI
from .controllers import health_controller
from .controllers.articles_controller import router as articles_router

app = FastAPI(title="NewsDesk API", version="0.1.0")
app.include_router(health_controller.router)  # /health
app.include_router(articles_router)           # /articles

@app.get("/")
def read_root():
    return {"service": "newsdesk-api", "ok": True}
