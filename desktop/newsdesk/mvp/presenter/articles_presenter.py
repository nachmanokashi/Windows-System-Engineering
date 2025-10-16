# newsdesk/mvp/presenter/articles_presenter.py
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
        
        # Cache של likes
        self._likes_cache: Dict[str, Dict[int, Dict]] = {}
        
        # שמירת threads פעילים
        self._threads: List[QThread] = []
        
        # דיבאונס וטוקנים פר קטגוריה
        self._debounce: Dict[str, QTimer] = {}
        self._token: Dict[str, int] = {}
        
        # חיבורי אירועים לכל קטגוריה
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
            
            # שמור reference
            self._threads.append(thread)
            
            # חבר signals
            thread.finished.connect(lambda items, c=cat: self._on_loaded(c, items))
            thread.error.connect(lambda e, c=cat: print(f"Error loading {c}: {e}"))
            
            # נקה
            thread.finished.connect(lambda t=thread: self._cleanup_thread(t))
            thread.error.connect(lambda e, t=thread: self._cleanup_thread(t))
            
            thread.start()
    
    @Slot(object)
    def _on_loaded(self, cat: str, items_obj: object) -> None:
        """מאמרים נטענו"""
        items: List[Article] = items_obj
        
        # טען likes לכל המאמרים
        self._load_likes_for_articles(cat, items)
    
    def _load_likes_for_articles(self, cat: str, articles: List[Article]) -> None:
        """טען likes לכל המאמרים"""
        # כרגע פשוט נציג בלי likes
        likes_data = {}
        for article in articles:
            likes_data[int(article.id)] = {
                "likes_count": 0,
                "user_liked": False
            }
        
        self._likes_cache[cat] = likes_data
        self._view.set_articles(cat, articles, likes_data)
    
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
        
        # צור thread
        if q:
            thread = WorkerThread(self._service.search, q, 20, cat)
        else:
            thread = WorkerThread(self._service.top, 20, cat)
        
        # שמור reference
        self._threads.append(thread)
        
        thread.finished.connect(on_result)
        thread.error.connect(lambda e: print(f"Search error: {e}"))
        
        # נקה
        thread.finished.connect(lambda t=thread: self._cleanup_thread(t))
        thread.error.connect(lambda e, t=thread: self._cleanup_thread(t))
        
        thread.start()
    
    def show_article_details(self, article: Article, likes_count: int, user_liked: bool) -> None:
        """הצג חלון פרטי מאמר"""
        detail_window = ArticleDetailWindow(
            article, 
            likes_count, 
            user_liked, 
            self._view
        )
        detail_window.like_clicked.connect(self._on_like_from_detail)
        detail_window.exec()
    
    def _on_like_from_detail(self, article: Article) -> None:
        """לייק מחלון הפרטים"""
        self._toggle_like(article)
    
    def _toggle_like(self, article: Article) -> None:
        """החלף מצב לייק"""
        print(f"Toggle like for article {article.id}")