from typing import List, Tuple, Any, Callable, Dict
from PySide6.QtCore import QObject, Slot, QTimer, QRunnable, Signal, QThreadPool
from PySide6.QtWidgets import QListWidgetItem, QMessageBox
from newsdesk.mvp.view.articles_window import ArticlesWindow
from newsdesk.mvp.model.article import Article
from newsdesk.infra.http.news_service_http import HttpNewsService

# --- Runner קטן לעבודה ברקע (מוטמע כאן כדי לצמצם קבצים) ---

class _TaskSignals(QObject):
    result = Signal(object)
    error = Signal(str)

class _Task(QRunnable):
    def __init__(self, fn: Callable[..., Any], *args: Any, **kwargs: Any) -> None:
        super().__init__(); self.fn=fn; self.args=args; self.kwargs=kwargs; self.signals=_TaskSignals()
    def run(self) -> None:
        try: self.signals.result.emit(self.fn(*self.args, **self.kwargs))
        except Exception as ex: self.signals.error.emit(str(ex))

def run_in_background(fn: Callable[..., Any], *args: Any, **kwargs: Any) -> _Task:
    t=_Task(fn,*args,**kwargs); QThreadPool.globalInstance().start(t); return t

# --- Presenter ---

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
            timer = QTimer(self); timer.setSingleShot(True); timer.setInterval(250)
            timer.timeout.connect(lambda c=cat: self._do_search(c))
            self._debounce[cat] = timer
            self._token[cat] = 0

            self._view.search_box(cat).textChanged.connect(lambda _t, c=cat: self.on_search_changed(c))
            self._view.list_widget(cat).itemActivated.connect(self.on_item_activated)

    # טעינה ראשונית לכל הטאבים (ברקע)
    def load_initial(self) -> None:
        for cat in self._view.categories:
            self._view.set_status(cat, "טוען...")
            task = run_in_background(self._service.top, 20, cat)
            task.signals.result.connect(lambda items, c=cat: self._on_loaded(c, items))
            task.signals.error.connect(self._view.show_error)

    @staticmethod
    def _rows(items: List[Article]) -> List[Tuple[str, Article]]:
        return [(f"{a.title}  •  {a.source}", a) for a in items]

    @Slot(object)
    def _on_loaded(self, cat: str, items_obj: object) -> None:
        items: List[Article] = items_obj  # type: ignore[assignment]
        self._view.set_items(cat, self._rows(items))
        self._view.set_status(cat, f"{len(items)} כתבות")

    # --- חיפוש פר־טאב ---
    @Slot()
    def on_search_changed(self, cat: str) -> None:
        self._debounce[cat].start()

    def _do_search(self, cat: str) -> None:
        q = self._view.search_box(cat).text().strip()
        self._token[cat] += 1; my_token = self._token[cat]
        self._view.set_status(cat, "מחפש...")

        def on_result(items_obj: object) -> None:
            if my_token != self._token[cat]: return
            items: List[Article] = items_obj  # type: ignore[assignment]
            self._view.set_items(cat, self._rows(items))
            self._view.set_status(cat, f"{len(items)} כתבות")

        task = run_in_background(self._service.search, q, 20, cat) if q \
               else run_in_background(self._service.top, 20, cat)
        task.signals.result.connect(on_result)
        task.signals.error.connect(self._view.show_error)

    # --- פרטי כתבה ---
    @Slot(QListWidgetItem)
    def on_item_activated(self, item: QListWidgetItem) -> None:
        a = self._view.item_to_article(item)
        if not a: return
        QMessageBox.information(self._view, "Article Details", f"{a.title}\n\n{a.source}\n\n{a.summary}")
