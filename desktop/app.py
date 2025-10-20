import sys
from PySide6.QtWidgets import QApplication

from newsdesk.infra.http.news_api_client import NewsApiClient
from newsdesk.infra.http.auth_service_http import HttpAuthService
from newsdesk.infra.auth.auth_manager import get_auth_manager
from newsdesk.mvp.view.login_window import LoginWindow
from newsdesk.mvp.presenter.login_presenter import LoginPresenter
from newsdesk.mvp.view.main_window_microfrontends import MainWindowMicrofrontends
from newsdesk.components.chat import ChatComponent, ChatPresenter


def main() -> None:
    app = QApplication(sys.argv)
    
    # API Client
    api_client = NewsApiClient("http://127.0.0.1:8000/api/v1")
    auth_manager = get_auth_manager()
    
    # Services
    auth_service = HttpAuthService(api_client)
    
    # משתנים גלובליים
    main_window = None
    login_presenter = None
    
    # === Login Window ===
    login_window = LoginWindow()
    login_presenter = LoginPresenter(login_window, auth_service, api_client)
    
    def on_login_successful():
        """אחרי התחברות מוצלחת"""
        nonlocal main_window
        
        # הגדרת Token
        token = auth_manager.access_token
        user_data = auth_manager.user_data
        
        if token:
            api_client.set_auth_token(token)
        
        # פרטי משתמש
        username = user_data.get("username", "User") if user_data else "User"
        is_admin = user_data.get("is_admin", False) if user_data else False
        
        # יצירת MainWindow עם Microfrontends
        # הרישום של Weather מתבצע אוטומטית בתוך MainWindow!
        main_window = MainWindowMicrofrontends(
            api_client=api_client,
            username=username,
            is_admin=is_admin
        )
        
        # חיבור Logout
        main_window.logout_clicked.connect(on_logout)
        
        # הצג
        main_window.show()
        login_window.hide()
    
    def on_logout():
        """טיפול ביציאה"""
        nonlocal main_window
        
        # נקה
        if main_window:
            main_window.close()
            main_window = None
        
        # נקה Token
        auth_manager.logout()
        api_client.set_auth_token(None)
        
        # חזור ל-Login
        login_window.show()
    
    # חיבור Login Success
    login_presenter.login_successful.connect(on_login_successful)
    
    # הצג Login
    login_window.show()
    
    sys.exit(app.exec())

def __init__(self):
    # ...
    
    # צור את קומפוננטת הצ'אט
    self.chat_component = ChatComponent()
    self.chat_presenter = ChatPresenter(self.api_client)
    self.chat_presenter.set_view(self.chat_component)
    self.chat_component.set_presenter(self.chat_presenter)
    
    # רשום בניהול הקומפוננטות
    self.component_manager.register_component(
        name="chat",
        component=self.chat_component
    )
    
    # חבר כפתור חזרה
    self.chat_component.back_requested.connect(
        lambda: self.navigate_to("articles_list")
    )

if __name__ == "__main__":
    main()