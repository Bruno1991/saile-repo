import os
import sqlite3
import xbmcvfs
import xbmcaddon

ADDON = xbmcaddon.Addon()
PROFILE_DIR = xbmcvfs.translatePath(ADDON.getAddonInfo('profile'))

if not os.path.exists(PROFILE_DIR):
    os.makedirs(PROFILE_DIR)

DB_PATH = os.path.join(PROFILE_DIR, 'saile_cache.db')

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS categories 
            (id TEXT, name TEXT, type TEXT, PRIMARY KEY(id, type))''')
        conn.execute('''CREATE TABLE IF NOT EXISTS streams 
            (stream_id TEXT PRIMARY KEY, category_id TEXT, name TEXT, type TEXT, icon TEXT, ext TEXT, plot TEXT)''')
        conn.execute('''CREATE TABLE IF NOT EXISTS series 
            (series_id TEXT PRIMARY KEY, category_id TEXT, name TEXT, cover TEXT, plot TEXT)''')
        conn.commit()
        conn.execute('CREATE INDEX IF NOT EXISTS idx_streams_category_type ON streams(category_id, type)')
        conn.execute('CREATE INDEX IF NOT EXISTS idx_categories_type ON categories(type)')
        conn.execute('CREATE INDEX IF NOT EXISTS idx_series_category_id ON series(category_id)')


def save_categories(categories, cat_type):
    with get_db() as conn:
        for c in categories:
            conn.execute('INSERT OR REPLACE INTO categories (id, name, type) VALUES (?, ?, ?)',
                         (str(c.get('category_id')), c.get('category_name'), cat_type))
        conn.commit()

def save_streams(streams, stream_type):
    with get_db() as conn:
        for s in streams:
            conn.execute('INSERT OR REPLACE INTO streams (stream_id, category_id, name, type, icon, ext, plot) VALUES (?, ?, ?, ?, ?, ?, ?)',
                         (str(s.get('stream_id')), str(s.get('category_id')), s.get('name'), stream_type, s.get('stream_icon'), s.get('container_extension', 'mp4'), s.get('plot', '')))
        conn.commit()

def save_series(series_list):
    with get_db() as conn:
        for s in series_list:
            conn.execute('INSERT OR REPLACE INTO series (series_id, category_id, name, cover, plot) VALUES (?, ?, ?, ?, ?)',
                         (str(s.get('series_id')), str(s.get('category_id')), s.get('name'), s.get('cover'), s.get('plot', '')))
        conn.commit()

def get_categories(cat_type):
    with get_db() as conn:
        return [dict(row) for row in conn.execute('SELECT id, name FROM categories WHERE type=?', (cat_type,)).fetchall()]

def get_streams(category_id, stream_type):
    with get_db() as conn:
        return [dict(row) for row in conn.execute('SELECT stream_id, name, icon, ext, plot FROM streams WHERE category_id=? AND type=?', (str(category_id), stream_type)).fetchall()]

def get_series(category_id):
    with get_db() as conn:
        return [dict(row) for row in conn.execute('SELECT series_id, name, cover, plot FROM series WHERE category_id=?', (str(category_id),)).fetchall()]

def has_data():
    with get_db() as conn:
        return conn.execute('SELECT COUNT(*) FROM categories').fetchone()[0] > 0