# survival

## X (Twitter) Commands

### Search Recent Posts

The `x search-recent` command allows you to search for recent posts on X (formerly Twitter). Posts are returned in reverse chronological order (newest first).

```bash
# Basic search
survival x search-recent "python"

# Control number of results per page (10-100)
survival x search-recent "python" --max-results 25
```

#### Pagination

There are two ways to paginate through results:

1. **Page-by-page Navigation**
   ```bash
   # First request
   survival x search-recent "python" --max-results 25
   # Response includes "next_token" in meta section if more pages exist
   
   # Get next page using next_token from previous response
   survival x search-recent "python" --max-results 25 --next-token abc123xyz
   ```

2. **Polling for New Posts**
   ```bash
   # First request
   survival x search-recent "python" --max-results 25
   # Response includes "newest_id" in meta section
   
   # Later, get only posts newer than the last request
   survival x search-recent "python" --since-id 1234567890
   ```

Note: When polling with `--since-id`, if multiple pages of new posts exist:
1. Use the `newest_id` from the FIRST response for your next polling request
2. Use `--next-token` to get all pages of new posts before polling again


## Development

### Editable install

After running `pip install -e .` or `uv pip install -e .`, when you want to run the `survival` command, make sure that the project root is on your `PYTHONPATH`.

Run the following command from the project root directory:

```bash
export PYTHONPATH="$PWD:$PYTHONPATH"
```