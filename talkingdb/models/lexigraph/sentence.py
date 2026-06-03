import sqlite3


class SentenceLexicalModel:

    @staticmethod
    def init_db(conn: sqlite3.Connection):
        conn.executescript("""
        PRAGMA journal_mode = WAL;

        CREATE TABLE IF NOT EXISTS sentence_dictionary (
            phrase TEXT PRIMARY KEY,
            frequency INTEGER DEFAULT 1
        );

        CREATE TABLE IF NOT EXISTS sentence_deletes (
            delete_phrase TEXT,
            phrase TEXT,
            PRIMARY KEY (delete_phrase, phrase)
        );

        CREATE TABLE IF NOT EXISTS sentence_entity_index (
            phrase TEXT,
            entity_id TEXT,
            PRIMARY KEY (phrase, entity_id)
        );

        CREATE TABLE IF NOT EXISTS sentence_meta (
            key TEXT PRIMARY KEY,
            value TEXT
        );
        """)

    def upsert_phrase(self, conn, phrase: str):
        conn.execute("""
            INSERT INTO sentence_dictionary (phrase, frequency)
            VALUES (?, 1)
            ON CONFLICT(phrase)
            DO UPDATE SET frequency = frequency + 1
        """, (phrase,))

    def add_delete_mapping(self, conn, delete_phrase: str, phrase: str):
        conn.execute("""
            INSERT OR IGNORE INTO sentence_deletes (delete_phrase, phrase)
            VALUES (?, ?)
        """, (delete_phrase, phrase))

    def add_entity(self, conn, phrase: str, entity_id: str):
        conn.execute("""
            INSERT OR IGNORE INTO sentence_entity_index (phrase, entity_id)
            VALUES (?, ?)
        """, (phrase, entity_id))

    def remove_entity(self, conn, phrase: str, entity_id: str):
        conn.execute("""
            DELETE FROM sentence_entity_index
            WHERE phrase = ? AND entity_id = ?
        """, (phrase, entity_id))

    def get_phrase(self, conn, phrase: str):
        return conn.execute("""
            SELECT frequency FROM sentence_dictionary WHERE phrase = ?
        """, (phrase,)).fetchone()

    def get_entities(self, conn, phrase: str):
        return conn.execute("""
            SELECT entity_id FROM sentence_entity_index
            WHERE phrase = ?
        """, (phrase,)).fetchall()

    def get_candidates(self, conn, delete_phrase: str):
        return conn.execute("""
            SELECT phrase FROM sentence_deletes
            WHERE delete_phrase = ?
        """, (delete_phrase,)).fetchall()
