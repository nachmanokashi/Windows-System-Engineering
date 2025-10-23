from typing import List, Optional, Dict, Any
from datetime import datetime
from newsdesk.mvp.model.article import Article
from newsdesk.infra.http.news_api_client import NewsApiClient
from dataclasses import fields # Import fields to check existing model fields

class HttpNewsService:
    def __init__(self, api: NewsApiClient) -> None:
        self._api = api

    def _parse(self, data: Dict[str, Any]) -> Optional[Article]:
        """Processes article data from the API into an Article object, with added checks."""
        published_at_dt = None
        published_at_str = data.get("published_at")
        if published_at_str:
            try:
                # Handle potential 'Z' for UTC timezone
                published_at_dt = datetime.fromisoformat(published_at_str.replace('Z', '+00:00'))
            except (ValueError, TypeError):
                 print(f"Warning: Could not parse date '{published_at_str}'")
                 # Return None or another default instead of now()
                 # published_at_dt = datetime.now()

        # Build a dictionary with all fields the Article model expects
        expected_fields = {f.name for f in fields(Article)}
        article_args = {
            "id": str(data.get("id", "")), # Ensure ID exists
            "title": data.get("title", "No Title"),
            "summary": data.get("summary", ""),
            "source": data.get("source", "Unknown"),
            "published_at": published_at_dt, # Can be None
            "category": data.get("category", "General"),
            "image_url": data.get("image_url", ""),
            "thumb_url": data.get("thumb_url", ""),
            "content": data.get("content", "") # Ensure content is retrieved
        }

        # Filter out fields received from API but not present in the model
        valid_args = {k: v for k, v in article_args.items() if k in expected_fields}

        try:
             # Attempt to create the object only with valid fields
             return Article(**valid_args)
        except TypeError as e:
             print(f"Error creating Article object: {e}. Data received: {data}")
             print(f"Arguments passed to Article constructor: {valid_args}")
             return None # Return None if creation fails

    def list_articles(self, page: int = 1, page_size: int = 20, category: Optional[str] = None) -> Dict[str, Any]:
        """Returns the full API response for listing articles (including pagination info)."""
        params: Dict[str, Any] = {"page": page, "page_size": page_size}
        if category:
            params["category"] = category
        res = self._api.get("/articles", params=params)
        # Ensure 'items' is a list before returning
        res["items"] = res.get("items", [])
        return res

    def search_articles(self, query: str, limit: int = 20, category: Optional[str] = None) -> Dict[str, Any]:
        """Returns the full API response for searching articles."""
        params: Dict[str, Any] = {"q": query, "limit": limit}
        if category:
            params["category"] = category
        res = self._api.get("/articles/search", params=params)
        # Ensure 'items' is a list before returning
        res["items"] = res.get("items", [])
        return res

    def get(self, article_id: str) -> Optional[Article]:
        """Returns a full Article object for a specific ID."""
        try:
            # The API returns the article object directly, without extra wrapping
            res = self._api.get(f"/articles/{article_id}")
            if not isinstance(res, dict): # Check if response is a dictionary
                 print(f"Error: Invalid response format for article {article_id}. Expected dict, got {type(res)}")
                 return None
            return self._parse(res) # Send the dictionary directly to the _parse function
        except Exception as e:
            print(f"Error fetching article {article_id}: {e}")
            return None # Return None in case of error

    def get_categories(self) -> Dict[str, Any]:
        """Returns the full API response for categories."""
        res = self._api.get("/articles/categories")
        res["items"] = res.get("items", [])
        return res