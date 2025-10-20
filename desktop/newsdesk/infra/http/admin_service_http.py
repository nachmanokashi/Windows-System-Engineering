from typing import Optional, Dict, Any, List
class AdminServiceHttp:
    """
    עטיפה לשירותי Admin מול ה-API.
    חשוב: ה-Presenter משתמש במתודות כאן לפי השמות שלמטה.
    """

    def __init__(self, api_client):
        # api_client אמור לספק מתודות: get(path, params=None), post(path, json=None), put(path, json=None), delete(path)
        self._api = api_client

    # ---------- Categories ----------
    def get_available_categories(self):
        """
        החזר רשימת קטגוריות זמינות לסיווג.
        יכול להחזיר list[str] או {"categories": [...] } – ה-Presenter תומך בשניהם.
        """
        try:
            data = self._api.get("/admin/categories")
        except Exception:
            # fallback (אם אין endpoint אדמין) – אפשר להביא מקטגוריות ציבוריות
            data = self._api.get("/categories")
        return data

    # ---------- Articles (list/details) ----------
    def get_all_articles(self, limit: int = 50, category: Optional[str] = None):
        """
        משיכת רשימת מאמרים לניהול.
        השרת אצלך כנראה מגביל limit<=100, לכן נעשה clamp.
        """
        try:
            lim = int(limit) if limit is not None else 50
        except Exception:
            lim = 50
        lim = max(1, min(lim, 100))

        params: Dict[str, Any] = {"limit": lim}
        if category:
            params["category"] = category

        # אם יש לך endpoint ייעודי לאדמין – החלף ל: "/admin/articles"
        return self._api.get("/articles", params=params)

    def get_article_details(self, article_id: int):
        """
        פרטי מאמר יחיד.
        אם יש לך endpoint אדמין – החלף ל: f"/admin/articles/{article_id}"
        """
        return self._api.get(f"/articles/{article_id}")

    # ---------- CRUD ----------
    def create_article(self,
                       title: str,
                       url: str,
                       source: str,
                       summary: Optional[str] = None,
                       content: Optional[str] = None,
                       category: Optional[str] = None,
                       image_url: Optional[str] = None):
        payload = {
            "title": title,
            "url": url,
            "source": source,
            "summary": summary,
            "content": content,
            "category": category,
            "image_url": image_url
        }
        # אדמין או ציבורי – תלוי במה שהגדרת בשרת
        # אם יש אדמין: return self._api.post("/admin/articles", json=payload)
        return self._api.post("/articles", json=payload)

    def update_article(self, article_id: int, **fields):
        """
        עדכון מאמר קיים. fields יכול לכלול title/url/source/summary/content/category/image_url
        """
        # אם יש אדמין: path = f"/admin/articles/{article_id}"
        path = f"/articles/{article_id}"
        return self._api.put(path, json=fields)

    def delete_article(self, article_id: int):
        # אם יש אדמין: path = f"/admin/articles/{article_id}"
        path = f"/articles/{article_id}"
        return self._api.delete(path)

    # ---------- Classification ----------
    def classify_article(self, article_id: int):
        """
        סיווג AI הצעתי (ללא שינוי ב-DB).
        """
        # אם יש אדמין: "/admin/articles/{id}/classify"
        return self._api.post(f"/articles/{article_id}/classify")

    def apply_classification(self, article_id: int):
        """
        החלת סיווג AI ושמירה בפועל.
        """
        # אם יש אדמין: "/admin/articles/{id}/apply-classification"
        return self._api.post(f"/articles/{article_id}/apply-classification")

    def get_uncategorized_articles(self, limit: int = 50):
        """
        החזר מאמרים בלי קטגוריה (לסיווג מרובה).
        אם אין endpoint ייעודי – אפשר להביא את כולם ולסנן בצד לקוח (פחות מומלץ).
        """
        try:
            lim = int(limit) if limit is not None else 50
        except Exception:
            lim = 50
        lim = max(1, min(lim, 100))

        # עדיף endpoint ייעודי:
        # return self._api.get("/admin/articles/uncategorized", params={"limit": lim})
        # fallback: הבאה רגילה + סינון (אם השרת לא מספק ייעודי)
        data = self._api.get("/articles", params={"limit": lim})
        if isinstance(data, dict):
            articles = data.get("articles", []) or data.get("data", [])
        else:
            articles = data or []

        uncategorized = [a for a in articles if isinstance(a, dict) and not a.get("category")]
        # ה-Presenter תומך גם ברשימה ישירה, אבל נחזיר dict סטנדרטי:
        return {"articles": uncategorized}

    def batch_classify(self, article_ids: List[int]):
        payload = {"article_ids": article_ids}
        return self._api.post("/articles/batch-classify", json=payload)
