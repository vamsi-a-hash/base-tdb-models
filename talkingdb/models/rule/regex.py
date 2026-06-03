import sqlite3
from dataclasses import dataclass
from typing import List, Dict, Any
from smart_slugify import slugify
import time


@dataclass
class RegexRule:
    rule_id: str
    pattern: str


class RegexModel:
    def __init__(self):
        self.rules: Dict[str, List[str]] = {}

    @staticmethod
    def make_id(name: str) -> str:
        return f"regex::{slugify(name)}"

    @staticmethod
    def init_db(conn: sqlite3.Connection) -> None:
        conn.executescript("""
        PRAGMA journal_mode = WAL;
        PRAGMA synchronous = NORMAL;

        CREATE TABLE IF NOT EXISTS regex_rules (
            rule_id TEXT NOT NULL,
            pattern TEXT NOT NULL,
            created_at TEXT,
            PRIMARY KEY (rule_id, pattern)
        );

        CREATE INDEX IF NOT EXISTS idx_regex_rules_rule_id
        ON regex_rules(rule_id);
        """)

    @classmethod
    def load(cls, conn: sqlite3.Connection) -> "RegexModel":
        cur = conn.cursor()
        model = cls()

        for rule_id, pattern in cur.execute(
            "SELECT rule_id, pattern FROM regex_rules"
        ):
            model.rules.setdefault(rule_id, []).append(pattern)

        return model

    def save(self, conn: sqlite3.Connection, overwrite: bool = True) -> None:
        cur = conn.cursor()

        if overwrite:
            cur.execute("DELETE FROM regex_rules")

        for rule_id, patterns in self.rules.items():
            for pattern in patterns:
                cur.execute(
                    """
                    INSERT OR REPLACE INTO regex_rules
                    (rule_id, pattern, created_at)
                    VALUES (?, ?, ?)
                    """,
                    (rule_id, pattern, time.strftime("%Y-%m-%d %H:%M:%S"))
                )

        conn.commit()

    def add_rule(self, rule_id: str, pattern: str) -> None:
        self.rules.setdefault(rule_id, []).append(pattern)

    def remove_rule(self, rule_id: str) -> None:
        self.rules.pop(rule_id, None)

    def clear(self) -> None:
        self.rules.clear()

    def to_dict(self) -> Dict[str, Any]:
        return self.rules
