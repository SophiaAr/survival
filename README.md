# Survival

A command-line tool for interacting with the X (Twitter) API.

## Installation

```bash
pip install -e .
```

## Environment Variables

Set your X API token:
```bash
export SURVIVAL_X_API_TOKEN="your_token_here"
```

## Commands

### Search Recent Posts

Search for recent posts on X with pagination support.

```bash
# Basic search
survival x search-recent "your query here"

# With output file
survival x search-recent "your query here" --outfile results.json

# With pagination
survival x search-recent "your query here" --next-token <token>

# With max results (10-100)
survival x search-recent "your query here" --max-results 50

# Pretty print output
survival x search-recent "your query here" --pretty
```

### Crawl Posts

Crawl recent posts on X, paginating through all available results. Results are written to a JSONL file.

```bash
# Basic crawl
survival x crawl "your query here" --outfile results.jsonl

# With max results per request (10-100)
survival x crawl "your query here" --outfile results.jsonl --max-results 50

# With custom delay between requests (in seconds)
survival x crawl "your query here" --outfile results.jsonl --delay 5

# Continue from previous crawl
survival x crawl "your query here" --outfile results.jsonl --previous previous_results.jsonl
```

### Dump Crawl Data

Convert a crawl JSONL file to CSV format. Adds X.com links for each post.

```bash
survival dump crawl --infile results.jsonl --outfile results.csv
```

### Get Follower Count

Get follower count for a user by ID or username.

```bash
# By user ID
survival x numfollowers 123456789

# By username
survival x numfollowers TwitterDev --username

# Pretty print output
survival x numfollowers TwitterDev --username --pretty
```

### Enrich Crawl Data

Enrich crawl data with author information like follower counts. Processes the entire file in two passes:
1. Collects all unique author IDs
2. Retrieves author information in batches
3. Enriches the data with author info

```bash
survival enrich --infile results.jsonl --outfile enriched_results.jsonl
```

## Output Formats

### JSONL Format

Each line in the output JSONL file contains a JSON object with the following structure:

```json
{
  "type": "post",
  "timestamp": 1234567890,
  "data": {
    "id": "1234567890",
    "text": "Post content",
    "author_id": "1234567890",
    "created_at": "2024-01-01T00:00:00Z"
  },
  "author_data": {
    "follower_count": 1234,
    "username": "example"
  }
}
```

### CSV Format

The CSV output includes all fields from the JSONL data, with nested fields flattened using underscores. For example:
- `author_data_follower_count`
- `author_data_username`

## Rate Limits

The tool automatically handles X API rate limits by:
1. Processing authors in batches of 100 (maximum allowed by the API)
2. Checking rate limit information after each request
3. Sleeping until the rate limit reset time when limits are hit

## Error Handling

All commands provide clear error messages and handle common issues:
- Missing required arguments
- Invalid file paths
- API errors
- Rate limit errors
- JSON parsing errors