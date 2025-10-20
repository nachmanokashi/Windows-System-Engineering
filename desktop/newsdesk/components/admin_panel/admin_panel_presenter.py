# desktop/newsdesk/components/admin_panel/admin_panel_presenter.py
"""
Admin Panel Presenter - לוגיקת ניהול מאמרים
"""

from typing import Dict, Any, Optional, List
from PySide6.QtWidgets import QMessageBox

from newsdesk.infra.http.admin_service_http import HttpAdminService
from newsdesk.infra.http.news_service_http import HttpNewsService
from newsdesk.components.admin_panel.admin_panel_view import AdminPanelView, ArticleFormDialog
from newsdesk.mvp.presenter.base_presenter import BasePresenter


class AdminPanelPresenter(BasePresenter):
    """Presenter לניהול Admin Panel"""

    def __init__(self, view: AdminPanelView, admin_service: HttpAdminService, news_service: HttpNewsService):
        super().__init__(view)
        self.view = view
        self.admin_service = admin_service
        self.news_service = news_service
        self.categories: List[str] = []

        self._connect_signals()
        self._load_categories()
        # טען רשימת מאמרים כבר בפתיחה לנוחות
        self.load_articles()

    # ------------------------------
    # Init / Signals / Bootstrap
    # ------------------------------
    def _connect_signals(self):
        """חיבור signals"""
        self.view.add_article_requested.connect(self.on_add_article)
        self.view.edit_article_requested.connect(self.on_edit_article)
        self.view.delete_article_requested.connect(self.on_delete_article)
        self.view.refresh_requested.connect(self.load_articles)
        self.view.classify_all_requested.connect(self.on_classify_all)

    def _load_categories(self):
        """טעינת רשימת קטגוריות"""
        def on_success(resp: Dict[str, Any]):
            # ה-backend מחזיר {"categories": [...]}; אם מגיע *רק* list, נטפל גם בזה
            cats = resp.get("categories", resp if isinstance(resp, list) else [])
            self.categories = list(cats or [])
            print(f"✅ Loaded {len(self.categories)} categories")

        def on_error(error: str):
            print(f"❌ Failed to load categories: {error}")
            self.categories = []

        # הקריאה מתבצעת דרך שירות ה-Admin שממפה ל-/admin/categories
        self._start_worker(
            self.admin_service.get_available_categories,
            finished_slot=on_success,
            error_slot=on_error
        )

    # ------------------------------
    # Articles list
    # ------------------------------
    def load_articles(self):
        """טען רשימת מאמרים"""
        self.view.show_loading("Loading articles...")

        def on_success(response: Dict[str, Any]):
            self.view.hide_loading()
            # מוודאים תמיכה גם במבנים שונים: {items:[...]} או [...]
            items = response.get("items") if isinstance(response, dict) else response
            articles = items or []
            self.view.display_articles(articles)

        def on_error(error: str):
            self.view.hide_loading()
            self.view.show_error(f"Failed to load articles: {error}")

        # מניחים שהשירות תומך בפרמטרים page/page_size
        self._start_worker(
            self.news_service.list_articles,
            page=1,
            page_size=100,
            finished_slot=on_success,
            error_slot=on_error
        )

    # ------------------------------
    # Create
    # ------------------------------
    def on_add_article(self):
        """הוספת מאמר חדש"""
        dialog = ArticleFormDialog(self.view, categories=self.categories)

        # בטל חיבור ברירת המחדל של הכפתור בדיאלוג (אם קיים) וחבר לסיווג שלנו
        try:
            dialog.classify_btn.clicked.disconnect()
        except Exception:
            pass
        dialog.classify_btn.clicked.connect(lambda: self._classify_in_dialog(dialog))

        if dialog.exec():
            form_data = dialog.get_form_data()

            if not form_data["title"] or not form_data["content"]:
                self.view.show_error("Title and Content are required!")
                return

            self._create_article(form_data)

    def _classify_in_dialog(self, dialog: ArticleFormDialog):
        """סיווג AI בתוך הדיאלוג (לצורך UX מהיר לפני שמירה)"""
        form_data = dialog.get_form_data()

        if not form_data["title"]:
            dialog.show_classification_error("Title is required for classification")
            return

        # Heuristic/Local quick classify (לא פוגע ב-backend)
        def classify_worker():
            title = (form_data["title"] or "").lower()
            content = (form_data.get("content") or "").lower()
            text = f"{title} {content}"

            if any(w in text for w in ["tech", "ai", "software", "computer"]):
                return {"category": "Technology", "confidence": 0.85}
            if any(w in text for w in ["sport", "game", "player", "team"]):
                return {"category": "Sports", "confidence": 0.80}
            if any(w in text for w in ["health", "medical", "doctor"]):
                return {"category": "Health", "confidence": 0.75}
            if any(w in text for w in ["business", "economy", "market"]):
                return {"category": "Business", "confidence": 0.70}
            return {"category": "General", "confidence": 0.50}

        def on_success(result: Dict[str, Any]):
            dialog.show_classification_result(result["category"], result["confidence"])

        def on_error(error: str):
            dialog.show_classification_error(error)

        self._start_worker(classify_worker, finished_slot=on_success, error_slot=on_error)

    def _create_article(self, form_data: Dict[str, Any]):
        """צור מאמר חדש דרך Admin API"""
        self.view.show_loading("Creating article...")

        def on_success(response: Dict[str, Any]):
            self.view.hide_loading()
            article_id = response.get("article_id")
            category = response.get("category")
            self.view.show_success(f"Article #{article_id} created successfully!\nCategory: {category or 'N/A'}")
            self.load_articles()  # רענון רשימה

        def on_error(error: str):
            self.view.hide_loading()
            self.view.show_error(f"Failed to create article: {error}")

        # ה-backend תומך ב-auto_classify אם לא בחרנו קטגוריה
        self._start_worker(
            self.admin_service.create_article,
            title=form_data["title"],
            summary=form_data["summary"],
            content=form_data["content"],
            url=form_data["url"],
            source=form_data["source"],
            category=form_data.get("category"),
            image_url=form_data.get("image_url"),
            auto_classify=form_data.get("auto_classify", True),
            finished_slot=on_success,
            error_slot=on_error
        )

    # ------------------------------
    # Edit / Update
    # ------------------------------
    def on_edit_article(self, article_id: int):
        """עריכת מאמר קיים"""
        self.view.show_loading(f"Loading article #{article_id}...")

        def on_article_loaded(article):
            self.view.hide_loading()

            if not article:
                self.view.show_error(f"Article #{article_id} not found")
                return

            # המרה ל-dict קל לעריכה
            article_data = {
                "id": getattr(article, "id", None) or article.get("id"),
                "title": getattr(article, "title", None) or article.get("title", ""),
                "summary": getattr(article, "summary", None) or article.get("summary", ""),
                "content": getattr(article, "content", None) or article.get("content", ""),
                "url": getattr(article, "url", None) or article.get("url", ""),
                "source": getattr(article, "source", None) or article.get("source", ""),
                "category": getattr(article, "category", None) or article.get("category"),
                "image_url": getattr(article, "image_url", None) or article.get("image_url"),
            }

            dialog = ArticleFormDialog(self.view, article_data=article_data, categories=self.categories)

            # נשאיר את כפתור הסיווג בדיאלוג (היוריסטיקה המקומית) למקרה שרוצים לרענן קטגוריה לפני השמירה
            try:
                dialog.classify_btn.clicked.disconnect()
            except Exception:
                pass
            dialog.classify_btn.clicked.connect(lambda: self._classify_in_dialog(dialog))

            if dialog.exec():
                form_data = dialog.get_form_data()
                self._update_article(article_id, form_data)

        def on_error(error: str):
            self.view.hide_loading()
            self.view.show_error(f"Failed to load article: {error}")

        # HttpNewsService.get אמור להחזיר Article/Dict עבור ה-id
        self._start_worker(
            self.news_service.get,
            article_id=str(article_id),
            finished_slot=on_article_loaded,
            error_slot=on_error
        )

    def _update_article(self, article_id: int, form_data: Dict[str, Any]):
        """עדכון מאמר"""
        self.view.show_loading("Updating article...")

        def on_success(_response: Dict[str, Any]):
            self.view.hide_loading()
            self.view.show_success(f"Article #{article_id} updated successfully!")
            self.load_articles()

        def on_error(error: str):
            self.view.hide_loading()
            self.view.show_error(f"Failed to update article: {error}")

        self._start_worker(
            self.admin_service.update_article,
            article_id=article_id,
            title=form_data["title"],
            summary=form_data["summary"],
            content=form_data["content"],
            url=form_data["url"],
            source=form_data["source"],
            category=form_data.get("category"),
            image_url=form_data.get("image_url"),
            finished_slot=on_success,
            error_slot=on_error
        )

    # ------------------------------
    # Delete
    # ------------------------------
    def on_delete_article(self, article_id: int):
        """מחיקת מאמר"""
        # אישור סופי מה-UI
        reply = QMessageBox.question(
            self.view,
            "Confirm Delete",
            f"Are you sure you want to delete article #{article_id}?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply != QMessageBox.Yes:
            return

        self.view.show_loading(f"Deleting article #{article_id}...")

        def on_success(_response: Dict[str, Any]):
            self.view.hide_loading()
            self.view.show_success(f"Article #{article_id} deleted successfully!")
            self.load_articles()

        def on_error(error: str):
            self.view.hide_loading()
            self.view.show_error(f"Failed to delete article: {error}")

        self._start_worker(
            self.admin_service.delete_article,
            article_id=article_id,
            finished_slot=on_success,
            error_slot=on_error
        )

    # ------------------------------
    # Classify (batch)
    # ------------------------------
    def on_classify_all(self):
        """סיווג כל המאמרים הלא מסווגים ('General' או ריקים)"""
        self.view.show_loading("Fetching uncategorized articles...")

        def on_uncategorized_loaded(response: Dict[str, Any]):
            # ה-backend של אדמין מחזיר {"count": X, "articles": [{id,title,category,...}]}
            articles = response.get("articles", []) if isinstance(response, dict) else []
            count = len(articles)

            if count == 0:
                self.view.hide_loading()
                self.view.show_success("No uncategorized articles found!")
                return

            # אישור פעולה מרובת פריטים
            reply = QMessageBox.question(
                self.view,
                "Confirm Batch Classification",
                f"Found {count} uncategorized articles.\nClassify them all?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )

            if reply == QMessageBox.Yes:
                article_ids = [a.get("id") for a in articles if a.get("id") is not None]
                if not article_ids:
                    self.view.hide_loading()
                    self.view.show_error("No valid article IDs to classify.")
                    return
                self._batch_classify(article_ids)
            else:
                self.view.hide_loading()

        def on_error(error: str):
            self.view.hide_loading()
            self.view.show_error(f"Failed to fetch uncategorized: {error}")

        # משתמשים ב-Admin API (לא שירות החדשות) כדי להביא *רשימת לא מסווגים*
        self._start_worker(
            self.admin_service.get_uncategorized_articles,
            limit=50,
            finished_slot=on_uncategorized_loaded,
            error_slot=on_error
        )

    def _batch_classify(self, article_ids: List[int]):
        """שליחת סיווג מרובה ל-backend"""
        self.view.update_status("Classifying articles with AI...")

        def on_success(response: Dict[str, Any]):
            # מצופה {"success": True, "total": N, "results": [...]}
            self.view.hide_loading()
            total = response.get("total", len(article_ids))
            self.view.show_success(f"Batch classification complete for {total} articles.")
            self.load_articles()

        def on_error(error: str):
            self.view.hide_loading()
            self.view.show_error(f"Batch classification failed: {error}")

        self._start_worker(
            self.admin_service.batch_classify_articles,
            article_ids=article_ids,
            finished_slot=on_success,
            error_slot=on_error
        )
