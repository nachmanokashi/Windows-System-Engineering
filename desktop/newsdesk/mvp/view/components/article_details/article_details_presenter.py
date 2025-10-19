# desktop/newsdesk/mvp/view/components/article_details/article_details_presenter.py
"""
ArticleDetailsPresenter - הלוגיקה של ArticleDetailsComponent
"""
from PySide6.QtCore import QObject, QThread, Signal
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from .article_details_view import ArticleDetailsComponent

from newsdesk.infra.http.news_service_http import HttpNewsService
from newsdesk.mvp.model.article import Article # Import the model

# WorkerThread (No change needed)
class WorkerThread(QThread):
    finished = Signal(object)
    error = Signal(str)
    def __init__(self, func, *args, **kwargs):
        super().__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs
    def run(self):
        try:
            result = self.func(*self.args, **self.kwargs)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))


class ArticleDetailsPresenter(QObject):
    """
    Presenter of ArticleDetailsComponent
    Responsible for loading article details from the server.
    """
    def __init__(self, view: 'ArticleDetailsComponent', news_service: HttpNewsService):
        super().__init__()
        self.view = view
        self.news_service = news_service
        self.thread: Optional[WorkerThread] = None

    def load_article_details(self, article_id: int) -> None:
        """Loads the full article details from the server."""
        self.view.show_loading(f"Loading article {article_id}...")
        if self.thread and self.thread.isRunning():
            self.thread.quit()
            self.thread.wait()

        self.thread = WorkerThread(self.news_service.get, str(article_id)) # Pass ID as string
        self.thread.finished.connect(self._on_article_loaded)
        self.thread.error.connect(self._on_load_error)
        self.thread.start()

    # --- שינוי כאן: מעבירים את אובייקט Article ישירות ---
    def _on_article_loaded(self, article_obj: Optional[Article]) -> None:
        """Called when article details are loaded successfully."""
        self.view.hide_loading()
        if article_obj and isinstance(article_obj, Article):
            # מעבירים את האובייקט המלא ל-View
            self.view.display_article(article_obj)
        else:
            # Trigger error handling if article_obj is None or not an Article
            print(f"Error: Did not receive a valid Article object. Got: {type(article_obj)}")
            self._on_load_error("Article data not found or invalid.")

    def _on_load_error(self, error: str) -> None:
        """Called when there is an error during loading."""
        self.view.hide_loading()
        print(f"Error loading article details: {error}")
        # --- תיקנו כאן: שימוש ב-show_error ---
        self.view.show_error(f"Failed to load article details: {error}")

    def cleanup(self) -> None:
        """Cleans up the thread if still running."""
        if self.thread and self.thread.isRunning():
            try:
                self.thread.quit()
                self.thread.wait(1000)
            except:
                pass
        self.thread = None