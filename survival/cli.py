import argparse
import json
import time
from typing import Any, Dict, Optional, List
from . import x
import sys
from datetime import datetime
from tqdm import tqdm
from . import convert

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

def x_crawl(args: argparse.Namespace) -> None:
    """Crawl recent posts on X, paginating through all available results."""
    if not args.output:
        raise ValueError("--output is required for crawl command")
    
    # Convert args to dict
    args_dict = {k: v for k, v in vars(args).items() if v is not None and k not in ("func", "output", "query", "previous")}
    query = " ".join(args.query)
    
    # If --previous is specified, get continuation parameters
    if args.previous:
        try:
            # Read the file to find the last crawl_step message
            last_crawl_step = None
            with open(args.previous, 'r') as f:
                for line in f:
                    try:
                        data = json.loads(line)
                        if data.get('type') == 'crawl_step':
                            last_crawl_step = data
                    except json.JSONDecodeError:
                        continue  # Skip invalid JSON lines
                
                if not last_crawl_step:
                    raise ValueError("No crawl_step messages found in previous file")
                
                pagination = last_crawl_step.get('pagination', {})
                args_dict['since_id'] = pagination.get('newest_id')
                args_dict['next_token'] = pagination.get('next_token')
                
        except Exception as e:
            raise RuntimeError(f"Error reading previous file: {str(e)}")
    
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

def x_dump_crawl(args: argparse.Namespace) -> None:
    """Convert a crawl JSONL file to CSV format with X.com links."""
    if not args.input:
        raise ValueError("--input is required for dump command")
    if not args.output:
        raise ValueError("--output is required for dump command")

    try:
        num_posts = convert.jsonl_to_csv(args.input, args.output)
        print(f"Successfully converted {num_posts} posts to CSV", file=sys.stderr)
    except Exception as e:
        raise RuntimeError(f"Error processing file: {str(e)}")

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
        
        To continue a previous crawl, use --previous to specify the last JSONL file.
        The command will automatically extract the continuation parameters.
        """
    )
    crawl_parser.add_argument("query", nargs='+', help="Search query")
    crawl_parser.add_argument("--output", type=str, required=True, help="Output JSONL file path")
    crawl_parser.add_argument("--max-results", type=int, default=100, help="Maximum results per request (10-100)")
    crawl_parser.add_argument("--next-token", help="Token for retrieving the next page of results")
    crawl_parser.add_argument("--since-id", help="Only return posts newer than this post ID")
    crawl_parser.add_argument("--delay", type=int, default=10, help="Seconds to wait between requests")
    crawl_parser.add_argument("--previous", type=str, help="Previous JSONL file to continue from")
    crawl_parser.set_defaults(func=x_crawl)

    dump_parser = subparsers.add_parser("dump", help="Dump data in various formats")
    dump_subparsers = dump_parser.add_subparsers(title="subcommands")

    dump_crawl_parser = dump_subparsers.add_parser(
        "crawl",
        help="Convert crawl JSONL to CSV",
        description="""
        Convert a crawl JSONL file to CSV format.
        Adds X.com links for each post.
        """
    )
    dump_crawl_parser.add_argument("--input", type=str, required=True, help="Input JSONL file from crawl")
    dump_crawl_parser.add_argument("--output", type=str, required=True, help="Output CSV file path")
    dump_crawl_parser.set_defaults(func=x_dump_crawl)

    parser.set_defaults(func=lambda _: parser.print_help())
    return parser

def main():
    parser = generate_argument_parser()
    args = parser.parse_args()
    try:
        return args.func(args)
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
