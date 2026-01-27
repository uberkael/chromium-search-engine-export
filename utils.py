import sqlite3
import json
import base64

BACKUP_FILE = 'engines.json'


def print_rows(rows):
    """Print each row to stdout."""
    for row in rows:
        print(row)


def db_read_keywords(database):
    """Read rows from the search engine database's `keywords` table."""
    with sqlite3.connect(database) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM keywords;')
        return cursor.fetchall()


def db_insert_rows(database, rows):
    """Insert multiple rows into the search engine `keywords` table."""
    with sqlite3.connect(database) as conn:
        cursor = conn.cursor()
        cursor.executemany('''
            INSERT OR IGNORE INTO keywords (
                id, short_name, keyword, favicon_url, url, safe_for_autoreplace, originating_url,
                date_created, usage_count, input_encodings, suggest_url, prepopulate_id, created_by_policy,
                last_modified, sync_guid, alternate_urls, image_url, search_url_post_params,
                suggest_url_post_params, image_url_post_params, new_tab_url, last_visited,
                created_from_play_api, is_active, starter_pack_id, enforced_by_policy, featured_by_policy
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', rows)
        conn.commit()


def bytes_to_base64(data):
    """Convert bytes objects in nested structures to base64 strings."""
    if isinstance(data, bytes):
        return base64.b64encode(data).decode('utf-8')
    elif isinstance(data, (list, tuple)):
        return [bytes_to_base64(item) for item in data]
    elif isinstance(data, dict):
        return {key: bytes_to_base64(value) for key, value in data.items()}
    else:
        return data


def base64_to_bytes(data):
    """Convert base64 strings back to bytes objects in nested structures."""
    if isinstance(data, str):
        # Try to decode as base64, if it fails, return the original string
        try:
            return base64.b64decode(data)
        except Exception:
            return data
    elif isinstance(data, list):
        return [base64_to_bytes(item) for item in data]
    elif isinstance(data, dict):
        return {key: base64_to_bytes(value) for key, value in data.items()}
    else:
        return data


def json_write(rows, f=BACKUP_FILE):
    """Write rows to a JSON backup file."""
    # Convert any bytes objects to base64 strings
    serializable_rows = bytes_to_base64(rows)
    with open(f, 'w', encoding='utf-8') as file:
        json.dump(serializable_rows, file, indent=2)


def json_read(f=BACKUP_FILE):
    """Read rows from a JSON backup file."""
    with open(f, 'r', encoding='utf-8') as file:
        rows = json.load(file)
        # rows = convert_base64_to_bytes(rows)
        return rows


def compare_data(rows1, rows2):
    """Compare two 2D arrays (lists of rows).

    Returns a tuple (bool, message)."""
    if len(rows1) != len(rows2):
        return False, "Outer dimensions do not match."

    for i in range(len(rows1)):
        if len(rows1[i]) != len(rows2[i]):
            return False, f"Inner dimensions do not match at row {i}."

        for j in range(len(rows1[i])):
            if rows1[i][j] != rows2[i][j]:
                return False, f"Difference found at row {i}, column {j}: {rows1[i][j]} != {rows2[i][j]}"

    return True, "The arrays are equal."


def add_spaces(lista, spaces=5):
    """Append `spaces` number of spaces to each string in `lista`."""
    return [item + ' ' * spaces for item in lista]
