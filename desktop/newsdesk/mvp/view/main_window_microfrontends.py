# client/newsdesk/mvp/view/main_window_microfrontends.py
"""
MainWindow עם Microfrontends
Container ראשי שמנהל את כל ה-Components
"""
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QStackedWidget, QFrame
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QIcon

from newsdesk.mvp.view.microfrontend_manager import MicrofrontendManager
from newsdesk.mvp.view.components.articles_list.articles_list_view import ArticlesListComponent
from newsdesk.mvp.view.components.articles_list.articles_list_presenter import ArticlesListPresenter
from newsdesk.infra.http.news_service_http import HttpNewsService
from newsdesk.infra.http.news_api_client import NewsApiClient


class MainWindowMicrofrontends(QMainWindow):
    """
    החלון הראשי עם Microfrontends Architecture
    
    מבנה:
    - Sidebar/TopBar לניווט
    - Content Area עם QStackedWidget
    - MicrofrontendManager לניהול Components
    """
    
    logout_clicked = Signal()
    
    def __init__(self, api_client: NewsApiClient, username: str = "User", is_admin: bool = False):
        super().__init__()
        
        self.api_client = api_client
        self.username = username
        self.is_admin = is_admin
        
        # Services
        self.news_service = HttpNewsService(api_client)
        
        # Setup
        self.setWindowTitle("NewsDesk - Microfrontends")
        self.setMinimumSize(1200, 700)
        
        self._setup_ui()
        self._setup_microfrontends()
        
        # טען את ה-component הראשון
        self.manager.load_component("articles_list")
    
    def _setup_ui(self) -> None:
        """בניית הממשק"""
        
        # Central Widget
        central = QWidget()
        self.setCentralWidget(central)
        
        # Main Layout
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # === Sidebar ===
        sidebar = self._create_sidebar()
        main_layout.addWidget(sidebar)
        
        # === Content Area ===
        content_area = self._create_content_area()
        main_layout.addWidget(content_area, 1)  # stretch
    
    def _create_sidebar(self) -> QWidget:
        """יצירת Sidebar לניווט"""
        sidebar = QFrame()
        sidebar.setFrameShape(QFrame.Shape.StyledPanel)
        sidebar.setStyleSheet("""
            QFrame {
                background-color: #2c3e50;
                border-right: 2px solid #34495e;
            }
        """)
        sidebar.setFixedWidth(220)
        
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(10, 20, 10, 20)
        layout.setSpacing(10)
        
        # === Logo/Title ===
        logo_label = QLabel("📰 NewsDesk")
        logo_label.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        logo_label.setStyleSheet("color: white; padding: 10px;")
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(logo_label)
        
        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet("background-color: #34495e;")
        layout.addWidget(separator)
        
        # === Navigation Buttons ===
        nav_style = """
            QPushButton {
                background-color: transparent;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 12px;
                text-align: left;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #34495e;
            }
            QPushButton:pressed {
                background-color: #1abc9c;
            }
        """
        
        # כפתור Articles
        self.nav_articles_btn = QPushButton("📄 Articles")
        self.nav_articles_btn.setStyleSheet(nav_style)
        self.nav_articles_btn.clicked.connect(lambda: self.navigate_to("articles_list"))
        layout.addWidget(self.nav_articles_btn)
        
        # כפתור Charts (נוסיף אחר כך)
        self.nav_charts_btn = QPushButton("📊 Charts")
        self.nav_charts_btn.setStyleSheet(nav_style)
        self.nav_charts_btn.clicked.connect(lambda: self.show_coming_soon("Charts"))
        self.nav_charts_btn.setEnabled(False)  # כרגע לא פעיל
        layout.addWidget(self.nav_charts_btn)
        
        # כפתור Chat (נוסיף אחר כך)
        self.nav_chat_btn = QPushButton("💬 AI Chat")
        self.nav_chat_btn.setStyleSheet(nav_style)
        self.nav_chat_btn.clicked.connect(lambda: self.show_coming_soon("AI Chat"))
        self.nav_chat_btn.setEnabled(False)  # כרגע לא פעיל
        layout.addWidget(self.nav_chat_btn)
        
        layout.addStretch()
        
        # === User Info ===
        user_frame = QFrame()
        user_frame.setStyleSheet("""
            QFrame {
                background-color: #34495e;
                border-radius: 5px;
                padding: 10px;
            }
        """)
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
        
        # === Logout Button ===
        logout_btn = QPushButton("🚪 Logout")
        logout_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        logout_btn.clicked.connect(self.on_logout_clicked)
        layout.addWidget(logout_btn)
        
        return sidebar
    
    def _create_content_area(self) -> QWidget:
        """יצירת אזור התוכן"""
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # QStackedWidget - כאן יוצגו ה-Components
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.setStyleSheet("background-color: #ecf0f1;")
        layout.addWidget(self.stacked_widget)
        
        return content
    
    def _setup_microfrontends(self) -> None:
        """הגדרת Microfrontends Manager ורישום Components"""
        
        # יצירת Manager
        self.manager = MicrofrontendManager(self.stacked_widget)
        
        # === רישום Components ===
        
        # 1. ArticlesListComponent
        self.manager.register_component("articles_list", ArticlesListComponent)
        
        # כאן נרשום Components נוספים בעתיד:
        # self.manager.register_component("article_details", ArticleDetailsComponent)
        # self.manager.register_component("charts", ChartsComponent)
        # self.manager.register_component("llm_chat", LLMChatComponent)
        
        # === חיבור Presenters ===
        # נצטרך לעשות את זה אחרי שה-Component נטען
        self.manager.container.currentChanged.connect(self._on_component_changed)
    
    def _on_component_changed(self, index: int) -> None:
        """
        נקרא כאשר Component משתנה
        כאן נחבר את ה-Presenter
        """
        current_component = self.manager.get_current_component()
        
        if current_component and isinstance(current_component, ArticlesListComponent):
            # חבר Presenter אם עדיין לא מחובר
            if not current_component.presenter:
                presenter = ArticlesListPresenter(current_component, self.news_service)
                current_component.presenter = presenter
                
                # חבר signals
                current_component.article_clicked.connect(self.on_article_clicked)
    
    # ============================================
    # Navigation Methods
    # ============================================
    
    def navigate_to(self, component_name: str, **kwargs) -> None:
        """
        ניווט ל-Component
        
        Args:
            component_name: שם ה-Component
            **kwargs: פרמטרים להעברה
        """
        self.manager.navigate_to(component_name, **kwargs)
    
    def on_article_clicked(self, article_id: int) -> None:
        """
        נקרא כאשר לוחצים על מאמר
        
        בעתיד נטען ArticleDetailsComponent
        """
        print(f"Article {article_id} clicked!")
        # בעתיד:
        # self.navigate_to("article_details", article_id=article_id)
        
        from PySide6.QtWidgets import QMessageBox
        QMessageBox.information(
            self, 
            "Article Clicked", 
            f"You clicked article {article_id}\n\n(Article Details Component coming soon!)"
        )
    
    def show_coming_soon(self, feature: str) -> None:
        """הצגת הודעה שהתכונה בקרוב"""
        from PySide6.QtWidgets import QMessageBox
        QMessageBox.information(
            self, 
            "Coming Soon", 
            f"{feature} component is coming soon!\n\nStay tuned! 🚀"
        )
    
    def on_logout_clicked(self) -> None:
        """לחיצה על Logout"""
        from PySide6.QtWidgets import QMessageBox
        
        reply = QMessageBox.question(
            self,
            "Logout",
            "Are you sure you want to logout?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.logout_clicked.emit()
            self.close()