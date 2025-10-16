# newsdesk/mvp/presenter/login_presenter.py
from PySide6.QtCore import QObject, Signal, Slot
from newsdesk.mvp.view.login_window import LoginWindow
from newsdesk.infra.http.auth_service_http import HttpAuthService
from newsdesk.infra.http.news_api_client import NewsApiClient
from newsdesk.infra.auth.auth_manager import get_auth_manager
from typing import Callable, Any
from PySide6.QtCore import QRunnable, QThreadPool

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


class LoginPresenter(QObject):
    """Presenter למסך Login"""
    
    login_successful = Signal()  # נשלח כשההתחברות מצליחה
    
    def __init__(self, view: LoginWindow, auth_service: HttpAuthService, api_client: NewsApiClient):
        super().__init__()
        self._view = view
        self._auth_service = auth_service
        self._api_client = api_client  # ← NEW: שמירת ה-API Client
        self._auth_manager = get_auth_manager()
        
        # חיבור אירועים
        self._view.login_requested.connect(self.on_login_requested)
        self._view.register_requested.connect(self.on_register_requested)
    
    @Slot(str, str)
    def on_login_requested(self, username: str, password: str):
        """טיפול בבקשת התחברות"""
        task = run_in_background(self._auth_service.login, username, password)
        task.signals.result.connect(self._on_login_success)
        task.signals.error.connect(self._on_login_error)
    
    @Slot(object)
    def _on_login_success(self, result_obj: object):
        """התחברות הצליחה"""
        result = result_obj  # type: ignore
        access_token = result.get("access_token")
        
        if not access_token:
            self._view.show_error("שגיאה: לא התקבל טוקן")
            return
        
        # ← FIX: הגדרת הטוקן ב-API Client לפני קריאה ל-/auth/me
        self._api_client.set_auth_token(access_token)
        
        # שמירת הטוקן ב-AuthManager
        self._auth_manager.login(access_token)
        
        # קבלת פרטי המשתמש (עכשיו עם הטוקן!)
        task = run_in_background(self._auth_service.get_current_user)
        task.signals.result.connect(self._on_user_data_loaded)
        task.signals.error.connect(self._on_user_data_error)
    
    @Slot(object)
    def _on_user_data_loaded(self, user_obj: object):
        """נתוני המשתמש נטענו"""
        user_data = user_obj  # type: ignore
        self._auth_manager.login(self._auth_manager.access_token, user_data)
        
        self._view.show_success("התחברת בהצלחה!")
        self._view.close()
        self.login_successful.emit()
    
    @Slot(str)
    def _on_user_data_error(self, error: str):
        """שגיאה בטעינת נתוני משתמש - לא קריטי"""
        print(f"Warning: Could not load user data: {error}")
        # ממשיכים גם בלי נתוני המשתמש
        self._view.show_success("התחברת בהצלחה!")
        self._view.close()
        self.login_successful.emit()
    
    @Slot(str)
    def _on_login_error(self, error: str):
        """התחברות נכשלה"""
        if "401" in error or "Unauthorized" in error:
            self._view.show_error("שם משתמש או סיסמה שגויים")
        else:
            self._view.show_error(f"שגיאה בהתחברות: {error}")
    
    @Slot(str, str, str, str)
    def on_register_requested(self, username: str, email: str, password: str, full_name: str):
        """טיפול ברישום משתמש חדש"""
        task = run_in_background(
            self._auth_service.register,
            username, email, password, full_name
        )
        task.signals.result.connect(self._on_register_success)
        task.signals.error.connect(self._on_register_error)
    
    @Slot(object)
    def _on_register_success(self, result_obj: object):
        """רישום הצליח"""
        from PySide6.QtWidgets import QMessageBox
        QMessageBox.information(
            self._view,
            "הרשמה הצליחה",
            "המשתמש נוצר בהצלחה!\nכעת ניתן להתחבר עם שם המשתמש והסיסמה."
        )
    
    @Slot(str)
    def _on_register_error(self, error: str):
        """רישום נכשל"""
        from PySide6.QtWidgets import QMessageBox
        if "already" in error.lower():
            QMessageBox.warning(
                self._view,
                "שגיאה",
                "שם המשתמש או האימייל כבר קיימים במערכת"
            )
        else:
            QMessageBox.warning(
                self._view,
                "שגיאה ברישום",
                f"לא ניתן ליצור משתמש: {error}"
            )