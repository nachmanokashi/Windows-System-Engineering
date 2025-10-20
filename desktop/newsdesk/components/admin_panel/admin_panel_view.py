# desktop/newsdesk/components/admin_panel/admin_panel_view.py
"""
Admin Panel View - ממשק ניהול מאמרים
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QTableWidget, QTableWidgetItem, QHeaderView,
    QLabel, QMessageBox, QDialog, QLineEdit, QTextEdit,
    QComboBox, QFormLayout, QDialogButtonBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QColor
from typing import List, Dict, Any, Optional


class ArticleFormDialog(QDialog):
    """דיאלוג להוספה/עריכת מאמר"""
    
    def __init__(self, parent=None, article_data: Optional[Dict] = None, categories: List[str] = None):
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
        """בנה את הממשק"""
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
        
        # Category
        category_layout = QHBoxLayout()
        self.category_combo = QComboBox()
        self.category_combo.addItem("-- Select Category --", None)
        for cat in self.categories:
            self.category_combo.addItem(cat, cat)
        category_layout.addWidget(self.category_combo)
        
        # AI Classify Button
        self.classify_btn = QPushButton("🤖 Auto-Classify")
        self.classify_btn.setMaximumWidth(150)
        self.classify_btn.clicked.connect(self._on_classify_clicked)
        category_layout.addWidget(self.classify_btn)
        
        form_layout.addRow("🏷️ Category:", category_layout)
        
        # AI Suggestion Label
        self.suggestion_label = QLabel("")
        self.suggestion_label.setStyleSheet("color: #2196F3; font-weight: bold;")
        form_layout.addRow("", self.suggestion_label)
        
        # Image URL
        self.image_input = QLineEdit()
        self.image_input.setPlaceholderText("https://example.com/image.jpg (optional)")
        form_layout.addRow("🖼️ Image URL:", self.image_input)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.Save | QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def _load_article_data(self):
        """טען נתוני מאמר קיים"""
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
            index = self.category_combo.findData(category)
            if index >= 0:
                self.category_combo.setCurrentIndex(index)
    
    def _on_classify_clicked(self):
        """כפתור סיווג נלחץ"""
        # Emit signal for presenter to handle
        self.classify_btn.setEnabled(False)
        self.classify_btn.setText("🔄 Classifying...")
        # Will be handled by presenter
    
    def show_classification_result(self, category: str, confidence: float):
        """הצג תוצאת סיווג"""
        self.suggested_category = category
        self.suggestion_label.setText(
            f"✨ AI suggests: {category} ({confidence:.1%} confidence)"
        )
        
        # Set in combo box
        index = self.category_combo.findData(category)
        if index >= 0:
            self.category_combo.setCurrentIndex(index)
        
        self.classify_btn.setEnabled(True)
        self.classify_btn.setText("🤖 Auto-Classify")
    
    def show_classification_error(self, error: str):
        """הצג שגיאת סיווג"""
        self.suggestion_label.setText(f"❌ Classification failed: {error}")
        self.suggestion_label.setStyleSheet("color: #f44336;")
        self.classify_btn.setEnabled(True)
        self.classify_btn.setText("🤖 Auto-Classify")
    
    def get_form_data(self) -> Dict[str, Any]:
        """קבל את הנתונים מהטופס"""
        category = self.category_combo.currentData()
        
        return {
            "title": self.title_input.text().strip(),
            "url": self.url_input.text().strip(),
            "source": self.source_input.text().strip(),
            "summary": self.summary_input.toPlainText().strip(),
            "content": self.content_input.toPlainText().strip(),
            "category": category,
            "image_url": self.image_input.text().strip() or None,
            "auto_classify": not category  # Auto-classify if no category selected
        }


class AdminPanelView(QWidget):
    """ממשק Admin Panel"""
    
    # Signals
    add_article_requested = Signal()
    edit_article_requested = Signal(int)  # article_id
    delete_article_requested = Signal(int)  # article_id
    refresh_requested = Signal()
    classify_all_requested = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
    
    def _setup_ui(self):
        """בנה את הממשק"""
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
        
        # Buttons
        self.add_btn = QPushButton("➕ Add Article")
        self.add_btn.clicked.connect(self.add_article_requested.emit)
        header_layout.addWidget(self.add_btn)
        
        self.classify_all_btn = QPushButton("🤖 Classify All Uncategorized")
        self.classify_all_btn.clicked.connect(self.classify_all_requested.emit)
        header_layout.addWidget(self.classify_all_btn)
        
        self.refresh_btn = QPushButton("🔄 Refresh")
        self.refresh_btn.clicked.connect(self.refresh_requested.emit)
        header_layout.addWidget(self.refresh_btn)
        
        layout.addLayout(header_layout)
        
        # Status Label
        self.status_label = QLabel("Loading articles...")
        layout.addWidget(self.status_label)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "ID", "Title", "Category", "Source", "Published", "Actions"
        ])
        
        # Column widths
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
    
    def display_articles(self, articles: List[Dict[str, Any]]):
        """הצג רשימת מאמרים"""
        self.table.setRowCount(0)
        
        for article in articles:
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            # ID
            id_item = QTableWidgetItem(str(article.get("id", "")))
            id_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 0, id_item)
            
            # Title
            title = article.get("title", "")[:60] + "..." if len(article.get("title", "")) > 60 else article.get("title", "")
            self.table.setItem(row, 1, QTableWidgetItem(title))
            
            # Category
            category_item = QTableWidgetItem(article.get("category", "N/A"))
            category_item.setTextAlignment(Qt.AlignCenter)
            
            # Color code by category
            if article.get("category") == "General" or not article.get("category"):
                category_item.setBackground(QColor("#FFF3E0"))
            
            self.table.setItem(row, 2, category_item)
            
            # Source
            self.table.setItem(row, 3, QTableWidgetItem(article.get("source", "N/A")))
            
            # Published
            published = article.get("published_at", "")
            if published:
                published = published[:10]  # Just the date
            self.table.setItem(row, 4, QTableWidgetItem(published))
            
            # Actions
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(4, 4, 4, 4)
            
            edit_btn = QPushButton("✏️")
            edit_btn.setMaximumWidth(40)
            edit_btn.clicked.connect(lambda checked, aid=article["id"]: self.edit_article_requested.emit(aid))
            actions_layout.addWidget(edit_btn)
            
            delete_btn = QPushButton("🗑️")
            delete_btn.setMaximumWidth(40)
            delete_btn.setStyleSheet("background-color: #ffebee;")
            delete_btn.clicked.connect(lambda checked, aid=article["id"]: self._confirm_delete(aid))
            actions_layout.addWidget(delete_btn)
            
            self.table.setCellWidget(row, 5, actions_widget)
        
        self.status_label.setText(f"📊 Showing {len(articles)} articles")
    
    def _confirm_delete(self, article_id: int):
        """אשר מחיקה"""
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete article #{article_id}?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.delete_article_requested.emit(article_id)
    
    def update_status(self, message: str):
        """עדכן סטטוס"""
        self.status_label.setText(message)
    
    def show_loading(self, message: str = "Loading..."):
        """הצג טעינה"""
        self.status_label.setText(f"⏳ {message}")
        self.table.setEnabled(False)
    
    def hide_loading(self):
        """הסתר טעינה"""
        self.table.setEnabled(True)
    
    def show_error(self, error: str):
        """הצג שגיאה"""
        QMessageBox.critical(self, "Error", error)
    
    def show_success(self, message: str):
        """הצג הצלחה"""
        QMessageBox.information(self, "Success", message)