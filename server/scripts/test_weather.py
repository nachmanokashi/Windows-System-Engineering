import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.gateways.weather_api_gateway import WeatherAPIGateway

try:
    gateway = WeatherAPIGateway()
    print(f"✅ Gateway עובד!")
    print(f"🔑 API Key: {gateway.api_key[:10]}...")
    
    weather = gateway.get_current_weather()
    print(f"\n🌡️ מזג אוויר ב{weather['city']}:")
    print(f"   טמפרטורה: {weather['temperature']}°C")
    print(f"   תיאור: {weather['description']}")
    
    print("\n✅ הכל עובד מצוין!")
except Exception as e:
    print(f"❌ שגיאה: {e}")