from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QWidget, QGraphicsDropShadowEffect
)
from PySide6.QtCore import Qt, Signal, QPropertyAnimation, QEasingCurve, QRect
from PySide6.QtGui import QFont, QLinearGradient, QColor, QPainter, QPalette

class AnimatedButton(QPushButton):
    """כפתור עם אנימציה"""
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setMinimumHeight(45)  # ← הקטנתי מ-50
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        # Shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(74, 158, 255, 100))
        shadow.setOffset(0, 5)
        self.setGraphicsEffect(shadow)

class LoginWindow(QDialog):
    """מסך התחברות מהמם"""
    
    login_requested = Signal(str, str)
    register_requested = Signal(str, str, str, str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("NewsDesk - Welcome")
        self.setFixedSize(450, 600)  # ← הקטנתי מ-500x700 ל-450x600
        self.setModal(True)
        
        # Remove window frame for custom design
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self._setup_ui()
        self._center_on_screen()
    
    def _center_on_screen(self):
        """מרכז את החלון במסך"""
        screen = self.screen().geometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)
    
    def _setup_ui(self):
        """בניית הממשק"""
        # Main container
        container = QWidget(self)
        container.setGeometry(0, 0, 450, 600)
        container.setStyleSheet("""
            QWidget {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 #1a1a2e,
                    stop:0.5 #16213e,
                    stop:1 #0f3460
                );
                border-radius: 30px;
            }
        """)
        
        # Add shadow to container
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(40)
        shadow.setColor(QColor(0, 0, 0, 160))
        shadow.setOffset(0, 10)
        container.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout(container)
        layout.setContentsMargins(40, 50, 40, 50)  # ← הקטנתי margins
        layout.setSpacing(20)  # ← הקטנתי מ-25
        
        # Close button
        close_btn = QPushButton("✕", container)
        close_btn.setGeometry(400, 20, 30, 30)
        close_btn.clicked.connect(self.close)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #888;
                border: none;
                font-size: 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                color: #ff6b6b;
            }
        """)
        
        # Logo/Icon
        logo_container = QWidget()
        logo_layout = QVBoxLayout(logo_container)
        logo_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        logo = QLabel("📰")
        logo_font = QFont()
        logo_font.setPointSize(50)  # ← הקטנתי מ-60
        logo.setFont(logo_font)
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_layout.addWidget(logo)
        
        layout.addWidget(logo_container)
        
        # Title
        title = QLabel("NewsDesk")
        title_font = QFont()
        title_font.setPointSize(28)  # ← הקטנתי מ-32
        title_font.setBold(True)
        title_font.setFamily("Segoe UI")
        title.setFont(title_font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("""
            QLabel {
                color: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #4a9eff,
                    stop:1 #00d4ff
                );
            }
        """)
        layout.addWidget(title)
        
        subtitle = QLabel("Your Daily News Companion")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("""
            QLabel {
                color: #8892b0;
                font-size: 13px;
                letter-spacing: 2px;
            }
        """)
        layout.addWidget(subtitle)
        
        layout.addSpacing(15)  # ← הקטנתי מ-20
        
        # Username input
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")
        self.username_input.setMinimumHeight(50)  # ← הקטנתי מ-55
        self.username_input.setStyleSheet("""
            QLineEdit {
                background-color: rgba(255, 255, 255, 0.05);
                border: 2px solid rgba(74, 158, 255, 0.2);
                border-radius: 15px;
                padding: 0 20px;
                color: white;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 2px solid #4a9eff;
                background-color: rgba(255, 255, 255, 0.08);
            }
            QLineEdit::placeholder {
                color: #8892b0;
            }
        """)
        layout.addWidget(self.username_input)
        
        # Password input
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setMinimumHeight(50)
        self.password_input.returnPressed.connect(self._on_login_clicked)
        self.password_input.setStyleSheet("""
            QLineEdit {
                background-color: rgba(255, 255, 255, 0.05);
                border: 2px solid rgba(74, 158, 255, 0.2);
                border-radius: 15px;
                padding: 0 20px;
                color: white;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 2px solid #4a9eff;
                background-color: rgba(255, 255, 255, 0.08);
            }
            QLineEdit::placeholder {
                color: #8892b0;
            }
        """)
        layout.addWidget(self.password_input)
        
        # Login button
        self.login_btn = AnimatedButton("Login")
        self.login_btn.clicked.connect(self._on_login_clicked)
        self.login_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #4a9eff,
                    stop:1 #00d4ff
                );
                color: white;
                border: none;
                border-radius: 15px;
                font-size: 15px;
                font-weight: bold;
                letter-spacing: 1px;
            }
            QPushButton:hover {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #5ab0ff,
                    stop:1 #20e4ff
                );
            }
            QPushButton:pressed {
                padding-top: 3px;
            }
        """)
        layout.addWidget(self.login_btn)
        
        # Divider
        divider_layout = QHBoxLayout()
        line1 = QLabel()
        line1.setFixedHeight(1)
        line1.setStyleSheet("background-color: rgba(136, 146, 176, 0.3);")
        divider_layout.addWidget(line1)
        
        or_label = QLabel("or")
        or_label.setStyleSheet("color: #8892b0; padding: 0 15px;")
        divider_layout.addWidget(or_label)
        
        line2 = QLabel()
        line2.setFixedHeight(1)
        line2.setStyleSheet("background-color: rgba(136, 146, 176, 0.3);")
        divider_layout.addWidget(line2)
        
        layout.addLayout(divider_layout)
        
        # Register button
        self.register_btn = QPushButton("Create Account")
        self.register_btn.setMinimumHeight(45)
        self.register_btn.clicked.connect(self._on_register_clicked)
        self.register_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.register_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: 2px solid rgba(74, 158, 255, 0.5);
                border-radius: 15px;
                color: #4a9eff;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                border: 2px solid #4a9eff;
                background-color: rgba(74, 158, 255, 0.1);
            }
        """)
        layout.addWidget(self.register_btn)
        
        layout.addStretch()
        
        # Status label
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setWordWrap(True)
        self.status_label.setStyleSheet("""
            QLabel {
                color: #ff6b6b;
                font-size: 12px;
                padding: 10px;
                background-color: rgba(255, 107, 107, 0.1);
                border-radius: 8px;
            }
        """)
        self.status_label.hide()
        layout.addWidget(self.status_label)
    
    def _on_login_clicked(self):
        """טיפול בלחיצה על כפתור התחברות"""
        username = self.username_input.text().strip()
        password = self.password_input.text()
        
        if not username or not password:
            self.show_error("Please enter username and password")
            return
        
        self.set_loading(True)
        self.login_requested.emit(username, password)
    
    def _on_register_clicked(self):
        """פתיחת חלון רישום"""
        from newsdesk.mvp.view.register_dialog import RegisterDialog
        dialog = RegisterDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            self.register_requested.emit(
                data["username"],
                data["email"],
                data["password"],
                data["full_name"]
            )
    
    def show_error(self, message: str):
        """הצגת שגיאה"""
        self.status_label.setText(message)
        self.status_label.show()
        self.set_loading(False)
    
    def show_success(self, message: str):
        """הצגת הצלחה"""
        self.status_label.setStyleSheet("""
            QLabel {
                color: #51cf66;
                font-size: 12px;
                padding: 10px;
                background-color: rgba(81, 207, 102, 0.1);
                border-radius: 8px;
            }
        """)
        self.status_label.setText(message)
        self.status_label.show()
    
    def set_loading(self, loading: bool):
        """מצב טעינה"""
        self.login_btn.setEnabled(not loading)
        self.register_btn.setEnabled(not loading)
        self.username_input.setEnabled(not loading)
        self.password_input.setEnabled(not loading)
        
        if loading:
            self.login_btn.setText("Logging in...")
            self.status_label.hide()
        else:
            self.login_btn.setText("Login")
    
    def clear(self):
        """ניקוי השדות"""
        self.username_input.clear()
        self.password_input.clear()
        self.status_label.clear()
        self.status_label.hide()