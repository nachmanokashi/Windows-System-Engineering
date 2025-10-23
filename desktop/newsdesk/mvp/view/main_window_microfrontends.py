from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QStackedWidget, QFrame, QMessageBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QIcon

from newsdesk.mvp.view.microfrontend_manager import MicrofrontendManager
from newsdesk.components.chat import ChatComponent, ChatPresenter
from newsdesk.components.articles_list.articles_list_view import ArticlesListComponent
from newsdesk.components.articles_list.articles_list_presenter import ArticlesListPresenter
from newsdesk.components.article_details.article_details_view import ArticleDetailsComponent
from newsdesk.components.article_details.article_details_presenter import ArticleDetailsPresenter
from newsdesk.components.weather.weather_component import WeatherComponent
from newsdesk.components.weather.weather_presenter import WeatherPresenter
from newsdesk.components.admin_panel.admin_panel_view import AdminPanelComponent
from newsdesk.components.admin_panel.admin_panel_presenter import AdminPanelPresenter
from newsdesk.infra.http.admin_service_http import AdminServiceHttp
from newsdesk.infra.http.news_api_client import NewsApiClient
from newsdesk.infra.http.news_service_http import HttpNewsService
from newsdesk.infra.http.likes_service_http import HttpLikesService


class MainWindowMicrofrontends(QMainWindow):
    logout_clicked = Signal()

    def __init__(self, api_client: NewsApiClient, username: str = "User", is_admin: bool = False):
        super().__init__(None)

        self.api_client = api_client
        self.username = username
        self.is_admin = is_admin

        # Services
        self.news_service = HttpNewsService(api_client)
        self.likes_service = HttpLikesService(api_client)
        self.admin_service = AdminServiceHttp(api_client)

        self.setWindowTitle("NewsDesk - Microfrontends")

        self.initial_width = 900
        self.initial_height = 500
        self.setMinimumSize(700, 400)
        self.resize(self.initial_width, self.initial_height)

        self._setup_ui()
        self._setup_microfrontends()

        self.manager.load_component("articles_list")
        self._center_on_screen()

    def _center_on_screen(self):
        screen_geometry = self.screen().availableGeometry()
        x = max(0, (screen_geometry.width() - self.initial_width) // 2)
        y = max(0, (screen_geometry.height() - self.initial_height) // 2)
        self.move(x, y)

    def _setup_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        sidebar = self._create_sidebar()
        main_layout.addWidget(sidebar)
        content_area = self._create_content_area()
        main_layout.addWidget(content_area, 1)

    def _create_sidebar(self) -> QWidget:
        sidebar = QFrame()
        sidebar.setFrameShape(QFrame.Shape.StyledPanel)
        sidebar.setStyleSheet("QFrame { background-color: #2c3e50; border-right: 2px solid #34495e; }")
        sidebar.setFixedWidth(220)
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(10, 20, 10, 20)
        layout.setSpacing(10)

        logo_label = QLabel("📰 NewsDesk")
        logo_label.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        logo_label.setStyleSheet("color: white; padding: 10px;")
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(logo_label)

        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet("background-color: #34495e;")
        layout.addWidget(separator)

        nav_style = """
            QPushButton {
                background-color: transparent; color: white; border: none;
                border-radius: 5px; padding: 12px; text-align: left;
                font-size: 14px; font-weight: bold;
            }
            QPushButton:hover { background-color: #34495e; }
            QPushButton:pressed { background-color: #1abc9c; }
            QPushButton:checked { background-color: #16a085; }
        """

        # Articles button
        self.nav_articles_btn = QPushButton("📄 Articles")
        self.nav_articles_btn.setStyleSheet(nav_style)
        self.nav_articles_btn.setCheckable(True)
        self.nav_articles_btn.clicked.connect(lambda: self.navigate_to("articles_list"))
        layout.addWidget(self.nav_articles_btn)

        # Weather button
        self.nav_weather_btn = QPushButton("🌤️ Weather")
        self.nav_weather_btn.setStyleSheet(nav_style)
        self.nav_weather_btn.setCheckable(True)
        self.nav_weather_btn.clicked.connect(lambda: self.navigate_to("weather"))
        layout.addWidget(self.nav_weather_btn)

        # AI Chat button
        self.nav_chat_btn = QPushButton("💬 AI Chat")
        self.nav_chat_btn.setStyleSheet(nav_style)
        self.nav_chat_btn.setCheckable(True)
        self.nav_chat_btn.clicked.connect(lambda: self.navigate_to("chat"))
        layout.addWidget(self.nav_chat_btn)

        # --- כפתור Admin Panel (רק לאדמין) ---
        if self.is_admin:
            self.nav_admin_btn = QPushButton("⚙️ Admin Panel")
            self.nav_admin_btn.setStyleSheet(nav_style)
            self.nav_admin_btn.setCheckable(True)
            self.nav_admin_btn.clicked.connect(lambda: self.navigate_to("admin_panel"))
            layout.addWidget(self.nav_admin_btn)

        layout.addStretch()

        # User info
        user_frame = QFrame()
        user_frame.setStyleSheet("QFrame { background-color: #34495e; border-radius: 5px; padding: 10px; }")
        user_layout = QVBoxLayout(user_frame)
        user_layout.setContentsMargins(5, 5, 5, 5)
        user_label = QLabel(f"👤 {self.username}")
        user_label.setStyleSheet("color: white; font-weight: bold;")
        user_layout.addWidget(user_label)
        if self.is_admin:
            admin_badge = QLabel("⭐ Admin")
            admin_badge.setStyleSheet("color: #f39c12; font-size: 11px;")
            user_layout.addWidget(admin_badge)
        layout.addWidget(user_frame)

        # Logout button
        logout_btn = QPushButton("🚪 Logout")
        logout_btn.setStyleSheet("""
            QPushButton { background-color: #e74c3c; color: white; border: none; border-radius: 5px; padding: 10px; font-weight: bold; }
            QPushButton:hover { background-color: #c0392b; }
        """)
        logout_btn.clicked.connect(self.on_logout_clicked)
        layout.addWidget(logout_btn)

        return sidebar

    def _create_content_area(self) -> QWidget:
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(0, 0, 0, 0); layout.setSpacing(0)
        self.stacked_widget = QStackedWidget()
        layout.addWidget(self.stacked_widget)
        return content

    def _setup_microfrontends(self) -> None:
        self.manager = MicrofrontendManager(self.stacked_widget)
        self.manager.register_component("articles_list", ArticlesListComponent)
        self.manager.register_component("article_details", ArticleDetailsComponent)
        self.manager.register_component("weather", WeatherComponent)
        self.manager.register_component("chat", ChatComponent)
        
        if self.is_admin:
            self.manager.register_component("admin_panel", AdminPanelComponent)
            
        self.manager.container.currentChanged.connect(self._on_component_changed)

    def _on_component_changed(self, index: int) -> None:
        print(f"Main window: Component changed to index {index}")
        current_component = self.stacked_widget.widget(index)
        current_component_name = type(current_component).__name__ 

        recognized_components = (
            ArticlesListComponent, ArticleDetailsComponent, WeatherComponent, 
            AdminPanelComponent, ChatComponent
        )

        if not isinstance(current_component, recognized_components):
            print(f"Main window: Widget at index {index} is not a recognized component ({current_component_name}).")
            self._update_active_nav_button(current_component)
            return

        print(f"Main window: Current component is {current_component_name}")
        self._update_active_nav_button(current_component)

        needs_initial_load = False

        # Articles List Component
        if isinstance(current_component, ArticlesListComponent):
            if not current_component.presenter:
                print("Main window: Connecting ArticlesListPresenter...")
                presenter = ArticlesListPresenter(current_component, self.news_service, self.likes_service) 
                current_component.presenter = presenter
                current_component.article_clicked.connect(self.on_article_clicked)
                current_component.like_toggled.connect(presenter.toggle_like)
                current_component.dislike_toggled.connect(presenter.toggle_dislike)
                needs_initial_load = True
            if needs_initial_load:
                print("Main window: Triggering initial data load for ArticlesListComponent.")
                current_component.load_initial_data()
            else:
                print("Main window: ArticlesListComponent already has a presenter.")

        # Article Details Component
        elif isinstance(current_component, ArticleDetailsComponent):
            if not current_component.presenter:
                print("Main window: Connecting ArticleDetailsPresenter...")
                presenter = ArticleDetailsPresenter(current_component, self.news_service)
                presenter.likes_service = self.likes_service
                current_component.presenter = presenter
                current_component.back_requested.connect(self.on_back_to_list_requested)

        # Weather Component
        elif isinstance(current_component, WeatherComponent):
            if not current_component._presenter:
                print("Main window: Connecting WeatherPresenter...")
                presenter = WeatherPresenter(self.api_client) 
                presenter.set_view(current_component)
                current_component.set_presenter(presenter)
                current_component.back_requested.connect(self.on_back_to_list_requested)
                current_component.on_mount()

        #   לוגיקה ל-Chat Component
        elif isinstance(current_component, ChatComponent): 
            if not current_component._presenter:
                print("Main window: Connecting ChatPresenter...")
                presenter = ChatPresenter(self.api_client) 
                current_component.set_presenter(presenter)
                presenter.set_view(current_component)
                current_component.back_requested.connect(self.on_back_to_list_requested)
            current_component.on_mount() 

        # --- Admin Panel Component (חיבור Presenter) ---
        elif isinstance(current_component, AdminPanelComponent):
            if not current_component.presenter:
                print("Main window: Connecting AdminPanelPresenter...")
                presenter = AdminPanelPresenter(current_component, self.admin_service, self.news_service)
                current_component.presenter = presenter
                presenter.load_articles()

    def _update_active_nav_button(self, current_component: QWidget = None):
        if current_component is None: current_component = self.manager.get_current_component()

        is_articles = isinstance(current_component, ArticlesListComponent)
        is_details = isinstance(current_component, ArticleDetailsComponent)
        is_weather = isinstance(current_component, WeatherComponent)
        is_admin_panel = isinstance(current_component, AdminPanelComponent)
        is_chat = isinstance(current_component, ChatComponent)

        print(f"Main window: Updating nav buttons - Articles: {is_articles}, Details: {is_details}, Weather: {is_weather}, Admin: {is_admin_panel}, Chat: {is_chat}")

        self.nav_articles_btn.setChecked(is_articles or is_details)
        self.nav_weather_btn.setChecked(is_weather)
        self.nav_chat_btn.setChecked(is_chat) 
        
        # --- עדכון כפתור האדמין ---
        if self.is_admin:
            self.nav_admin_btn.setChecked(is_admin_panel)

    def navigate_to(self, component_name: str, **kwargs) -> None:
        print(f"Main window: Navigating to '{component_name}' with args: {kwargs}")
        self.manager.navigate_to(component_name, **kwargs)

    def on_article_clicked(self, article_id: int) -> None:
        print(f"Main window: Article {article_id} clicked, navigating to details.")
        self.navigate_to("article_details", article_id=article_id)

    def on_back_to_list_requested(self) -> None:
        print("Main window: Back requested, navigating to articles list.")
        self.navigate_to("articles_list")

    def show_coming_soon(self, feature: str) -> None:
        QMessageBox.information(self, "Coming Soon", f"{feature} component is coming soon! 🚀")
        sender = self.sender()
        if sender and isinstance(sender, QPushButton) and sender.isCheckable(): 
            self._update_active_nav_button() 
        else: 
            self._update_active_nav_button()

    def on_logout_clicked(self) -> None:
        reply = QMessageBox.question(self, "Logout", "Are you sure you want to logout?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            # Cleanup for presenters
            for component_name, component_instance in self.manager._component_instances.items():
                if hasattr(component_instance, 'presenter') and component_instance.presenter and hasattr(component_instance.presenter, 'cleanup'):
                    print(f"Main window: Cleaning up presenter for {component_name}")
                    component_instance.presenter.cleanup()
                elif hasattr(component_instance, '_presenter') and component_instance._presenter and hasattr(component_instance._presenter, 'cleanup'):
                    print(f"Main window: Cleaning up presenter for {component_name} (weather/chat style)")
                    component_instance._presenter.cleanup()

            self.logout_clicked.emit(); self.close()