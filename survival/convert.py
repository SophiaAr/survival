"""Data conversion utilities for survival."""

import json
import csv
from typing import List, Dict, Any

def jsonl_to_csv(input_path: str, output_path: str) -> int:
    """Convert a JSONL file containing posts to CSV format.
    
    Args:
        input_path: Path to input JSONL file
        output_path: Path to output CSV file
        
    Returns:
        Number of posts converted
        
    Raises:
        ValueError: If no posts are found in the input file
        RuntimeError: If there are any errors processing the files
    """
    try:
        # Read all posts from the JSONL file
        posts = []
        with open(input_path, 'r') as f:
            for line in f:
                try:
                    data = json.loads(line)
                    if data.get('type') == 'post':
                        post = data.get('data', {})
                        # Add X.com link
                        post['x_link'] = f"https://x.com/i/web/status/{post.get('id')}"
                        posts.append(post)
                except json.JSONDecodeError:
                    continue

        if not posts:
            raise ValueError("No posts found in input file")

        # Write to CSV
        with open(output_path, 'w', newline='') as f:
            # Get all possible fields from all posts
            fieldnames = set()
            for post in posts:
                fieldnames.update(post.keys())
            fieldnames = sorted(list(fieldnames))

            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(posts)

        return len(posts)

    except Exception as e:
        raise RuntimeError(f"Error processing file: {str(e)}") 