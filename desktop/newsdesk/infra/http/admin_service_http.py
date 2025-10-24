from typing import Optional, Dict, Any, List

class AdminServiceHttp:

    def __init__(self, api_client):
        self._api = api_client

    # ---------- Categories ----------
    def get_available_categories(self):
        """
        החזר רשימת קטגוריות זמינות לסיווג.
        """
        try:
            data = self._api.get("admin/categories")
        except Exception:
            data = self._api.get("categories")
        return data

    # ---------- Articles (list/details) ----------
    def get_all_articles(self, limit: int = 50, category: Optional[str] = None):
        """משיכת רשימת מאמרים לניהול"""
        try:
            lim = int(limit) if limit is not None else 50
        except Exception:
            lim = 50
        lim = max(1, min(lim, 1000))  

        params: Dict[str, Any] = {"limit": lim}
        if category:
            params["category"] = category

        return self._api.get("admin/articles", params=params)

    def get_article_details(self, article_id: int):
        """פרטי מאמר יחיד"""
        return self._api.get(f"admin/articles/{article_id}") 

    # ---------- CRUD ----------
    def create_article(self,
                    title: str,
                    url: str,
                    source: str,
                    summary: str = "",  
                    content: str = "",  
                    category: Optional[str] = None,
                    image_url: Optional[str] = None):
        payload = {
            "title": title,
            "url": url,
            "source": source,
            "summary": summary or "",  
            "content": content or "", 
            "category": category,
            "image_url": image_url
        }
        print(f"🔵 Creating article with payload: {payload}")
        return self._api.post("admin/articles", json=payload)

    def update_article(self, article_id: int, **fields):
        """עדכון מאמר קיים"""
        return self._api.put(f"admin/articles/{article_id}", json=fields)  

    def delete_article(self, article_id: int):
        """מחיקת מאמר"""
        return self._api.delete(f"admin/articles/{article_id}") 

    # ---------- Classification ----------
    def classify_article(self, article_id: int):
        """סיווג AI הצעתי (ללא שינוי ב-DB)"""
        return self._api.post(f"admin/articles/{article_id}/classify")
    
    def classify_draft(self, title: str, summary: str = "", content: str = ""):
        """סיווג טיוטה"""
        payload = {
            "title": title,
            "summary": summary or "",
            "content": content or ""
        }
        return self._api.post("admin/classify-draft", json=payload)

    def apply_classification(self, article_id: int):
        """החלת סיווג AI ושמירה בפועל"""
        return self._api.post(f"admin/articles/{article_id}/apply-classification")

    def get_uncategorized_articles(self, limit: int = 50):  
        """החזר מאמרים בלי קטגוריה"""
        try:
            lim = int(limit) if limit is not None else 50
        except Exception:
            lim = 50
        lim = max(1, min(lim, 100))

        return self._api.get("admin/articles/uncategorized", params={"limit": lim})

    def batch_classify(self, article_ids: List[int]):  
        """סיווג מרובה"""
        payload = {"article_ids": article_ids}
        return self._api.post("admin/articles/batch-classify", json=payload)