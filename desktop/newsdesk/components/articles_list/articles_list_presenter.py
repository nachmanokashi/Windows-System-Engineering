from PySide6.QtCore import QObject, QThread, Signal, Slot 
from typing import TYPE_CHECKING, Optional, List, Dict, Any

if TYPE_CHECKING:
    from newsdesk.components.articles_list.articles_list_view import ArticlesListComponent

from newsdesk.infra.http.news_service_http import HttpNewsService
from newsdesk.infra.http.likes_service_http import HttpLikesService 

# WorkerThread 
class WorkerThread(QThread):
    finished = Signal(object); error = Signal(str)
    def __init__(self, func, *args, **kwargs): super().__init__(); self.func = func; self.args = args; self.kwargs = kwargs
    def run(self):
        try: result = self.func(*self.args, **self.kwargs); self.finished.emit(result)
        except Exception as e: self.error.emit(str(e))

class ArticlesListPresenter(QObject):
    """
    Presenter for ArticlesListComponent. Handles loading, searching, filtering, and like actions.
    """
    def __init__(self, view: 'ArticlesListComponent', news_service: HttpNewsService, likes_service: HttpLikesService):
        super().__init__()
        self.view = view
        self.news_service = news_service
        self.likes_service = likes_service 

        # State
        self.current_page = 1; self.page_size = 20
        self.current_category: Optional[str] = None
        self.current_search_query: Optional[str] = None
        self.cached_articles: List[Dict[str, Any]] = []
        self.cached_likes: Dict[int, Dict] = {}

        # Threads
        self.active_threads: List[QThread] = [] 

    def _start_worker(self, func, *args, finished_slot=None, error_slot=None, **kwargs):
        """Helper method to start and manage WorkerThreads"""
        thread = WorkerThread(func, *args, **kwargs)
        if finished_slot:
            thread.finished.connect(finished_slot)
        if error_slot:
            thread.error.connect(error_slot)
        thread.finished.connect(lambda t=thread: self._remove_thread(t))
        thread.error.connect(lambda e, t=thread: self._remove_thread(t))
        self.active_threads.append(thread)
        thread.start()
        return thread

    def _remove_thread(self, thread: QThread):
        """Removes a thread from the active list"""
        try:
            self.active_threads.remove(thread)
        except ValueError:
            pass 


    def load_articles(self, page: int = 1) -> None:
        """Loads articles from the server."""
        self.current_page = page
        self.view.show_loading("Loading articles...")
        self._start_worker(
            self.news_service.list_articles, page=page, page_size=self.page_size, category=self.current_category,
            finished_slot=self._on_articles_loaded,
            error_slot=self._on_load_error
        )

    def search_articles(self, query: str) -> None:
        """Searches articles."""
        if not query or len(query) < 2:
            self.current_search_query = None; self.load_articles(); return
        self.current_search_query = query
        self.view.show_loading(f"Searching for '{query}'...")
        self._start_worker(
            self.news_service.search_articles, query=query, category=self.current_category, limit=self.page_size * 2,
            finished_slot=self._on_search_results,
            error_slot=self._on_load_error
        )

    def filter_by_category(self, category: Optional[str]) -> None:
        """Filters articles by category."""
        self.current_category = category if category else None
        if self.current_search_query: self.search_articles(self.current_search_query)
        else: self.load_articles(page=1)

    def load_categories(self) -> None:
        """Loads the list of categories."""
        self._start_worker(
            self.news_service.get_categories,
            finished_slot=self._on_categories_loaded,
            error_slot=lambda err: print(f"Failed to load categories: {err}")
        )

    # Callbacks & Data Handling
    def _on_articles_loaded(self, response: Dict[str, Any]) -> None:
        self.view.hide_loading()
        self.cached_articles = response.get("items", [])
        total = response.get("total", 0)
        self._load_likes_for_current_articles()
        self.view.update_status(f"Loaded {len(self.cached_articles)} of {total} articles. Fetching likes...")

    def _on_search_results(self, response: Dict[str, Any]) -> None:
        self.view.hide_loading()
        self.cached_articles = response.get("items", [])
        self._load_likes_for_current_articles()
        self.view.update_status(f"Found {len(self.cached_articles)} articles matching '{self.current_search_query}'. Fetching likes...")

    def _load_likes_for_current_articles(self):
        if not self.cached_articles:
            self.view.display_articles([], {}); return
        
        article_ids = []
        for a in self.cached_articles:
            try:
                article_ids.append(int(a.get("id")))
            except (ValueError, TypeError):
                print(f"Warning: Invalid article ID '{a.get('id')}' found in list.")
        
        if not article_ids:
            self.view.display_articles(self.cached_articles, {}); return
            
        print(f"Presenter: Fetching batch stats for {len(article_ids)} articles...")
        self._start_worker(
            self.likes_service.get_batch_stats, article_ids,
            finished_slot=self._on_likes_loaded,
            error_slot=self._on_likes_load_error
        )

    def _on_likes_loaded(self, stats_data: Dict[str, Any]):
        print(f"Presenter: Received stats for {len(stats_data)} articles.")
        self.cached_likes = {int(k): v for k, v in stats_data.items()}
        self.view.display_articles(self.cached_articles, self.cached_likes)
        self.view.update_status(f"Showing {len(self.cached_articles)} articles.")

    def _on_likes_load_error(self, error: str):
        print(f"Presenter Error: Failed to load like stats: {error}")
        self.cached_likes = {}
        self.view.display_articles(self.cached_articles, {})
        self.view.show_error(f"Could not load like/dislike status: {error}")
        self.view.update_status(f"Showing {len(self.cached_articles)} articles (like status unavailable).")

    def _on_categories_loaded(self, response: Dict[str, Any]) -> None:
        categories = response.get("items", [])
        self.view.display_categories(categories)

    def _on_load_error(self, error: str) -> None:
        self.view.hide_loading()
        self.view.show_error(f"Failed to load data: {error}")
        self.view.update_status("Error loading data")

    # Like/Dislike Handling
    @Slot(int)
    def toggle_like(self, article_id: int):
        if not self.likes_service: return
        print(f"Presenter (List): Toggle like for {article_id}")
        current_status = self.cached_likes.get(article_id, {})
        currently_liked = current_status.get("user_liked", False)
        api_call = self.likes_service.unlike_article if currently_liked else self.likes_service.like_article
        card = self.view.card_widgets.get(article_id)
        if card: card.like_button.setEnabled(False); card.dislike_button.setEnabled(False)
        self._start_worker(
            api_call, article_id,
            finished_slot=lambda result, aid=article_id: self._on_toggle_finished(aid, result),
            error_slot=lambda error, aid=article_id: self._on_toggle_error(aid, error)
        )

    @Slot(int)
    def toggle_dislike(self, article_id: int):
        if not self.likes_service: return
        print(f"Presenter (List): Toggle dislike for {article_id}")
        current_status = self.cached_likes.get(article_id, {})
        currently_disliked = current_status.get("user_disliked", False)
        api_call = self.likes_service.remove_dislike if currently_disliked else self.likes_service.dislike_article
        card = self.view.card_widgets.get(article_id)
        if card: card.like_button.setEnabled(False); card.dislike_button.setEnabled(False)
        self._start_worker(
            api_call, article_id,
            finished_slot=lambda result, aid=article_id: self._on_toggle_finished(aid, result),
            error_slot=lambda error, aid=article_id: self._on_toggle_error(aid, error)
        )

    def _on_toggle_finished(self, article_id: int, result: Dict):
        print(f"Presenter (List): Toggle finished for {article_id}, result: {result}")
        card = self.view.card_widgets.get(article_id)
        if card: card.like_button.setEnabled(True); card.dislike_button.setEnabled(True)
        if result and "stats" in result:
            new_stats = result["stats"]
            self.cached_likes[article_id] = new_stats
            self.view.update_article_card_stats(article_id, new_stats)
        else:
            print(f"Error: Invalid response from list toggle API: {result}")
            if card: self.view.update_article_card_stats(article_id, self.cached_likes.get(article_id, {}))
            self.view.show_error("Could not update like status.")

    def _on_toggle_error(self, article_id: int, error: str):
        print(f"Presenter (List): Toggle error for {article_id}: {error}")
        card = self.view.card_widgets.get(article_id)
        if card: card.like_button.setEnabled(True); card.dislike_button.setEnabled(True)
        if card: self.view.update_article_card_stats(article_id, self.cached_likes.get(article_id, {}))
        self.view.show_error(f"Error updating status: {error}")

    # Cleanup
    def cleanup(self) -> None:
        """Cleans up all active threads."""
        print(f"Cleaning up {len(self.active_threads)} threads in ArticlesListPresenter...")
        threads_to_stop = self.active_threads[:]
        self.active_threads.clear()
        for thread in threads_to_stop:
            try:
                if thread.isRunning(): thread.quit(); thread.wait(1000)
            except: pass
        print("ArticlesListPresenter cleanup complete.")