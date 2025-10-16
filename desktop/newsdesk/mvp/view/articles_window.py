# newsdesk/mvp/view/articles_window.py
from typing import List, Optional, Dict
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit,
    QScrollArea, QPushButton, QLabel, QFrame, QTabWidget, QMessageBox, QMenu
)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QPixmap, QFont, QIcon, QAction

from newsdesk.mvp.model.article import Article

CATS = ["sports", "economy", "politics"]

class ArticleCard(QFrame):
    """כרטיס מאמר מעוצב"""
    clicked = Signal(Article)
    like_clicked = Signal(Article)
    
    def __init__(self, article: Article, likes_count: int = 0, user_liked: bool = False):
        super().__init__()
        self.article = article
        self.likes_count = likes_count
        self.user_liked = user_liked
        
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setStyleSheet("""
            ArticleCard {
                background-color: #2d2d2d;
                border-radius: 12px;
                padding: 15px;
                margin: 5px;
            }
            ArticleCard:hover {
                background-color: #3d3d3d;
                border: 2px solid #4a9eff;
            }
        """)
        
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMaximumHeight(180)
        
        layout = QHBoxLayout(self)
        
        # תמונה (placeholder)
        self.image_label = QLabel()
        self.image_label.setFixedSize(150, 150)
        self.image_label.setStyleSheet("""
            QLabel {
                background-color: #1a1a1a;
                border-radius: 8px;
                border: 2px solid #444;
            }
        """)
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # תמונה - emoji גדול
        emoji_text = "📰"
        if hasattr(article, 'category'):
            if article.category.lower() == 'sports':
                emoji_text = "⚽"
            elif article.category.lower() == 'economy':
                emoji_text = "💰"
            elif article.category.lower() == 'politics':
                emoji_text = "🏛️"
        
        self.image_label.setText(emoji_text)
        
        image_font = QFont()
        image_font.setPointSize(48)
        self.image_label.setFont(image_font)
        
        layout.addWidget(self.image_label)
        
        # תוכן
        content_layout = QVBoxLayout()
        
        # כותרת
        title_label = QLabel(article.title)
        title_label.setWordWrap(True)
        title_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 16px;
                font-weight: bold;
            }
        """)
        content_layout.addWidget(title_label)
        
        # סיכום
        summary_text = article.summary if article.summary else "No summary available"
        if len(summary_text) > 150:
            summary_text = summary_text[:150] + "..."
        
        summary_label = QLabel(summary_text)
        summary_label.setWordWrap(True)
        summary_label.setStyleSheet("""
            QLabel {
                color: #aaaaaa;
                font-size: 13px;
            }
        """)
        content_layout.addWidget(summary_label)
        
        # מטא דאטה
        meta_layout = QHBoxLayout()
        
        source_label = QLabel(f"📍 {article.source}")
        source_label.setStyleSheet("color: #888; font-size: 12px;")
        meta_layout.addWidget(source_label)
        
        meta_layout.addStretch()
        
        # Sentiment (אם יש)
        sentiment_label = QLabel("😊")
        sentiment_label.setStyleSheet("font-size: 18px;")
        meta_layout.addWidget(sentiment_label)
        
        # כפתור לייק
        heart = "❤️" if user_liked else "🤍"
        self.like_btn = QPushButton(f"{heart} {likes_count}")
        self.like_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {'#ff4444' if user_liked else '#444'};
                color: white;
                border: none;
                border-radius: 15px;
                padding: 5px 15px;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: #ff6666;
            }}
        """)
        self.like_btn.clicked.connect(lambda: self.like_clicked.emit(self.article))
        meta_layout.addWidget(self.like_btn)
        
        content_layout.addLayout(meta_layout)
        layout.addLayout(content_layout)
    
    def mousePressEvent(self, event):
        """לחיצה על הכרטיס"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.article)


class ArticlesWindow(QMainWindow):
    """חלון מאמרים מעוצב"""
    
    logout_clicked = Signal()  # סיגנל ליציאה
    
    def __init__(self, is_admin: bool = False, username: str = "User"):
        super().__init__()
        self.is_admin = is_admin
        self.username = username
        self.setWindowTitle("NewsDesk 📰")
        self.setMinimumSize(1200, 800)
        
        # Dark theme
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1a1a1a;
            }
            QTabWidget::pane {
                border: 1px solid #444;
                background-color: #1a1a1a;
            }
            QTabBar::tab {
                background-color: #2d2d2d;
                color: #aaa;
                padding: 10px 20px;
                margin-right: 2px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
            }
            QTabBar::tab:selected {
                background-color: #4a9eff;
                color: white;
            }
            QLineEdit {
                background-color: #2d2d2d;
                color: white;
                border: 2px solid #444;
                border-radius: 8px;
                padding: 10px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 2px solid #4a9eff;
            }
            QScrollArea {
                border: none;
                background-color: #1a1a1a;
            }
            QPushButton {
                background-color: #4a9eff;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #5ab0ff;
            }
            QLabel {
                color: #aaa;
            }
            QMenu {
                background-color: #2d2d2d;
                color: white;
                border: 1px solid #444;
            }
            QMenu::item:selected {
                background-color: #4a9eff;
            }
        """)
        
        self._setup_ui()
    
    def _setup_ui(self):
        """בניית הממשק"""
        central = QWidget()
        self.setCentralWidget(central)
        
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        header_layout = QHBoxLayout()
        
        title = QLabel("📰 NewsDesk")
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet("color: #4a9eff;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Admin button
        if self.is_admin:
            admin_btn = QPushButton("👑 Admin Panel")
            admin_btn.clicked.connect(self._show_admin_panel)
            header_layout.addWidget(admin_btn)
        
        # Profile button with menu
        self.profile_btn = QPushButton(f"👤 {self.username}")
        self.profile_btn.clicked.connect(self._show_profile_menu)
        header_layout.addWidget(self.profile_btn)
        
        main_layout.addLayout(header_layout)
        
        # Tabs
        self._tabs = QTabWidget()
        self._per_cat_widgets: Dict[str, Dict[str, object]] = {}
        
        for cat in CATS:
            page = QWidget()
            page_layout = QVBoxLayout(page)
            
            # Search box
            search = QLineEdit()
            search.setPlaceholderText(f"🔍 חיפוש ב-{cat}...")
            page_layout.addWidget(search)
            
            # Scroll area for cards
            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            
            scroll_content = QWidget()
            scroll_layout = QVBoxLayout(scroll_content)
            scroll_layout.setSpacing(10)
            
            scroll.setWidget(scroll_content)
            page_layout.addWidget(scroll)
            
            # Status
            status = QLabel("")
            status.setStyleSheet("color: #888; font-size: 12px;")
            page_layout.addWidget(status)
            
            self._tabs.addTab(page, cat.capitalize())
            
            self._per_cat_widgets[cat] = {
                "search": search,
                "scroll_layout": scroll_layout,
                "status": status
            }
        
        main_layout.addWidget(self._tabs)
    
    def _show_profile_menu(self):
        """הצג תפריט פרופיל"""
        menu = QMenu(self)
        
        # Profile info
        info_action = QAction(f"👤 {self.username}", self)
        info_action.setEnabled(False)
        menu.addAction(info_action)
        
        menu.addSeparator()
        
        # Settings
        settings_action = QAction("⚙️ Settings", self)
        settings_action.triggered.connect(self._show_settings)
        menu.addAction(settings_action)
        
        # Logout
        logout_action = QAction("🚪 Logout", self)
        logout_action.triggered.connect(self._logout)
        menu.addAction(logout_action)
        
        # Show menu at button position
        menu.exec(self.profile_btn.mapToGlobal(self.profile_btn.rect().bottomLeft()))
    
    def _logout(self):
        """יציאה מהמערכת"""
        reply = QMessageBox.question(
            self,
            "Logout",
            "Are you sure you want to logout?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.logout_clicked.emit()
            self.close()
    
    def _show_settings(self):
        """הגדרות"""
        QMessageBox.information(self, "Settings", "Settings - Coming Soon!")
    
    def set_articles(self, cat: str, articles: List[Article], likes_data: Dict[int, Dict] = None):
        """הצגת מאמרים בכרטיסים"""
        scroll_layout = self._per_cat_widgets[cat]["scroll_layout"]
        
        # נקה קודם
        while scroll_layout.count():
            child = scroll_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        # הוסף כרטיסים
        for article in articles:
            likes_count = 0
            user_liked = False
            
            if likes_data and int(article.id) in likes_data:
                likes_count = likes_data[int(article.id)].get("likes_count", 0)
                user_liked = likes_data[int(article.id)].get("user_liked", False)
            
            card = ArticleCard(article, likes_count, user_liked)
            card.clicked.connect(self._on_article_clicked)
            card.like_clicked.connect(self._on_like_clicked)
            scroll_layout.addWidget(card)
        
        scroll_layout.addStretch()
        
        # Status
        self._per_cat_widgets[cat]["status"].setText(f"{len(articles)} כתבות")
    
    def _on_article_clicked(self, article: Article):
        """לחיצה על מאמר"""
        QMessageBox.information(
            self,
            article.title,
            f"{article.summary}\n\nSource: {article.source}"
        )
    
    def _on_like_clicked(self, article: Article):
        """לייק למאמר"""
        print(f"Like article {article.id}")
    
    def _show_admin_panel(self):
        """פתח Admin Panel"""
        QMessageBox.information(self, "Admin", "Admin Panel - Coming Soon!")
    
    def search_box(self, cat: str) -> QLineEdit:
        return self._per_cat_widgets[cat]["search"]
    
    @property
    def categories(self) -> List[str]:
        return CATS