import sqlite3


class LexicalModel:

    @staticmethod
    def init_db(conn: sqlite3.Connection):
        conn.executescript("""
        PRAGMA journal_mode = WAL;

        CREATE TABLE IF NOT EXISTS lexicon_words (
            collection TEXT,
            word TEXT,
            frequency INTEGER DEFAULT 1,
            PRIMARY KEY (collection, word)
        );

        CREATE TABLE IF NOT EXISTS lexicon_meta (
            collection TEXT PRIMARY KEY,
            max_edit_distance INTEGER DEFAULT 2,
            longest_word_length INTEGER DEFAULT 0
        );
        """)

    def upsert_word(self, conn, collection: str, word: str):
        conn.execute("""
            INSERT INTO lexicon_words (collection, word, frequency)
            VALUES (?, ?, 1)
            ON CONFLICT(collection, word)
            DO UPDATE SET frequency = frequency + 1
        """, (collection, word))

    def get_words(self, conn, collection: str):
        return conn.execute("""
            SELECT word, frequency
            FROM lexicon_words
            WHERE collection = ?
        """, (collection,)).fetchall()

    def update_meta(self, conn, collection: str, max_dist: int, longest: int):
        conn.execute("""
            INSERT INTO lexicon_meta (collection, max_edit_distance, longest_word_length)
            VALUES (?, ?, ?)
            ON CONFLICT(collection)
            DO UPDATE SET
                max_edit_distance = excluded.max_edit_distance,
                longest_word_length = excluded.longest_word_length
        """, (collection, max_dist, longest))

    def get_meta(self, conn, collection: str):
        return conn.execute("""
            SELECT max_edit_distance, longest_word_length
            FROM lexicon_meta
            WHERE collection = ?
        """, (collection,)).fetchone()
