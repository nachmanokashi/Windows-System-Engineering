# client/newsdesk/mvp/view/components/articles_list/articles_list_view.py
"""
ArticlesListComponent - View
Displays a list of articles
"""
from PySide6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QComboBox,
    QHeaderView, QWidget, QMessageBox
)
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QFont, QColor # Import QColor
from typing import List, Dict, Any
from datetime import datetime

from newsdesk.components.base_component import BaseComponent

class ArticlesListComponent(BaseComponent):
    """Component for displaying the list of articles."""
    article_clicked = Signal(int)
    search_requested = Signal(str)
    category_changed = Signal(str)
    refresh_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.presenter = None

    def setup_ui(self) -> None:
        """Build the UI."""
        # Header (Title and Refresh button)
        header_layout = QHBoxLayout()
        title = QLabel("📰 Articles")
        title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        title.setStyleSheet("color: #2c3e50; padding: 10px;")
        header_layout.addWidget(title)
        header_layout.addStretch()
        self.refresh_btn = QPushButton("🔄 Refresh")
        self.refresh_btn.setStyleSheet(self._get_button_style())
        self.refresh_btn.clicked.connect(self.on_refresh_clicked)
        header_layout.addWidget(self.refresh_btn)
        self.main_layout.addLayout(header_layout)

        # Search and Filter Bar
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Search articles...")
        self.search_input.setStyleSheet(self._get_input_style())
        self.search_input.returnPressed.connect(self.on_search_clicked)
        search_layout.addWidget(self.search_input, 3)
        search_btn = QPushButton("Search")
        search_btn.setStyleSheet(self._get_button_style())
        search_btn.clicked.connect(self.on_search_clicked)
        search_layout.addWidget(search_btn)
        category_label = QLabel("Category:")
        category_label.setStyleSheet("color: #2c3e50; font-weight: bold; padding: 5px;")
        search_layout.addWidget(category_label)
        self.category_combo = QComboBox()
        self.category_combo.setStyleSheet(self._get_combo_style())
        self.category_combo.addItem("All Categories", "")
        self.category_combo.currentTextChanged.connect(self.on_category_changed)
        search_layout.addWidget(self.category_combo, 1)
        self.main_layout.addLayout(search_layout)

        # Articles Table
        self.articles_table = QTableWidget()
        self.articles_table.setColumnCount(4)
        self.articles_table.setHorizontalHeaderLabels(["ID", "Title", "Category", "Published"])
        self.articles_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.articles_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.articles_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.articles_table.verticalHeader().setVisible(False)
        self.articles_table.setAlternatingRowColors(True) # Keep alternating colors
        header = self.articles_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.articles_table.setStyleSheet(self._get_table_style()) # Apply improved style
        self.articles_table.cellDoubleClicked.connect(self.on_article_double_clicked)
        self.main_layout.addWidget(self.articles_table)

        # Status Bar
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("color: #7f8c8d; padding: 5px; font-size: 12px;")
        self.main_layout.addWidget(self.status_label)

    def on_mount(self) -> None:
        super().on_mount()

    def load_initial_data(self) -> None:
        if self.presenter:
            print("View: Requesting initial data from presenter...")
            self.presenter.load_articles()
            self.presenter.load_categories()
        else:
            print("View Warning: Presenter not connected when trying to load initial data.")

    def on_refresh_clicked(self) -> None:
        self.refresh_requested.emit()
        if self.presenter:
            self.presenter.load_articles()

    def on_search_clicked(self) -> None:
        query = self.search_input.text().strip()
        self.search_requested.emit(query)
        if self.presenter:
            self.presenter.search_articles(query)

    def on_category_changed(self, category_text: str) -> None:
        category = self.category_combo.currentData()
        self.category_changed.emit(category if category else "")
        if self.presenter:
            self.presenter.filter_by_category(category if category else None)

    def on_article_double_clicked(self, row: int, column: int) -> None:
        article_id_item = self.articles_table.item(row, 0)
        if article_id_item:
            try:
                article_id = int(article_id_item.text())
                self.article_clicked.emit(article_id)
            except ValueError:
                 print(f"Error: Could not convert article ID '{article_id_item.text()}' to integer.")


    def display_articles(self, articles: List[Dict[str, Any]]) -> None:
        """Displays articles in the table with readable text color."""
        print(f"View: Received {len(articles)} articles to display.")
        if not articles:
            print("View: No articles received.")

        self.articles_table.setRowCount(0)
        text_color = QColor("#2c3e50") # Dark gray/blue text color

        for row_index, article in enumerate(articles):
            # print(f"View: Adding row {row_index} for article ID {article.get('id')}") # Less verbose now
            self.articles_table.insertRow(row_index)

            # --- Create items ---
            id_item = QTableWidgetItem(str(article.get("id", "")))
            title_item = QTableWidgetItem(article.get("title", "N/A"))
            category_item = QTableWidgetItem(article.get("category", "N/A"))

            # --- Date Handling ---
            published_str = article.get("published_at")
            display_date = "N/A"
            if published_str:
                try:
                    dt_obj = datetime.fromisoformat(published_str.replace('Z', '+00:00'))
                    display_date = dt_obj.strftime("%d/%m/%Y")
                except (ValueError, TypeError):
                    if isinstance(published_str, str) and len(published_str) >= 10: display_date = published_str[:10]
                    else: display_date = "Invalid Date"
            published_item = QTableWidgetItem(display_date)

            # --- Set Alignment & Text Color ---
            id_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            category_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            published_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            items_to_set = [id_item, title_item, category_item, published_item]
            for col_index, item in enumerate(items_to_set):
                item.setForeground(text_color) # Set text color explicitly
                self.articles_table.setItem(row_index, col_index, item)

        # print(f"View: Finished adding {len(articles)} rows to table.") # Less verbose now
        self.update_status(f"Showing {len(articles)} articles")


    def display_categories(self, categories: List[str]) -> None:
        """Displays categories in the ComboBox."""
        current_category = self.category_combo.currentData()
        self.category_combo.blockSignals(True)
        self.category_combo.clear()
        self.category_combo.addItem("All Categories", "")
        for category in sorted(categories):
            self.category_combo.addItem(category, category)
        # Restore selection robustly
        index_to_select = 0 # Default to "All Categories"
        if current_category is not None:
            found_index = self.category_combo.findData(current_category)
            if found_index >= 0:
                index_to_select = found_index
        self.category_combo.setCurrentIndex(index_to_select)
        self.category_combo.blockSignals(False)

    def update_status(self, message: str) -> None:
        self.status_label.setText(message)

    def show_loading(self, message: str = "Loading...") -> None:
        self.update_status(f"⏳ {message}")
        self.articles_table.setEnabled(False)

    def hide_loading(self) -> None:
        self.articles_table.setEnabled(True)

    # Styles
    def _get_button_style(self) -> str: return """QPushButton { background-color: #3498db; color: white; border: none; border-radius: 5px; padding: 8px 16px; font-weight: bold; font-size: 13px; } QPushButton:hover { background-color: #2980b9; } QPushButton:pressed { background-color: #21618c; }"""
    def _get_input_style(self) -> str: return """QLineEdit { border: 2px solid #bdc3c7; border-radius: 5px; padding: 8px; font-size: 13px; background-color: white; color: #2c3e50; } QLineEdit:focus { border: 2px solid #3498db; }""" # Added background/color
    def _get_combo_style(self) -> str: return """QComboBox { border: 2px solid #bdc3c7; border-radius: 5px; padding: 5px 8px; font-size: 13px; min-height: 22px; background-color: white; color: #2c3e50;} QComboBox:focus { border: 2px solid #3498db; } QComboBox::drop-down { border: none; width: 15px;} QComboBox::down-arrow { image: none; /* Consider adding an arrow icon if needed */ } QComboBox QAbstractItemView { border: 1px solid #bdc3c7; background-color: white; color: #2c3e50; selection-background-color: #3498db; }""" # Improved styling
    def _get_table_style(self) -> str:
        """Improved table style for better readability."""
        return """
            QTableWidget {
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                background-color: white;
                gridline-color: #ecf0f1;
                alternate-background-color: #f8f9f9; /* Lighter alternate color */
                font-size: 13px;
                color: #2c3e50; /* Default text color */
            }
            QTableWidget::item {
                padding: 7px;
                border-bottom: 1px solid #ecf0f1; /* Row separator */
                /* Text color is set explicitly in display_articles */
            }
            /* Ensure selected item text is readable */
            QTableWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
            /* Style for alternating rows when selected */
             QTableWidget::item:alternate:selected {
                background-color: #3498db;
                color: white;
            }
            QHeaderView::section {
                background-color: #34495e;
                color: white;
                padding: 10px 8px;
                font-weight: bold;
                border: none;
                border-bottom: 1px solid #2c3e50;
            }
            QTableCornerButton::section {
                 background-color: #34495e;
                 border: none;
            }
        """