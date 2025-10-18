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
    dislike_clicked = Signal(Article)
    
    def __init__(self, article: Article, likes_count: int = 0, dislikes_count: int = 0, 
                 user_liked: bool = False, user_disliked: bool = False):
        super().__init__()
        self.article = article
        self.likes_count = likes_count
        self.dislikes_count = dislikes_count
        self.user_liked = user_liked
        self.user_disliked = user_disliked
        
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setStyleSheet("""
            ArticleCard {
                background-color: #2d2d2d;
                border-radius: 12px;
                padding: 10px;
                margin: 4px;
            }
            ArticleCard:hover {
                background-color: #3d3d3d;
                border: 2px solid #4a9eff;
            }
        """)
        
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMaximumHeight(110)
        self.setMaximumWidth(800)
        
        layout = QHBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(8, 8, 8, 8)
        
        self.image_label = QLabel()
        self.image_label.setFixedSize(90, 90)
        self.image_label.setStyleSheet("""
            QLabel {
                background-color: #1a1a1a;
                border-radius: 8px;
                border: 2px solid #444;
            }
        """)
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
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
        image_font.setPointSize(32)
        self.image_label.setFont(image_font)
        
        layout.addWidget(self.image_label)
        
        content_layout = QVBoxLayout()
        content_layout.setSpacing(3)
        
        title_label = QLabel(article.title)
        title_label.setWordWrap(True)
        title_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 13px;
                font-weight: bold;
            }
        """)
        title_label.setMaximumHeight(35)
        content_layout.addWidget(title_label)
        
        summary_text = article.summary if article.summary else "No summary available"
        if len(summary_text) > 90:
            summary_text = summary_text[:90] + "..."
        
        summary_label = QLabel(summary_text)
        summary_label.setWordWrap(True)
        summary_label.setStyleSheet("""
            QLabel {
                color: #aaaaaa;
                font-size: 11px;
            }
        """)
        summary_label.setMaximumHeight(30)
        content_layout.addWidget(summary_label)
        
        meta_layout = QHBoxLayout()
        meta_layout.setSpacing(8)
        
        source_label = QLabel(f"📰 {article.source}")
        source_label.setStyleSheet("color: #888; font-size: 10px;")
        meta_layout.addWidget(source_label)
        
        meta_layout.addStretch()
        
        like_icon = "❤️" if user_liked else "🤍"
        self.like_btn = QPushButton(f"{like_icon} {likes_count}")
        self.like_btn.setFixedSize(60, 24)
        self.like_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {'#ff4444' if user_liked else '#444'};
                color: white;
                border: none;
                border-radius: 10px;
                padding: 2px 8px;
                font-size: 11px;
            }}
            QPushButton:hover {{
                background-color: {'#ff6666' if user_liked else '#666'};
            }}
        """)
        self.like_btn.clicked.connect(lambda: self.like_clicked.emit(self.article))
        meta_layout.addWidget(self.like_btn)
        
        dislike_icon = "👎" if user_disliked else "👎🏻"
        self.dislike_btn = QPushButton(f"{dislike_icon} {dislikes_count}")
        self.dislike_btn.setFixedSize(60, 24)
        self.dislike_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {'#4444ff' if user_disliked else '#444'};
                color: white;
                border: none;
                border-radius: 10px;
                padding: 2px 8px;
                font-size: 11px;
            }}
            QPushButton:hover {{
                background-color: {'#6666ff' if user_disliked else '#666'};
            }}
        """)
        self.dislike_btn.clicked.connect(lambda: self.dislike_clicked.emit(self.article))
        meta_layout.addWidget(self.dislike_btn)
        
        content_layout.addLayout(meta_layout)
        layout.addLayout(content_layout)
    
    def update_stats(self, likes_count: int, dislikes_count: int, user_liked: bool, user_disliked: bool):
        """עדכון סטטיסטיקות"""
        self.likes_count = likes_count
        self.dislikes_count = dislikes_count
        self.user_liked = user_liked
        self.user_disliked = user_disliked
        
        like_icon = "❤️" if user_liked else "🤍"
        dislike_icon = "👎" if user_disliked else "👎🏻"
        
        self.like_btn.setText(f"{like_icon} {likes_count}")
        self.like_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {'#ff4444' if user_liked else '#444'};
                color: white;
                border: none;
                border-radius: 10px;
                padding: 2px 8px;
                font-size: 11px;
            }}
            QPushButton:hover {{
                background-color: {'#ff6666' if user_liked else '#666'};
            }}
        """)
        
        self.dislike_btn.setText(f"{dislike_icon} {dislikes_count}")
        self.dislike_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {'#4444ff' if user_disliked else '#444'};
                color: white;
                border: none;
                border-radius: 10px;
                padding: 2px 8px;
                font-size: 11px;
            }}
            QPushButton:hover {{
                background-color: {'#6666ff' if user_disliked else '#666'};
            }}
        """)
    
    def mousePressEvent(self, event):
        """לחיצה על הכרטיס"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.article)


class ArticlesWindow(QMainWindow):
    """חלון מאמרים מעוצב"""
    article_card_clicked = Signal(Article)
    like_button_clicked = Signal(Article)
    dislike_button_clicked = Signal(Article)
    logout_clicked = Signal()
    
    def __init__(self, is_admin: bool = False, username: str = "User"):
        super().__init__()
        self.is_admin = is_admin
        self.username = username
        self.setWindowTitle("NewsDesk 📰")
        self.setMinimumSize(1000, 700)
        self._card_widgets: Dict[str, Dict[int, ArticleCard]] = {}

        self.setStyleSheet("""
            QMainWindow {
                background-color: #1a1a2e;
            }
            QTabWidget::pane {
                border: 1px solid #444;
                background-color: #1a1a2e;
                border-radius: 8px;
            }
            QTabBar::tab {
                background-color: #2d2d2d;
                color: #aaa;
                padding: 10px 20px;
                margin-right: 2px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                font-size: 13px;
            }
            QTabBar::tab:selected {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #4a9eff,
                    stop:1 #00d4ff
                );
                color: white;
                font-weight: bold;
            }
            QLineEdit {
                background-color: rgba(255, 255, 255, 0.05);
                color: white;
                border: 2px solid rgba(74, 158, 255, 0.2);
                border-radius: 10px;
                padding: 10px 15px;
                font-size: 13px;
            }
            QLineEdit:focus {
                border: 2px solid #4a9eff;
                background-color: rgba(255, 255, 255, 0.08);
            }
            QLineEdit::placeholder {
                color: #8892b0;
            }
            QScrollArea {
                border: none;
                background-color: #1a1a2e;
            }
            QPushButton {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #4a9eff,
                    stop:1 #00d4ff
                );
                color: white;
                border: none;
                border-radius: 10px;
                padding: 10px 20px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #5ab0ff,
                    stop:1 #20e4ff
                );
            }
            QLabel {
                color: #aaa;
            }
            QMenu {
                background-color: #2d2d2d;
                color: white;
                border: 1px solid #444;
                border-radius: 8px;
                padding: 5px;
            }
            QMenu::item {
                padding: 8px 20px;
                border-radius: 5px;
            }
            QMenu::item:selected {
                background-color: #4a9eff;
            }
        """)
        
        self._setup_ui()
        self._center_on_screen()
    
    def _center_on_screen(self):
        screen = self.screen().geometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)
    
    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        header_layout = QHBoxLayout()
        
        title = QLabel("📰 NewsDesk")
        title_font = QFont()
        title_font.setPointSize(22)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet("""
            QLabel {
                color: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #4a9eff,
                    stop:1 #00d4ff
                );
            }
        """)
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        if self.is_admin:
            admin_btn = QPushButton("👑 Admin Panel")
            admin_btn.setMaximumWidth(150)
            admin_btn.clicked.connect(self._show_admin_panel)
            header_layout.addWidget(admin_btn)
        
        self.profile_btn = QPushButton(f"👤 {self.username}")
        self.profile_btn.setMaximumWidth(180)
        self.profile_btn.clicked.connect(self._show_profile_menu)
        header_layout.addWidget(self.profile_btn)
        
        main_layout.addLayout(header_layout)
        
        self._tabs = QTabWidget()
        self._per_cat_widgets: Dict[str, Dict[str, object]] = {}
        
        for cat in CATS:
            page = QWidget()
            page_layout = QVBoxLayout(page)
            page_layout.setSpacing(10)
            
            search = QLineEdit()
            search.setPlaceholderText(f"🔍 חיפוש ב-{cat}...")
            search.setMaximumHeight(45)
            page_layout.addWidget(search)
            
            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            
            scroll_content = QWidget()
            scroll_layout = QVBoxLayout(scroll_content)
            scroll_layout.setSpacing(8)
            
            scroll.setWidget(scroll_content)
            page_layout.addWidget(scroll)
            
            status = QLabel("")
            status.setStyleSheet("color: #888; font-size: 11px;")
            page_layout.addWidget(status)
            
            self._tabs.addTab(page, cat.capitalize())
            
            self._per_cat_widgets[cat] = {
                "search": search,
                "scroll_layout": scroll_layout,
                "status": status
            }
        
        main_layout.addWidget(self._tabs)
    
    def _show_profile_menu(self):
        menu = QMenu(self)
        info_action = QAction(f"👤 {self.username}", self)
        info_action.setEnabled(False)
        menu.addAction(info_action)
        menu.addSeparator()
        settings_action = QAction("⚙️ Settings", self)
        settings_action.triggered.connect(self._show_settings)
        menu.addAction(settings_action)
        logout_action = QAction("🚪 Logout", self)
        logout_action.triggered.connect(self._logout)
        menu.addAction(logout_action)
        menu.exec(self.profile_btn.mapToGlobal(self.profile_btn.rect().bottomLeft()))
    
    def _logout(self):
        reply = QMessageBox.question(
            self, "Logout", "Are you sure you want to logout?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.logout_clicked.emit()
            self.close()

    def _show_settings(self):
        msg = QMessageBox(self)
        msg.setWindowTitle("Settings")
        msg.setText("Settings - Coming Soon!")
        msg.exec()

    def set_articles(self, cat: str, articles: List[Article], likes_data: Dict[int, Dict] = None):
        scroll_layout = self._per_cat_widgets[cat]["scroll_layout"]
        
        while scroll_layout.count():
            child = scroll_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        self._card_widgets[cat] = {}
        
        for article in articles:
            article_id = int(article.id)
            stats = likes_data.get(article_id, {})
            
            card = ArticleCard(
                article=article,
                likes_count=stats.get("likes_count", 0),
                dislikes_count=stats.get("dislikes_count", 0),
                user_liked=stats.get("user_liked", False),
                user_disliked=stats.get("user_disliked", False)
            )
            
            card.clicked.connect(self.article_card_clicked.emit)
            card.like_clicked.connect(self.like_button_clicked.emit)
            card.dislike_clicked.connect(self.dislike_button_clicked.emit)
            
            scroll_layout.addWidget(card)
            self._card_widgets[cat][article_id] = card
        
        scroll_layout.addStretch()
        self._per_cat_widgets[cat]["status"].setText(f"{len(articles)} כתבות")

    def update_article_card(self, cat: str, article_id: int, stats: Dict):
        if cat in self._card_widgets and article_id in self._card_widgets[cat]:
            card = self._card_widgets[cat][article_id]
            card.update_stats(
                likes_count=stats.get("likes_count", 0),
                dislikes_count=stats.get("dislikes_count", 0),
                user_liked=stats.get("user_liked", False),
                user_disliked=stats.get("user_disliked", False)
            )

    def _show_admin_panel(self):
        msg = QMessageBox(self)
        msg.setWindowTitle("Admin")
        msg.setText("Admin Panel - Coming Soon!")
        msg.exec()
    
    def search_box(self, cat: str) -> QLineEdit:
        return self._per_cat_widgets[cat]["search"]
    
    @property
    def categories(self) -> List[str]:
        return CATS