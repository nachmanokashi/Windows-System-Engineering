# newsdesk/mvp/view/login_window.py
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QMessageBox, QWidget
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

class LoginWindow(QDialog):
    """מסך התחברות"""
    
    login_requested = Signal(str, str)  # username, password
    register_requested = Signal(str, str, str, str)  # username, email, password, full_name
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("NewsDesk - Login")
        self.setFixedSize(400, 300)
        self.setModal(True)
        
        self._setup_ui()
    
    def _setup_ui(self):
        """בניית הממשק"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(40, 40, 40, 40)
        
        # כותרת
        title = QLabel("NewsDesk")
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        subtitle = QLabel("התחברות למערכת")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle)
        
        layout.addSpacing(20)
        
        # שדות קלט
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("שם משתמש")
        self.username_input.setMinimumHeight(35)
        layout.addWidget(self.username_input)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("סיסמה")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setMinimumHeight(35)
        self.password_input.returnPressed.connect(self._on_login_clicked)
        layout.addWidget(self.password_input)
        
        # כפתורים
        self.login_btn = QPushButton("כניסה")
        self.login_btn.setMinimumHeight(40)
        self.login_btn.setDefault(True)
        self.login_btn.clicked.connect(self._on_login_clicked)
        layout.addWidget(self.login_btn)
        
        self.register_btn = QPushButton("אין לך חשבון? הירשם כאן")
        self.register_btn.setFlat(True)
        self.register_btn.clicked.connect(self._on_register_clicked)
        layout.addWidget(self.register_btn)
        
        layout.addStretch()
        
        # Status
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("color: red;")
        layout.addWidget(self.status_label)
    
    def _on_login_clicked(self):
        """טיפול בלחיצה על כפתור התחברות"""
        username = self.username_input.text().strip()
        password = self.password_input.text()
        
        if not username or not password:
            self.show_error("נא למלא שם משתמש וסיסמה")
            return
        
        self.set_loading(True)
        self.login_requested.emit(username, password)
    
    def _on_register_clicked(self):
        """פתיחת חלון רישום"""
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
        self.set_loading(False)
    
    def show_success(self, message: str):
        """הצגת הצלחה"""
        self.status_label.setStyleSheet("color: green;")
        self.status_label.setText(message)
    
    def set_loading(self, loading: bool):
        """מצב טעינה"""
        self.login_btn.setEnabled(not loading)
        self.register_btn.setEnabled(not loading)
        self.username_input.setEnabled(not loading)
        self.password_input.setEnabled(not loading)
        
        if loading:
            self.login_btn.setText("מתחבר...")
            self.status_label.setText("")
        else:
            self.login_btn.setText("כניסה")
    
    def clear(self):
        """ניקוי השדות"""
        self.username_input.clear()
        self.password_input.clear()
        self.status_label.clear()


class RegisterDialog(QDialog):
    """דיאלוג רישום משתמש חדש"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("רישום משתמש חדש")
        self.setFixedSize(400, 350)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # שדות
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("שם משתמש (לפחות 3 תווים)")
        
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("אימייל")
        
        self.full_name_input = QLineEdit()
        self.full_name_input.setPlaceholderText("שם מלא (אופציונלי)")
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("סיסמה (לפחות 6 תווים)")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        
        self.password_confirm_input = QLineEdit()
        self.password_confirm_input.setPlaceholderText("אימות סיסמה")
        self.password_confirm_input.setEchoMode(QLineEdit.EchoMode.Password)
        
        layout.addWidget(QLabel("שם משתמש:"))
        layout.addWidget(self.username_input)
        layout.addWidget(QLabel("אימייל:"))
        layout.addWidget(self.email_input)
        layout.addWidget(QLabel("שם מלא:"))
        layout.addWidget(self.full_name_input)
        layout.addWidget(QLabel("סיסמה:"))
        layout.addWidget(self.password_input)
        layout.addWidget(QLabel("אימות סיסמה:"))
        layout.addWidget(self.password_confirm_input)
        
        # כפתורים
        btn_layout = QHBoxLayout()
        self.ok_btn = QPushButton("הירשם")
        self.cancel_btn = QPushButton("ביטול")
        
        self.ok_btn.clicked.connect(self._on_ok)
        self.cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(self.cancel_btn)
        btn_layout.addWidget(self.ok_btn)
        layout.addLayout(btn_layout)
    
    def _on_ok(self):
        """אימות ואישור"""
        username = self.username_input.text().strip()
        email = self.email_input.text().strip()
        password = self.password_input.text()
        password_confirm = self.password_confirm_input.text()
        
        # Validation
        if not username or len(username) < 3:
            QMessageBox.warning(self, "שגיאה", "שם משתמש חייב להיות לפחות 3 תווים")
            return
        
        if not email or "@" not in email:
            QMessageBox.warning(self, "שגיאה", "נא להזין כתובת אימייל תקינה")
            return
        
        if not password or len(password) < 6:
            QMessageBox.warning(self, "שגיאה", "סיסמה חייבת להיות לפחות 6 תווים")
            return
        
        if password != password_confirm:
            QMessageBox.warning(self, "שגיאה", "הסיסמאות לא תואמות")
            return
        
        self.accept()
    
    def get_data(self):
        """קבלת הנתונים"""
        return {
            "username": self.username_input.text().strip(),
            "email": self.email_input.text().strip(),
            "password": self.password_input.text(),
            "full_name": self.full_name_input.text().strip()
        }