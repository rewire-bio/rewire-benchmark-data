"""Sources that share a DOI are one study, on the real store.

Run after building the database (python3 kb/migrate.py):
  python3 -m unittest kb/tests/test_studies.py
KB_DB names another database.
"""
from __future__ import annotations

import collections
import os
import sqlite3
import unittest
from pathlib import Path

DB = os.environ.get("KB_DB", str(Path(__file__).resolve().parents[1] / "build" / "kb.sqlite"))
BEELINE = ("acquired-source-0f6c059ffdc338b70a5c", "acquired-source-31344fb7e5e8ae6b9666", "acquired-source-3156602fda847ae943b4")


class Studies(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db = sqlite3.connect(DB)

    @classmethod
    def tearDownClass(cls):
        cls.db.close()

    def test_sources_sharing_a_doi_are_one_study(self):
        studies = collections.defaultdict(set)
        for doi, study in self.db.execute(
                "SELECT lower(s.doi), ss.study_id FROM source s JOIN source_study ss ON ss.source_id = s.id "
                "WHERE s.doi IS NOT NULL AND s.doi NOT LIKE char(0) || '%'"):
            studies[doi].add(study)
        split = {doi: sorted(found) for doi, found in studies.items() if len(found) > 1}
        self.assertEqual(split, {})

    def test_beeline_source_data_files_are_one_study(self):
        found = {s for (s,) in self.db.execute(
            f"SELECT study_id FROM source_study WHERE source_id IN ({', '.join('?' * len(BEELINE))})", BEELINE)}
        self.assertEqual(len(found), 1)


if __name__ == "__main__":
    unittest.main()
