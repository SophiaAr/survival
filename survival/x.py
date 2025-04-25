import os
import requests
from typing import Optional, Dict, Any, Tuple, List

def search_recent_posts(
    query: str, 
    max_results: Optional[int] = 10,
    next_token: Optional[str] = None,
    since_id: Optional[str] = None
) -> Tuple[List[Dict[str, Any]], Dict[str, Any], Dict[str, Any]]:
    """Search for recent posts on X about a given topic.
    
    Args:
        query: The search query
        max_results: Maximum number of results to return (default: 10, max: 100)
        next_token: Token for retrieving the next page of results
        since_id: Only return posts newer than this post ID
    
    Returns:
        Tuple containing:
        - data: List of posts matching the query
        - meta: Pagination metadata including next_token, newest_id, oldest_id, result_count
        - rate_limit: Rate limit info with limit, remaining, reset (seconds since epoch)
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

    # Add pagination parameters if provided
    if next_token:
        params["next_token"] = next_token
    if since_id:
        params["since_id"] = since_id

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    
    rate_limit = {
        "limit": int(response.headers.get("x-rate-limit-limit", 0)),
        "remaining": int(response.headers.get("x-rate-limit-remaining", 0)),
        "reset": int(response.headers.get("x-rate-limit-reset", 0))
    }
    
    result = response.json()
    return result["data"], result["meta"], rate_limit 