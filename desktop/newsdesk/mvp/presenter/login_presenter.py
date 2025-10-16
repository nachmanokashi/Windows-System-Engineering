# newsdesk/mvp/presenter/login_presenter.py
from PySide6.QtCore import QObject, Signal, Slot, QThread
from newsdesk.mvp.view.login_window import LoginWindow
from newsdesk.infra.http.auth_service_http import HttpAuthService
from newsdesk.infra.http.news_api_client import NewsApiClient
from newsdesk.infra.auth.auth_manager import get_auth_manager
from typing import Callable, Any

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


class LoginPresenter(QObject):
    """Presenter למסך Login"""
    
    login_successful = Signal()
    
    def __init__(self, view: LoginWindow, auth_service: HttpAuthService, api_client: NewsApiClient):
        super().__init__()
        self._view = view
        self._auth_service = auth_service
        self._api_client = api_client
        self._auth_manager = get_auth_manager()
        
        # שמירת threads פעילים
        self._threads = []
        
        # חיבור אירועים
        self._view.login_requested.connect(self.on_login_requested)
        self._view.register_requested.connect(self.on_register_requested)
    
    def __del__(self):
        """Cleanup כשה-Presenter נהרס"""
        self.cleanup()
    
    def cleanup(self):
        """נקה את כל ה-threads"""
        for thread in self._threads[:]:
            try:
                if thread.isRunning():
                    thread.quit()
                    thread.wait(1000)
            except:
                pass
        self._threads.clear()
    
    @Slot(str, str)
    def on_login_requested(self, username: str, password: str):
        """טיפול בבקשת התחברות"""
        thread = WorkerThread(self._auth_service.login, username, password)
        thread.finished.connect(self._on_login_success)
        thread.error.connect(self._on_login_error)
        
        # שמור reference
        self._threads.append(thread)
        thread.finished.connect(lambda: self._cleanup_thread(thread))
        thread.error.connect(lambda: self._cleanup_thread(thread))
        
        thread.start()
    
    def _cleanup_thread(self, thread):
        """נקה thread"""
        try:
            # המתן לסיום ה-thread
            thread.quit()
            thread.wait()
            self._threads.remove(thread)
            thread.deleteLater()
        except (ValueError, RuntimeError):
            pass
    
    @Slot(object)
    def _on_login_success(self, result_obj: object):
        """התחברות הצליחה"""
        result = result_obj
        access_token = result.get("access_token")
        
        if not access_token:
            self._view.show_error("שגיאה: לא התקבל טוקן")
            return
        
        # הגדרת הטוקן
        self._api_client.set_auth_token(access_token)
        self._auth_manager.login(access_token)
        
        # קבלת פרטי המשתמש
        thread = WorkerThread(self._auth_service.get_current_user)
        thread.finished.connect(self._on_user_data_loaded)
        thread.error.connect(self._on_user_data_error)
        
        self._threads.append(thread)
        thread.finished.connect(lambda: self._cleanup_thread(thread))
        thread.error.connect(lambda: self._cleanup_thread(thread))
        
        thread.start()
    
    @Slot(object)
    def _on_user_data_loaded(self, user_obj: object):
        """נתוני המשתמש נטענו"""
        user_data = user_obj
        self._auth_manager.login(self._auth_manager.access_token, user_data)
        
        self._view.show_success("התחברת בהצלחה!")
        
        from PySide6.QtCore import QTimer
        QTimer.singleShot(500, self._complete_login)
    
    def _complete_login(self):
        """השלם התחברות"""
        self._view.close()
        self.login_successful.emit()
    
    @Slot(str)
    def _on_user_data_error(self, error: str):
        """שגיאה בטעינת נתוני משתמש"""
        print(f"Warning: Could not load user data: {error}")
        self._view.show_success("התחברת בהצלחה!")
        
        from PySide6.QtCore import QTimer
        QTimer.singleShot(500, self._complete_login)
    
    @Slot(str)
    def _on_login_error(self, error: str):
        """התחברות נכשלה"""
        if "401" in error or "Unauthorized" in error:
            self._view.show_error("שם משתמש או סיסמה שגויים")
        elif "timeout" in error.lower() or "timed out" in error.lower():
            self._view.show_error("זמן החיבור לשרת פג. נסה שוב.")
        elif "connection" in error.lower():
            self._view.show_error("לא ניתן להתחבר לשרת. בדוק את החיבור לאינטרנט.")
        else:
            self._view.show_error(f"שגיאה בהתחברות: {error}")
    
    @Slot(str, str, str, str)
    def on_register_requested(self, username: str, email: str, password: str, full_name: str):
        """טיפול ברישום משתמש חדש"""
        thread = WorkerThread(
            self._auth_service.register,
            username, email, password, full_name
        )
        
        thread.finished.connect(self._on_register_success)
        thread.error.connect(self._on_register_error)
        
        self._threads.append(thread)
        thread.finished.connect(lambda: self._cleanup_thread(thread))
        thread.error.connect(lambda: self._cleanup_thread(thread))
        
        thread.start()
    
    @Slot(object)
    def _on_register_success(self, result_obj: object):
        """רישום הצליח"""
        from PySide6.QtWidgets import QMessageBox
        
        msg = QMessageBox(self._view)
        msg.setWindowTitle("הרשמה הצליחה")
        msg.setText("המשתמש נוצר בהצלחה!\nכעת ניתן להתחבר עם שם המשתמש והסיסמה.")
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setStyleSheet("""
            QMessageBox {
                background-color: #1a1a2e;
            }
            QMessageBox QLabel {
                color: white;
                min-width: 300px;
            }
            QPushButton {
                background-color: #4a9eff;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 20px;
                min-width: 80px;
            }
        """)
        msg.exec()
    
    @Slot(str)
    def _on_register_error(self, error: str):
        """רישום נכשל"""
        from PySide6.QtWidgets import QMessageBox
        
        msg = QMessageBox(self._view)
        msg.setWindowTitle("שגיאה")
        msg.setIcon(QMessageBox.Icon.Warning)
        
        if "already" in error.lower():
            msg.setText("שם המשתמש או האימייל כבר קיימים במערכת")
        elif "timeout" in error.lower():
            msg.setText("זמן החיבור לשרת פג. נסה שוב.")
        elif "connection" in error.lower():
            msg.setText("לא ניתן להתחבר לשרת. בדוק את החיבור לאינטרנט.")
        else:
            msg.setText(f"לא ניתן ליצור משתמש: {error}")
        
        msg.setStyleSheet("""
            QMessageBox {
                background-color: #1a1a2e;
            }
            QMessageBox QLabel {
                color: white;
                min-width: 300px;
            }
            QPushButton {
                background-color: #4a9eff;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 20px;
                min-width: 80px;
            }
        """)
        msg.exec()