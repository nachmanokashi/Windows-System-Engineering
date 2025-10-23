from __future__ import annotations
from typing import Any, Callable, Optional
import traceback

from PySide6.QtCore import QObject, Signal, QRunnable, QThreadPool, Qt, QTimer


class _WorkerSignals(QObject):
    """סיגנלים פנימיים לעבודה אסינכרונית."""
    finished = Signal(object)   
    error = Signal(str)          


class _Worker(QRunnable):
    """
    Runnable כללי שמריץ פונקציה ברקע ושולח סיגנלים עם תוצאה/שגיאה.
    """
    def __init__(self, fn: Callable[..., Any], *args: Any, **kwargs: Any) -> None:
        super().__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = _WorkerSignals()
        self.setAutoDelete(True)

    def run(self) -> None:
        try:
            result = self.fn(*self.args, **self.kwargs)
            self.signals.finished.emit(result)
        except Exception as e:
            tb = traceback.format_exc()
            self.signals.error.emit(f"{e}\n{tb}")


class BasePresenter(QObject):
    """
    בסיס לכל Presenter.
    - שומר רפרנס ל-View
    - מנהל ThreadPool משותף
    - מספק _start_worker() להרצת פונקציות ברקע והתחברות לקולבקים
    """
    def __init__(self, view: QObject) -> None:
        super().__init__(parent=view if isinstance(view, QObject) else None)
        self.view = view
        self._thread_pool = QThreadPool.globalInstance()

    # ---------------------------
    # Public helpers
    # ---------------------------
    def run_on_ui(self, fn: Callable[[], None], delay_ms: int = 0) -> None:
        """
        הרצת callable על ה-UI thread (אופציונלית עם דיליי קצר).
        """
        QTimer.singleShot(delay_ms, fn)

    def _start_worker(
        self,
        fn: Callable[..., Any],
        *args: Any,
        finished_slot: Optional[Callable[[Any], None]] = None,
        error_slot: Optional[Callable[[str], None]] = None,
        **kwargs: Any,
    ) -> None:
        """
        הרצת פונקציה ברקע עם תמיכה ב-callbacks:
        - finished_slot(result)
        - error_slot(error_message)
        
        שימוש:
            self._start_worker(
                service.call_api,
                param1=...,
                finished_slot=on_success,
                error_slot=on_error
            )
        """
        worker = _Worker(fn, *args, **kwargs)

        if finished_slot is not None:
            worker.signals.finished.connect(finished_slot, Qt.QueuedConnection)

        if error_slot is not None:
            worker.signals.error.connect(error_slot, Qt.QueuedConnection)

        self._thread_pool.start(worker)

    def dispose(self) -> None:
        pass
