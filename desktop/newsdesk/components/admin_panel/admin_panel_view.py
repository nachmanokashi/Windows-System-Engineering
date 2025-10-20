from typing import List, Dict, Any, Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QLabel, QMessageBox, QDialog, QLineEdit, QTextEdit,
    QComboBox, QFormLayout, QDialogButtonBox
)
from PySide6.QtGui import QFont


# ---------------------------
# ArticleFormDialog
# ---------------------------
class ArticleFormDialog(QDialog):
    draft_classify_requested = Signal(dict)

    def __init__(self, parent=None, article_data: Optional[Dict] = None, categories: Optional[List[str]] = None):
        super().__init__(parent)
        self.article_data = article_data
        self.is_edit_mode = article_data is not None
        self.categories = categories or []
        self.suggested_category = None

        self.setWindowTitle("✏️ Edit Article" if self.is_edit_mode else "➕ Add New Article")
        self.setMinimumWidth(600)
        self.setMinimumHeight(500)

        self._setup_ui()

        if self.is_edit_mode:
            self._load_article_data()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        # Form
        form_layout = QFormLayout()

        # Title
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Article title...")
        form_layout.addRow("📰 Title:", self.title_input)

        # URL
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("https://example.com/article")
        form_layout.addRow("🔗 URL:", self.url_input)

        # Source
        self.source_input = QLineEdit()
        self.source_input.setPlaceholderText("TechCrunch, CNN, etc.")
        form_layout.addRow("📡 Source:", self.source_input)

        # Summary
        self.summary_input = QTextEdit()
        self.summary_input.setPlaceholderText("Brief summary...")
        self.summary_input.setMaximumHeight(80)
        form_layout.addRow("📝 Summary:", self.summary_input)

        # Content
        self.content_input = QTextEdit()
        self.content_input.setPlaceholderText("Full article content...")
        self.content_input.setMinimumHeight(150)
        form_layout.addRow("📄 Content:", self.content_input)

        # Category + Auto-Classify
        category_layout = QHBoxLayout()
        self.category_combo = QComboBox()
        self.category_combo.addItem("-- Select Category --", None)
        for cat in self.categories:
            self.category_combo.addItem(cat, cat)
        category_layout.addWidget(self.category_combo)

        self.classify_btn = QPushButton("🤖 Auto-Classify")
        self.classify_btn.setMaximumWidth(150)
        self.classify_btn.clicked.connect(self._on_classify_clicked)
        category_layout.addWidget(self.classify_btn)
        form_layout.addRow("🏷️ Category:", category_layout)

        # AI suggestion label
        self.suggestion_label = QLabel("")
        self.suggestion_label.setStyleSheet("color: #2196F3; font-weight: bold;")
        form_layout.addRow("", self.suggestion_label)

        # Image URL
        self.image_input = QLineEdit()
        self.image_input.setPlaceholderText("https://example.com/image.jpg (optional)")
        form_layout.addRow("🖼️ Image URL:", self.image_input)

        layout.addLayout(form_layout)

        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def _load_article_data(self):
        if not self.article_data:
            return
        self.title_input.setText(self.article_data.get("title", ""))
        self.url_input.setText(self.article_data.get("url", ""))
        self.source_input.setText(self.article_data.get("source", ""))
        self.summary_input.setPlainText(self.article_data.get("summary", ""))
        self.content_input.setPlainText(self.article_data.get("content", ""))
        self.image_input.setText(self.article_data.get("image_url", ""))

        category = self.article_data.get("category")
        if category:
            idx = self.category_combo.findData(category)
            if idx >= 0:
                self.category_combo.setCurrentIndex(idx)

    def _on_classify_clicked(self):
        self.classify_btn.setEnabled(False)
        self.classify_btn.setText("🔄 Classifying...")
        self.suggestion_label.setStyleSheet("color: #2196F3; font-weight: bold;")
        self.draft_classify_requested.emit({
            "title": self.title_input.text().strip(),
            "summary": self.summary_input.toPlainText().strip(),
            "content": self.content_input.toPlainText().strip()
        })

    def show_classification_result(self, category: str, confidence: float):
        self.suggested_category = category
        self.suggestion_label.setText(f"✨ AI suggests: {category} ({confidence:.1%} confidence)")
        idx = self.category_combo.findData(category)
        if idx >= 0:
            self.category_combo.setCurrentIndex(idx)
        self.classify_btn.setEnabled(True)
        self.classify_btn.setText("🤖 Auto-Classify")

    def show_classification_error(self, error: str):
        self.suggestion_label.setText(f"❌ Classification failed: {error}")
        self.suggestion_label.setStyleSheet("color: #f44336; font-weight: bold;")
        self.classify_btn.setEnabled(True)
        self.classify_btn.setText("🤖 Auto-Classify")

    # IMPORTANT: presenter מצפה למתודה הזו
    def get_form_data(self) -> Dict[str, Any]:
        return {
            "title": self.title_input.text().strip(),
            "url": self.url_input.text().strip(),
            "source": self.source_input.text().strip(),
            "summary": self.summary_input.toPlainText().strip(),
            "content": self.content_input.toPlainText().strip(),
            "category": self.category_combo.currentData(),
            "image_url": self.image_input.text().strip() or None
        }

    # לשמירה על תאימות אם ה-presenter קורא get_data()
    def get_data(self) -> Dict[str, Any]:
        return self.get_form_data()


# ---------------------------
# AdminPanelComponent
# ---------------------------
class AdminPanelComponent(QWidget):
    """ממשק Admin Panel"""

    # Signals
    add_article_requested = Signal()
    edit_article_requested = Signal(int)
    delete_article_requested = Signal(int)
    refresh_articles_requested = Signal()
    classify_requested = Signal(int)
    apply_classification_requested = Signal(int)
    batch_classify_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.presenter = None  # ימנע AttributeError בבדיקת main window
        self._categories: List[str] = []
        self._setup_ui()

    # ---- Presenter hookup & lifecycle ----
    def set_presenter(self, presenter) -> None:
        self.presenter = presenter

    def on_mount(self) -> None:
        """נקרא ע״י המנהל בעת ניווט ל-Admin Panel"""
        if self.presenter and hasattr(self.presenter, "attach_view"):
            self.presenter.attach_view(self)
        # טעינות ראשוניות (רק אם קיימות מתודות ב-presenter)
        if self.presenter:
            if hasattr(self.presenter, "load_categories"):
                self.presenter.load_categories()
            if hasattr(self.presenter, "load_articles"):
                self.presenter.load_articles()

    def on_unmount(self) -> None:
        if self.presenter and hasattr(self.presenter, "detach_view"):
            self.presenter.detach_view()

    # ---- UI ----
    def _setup_ui(self):
        layout = QVBoxLayout(self)

        # Header
        header_layout = QHBoxLayout()
        title_label = QLabel("🔐 Admin Panel - Article Management")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        header_layout.addWidget(title_label)
        header_layout.addStretch()

        self.add_btn = QPushButton("➕ Add Article")
        self.add_btn.clicked.connect(self.add_article_requested.emit)
        header_layout.addWidget(self.add_btn)

        self.classify_all_btn = QPushButton("🤖 Classify All Uncategorized")
        self.classify_all_btn.clicked.connect(self.batch_classify_requested.emit)
        header_layout.addWidget(self.classify_all_btn)

        self.refresh_btn = QPushButton("🔄 Refresh")
        self.refresh_btn.clicked.connect(self.refresh_articles_requested.emit)
        header_layout.addWidget(self.refresh_btn)

        layout.addLayout(header_layout)

        # Status
        self.status_label = QLabel("Loading articles...")
        layout.addWidget(self.status_label)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["ID", "Title", "Category", "Source", "Published", "Actions"])
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setAlternatingRowColors(True)
        layout.addWidget(self.table)

    # קבלת קטגוריות מה-presenter
    def set_categories(self, categories: List[str]):
        self._categories = categories or []

    def show_info(self, message: str):
        QMessageBox.information(self, "Info", message)

    def display_articles(self, articles: List[Dict[str, Any]]):
        """ממלא את הטבלה בנתוני מאמרים"""
        self.table.setRowCount(0)

        for article in (articles or []):
            row = self.table.rowCount()
            self.table.insertRow(row)

            # ID
            id_item = QTableWidgetItem(str(article.get("id", "")))
            id_item.setFlags(id_item.flags() ^ Qt.ItemIsEditable)
            self.table.setItem(row, 0, id_item)

            # Title
            title_item = QTableWidgetItem(article.get("title", "") or "")
            title_item.setFlags(title_item.flags() ^ Qt.ItemIsEditable)
            self.table.setItem(row, 1, title_item)

            # Category
            cat_item = QTableWidgetItem(article.get("category", "") or "")
            cat_item.setFlags(cat_item.flags() ^ Qt.ItemIsEditable)
            self.table.setItem(row, 2, cat_item)

            # Source
            src_item = QTableWidgetItem(article.get("source", "") or "")
            src_item.setFlags(src_item.flags() ^ Qt.ItemIsEditable)
            self.table.setItem(row, 3, src_item)

            # Published (str/ISO if exists)
            published = article.get("published_at") or article.get("published") or ""
            pub_item = QTableWidgetItem(str(published))
            pub_item.setFlags(pub_item.flags() ^ Qt.ItemIsEditable)
            self.table.setItem(row, 4, pub_item)

            # Actions
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(4, 4, 4, 4)

            aid = article.get("id")

            edit_btn = QPushButton("✏️")
            edit_btn.setMaximumWidth(40)
            edit_btn.clicked.connect(lambda checked=False, _aid=aid: self.edit_article_requested.emit(int(_aid)))
            actions_layout.addWidget(edit_btn)

            delete_btn = QPushButton("🗑️")
            delete_btn.setMaximumWidth(40)
            delete_btn.setStyleSheet("background-color: #ffebee;")
            delete_btn.clicked.connect(lambda checked=False, _aid=aid: self._confirm_delete(int(_aid)))
            actions_layout.addWidget(delete_btn)

            classify_btn = QPushButton("🤖")
            classify_btn.setToolTip("AI Classify (suggest)")
            classify_btn.setMaximumWidth(40)
            classify_btn.clicked.connect(lambda checked=False, _aid=aid: self.classify_requested.emit(int(_aid)))
            actions_layout.addWidget(classify_btn)

            apply_btn = QPushButton("✅")
            apply_btn.setToolTip("Apply AI Classification")
            apply_btn.setMaximumWidth(40)
            apply_btn.clicked.connect(lambda checked=False, _aid=aid: self.apply_classification_requested.emit(int(_aid)))
            actions_layout.addWidget(apply_btn)

            self.table.setCellWidget(row, 5, actions_widget)

        self.status_label.setText(f"📊 Showing {len(articles or [])} articles")

    def _confirm_delete(self, article_id: int):
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete article #{article_id}?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.delete_article_requested.emit(article_id)

    # Helpers
    def update_status(self, message: str):
        self.status_label.setText(message)

    def show_loading(self, message: str = "Loading..."):
        self.status_label.setText(f"⏳ {message}")
        self.table.setEnabled(False)

    def hide_loading(self):
        self.table.setEnabled(True)

    def show_error(self, error: str):
        QMessageBox.critical(self, "Error", error)

    def show_success(self, message: str):
        QMessageBox.information(self, "Success", message)
