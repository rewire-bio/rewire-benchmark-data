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
MSALIGN = ("evidence-official-760ab2fa8c396aeb796c", "uc20260930-source-msalign-v2")
FLIP2_LOCAL = (
    "rewire-local-20260920-source-flip2-composition",
    "rewire-local-20260920-source-flip2-train-mean",
    "rewire-local-20260921-source-composition22",
    "rewire-local-20260921-source-esm2-35m",
    "rewire-local-20260921-source-esm2-8m",
)
TRROSETTARNA = (
    "model-pages-20261126-batch3-trrosettarna-source-package-env",
    "model-pages-20261126-batch3-trrosettarna-source-package-readme",
    "model-pages-20261126-batch3-trrosettarna-source-paper",
    "model-pages-20261126-batch3-trrosettarna-source-zenodo",
)


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

    def test_companion_and_zenodo_work_groups_are_one_study_each(self):
        for label, group in (("MSAlign", MSALIGN), ("FLIP2_LOCAL", FLIP2_LOCAL), ("TRROSETTARNA", TRROSETTARNA)):
            found = {s for (s,) in self.db.execute(
                f"SELECT study_id FROM source_study WHERE source_id IN ({', '.join('?' * len(group))})", group)}
            self.assertEqual(len(found), 1, f"{label}: {sorted(found)}")


if __name__ == "__main__":
    unittest.main()
