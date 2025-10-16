# main.py
from fastapi import FastAPI
from app.core.config import get_settings
from app.core.middleware import add_middlewares
from app.core.db import Base, engine
from app.mvc.controllers import articles_controller, auth_controller, llm_controller
from app.mvc.controllers import health_controller

settings = get_settings()

# יצירת אפליקציית FastAPI
app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG,
    docs_url="/docs",
    redoc_url="/redoc"
)

# הוספת middlewares (CORS, Exception handlers)
add_middlewares(app, settings)

# יצירת טבלאות בבסיס הנתונים
if settings.RUN_CREATE_ALL:
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")

# רישום Controllers (Routes)
app.include_router(health_controller.router, prefix=settings.API_PREFIX)
app.include_router(auth_controller.router, prefix=settings.API_PREFIX)
app.include_router(articles_controller.router, prefix=settings.API_PREFIX)
app.include_router(llm_controller.router, prefix=settings.API_PREFIX)


@app.get("/")
def root():
    return {
        "message": "Welcome to NewsDesk API",
        "version": "1.0.0",
        "docs": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)