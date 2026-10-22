"""Value check and receipt hashing in scripts/omics/batch.py, on small synthetic batches."""
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location("batch", ROOT / "scripts/omics/batch.py")
batch = importlib.util.module_from_spec(spec)
spec.loader.exec_module(batch)

XML = """<article><body><table-wrap><label>Table 3</label><table>
<tr><th>Metric</th><th>Method A</th><th>Method B</th></tr>
<tr><td>R<sup>2</sup></td><td>0.79 [0.75, 0.82]</td><td>0.56 [0.51, 0.60]</td></tr>
<tr><td>MUE</td><td>N/A</td><td>0.91</td></tr>
</table></table-wrap></body></article>"""

TEXT = """Table 12: Comparison.
          method   Pearson R   Kendall tau
          Boltz-2     0.66        0.48
          GAT         0.40        0.28
"""


def result(rid, source, printed, locator):
    return {"id": rid, "kind": "result", "source_ids": [source],
            "attributes": {"printed_value": printed, "source_locator": locator}}


class BatchToolTest(unittest.TestCase):
    def setUp(self):
        self.dir = Path(tempfile.mkdtemp())
        self.xml = self.dir / "a.xml"
        self.xml.write_text(XML)
        self.txt = self.dir / "b.txt"
        self.txt.write_text(TEXT)
        self.folder = self.dir / "batch"
        self.folder.mkdir()

    def write(self, records):
        (self.folder / "batch.jsonl").write_text("".join(json.dumps(r) + "\n" for r in records))

    def statuses(self, records):
        self.write(records)
        batch.check_values(self.folder, {"x": self.xml, "t": self.txt})
        lines = (self.folder / "value-check.tsv").read_text().splitlines()[1:]
        return {line.split("\t")[0]: line.split("\t")[1] for line in lines}

    def test_xml_checks_row_and_column(self):
        got = self.statuses([
            result("ok", "x", "0.56 [0.51, 0.60]", 'Table 3, row "R2", column "Method B"'),
            result("na", "x", "N/A", 'Table 3, row "MUE", column "Method A"'),
            result("swapped", "x", "0.79 [0.75, 0.82]", 'Table 3, row "R2", column "Method B"'),
            result("wrong", "x", "0.57", 'Table 3, row "R2", column "Method B"'),
            result("norow", "x", "0.1", 'Table 3, row "RMSE", column "Method B"'),
            result("notable", "x", "0.1", 'Table 9, row "R2", column "Method B"'),
        ])
        self.assertEqual(got, {"ok": "in_cell", "na": "in_cell", "swapped": "wrong_column",
                               "wrong": "not_in_row", "norow": "row_not_found", "notable": "table_not_found"})

    def test_text_checks_row(self):
        got = self.statuses([
            result("ok", "t", "0.66", 'Table 12, row "Boltz-2", column "Pearson R"'),
            result("wrong", "t", "0.67", 'Table 12, row "Boltz-2", column "Pearson R"'),
            result("prefix", "t", "0.40", 'Table 12, row "Boltz", column "Pearson R"'),
            result("free", "t", "0.66", "Section 3, paragraph 2"),
            result("nosrc", "z", "0.66", 'Table 12, row "Boltz-2"'),
        ])
        self.assertEqual(got, {"ok": "in_row", "wrong": "not_in_row", "prefix": "row_not_found",
                               "free": "locator_not_parsed", "nosrc": "no_artifact_given"})

    def test_hash_checks_artifacts_and_keeps_receipt_fields(self):
        digest = hashlib.sha256(self.xml.read_bytes()).hexdigest()
        self.write([{"id": "x", "kind": "source", "attributes": {"artifact_sha256": digest}}])
        (self.folder / "review.json").write_text(json.dumps({"method": "kept", "files": {"stale": "0"}}))
        (self.folder / "notes.md").write_text("notes\n")
        receipt, missing = batch.hash_batch(self.folder, {"x": self.xml})
        self.assertEqual(receipt["method"], "kept")
        self.assertEqual(set(receipt["files"]), {"batch.jsonl", "notes.md"})
        self.assertEqual(receipt["source_artifacts"], {"x": digest})
        self.assertIn("reviewer", missing)
        with self.assertRaises(SystemExit):
            batch.hash_batch(self.folder, {"x": self.txt})


if __name__ == "__main__":
    unittest.main()
