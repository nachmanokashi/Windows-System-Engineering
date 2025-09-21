from fastapi import FastAPI
from .core.config import get_settings
from .core.middleware import add_middlewares
from .mvc.controllers import health_controller
from .mvc.controllers.articles_controller import router as articles_router

settings = get_settings()

app = FastAPI(title=settings.APP_NAME, version="0.1.0", debug=settings.DEBUG)

# ליבה
add_middlewares(app, settings)

# Routers (מוסיפים prefix של גרסה ברמת ה-include)
app.include_router(health_controller.router, prefix=settings.API_PREFIX)   # /api/v1/health
app.include_router(articles_router,        prefix=settings.API_PREFIX)     # /api/v1/articles

@app.get("/")
def read_root():
    return {"service": "newsdesk-api", "ok": True}
