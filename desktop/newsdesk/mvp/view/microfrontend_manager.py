# client/newsdesk/mvp/view/microfrontend_manager.py
"""
MicrofrontendManager - מנהל את ה-Components

תפקידים:
1. רישום components
2. החלפת components
3. ניהול מחזור החיים (lifecycle)
4. העברת נתונים בין components
"""
from typing import Dict, Type, Optional, Any
from PySide6.QtWidgets import QWidget, QStackedWidget
from newsdesk.components.base_component import BaseComponent


class MicrofrontendManager:
    """
    מנהל ה-Microfrontends
    
    אחראי על:
    - רישום components
    - החלפת components
    - ניהול state גלובלי
    """
    
    def __init__(self, container: QStackedWidget):
        """
        Args:
            container: QStackedWidget שבו נציג את ה-components
        """
        self.container = container
        
        # Dictionary של components רשומים: {name: ComponentClass}
        self._registered_components: Dict[str, Type[BaseComponent]] = {}
        
        # Dictionary של instances: {name: ComponentInstance}
        self._component_instances: Dict[str, BaseComponent] = {}
        
        # Component נוכחי
        self._current_component_name: Optional[str] = None
        
        # State גלובלי (נתונים משותפים בין components)
        self._global_state: Dict[str, Any] = {}
    
    def register_component(self, name: str, component_class: Type[BaseComponent]) -> None:
        """
        רישום component חדש
        
        Args:
            name: שם ה-component (לדוגמה: "articles_list")
            component_class: המחלקה של ה-component
            
        Example:
            manager.register_component("articles_list", ArticlesListComponent)
        """
        self._registered_components[name] = component_class
        print(f"✅ Component '{name}' registered")
    
    def load_component(self, name: str, **kwargs) -> None:
        """
        טעינת component (החלפה)
        
        Args:
            name: שם ה-component לטעון
            **kwargs: פרמטרים להעברה ל-component
            
        Example:
            manager.load_component("article_details", article_id=123)
        """
        # בדוק שה-component רשום
        if name not in self._registered_components:
            print(f"❌ Component '{name}' not registered!")
            return
        
        # אם זה אותו component, אל תעשה כלום
        if self._current_component_name == name:
            print(f"ℹ️ Component '{name}' already loaded")
            return
        
        # הסר את ה-component הנוכחי
        if self._current_component_name:
            self._unmount_current_component()
        
        # צור או קבל instance של ה-component החדש
        if name not in self._component_instances:
            # צור instance חדש
            component_class = self._registered_components[name]
            component_instance = component_class(parent=self.container)
            self._component_instances[name] = component_instance
            
            # הוסף ל-container
            self.container.addWidget(component_instance)
        
        # קבל את ה-instance
        component = self._component_instances[name]
        
        # העבר פרמטרים (אם יש)
        for key, value in kwargs.items():
            component.set_state(key, value)
        
        # הצג את ה-component
        self.container.setCurrentWidget(component)
        
        # קרא ל-on_mount
        component.on_mount()
        
        # עדכן current
        self._current_component_name = name
        
        print(f"✅ Component '{name}' loaded")
    
    def _unmount_current_component(self) -> None:
        """הורדת ה-component הנוכחי"""
        if not self._current_component_name:
            return
        
        current_component = self._component_instances.get(self._current_component_name)
        if current_component:
            # קרא ל-on_unmount
            current_component.on_unmount()
    
    def get_current_component(self) -> Optional[BaseComponent]:
        """קבלת ה-component הנוכחי"""
        if not self._current_component_name:
            return None
        return self._component_instances.get(self._current_component_name)
    
    def set_global_state(self, key: str, value: Any) -> None:
        """
        שמירת ערך ב-state גלובלי (משותף לכל ה-components)
        
        Args:
            key: מפתח
            value: ערך
            
        Example:
            manager.set_global_state("current_user", user_data)
        """
        self._global_state[key] = value
    
    def get_global_state(self, key: str, default: Any = None) -> Any:
        """
        קבלת ערך מה-state הגלובלי
        
        Args:
            key: מפתח
            default: ערך ברירת מחדל
            
        Returns:
            הערך או default
        """
        return self._global_state.get(key, default)
    
    def navigate_to(self, component_name: str, **kwargs) -> None:
        """
        ניווט ל-component אחר
        
        זה wrapper נוח ל-load_component
        
        Args:
            component_name: שם ה-component
            **kwargs: פרמטרים
            
        Example:
            manager.navigate_to("article_details", article_id=123)
        """
        self.load_component(component_name, **kwargs)
    
    def reload_current_component(self) -> None:
        """טעינה מחדש של ה-component הנוכחי"""
        if self._current_component_name:
            current = self.get_current_component()
            if current:
                current.on_unmount()
                current.on_mount()
    
    def remove_component_instance(self, name: str) -> None:
        """
        הסרת instance של component (לניקוי זיכרון)
        
        Args:
            name: שם ה-component
        """
        if name in self._component_instances:
            component = self._component_instances[name]
            component.on_unmount()
            self.container.removeWidget(component)
            component.deleteLater()
            del self._component_instances[name]
            print(f"🗑️ Component '{name}' instance removed")


# ============================================
# דוגמה לשימוש (לא חלק מהקובץ - רק הסבר)
# ============================================

"""
# יצירת המנהל
container = QStackedWidget()
manager = MicrofrontendManager(container)

# רישום components
manager.register_component("articles_list", ArticlesListComponent)
manager.register_component("article_details", ArticleDetailsComponent)
manager.register_component("charts", ChartsComponent)

# טעינת component ראשון
manager.load_component("articles_list")

# ניווט לפרטי מאמר
manager.navigate_to("article_details", article_id=123)

# חזרה לרשימה
manager.navigate_to("articles_list")
"""