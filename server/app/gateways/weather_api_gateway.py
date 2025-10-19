import requests
from typing import Dict, List
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

class WeatherAPIGateway:
    """Gateway לשירות OpenWeatherMap"""
    
    def __init__(self):
        self.api_key = os.getenv("WEATHER_API_KEY")
        self.base_url = "https://api.openweathermap.org/data/2.5"
        self.default_city = "Tel Aviv"
        
        if not self.api_key:
            raise ValueError("❌ WEATHER_API_KEY לא מוגדר ב-.env")
    
    def _make_request(self, endpoint: str, params: Dict) -> Dict:
        """בצע בקשה ל-API"""
        params["appid"] = self.api_key
        params["units"] = "metric"
        params["lang"] = "he"
        
        url = f"{self.base_url}/{endpoint}"
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    
    def get_current_weather(self, city: str = None) -> Dict:
        """קבל מזג אוויר נוכחי"""
        city = city or self.default_city
        data = self._make_request("weather", {"q": city})
        
        return {
            "city": data["name"],
            "temperature": round(data["main"]["temp"]),
            "feels_like": round(data["main"]["feels_like"]),
            "humidity": data["main"]["humidity"],
            "wind_speed": round(data["wind"]["speed"] * 3.6, 1),
            "description": data["weather"][0]["description"],
            "icon": data["weather"][0]["icon"]
        }
    
    def get_daily_forecast(self, city: str = None) -> List[Dict]:
        """קבל תחזית ל-5 ימים"""
        city = city or self.default_city
        data = self._make_request("forecast", {"q": city})
        
        daily = {}
        for item in data["list"]:
            date = datetime.fromtimestamp(item["dt"]).strftime("%Y-%m-%d")
            if date not in daily:
                daily[date] = {
                    "date": date,
                    "day_name": datetime.fromtimestamp(item["dt"]).strftime("%A"),
                    "temps": []
                }
            daily[date]["temps"].append(round(item["main"]["temp"]))
        
        result = []
        for date, info in list(daily.items())[:5]:
            result.append({
                "date": date,
                "day_name": info["day_name"],
                "temp_min": min(info["temps"]),
                "temp_max": max(info["temps"]),
                "temp_avg": round(sum(info["temps"]) / len(info["temps"]))
            })
        
        return result