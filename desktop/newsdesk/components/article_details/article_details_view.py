from PySide6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QScrollArea,
    QWidget, QFrame, QTextBrowser, QSizePolicy
)
from PySide6.QtCore import Qt, Signal, QThread
from PySide6.QtGui import QFont, QPixmap, QResizeEvent
from typing import Dict, Any, Optional
import httpx

from newsdesk.components.base_component import BaseComponent
from newsdesk.mvp.model.article import Article


# ============================================
# Image Loader Thread
# ============================================
class ImageLoaderThread(QThread):
    """טוען תמונות באופן אסינכרוני"""
    image_loaded = Signal(QPixmap)
    load_error = Signal(str)
    
    def __init__(self, img_url):
        super().__init__()
        self.img_url = img_url
    
    def run(self):
        try:
            with httpx.Client() as client:
                r = client.get(self.img_url, follow_redirects=True, timeout=15)
                r.raise_for_status()
            
            px = QPixmap()
            if px.loadFromData(r.content):
                self.image_loaded.emit(px)
            else:
                self.load_error.emit("Failed to load image data.")
        except httpx.RequestError as e:
            self.load_error.emit(f"Network error: {e}")
        except Exception as e:
            self.load_error.emit(f"Error loading image: {e}")


# ============================================
# Article Details Component
# ============================================
class ArticleDetailsComponent(BaseComponent):
    """Component להצגת פרטי מאמר מלאים"""
    
    back_requested = Signal()
    like_toggled = Signal(int)
    dislike_toggled = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.presenter = None
        self.current_article_id: Optional[int] = None
        self.current_article_obj: Optional[Article] = None
        self.image_loader_thread: Optional[ImageLoaderThread] = None
        self.like_button: Optional[QPushButton] = None
        self.dislike_button: Optional[QPushButton] = None
        self.image_label: Optional[QLabel] = None
        self.original_pixmap: Optional[QPixmap] = None

    def setup_ui(self) -> None:
        """בניית הממשק"""
        # Header with back button
        header_layout = QHBoxLayout()
        self.back_button = QPushButton("⬅️ Back to List")
        self.back_button.setStyleSheet(self._get_button_style(button_type="secondary"))
        self.back_button.clicked.connect(self.back_requested.emit)
        header_layout.addWidget(self.back_button)
        header_layout.addStretch()
        self.main_layout.addLayout(header_layout)

        # Scroll area for content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #ecf0f1;
                padding: 0px;
            }
            QWidget {
                background-color: #ecf0f1;
            }
        """)

        scroll_widget = QWidget()
        self.content_layout = QVBoxLayout(scroll_widget)
        self.content_layout.setContentsMargins(30, 20, 30, 30)
        self.content_layout.setSpacing(18)

        scroll.setWidget(scroll_widget)
        self.main_layout.addWidget(scroll)

    def on_mount(self) -> None:
        """נקרא כשה-Component נטען"""
        super().on_mount()
        self.current_article_id = self.get_state("article_id")
        if self.current_article_id and self.presenter:
            self.presenter.load_article_details(self.current_article_id)
        else:
            self.show_error("Article ID not provided.")

    def on_unmount(self) -> None:
        """נקרא כשה-Component יורד"""
        super().on_unmount()
        if self.image_loader_thread and self.image_loader_thread.isRunning():
            self.image_loader_thread.quit()
            self.image_loader_thread.wait()
        self._clear_content_layout()
        self.current_article_id = None
        self.current_article_obj = None
        self.like_button = None
        self.dislike_button = None
        self.image_label = None
        self.original_pixmap = None

    def _clear_content_layout(self):
        """ניקוי כל הווידג'טים מה-layout"""
        for i in reversed(range(self.content_layout.count())):
            item = self.content_layout.itemAt(i)
            widget = item.widget()
            layout = item.layout()
            
            if widget is not None:
                widget.deleteLater()
            elif layout is not None:
                while layout.count():
                    child_item = layout.takeAt(0)
                    child_widget = child_item.widget()
                    if child_widget:
                        child_widget.deleteLater()
        
        self.like_button = None
        self.dislike_button = None
        self.image_label = None
        self.original_pixmap = None

    def display_article(self, article: Article) -> None:
        """הצגת פרטי המאמר המלאים"""
        
        # Debug output
        print(f"\n{'='*80}")
        print(f"📰 Displaying Article ID: {article.id}")
        print(f"📝 Title: {article.title}")
        print(f"📄 Content type: {type(article.content)}")
        print(f"📄 Content is None: {article.content is None}")
        print(f"📄 Content length: {len(article.content) if article.content else 0}")
        if article.content:
            print(f"📄 Content preview: {article.content[:200]}")
        print(f"{'='*80}\n")
        
        self._clear_content_layout()
        self.current_article_obj = article

        # 1. Category Badge
        cat_lbl = QLabel(article.category.upper() if article.category else 'GENERAL')
        cat_lbl.setStyleSheet(self._get_badge_style())
        cat_lbl.setMaximumWidth(120)
        cat_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.content_layout.addWidget(cat_lbl, alignment=Qt.AlignmentFlag.AlignLeft)
        
        # 2. Title
        title_lbl = QLabel(article.title or 'No Title')
        title_lbl.setWordWrap(True)
        title_font = QFont("Segoe UI", 22, QFont.Weight.Bold)
        title_lbl.setFont(title_font)
        title_lbl.setStyleSheet("color: #2c3e50; margin-bottom: 8px;")
        self.content_layout.addWidget(title_lbl)
        
        # 3. Meta (source + date)
        meta_layout = QHBoxLayout()
        src_lbl = QLabel(f"📰 {article.source or 'Unknown'}")
        src_lbl.setStyleSheet("color: #7f8c8d; font-size: 14px; margin-right: 15px;")
        meta_layout.addWidget(src_lbl)
        
        if article.published_at:
            try:
                date_str = article.published_at.strftime("%d %B %Y, %H:%M")
                date_lbl = QLabel(f"🕐 {date_str}")
                date_lbl.setStyleSheet("color: #7f8c8d; font-size: 14px;")
                meta_layout.addWidget(date_lbl)
            except AttributeError:
                pass
        
        meta_layout.addStretch()
        self.content_layout.addLayout(meta_layout)
        
        # 4. Like/Dislike Buttons
        likes_frame = QFrame()
        likes_layout = QHBoxLayout(likes_frame)
        likes_layout.setContentsMargins(0, 10, 0, 5)
        likes_layout.setSpacing(10)
        
        self.like_button = QPushButton("🤍 Like (0)")
        self.dislike_button = QPushButton("👎🏻 Dislike (0)")
        
        stats = self.presenter.get_current_stats(int(article.id)) if self.presenter else {}
        self.update_like_buttons(stats)
        
        self.like_button.setCheckable(True)
        self.dislike_button.setCheckable(True)
        self.like_button.clicked.connect(self._on_like_clicked)
        self.dislike_button.clicked.connect(self._on_dislike_clicked)
        
        likes_layout.addWidget(self.like_button)
        likes_layout.addWidget(self.dislike_button)
        likes_layout.addStretch()
        self.content_layout.addWidget(likes_frame)
        
        # 5. Divider
        divider = QFrame()
        divider.setFrameShape(QFrame.Shape.HLine)
        divider.setStyleSheet("background-color: #bdc3c7; max-height: 1px; margin: 10px 0;")
        self.content_layout.addWidget(divider)
        
        # 6. Image
        self.image_label = QLabel("Loading image...")
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setMinimumHeight(250)
        self.image_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.MinimumExpanding)
        self.image_label.setScaledContents(False)
        self.image_label.setStyleSheet("background-color: #dfe6e9; border: 1px solid #bdc3c7; border-radius: 8px; color: #7f8c8d;")
        self.content_layout.addWidget(self.image_label)
        
        if article.image_url:
            self.load_image_async(article.image_url)
        else:
            self.image_label.setText("🖼️ No Image")
        
        # 7. Summary
        if article.summary and len(article.summary.strip()) > 0:
            sum_lbl = QLabel(f"{article.summary}")
            sum_lbl.setWordWrap(True)
            sum_lbl.setStyleSheet(self._get_summary_box_style())
            self.content_layout.addWidget(sum_lbl)
        
        # 8. Content - הצגת התוכן המלא
        if article.content and len(article.content.strip()) > 0:
            print(f"✅ Displaying content ({len(article.content)} chars)")
            
            content_browser = QTextBrowser()
            content_browser.setReadOnly(True)  # ✅ הוסף את זה
            content_browser.setFocusPolicy(Qt.FocusPolicy.NoFocus)  # ✅ וגם את זה
            
            # בדוק אם זה HTML או טקסט רגיל
            if "<body" in article.content.lower() or "<p>" in article.content.lower() or "<br" in article.content.lower():
                content_browser.setHtml(article.content)
            else:
                content_browser.setPlainText(article.content)
            
                content_browser.setStyleSheet("""
                    QTextBrowser {
                        background-color: white;
                        color: #2c3e50;
                        border: 1px solid #bdc3c7;
                        border-radius: 5px;
                        padding: 15px;
                        font-size: 14px;
                        line-height: 1.6;
                    }
                """)
                content_browser.setOpenExternalLinks(True)
                content_browser.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
                
                self.content_layout.addWidget(content_browser, 1)

        else:
            print(f"❌ No content to display (content: {repr(article.content)})")
            no_cont_lbl = QLabel("📄 Full content not available.")
            no_cont_lbl.setStyleSheet("color: #95a5a6; font-style: italic; padding: 20px;")
            no_cont_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.content_layout.addWidget(no_cont_lbl)
        
        self.content_layout.addStretch()

    def load_image_async(self, url: str):
        """טעינת תמונה באופן אסינכרוני"""
        if self.image_loader_thread and self.image_loader_thread.isRunning():
            self.image_loader_thread.quit()
            self.image_loader_thread.wait()
        
        self.image_loader_thread = ImageLoaderThread(url)
        self.image_loader_thread.image_loaded.connect(self._set_image)
        self.image_loader_thread.load_error.connect(self._image_load_error)
        self.image_loader_thread.start()

    def _set_image(self, pixmap: QPixmap):
        """שמירת התמונה והצגתה"""
        self.original_pixmap = pixmap
        if self.image_label:
            self.image_label.setStyleSheet("background-color: transparent; border: none; border-radius: 8px;")
            self._resize_image_label()

    def _image_load_error(self, error_message: str):
        """טיפול בשגיאת טעינת תמונה"""
        print(f"Image load error: {error_message}")
        if self.image_label:
            self.image_label.setText("🖼️ Image not available")
            self.image_label.setStyleSheet("""
                background-color: #dfe6e9;
                border: 1px solid #bdc3c7;
                border-radius: 8px;
                color: #e74c3c;
                font-weight: bold;
                padding: 20px;
            """)
            self.image_label.setMinimumHeight(100)
            self.image_label.setScaledContents(False)
        self.original_pixmap = None

    def resizeEvent(self, event: QResizeEvent) -> None:
        """שינוי גודל התמונה כשהחלון משתנה"""
        super().resizeEvent(event)
        self._resize_image_label()

    def _resize_image_label(self):
        """שינוי גודל התמונה לפי רוחב החלון"""
        if self.image_label and self.original_pixmap:
            label_width = self.image_label.width() - 2
            if label_width > 50:
                scaled_pixmap = self.original_pixmap.scaledToWidth(
                    label_width,
                    Qt.TransformationMode.SmoothTransformation
                )
                if self.image_label:
                    self.image_label.setPixmap(scaled_pixmap)

    def _on_like_clicked(self):
        """טיפול בלחיצה על Like"""
        if self.current_article_obj:
            self.like_toggled.emit(int(self.current_article_obj.id))

    def _on_dislike_clicked(self):
        """טיפול בלחיצה על Dislike"""
        if self.current_article_obj:
            self.dislike_toggled.emit(int(self.current_article_obj.id))

    def update_like_buttons(self, stats: Dict[str, Any]):
        """עדכון כפתורי Like/Dislike"""
        if not self.like_button or not self.dislike_button:
            print("Warning: Like buttons not found in update_like_buttons")
            return

        likes_count = stats.get("likes_count", 0)
        dislikes_count = stats.get("dislikes_count", 0)
        user_liked = stats.get("user_liked", False)
        user_disliked = stats.get("user_disliked", False)

        # Update Like button
        like_icon = "❤️" if user_liked else "🤍"
        self.like_button.setText(f"{like_icon} Like ({likes_count})")
        self.like_button.setStyleSheet(self._get_button_style(button_type="like", active=user_liked))
        self.like_button.blockSignals(True)
        self.like_button.setChecked(user_liked)
        self.like_button.blockSignals(False)

        # Update Dislike button
        dislike_icon = "👎" if user_disliked else "👎🏻"
        self.dislike_button.setText(f"{dislike_icon} Dislike ({dislikes_count})")
        self.dislike_button.setStyleSheet(self._get_button_style(button_type="dislike", active=user_disliked))
        self.dislike_button.blockSignals(True)
        self.dislike_button.setChecked(user_disliked)
        self.dislike_button.blockSignals(False)

    # ============================================
    # Style Helper Methods
    # ============================================
    
    def _get_button_style(self, button_type: str, active: bool = False) -> str:
        """מחזיר CSS לסוגי כפתורים שונים"""
        font_size = "13px"
        padding = "8px 16px"
        min_width = "110px"
        
        if button_type == "secondary":
            return f"""
                QPushButton {{
                    background-color: #95a5a6;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    padding: {padding};
                    font-weight: bold;
                    font-size: {font_size};
                    max-width: 130px;
                }}
                QPushButton:hover {{
                    background-color: #7f8c8d;
                }}
                QPushButton:pressed {{
                    background-color: #596275;
                }}
            """
        
        elif button_type == "like":
            bg = "#e74c3c" if active else "#bdc3c7"
            hover = "#c0392b" if active else "#95a5a6"
            press = "#a52a1a" if active else "#7f8c8d"
            border = "1px solid #c0392b" if active else "none"
            return f"""
                QPushButton {{
                    background-color: {bg};
                    color: white;
                    border: {border};
                    border-radius: 5px;
                    padding: {padding};
                    font-size: {font_size};
                    min-width: {min_width};
                }}
                QPushButton:hover {{
                    background-color: {hover};
                }}
                QPushButton:pressed {{
                    background-color: {press};
                }}
                QPushButton:checked {{
                    background-color: {bg};
                    border: {border};
                }}
            """
        
        elif button_type == "dislike":
            bg = "#3498db" if active else "#bdc3c7"
            hover = "#2980b9" if active else "#95a5a6"
            press = "#21618c" if active else "#7f8c8d"
            border = "1px solid #2980b9" if active else "none"
            return f"""
                QPushButton {{
                    background-color: {bg};
                    color: white;
                    border: {border};
                    border-radius: 5px;
                    padding: {padding};
                    font-size: {font_size};
                    min-width: {min_width};
                }}
                QPushButton:hover {{
                    background-color: {hover};
                }}
                QPushButton:pressed {{
                    background-color: {press};
                }}
                QPushButton:checked {{
                    background-color: {bg};
                    border: {border};
                }}
            """
        
        else:  # Default
            return f"""
                QPushButton {{
                    background-color: #3498db;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    padding: {padding};
                    font-weight: bold;
                    font-size: {font_size};
                }}
                QPushButton:hover {{
                    background-color: #2980b9;
                }}
                QPushButton:pressed {{
                    background-color: #21618c;
                }}
            """

    def _get_badge_style(self) -> str:
        """סטייל ל-badge של קטגוריה"""
        return """
            QLabel {
                background-color: #1abc9c;
                color: white;
                padding: 4px 10px;
                border-radius: 10px;
                font-size: 11px;
                font-weight: bold;
                margin-bottom: 5px;
            }
        """

    def _get_summary_box_style(self) -> str:
        """סטייל לסיכום"""
        return """
            QLabel {
                background-color: #ffffff;
                color: #34495e;
                font-size: 14px;
                border: 1px solid #bdc3c7;
                border-left: 4px solid #3498db;
                border-radius: 5px;
                padding: 12px;
                margin-top: 15px;
                margin-bottom: 5px;
            }
        """