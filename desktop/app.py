# app.py - נקודת כניסה עם Login
import sys
from PySide6.QtWidgets import QApplication
from newsdesk.infra.http.news_api_client import NewsApiClient
from newsdesk.infra.http.news_service_http import HttpNewsService
from newsdesk.infra.http.auth_service_http import HttpAuthService
from newsdesk.infra.auth.auth_manager import get_auth_manager
from newsdesk.mvp.view.articles_window import ArticlesWindow
from newsdesk.mvp.view.login_window import LoginWindow
from newsdesk.mvp.presenter.articles_presenter import ArticlesPresenter
from newsdesk.mvp.presenter.login_presenter import LoginPresenter

def main() -> None:
    app = QApplication(sys.argv)
    
    # יצירת API Client
    api_client = NewsApiClient("http://127.0.0.1:8000/api/v1")
    auth_manager = get_auth_manager()
    
    # יצירת Services
    auth_service = HttpAuthService(api_client)
    news_service = HttpNewsService(api_client)
    
    # משתנים גלובליים
    articles_window = None
    articles_presenter = None
    login_presenter = None
    
    # יצירת חלון Login
    login_window = LoginWindow()
    login_presenter = LoginPresenter(login_window, auth_service, api_client)
    
    def on_login_successful():
        """אחרי התחברות מוצלחת"""
        nonlocal articles_window, articles_presenter
        
        # הגדרת הטוקן ב-API Client
        token = auth_manager.access_token
        user_data = auth_manager.user_data
        
        if token:
            api_client.set_auth_token(token)
        
        # קבל פרטי משתמש
        username = user_data.get("username", "User") if user_data else "User"
        is_admin = user_data.get("is_admin", False) if user_data else False
        
        # צור חלון מאמרים
        articles_window = ArticlesWindow(is_admin=is_admin, username=username)
        articles_presenter = ArticlesPresenter(articles_window, news_service, api_client)
        
        # חיבור logout
        articles_window.logout_clicked.connect(on_logout)
        
        # טעינה והצגה
        articles_presenter.load_initial()
        articles_window.show()
        
    def on_logout():
        """טיפול ביציאה"""
        nonlocal articles_window, articles_presenter
        
        # נקה threads פעילים
        if articles_presenter:
            cleanup_presenter(articles_presenter)
        
        # נקה טוקן
        auth_manager.logout()
        api_client.clear_auth_token()
        
        # סגור חלון מאמרים
        if articles_window:
            articles_window.close()
            articles_window = None
            articles_presenter = None
        
        # הצג מחדש את Login
        login_window.clear()
        login_window.show()
    
    def cleanup_presenter(presenter):
        """נקה את כל ה-threads של presenter"""
        if hasattr(presenter, '_threads'):
            for thread in presenter._threads[:]:  # copy list
                try:
                    if thread.isRunning():
                        thread.quit()
                        thread.wait(1000)  # המתן עד שנייה
                except:
                    pass
    
    def on_app_quit():
        """נקה לפני סגירת האפליקציה"""
        if articles_presenter:
            cleanup_presenter(articles_presenter)
        if login_presenter:
            cleanup_presenter(login_presenter)
    
    # חיבור האירועים
    login_presenter.login_successful.connect(on_login_successful)
    app.aboutToQuit.connect(on_app_quit)
    
    # הצגת חלון Login
    login_window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()