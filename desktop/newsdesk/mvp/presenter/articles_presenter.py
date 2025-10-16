# newsdesk/mvp/presenter/modern_articles_presenter.py
from typing import List, Dict, Any, Callable
from PySide6.QtCore import QObject, Slot, QTimer, QRunnable, Signal, QThreadPool
from newsdesk.mvp.view.articles_window import ArticlesWindow
from newsdesk.mvp.model.article import Article
from newsdesk.infra.http.news_service_http import HttpNewsService

# --- Background Task Runner ---
class _TaskSignals(QObject):
    result = Signal(object)
    error = Signal(str)

class _Task(QRunnable):
    def __init__(self, fn: Callable[..., Any], *args: Any, **kwargs: Any) -> None:
        super().__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = _TaskSignals()
    
    def run(self) -> None:
        try:
            self.signals.result.emit(self.fn(*self.args, **self.kwargs))
        except Exception as ex:
            self.signals.error.emit(str(ex))

def run_in_background(fn: Callable[..., Any], *args: Any, **kwargs: Any) -> _Task:
    t = _Task(fn, *args, **kwargs)
    QThreadPool.globalInstance().start(t)
    return t

# --- Modern Articles Presenter ---
class ArticlesPresenter(QObject):
    def __init__(self, view: ArticlesWindow, service: HttpNewsService) -> None:
        super().__init__()
        self._view = view
        self._service = service
        
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
    
    def load_initial(self) -> None:
        """טעינה ראשונית לכל הטאבים"""
        for cat in self._view.categories:
            task = run_in_background(self._service.top, 20, cat)
            task.signals.result.connect(lambda items, c=cat: self._on_loaded(c, items))
            task.signals.error.connect(lambda e: print(f"Error: {e}"))
    
    @Slot(object)
    def _on_loaded(self, cat: str, items_obj: object) -> None:
        """מאמרים נטענו"""
        items: List[Article] = items_obj  # type: ignore
        
        # TODO: טען גם likes data מהשרת
        likes_data = {}  # {article_id: {"likes_count": 0, "user_liked": False}}
        
        self._view.set_articles(cat, items, likes_data)
    
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
            items: List[Article] = items_obj  # type: ignore
            likes_data = {}
            self._view.set_articles(cat, items, likes_data)
        
        task = run_in_background(self._service.search, q, 20, cat) if q \
               else run_in_background(self._service.top, 20, cat)
        task.signals.result.connect(on_result)
        task.signals.error.connect(lambda e: print(f"Search error: {e}"))