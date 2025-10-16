# newsdesk/mvp/view/article_detail_window.py
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QScrollArea, QWidget, QFrame
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from newsdesk.mvp.model.article import Article
from datetime import datetime

class ArticleDetailWindow(QDialog):
    """חלון פרטי מאמר מעוצב"""
    
    like_clicked = Signal(Article)
    
    def __init__(self, article: Article, likes_count: int = 0, user_liked: bool = False, parent=None):
        super().__init__(parent)
        self.article = article
        self.likes_count = likes_count
        self.user_liked = user_liked
        
        self.setWindowTitle(article.title)
        self.setMinimumSize(700, 550)  # ← הקטנתי מ-800x600
        self.setModal(True)
        
        # Dark theme - עיצוב זהה לשאר האפליקציה
        self.setStyleSheet("""
            QDialog {
                background-color: #1a1a2e;
            }
            QLabel {
                color: #ffffff;
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
            QScrollArea {
                border: none;
            }
        """)
        
        self._setup_ui()
        self._center_on_parent()
    
    def _center_on_parent(self):
        """מרכז את החלון ביחס ל-parent"""
        if self.parent():
            parent_geo = self.parent().geometry()
            x = parent_geo.x() + (parent_geo.width() - self.width()) // 2
            y = parent_geo.y() + (parent_geo.height() - self.height()) // 2
            self.move(x, y)
    
    def _setup_ui(self):
        """בניית הממשק"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(15)
        
        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setSpacing(12)
        
        # Category badge
        category_label = QLabel(self.article.category.upper())
        category_label.setStyleSheet("""
            QLabel {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #4a9eff,
                    stop:1 #00d4ff
                );
                color: white;
                padding: 5px 15px;
                border-radius: 12px;
                font-size: 11px;
                font-weight: bold;
            }
        """)
        category_label.setMaximumWidth(120)
        scroll_layout.addWidget(category_label)
        
        # כותרת
        title_label = QLabel(self.article.title)
        title_label.setWordWrap(True)
        title_font = QFont()
        title_font.setPointSize(20)  # ← הקטנתי מ-22
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet("""
            QLabel {
                color: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #ffffff,
                    stop:1 #cccccc
                );
            }
        """)
        scroll_layout.addWidget(title_label)
        
        # Meta info
        meta_layout = QHBoxLayout()
        
        source_label = QLabel(f"📰 {self.article.source}")
        source_label.setStyleSheet("color: #888; font-size: 13px;")
        meta_layout.addWidget(source_label)
        
        # תאריך
        if self.article.published_at:
            date_str = self.article.published_at.strftime("%d/%m/%Y %H:%M")
            date_label = QLabel(f"🕐 {date_str}")
            date_label.setStyleSheet("color: #888; font-size: 13px;")
            meta_layout.addWidget(date_label)
        
        meta_layout.addStretch()
        scroll_layout.addLayout(meta_layout)
        
        # Divider
        divider = QFrame()
        divider.setFrameShape(QFrame.Shape.HLine)
        divider.setStyleSheet("background-color: #444; max-height: 1px;")
        scroll_layout.addWidget(divider)
        
        # תמונה גדולה (placeholder)
        image_label = QLabel()
        image_label.setFixedHeight(250)  # ← הקטנתי מ-300
        image_label.setStyleSheet("""
            QLabel {
                background-color: #2d2d2d;
                border-radius: 12px;
                border: 2px solid #444;
            }
        """)
        image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Emoji לפי קטגוריה
        emoji = "📰"
        if self.article.category.lower() == 'sports':
            emoji = "⚽"
        elif self.article.category.lower() == 'economy':
            emoji = "💰"
        elif self.article.category.lower() == 'politics':
            emoji = "🏛️"
        
        image_label.setText(emoji)
        image_font = QFont()
        image_font.setPointSize(70)  # ← הקטנתי מ-80
        image_label.setFont(image_font)
        scroll_layout.addWidget(image_label)
        
        # סיכום
        if self.article.summary:
            summary_label = QLabel(self.article.summary)
            summary_label.setWordWrap(True)
            summary_label.setStyleSheet("""
                QLabel {
                    color: #cccccc;
                    font-size: 14px;
                    line-height: 1.6;
                    padding: 15px;
                    background-color: #2d2d2d;
                    border-radius: 10px;
                    border-left: 3px solid #4a9eff;
                }
            """)
            scroll_layout.addWidget(summary_label)
        
        # AI Analysis (אנימ)
        ai_frame = QFrame()
        ai_frame.setStyleSheet("""
            QFrame {
                background-color: #2d2d2d;
                border-radius: 10px;
                padding: 12px;
            }
        """)
        ai_layout = QVBoxLayout(ai_frame)
        
        ai_title = QLabel("🤖 AI Analysis")
        ai_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #4a9eff;")
        ai_layout.addWidget(ai_title)
        
        sentiment_label = QLabel("😊 Sentiment: Positive (85% confidence)")
        sentiment_label.setStyleSheet("color: #aaa; font-size: 13px;")
        ai_layout.addWidget(sentiment_label)
        
        scroll_layout.addWidget(ai_frame)
        
        scroll_layout.addStretch()
        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)
        
        # Bottom bar
        bottom_layout = QHBoxLayout()
        
        # Like button
        heart = "❤️" if self.user_liked else "🤍"
        self.like_btn = QPushButton(f"{heart} {self.likes_count} Likes")
        self.like_btn.setMaximumWidth(150)
        self.like_btn.clicked.connect(self._on_like_clicked)
        bottom_layout.addWidget(self.like_btn)
        
        bottom_layout.addStretch()
        
        # Close button
        close_btn = QPushButton("✖ Close")
        close_btn.setMaximumWidth(120)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: 2px solid rgba(74, 158, 255, 0.5);
                color: #4a9eff;
            }
            QPushButton:hover {
                border: 2px solid #4a9eff;
                background-color: rgba(74, 158, 255, 0.1);
            }
        """)
        close_btn.clicked.connect(self.close)
        bottom_layout.addWidget(close_btn)
        
        layout.addLayout(bottom_layout)
    
    def _on_like_clicked(self):
        """לייק נלחץ"""
        self.like_clicked.emit(self.article)
        
        # עדכן UI
        self.user_liked = not self.user_liked
        if self.user_liked:
            self.likes_count += 1
        else:
            self.likes_count = max(0, self.likes_count - 1)
        
        heart = "❤️" if self.user_liked else "🤍"
        self.like_btn.setText(f"{heart} {self.likes_count} Likes")