import os
import requests
from typing import Optional

def search_recent_posts(query: str, max_results: Optional[int] = 10) -> dict:
    """Search for recent posts on X about a given topic.
    
    Args:
        query: The search query
        max_results: Maximum number of results to return (default: 10, max: 100)
    
    Returns:
        dict: The API response containing the search results
    """
    token = os.environ.get("SURVIVAL_X_API_TOKEN")
    if not token:
        raise ValueError("SURVIVAL_X_API_TOKEN environment variable not set")

    url = "https://api.twitter.com/2/tweets/search/recent"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    params = {
        "query": query,
        "max_results": min(max(10, max_results), 100),
        "tweet.fields": "created_at,author_id,text"
    }

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json() 