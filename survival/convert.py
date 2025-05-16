"""Data conversion utilities for survival."""

import json
import csv
from typing import List, Dict, Any

def flatten_dict(d: Dict[str, Any], parent_key: str = '', sep: str = '_') -> Dict[str, Any]:
    """Flatten a nested dictionary.
    
    Args:
        d: Dictionary to flatten
        parent_key: Key of the parent dictionary
        sep: Separator to use between nested keys
        
    Returns:
        Flattened dictionary
    """
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)

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
                        # Add author data if present
                        if 'author_data' in data:
                            post['author_data'] = data['author_data']
                        # Flatten the post data
                        post = flatten_dict(post)
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