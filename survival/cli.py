import argparse
import json
import time
from typing import Any, Dict
from . import x

def format_output(command: str, args: Dict[str, Any], result: Any = None, error: str = None) -> Dict[str, Any]:
    """Format the command output in a standard structure."""
    return {
        "command": command,
        "args": args,
        "executed_at": int(time.time()),
        "errors": error,
        "result": result
    }

def x_search_recent(args):
    try:
        # Convert args to dict, excluding the func attribute
        args_dict = {k: v for k, v in vars(args).items() if k != 'func'}
        
        result = x.search_recent_posts(
            args.query,
            max_results=args.max_results,
            next_token=args.next_token,
            since_id=args.since_id
        )
        
        output = format_output("x/search-recent", args_dict, result=result)
        print(json.dumps(output, indent=2))
        return 0
    except Exception as e:
        output = format_output("x/search-recent", args_dict, error=str(e))
        print(json.dumps(output, indent=2))
        return 1

def generate_argument_parser():
    parser = argparse.ArgumentParser(description="survival")
    subparsers = parser.add_subparsers(title="commands")
    
    # X search-recent command
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
    search_parser.add_argument("query", help="Search query")
    search_parser.add_argument("--max-results", type=int, default=10, help="Maximum number of results (10-100)")
    search_parser.add_argument("--next-token", help="Token for retrieving the next page of results")
    search_parser.add_argument("--since-id", help="Only return posts newer than this post ID")
    search_parser.set_defaults(func=x_search_recent)

    parser.set_defaults(func=lambda _: parser.print_help())
    return parser

def main():
    parser = generate_argument_parser()
    args = parser.parse_args()
    return args.func(args)

if __name__ == "__main__":
    main()
