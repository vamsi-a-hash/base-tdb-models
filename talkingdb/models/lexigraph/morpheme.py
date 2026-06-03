import sqlite3


class MorphemeModel:

    @staticmethod
    def init_db(conn: sqlite3.Connection):
        conn.executescript("""
        PRAGMA journal_mode = WAL;

        CREATE TABLE IF NOT EXISTS morphemes (
            word TEXT PRIMARY KEY
        );
        """)

    def add_word(self, conn, word: str):
        conn.execute("""
            INSERT OR IGNORE INTO morphemes(word)
            VALUES (?)
        """, (word,))

    def exists(self, conn, word: str) -> bool:
        row = conn.execute("""
            SELECT 1 FROM morphemes WHERE word = ? LIMIT 1
        """, (word,)).fetchone()

        return row is not None

    def load_all(self, conn):
        return {
            row[0]
            for row in conn.execute("SELECT word FROM morphemes")
        }