import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import trial  # noqa: E402


def guide_record(record_id, steps, outputs=(), prerequisites=("A shell.",), kind="model"):
    return {
        "id": record_id,
        "kind": kind,
        "name": record_id.title(),
        "attributes": {
            "run_guide": {
                "record_id": record_id,
                "summary": "A synthetic guide.",
                "status": "source_reviewed_not_executed",
                "prerequisites": list(prerequisites),
                "steps": [
                    {"title": title, "shell": shell, "explanation": "x", "source_ids": ["s"], "source_locator": "x"}
                    for title, shell in steps
                ],
                "outputs": list(outputs),
                "limitations": ["Not executed."],
                "source_ids": ["s"],
                "review": {"method": "official_repository_review", "date": "2026-11-27"},
            }
        },
    }


CD_GUIDE = guide_record(
    "synthetic-cd",
    [
        ("Make and enter a directory", "mkdir -p project\ncd project\nexport TRIAL_MARK=kept"),
        ("Use it", 'test "$(basename "$PWD")" = project\ntest "$TRIAL_MARK" = kept\necho made > result.txt\necho done'),
    ],
    outputs=["The file result.txt in the project directory, and the folder project/ itself."],
)

FAIL_GUIDE = guide_record(
    "synthetic-fail",
    [
        ("Say hello", "echo hello"),
        ("Fail in the middle", "echo before\nfalse\necho after"),
        ("Never reached", "echo never > never.txt"),
    ],
)


class RunGuideTrialTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.entities = self.root / "entities"
        self.entities.mkdir()
        with (self.entities / "models.jsonl").open("w") as handle:
            for record in (CD_GUIDE, FAIL_GUIDE):
                handle.write(json.dumps(record) + "\n")

    def tearDown(self):
        self.tmp.cleanup()

    def run_trial(self, record):
        script = self.root / f"{record['id']}.sh"
        trial.main(["--entities", str(self.entities), "script", record["id"], "--out", str(script)])
        trial_dir = self.root / f"trial-{record['id']}"
        completed = subprocess.run(["bash", str(script), str(trial_dir)], capture_output=True, text=True, timeout=60)
        self.assertEqual(completed.returncode, 0, completed.stderr)
        return trial_dir, trial.build_receipt(trial_dir, record)

    def test_a_cd_and_an_export_in_one_step_hold_in_the_next(self):
        trial_dir, receipt = self.run_trial(CD_GUIDE)
        self.assertEqual(receipt["result"], "completed")
        self.assertEqual([s["status"] for s in receipt["steps"]], ["completed", "completed"])
        self.assertEqual([s["exit_code"] for s in receipt["steps"]], [0, 0])
        self.assertIn("done", receipt["steps"][1]["log_tail"])
        self.assertNotIn("likely_cause", receipt)
        self.assertEqual(receipt["run_guide_sha256"], trial.guide_hash(CD_GUIDE["attributes"]["run_guide"]))
        files = {f["path"]: f for f in receipt["outputs"]["files"]}
        self.assertEqual(files["result.txt"]["size_bytes"], len("made\n"))
        self.assertEqual(len(files["result.txt"]["sha256"]), 64)
        self.assertEqual([d["path"] for d in receipt["outputs"]["directories"]], ["project/"])
        self.assertIsInstance(receipt["runner"]["disk_free_bytes_at_start"], int)
        for key in ("os", "cpu_count", "memory_bytes", "disk_free_bytes_at_end", "receipt_python", "gpu_present"):
            self.assertIn(key, receipt["runner"])

    def test_a_failing_step_stops_the_run_and_later_steps_are_not_run(self):
        trial_dir, receipt = self.run_trial(FAIL_GUIDE)
        self.assertEqual(receipt["result"], "failed_at_step_2")
        self.assertEqual([s["status"] for s in receipt["steps"]], ["completed", "failed", "not_run"])
        self.assertEqual(receipt["steps"][1]["exit_code"], 1)
        self.assertIn("before", receipt["steps"][1]["log_tail"])
        self.assertNotIn("after", receipt["steps"][1]["log_tail"])
        self.assertIsNone(receipt["steps"][2]["seconds"])
        self.assertFalse((trial_dir / "work" / "never.txt").exists())
        self.assertEqual(receipt["likely_cause"], "other")
        self.assertEqual(receipt["manual_steps"], [])

    def test_receipt_command_writes_receipt_and_logs(self):
        trial_dir, _ = self.run_trial(FAIL_GUIDE)
        out = self.root / "receipt"
        code = trial.main(["--entities", str(self.entities), "receipt", str(trial_dir), FAIL_GUIDE["id"], "--out-dir", str(out)])
        self.assertEqual(code, 0)
        saved = json.loads((out / "receipt.json").read_text())
        self.assertEqual(saved["record_id"], FAIL_GUIDE["id"])
        self.assertTrue((out / "logs" / "2.log").is_file())
        table = trial.summary(saved)
        self.assertIn("| 2 | Fail in the middle | failed | 1 |", table)
        self.assertIn("| 3 | Never reached | not_run |  |  |", table)

    def test_receipt_refuses_a_changed_guide(self):
        trial_dir, _ = self.run_trial(FAIL_GUIDE)
        changed = json.loads(json.dumps(FAIL_GUIDE))
        changed["attributes"]["run_guide"]["steps"][0]["shell"] = "echo changed"
        with self.assertRaises(SystemExit):
            trial.build_receipt(trial_dir, changed)

    def test_step_text_containing_the_heredoc_delimiter_is_kept_whole(self):
        record = guide_record("synthetic-delimiter", [("Tricky", "echo RUN_GUIDE_STEP_1_END > tricky.txt")],
                              outputs=["tricky.txt"])
        with (self.entities / "models.jsonl").open("a") as handle:
            handle.write(json.dumps(record) + "\n")
        trial_dir, receipt = self.run_trial(record)
        self.assertEqual(receipt["result"], "completed")
        self.assertEqual((trial_dir / "work" / "tricky.txt").read_text(), "RUN_GUIDE_STEP_1_END\n")


    def test_a_step_that_exits_or_drops_the_trap_is_still_recorded(self):
        for record_id, shell, code in [("synthetic-exit", "echo bye\nexit 3", 3),
                                       ("synthetic-trap", "trap - EXIT\nfalse", 1)]:
            record = guide_record(record_id, [("End it", shell), ("After", "echo after")])
            with (self.entities / "models.jsonl").open("a") as handle:
                handle.write(json.dumps(record) + "\n")
            with self.subTest(record_id=record_id):
                _, receipt = self.run_trial(record)
                self.assertEqual(receipt["result"], "failed_at_step_1")
                self.assertEqual(receipt["steps"][0]["exit_code"], code)
                self.assertEqual(receipt["steps"][1]["status"], "not_run")


class TimeoutReceiptTest(unittest.TestCase):
    """Canned record directories, since the tests cannot rely on GNU timeout being installed."""

    def receipt(self, status, run):
        with tempfile.TemporaryDirectory() as tmp:
            trial_dir = Path(tmp)
            (trial_dir / "record").mkdir()
            (trial_dir / "record" / "status.tsv").write_text("".join("\t".join(row) + "\n" for row in status))
            (trial_dir / "record" / "run.tsv").write_text("".join("\t".join(row) + "\n" for row in run))
            return trial.build_receipt(trial_dir, FAIL_GUIDE)

    started = [("started_at", "2026-11-27T10:00:00Z"), ("timeout_seconds", "60")]
    step_one = [("begin", "1", "100"), ("end", "1", "101", "0", "normal"), ("begin", "2", "101")]

    def test_a_trap_written_end_after_the_timeout_is_a_timeout(self):
        receipt = self.receipt(self.step_one + [("end", "2", "160", "143", "exit")],
                               self.started + [("finished_at", "x"), ("session_exit", "124"), ("timed_out", "yes")])
        self.assertEqual(receipt["result"], "timed_out")
        self.assertEqual([s["status"] for s in receipt["steps"]], ["completed", "timed_out", "not_run"])
        self.assertNotIn("likely_cause", receipt)

    def test_a_run_killed_before_it_finished_is_a_timeout(self):
        receipt = self.receipt(self.step_one, self.started)
        self.assertEqual(receipt["result"], "timed_out")
        self.assertEqual(receipt["steps"][1]["status"], "timed_out")

    def test_a_failure_before_the_timeout_stays_a_failure(self):
        receipt = self.receipt(self.step_one + [("end", "2", "102", "1", "exit")],
                               self.started + [("finished_at", "x"), ("session_exit", "1"), ("timed_out", "no")])
        self.assertEqual(receipt["result"], "failed_at_step_2")
        self.assertEqual(receipt["steps"][1]["exit_code"], 1)

    def test_no_step_begun_is_not_started(self):
        receipt = self.receipt([], self.started + [("finished_at", "x"), ("session_exit", "1"), ("timed_out", "no")])
        self.assertEqual(receipt["result"], "not_started")


class LikelyCauseTest(unittest.TestCase):
    cases = {
        "no_gpu": "AssertionError: Torch not compiled with CUDA enabled",
        "out_of_memory": "RuntimeError: [enforce fail at alloc_cpu.cpp:83] DefaultCPUAllocator: can't allocate memory: you tried to allocate 1 bytes. Error code 12 (Cannot allocate memory)",
        "out_of_disk": "ERROR: Could not install packages due to an OSError: [Errno 28] No space left on device",
        "network": "curl: (6) Could not resolve host: example.org",
        "gated_download": "huggingface_hub.errors.GatedRepoError: 401 Client Error. Cannot access gated repo for url",
        "missing_file": "FileNotFoundError: [Errno 2] No such file or directory: 'weights.pt'",
        "dependency": "ERROR: Could not find a version that satisfies the requirement tensorflow==1.15",
        "python_version": "ERROR: Package 'foo' requires a different Python: 3.12.3 not in '<3.11,>=3.8'",
        "needs_root": "sudo: a terminal is required to read the password",
        "other": "Traceback (most recent call last):\nValueError: bad value",
    }

    def test_each_rule(self):
        for cause, tail in self.cases.items():
            with self.subTest(cause=cause):
                self.assertEqual(trial.likely_cause(tail), cause)

    def test_flash_attn_build_without_cuda_is_a_gpu_cause(self):
        tail = "Failed building wheel for flash-attn\nOSError: CUDA_HOME environment variable is not set."
        self.assertEqual(trial.likely_cause(tail), "no_gpu")

    def test_download_sizes_are_not_http_errors(self):
        self.assertEqual(trial.likely_cause("Downloading foo-1.0.whl (404 kB)\nValueError: bad"), "other")

    def test_a_killed_process_with_no_message_is_memory(self):
        self.assertEqual(trial.likely_cause("", 137), "out_of_memory")


class CandidatesTest(unittest.TestCase):
    def assess(self, record, checkpoints=()):
        return trial.assess(record, list(checkpoints))

    def test_a_small_pip_guide_is_a_candidate(self):
        record = guide_record("small", [("Install", "pip install small-model"), ("Run", "python3 -c 'import small_model'")])
        ok, why, parameters = self.assess(record, [{"checkpoint": "small-base", "parameters": 30_000_000}])
        self.assertTrue(ok)
        self.assertEqual(parameters, 30_000_000)
        self.assertIn("largest in the family", why[-1])

    def test_rules_that_exclude(self):
        install = ("Install", "pip install thing")
        cases = {
            "needs a GPU or CUDA": guide_record("gpu", [install, ("Run", "python3 run.py --device cuda:0")]),
            "5 steps": guide_record("long", [install] + [("Step", "echo x")] * 4),
            "no pip or conda install": guide_record("noinstall", [("Run", "python3 run.py")]),
            "needs sudo or a container runtime": guide_record("docker", [install, ("Run", "docker run image")]),
            "has a placeholder or refers to the reader's own data": guide_record("placeholder", [install, ("Run", "python3 run.py --in /path/to/data")]),
            "has a manual step (comments only)": guide_record("manual", [install, ("Fetch", "# Download the weights by hand")]),
            "names a size of 40 GB": guide_record("big", [install], prerequisites=["About 40 GB of disk for the weights."]),
        }
        for expected, record in cases.items():
            with self.subTest(expected=expected):
                ok, why, _ = self.assess(record)
                self.assertFalse(ok)
                self.assertEqual(why, [expected])

    def test_unstated_gpu_memory_does_not_make_a_gpu_optional(self):
        record = guide_record("gpumemory", [("Install", "pip install thing")],
                              prerequisites=["A CUDA-capable GPU. Memory needs are not stated."])
        self.assertFalse(self.assess(record)[0])
        record = guide_record("gpuneed", [("Install", "pip install thing")],
                              prerequisites=["GPU need for generation is not stated."])
        self.assertTrue(self.assess(record)[0])

    def test_gpu_in_prerequisites_excludes(self):
        record = guide_record("gpuprereq", [("Install", "pip install thing")], prerequisites=["A CUDA GPU."])
        self.assertFalse(self.assess(record)[0])

    def test_an_optional_gpu_in_prerequisites_does_not_exclude(self):
        record = guide_record("gpuoptional", [("Install", "pip install thing")],
                              prerequisites=["A GPU is optional; the tool falls back to cpu."])
        ok, why, _ = self.assess(record)
        self.assertTrue(ok)
        self.assertEqual(why[0], "GPU mentioned but not as required")

    def test_named_checkpoint_counts_over_family(self):
        record = guide_record("family", [("Install", "pip install fam\npython3 -c 'load(\"org/fam-large\")'")])
        checkpoints = [
            {"checkpoint": "fam-small", "parameters": 10_000_000, "weights_url": "https://huggingface.co/org/fam-small"},
            {"checkpoint": "fam-large", "parameters": 3_000_000_000, "weights_url": "https://huggingface.co/org/fam-large"},
        ]
        ok, why, parameters = self.assess(record, checkpoints)
        self.assertFalse(ok)
        self.assertEqual(parameters, 3_000_000_000)

    def test_gated_named_checkpoint_excludes(self):
        record = guide_record("gated", [("Install", "pip install g\npython3 -c 'load(\"g-base\")'")])
        ok, why, _ = self.assess(record, [{"checkpoint": "g-base", "parameters": 1_000_000, "gated": True}])
        self.assertFalse(ok)
        self.assertEqual(why, ["named checkpoint is gated"])


class MatrixTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.entities = Path(self.tmp.name)
        record = guide_record("py", [("Install", "pip install x")], prerequisites=["Python 3.10, as the README says."])
        (self.entities / "models.jsonl").write_text(json.dumps(record) + "\n" + json.dumps(FAIL_GUIDE) + "\n")

    def tearDown(self):
        self.tmp.cleanup()

    def test_matrix_names_python_only_when_stated(self):
        plan = trial.matrix("py synthetic-fail", "30", self.entities)
        self.assertEqual(plan["matrix"]["include"], [{"id": "py", "python": "3.10"}, {"id": "synthetic-fail", "python": ""}])
        self.assertEqual(plan["timeout_minutes"], 30)
        self.assertEqual(plan["session_seconds"], 1800)
        self.assertLess(plan["timeout_minutes"], plan["step_timeout_minutes"])
        self.assertLess(plan["step_timeout_minutes"], plan["job_timeout_minutes"])

    def test_matrix_rejects_bad_input(self):
        for ids, minutes in [("", "30"), ("py", "91"), ("py", "0"), ("Py;rm", "30"), ("py py", "30"),
                             (" ".join(f"id{n}" for n in range(11)), "30"), ("missing", "30")]:
            with self.subTest(ids=ids, minutes=minutes), self.assertRaises(SystemExit):
                trial.matrix(ids, minutes, self.entities)


class OutputPathsTest(unittest.TestCase):
    def test_extracts_path_like_tokens_from_prose(self):
        names = trial.output_paths([
            "sorted.test.chromatin_profile_diffs.tsv and sorted.test.sequence_class_scores.tsv, sorted by score.",
            "Per-attempt output under results/full/platforms/<ID>/attempt-<n>/.",
            "Shapes (1, 30, 768); accuracy of 0.93 as the README says, see https://example.org/x.html",
        ])
        self.assertIn("sorted.test.chromatin_profile_diffs.tsv", names)
        self.assertIn("results/full/platforms/", names)
        self.assertNotIn("0.93", names)
        self.assertFalse(any(n.startswith("http") or "example.org" in n for n in names))


if __name__ == "__main__":
    unittest.main()
