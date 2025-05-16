import os
import requests
import time
import json
import sys
from typing import Optional, Dict, Any, Tuple, List, Iterator
from tqdm import tqdm

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
    return result.get("data", []), result.get("meta", {}), rate_limit

def crawl(
    query: str,
    max_results: Optional[int] = 100,
    next_token: Optional[str] = None,
    since_id: Optional[str] = None,
    delay: int = 10
) -> Iterator[Tuple[List[Dict[str, Any]], Dict[str, Any], Dict[str, Any]]]:
    """Crawl recent posts on X, paginating through all available results.
    
    Args:
        query: The search query
        max_results: Maximum number of results per request (default: 100)
        next_token: Token for retrieving the next page of results
        since_id: Only return posts newer than this post ID
        delay: Seconds to wait between requests (default: 10)
        
    Yields:
        Tuple of (posts, pagination, rate_limit) for each request
    """
    total_posts = 0
    
    with tqdm(desc="Crawling posts", unit="posts") as pbar:
        while True:
            try:
                # Make API request
                posts, pagination, rate_limit = search_recent_posts(
                    query,
                    max_results=max_results,
                    next_token=next_token,
                    since_id=since_id
                )
                
                # Update progress
                total_posts += len(posts)
                pbar.update(len(posts))
                pbar.set_postfix({"total": total_posts})
                
                # Update pagination
                if newest_id := pagination.get("newest_id"):
                    since_id = newest_id
                if next_token := pagination.get("next_token"):
                    next_token = next_token
                else:
                    next_token = None
                
                # Check rate limits and sleep
                remaining = rate_limit.get("remaining", 0)
                reset = rate_limit.get("reset", 0)
                
                if remaining == 0:
                    sleep_time = (reset - time.time()) + 10
                    pbar.set_description(f"Rate limited, waiting {sleep_time:.0f}s")
                    time.sleep(sleep_time)
                else:
                    pbar.set_description(f"Waiting {delay}s between requests")
                    time.sleep(delay)
                
                yield posts, pagination, rate_limit
                    
            except Exception as e:
                print(f"Error: {str(e)}", file=sys.stderr)
                time.sleep(delay)  # Still respect delay on error
                continue 

def get_follower_count(identifier: str, by_username: bool = False) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """Get follower count for a user by ID or username.
    
    Args:
        identifier: Either author_id or username
        by_username: If True, identifier is treated as username, otherwise as author_id
        
    Returns:
        Tuple containing:
        - user_data: User data including follower count
        - rate_limit: Rate limit info with limit, remaining, reset (seconds since epoch)
        
    Raises:
        ValueError: If SURVIVAL_X_API_TOKEN is not set
        requests.exceptions.HTTPError: If API request fails
    """
    token = os.environ.get("SURVIVAL_X_API_TOKEN")
    if not token:
        raise ValueError("SURVIVAL_X_API_TOKEN environment variable not set")

    url = "https://api.twitter.com/2/users"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    # Build query parameter based on identifier type
    if by_username:
        params = {
            "usernames": identifier,
            "user.fields": "public_metrics"
        }
    else:
        params = {
            "ids": identifier,
            "user.fields": "public_metrics"
        }

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    
    rate_limit = {
        "limit": int(response.headers.get("x-rate-limit-limit", 0)),
        "remaining": int(response.headers.get("x-rate-limit-remaining", 0)),
        "reset": int(response.headers.get("x-rate-limit-reset", 0))
    }
    
    result = response.json()
    users = result.get("data", [])
    
    if not users:
        raise ValueError(f"No user found with {'username' if by_username else 'ID'}: {identifier}")
    
    return users[0], rate_limit 

def get_users_batch(user_ids: List[str]) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """Get information for multiple users in a single request.
    
    Args:
        user_ids: List of user IDs to look up
        
    Returns:
        Tuple containing:
        - users: List of user data including follower counts
        - rate_limit: Rate limit info with limit, remaining, reset (seconds since epoch)
        
    Raises:
        ValueError: If SURVIVAL_X_API_TOKEN is not set
        requests.exceptions.HTTPError: If API request fails
    """
    token = os.environ.get("SURVIVAL_X_API_TOKEN")
    if not token:
        raise ValueError("SURVIVAL_X_API_TOKEN environment variable not set")

    url = "https://api.twitter.com/2/users"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    # Join IDs with commas and request public metrics
    params = {
        "ids": ",".join(user_ids),
        "user.fields": "public_metrics,username"
    }

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    
    rate_limit = {
        "limit": int(response.headers.get("x-rate-limit-limit", 0)),
        "remaining": int(response.headers.get("x-rate-limit-remaining", 0)),
        "reset": int(response.headers.get("x-rate-limit-reset", 0))
    }
    
    result = response.json()
    return result.get("data", []), rate_limit 