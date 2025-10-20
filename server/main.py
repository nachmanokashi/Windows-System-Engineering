from fastapi import FastAPI
from app.core.config import get_settings
from app.core.middleware import add_middlewares
from app.core.db import Base, engine
from app.mvc.controllers import health_controller
from app.mvc.controllers import (
    articles_controller, 
    auth_controller, 
    llm_controller, 
    likes_controller,
    admin_controller  
)
from fastapi.staticfiles import StaticFiles
from app.gateways.weather_api_gateway import WeatherAPIGateway

settings = get_settings()

# יצירת אפליקציית FastAPI
app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG,
    docs_url="/docs",
    redoc_url="/redoc"
)

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
app.include_router(likes_controller.router, prefix=settings.API_PREFIX)
app.include_router(admin_controller.router, prefix=settings.API_PREFIX)  
app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.get("/")
def root():
    return {
        "message": "Welcome to NewsDesk API",
        "version": "1.0.0",
        "docs": "/docs",
        "admin": "/docs#/admin"  
    }

@app.get("/api/v1/weather/current")
def get_current_weather(city: str = None):
    """מזג אוייר נוכחי"""
    try:
        gateway = WeatherAPIGateway()
        weather = gateway.get_current_weather(city)
        return weather
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/v1/weather/daily")
def get_daily_forecast(city: str = None):
    """תחזית ל-5 ימים"""
    try:
        gateway = WeatherAPIGateway()
        forecast = gateway.get_daily_forecast(city)
        return {"daily_forecast": forecast}
    except Exception as e:
        return {"error": str(e)}
    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=False)