from PySide6.QtWidgets import QWidget, QVBoxLayout
from abc import ABC, abstractmethod, ABCMeta
from typing import Optional, Any, Dict


class QWidgetABCMeta(type(QWidget), ABCMeta):
    pass

class BaseComponent(QWidget, ABC, metaclass=QWidgetABCMeta):
    
    
    def __init__(self, parent: Optional[QWidget] = None):
       
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
        pass
    
    def on_mount(self) -> None:
        self._is_mounted = True
        print(f"✅ {self.__class__.__name__} mounted")
    
    def on_unmount(self) -> None:
       
        self._is_mounted = False
        print(f"❌ {self.__class__.__name__} unmounted")
    
    @property
    def is_mounted(self) -> bool:
        return self._is_mounted
    
    def set_state(self, key: str, value: Any) -> None:
        
        self._state[key] = value
    
    def get_state(self, key: str, default: Any = None) -> Any:
        
        return self._state.get(key, default)
    
    def clear_state(self) -> None:
        """ניקוי כל ה-state"""
        self._state.clear()
    
    def show_loading(self, message: str = "Loading...") -> None:
        
        pass
    
    def hide_loading(self) -> None:
        
        pass
    
    def show_error(self, message: str) -> None:
        
        from PySide6.QtWidgets import QMessageBox
        QMessageBox.critical(self, "Error", message)
    
    def show_success(self, message: str) -> None:
        from PySide6.QtWidgets import QMessageBox
        QMessageBox.information(self, "Success", message)