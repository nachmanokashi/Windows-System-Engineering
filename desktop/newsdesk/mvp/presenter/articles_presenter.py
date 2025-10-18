from typing import List, Dict, Any, Callable
from PySide6.QtCore import QObject, Slot, QTimer, QThread, Signal
from newsdesk.mvp.view.articles_window import ArticlesWindow
from newsdesk.mvp.view.article_detail_window import ArticleDetailWindow
from newsdesk.mvp.model.article import Article
from newsdesk.infra.http.news_service_http import HttpNewsService
from newsdesk.infra.http.likes_service_http import HttpLikesService
from newsdesk.infra.http.news_api_client import NewsApiClient

class WorkerThread(QThread):
    """Worker thread for background tasks"""
    finished = Signal(object)
    error = Signal(str)
    
    def __init__(self, fn: Callable, *args, **kwargs):
        super().__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
    
    def run(self):
        try:
            result = self.fn(*self.args, **self.kwargs)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))


class ArticlesPresenter(QObject):
    def __init__(self, view: ArticlesWindow, service: HttpNewsService, api_client: NewsApiClient) -> None:
        super().__init__()
        self._view = view
        self._service = service
        self._likes_service = HttpLikesService(api_client)
        
        self._likes_cache: Dict[str, Dict[int, Dict]] = {}
        self._threads: List[QThread] = []
        self._debounce: Dict[str, QTimer] = {}
        self._token: Dict[str, int] = {}
        
        for cat in self._view.categories:
            timer = QTimer(self)
            timer.setSingleShot(True)
            timer.setInterval(250)
            timer.timeout.connect(lambda c=cat: self._do_search(c))
            self._debounce[cat] = timer
            self._token[cat] = 0
            
            self._view.search_box(cat).textChanged.connect(
                lambda _t, c=cat: self.on_search_changed(c)
            )

        self._view.article_card_clicked.connect(self.show_article_details)
        self._view.like_button_clicked.connect(self._toggle_like)
        self._view.dislike_button_clicked.connect(self._toggle_dislike)

    def _cleanup_thread(self, thread: QThread):
        """נקה thread"""
        try:
            self._threads.remove(thread)
        except ValueError:
            pass
    
    def load_initial(self) -> None:
        """טעינה ראשונית לכל הטאבים"""
        for cat in self._view.categories:
            thread = WorkerThread(self._service.top, 20, cat)
            self._threads.append(thread)
            thread.finished.connect(lambda items, c=cat: self._on_loaded(c, items))
            thread.error.connect(lambda e, c=cat: print(f"Error loading {c}: {e}"))
            thread.finished.connect(lambda t=thread: self._cleanup_thread(t))
            thread.error.connect(lambda e, t=thread: self._cleanup_thread(t))
            thread.start()
    
    @Slot(object)
    def _on_loaded(self, cat: str, items_obj: object) -> None:
        """מאמרים נטענו"""
        items: List[Article] = items_obj
        self._load_likes_for_articles(cat, items)
    
    def _load_likes_for_articles(self, cat: str, articles: List[Article]) -> None:
        """טוען סטטיסטיקות לייקים עבור רשימת כתבות"""
        if not articles:
            self._view.set_articles(cat, [], {})
            return

        article_ids = [int(a.id) for a in articles]
        
        def on_stats_loaded(stats_obj: object):
            stats_data = stats_obj
            stats_data_int_keys = {int(k): v for k, v in stats_data.items()}
            self._likes_cache[cat] = stats_data
            self._view.set_articles(cat, articles, stats_data)

        thread = WorkerThread(self._likes_service.get_batch_stats, article_ids)
        thread.finished.connect(on_stats_loaded)
        thread.error.connect(lambda e: print(f"Error loading likes stats: {e}"))
        self._threads.append(thread)
        thread.finished.connect(lambda t=thread: self._cleanup_thread(t))
        thread.start()

    @Slot()
    def on_search_changed(self, cat: str) -> None:
        """חיפוש השתנה"""
        self._debounce[cat].start()
    
    def _do_search(self, cat: str) -> None:
        """ביצוע חיפוש"""
        q = self._view.search_box(cat).text().strip()
        self._token[cat] += 1
        my_token = self._token[cat]
        
        def on_result(items_obj: object) -> None:
            if my_token != self._token[cat]:
                return
            items: List[Article] = items_obj
            self._load_likes_for_articles(cat, items)
        
        if q:
            thread = WorkerThread(self._service.search, q, 20, cat)
        else:
            thread = WorkerThread(self._service.top, 20, cat)
        
        self._threads.append(thread)
        thread.finished.connect(on_result)
        thread.error.connect(lambda e: print(f"Search error: {e}"))
        thread.finished.connect(lambda t=thread: self._cleanup_thread(t))
        thread.error.connect(lambda e, t=thread: self._cleanup_thread(t))
        thread.start()
    
    @Slot(Article)
    def show_article_details(self, article: Article) -> None:
        """מציג חלון פרטי כתבה"""
        cat = article.category
        article_id = int(article.id)
        
        stats = self._likes_cache.get(cat, {}).get(article_id, {
            "likes_count": 0, "dislikes_count": 0, "user_liked": False, "user_disliked": False
        })

        detail_window = ArticleDetailWindow(
            article=article,
            likes_count=stats['likes_count'],
            user_liked=stats['user_liked'],
            parent=self._view
        )
        detail_window.like_clicked.connect(self._toggle_like)
        detail_window.exec()

    def _update_ui_for_article(self, article_id: int, new_stats: Dict):
        """מעדכן את ה-UI ואת ה-cache לאחר שינוי"""
        for cat, cache in self._likes_cache.items():
            if article_id in cache:
                cache[article_id] = new_stats
                self._view.update_article_card(cat, article_id, new_stats)
                break

    @Slot(Article)
    def _toggle_like(self, article: Article) -> None:
        """מטפל בלחיצה על כפתור לייק"""
        article_id = int(article.id)
        cat = article.category
        currently_liked = self._likes_cache.get(cat, {}).get(article_id, {}).get("user_liked", False)

        service_call = self._likes_service.unlike_article if currently_liked else self._likes_service.like_article

        thread = WorkerThread(service_call, article_id)
        thread.finished.connect(lambda result: self._update_ui_for_article(article_id, result.get("stats", {})))
        thread.error.connect(lambda e: print(f"Error toggling like: {e}"))
        self._threads.append(thread)
        thread.finished.connect(lambda t=thread: self._cleanup_thread(t))
        thread.start()

    @Slot(Article)
    def _toggle_dislike(self, article: Article) -> None:
        """מטפל בלחיצה על כפתור דיסלייק"""
        article_id = int(article.id)
        cat = article.category
        currently_disliked = self._likes_cache.get(cat, {}).get(article_id, {}).get("user_disliked", False)

        service_call = self._likes_service.remove_dislike if currently_disliked else self._likes_service.dislike_article
        
        thread = WorkerThread(service_call, article_id)
        thread.finished.connect(lambda result: self._update_ui_for_article(article_id, result.get("stats", {})))
        thread.error.connect(lambda e: print(f"Error toggling dislike: {e}"))
        self._threads.append(thread)
        thread.finished.connect(lambda t=thread: self._cleanup_thread(t))
        thread.start()