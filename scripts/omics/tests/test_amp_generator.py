"""Bounded regressions for reviewed AMP source bindings and exact CSV values."""
import csv
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[3]
GENERATOR_PATH = ROOT / "scripts/omics/build-amp-coverage.py"
NATIVE_ROOT = ROOT / "data/omics/use-case-coverage-amp-20261007"


def batch_records(added_in):
    """Records a batch added, read from the canonical store through provenance."""
    ids = {row["id"] for row in map(json.loads, (ROOT / "data/provenance/records.jsonl").read_text().splitlines())
           if row["added_in"] == added_in}
    return [record for path in sorted((ROOT / "data").glob("[ee][nv]*/*.jsonl"))
            for record in map(json.loads, path.read_text().splitlines()) if record["id"] in ids]


def digest(content):
    return hashlib.sha256(content).hexdigest()


def load_generator():
    spec = importlib.util.spec_from_file_location("amp_generator_under_test", GENERATOR_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class AmpGeneratorRegressionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.generator = load_generator()

    def test_expected_public_hash_is_required_and_original_hash_is_distinct(self):
        raw = b'{"printed_value":"73%","locator":"Table 1"}\n'
        archived = gzip.compress(raw, mtime=0)
        original_hash = digest(b"original retrieved full source")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "receipt.json.gz").write_bytes(archived)
            with patch.object(self.generator, "ROOT", root), patch.object(self.generator, "ARTIFACT_BINDINGS", {}):
                result = self.generator.bind_artifact("receipt.json.gz", digest(raw), original_hash)
                self.assertEqual(result, (digest(raw), digest(archived), False, original_hash))
                binding = self.generator.ARTIFACT_BINDINGS["receipt.json.gz"]
                self.assertEqual(binding["artifact_sha256"], digest(raw))
                self.assertEqual(binding["archive_sha256"], digest(archived))
                self.assertFalse(binding["matches_original_artifact_sha256"])
                self.generator.ARTIFACT_BINDINGS.clear()
                with self.assertRaisesRegex(ValueError, "expected reviewed value"):
                    self.generator.bind_artifact("receipt.json.gz", digest(b"unreviewed receipt"), original_hash)
                self.assertEqual(self.generator.ARTIFACT_BINDINGS, {})

    def test_changed_or_missing_archive_registry_is_rejected(self):
        verified = self.generator._ARCHIVE_TRANSFORM_PATH.read_bytes()
        with tempfile.TemporaryDirectory() as directory:
            registry = Path(directory) / "archive-transformation.json"
            with patch.object(self.generator, "_ARCHIVE_TRANSFORM_PATH", registry):
                with self.assertRaises(FileNotFoundError):
                    self.generator._load_archive_transform_registry()
                registry.write_bytes(verified)
                self.assertEqual(self.generator._load_archive_transform_registry(), self.generator.ARCHIVE_TRANSFORM_REGISTRY)
                registry.write_bytes(verified + b"\n")
                with self.assertRaisesRegex(ValueError, "changed since last reviewed"):
                    self.generator._load_archive_transform_registry()

    def test_claims_csv_preserves_every_canonical_printed_value(self):
        records = batch_records("data/omics/use-case-coverage-amp-20261007/clinical/records.jsonl")
        results = {record["id"]: record for record in records if record["kind"] == "result"}
        with (NATIVE_ROOT / "clinical/claims.csv").open(newline="") as stream:
            reader = csv.DictReader(stream)
            self.assertEqual(reader.fieldnames, ["record_id", "source_id", "locator", "printed_value", "review_scope"])
            rows = list(reader)
        self.assertEqual(len(rows), len(results))
        self.assertEqual({row["record_id"] for row in rows}, set(results))
        for row in rows:
            self.assertNotIn(None, row, row)
            self.assertTrue(all(value is not None for value in row.values()), row)
            record = results[row["record_id"]]
            self.assertEqual(row["printed_value"], record["attributes"]["printed_value"])
            self.assertEqual(row["locator"], record["attributes"]["source_locator"])
            self.assertEqual(row["source_id"], record["source_ids"][0])
            self.assertEqual(row["review_scope"], "automated_source_review")
        self.assertTrue({"23,848", "24,132"}.issubset({row["printed_value"] for row in rows}))

    def test_public_artifact_inventory_and_both_hash_layers_are_bound(self):
        records = batch_records("data/omics/use-case-coverage-amp-20261007/clinical/records.jsonl")
        sources = [record for record in records if record["kind"] == "source"]
        expected_paths = {record["attributes"]["review_artifact"] for record in sources}
        expected_paths.update(f"data/omics/amp-coverage-20261007/feng/{name}" for name in
                              ("fulltext.xml.gz", "selected-rows.json", "review-notes.md"))
        review = json.loads((NATIVE_ROOT / "review-clinical.json").read_text())["checked"]
        raw_hashes = review["bound_artifacts_raw_sha256"]
        archive_hashes = review["bound_artifacts_archive_sha256"]
        self.assertEqual(set(raw_hashes), expected_paths)
        self.assertEqual(set(archive_hashes), expected_paths)
        for relative in sorted(expected_paths):
            archived = (ROOT / relative).read_bytes()
            raw = gzip.decompress(archived) if relative.endswith(".gz") else archived
            self.assertEqual(digest(archived), archive_hashes[relative], relative)
            self.assertEqual(digest(raw), raw_hashes[relative], relative)
        for source in sources:
            attributes = source["attributes"]
            relative = attributes["review_artifact"]
            self.assertEqual(attributes["artifact_sha256"], raw_hashes[relative])
            self.assertEqual(attributes["archive_sha256"], archive_hashes[relative])
            self.assertEqual(attributes["review_artifact_matches_original_artifact_sha256"],
                             attributes["artifact_sha256"] == attributes["original_artifact_sha256"], source["id"])


if __name__ == "__main__":
    unittest.main()
