# Chromium Search Engines Export/Import

Tool for **Export/Import** search engines between **Chromium**-based **browsers**.

## Use

Using UV or Poetry:

```bash
uv run main.py
# or
poetry run python main.py
```

Using requirements:

```bash
pip install -r requirements.txt
python main.py
```

### Select the browser

![Select browser](select.png)

### Export Search Engines to a JSON file

![Export](export.png)

The JSON file is saved in the same directory as the script,
with the name `engines.json`.

### Import Search Engines from a JSON file

![alt text](import.png)

The JSONfile must be in the same directory as the script,
with the name `engines.json`.

## TODO

- Deploy as executable.
- Github CI
- ~~Tkinter → Qt~~
