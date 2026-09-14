from __future__ import annotations

import json
import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"


class ScriptTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        result = self.run_script("init_novel.py", "Test Novel", "--root", str(self.root), "--slug", "test-novel")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.project = self.root / "test-novel"

    def tearDown(self) -> None:
        self.temp.cleanup()

    def run_script(self, name: str, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPTS / name), *args],
            text=True,
            encoding="utf-8",
            capture_output=True,
            check=False,
        )

    def test_initializer_creates_schema_13_story_controls(self) -> None:
        schema = json.loads((self.project / "00_project" / "project_schema.json").read_text(encoding="utf-8"))
        self.assertEqual(schema["schema_version"], "1.3.0")
        self.assertTrue((self.project / "04_story" / "story_engine.yaml").exists())
        self.assertTrue((self.project / "04_story" / "reader_promises.yaml").exists())
        self.assertTrue((self.project / "08_memory" / "deltas").is_dir())
        registry = json.loads((self.project / "09_writing" / "repetition_registry.json").read_text(encoding="utf-8"))
        self.assertEqual(registry, {"schema_version": 1, "entries": []})

    def test_context_pack_uses_recent_summaries_and_missing_audit(self) -> None:
        plan = self.project / "05_structure" / "chapter_plans" / "chapter_0008.yaml"
        plan.write_text('chapter: 8\ncharacters:\n  - Alice\nplotline_progress: ["PL-001"]\n', encoding="utf-8")
        for chapter in range(1, 8):
            (self.project / "07_summaries" / f"chapter_{chapter:04d}_short.md").write_text(f"summary {chapter}\n", encoding="utf-8")
        state = self.project / "03_characters" / "states" / "alice.yaml"
        state.write_text('name: "Alice"\nlocation: "dock"\n', encoding="utf-8")
        default_volume = self.project / "05_structure" / "volumes" / "volume_001.md"
        default_volume.unlink()
        case_volume = self.project / "05_structure" / "volumes" / "case_001_test.md"
        case_volume.write_text("# Current Case Marker\n", encoding="utf-8")
        status = self.project / "00_project" / "status.yaml"
        status.write_text(status.read_text(encoding="utf-8") + "current_case: 1\n", encoding="utf-8")
        result = self.run_script(
            "context_pack.py", str(self.project), "--chapter", "8",
            "--recent-summaries", "5", "--max-chars", "80000", "--stdout",
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn("chapter_0002_short.md", result.stdout)
        self.assertIn("chapter_0003_short.md", result.stdout)
        self.assertIn("alice.yaml", result.stdout)
        self.assertIn("Current Case Marker", result.stdout)
        self.assertIn("## Writing Style", result.stdout)
        self.assertIn("## Context Audit", result.stdout)

    def test_repetition_scan_restores_full_cross_book_context_and_ignores_legacy_whitelist(self) -> None:
        phrase = "老河狸蜷在舟尾，正用一块旧布擦那根竹竿，一下，又一下。"
        (self.project / "06_chapters" / "chapter_0001.md").write_text(
            f"# One\n\n先发生别的事。{phrase}随后船离开了。\n", encoding="utf-8",
        )
        (self.project / "06_chapters" / "chapter_0008.md").write_text(
            f"# Eight\n\n这是八章后的场景。{phrase}这次无人说话。\n", encoding="utf-8",
        )
        (self.project / "09_writing" / "repetition_watchlist.md").write_text(
            "# Legacy\n\n- 老河狸\n- 一下\n", encoding="utf-8",
        )
        result = self.run_script(
            "scan_repetition.py", str(self.project), "--chapter", "8", "--against", "all", "--format", "json",
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["findings"])
        finding = payload["findings"][0]
        self.assertEqual(finding["other_chapter"], 1)
        self.assertIn(phrase, finding["current_context"])
        self.assertGreaterEqual(finding["length"], 24)

    def test_repetition_registry_is_occurrence_scoped_and_cannot_hide_longer_match(self) -> None:
        approved = "水在墙里走，滴，滴，滴。"
        longer = "办公室静下来。" + approved + "门外没有脚步声。"
        (self.project / "06_chapters" / "chapter_0001.md").write_text(
            f"甲。{approved}乙。\n", encoding="utf-8",
        )
        (self.project / "06_chapters" / "chapter_0008.md").write_text(
            f"丙。{approved}丁。\n", encoding="utf-8",
        )
        registry_path = self.project / "09_writing" / "repetition_registry.json"
        registry_path.write_text(json.dumps({
            "schema_version": 1,
            "entries": [{
                "id": "water-motif", "text": approved, "category": "motif",
                "chapters": [1, 8], "reason": "fixed sound",
            }],
        }, ensure_ascii=False), encoding="utf-8")
        approved_result = self.run_script(
            "scan_repetition.py", str(self.project), "--chapter", "8", "--format", "json",
        )
        self.assertEqual(json.loads(approved_result.stdout)["findings"], [])

        (self.project / "06_chapters" / "chapter_0001.md").write_text(f"甲。{longer}乙。\n", encoding="utf-8")
        (self.project / "06_chapters" / "chapter_0008.md").write_text(f"丙。{longer}丁。\n", encoding="utf-8")
        longer_result = self.run_script(
            "scan_repetition.py", str(self.project), "--chapter", "8", "--format", "json",
        )
        findings = json.loads(longer_result.stdout)["findings"]
        self.assertTrue(findings)
        self.assertIn("办公室静下来", findings[0]["text"])

    def test_repetition_scan_merges_small_changes_only_when_both_sides_are_contiguous(self) -> None:
        left = "老河狸蜷在舟尾擦着那根旧竹竿"
        right = "潮水从石缝下面一点一点涨起来"
        (self.project / "06_chapters" / "chapter_0001.md").write_text(
            f"甲。{left}仍然{right}。乙。", encoding="utf-8",
        )
        (self.project / "06_chapters" / "chapter_0008.md").write_text(
            f"丙。{left}忽然{right}。丁。", encoding="utf-8",
        )
        result = self.run_script(
            "scan_repetition.py", str(self.project), "--chapter", "8", "--format", "json",
        )
        finding = json.loads(result.stdout)["findings"][0]
        self.assertIn("忽然", finding["text"])
        self.assertLess(finding["similarity"], 1.0)
        self.assertGreater(finding["similarity"], 0.8)

    def test_accept_gate_requires_candidate_classification_and_reason(self) -> None:
        sys.path.insert(0, str(SCRIPTS))
        try:
            spec = importlib.util.spec_from_file_location("check_chapter_for_test", SCRIPTS / "check_chapter.py")
            self.assertIsNotNone(spec)
            self.assertIsNotNone(spec.loader)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
        finally:
            sys.path.pop(0)
        issue = (
            "WARN P1 cross_chapter_reuse: REP-012345abcdef ch0008:4 <-> ch0001:3; "
            "28 chars, similarity=1.00"
        )
        report_path = self.project / "10_review" / "gate_chapter_0008.md"
        report = module.report_markdown(self.project, 8, "post", [issue]).replace("- [ ]", "- [x]")
        report_path.write_text(report, encoding="utf-8")
        unresolved = module.check_manual_gate_report(report_path)
        self.assertTrue(any("lacks a checked classification and reason" in item for item in unresolved))
        report_path.write_text(
            report.replace("<classification> — <reason and action>", "motif — Fixed water-system sound motif."),
            encoding="utf-8",
        )
        self.assertEqual(module.check_manual_gate_report(report_path), [])

    def test_pre_gate_rejects_empty_required_sections(self) -> None:
        gate = self.project / "10_review" / "continuity_pre_chapter_0001.md"
        headings = [
            "Time Handoff", "New-Information Inventory", "Character Locations",
            "Character Knowledge", "Character Possessions and Access", "Information Chain",
            "Domain and Canon Constraints", "Blocking Risks",
        ]
        gate.write_text("# Gate\n\n" + "\n\n".join(f"## {item}" for item in headings) + "\n", encoding="utf-8")
        result = self.run_script(
            "check_chapter.py", str(self.project), "--chapter", "1", "--stage", "pre", "--no-report",
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("section 'Time Handoff' is empty", result.stdout)

        gate.write_text(
            "# Gate\n\n" + "\n\n".join(f"## {item}\n\n- [ ] Verify later" for item in headings) + "\n",
            encoding="utf-8",
        )
        unchecked = self.run_script(
            "check_chapter.py", str(self.project), "--chapter", "1", "--stage", "pre", "--no-report",
        )
        self.assertEqual(unchecked.returncode, 1)
        self.assertIn("section 'Information Chain' is empty", unchecked.stdout)

    def test_term_sync_requires_exact_count_and_archives(self) -> None:
        target = self.project / "02_world" / "terms.yaml"
        target.write_text("terms:\n  - old_name\n", encoding="utf-8")
        refused = self.run_script(
            "sync_term.py", str(self.project), "--term", "old_name", "--replace-with", "new_name",
            "--apply", "--confirm-count", "2",
        )
        self.assertNotEqual(refused.returncode, 0)
        self.assertIn("old_name", target.read_text(encoding="utf-8"))
        applied = self.run_script(
            "sync_term.py", str(self.project), "--term", "old_name", "--replace-with", "new_name",
            "--apply", "--confirm-count", "1",
        )
        self.assertEqual(applied.returncode, 0, applied.stderr)
        self.assertIn("new_name", target.read_text(encoding="utf-8"))
        self.assertTrue(any((self.project / "99_archive").rglob("terms.yaml")))

    def test_delta_apply_updates_freshness_and_status(self) -> None:
        (self.project / "06_chapters" / "chapter_0001.md").write_text("# Chapter 1\n\nThe door opened.\n", encoding="utf-8")
        pre_headings = [
            "Time Handoff", "New-Information Inventory", "Character Locations",
            "Character Knowledge", "Character Possessions and Access", "Information Chain",
            "Domain and Canon Constraints", "Blocking Risks",
        ]
        post_headings = [
            "Ending State", "New Facts", "Information Learned By Character", "Objects and Evidence",
            "State Updates", "Timeline Updates", "Summary Updates", "Residual Risks",
        ]
        (self.project / "10_review" / "continuity_pre_chapter_0001.md").write_text(
            "# Pre\n\n" + "\n\n".join(f"## {item}\n\n- Checked" for item in pre_headings) + "\n", encoding="utf-8",
        )
        (self.project / "10_review" / "continuity_post_chapter_0001.md").write_text(
            "# Post\n\n" + "\n\n".join(f"## {item}\n\n- Checked" for item in post_headings) + "\n", encoding="utf-8",
        )
        delta_dir = self.project / "08_memory" / "deltas"
        delta_dir.mkdir(parents=True, exist_ok=True)
        delta_path = delta_dir / "chapter_0001.json"
        full = "07_summaries/chapter_0001_summary.md"
        short = "07_summaries/chapter_0001_short.md"
        timeline = "04_story/timeline.yaml"
        scene_clock = "08_memory/scene_clock.yaml"
        delta = {
            "schema_version": 1,
            "chapter": 1,
            "canon_through_chapter": 1,
            "summary": "First turn",
            "events": [], "state_changes": [], "knowledge_changes": [], "object_changes": [],
            "relationship_changes": [], "timeline_changes": [], "plotline_changes": [], "promise_changes": [],
            "file_updates": [
                {"path": full, "content": "# Summary\n\nChanged.\n"},
                {"path": short, "content": "Changed.\n"},
                {"path": timeline, "content": "time_baseline:\n  label: story_day_0\nevents:\n  - id: TL-001\n    chapter: 1\n    day_index: 0\n    night_index: 0\n"},
                {"path": scene_clock, "content": "time_baseline:\n  label: story_day_0\nchapters:\n  - chapter: 1\n    day_index_open: 0\n    night_index_open: 0\n    day_index_close: 0\n    night_index_close: 0\n"},
            ],
            "confirmed_current": [
                "08_memory/information_ledger.yaml",
            ],
            "blocking_risks": [],
            "updated_at": "",
        }
        delta_path.write_text(json.dumps(delta, ensure_ascii=False, indent=2), encoding="utf-8")
        dry = self.run_script("apply_chapter_delta.py", str(self.project), "--chapter", "1")
        self.assertEqual(dry.returncode, 0, dry.stderr)
        self.assertFalse((self.project / full).exists())
        applied = self.run_script("apply_chapter_delta.py", str(self.project), "--chapter", "1", "--apply")
        self.assertEqual(applied.returncode, 0, applied.stderr)
        freshness = json.loads((self.project / "08_memory" / "freshness.json").read_text(encoding="utf-8"))
        self.assertEqual(freshness[full]["canon_through_chapter"], 1)
        self.assertIn("last_completed_chapter: 1", (self.project / "00_project" / "status.yaml").read_text(encoding="utf-8"))
        premature = self.run_script(
            "check_chapter.py", str(self.project), "--chapter", "1", "--stage", "accept", "--no-report",
        )
        self.assertEqual(premature.returncode, 1)
        self.assertIn("manual_gate", premature.stdout)
        repeated = self.run_script("apply_chapter_delta.py", str(self.project), "--chapter", "1", "--apply")
        self.assertEqual(repeated.returncode, 0, repeated.stderr)
        self.assertIn("ALREADY_APPLIED", repeated.stdout)
        post = self.run_script("check_chapter.py", str(self.project), "--chapter", "1", "--stage", "post")
        self.assertEqual(post.returncode, 0, post.stdout + post.stderr)
        gate_report = self.project / "10_review" / "gate_chapter_0001.md"
        gate_report.write_text(
            gate_report.read_text(encoding="utf-8").replace("- [ ]", "- [x]"),
            encoding="utf-8",
        )
        accepted = self.run_script(
            "check_chapter.py", str(self.project), "--chapter", "1", "--stage", "accept", "--no-report",
        )
        self.assertEqual(accepted.returncode, 0, accepted.stdout + accepted.stderr)


class MigrationTests(unittest.TestCase):
    def test_legacy_migration_is_additive_and_dry_by_default(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "legacy"
            (project / "00_project").mkdir(parents=True)
            (project / "00_project" / "status.yaml").write_text(
                'title: "Legacy"\nslug: "legacy"\nlast_completed_chapter: 17\n', encoding="utf-8",
            )
            dry = subprocess.run(
                [sys.executable, str(SCRIPTS / "migrate_project.py"), str(project)],
                text=True, encoding="utf-8", capture_output=True, check=False,
            )
            self.assertEqual(dry.returncode, 0, dry.stderr)
            self.assertFalse((project / "04_story" / "story_engine.yaml").exists())
            applied = subprocess.run(
                [sys.executable, str(SCRIPTS / "migrate_project.py"), str(project), "--apply"],
                text=True, encoding="utf-8", capture_output=True, check=False,
            )
            self.assertEqual(applied.returncode, 0, applied.stderr)
            self.assertTrue((project / "04_story" / "story_engine.yaml").exists())
            self.assertIn('project_schema_version: "1.3.0"', (project / "00_project" / "status.yaml").read_text(encoding="utf-8"))
            schema = json.loads((project / "00_project" / "project_schema.json").read_text(encoding="utf-8"))
            self.assertEqual(schema["canon_through_chapter"], 17)

    def test_migration_refuses_newer_schema(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "newer"
            (project / "00_project").mkdir(parents=True)
            (project / "00_project" / "status.yaml").write_text('title: "Newer"\n', encoding="utf-8")
            (project / "00_project" / "project_schema.json").write_text(
                json.dumps({"schema_version": "9.0.0"}), encoding="utf-8",
            )
            result = subprocess.run(
                [sys.executable, str(SCRIPTS / "migrate_project.py"), str(project), "--apply"],
                text=True, encoding="utf-8", capture_output=True, check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Refusing to downgrade", result.stderr)


if __name__ == "__main__":
    unittest.main()
