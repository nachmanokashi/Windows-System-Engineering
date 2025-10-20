# desktop/newsdesk/components/chat/chat_component.py
"""
Chat Component - ממשק צ'אט עם Gemini AI
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, 
    QLineEdit, QPushButton, QLabel, QScrollArea, QFrame
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont


class ChatBubble(QFrame):
    """בועת צ'אט בודדת"""
    
    def __init__(self, message: str, is_user: bool, parent=None):
        super().__init__(parent)
        self.setup_ui(message, is_user)
    
    def setup_ui(self, message: str, is_user: bool):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        
        # Label עם ההודעה
        label = QLabel(message)
        label.setWordWrap(True)
        label.setTextFormat(Qt.PlainText)
        label.setFont(QFont("Segoe UI", 10))
        
        # עיצוב לפי מי שכתב
        if is_user:
            self.setStyleSheet("""
                QFrame {
                    background-color: #007bff;
                    color: white;
                    border-radius: 15px;
                    padding: 5px;
                }
            """)
            label.setStyleSheet("color: white;")
            label.setAlignment(Qt.AlignRight)
        else:
            self.setStyleSheet("""
                QFrame {
                    background-color: #f1f3f4;
                    color: #202124;
                    border-radius: 15px;
                    padding: 5px;
                }
            """)
            label.setStyleSheet("color: #202124;")
            label.setAlignment(Qt.AlignLeft)
        
        layout.addWidget(label)


class ChatComponent(QWidget):
    """קומפוננטת צ'אט AI"""
    
    back_requested = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._presenter = None
        self._setup_ui()
    
    def _setup_ui(self):
        """בניית הממשק"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Header
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(30, 20, 30, 20)
        
        title = QLabel("🤖 צ'אט AI - Gemini")
        title.setStyleSheet("font-size: 32px; font-weight: bold; color: #1a73e8;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # כפתור איפוס
        clear_btn = QPushButton("🗑️ נקה צ'אט")
        clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #ff9800;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #f57c00; }
        """)
        clear_btn.clicked.connect(self._on_clear_chat)
        header_layout.addWidget(clear_btn)
        
        # כפתור חזרה
        back_btn = QPushButton("← חזרה")
        back_btn.setStyleSheet("""
            QPushButton {
                background-color: #e8e8e8;
                border: none;
                padding: 12px 24px;
                border-radius: 8px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #d0d0d0; }
        """)
        back_btn.clicked.connect(self.back_requested.emit)
        header_layout.addWidget(back_btn)
        
        main_layout.addLayout(header_layout)
        
        # אזור הצ'אט (Scroll Area)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("background-color: white;")
        
        # Widget עם ההודעות
        self.messages_widget = QWidget()
        self.messages_layout = QVBoxLayout(self.messages_widget)
        self.messages_layout.setContentsMargins(30, 20, 30, 20)
        self.messages_layout.setSpacing(15)
        self.messages_layout.addStretch()
        
        scroll.setWidget(self.messages_widget)
        main_layout.addWidget(scroll)
        
        # אזור הקלדה
        input_layout = QHBoxLayout()
        input_layout.setContentsMargins(30, 20, 30, 30)
        input_layout.setSpacing(15)
        
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("הקלד הודעה...")
        self.input_field.setStyleSheet("""
            QLineEdit {
                padding: 15px;
                font-size: 14px;
                border: 2px solid #e0e0e0;
                border-radius: 25px;
                background-color: #f9f9f9;
                color: #000000; /* ✅ תיקון: צבע המלל המוקלד מוגדר לשחור */
            }
            QLineEdit:focus {
                border: 2px solid #1a73e8;
                background-color: white;
                color: #000000; /* ✅ תיקון: צבע המלל במצב פוקוס מוגדר לשחור */
            }
        """)
        self.input_field.returnPressed.connect(self._on_send_message)
        input_layout.addWidget(self.input_field)
        
        self.send_btn = QPushButton("שלח 📤")
        self.send_btn.setStyleSheet("""
            QPushButton {
                background-color: #1a73e8;
                color: white;
                border: none;
                padding: 15px 30px;
                border-radius: 25px;
                font-size: 14px;
                font-weight: bold;
                min-width: 100px;
            }
            QPushButton:hover { background-color: #1557b0; }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)
        self.send_btn.clicked.connect(self._on_send_message)
        input_layout.addWidget(self.send_btn)
        
        main_layout.addLayout(input_layout)
    
    def add_message(self, message: str, is_user: bool):
        """הוסף הודעה לצ'אט"""
        # הסר את ה-stretch האחרון
        count = self.messages_layout.count()
        if count > 0:
            item = self.messages_layout.itemAt(count - 1)
            if item.spacerItem():
                self.messages_layout.removeItem(item)
        
        # צור בועת צ'אט
        bubble = ChatBubble(message, is_user)
        
        # Layout לבועה (לצד הנכון)
        bubble_layout = QHBoxLayout()
        if is_user:
            bubble_layout.addStretch()
            bubble_layout.addWidget(bubble, 0, Qt.AlignRight)
        else:
            bubble_layout.addWidget(bubble, 0, Qt.AlignLeft)
            bubble_layout.addStretch()
        
        self.messages_layout.addLayout(bubble_layout)
        
        # הוסף stretch חדש
        self.messages_layout.addStretch()
        
        # גלול למטה
        self.messages_widget.updateGeometry()
    
    def clear_chat(self):
        """נקה את כל ההודעות"""
        while self.messages_layout.count():
            item = self.messages_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                while item.layout().count():
                    sub_item = item.layout().takeAt(0)
                    if sub_item.widget():
                        sub_item.widget().deleteLater()
        
        self.messages_layout.addStretch()
    
    def _on_send_message(self):
        """כשלוחצים שלח"""
        message = self.input_field.text().strip()
        if not message:
            return
        
        # הוסף הודעת משתמש
        self.add_message(message, is_user=True)
        self.input_field.clear()
        self.send_btn.setEnabled(False)
        
        # שלח ל-Presenter
        if self._presenter:
            self._presenter.send_message(message)
    
    def _on_clear_chat(self):
        """נקה צ'אט"""
        self.clear_chat()
        if self._presenter:
            self._presenter.clear_chat()
    
    def show_ai_response(self, response: str):
        """הצג תשובה מה-AI"""
        self.add_message(response, is_user=False)
        self.send_btn.setEnabled(True)
    
    def show_error(self, error: str):
        """הצג שגיאה"""
        self.add_message(f"❌ שגיאה: {error}", is_user=False)
        self.send_btn.setEnabled(True)
    
    def set_presenter(self, presenter):
        """קבע Presenter"""
        self._presenter = presenter
    
    def on_mount(self):
        """נקרא כשהקומפוננטה נטענת"""
        print("✅ ChatComponent mounted")
        # הודעת פתיחה
        self.add_message("שלום! אני Gemini AI. במה אוכל לעזור לך היום?", is_user=False)
    
    def on_unmount(self):
        """נקרא כשהקומפוננטה מוסרת"""
        print("❌ ChatComponent unmounted")