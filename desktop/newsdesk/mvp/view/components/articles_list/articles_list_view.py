# client/newsdesk/mvp/view/components/articles_list/articles_list_view.py
"""
ArticlesListComponent - View
הצגת רשימת מאמרים
"""
from PySide6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QTableWidget, QTableWidgetItem, QComboBox,
    QHeaderView, QWidget, QMessageBox
)
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QFont, QColor
from typing import List, Dict, Any

from newsdesk.mvp.view.components.base_component import BaseComponent


class ArticlesListComponent(BaseComponent):
    """
    Component לhצגת רשימת מאמרים
    
    Signals:
        article_clicked: נשלח כאשר לוחצים על מאמר (עם article_id)
        search_requested: נשלח כאשר מבקשים חיפוש
        category_changed: נשלח כאשר משנים קטגוריה
        refresh_requested: נשלח כאשר לוחצים refresh
    """
    
    # Signals
    article_clicked = Signal(int)  # article_id
    search_requested = Signal(str)  # search query
    category_changed = Signal(str)  # category
    refresh_requested = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.presenter = None  # יוגדר מבחוץ
    
    def setup_ui(self) -> None:
        """בניית הממשק"""
        
        # === Header ===
        header_layout = QHBoxLayout()
        
        # כותרת
        title = QLabel("📰 Articles")
        title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        title.setStyleSheet("color: #2c3e50; padding: 10px;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # כפתור Refresh
        self.refresh_btn = QPushButton("🔄 Refresh")
        self.refresh_btn.setStyleSheet(self._get_button_style())
        self.refresh_btn.clicked.connect(self.on_refresh_clicked)
        header_layout.addWidget(self.refresh_btn)
        
        self.main_layout.addLayout(header_layout)
        
        # === Search & Filter Bar ===
        search_layout = QHBoxLayout()
        
        # שדה חיפוש
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Search articles...")
        self.search_input.setStyleSheet(self._get_input_style())
        self.search_input.returnPressed.connect(self.on_search_clicked)
        search_layout.addWidget(self.search_input, 3)
        
        # כפתור חיפוש
        search_btn = QPushButton("Search")
        search_btn.setStyleSheet(self._get_button_style())
        search_btn.clicked.connect(self.on_search_clicked)
        search_layout.addWidget(search_btn)
        
        # פילטר קטגוריה
        category_label = QLabel("Category:")
        category_label.setStyleSheet("color: #2c3e50; font-weight: bold; padding: 5px;")
        search_layout.addWidget(category_label)
        
        self.category_combo = QComboBox()
        self.category_combo.setStyleSheet(self._get_combo_style())
        self.category_combo.addItem("All Categories", "")
        self.category_combo.currentTextChanged.connect(self.on_category_changed)
        search_layout.addWidget(self.category_combo, 1)
        
        self.main_layout.addLayout(search_layout)
        
        # === Articles Table ===
        self.articles_table = QTableWidget()
        self.articles_table.setColumnCount(4)
        self.articles_table.setHorizontalHeaderLabels(["ID", "Title", "Category", "Published"])
        
        # הגדרות טבלה
        self.articles_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.articles_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.articles_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.articles_table.verticalHeader().setVisible(False)
        self.articles_table.setAlternatingRowColors(True)
        
        # רוחב עמודות
        header = self.articles_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        
        # עיצוב טבלה
        self.articles_table.setStyleSheet(self._get_table_style())
        
        # אירוע לחיצה כפולה
        self.articles_table.cellDoubleClicked.connect(self.on_article_double_clicked)
        
        self.main_layout.addWidget(self.articles_table)
        
        # === Status Bar ===
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("color: #7f8c8d; padding: 5px; font-size: 12px;")
        self.main_layout.addWidget(self.status_label)
    
    def on_mount(self) -> None:
        """כאשר ה-Component נטען"""
        super().on_mount()
        
        # טען נתונים ראשוניים
        if self.presenter:
            self.presenter.load_articles()
            self.presenter.load_categories()
    
    def on_refresh_clicked(self) -> None:
        """לחיצה על Refresh"""
        self.refresh_requested.emit()
        if self.presenter:
            self.presenter.load_articles()
    
    def on_search_clicked(self) -> None:
        """לחיצה על Search"""
        query = self.search_input.text().strip()
        self.search_requested.emit(query)
        if self.presenter:
            self.presenter.search_articles(query)
    
    def on_category_changed(self, category_text: str) -> None:
        """שינוי קטגוריה"""
        category = self.category_combo.currentData()
        self.category_changed.emit(category)
        if self.presenter:
            self.presenter.filter_by_category(category)
    
    def on_article_double_clicked(self, row: int, column: int) -> None:
        """לחיצה כפולה על מאמר"""
        article_id_item = self.articles_table.item(row, 0)
        if article_id_item:
            article_id = int(article_id_item.text())
            self.article_clicked.emit(article_id)
    
    # ============================================
    # Public Methods - נקראים מה-Presenter
    # ============================================
    
    def display_articles(self, articles: List[Dict[str, Any]]) -> None:
        """
        הצגת מאמרים בטבלה
        
        Args:
            articles: רשימת מאמרים
        """
        self.articles_table.setRowCount(0)
        
        for article in articles:
            row = self.articles_table.rowCount()
            self.articles_table.insertRow(row)
            
            # ID
            id_item = QTableWidgetItem(str(article.get("id", "")))
            id_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.articles_table.setItem(row, 0, id_item)
            
            # Title
            title_item = QTableWidgetItem(article.get("title", ""))
            self.articles_table.setItem(row, 1, title_item)
            
            # Category
            category_item = QTableWidgetItem(article.get("category", ""))
            category_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.articles_table.setItem(row, 2, category_item)
            
            # Published
            published = article.get("published_at", "")
            if published:
                published = published[:10]  # רק התאריך
            published_item = QTableWidgetItem(published)
            published_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.articles_table.setItem(row, 3, published_item)
        
        self.update_status(f"Showing {len(articles)} articles")
    
    def display_categories(self, categories: List[str]) -> None:
        """
        הצגת קטגוריות בComboBox
        
        Args:
            categories: רשימת קטגוריות
        """
        current_category = self.category_combo.currentData()
        
        self.category_combo.clear()
        self.category_combo.addItem("All Categories", "")
        
        for category in categories:
            self.category_combo.addItem(category, category)
        
        # שמור את הבחירה הקודמת
        if current_category:
            index = self.category_combo.findData(current_category)
            if index >= 0:
                self.category_combo.setCurrentIndex(index)
    
    def update_status(self, message: str) -> None:
        """עדכון שורת הסטטוס"""
        self.status_label.setText(message)
    
    def show_loading(self, message: str = "Loading...") -> None:
        """הצגת אינדיקטור טעינה"""
        self.update_status(f"⏳ {message}")
        self.articles_table.setEnabled(False)
    
    def hide_loading(self) -> None:
        """הסתרת אינדיקטור טעינה"""
        self.articles_table.setEnabled(True)
    
    # ============================================
    # Styles
    # ============================================
    
    def _get_button_style(self) -> str:
        return """
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
        """
    
    def _get_input_style(self) -> str:
        return """
            QLineEdit {
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                padding: 8px;
                font-size: 13px;
            }
            QLineEdit:focus {
                border: 2px solid #3498db;
            }
        """
    
    def _get_combo_style(self) -> str:
        return """
            QComboBox {
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                padding: 5px;
                font-size: 13px;
            }
            QComboBox:focus {
                border: 2px solid #3498db;
            }
        """
    
    def _get_table_style(self) -> str:
        return """
            QTableWidget {
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                background-color: white;
                gridline-color: #ecf0f1;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QTableWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
            QHeaderView::section {
                background-color: #34495e;
                color: white;
                padding: 8px;
                font-weight: bold;
                border: none;
            }
        """