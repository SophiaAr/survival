import argparse
import json
import time
from typing import Any, Dict, Optional, List
from . import x
import sys
from datetime import datetime
from tqdm import tqdm

def format_output(command: str, query: str, args: Dict[str, Any], error: Optional[str], result: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Format command output in a standard structure.
    
    Args:
        command: The command being executed (e.g. 'x/search-recent')
        args: Dictionary of command arguments
        error: Error message (if failed)
        result: The command result data (if successful)
        
    Returns:
        dict: Standardized output format
    """
    return {
        "command": command,
        "query": query,
        "args": args,
        "executed_at": int(time.time()),
        "errors": error,
        "result": result
    }

def x_search_recent(args: argparse.Namespace) -> None:
    """Search for recent posts on X."""
    # Convert args to dict and extract output path
    args_dict = {k: v for k, v in vars(args).items() if v is not None and k not in ("func", "output")}
    output_path = args.output
    
    # Extract and join query
    query = " ".join(args_dict.pop("query"))
    
    try:
        # Call API
        posts, pagination, rate_limit = x.search_recent_posts(query, **args_dict)
        result = {
            "posts": posts,
            "pagination": pagination,
            "rate_limit": rate_limit
        }
        output = format_output("x/search-recent", query, args_dict, None, result)
    except Exception as e:
        output = format_output("x/search-recent", query, args_dict, str(e), None)
    
    # Write output
    if output_path:
        with open(output_path, "w") as f:
            json.dump(output, f)
    else:
        print(json.dumps(output, indent=2))

def x_crawl(args: argparse.Namespace) -> None:
    """Crawl recent posts on X, paginating through all available results."""
    if not args.output:
        print("Error: --output is required for crawl command", file=sys.stderr)
        sys.exit(1)
    
    # Convert args to dict
    args_dict = {k: v for k, v in vars(args).items() if v is not None and k not in ("func", "output", "query")}
    query = " ".join(args.query)
    
    # Open output file
    with open(args.output, "a") as f:
        # Start crawling
        for posts, pagination, rate_limit in x.crawl(
            query=query,
            **args_dict
        ):
            # Write crawl metadata
            crawl_msg = {
                "type": "crawl_step",
                "timestamp": int(time.time()),
                "pagination": pagination,
                "rate_limit": rate_limit
            }
            f.write(json.dumps(crawl_msg) + "\n")
            
            # Write each post
            for post in posts:
                post_msg = {
                    "type": "post",
                    "timestamp": int(time.time()),
                    "data": post
                }
                f.write(json.dumps(post_msg) + "\n")
            
            # Print progress to stderr
            print(f"Found {len(posts)} posts (total: {pagination.get('result_count', 0)})", file=sys.stderr)
            if rate_limit.get("remaining", 0) == 0:
                reset = rate_limit.get("reset", 0)
                print(f"Rate limited, reset at {datetime.fromtimestamp(reset)}", file=sys.stderr)

def generate_argument_parser():
    parser = argparse.ArgumentParser(description="survival")
    subparsers = parser.add_subparsers(title="commands")
    
    x_parser = subparsers.add_parser("x", help="X (Twitter) related commands")
    x_subparsers = x_parser.add_subparsers(title="subcommands")
    
    search_parser = x_subparsers.add_parser(
        "search-recent", 
        help="Search for recent posts on X",
        description="""
        Search for recent posts on X with pagination support.
        
        For page-by-page navigation:
        1. Make initial request
        2. Use the next_token from response metadata for subsequent pages
        
        For polling new posts:
        1. Make initial request
        2. Use the newest_id from response metadata as since_id in next poll
        """
    )
    search_parser.add_argument("query", nargs='+', help="Search query")
    search_parser.add_argument("--max-results", type=int, default=10, help="Maximum number of results (10-100)")
    search_parser.add_argument("--next-token", help="Token for retrieving the next page of results")
    search_parser.add_argument("--since-id", help="Only return posts newer than this post ID")
    search_parser.add_argument("-o", "--output", type=str, help="Write output to file instead of stdout")
    search_parser.add_argument("--pretty", action="store_true", help="Pretty print the output")
    search_parser.set_defaults(func=x_search_recent)

    crawl_parser = x_subparsers.add_parser(
        "crawl",
        help="Crawl recent posts on X",
        description="""
        Crawl recent posts on X, paginating through all available results.
        Results are written to a JSONL file, one response per line.
        """
    )
    crawl_parser.add_argument("query", nargs='+', help="Search query")
    crawl_parser.add_argument("--output", type=str, required=True, help="Output JSONL file path")
    crawl_parser.add_argument("--max-results", type=int, default=100, help="Maximum results per request (10-100)")
    crawl_parser.add_argument("--next-token", help="Token for retrieving the next page of results")
    crawl_parser.add_argument("--since-id", help="Only return posts newer than this post ID")
    crawl_parser.add_argument("--delay", type=int, default=10, help="Seconds to wait between requests")
    crawl_parser.set_defaults(func=x_crawl)

    parser.set_defaults(func=lambda _: parser.print_help())
    return parser

def main():
    parser = generate_argument_parser()
    args = parser.parse_args()
    return args.func(args)

if __name__ == "__main__":
    main()
