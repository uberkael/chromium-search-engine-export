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


def db_get_existing_ids(database, ids):
    """Check which ids already exist in the keywords table."""
    if not ids:
        return set()
    with sqlite3.connect(database) as conn:
        cursor = conn.cursor()
        placeholders = ', '.join(['?'] * len(ids))
        cursor.execute(f'SELECT id FROM keywords WHERE id IN ({placeholders})', ids)
        existing = cursor.fetchall()
        return {row[0] for row in existing}


def compare_rows(old_row, new_row):
    """Compare two rows and return a diff string for key fields in HTML."""
    key_fields = {
        1: 'Name',
        2: 'Shortcut',
        3: 'Favicon URL',
        4: 'URL',
        10: 'Suggest URL'
    }
    diff = []
    for i, (o, n) in enumerate(zip(old_row, new_row)):
        if o != n and i in key_fields:
            diff.append(f"<b>{key_fields[i]}:</b><br><span style='background-color:#ff0000;color:black;padding:2px'>{o}</span> → <span style='background-color:#0066cc;color:white;padding:2px'>{n}</span>")
    return "<br>".join(diff) if diff else "No key changes"


def get_row_by_id(database, row_id):
    """Get a row by id from keywords table."""
    with sqlite3.connect(database) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM keywords WHERE id = ?', (row_id,))
        return cursor.fetchone()


def db_insert_rows(database, rows, mode='ignore'):
    """Insert multiple rows into the search engine `keywords` table.
    
    mode: 'ignore' to skip existing, 'replace' to update existing.
    """
    with sqlite3.connect(database) as conn:
        cursor = conn.cursor()
        
        # Get the table schema to determine the number of columns
        cursor.execute('PRAGMA table_info(keywords);')
        columns_info = cursor.fetchall()
        column_names = [col[1] for col in columns_info]
        num_columns = len(column_names)
        
        # Adjust rows to match the target database schema
        adjusted_rows = []
        for row in rows:
            row_list = list(row)
            
            # If row has fewer columns than target, pad with NULL
            while len(row_list) < num_columns:
                row_list.append(None)
            
            # If row has more columns than target, truncate
            if len(row_list) > num_columns:
                row_list = row_list[:num_columns]
            
            adjusted_rows.append(tuple(row_list))
        
        # Build the INSERT statement dynamically
        columns_str = ', '.join(column_names)
        placeholders = ', '.join(['?'] * num_columns)
        
        or_clause = 'OR REPLACE' if mode == 'replace' else 'OR IGNORE'
        
        cursor.executemany(f'''
            INSERT {or_clause} INTO keywords ({columns_str})
            VALUES ({placeholders})
        ''', adjusted_rows)
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


def handle_import_conflicts(file_path, filas):
    """Prepare data for import and identify conflicts and new entries.
    
    Returns: (to_insert, conflicts) where conflicts is list of (eid, old_row, new_row)
    """
    # Prepare data
    new_rows = {row[0]: row for row in filas}
    ids = list(new_rows.keys())
    existing_ids = db_get_existing_ids(file_path, ids)
    
    conflicts = []
    
    for eid in existing_ids:
        if eid in new_rows:
            old_row = get_row_by_id(file_path, eid)
            new_row = new_rows[eid]
            if old_row != tuple(new_row):
                conflicts.append((eid, old_row, new_row))
    
    # New entries
    to_insert = [row for row in filas if row[0] not in existing_ids]
    
    return to_insert, conflicts


def add_spaces(lista, spaces=5):
    """Append `spaces` number of spaces to each string in `lista`."""
    return [item + ' ' * spaces for item in lista]
