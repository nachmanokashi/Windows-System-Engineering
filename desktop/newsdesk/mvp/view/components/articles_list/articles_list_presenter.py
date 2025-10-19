# client/newsdesk/mvp/view/components/articles_list/articles_list_presenter.py
"""
ArticlesListPresenter - הלוגיקה של ArticlesListComponent
"""
from PySide6.QtCore import QObject, QThread, Signal
from typing import TYPE_CHECKING, Optional, List, Dict, Any

if TYPE_CHECKING:
    from newsdesk.mvp.view.components.articles_list.articles_list_view import ArticlesListComponent

from newsdesk.infra.http.news_service_http import HttpNewsService


class WorkerThread(QThread):
    """Thread עבודה לפעולות ברקע"""
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


class ArticlesListPresenter(QObject):
    """
    Presenter של ArticlesListComponent
    
    אחראי על:
    - טעינת מאמרים מהשרת
    - חיפוש
    - פילטר לפי קטגוריה
    - טיפול בשגיאות
    """
    
    def __init__(self, view: 'ArticlesListComponent', news_service: HttpNewsService):
        super().__init__()
        self.view = view
        self.news_service = news_service
        
        # State
        self.current_page = 1
        self.page_size = 20
        self.current_category: Optional[str] = None
        self.current_search_query: Optional[str] = None
        
        # Threads
        self.threads: List[QThread] = []
    
    def load_articles(self, page: int = 1) -> None:
        """
        טעינת מאמרים מהשרת
        
        Args:
            page: מספר עמוד
        """
        self.current_page = page
        self.view.show_loading("Loading articles...")
        
        # יצירת thread
        thread = WorkerThread(
            self.news_service.list_articles,
            page=page,
            page_size=self.page_size,
            category=self.current_category
        )
        
        thread.finished.connect(self._on_articles_loaded)
        thread.error.connect(self._on_load_error)
        thread.finished.connect(lambda: self._cleanup_thread(thread))
        thread.error.connect(lambda: self._cleanup_thread(thread))
        
        self.threads.append(thread)
        thread.start()
    
    def search_articles(self, query: str) -> None:
        """
        חיפוש מאמרים
        
        Args:
            query: טקסט החיפוש
        """
        if not query or len(query) < 2:
            # אם החיפוש ריק, טען את כל המאמרים
            self.current_search_query = None
            self.load_articles()
            return
        
        self.current_search_query = query
        self.view.show_loading(f"Searching for '{query}'...")
        
        # יצירת thread
        thread = WorkerThread(
            self.news_service.search_articles,
            query=query,
            category=self.current_category
        )
        
        thread.finished.connect(self._on_search_results)
        thread.error.connect(self._on_load_error)
        thread.finished.connect(lambda: self._cleanup_thread(thread))
        thread.error.connect(lambda: self._cleanup_thread(thread))
        
        self.threads.append(thread)
        thread.start()
    
    def filter_by_category(self, category: Optional[str]) -> None:
        """
        פילטר לפי קטגוריה
        
        Args:
            category: שם הקטגוריה או None לכל הקטגוריות
        """
        self.current_category = category if category else None
        
        # אם יש חיפוש פעיל, חפש עם הקטגוריה החדשה
        if self.current_search_query:
            self.search_articles(self.current_search_query)
        else:
            self.load_articles(page=1)
    
    def load_categories(self) -> None:
        """טעינת רשימת קטגוריות"""
        thread = WorkerThread(self.news_service.get_categories)
        
        thread.finished.connect(self._on_categories_loaded)
        thread.error.connect(lambda err: print(f"Failed to load categories: {err}"))
        thread.finished.connect(lambda: self._cleanup_thread(thread))
        thread.error.connect(lambda: self._cleanup_thread(thread))
        
        self.threads.append(thread)
        thread.start()
    
    # ============================================
    # Callbacks
    # ============================================
    
    def _on_articles_loaded(self, response: Dict[str, Any]) -> None:
        """נקרא כאשר המאמרים נטענו"""
        self.view.hide_loading()
        
        articles = response.get("items", [])
        total = response.get("total", 0)
        
        self.view.display_articles(articles)
        self.view.update_status(f"Loaded {len(articles)} of {total} articles")
    
    def _on_search_results(self, response: Dict[str, Any]) -> None:
        """נקרא כאשר תוצאות החיפוש חזרו"""
        self.view.hide_loading()
        
        articles = response.get("items", [])
        
        self.view.display_articles(articles)
        self.view.update_status(f"Found {len(articles)} articles matching '{self.current_search_query}'")
    
    def _on_categories_loaded(self, response: Dict[str, Any]) -> None:
        """נקרא כאשר הקטגוריות נטענו"""
        categories = response.get("items", [])
        self.view.display_categories(categories)
    
    def _on_load_error(self, error: str) -> None:
        """נקרא כאשר יש שגיאה"""
        self.view.hide_loading()
        self.view.show_error(f"Failed to load articles: {error}")
        self.view.update_status("Error loading articles")
    
    def _cleanup_thread(self, thread: QThread) -> None:
        """ניקוי thread"""
        try:
            if thread in self.threads:
                self.threads.remove(thread)
            thread.quit()
            thread.wait()
        except:
            pass
    
    def cleanup(self) -> None:
        """ניקוי כל ה-threads"""
        for thread in self.threads[:]:
            try:
                thread.quit()
                thread.wait(1000)
            except:
                pass
        self.threads.clear()