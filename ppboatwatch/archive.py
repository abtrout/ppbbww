import logging
import sqlite3

from contextlib import closing


INIT_TABLES_SQL = """
CREATE TABLE IF NOT EXISTS matches (
    ts,
    filename,
    label,
    score,
    x0, y0, x1, y1
)"""

ADD_MATCH_SQL = """
INSERT INTO matches (ts, filename, label, score, x0, y0, x1, y1)
VALUES (?, ?, ?, ?, ?, ?, ?, ?)"""

LIST_MATCHES_SQL = """
SELECT ts, filename, label, score, x0, y0, x1, y1
FROM matches ORDER BY ts DESC"""


class Archive:
    def __init__(self, db_file):
        self.con = sqlite3.connect(db_file)
        with closing(self.con.cursor()) as cur:
            cur.executescript(INIT_TABLES_SQL)
            self.con.commit()

    def add_match(self, *, ts, filename, label, score, box):
        with closing(self.con.cursor()) as cur:
            res = cur.execute(ADD_MATCH_SQL, (ts, filename, label, score, *box))
            self.con.commit()
            return res

    def list_matches(self):
        with closing(self.con.cursor()) as cur:
            return cur.execute(LIST_MATCHES_SQL).fetchall()

