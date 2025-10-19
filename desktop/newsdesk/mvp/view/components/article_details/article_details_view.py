# desktop/newsdesk/mvp/view/components/article_details/article_details_view.py
"""
ArticleDetailsComponent - View
הצגת פרטים מלאים של מאמר
"""
from PySide6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QScrollArea,
    QWidget, QFrame, QTextBrowser
)
from PySide6.QtCore import Qt, Signal, QThread
from PySide6.QtGui import QFont, QPixmap
from typing import Dict, Any, Optional
import httpx # נייבא לקריאת תמונה

from newsdesk.mvp.view.components.base_component import BaseComponent
from newsdesk.mvp.model.article import Article # נייבא את המודל המלא

# ImageLoaderThread (ללא שינוי)
class ImageLoaderThread(QThread):
    image_loaded = Signal(QPixmap)
    load_error = Signal(str)
    def __init__(self, img_url):
        super().__init__()
        self.img_url = img_url
    def run(self):
        try:
            with httpx.Client() as client:
                response = client.get(self.img_url, follow_redirects=True, timeout=15)
                response.raise_for_status()
            pixmap = QPixmap()
            if pixmap.loadFromData(response.content): self.image_loaded.emit(pixmap)
            else: self.load_error.emit("Failed to load image data into QPixmap.")
        except httpx.RequestError as e: self.load_error.emit(f"Network error: {e}")
        except Exception as e: self.load_error.emit(f"Error loading image: {e}")

class ArticleDetailsComponent(BaseComponent):
    """
    Component להצגת פרטי מאמר מלאים.
    """
    back_requested = Signal()
    like_clicked = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.presenter = None
        self.current_article_id: Optional[int] = None
        self.current_article_obj: Optional[Article] = None # שומרים את האובייקט
        self.image_loader_thread: Optional[ImageLoaderThread] = None # נוסיף רפרנס ל-thread

    def setup_ui(self) -> None:
        """בניית הממשק"""
        header_layout = QHBoxLayout()
        self.back_button = QPushButton("⬅️ Back to List")
        self.back_button.setStyleSheet(self._get_button_style(secondary=True))
        self.back_button.clicked.connect(self.back_requested.emit)
        header_layout.addWidget(self.back_button)
        header_layout.addStretch()
        self.main_layout.addLayout(header_layout)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { border: none; background-color: #ecf0f1; }")

        scroll_widget = QWidget()
        scroll_widget.setStyleSheet("background-color: #ecf0f1;")
        self.content_layout = QVBoxLayout(scroll_widget)
        self.content_layout.setContentsMargins(20, 15, 20, 20)
        self.content_layout.setSpacing(15)

        scroll.setWidget(scroll_widget)
        self.main_layout.addWidget(scroll)

    def on_mount(self) -> None:
        super().on_mount()
        self.current_article_id = self.get_state("article_id")
        if self.current_article_id and self.presenter:
            self.presenter.load_article_details(self.current_article_id)
        else:
            self.show_error("Article ID not provided.")

    def on_unmount(self) -> None:
        super().on_unmount()
        # עצור את ה-thread אם הוא רץ
        if self.image_loader_thread and self.image_loader_thread.isRunning():
            self.image_loader_thread.quit()
            self.image_loader_thread.wait()
        self._clear_content_layout()
        self.current_article_id = None
        self.current_article_obj = None

    def _clear_content_layout(self):
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    # --- שינוי כאן: מקבלים אובייקט Article ---
    def display_article(self, article: Article) -> None:
        """הצגת פרטי המאמר מאובייקט Article"""
        self._clear_content_layout()
        self.current_article_obj = article

        # Category Badge
        category_label = QLabel(article.category.upper() if article.category else 'GENERAL')
        category_label.setStyleSheet(self._get_badge_style())
        category_label.setMaximumWidth(120)
        category_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.content_layout.addWidget(category_label, alignment=Qt.AlignmentFlag.AlignLeft)

        # כותרת
        title_label = QLabel(article.title or 'No Title')
        title_label.setWordWrap(True)
        title_font = QFont("Segoe UI", 20, QFont.Weight.Bold)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #2c3e50; margin-bottom: 5px;")
        self.content_layout.addWidget(title_label)

        # Meta info (Source & Date)
        meta_layout = QHBoxLayout()
        source_label = QLabel(f"📰 {article.source or 'Unknown'}")
        source_label.setStyleSheet("color: #7f8c8d; font-size: 13px;")
        meta_layout.addWidget(source_label)

        # --- שינוי כאן: עובדים ישירות עם אובייקט datetime ---
        if article.published_at:
            try:
                date_str = article.published_at.strftime("%d/%m/%Y %H:%M")
                date_label = QLabel(f"🕐 {date_str}")
                date_label.setStyleSheet("color: #7f8c8d; font-size: 13px;")
                meta_layout.addWidget(date_label)
            except AttributeError: # במקרה וזה לא אובייקט תאריך תקין משום מה
                print(f"Warning: published_at is not a valid datetime object for article {article.id}")
                meta_layout.addWidget(QLabel("🕐 Invalid Date"))


        meta_layout.addStretch()
        self.content_layout.addLayout(meta_layout)

        # Divider
        divider = QFrame()
        divider.setFrameShape(QFrame.Shape.HLine)
        divider.setStyleSheet("background-color: #bdc3c7; max-height: 1px; margin: 10px 0;")
        self.content_layout.addWidget(divider)

        # תמונה ראשית
        self.image_label = QLabel("Loading image...")
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setMinimumHeight(250)
        self.image_label.setStyleSheet("background-color: #dfe6e9; border-radius: 8px; color: #7f8c8d;")
        self.content_layout.addWidget(self.image_label)
        if article.image_url:
            self.load_image_async(article.image_url)
        else:
            self.image_label.setText("🖼️ No Image")

        # תקציר
        if article.summary:
            summary_label = QLabel(f"Summary: {article.summary}")
            summary_label.setWordWrap(True)
            summary_label.setStyleSheet(self._get_summary_box_style())
            self.content_layout.addWidget(summary_label)

        # תוכן מלא
        if article.content:
            content_browser = QTextBrowser()
            content_browser.setHtml(article.content) # הנחה שהתוכן הוא HTML או טקסט פשוט
            content_browser.setStyleSheet("background-color: white; border: 1px solid #bdc3c7; border-radius: 5px; padding: 10px; font-size: 14px;")
            content_browser.setOpenExternalLinks(True)
            # הגדר גובה מינימלי וגמישות בגובה
            content_browser.setMinimumHeight(200)
            content_browser.setSizePolicy(QWidget.Policy.Expanding, QWidget.Policy.Expanding)
            self.content_layout.addWidget(content_browser)
        else:
             no_content_label = QLabel("Full content not available.")
             no_content_label.setStyleSheet("color: #7f8c8d; font-style: italic;")
             self.content_layout.addWidget(no_content_label)

        self.content_layout.addStretch()

    def load_image_async(self, url: str):
        # עצור thread קודם אם רץ
        if self.image_loader_thread and self.image_loader_thread.isRunning():
            self.image_loader_thread.quit()
            self.image_loader_thread.wait()

        self.image_loader_thread = ImageLoaderThread(url)
        self.image_loader_thread.image_loaded.connect(self._set_image)
        self.image_loader_thread.load_error.connect(self._image_load_error)
        self.image_loader_thread.start()

    def _set_image(self, pixmap: QPixmap):
        """מעדכן את התמונה ב-QLabel תוך שמירה על יחס גובה-רוחב"""
        # חשב רוחב מקסימלי (למשל, רוחב אזור התוכן פחות שוליים)
        max_width = self.content_layout.geometry().width() - 40 # הפחתנו שוליים
        if max_width <= 0: max_width = 600 # ערך ברירת מחדל אם ה-layout עוד לא חושב

        scaled_pixmap = pixmap.scaledToWidth(max_width, Qt.TransformationMode.SmoothTransformation)
        self.image_label.setPixmap(scaled_pixmap)
        self.image_label.setMinimumHeight(100) # גובה מינימלי סביר
        self.image_label.setMaximumHeight(scaled_pixmap.height()) # הגבל גובה מקסימלי לגובה התמונה
        self.image_label.setStyleSheet("background-color: transparent; border-radius: 8px;")

    def _image_load_error(self, error_message: str):
        print(f"Image load error: {error_message}")
        self.image_label.setText("🖼️ Image not available")
        self.image_label.setStyleSheet("background-color: #dfe6e9; border-radius: 8px; color: #e74c3c; font-weight: bold; padding: 20px;")
        self.image_label.setMinimumHeight(100) # גובה מינימלי גם לשגיאה

    # Styles (ללא שינוי)
    def _get_button_style(self, secondary=False) -> str:
        if secondary: return """ QPushButton { background-color: #95a5a6; color: white; border: none; border-radius: 5px; padding: 8px 16px; font-weight: bold; font-size: 13px; } QPushButton:hover { background-color: #7f8c8d; } QPushButton:pressed { background-color: #596275; } """
        else: return """ QPushButton { background-color: #3498db; color: white; border: none; border-radius: 5px; padding: 8px 16px; font-weight: bold; font-size: 13px; } QPushButton:hover { background-color: #2980b9; } QPushButton:pressed { background-color: #21618c; } """
    def _get_badge_style(self) -> str: return """ QLabel { background-color: #1abc9c; color: white; padding: 4px 10px; border-radius: 10px; font-size: 11px; font-weight: bold; margin-bottom: 5px; } """
    def _get_summary_box_style(self) -> str: return """ QLabel { background-color: #ffffff; color: #34495e; font-size: 14px; border: 1px solid #bdc3c7; border-left: 4px solid #3498db; border-radius: 5px; padding: 12px; margin-top: 10px; } """