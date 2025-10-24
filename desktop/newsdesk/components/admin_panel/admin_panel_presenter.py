from typing import Dict, Any, List
from PySide6.QtWidgets import QMessageBox

from newsdesk.infra.http.admin_service_http import AdminServiceHttp
from newsdesk.infra.http.news_service_http import HttpNewsService
from newsdesk.components.admin_panel.admin_panel_view import AdminPanelComponent, ArticleFormDialog
from newsdesk.mvp.presenter.base_presenter import BasePresenter


class AdminPanelPresenter(BasePresenter):
    """Admin Panel Presenter"""

    def __init__(self, view: AdminPanelComponent, admin_service: AdminServiceHttp, news_service: HttpNewsService):
        super().__init__(view)
        self.view = view
        self.admin_service = admin_service
        self.news_service = news_service
        self.categories: List[str] = []

        if hasattr(self.view, "set_presenter"):
            self.view.set_presenter(self)

        self._connect_signals()
        self.load_categories()
        self.load_articles()

    def _connect_signals(self):
        """Connect view signals to presenter methods"""
        self.view.add_article_requested.connect(self.on_add_article)
        self.view.delete_article_requested.connect(self.on_delete_article)
        self.view.edit_article_requested.connect(self.on_edit_article)
        self.view.refresh_articles_requested.connect(self.load_articles)
        self.view.classify_requested.connect(self.on_classify_article)
        self.view.apply_classification_requested.connect(self.on_apply_classification)
        self.view.batch_classify_requested.connect(self.on_batch_classify)

    def attach_view(self, view: AdminPanelComponent) -> None:
        self.view = view

    def detach_view(self) -> None:
        pass

    def load_categories(self):
        """Load available categories"""
        self.view.show_loading("Loading categories...")

        def on_success(data):
            if isinstance(data, list):
                cats = data
            elif isinstance(data, dict):
                cats = data.get("categories", [])
            else:
                cats = []

            self.categories = cats or []
            self.view.set_categories(self.categories)
            self.view.hide_loading()

        def on_error(error: str):
            self.view.hide_loading()
            self.view.show_error(f"Failed to load categories: {error}")

        self._start_worker(
            self.admin_service.get_available_categories,
            finished_slot=on_success,
            error_slot=on_error
        )

    def load_articles(self):
        """Load articles list"""
        self.view.show_loading("Loading articles list...")

        def on_articles_loaded(data):
            self.view.hide_loading()
            if isinstance(data, list):
                articles = data
            elif isinstance(data, dict):
                articles = data.get("articles", []) or data.get("data", [])
            else:
                articles = []
            self.view.display_articles(articles)

        def on_error(error: str):
            self.view.hide_loading()
            if "422" in str(error):
                self.view.show_error("The requested 'limit' is not allowed by the server. Try a smaller value (<=100).")
            else:
                self.view.show_error(f"Failed to load articles: {error}")

        self._start_worker(
            self.admin_service.get_all_articles,
            finished_slot=on_articles_loaded,
            error_slot=on_error,
            limit=50
        )

    def on_add_article(self):
        """Open dialog to add new article"""
        dialog = ArticleFormDialog(self.view, categories=self.categories)

        def _on_draft(payload: Dict[str, Any]):
            """Classify draft article with AI"""
            title = payload.get("title", "")
            summary = payload.get("summary", "")
            content = payload.get("content", "")
            
            try:
                result = self.admin_service.classify_draft(title=title, summary=summary, content=content)
                category = result.get("suggested_category") or result.get("category", "General")
                confidence = result.get("confidence", 0.0)
                dialog.show_classification_result(category, confidence)
            except Exception as e:
                dialog.show_classification_error(f"Classification failed: {str(e)}")

        if hasattr(dialog, "draft_classify_requested"):
            dialog.draft_classify_requested.connect(_on_draft)

        if dialog.exec() == ArticleFormDialog.Accepted:
            data = dialog.get_data()
            self._create_article(data)

    def _create_article(self, data: Dict[str, Any]):
        """Create new article"""
        self.view.show_loading("Creating new article...")

        def on_success(response: Dict[str, Any]):
            article_id = response.get("article_id") or response.get("id", "N/A")
            self.view.hide_loading()
            self.view.show_success(f"Article #{article_id} created successfully!")
            self.load_articles()

        def on_error(error: str):
            self.view.hide_loading()
            self.view.show_error(f"Failed to create article: {error}")

        self._start_worker(
            self.admin_service.create_article,
            finished_slot=on_success,
            error_slot=on_error,
            **data
        )

    def on_edit_article(self, article_id: int):
        """Load article for editing"""
        self.view.show_loading(f"Loading article #{article_id}...")

        def on_article_loaded(data: Dict[str, Any]):
            self.view.hide_loading()
            article_data = data.get("article") if isinstance(data, dict) else data
            if not article_data:
                self.view.show_error(f"Article #{article_id} not found.")
                return

            dialog = ArticleFormDialog(self.view, article_data=article_data, categories=self.categories)

            def _on_draft(payload: Dict[str, Any]):
                """Classify draft article with AI"""
                title = payload.get("title", "")
                summary = payload.get("summary", "")
                content = payload.get("content", "")
                
                try:
                    result = self.admin_service.classify_draft(title=title, summary=summary, content=content)
                    category = result.get("suggested_category") or result.get("category", "General")
                    confidence = result.get("confidence", 0.0)
                    dialog.show_classification_result(category, confidence)
                except Exception as e:
                    dialog.show_classification_error(f"Classification failed: {str(e)}")

            if hasattr(dialog, "draft_classify_requested"):
                dialog.draft_classify_requested.connect(_on_draft)

            if dialog.exec() == ArticleFormDialog.Accepted:
                updated_data = dialog.get_data()
                self._update_article(article_id, updated_data)

        def on_error(error: str):
            self.view.hide_loading()
            self.view.show_error(f"Failed to load article for edit: {error}")

        self._start_worker(
            self.admin_service.get_article_details,
            article_id=article_id,
            finished_slot=on_article_loaded,
            error_slot=on_error
        )

    def _update_article(self, article_id: int, data: Dict[str, Any]):
        """Update existing article"""
        self.view.show_loading(f"Updating article #{article_id}...")

        def on_success(response: Dict[str, Any]):
            self.view.hide_loading()
            self.view.show_success(f"Article #{article_id} updated successfully.")
            self.load_articles()

        def on_error(error: str):
            self.view.hide_loading()
            self.view.show_error(f"Failed to update article: {error}")

        self._start_worker(
            self.admin_service.update_article,
            article_id=article_id,
            finished_slot=on_success,
            error_slot=on_error,
            **data
        )

    def on_delete_article(self, article_id: int):
        """Delete article"""
        self.view.show_loading(f"Deleting article #{article_id}...")

        def on_success(response: Dict[str, Any]):
            self.view.hide_loading()
            self.view.show_success(f"Article #{article_id} deleted.")
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

    def on_classify_article(self, article_id: int):
        """Classify existing article with AI"""
        self.view.show_loading(f"Classifying article #{article_id}...")

        def on_success(response: Dict[str, Any]):
            self.view.hide_loading()
            suggested = response.get("suggested_category") or response.get("category") or "N/A"
            confidence = response.get("confidence") or response.get("score") or 0.0
            self.view.show_info(
                f"Classification result for article #{article_id}: "
                f"Suggested category is '{suggested}' (Confidence: {confidence:.2f})"
            )

        def on_error(error: str):
            self.view.hide_loading()
            self.view.show_error(f"Failed to classify article: {error}")

        self._start_worker(
            self.admin_service.classify_article,
            article_id=article_id,
            finished_slot=on_success,
            error_slot=on_error
        )

    def on_apply_classification(self, article_id: int):
        """Apply AI classification and save to DB"""
        self.view.show_loading(f"Applying AI classification to article #{article_id}...")

        def on_success(response: Dict[str, Any]):
            self.view.hide_loading()
            new_category = response.get("new_category") or response.get("category") or "N/A"
            self.view.show_success(f"Article #{article_id} category set to '{new_category}' by AI.")
            self.load_articles()

        def on_error(error: str):
            self.view.hide_loading()
            self.view.show_error(f"Failed to apply classification: {error}")

        self._start_worker(
            self.admin_service.apply_classification,
            article_id=article_id,
            finished_slot=on_success,
            error_slot=on_error
        )

    def on_batch_classify(self):
        """Batch classify uncategorized articles"""
        self.view.show_loading("Loading uncategorized articles...")

        def on_uncategorized_loaded(data: Dict[str, Any]):
            articles = data.get("articles", []) if isinstance(data, dict) else (data or [])
            article_ids = [a["id"] for a in articles if isinstance(a, dict) and "id" in a]

            if article_ids:
                self.view.update_status(f"Found {len(article_ids)} uncategorized articles.")

                reply = QMessageBox.question(
                    self.view,
                    "Confirm Batch Classify",
                    f"Found {len(article_ids)} articles without a category. "
                    f"Do you want to send them for batch AI classification? This may take a moment.",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )

                if reply == QMessageBox.Yes:
                    self._batch_classify(article_ids)
                else:
                    self.view.hide_loading()
                    return
            else:
                self.view.hide_loading()
                self.view.show_info("No uncategorized articles found for batch classification.")

        def on_error(error: str):
            self.view.hide_loading()
            self.view.show_error(f"Failed to fetch uncategorized articles: {error}")

        self._start_worker(
            self.admin_service.get_uncategorized_articles,
            limit=50,
            finished_slot=on_uncategorized_loaded,
            error_slot=on_error
        )

    def _batch_classify(self, article_ids: List[int]):
        """Send batch classification request"""
        self.view.update_status("Classifying articles with AI...")

        def on_success(response: Dict[str, Any]):
            self.view.hide_loading()
            total = response.get("total", len(article_ids))
            self.view.show_success(f"Batch classification complete for {total} articles.")
            self.load_articles()

        def on_error(error: str):
            self.view.hide_loading()
            self.view.show_error(f"Batch classification failed: {error}")

        self._start_worker(
            self.admin_service.batch_classify,
            article_ids=article_ids,
            finished_slot=on_success,
            error_slot=on_error
        )