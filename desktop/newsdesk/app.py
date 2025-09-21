import sys
from PySide6.QtWidgets import QApplication
from newsdesk.infra.http.news_api_client import NewsApiClient
from newsdesk.infra.http.news_service_http import HttpNewsService
from newsdesk.mvp.view.articles_window import ArticlesWindow
from newsdesk.mvp.presenter.articles_presenter import ArticlesPresenter

def main() -> None:
    app = QApplication(sys.argv)
    view = ArticlesWindow()
    service = HttpNewsService(NewsApiClient("http://127.0.0.1:8000/api/v1"))
    presenter = ArticlesPresenter(view, service)
    presenter.load_initial()
    view.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
