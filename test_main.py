import os
import sqlite3
import tempfile

import locations
import utils


def test_browser_names():
    browsers = ["chrome", "chromium", "brave", "edge", "vivaldi", "opera", "helium"]

    for k in locations.LOCATIONS.keys():
        assert k in browsers


def test_padding():
    lista = ['a', 'b', 'c']
    assert utils.add_spaces(lista) == ['a     ', 'b     ', 'c     ']


def test_compare_rows():
    old_row = (1, 'Google', 'google', 'favicon.ico', 'https://google.es/search?q={searchTerms}', 1, '', 0, 0, 'UTF-8', 'https://google.es/complete/search?q={searchTerms}', 1, 0, 0, 'guid', '[]', '', '', '', '', '', 0, 0, 1, 0, 0, 0)
    new_row = (1, 'Google', 'google', 'favicon.ico', 'https://google.com/search?q={searchTerms}', 1, '', 0, 0, 'UTF-8', 'https://google.com/complete/search?q={searchTerms}', 1, 0, 0, 'guid', '[]', '', '', '', '', '', 0, 0, 1, 0, 0, 0)
    
    diff = utils.compare_rows(old_row, new_row)
    assert 'URL:' in diff
    assert 'Suggest URL:' in diff
    assert 'google.<span style=\'background-color:#ff0000;color:black;padding:2px\'>es</span>/search?q={searchTerms}' in diff
    assert 'google.<span style=\'background-color:#0066cc;color:white;padding:2px\'>com</span>/search?q={searchTerms}' in diff
    """Test that db_insert_rows handles different column counts correctly."""

    # Create two temporary databases with different schemas
    with tempfile.TemporaryDirectory() as tmpdir:
        db_27_cols = os.path.join(tmpdir, 'db_27.sqlite')
        db_28_cols = os.path.join(tmpdir, 'db_28.sqlite')

        # Create database with 27 columns (Chromium)
        with sqlite3.connect(db_27_cols) as conn:
            conn.execute('''
                CREATE TABLE keywords (
                    id INTEGER, short_name VARCHAR, keyword VARCHAR, favicon_url VARCHAR,
                    url VARCHAR, safe_for_autoreplace INTEGER, originating_url VARCHAR,
                    date_created INTEGER, usage_count INTEGER, input_encodings VARCHAR,
                    suggest_url VARCHAR, prepopulate_id INTEGER, created_by_policy INTEGER,
                    last_modified INTEGER, sync_guid VARCHAR, alternate_urls VARCHAR,
                    image_url VARCHAR, search_url_post_params VARCHAR,
                    suggest_url_post_params VARCHAR, image_url_post_params VARCHAR,
                    new_tab_url VARCHAR, last_visited INTEGER, created_from_play_api INTEGER,
                    is_active INTEGER, starter_pack_id INTEGER, enforced_by_policy INTEGER,
                    featured_by_policy INTEGER
                )
            ''')

        # Create database with 28 columns (Edge)
        with sqlite3.connect(db_28_cols) as conn:
            conn.execute('''
                CREATE TABLE keywords (
                    id INTEGER, short_name VARCHAR, keyword VARCHAR, favicon_url VARCHAR,
                    url VARCHAR, safe_for_autoreplace INTEGER, originating_url VARCHAR,
                    date_created INTEGER, usage_count INTEGER, input_encodings VARCHAR,
                    suggest_url VARCHAR, prepopulate_id INTEGER, created_by_policy INTEGER,
                    last_modified INTEGER, sync_guid VARCHAR, alternate_urls VARCHAR,
                    image_url VARCHAR, search_url_post_params VARCHAR,
                    suggest_url_post_params VARCHAR, image_url_post_params VARCHAR,
                    new_tab_url VARCHAR, last_visited INTEGER, created_from_play_api INTEGER,
                    is_active INTEGER, starter_pack_id INTEGER, enforced_by_policy INTEGER,
                    featured_by_policy INTEGER, url_hash BLOB
                )
            ''')

        # Test data with 27 columns
        test_row_27 = [(1, 'Google', 'google.com', 'favicon.ico', 'https://google.com/search?q={searchTerms}',
                        1, '', 0, 0, 'UTF-8', 'https://google.com/complete/search?q={searchTerms}',
                        1, 0, 0, 'test-guid', '[]', '', '', '', '', '', 0, 0, 1, 0, 0, 0)]

        # Test inserting 27-column data into 27-column database
        utils.db_insert_rows(db_27_cols, test_row_27)
        with sqlite3.connect(db_27_cols) as conn:
            result = conn.execute('SELECT * FROM keywords WHERE id = 1').fetchone()
            assert result is not None
            assert len(result) == 27
            assert result[1] == 'Google'

        # Test inserting 27-column data into 28-column database (should pad with NULL)
        utils.db_insert_rows(db_28_cols, test_row_27)
        with sqlite3.connect(db_28_cols) as conn:
            result = conn.execute('SELECT * FROM keywords WHERE id = 1').fetchone()
            assert result is not None
            assert len(result) == 28
            assert result[1] == 'Google'
            assert result[27] is None  # url_hash should be NULL

        # Test data with 28 columns
        test_row_28 = [(2, 'Bing', 'bing.com', 'favicon.ico', 'https://bing.com/search?q={searchTerms}',
                        1, '', 0, 0, 'UTF-8', 'https://bing.com/complete/search?q={searchTerms}',
                        2, 0, 0, 'test-guid-2', '[]', '', '', '', '', '', 0, 0, 1, 0, 0, 0, b'hash')]

        # Test inserting 28-column data into 28-column database
        utils.db_insert_rows(db_28_cols, test_row_28)
        with sqlite3.connect(db_28_cols) as conn:
            result = conn.execute('SELECT * FROM keywords WHERE id = 2').fetchone()
            assert result is not None
            assert len(result) == 28
            assert result[1] == 'Bing'

        # Test inserting 28-column data into 27-column database (should truncate)
        utils.db_insert_rows(db_27_cols, test_row_28)
        with sqlite3.connect(db_27_cols) as conn:
            result = conn.execute('SELECT * FROM keywords WHERE id = 2').fetchone()
            assert result is not None
            assert len(result) == 27
            assert result[1] == 'Bing'
