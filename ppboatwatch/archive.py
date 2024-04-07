import logging
import sqlite3

from contextlib import closing


INIT_TABLES_SQL = """
CREATE TABLE IF NOT EXISTS matches (
    ts INTEGER PRIMARY KEY,
    filename,
    label,
    score,
    x0, y0, x1, y1,
    gallery DEFAULT NULL
)"""

ADD_MATCH_SQL = """
INSERT OR IGNORE INTO matches (ts, filename, label, score, x0, y0, x1, y1)
VALUES (?, ?, ?, ?, ?, ?, ?, ?)"""

LIST_MATCHES_SQL = """
SELECT ts, filename, label, score, x0, y0, x1, y1, gallery
FROM matches ORDER BY ts DESC"""

LIST_GALLERY_MATCHES_SQL = """
SELECT ts, filename, label, score, x0, y0, x1, y1, gallery
FROM matches WHERE gallery IS NOT NULL ORDER BY ts DESC"""

UPDATE_GALLERY_SQL = """
UPDATE matches SET gallery = ? WHERE ts = ?"""

GET_MATCH_PAGE_SQL = """
SELECT ts, filename, label, score, x0, y0, x1, y1, gallery, previous_ts, next_ts
FROM (SELECT *,
    LAG(ts, 1) OVER (ORDER BY ts DESC) AS next_ts,
    LEAD(ts, 1) OVER (ORDER BY ts DESC) AS previous_ts
    FROM matches ORDER BY ts DESC
) WHERE ts = ?"""


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

    def list_gallery_matches(self):
        with closing(self.con.cursor()) as cur:
            return cur.execute(LIST_GALLERY_MATCHES_SQL).fetchall()

    def get_match_page(self, ts):
        with closing(self.con.cursor()) as cur:
            return cur.execute(GET_MATCH_PAGE_SQL, (ts,)).fetchone()

    def set_gallery(self, ts):
        return self.__update_gallery(ts, 1)

    def unset_gallery(self, ts):
        return self.__update_gallery(ts, None)

    def __update_gallery(self, ts, value):
        with closing(self.con.cursor()) as cur:
            res = cur.execute(UPDATE_GALLERY_SQL, (value, ts))
            self.con.commit()
            return res
