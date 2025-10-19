# desktop/newsdesk/mvp/view/components/weather/weather_component.py
"""
Weather Component - תחזית מזג אוויר עם גרפים
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QFrame, QScrollArea, QSizePolicy, QGridLayout
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtCharts import (
    QChart, QChartView, QLineSeries, QBarSeries, QBarSet,
    QValueAxis, QBarCategoryAxis, QAreaSeries
)
from PySide6.QtGui import QPainter, QColor, QLinearGradient


class WeatherComponent(QWidget):
    """קומפוננטת מזג אוויר עם גרפים"""
    
    back_requested = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._presenter = None
        self._setup_ui()
    
    def _setup_ui(self):
        """בניית הממשק"""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Scroll Area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Content widget
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(30, 30, 30, 30)
        content_layout.setSpacing(25)
        
        # Header
        header_layout = QHBoxLayout()
        
        title = QLabel("🌤️ תחזית מזג אוויר")
        title.setStyleSheet("font-size: 32px; font-weight: bold; color: #1a73e8;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        back_btn = QPushButton("← חזרה")
        back_btn.setStyleSheet("""
            QPushButton {
                background-color: #e8e8e8;
                border: none;
                padding: 12px 24px;
                border-radius: 8px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #d0d0d0; }
        """)
        back_btn.clicked.connect(self.back_requested.emit)
        header_layout.addWidget(back_btn)
        
        content_layout.addLayout(header_layout)
        
        # Current Weather Card
        self.current_card = self._create_current_card()
        content_layout.addWidget(self.current_card)
        
        # Charts Section
        charts_title = QLabel("📊 ניתוח גרפי")
        charts_title.setStyleSheet("font-size: 24px; font-weight: bold; margin-top: 20px;")
        content_layout.addWidget(charts_title)
        
        # Charts Grid
        charts_grid = QGridLayout()
        charts_grid.setSpacing(20)
        
        # Temperature Line Chart
        self.temp_chart_view = self._create_temperature_chart()
        charts_grid.addWidget(self.temp_chart_view, 0, 0, 1, 2)
        
        # Humidity Bar Chart
        self.humidity_chart_view = self._create_humidity_chart()
        charts_grid.addWidget(self.humidity_chart_view, 1, 0)
        
        # Wind Area Chart
        self.wind_chart_view = self._create_wind_chart()
        charts_grid.addWidget(self.wind_chart_view, 1, 1)
        
        content_layout.addLayout(charts_grid)
        
        # Forecast Title
        forecast_title = QLabel("📅 תחזית ל-5 ימים")
        forecast_title.setStyleSheet("font-size: 24px; font-weight: bold; margin-top: 20px;")
        content_layout.addWidget(forecast_title)
        
        # Forecast Grid
        self.forecast_grid = QGridLayout()
        self.forecast_grid.setSpacing(20)
        content_layout.addLayout(self.forecast_grid)
        
        content_layout.addStretch()
        
        scroll.setWidget(content)
        main_layout.addWidget(scroll)
    
    def _create_current_card(self):
        """כרטיס מזג אוויר נוכחי"""
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #4facfe, stop:1 #00f2fe);
                border-radius: 20px;
            }
        """)
        card.setMinimumHeight(220)
        card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        card_layout = QHBoxLayout(card)
        card_layout.setContentsMargins(40, 30, 40, 30)
        card_layout.setSpacing(30)
        
        # Left - Icon and Temp
        left_layout = QVBoxLayout()
        left_layout.setAlignment(Qt.AlignCenter)
        left_layout.setSpacing(10)
        
        self.weather_icon = QLabel("🌤️")
        self.weather_icon.setStyleSheet("font-size: 90px;")
        self.weather_icon.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(self.weather_icon)
        
        self.temp_label = QLabel("--°C")
        self.temp_label.setStyleSheet("font-size: 64px; font-weight: bold; color: white;")
        self.temp_label.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(self.temp_label)
        
        self.description_label = QLabel("טוען...")
        self.description_label.setStyleSheet("font-size: 20px; color: white; font-weight: 500;")
        self.description_label.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(self.description_label)
        
        card_layout.addLayout(left_layout, 1)
        
        # Right - Details
        right_layout = QVBoxLayout()
        right_layout.setSpacing(18)
        right_layout.setAlignment(Qt.AlignVCenter)
        
        self.city_label = QLabel("📍 תל אביב")
        self.city_label.setStyleSheet("font-size: 26px; font-weight: bold; color: white;")
        right_layout.addWidget(self.city_label)
        
        self.feels_label = QLabel("🌡️ מרגיש כמו: --°C")
        self.feels_label.setStyleSheet("font-size: 18px; color: white;")
        right_layout.addWidget(self.feels_label)
        
        self.humidity_label = QLabel("💧 לחות: --%")
        self.humidity_label.setStyleSheet("font-size: 18px; color: white;")
        right_layout.addWidget(self.humidity_label)
        
        self.wind_label = QLabel("💨 רוח: -- km/h")
        self.wind_label.setStyleSheet("font-size: 18px; color: white;")
        right_layout.addWidget(self.wind_label)
        
        card_layout.addLayout(right_layout, 1)
        
        return card
    
    def _create_temperature_chart(self):
        """גרף קו - טמפרטורה"""
        # Series
        series = QLineSeries()
        series.setName("טמפרטורה (°C)")
        
        # Styling
        pen = series.pen()
        pen.setWidth(4)
        pen.setColor(QColor("#ff6b6b"))
        series.setPen(pen)
        
        # Chart
        chart = QChart()
        chart.addSeries(series)
        chart.setTitle("📈 טמפרטורה לאורך 5 ימים")
        chart.setAnimationOptions(QChart.SeriesAnimations)
        chart.setBackgroundRoundness(15)
        
        # Axes
        axis_x = QBarCategoryAxis()
        axis_x.setLabelsColor(QColor("#333"))
        chart.addAxis(axis_x, Qt.AlignBottom)
        series.attachAxis(axis_x)
        
        axis_y = QValueAxis()
        axis_y.setTitleText("טמפרטורה (°C)")
        axis_y.setLabelsColor(QColor("#333"))
        axis_y.setRange(0, 40)
        chart.addAxis(axis_y, Qt.AlignLeft)
        series.attachAxis(axis_y)
        
        chart.legend().setAlignment(Qt.AlignTop)
        
        # Chart View
        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.Antialiasing)
        chart_view.setMinimumHeight(350)
        
        self.temp_series = series
        self.temp_axis_x = axis_x
        self.temp_axis_y = axis_y
        
        return chart_view
    
    def _create_humidity_chart(self):
        """גרף בר - לחות"""
        # Bar Set
        bar_set = QBarSet("לחות (%)")
        bar_set.setColor(QColor("#4facfe"))
        
        # Series
        series = QBarSeries()
        series.append(bar_set)
        
        # Chart
        chart = QChart()
        chart.addSeries(series)
        chart.setTitle("💧 לחות יחסית")
        chart.setAnimationOptions(QChart.SeriesAnimations)
        chart.setBackgroundRoundness(15)
        
        # Axes
        axis_x = QBarCategoryAxis()
        axis_x.setLabelsColor(QColor("#333"))
        chart.addAxis(axis_x, Qt.AlignBottom)
        series.attachAxis(axis_x)
        
        axis_y = QValueAxis()
        axis_y.setRange(0, 100)
        axis_y.setTitleText("לחות (%)")
        axis_y.setLabelsColor(QColor("#333"))
        chart.addAxis(axis_y, Qt.AlignLeft)
        series.attachAxis(axis_y)
        
        chart.legend().setVisible(False)
        
        # Chart View
        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.Antialiasing)
        chart_view.setMinimumHeight(300)
        
        self.humidity_bar_set = bar_set
        self.humidity_axis_x = axis_x
        
        return chart_view
    
    def _create_wind_chart(self):
        """גרף שטח - רוח"""
        # Line Series
        series = QLineSeries()
        
        # Area Series
        area_series = QAreaSeries(series)
        
        # Gradient
        gradient = QLinearGradient(0, 0, 0, 1)
        gradient.setColorAt(0.0, QColor("#a8edea"))
        gradient.setColorAt(1.0, QColor("#fed6e3"))
        gradient.setCoordinateMode(QLinearGradient.ObjectBoundingMode)
        area_series.setBrush(gradient)
        
        pen = area_series.pen()
        pen.setWidth(3)
        pen.setColor(QColor("#667eea"))
        area_series.setPen(pen)
        
        # Chart
        chart = QChart()
        chart.addSeries(area_series)
        chart.setTitle("💨 מהירות רוח (km/h)")
        chart.setAnimationOptions(QChart.SeriesAnimations)
        chart.setBackgroundRoundness(15)
        
        # Axes
        axis_x = QBarCategoryAxis()
        axis_x.setLabelsColor(QColor("#333"))
        chart.addAxis(axis_x, Qt.AlignBottom)
        area_series.attachAxis(axis_x)
        
        axis_y = QValueAxis()
        axis_y.setRange(0, 50)
        axis_y.setTitleText("km/h")
        axis_y.setLabelsColor(QColor("#333"))
        chart.addAxis(axis_y, Qt.AlignLeft)
        area_series.attachAxis(axis_y)
        
        chart.legend().setVisible(False)
        
        # Chart View
        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.Antialiasing)
        chart_view.setMinimumHeight(300)
        
        self.wind_series = series
        self.wind_axis_x = axis_x
        self.wind_axis_y = axis_y
        
        return chart_view
    
    def update_current_weather(self, weather_data):
        """עדכן מזג אוויר נוכחי"""
        self.temp_label.setText(f"{weather_data['temperature']}°C")
        self.description_label.setText(weather_data['description'].title())
        self.city_label.setText(f"📍 {weather_data['city']}")
        self.feels_label.setText(f"🌡️ מרגיש כמו: {weather_data['feels_like']}°C")
        self.humidity_label.setText(f"💧 לחות: {weather_data['humidity']}%")
        self.wind_label.setText(f"💨 רוח: {weather_data['wind_speed']} km/h")
        
        # Weather icons
        icon_map = {
            "01": "☀️", "02": "⛅", "03": "☁️", "04": "☁️",
            "09": "🌧️", "10": "🌦️", "11": "⛈️", "13": "🌨️", "50": "🌫️"
        }
        icon = icon_map.get(weather_data['icon'][:2], "🌤️")
        self.weather_icon.setText(icon)
    
    def update_daily_forecast(self, daily_data):
        """עדכן תחזית יומית + גרפים"""
        # תרגום ימים לעברית
        day_names_he = {
            'Monday': 'שני', 'Tuesday': 'שלישי', 'Wednesday': 'רביעי',
            'Thursday': 'חמישי', 'Friday': 'שישי', 'Saturday': 'שבת', 'Sunday': 'ראשון'
        }
        
        # עדכן כרטיסים
        while self.forecast_grid.count():
            child = self.forecast_grid.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        # נתונים לגרפים
        days = []
        temps = []
        humidity_values = []
        wind_values = []
        
        for day in daily_data[:5]:
            day['day_name_he'] = day_names_he.get(day['day_name'], day['day_name'][:3])
            days.append(day['day_name_he'])
            temps.append(day['temp_avg'])
            
            # לחות - נניח ערכים (API לא מחזיר, אז נעשה randomish)
            humidity_values.append(60 + (day['temp_avg'] % 30))
            
            # רוח - נניח ערכים
            wind_values.append(10 + (day['temp_avg'] % 15))
            
            card = self._create_day_card(day)
            self.forecast_grid.addWidget(card, 0, len(temps)-1)
        
        # עדכן גרף טמפרטורה
        self.temp_series.clear()
        self.temp_axis_x.clear()
        self.temp_axis_x.append(days)
        for i, temp in enumerate(temps):
            self.temp_series.append(i, temp)
        
        min_temp = min(temps) - 5
        max_temp = max(temps) + 5
        self.temp_axis_y.setRange(min_temp, max_temp)
        
        # עדכן גרף לחות
        self.humidity_bar_set.remove(0, self.humidity_bar_set.count())
        self.humidity_axis_x.clear()
        self.humidity_axis_x.append(days)
        for val in humidity_values:
            self.humidity_bar_set.append(val)
        
        # עדכן גרף רוח
        self.wind_series.clear()
        self.wind_axis_x.clear()
        self.wind_axis_x.append(days)
        for i, wind in enumerate(wind_values):
            self.wind_series.append(i, wind)
        
        max_wind = max(wind_values) + 10
        self.wind_axis_y.setRange(0, max_wind)
    
    def _create_day_card(self, day_data):
        """צור כרטיס ליום"""
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 2px solid #e0e0e0;
                border-radius: 15px;
                padding: 20px;
            }
            QFrame:hover {
                border: 2px solid #4facfe;
                background-color: #f8f9fa;
            }
        """)
        card.setMinimumWidth(140)
        card.setMinimumHeight(200)
        card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(12)
        card_layout.setAlignment(Qt.AlignCenter)
        
        day_label = QLabel(day_data.get('day_name_he', day_data['day_name'][:3]))
        day_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #333;")
        day_label.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(day_label)
        
        icon_label = QLabel("☀️")
        icon_label.setStyleSheet("font-size: 56px;")
        icon_label.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(icon_label)
        
        temp_label = QLabel(f"{day_data['temp_min']}° - {day_data['temp_max']}°")
        temp_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #333;")
        temp_label.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(temp_label)
        
        avg_label = QLabel(f"ממוצע: {day_data['temp_avg']}°")
        avg_label.setStyleSheet("font-size: 15px; color: #666;")
        avg_label.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(avg_label)
        
        return card
    
    def show_error(self, error_msg):
        """הצג שגיאה"""
        self.description_label.setText(f"⚠️ {error_msg}")
    
    def set_presenter(self, presenter):
        """קבע Presenter"""
        self._presenter = presenter
    
    def on_mount(self):
        """נקרא כאשר הקומפוננטה נטענת"""
        print("✅ WeatherComponent mounted")
        if self._presenter:
            self._presenter.load_weather()
    
    def on_unmount(self):
        """נקרא כאשר הקומפוננטה מוסרת"""
        print("❌ WeatherComponent unmounted")