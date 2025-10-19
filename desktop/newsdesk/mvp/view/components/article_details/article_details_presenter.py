# desktop/newsdesk/mvp/view/components/article_details/article_details_presenter.py
"""
ArticleDetailsPresenter - הלוגיקה של ArticleDetailsComponent
"""
from PySide6.QtCore import QObject, QThread, Signal, Slot
from typing import TYPE_CHECKING, Optional, Dict, List # הוספנו List

if TYPE_CHECKING:
    from .article_details_view import ArticleDetailsComponent

from newsdesk.infra.http.news_service_http import HttpNewsService
from newsdesk.mvp.model.article import Article
from newsdesk.infra.http.likes_service_http import HttpLikesService
from dataclasses import asdict

# WorkerThread (No change needed)
class WorkerThread(QThread):
    finished = Signal(object)
    error = Signal(str)
    def __init__(self, func, *args, **kwargs):
        super().__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs
        # Set parent to manage lifetime? Maybe not needed if presenter manages manually.
        # self.setParent(kwargs.get('parent', None))
    def run(self):
        try:
            result = self.func(*self.args, **self.kwargs)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))


class ArticleDetailsPresenter(QObject):
    """
    Presenter of ArticleDetailsComponent
    Responsible for loading article details and handling like/dislike actions.
    """
    def __init__(self, view: 'ArticleDetailsComponent', news_service: HttpNewsService):
        super().__init__()
        self.view = view
        self.news_service = news_service
        self.likes_service: Optional[HttpLikesService] = None
        # --- שינוי כאן: רשימה לניהול Threads ---
        self.active_threads: List[WorkerThread] = []
        self.current_stats: Dict[int, Dict] = {}

        self.view.like_toggled.connect(self.toggle_like)
        self.view.dislike_toggled.connect(self.toggle_dislike)

    def _start_worker(self, func, *args, finished_slot=None, error_slot=None, **kwargs):
        """Helper method to start and manage WorkerThreads"""
        # נקה threads קודמים מאותו סוג (אם צריך למנוע כפילות)
        # למשל, אם לא רוצים שטעינת הלייקים תרוץ פעמיים
        thread = WorkerThread(func, *args, **kwargs)
        if finished_slot:
            thread.finished.connect(finished_slot)
        if error_slot:
            thread.error.connect(error_slot)
        # חבר פונקציה שתנקה את ה-thread מהרשימה כשהוא מסיים
        thread.finished.connect(lambda t=thread: self._remove_thread(t))
        thread.error.connect(lambda e, t=thread: self._remove_thread(t)) # נקה גם בשגיאה
        self.active_threads.append(thread)
        thread.start()
        return thread # החזר את ה-thread אם צריך אותו ספציפית

    def _remove_thread(self, thread: WorkerThread):
        """Removes a thread from the active list"""
        try:
            self.active_threads.remove(thread)
        except ValueError:
            pass # Thread already removed or wasn't added properly

    def load_article_details(self, article_id: int) -> None:
        """Loads the full article details and like status from the server."""
        self.view.show_loading(f"Loading article {article_id}...")
        # נקה threads קודמים של טעינת *כתבה* ספציפית זו (אם רוצים)
        # self.cleanup() # אפשרות קיצונית יותר: נקה הכל לפני טעינה חדשה
        self.current_stats.pop(article_id, None)

        # טען תוכן כתבה
        self._start_worker(
            self.news_service.get, str(article_id),
            finished_slot=self._on_article_loaded,
            error_slot=self._on_load_error
        )
        # טען סטטוס לייקים
        self._load_like_stats(article_id)

    def _on_article_loaded(self, article_obj: Optional[Article]) -> None:
        if article_obj and isinstance(article_obj, Article):
            self.view.display_article(article_obj)
            article_id_int = int(article_obj.id)
            # בדוק אם גם הסטטוס נטען
            if article_id_int in self.current_stats:
                self.view.update_like_buttons(self.current_stats[article_id_int])
                self.view.hide_loading()
        else:
            print(f"Error: Did not receive a valid Article object. Got: {type(article_obj)}")
            # אם הכתבה נכשלה, עדיין צריך להסתיר טעינה אם הסטטוס יצליח
            # זה יטופל ב-_on_stats_loaded
            self._on_load_error("Article data not found or invalid.")

    def _load_like_stats(self, article_id: int):
        if not self.likes_service:
            print("Error: Likes service not available...")
            self._check_hide_loading_on_error(article_id)
            return
        self._start_worker(
            self.likes_service.get_article_stats, article_id,
            finished_slot=lambda stats, aid=article_id: self._on_stats_loaded(aid, stats),
            error_slot=lambda error, aid=article_id: self._on_stats_load_error(aid, error)
        )

    def _on_stats_loaded(self, article_id: int, stats: Dict):
        print(f"Stats loaded for article {article_id}: {stats}")
        self.current_stats[article_id] = stats
        # עדכן כפתורים רק אם ה-View מציג את המאמר הזה
        if self.view.current_article_obj and int(self.view.current_article_obj.id) == article_id:
            self.view.update_like_buttons(stats)
            self.view.hide_loading() # הסתר טעינה אחרי ששניהם נטענו

    def _on_stats_load_error(self, article_id: int, error: str):
        print(f"Error loading stats for article {article_id}: {error}")
        self.current_stats[article_id] = {"likes_count": 0, "dislikes_count": 0, "user_liked": False, "user_disliked": False}
        self._check_hide_loading_on_error(article_id)
        if self.view.current_article_obj and int(self.view.current_article_obj.id) == article_id:
             self.view.update_like_buttons(self.current_stats[article_id])
             self.view.show_error(f"Could not load like status: {error}")

    def _check_hide_loading_on_error(self, article_id: int):
         """Hide loading if the view is showing the current article, even on error"""
         if self.view.current_article_obj and int(self.view.current_article_obj.id) == article_id:
              self.view.hide_loading()


    def get_current_stats(self, article_id: int) -> Dict:
        return self.current_stats.get(int(article_id), {})

    @Slot(int)
    def toggle_like(self, article_id: int):
        if not self.likes_service: return
        print(f"Presenter: Toggle like for {article_id}")
        current_like_status = self.current_stats.get(article_id, {}).get("user_liked", False)
        api_call = self.likes_service.unlike_article if current_like_status else self.likes_service.like_article
        self.view.like_button.setEnabled(False)
        self.view.dislike_button.setEnabled(False)
        self._start_worker(
            api_call, article_id,
            finished_slot=lambda result, aid=article_id: self._on_toggle_finished(aid, result),
            error_slot=lambda error, aid=article_id: self._on_toggle_error(aid, error)
        )

    @Slot(int)
    def toggle_dislike(self, article_id: int):
        if not self.likes_service: return
        print(f"Presenter: Toggle dislike for {article_id}")
        current_dislike_status = self.current_stats.get(article_id, {}).get("user_disliked", False)
        api_call = self.likes_service.remove_dislike if current_dislike_status else self.likes_service.dislike_article
        self.view.like_button.setEnabled(False)
        self.view.dislike_button.setEnabled(False)
        self._start_worker(
            api_call, article_id,
            finished_slot=lambda result, aid=article_id: self._on_toggle_finished(aid, result),
            error_slot=lambda error, aid=article_id: self._on_toggle_error(aid, error)
        )

    def _on_toggle_finished(self, article_id: int, result: Dict):
        print(f"Presenter: Toggle finished for {article_id}, result: {result}")
        # הפעל מחדש כפתורים רק אם ה-View עדיין מציג את המאמר הזה
        if self.view.current_article_obj and int(self.view.current_article_obj.id) == article_id:
            if hasattr(self.view, 'like_button'): self.view.like_button.setEnabled(True)
            if hasattr(self.view, 'dislike_button'): self.view.dislike_button.setEnabled(True)

            if result and "stats" in result:
                new_stats = result["stats"]
                self.current_stats[article_id] = new_stats
                self.view.update_like_buttons(new_stats)
            else:
                print(f"Error: Invalid response from toggle API: {result}")
                self.view.update_like_buttons(self.current_stats.get(article_id, {}))
                self.view.show_error("Could not update like status.")

    def _on_toggle_error(self, article_id: int, error: str):
        print(f"Presenter: Toggle error for {article_id}: {error}")
        if self.view.current_article_obj and int(self.view.current_article_obj.id) == article_id:
            if hasattr(self.view, 'like_button'): self.view.like_button.setEnabled(True)
            if hasattr(self.view, 'dislike_button'): self.view.dislike_button.setEnabled(True)
            self.view.show_error(f"Error updating status: {error}")
            self.view.update_like_buttons(self.current_stats.get(article_id, {}))

    def _on_load_error(self, error: str) -> None:
        """Called when there is an error during article loading."""
        # אם טעינת הכתבה נכשלה, צריך להסתיר טעינה בכל מקרה
        self.view.hide_loading()
        print(f"Error loading article details: {error}")
        self.view.show_error(f"Failed to load article details: {error}")

    # --- שינוי כאן: לולאה על כל ה-Threads הפעילים ---
    def cleanup(self) -> None:
        """Cleans up all active threads."""
        print(f"Cleaning up {len(self.active_threads)} active threads in ArticleDetailsPresenter...")
        threads_to_stop = self.active_threads[:] # Create a copy to iterate over
        self.active_threads.clear() # Clear the list immediately

        for thread in threads_to_stop:
            try:
                if thread.isRunning():
                    print(f"Stopping thread {thread}...")
                    thread.quit() # Request termination
                    if not thread.wait(1500): # Wait up to 1.5 seconds
                         print(f"Warning: Thread {thread} did not terminate gracefully.")
                         # thread.terminate() # Force terminate if needed (use with caution)
                print(f"Thread {thread} finished/stopped.")
            except Exception as e:
                print(f"Error during thread cleanup: {e}")
        print("ArticleDetailsPresenter cleanup complete.")