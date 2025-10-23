from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, 
    QPushButton, QWidget, QMessageBox, QGraphicsDropShadowEffect
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QColor

class RegisterDialog(QDialog):
    """דיאלוג רישום מעוצב"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create Account")
        self.setFixedSize(450, 550)  
        self.setModal(True)
        
        # Remove frame for custom design
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self._setup_ui()
        
        # ← NEW: מרכז את החלון במסך
        self._center_on_screen()
    
    def _center_on_screen(self):
        """מרכז את החלון במסך"""
        if self.parent():
            # אם יש parent, מרכז ביחס אליו
            parent_geo = self.parent().geometry()
            x = parent_geo.x() + (parent_geo.width() - self.width()) // 2
            y = parent_geo.y() + (parent_geo.height() - self.height()) // 2
            self.move(x, y)
        else:
            # אחרת, מרכז במסך
            screen = self.screen().geometry()
            x = (screen.width() - self.width()) // 2
            y = (screen.height() - self.height()) // 2
            self.move(x, y)
    
    def _setup_ui(self):
        """בניית הממשק"""
        # Container
        container = QWidget(self)
        container.setGeometry(0, 0, 450, 550)
        container.setStyleSheet("""
            QWidget {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 #1a1a2e,
                    stop:1 #16213e
                );
                border-radius: 25px;
            }
        """)
        
        # Shadow
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setColor(QColor(0, 0, 0, 150))
        shadow.setOffset(0, 8)
        container.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout(container)
        layout.setContentsMargins(40, 30, 40, 30)  
        layout.setSpacing(15)  
        
        # Close button
        close_btn = QPushButton("✕", container)
        close_btn.setGeometry(405, 15, 30, 30)
        close_btn.clicked.connect(self.reject)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #888;
                border: none;
                font-size: 18px;
            }
            QPushButton:hover {
                color: #ff6b6b;
            }
        """)
        
        # Title
        title = QLabel("Create Account")
        title_font = QFont()
        title_font.setPointSize(22) 
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #4a9eff;")
        layout.addWidget(title)
        
        subtitle = QLabel("Join NewsDesk today")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("color: #8892b0; font-size: 12px;") 
        layout.addWidget(subtitle)
        
        layout.addSpacing(5) 
        
        # Input style
        input_style = """
            QLineEdit {
                background-color: rgba(255, 255, 255, 0.05);
                border: 2px solid rgba(74, 158, 255, 0.2);
                border-radius: 12px;
                padding: 12px;
                color: white;
                font-size: 13px;
                min-height: 20px;
            }
            QLineEdit:focus {
                border: 2px solid #4a9eff;
                background-color: rgba(255, 255, 255, 0.08);
            }
            QLineEdit::placeholder {
                color: #8892b0;
            }
        """
        
        # Username
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username (min 3 characters)")
        self.username_input.setStyleSheet(input_style)
        layout.addWidget(self.username_input)
        
        # Email
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Email address")
        self.email_input.setStyleSheet(input_style)
        layout.addWidget(self.email_input)
        
        # Full name
        self.full_name_input = QLineEdit()
        self.full_name_input.setPlaceholderText("Full name (optional)")
        self.full_name_input.setStyleSheet(input_style)
        layout.addWidget(self.full_name_input)
        
        # Password
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password (min 6 characters)")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setStyleSheet(input_style)
        layout.addWidget(self.password_input)
        
        # Confirm password
        self.password_confirm_input = QLineEdit()
        self.password_confirm_input.setPlaceholderText("Confirm password")
        self.password_confirm_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_confirm_input.setStyleSheet(input_style)
        layout.addWidget(self.password_confirm_input)
        
        layout.addSpacing(5)
        
        # Register button
        self.ok_btn = QPushButton("Create Account")
        self.ok_btn.setMinimumHeight(45)  
        self.ok_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.ok_btn.clicked.connect(self._on_ok)
        self.ok_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #4a9eff,
                    stop:1 #00d4ff
                );
                color: white;
                border: none;
                border-radius: 12px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #5ab0ff,
                    stop:1 #20e4ff
                );
            }
        """)
        layout.addWidget(self.ok_btn)
        
        # Cancel button
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setMinimumHeight(40)  
        self.cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.cancel_btn.clicked.connect(self.reject)
        self.cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: 2px solid rgba(74, 158, 255, 0.3);
                border-radius: 12px;
                color: #8892b0;
                font-size: 13px;
            }
            QPushButton:hover {
                border: 2px solid #4a9eff;
                color: #4a9eff;
            }
        """)
        layout.addWidget(self.cancel_btn)
        
        layout.addStretch()
    
    def _on_ok(self):
        """אימות ואישור"""
        username = self.username_input.text().strip()
        email = self.email_input.text().strip()
        password = self.password_input.text()
        password_confirm = self.password_confirm_input.text()
        
        # Validation
        if not username or len(username) < 3:
            self._show_error("Username must be at least 3 characters")
            return
        
        if not email or "@" not in email:
            self._show_error("Please enter a valid email address")
            return
        
        if not password or len(password) < 6:
            self._show_error("Password must be at least 6 characters")
            return
        
        if password != password_confirm:
            self._show_error("Passwords do not match")
            return
        
        self.accept()
    
    def _show_error(self, message: str):
        """הצגת שגיאה"""
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Icon.Warning)
        msg.setWindowTitle("Validation Error")
        msg.setText(message)
        msg.setStyleSheet("""
            QMessageBox {
                background-color: #1a1a2e;
            }
            QMessageBox QLabel {
                color: white;
                min-width: 250px;
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
    
    def get_data(self):
        """קבלת הנתונים"""
        return {
            "username": self.username_input.text().strip(),
            "email": self.email_input.text().strip(),
            "password": self.password_input.text(),
            "full_name": self.full_name_input.text().strip()
        }