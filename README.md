# survival

## Development

### Editable install

After running `pip install -e .` or `uv pip install -e .`, when you want to run the `survival` command, make sure that the project root is on your `PYTHONPATH`.

Run the following command from the project root directory:

```bash
export PYTHONPATH="$PWD:$PYTHONPATH"
```
