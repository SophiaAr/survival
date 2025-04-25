import os
import requests
from typing import Optional

def search_recent_posts(
    query: str, 
    max_results: Optional[int] = 10,
    next_token: Optional[str] = None,
    since_id: Optional[str] = None
) -> dict:
    """Search for recent posts on X about a given topic.
    
    Args:
        query: The search query
        max_results: Maximum number of results to return (default: 10, max: 100)
        next_token: Token for retrieving the next page of results
        since_id: Only return posts newer than this post ID
    
    Returns:
        dict: The API response containing the search results and pagination metadata
              The metadata includes:
              - next_token: Token for the next page (if available)
              - newest_id: ID of the most recent post (useful for polling)
              - oldest_id: ID of the oldest post in the response
              - result_count: Number of posts in this response
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
    return response.json() 