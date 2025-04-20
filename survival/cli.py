import argparse
import json
from . import x

def x_search_recent(args):
    try:
        results = x.search_recent_posts(args.query, args.max_results)
        print(json.dumps(results, indent=2))
    except Exception as e:
        print(f"Error: {e}")
        return 1
    return 0

def generate_argument_parser():
    parser = argparse.ArgumentParser(description="survival")
    subparsers = parser.add_subparsers(title="commands")
    
    # X search-recent command
    x_parser = subparsers.add_parser("x", help="X (Twitter) related commands")
    x_subparsers = x_parser.add_subparsers(title="subcommands")
    
    search_parser = x_subparsers.add_parser("search-recent", help="Search for recent posts on X")
    search_parser.add_argument("query", help="Search query")
    search_parser.add_argument("--max-results", type=int, default=10, help="Maximum number of results (10-100)")
    search_parser.set_defaults(func=x_search_recent)

    parser.set_defaults(func=lambda _: parser.print_help())
    return parser

def main():
    parser = generate_argument_parser()
    args = parser.parse_args()
    return args.func(args)

if __name__ == "__main__":
    main()
