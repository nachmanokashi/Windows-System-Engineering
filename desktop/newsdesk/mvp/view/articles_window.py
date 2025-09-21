from typing import List, Tuple, Optional, Dict
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QLineEdit,
    QListWidget, QListWidgetItem, QLabel, QTabWidget
)
from PySide6.QtCore import Qt
from newsdesk.mvp.model.article import Article

CATS = ["sports", "economy", "politics"]  # הדפים/טאבים

class ArticlesWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("NewsDesk – Categories")

        self._tabs = QTabWidget()
        self._per_cat_widgets: Dict[str, Dict[str, object]] = {}

        # עמוד לכל קטגוריה: Search + List + Status
        for cat in CATS:
            status = QLabel("")
            search = QLineEdit()
            search.setPlaceholderText(f"חיפוש ב-{cat}...")
            lst = QListWidget()

            page = QWidget()
            lay = QVBoxLayout(page)
            lay.addWidget(search)
            lay.addWidget(lst)
            lay.addWidget(status, alignment=Qt.AlignmentFlag.AlignLeft)

            self._tabs.addTab(page, cat.capitalize())
            self._per_cat_widgets[cat] = {"status": status, "search": search, "list": lst}

        root = QWidget()
        root_lay = QVBoxLayout(root)
        root_lay.addWidget(self._tabs)
        self.setCentralWidget(root)

    # ----- API "טיפש" ל-Presenter -----

    def status_label(self, cat: str) -> QLabel:
        return self._per_cat_widgets[cat]["status"]  # type: ignore[return-value]

    def search_box(self, cat: str) -> QLineEdit:
        return self._per_cat_widgets[cat]["search"]  # type: ignore[return-value]

    def list_widget(self, cat: str) -> QListWidget:
        return self._per_cat_widgets[cat]["list"]  # type: ignore[return-value]

    def set_items(self, cat: str, rows: List[Tuple[str, Article]]) -> None:
        lst = self.list_widget(cat)
        lst.clear()
        for text, article in rows:
            item = QListWidgetItem(text, lst)
            item.setData(Qt.ItemDataRole.UserRole, article)

    def set_status(self, cat: str, text: str) -> None:
        self.status_label(cat).setText(text)

    def show_error(self, message: str) -> None:
        idx = self._tabs.currentIndex()
        cat = CATS[idx]
        self.set_status(cat, f"שגיאה: {message}")

    @staticmethod
    def item_to_article(item: QListWidgetItem) -> Optional[Article]:
        return item.data(Qt.ItemDataRole.UserRole) if item else None

    @property
    def categories(self) -> List[str]:
        return CATS
