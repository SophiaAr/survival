import argparse
import json
import time
from typing import Any, Dict, Optional, List
from . import x
import sys
from datetime import datetime

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
    args_dict = {k: v for k, v in vars(args).items() if v is not None and k not in ("func", "output")}
    output_path = args.output
    
    query = " ".join(args_dict.pop("query", []))
    pretty = args_dict.pop("pretty", False)
    
    try:
        posts, pagination, rate_limit = x.search_recent_posts(query, **args_dict)
        result = {
            "posts": posts,
            "pagination": pagination,
            "rate_limit": rate_limit
        }
        output = format_output("x/search-recent", query, args_dict, None, result)
    except Exception as e:
        output = format_output("x/search-recent", query, args_dict, str(e), None)
    
    if output_path:
        if pretty:
            with open(output_path, "w") as f:
                json.dump(output, f, indent=4, sort_keys=True)
        else:
            with open(output_path, "w") as f:
                json.dump(output, f)
    else:
        if pretty:
            print(json.dumps(output, indent=4, sort_keys=True))
        else:
            print(json.dumps(output))

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

    parser.set_defaults(func=lambda _: parser.print_help())
    return parser

def main():
    parser = generate_argument_parser()
    args = parser.parse_args()
    return args.func(args)

if __name__ == "__main__":
    main()
