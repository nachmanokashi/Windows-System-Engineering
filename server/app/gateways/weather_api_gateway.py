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
            "wind_speed": round(data["wind"]["speed"] * 3.6, 1),  # m/s to km/h
            "description": data["weather"][0]["description"],
            "icon": data["weather"][0]["icon"]
        }
    
    def get_daily_forecast(self, city: str = None) -> List[Dict]:

        city = city or self.default_city
        data = self._make_request("forecast", {"q": city})
        
        daily = {}
        
        for item in data["list"]:
            date = datetime.fromtimestamp(item["dt"]).strftime("%Y-%m-%d")
            
            if date not in daily:
                daily[date] = {
                    "date": date,
                    "day_name": datetime.fromtimestamp(item["dt"]).strftime("%A"),
                    "temps": [],
                    "humidity": [],      
                    "wind_speed": []   
                }
            
            # הוספת נתונים
            daily[date]["temps"].append(round(item["main"]["temp"]))
            daily[date]["humidity"].append(item["main"]["humidity"])
            daily[date]["wind_speed"].append(round(item["wind"]["speed"] * 3.6, 1))  # m/s to km/h
        
        result = []
        for date, info in list(daily.items())[:5]:
            result.append({
                "date": date,
                "day_name": info["day_name"],
                "temp_min": min(info["temps"]),
                "temp_max": max(info["temps"]),
                "temp_avg": round(sum(info["temps"]) / len(info["temps"])),
                "humidity_avg": round(sum(info["humidity"]) / len(info["humidity"])),
                "wind_speed_avg": round(sum(info["wind_speed"]) / len(info["wind_speed"]), 1)
            })
        
        print(f"✅ Weather data for {len(result)} days:")
        for day in result:
            print(f"   {day['day_name']}: Temp={day['temp_avg']}°C, Humidity={day['humidity_avg']}%, Wind={day['wind_speed_avg']}km/h")
        
        return result