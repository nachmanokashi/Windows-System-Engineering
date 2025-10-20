# client/newsdesk/components/articles_list/articles_list_view.py
"""
ArticlesListComponent - View
Displays a list of articles using Cards
"""
from PySide6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QScrollArea, QWidget, QFrame, QSizePolicy, QSpacerItem,
    QComboBox
)
from PySide6.QtCore import Signal, Qt, QSize
from PySide6.QtGui import QFont, QColor, QPixmap
from typing import List, Dict, Any, Optional
from datetime import datetime

# ודא שהנתיב לייבוא נכון
from newsdesk.components.base_component import BaseComponent

# ============================================
# Article Card Widget (אותו קוד כמו קודם)
# ============================================
class ArticleCard(QFrame):
    clicked = Signal(int); like_toggled = Signal(int); dislike_toggled = Signal(int)
    def __init__(self, article_data: Dict[str, Any], stats: Dict[str, Any] = None, parent=None):
        super().__init__(parent); self.article_id = article_data.get("id"); self.stats = stats or {"likes_count": 0, "dislikes_count": 0, "user_liked": False, "user_disliked": False}
        self.setFrameShape(QFrame.Shape.StyledPanel); self.setCursor(Qt.CursorShape.PointingHandCursor); self.setMinimumHeight(120); self.setMaximumWidth(900); self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed); self.setStyleSheet(self._get_card_style())
        layout = QHBoxLayout(self); layout.setSpacing(15); layout.setContentsMargins(15, 15, 15, 15)
        self.image_label = QLabel(); self.image_label.setFixedSize(90, 90); self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter); self.image_label.setStyleSheet("background-color: #dfe6e9; border-radius: 8px; border: 1px solid #bdc3c7;"); self._set_icon(article_data.get("category", "")); layout.addWidget(self.image_label)
        content_layout = QVBoxLayout(); content_layout.setSpacing(5)
        title_label = QLabel(article_data.get("title", "No Title")); title_label.setWordWrap(True); title_label.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold)); title_label.setStyleSheet("color: #2c3e50;"); title_label.setMaximumHeight(45); content_layout.addWidget(title_label)
        summary_text = article_data.get("summary", "No summary available.");
        if len(summary_text) > 100: summary_text = summary_text[:100] + "...";
        summary_label = QLabel(summary_text); summary_label.setWordWrap(True); summary_label.setStyleSheet("color: #7f8c8d; font-size: 12px;"); summary_label.setMaximumHeight(35); content_layout.addWidget(summary_label)
        content_layout.addStretch(1)
        meta_likes_layout = QHBoxLayout(); meta_likes_layout.setSpacing(10)
        source_label = QLabel(f"📰 {article_data.get('source', 'Unknown')}"); source_label.setStyleSheet("color: #95a5a6; font-size: 11px; font-weight: bold;"); meta_likes_layout.addWidget(source_label)
        meta_likes_layout.addStretch(1)
        self.like_button = QPushButton(""); self.like_button.setFixedSize(QSize(90, 28)); self.like_button.setCheckable(True); self.like_button.clicked.connect(self._on_like_clicked); meta_likes_layout.addWidget(self.like_button)
        self.dislike_button = QPushButton(""); self.dislike_button.setFixedSize(QSize(100, 28)); self.dislike_button.setCheckable(True); self.dislike_button.clicked.connect(self._on_dislike_clicked); meta_likes_layout.addWidget(self.dislike_button)
        content_layout.addLayout(meta_likes_layout); layout.addLayout(content_layout, 1)
        self.update_stats(self.stats)
    def _set_icon(self, category: str): icon_map = {"sports": "⚽", "economy": "💰", "politics": "🏛️", "technology": "💻", "health": "⚕️", "science": "🔬", "environment": "🌳", "business": "💼"}; emoji = icon_map.get(category.lower(), "📰"); self.image_label.setText(emoji); icon_font = QFont(); icon_font.setPointSize(40); self.image_label.setFont(icon_font)
    def _on_like_clicked(self):
        try: self.like_toggled.emit(int(self.article_id)) if self.article_id is not None else None
        except (ValueError, TypeError): print(f"Card Error: Invalid article_id '{self.article_id}' for like")
    def _on_dislike_clicked(self):
        try: self.dislike_toggled.emit(int(self.article_id)) if self.article_id is not None else None
        except (ValueError, TypeError): print(f"Card Error: Invalid article_id '{self.article_id}' for dislike")
    def update_stats(self, stats: Dict[str, Any]):
        self.stats = stats; likes = stats.get("likes_count", 0); dislikes = stats.get("dislikes_count", 0); liked = stats.get("user_liked", False); disliked = stats.get("user_disliked", False)
        like_icon = "❤️" if liked else "🤍"; self.like_button.setText(f"{like_icon} ({likes})"); self.like_button.setStyleSheet(self._get_button_style("like", liked)); self.like_button.blockSignals(True); self.like_button.setChecked(liked); self.like_button.blockSignals(False)
        dislike_icon = "👎" if disliked else "👎🏻"; self.dislike_button.setText(f"{dislike_icon} ({dislikes})"); self.dislike_button.setStyleSheet(self._get_button_style("dislike", disliked)); self.dislike_button.blockSignals(True); self.dislike_button.setChecked(disliked); self.dislike_button.blockSignals(False)
    def mouseDoubleClickEvent(self, event):
        try: self.clicked.emit(int(self.article_id)) if self.article_id is not None else None
        except (ValueError, TypeError): print(f"Card Error: Invalid article_id '{self.article_id}' for click")
        super().mouseDoubleClickEvent(event)
    def _get_card_style(self) -> str: return """ ArticleCard { background-color: white; border: 1px solid #dfe6e9; border-radius: 8px; margin-bottom: 10px; } ArticleCard:hover { border: 1px solid #74b9ff; background-color: #f8f9fa; } """
    def _get_button_style(self, button_type: str, active: bool = False) -> str:
        fs = "11px"; pad = "4px 8px"; mw = "70px"; press_like = "#a52a1a" if active else "#95a5a6"; press_dislike = "#21618c" if active else "#95a5a6"
        if button_type == "like": bg = "#e74c3c" if active else "#dfe6e9"; clr = "white" if active else "#7f8c8d"; hov = "#c0392b" if active else "#bdc3c7"; border="none"; press=press_like
        elif button_type == "dislike": bg = "#3498db" if active else "#dfe6e9"; clr = "white" if active else "#7f8c8d"; hov = "#2980b9" if active else "#bdc3c7"; border="none"; press=press_dislike
        else: return ""
        return f""" QPushButton {{ background-color: {bg}; color: {clr}; border: {border}; border-radius: 5px; padding: {pad}; font-size: {fs}; min-width: {mw}; }} QPushButton:hover {{ background-color: {hov}; }} QPushButton:pressed {{ background-color: {press}; }} QPushButton:checked {{ background-color: {bg}; border: {border}; }} """

# ============================================
# Articles List Component
# ============================================
class ArticlesListComponent(BaseComponent):
    article_clicked = Signal(int); search_requested = Signal(str); category_changed = Signal(str); refresh_requested = Signal(); like_toggled = Signal(int); dislike_toggled = Signal(int)
    def __init__(self, parent=None): super().__init__(parent); self.presenter = None; self.card_widgets: Dict[int, ArticleCard] = {}

    def setup_ui(self) -> None:
        # --- הוספנו צבע רקע לרכיב הראשי ---
        self.setStyleSheet("background-color: #f0f2f5;") # צבע רקע אפור בהיר

        # Header
        hdr_layout = QHBoxLayout(); title = QLabel("📰 Articles"); title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold)); title.setStyleSheet("color: #2c3e50; padding: 10px;"); hdr_layout.addWidget(title); hdr_layout.addStretch(); self.refresh_btn = QPushButton("🔄 Refresh"); self.refresh_btn.setStyleSheet(self._get_button_style()); self.refresh_btn.clicked.connect(self.on_refresh_clicked); hdr_layout.addWidget(self.refresh_btn); self.main_layout.addLayout(hdr_layout)
        # Search Bar
        srch_layout = QHBoxLayout(); self.search_input = QLineEdit(); self.search_input.setPlaceholderText("🔍 Search articles..."); self.search_input.setStyleSheet(self._get_input_style()); self.search_input.returnPressed.connect(self.on_search_clicked); srch_layout.addWidget(self.search_input, 3); srch_btn = QPushButton("Search"); srch_btn.setStyleSheet(self._get_button_style()); srch_btn.clicked.connect(self.on_search_clicked); srch_layout.addWidget(srch_btn); cat_lbl = QLabel("Category:"); cat_lbl.setStyleSheet("color: #2c3e50; font-weight: bold; padding: 5px;"); srch_layout.addWidget(cat_lbl); self.category_combo = QComboBox(); self.category_combo.setStyleSheet(self._get_combo_style()); self.category_combo.addItem("All Categories", ""); self.category_combo.currentTextChanged.connect(self.on_category_changed); srch_layout.addWidget(self.category_combo, 1); self.main_layout.addLayout(srch_layout)
        # Scroll Area
        self.scroll_area = QScrollArea(); self.scroll_area.setWidgetResizable(True); self.scroll_area.setFrameShape(QFrame.NoFrame); self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff); self.scroll_area.setStyleSheet("QScrollArea { background-color: #f0f2f5; border: none; }") # הסרנו border
        self.scroll_content_widget = QWidget(); self.scroll_layout = QVBoxLayout(self.scroll_content_widget); self.scroll_layout.setContentsMargins(20, 15, 20, 15); self.scroll_layout.setSpacing(0); self.scroll_content_widget.setLayout(self.scroll_layout) # חשוב להגדיר את ה-layout לווידג'ט הפנימי!
        self.scroll_area.setWidget(self.scroll_content_widget); self.main_layout.addWidget(self.scroll_area, 1)
        # Status Bar
        self.status_label = QLabel("Ready"); self.status_label.setStyleSheet("color: #7f8c8d; padding: 5px; font-size: 12px;"); self.main_layout.addWidget(self.status_label)


    def on_mount(self) -> None: super().on_mount()
    def load_initial_data(self) -> None:
        if self.presenter: print("View: Requesting initial data..."); self.presenter.load_articles(); self.presenter.load_categories()
        else: print("View Warning: Presenter not connected...")
    def on_refresh_clicked(self) -> None: self.refresh_requested.emit(); self.presenter.load_articles() if self.presenter else None
    def on_search_clicked(self) -> None: query = self.search_input.text().strip(); self.search_requested.emit(query); self.presenter.search_articles(query) if self.presenter else None
    def on_category_changed(self, category_text: str) -> None: category = self.category_combo.currentData(); self.category_changed.emit(category if category else ""); self.presenter.filter_by_category(category if category else None) if self.presenter else None

    def display_articles(self, articles: List[Dict[str, Any]], likes_data: Optional[Dict[int, Dict]] = None) -> None:
        print(f"View: Displaying {len(articles)} articles."); likes_data = likes_data or {}
        self.card_widgets.clear()

        # --- ניקוי Layout בצורה בטוחה ---
        # הסר הכל מה-layout פרט ל-stretch item האחרון (אם קיים)
        stretch_item = None
        while self.scroll_layout.count() > 0:
            item = self.scroll_layout.takeAt(0)
            if isinstance(item, QSpacerItem): # שמור את ה-stretch item
                stretch_item = item
            else:
                widget = item.widget()
                if widget:
                    widget.deleteLater() # מחק את הווידג'ט הקודם

        # --- הצג הודעה אם אין כתבות ---
        if not articles:
            print("View: No articles to display.")
            no_articles_label = QLabel("No articles found."); no_articles_label.setAlignment(Qt.AlignmentFlag.AlignCenter); no_articles_label.setStyleSheet("color: #7f8c8d; font-size: 16px; padding: 50px;"); self.scroll_layout.addWidget(no_articles_label) # פשוט הוסף
            self.update_status("No articles found.");
        else:
            # --- הוסף כרטיסים חדשים ---
            print(f"View: Starting to add cards...")
            for i, article_data in enumerate(articles):
                article_id_any = article_data.get("id");
                if article_id_any is None: print(f"View Warning: Skip article index {i} no ID."); continue
                try: article_id = int(article_id_any)
                except (ValueError, TypeError): print(f"View Warning: Skip article index {i} invalid ID '{article_id_any}'."); continue
                stats = likes_data.get(article_id, {})
                # print(f"View: Creating card for ID {article_id}") # צמצום הדפסות
                card = ArticleCard(article_data, stats, parent=self.scroll_content_widget) # הגדר parent
                card.clicked.connect(self.article_clicked.emit)
                card.like_toggled.connect(self.like_toggled.emit)
                card.dislike_toggled.connect(self.dislike_toggled.emit)
                self.scroll_layout.addWidget(card) # פשוט הוסף בסוף
                self.card_widgets[article_id] = card
            print(f"View: Finished adding {len(self.card_widgets)} cards.")

        # --- הוסף את ה-stretch item מחדש בסוף ---
        if stretch_item:
             self.scroll_layout.addSpacerItem(stretch_item)
        else:
             self.scroll_layout.addStretch(1) # או צור אחד חדש אם לא היה קיים

        # --- עדכון מינימלי של גודל הווידג'ט הפנימי (יכול לעזור) ---
        self.scroll_content_widget.adjustSize()
        self.update_status(f"Showing {len(articles)} articles")


    def update_article_card_stats(self, article_id: int, stats: Dict[str, Any]):
        if article_id in self.card_widgets: self.card_widgets[article_id].update_stats(stats)
        else: print(f"Warning: Card ID {article_id} not found for stat update.")

    def display_categories(self, categories: List[str]) -> None:
        curr_cat = self.category_combo.currentData(); self.category_combo.blockSignals(True); self.category_combo.clear(); self.category_combo.addItem("All Categories", "")
        for cat in sorted(categories): self.category_combo.addItem(cat, cat)
        idx = 0;
        if curr_cat is not None: f_idx = self.category_combo.findData(curr_cat);
        if f_idx >= 0: idx = f_idx
        self.category_combo.setCurrentIndex(idx); self.category_combo.blockSignals(False)

    def update_status(self, message: str) -> None: self.status_label.setText(message)
    def show_loading(self, message: str = "Loading...") -> None: self.update_status(f"⏳ {message}"); self.scroll_area.setEnabled(False)
    def hide_loading(self) -> None: self.scroll_area.setEnabled(True)

    # Styles
    def _get_button_style(self) -> str: return """QPushButton { background-color: #3498db; color: white; border: none; border-radius: 5px; padding: 8px 16px; font-weight: bold; font-size: 13px; } QPushButton:hover { background-color: #2980b9; } QPushButton:pressed { background-color: #21618c; }"""
    def _get_input_style(self) -> str: return """QLineEdit { border: 2px solid #bdc3c7; border-radius: 5px; padding: 8px; font-size: 13px; background-color: white; color: #2c3e50; } QLineEdit:focus { border: 2px solid #3498db; }"""
    def _get_combo_style(self) -> str: return """QComboBox { border: 2px solid #bdc3c7; border-radius: 5px; padding: 5px 8px; font-size: 13px; min-height: 22px; background-color: white; color: #2c3e50;} QComboBox:focus { border: 2px solid #3498db; } QComboBox::drop-down { border: none; width: 15px;} QComboBox::down-arrow { image: none; } QComboBox QAbstractItemView { border: 1px solid #bdc3c7; background-color: white; color: #2c3e50; selection-background-color: #3498db; }"""