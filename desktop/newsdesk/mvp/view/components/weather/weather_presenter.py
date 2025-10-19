# desktop/newsdesk/mvp/view/components/weather/weather_presenter.py
"""
Weather Presenter - לוגיקה לתחזית מזג אוויר
"""

from PySide6.QtCore import QObject, Signal


class WeatherPresenter(QObject):
    """Presenter למזג אוויר"""
    
    weather_loaded = Signal(dict)
    daily_loaded = Signal(list)
    error_occurred = Signal(str)
    
    def __init__(self, api_client):
        super().__init__()
        self.api_client = api_client
        self.view = None
    
    def set_view(self, view):
        """קבע את ה-View"""
        self.view = view
        self.weather_loaded.connect(view.update_current_weather)
        self.daily_loaded.connect(view.update_daily_forecast)
        self.error_occurred.connect(view.show_error)
    
    def load_weather(self, city=None):
        """טען מזג אוויר"""
        print(f"🌤️ טוען מזג אוויר...")
        
        # טען ישירות
        self._load_current(city)
        self._load_daily(city)
    
    def _load_current(self, city=None):
        """טען מזג אוויר נוכחי"""
        try:
            params = {}
            if city:
                params["city"] = city
            
            # api_client.get מחזיר Response object
            response = self.api_client.get("/weather/current", params=params)
            
            # בדוק אם זה Response או dict
            if hasattr(response, 'status_code'):
                # זה Response object
                if response.status_code == 200:
                    data = response.json()
                    print(f"✅ מזג אוויר: {data['temperature']}°C")
                    self.weather_loaded.emit(data)
                else:
                    error = f"שגיאה {response.status_code}"
                    print(f"❌ {error}")
                    self.error_occurred.emit(error)
            else:
                # זה כבר dict
                if 'error' in response:
                    print(f"❌ {response['error']}")
                    self.error_occurred.emit(response['error'])
                else:
                    print(f"✅ מזג אוויר: {response['temperature']}°C")
                    self.weather_loaded.emit(response)
                
        except Exception as e:
            error = f"שגיאה: {str(e)}"
            print(f"❌ {error}")
            self.error_occurred.emit(error)
    
    def _load_daily(self, city=None):
        """טען תחזית יומית"""
        try:
            params = {}
            if city:
                params["city"] = city
            
            response = self.api_client.get("/weather/daily", params=params)
            
            # בדוק אם זה Response או dict
            if hasattr(response, 'status_code'):
                # זה Response object
                if response.status_code == 200:
                    data = response.json()
                    daily = data["daily_forecast"]
                    print(f"✅ תחזית: {len(daily)} ימים")
                    self.daily_loaded.emit(daily)
                else:
                    print(f"❌ שגיאה בתחזית: {response.status_code}")
            else:
                # זה כבר dict
                if 'error' in response:
                    print(f"❌ {response['error']}")
                elif 'daily_forecast' in response:
                    daily = response["daily_forecast"]
                    print(f"✅ תחזית: {len(daily)} ימים")
                    self.daily_loaded.emit(daily)
                
        except Exception as e:
            print(f"❌ שגיאה בתחזית: {e}")