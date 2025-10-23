from PySide6.QtWidgets import QWidget, QVBoxLayout
from abc import ABC, abstractmethod, ABCMeta
from typing import Optional, Any, Dict


class QWidgetABCMeta(type(QWidget), ABCMeta):
    pass

class BaseComponent(QWidget, ABC, metaclass=QWidgetABCMeta):
    """
    מחלקת בסיס לכל ה-Components
    
    כל component צריך לממש:
    - setup_ui() - בניית הממשק
    - on_mount() - מה לעשות כשה-component נטען
    - on_unmount() - מה לעשות כשה-component יורד
    """
    
    def __init__(self, parent: Optional[QWidget] = None):
        """
        Args:
            parent: Widget האב (בדרך כלל ה-MainWindow)
        """
        super().__init__(parent)
        
        # State של ה-Component
        self._state: Dict[str, Any] = {}
        self._is_mounted: bool = False
        
        # Layout ראשי
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # בניית הממשק (כל component מממש את זה)
        self.setup_ui()
    
    @abstractmethod
    def setup_ui(self) -> None:
        """
        בניית הממשק של ה-Component
        
        כל component חייב לממש פונקציה זו!
        
        Example:
            def setup_ui(self):
                label = QLabel("Hello from Component")
                self.main_layout.addWidget(label)
        """
        pass
    
    def on_mount(self) -> None:
        """
        נקרא כשה-Component נטען ומוצג
        
        זה המקום לטעון נתונים, להתחבר לsignals, וכו'.
        
        Example:
            def on_mount(self):
                print("Component mounted!")
                self.load_data()
        """
        self._is_mounted = True
        print(f"✅ {self.__class__.__name__} mounted")
    
    def on_unmount(self) -> None:
        """
        נקרא כשה-Component יורד (לפני שמחליפים אותו)
        
        זה המקום לנקות resources, לנתק signals, וכו'.
        
        Example:
            def on_unmount(self):
                print("Component unmounted!")
                self.cleanup_threads()
        """
        self._is_mounted = False
        print(f"❌ {self.__class__.__name__} unmounted")
    
    @property
    def is_mounted(self) -> bool:
        """בדיקה אם ה-Component כרגע מוצג"""
        return self._is_mounted
    
    def set_state(self, key: str, value: Any) -> None:
        """
        שמירת ערך ב-state של ה-Component
        
        Args:
            key: מפתח
            value: ערך
            
        Example:
            self.set_state("selected_article_id", 123)
        """
        self._state[key] = value
    
    def get_state(self, key: str, default: Any = None) -> Any:
        """
        קבלת ערך מה-state
        
        Args:
            key: מפתח
            default: ערך ברירת מחדל אם אין
            
        Returns:
            הערך או default
            
        Example:
            article_id = self.get_state("selected_article_id")
        """
        return self._state.get(key, default)
    
    def clear_state(self) -> None:
        """ניקוי כל ה-state"""
        self._state.clear()
    
    def show_loading(self, message: str = "Loading...") -> None:
        """
        הצגת אינדיקטור טעינה
        
        Components יכולים לממש את זה אם רוצים
        """
        pass
    
    def hide_loading(self) -> None:
        """
        הסתרת אינדיקטור טעינה
        """
        pass
    
    def show_error(self, message: str) -> None:
        """
        הצגת הודעת שגיאה
        
        Args:
            message: הודעת השגיאה
        """
        from PySide6.QtWidgets import QMessageBox
        QMessageBox.critical(self, "Error", message)
    
    def show_success(self, message: str) -> None:
        """
        הצגת הודעת הצלחה
        
        Args:
            message: הודעת ההצלחה
        """
        from PySide6.QtWidgets import QMessageBox
        QMessageBox.information(self, "Success", message)