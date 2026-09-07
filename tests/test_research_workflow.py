from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INITIALIZER = ROOT / "research-workflow" / "scripts" / "init_workspace.py"
MANIFEST_SCHEMA = ROOT / "research-workflow" / "references" / "manifest-schema.md"
ARTIFACT_TEMPLATES = ROOT / "research-workflow" / "references" / "artifact-templates.md"
EXPECTED_FILES = {
    "manifest.json",
    "brief.md",
    "state.md",
    "sources.md",
    "assumptions.md",
    "changes.md",
    "research",
    "runs",
}
MANIFEST_KEYS = {
    "schema_version",
    "project_key",
    "topic_slug",
    "title",
    "status",
    "phase",
    "created_at",
    "updated_at",
    "goal",
    "scope",
    "out_of_scope",
    "current_question",
    "current_conclusion",
    "questions",
    "source_status",
    "artifacts",
    "next_action",
}
LIST_MANIFEST_FIELDS = {
    "scope",
    "out_of_scope",
    "questions",
    "source_status",
    "artifacts",
}
EXPECTED_HEADINGS = {
    "brief.md": [
        "# Research brief",
        "## Goal",
        "## Decision or deliverable",
        "## Scope",
        "## Out of scope",
        "## Constraints",
        "## Questions",
    ],
    "state.md": [
        "# Research state",
        "## Phase",
        "## Current conclusion",
        "## Current question",
        "## Confirmed constraints",
        "## Unresolved questions",
        "## Stale, unavailable, or unauthenticated sources",
        "## Next action",
    ],
    "sources.md": ["# Sources"],
    "assumptions.md": ["# Assumptions"],
    "changes.md": ["# Research changes", "## <timestamp> — <phase>"],
}
EXPECTED_TABLE_COLUMNS = {
    "sources.md": [
        "ID",
        "Source identity/location",
        "Authority",
        "Retrieved",
        "Freshness window",
        "Scope",
        "Supports",
        "Status",
        "Last error",
    ],
    "assumptions.md": [
        "ID",
        "Assumption",
        "Reason",
        "Confidence",
        "Validation",
        "Status",
    ],
}
UTC_TIMESTAMP = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")


class ResearchWorkspaceInitializerTests(unittest.TestCase):
    def valid_manifest(self) -> dict[str, object]:
        return {
            "schema_version": 2,
            "project_key": "project",
            "topic_slug": "topic",
            "title": "Populated title",
            "status": "active",
            "phase": "deepening",
            "created_at": "2026-09-01T00:00:00Z",
            "updated_at": "2026-09-01T00:00:00Z",
            "goal": "Answer the decision",
            "scope": ["production"],
            "out_of_scope": ["staging"],
            "current_question": "What changed?",
            "current_conclusion": "Evidence is incomplete",
            "questions": [{"id": "Q1", "status": "open"}],
            "source_status": [{"id": "S1", "status": "fresh"}],
            "artifacts": [{"path": "brief.md"}],
            "next_action": "Refresh S1",
        }

    def write_existing_manifest(
        self, base: Path, content: bytes
    ) -> tuple[Path, Path, Path, Path]:
        home = base / "home"
        cwd = base / "work"
        research_home = base / "research"
        target = research_home / "project" / "topic"
        home.mkdir()
        cwd.mkdir()
        target.mkdir(parents=True)
        (target / "manifest.json").write_bytes(content)
        return home, cwd, research_home, target

    def documented_example(self, heading: str, language: str) -> str:
        text = ARTIFACT_TEMPLATES.read_text(encoding="utf-8")
        match = re.search(
            rf"^## {re.escape(heading)}\s*$.*?^```{language}\s*$\n(.*?)^```\s*$",
            text,
            re.MULTILINE | re.DOTALL,
        )
        self.assertIsNotNone(match, f"missing documented example for {heading}")
        return match.group(1)

    @staticmethod
    def headings(text: str) -> list[str]:
        headings = [line for line in text.splitlines() if re.match(r"^#{1,6} ", line)]
        return [
            "## <timestamp> — <phase>"
            if re.match(
                r"^## (?:\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z|YYYY-MM-DDTHH:MM:SSZ) — .+",
                heading,
            )
            else heading
            for heading in headings
        ]

    @staticmethod
    def table_columns(text: str) -> list[str]:
        header = next(line for line in text.splitlines() if line.startswith("|"))
        return [cell.strip() for cell in header.strip("|").split("|")]

    def run_initializer(
        self,
        slug: str,
        *,
        cwd: Path,
        home: Path,
        research_home: Path | None = None,
        root_argument: Path | None = None,
        project_key: str | None = None,
        check: bool = True,
    ) -> subprocess.CompletedProcess[str]:
        environment = os.environ.copy()
        environment["HOME"] = str(home)
        environment["PYTHONDONTWRITEBYTECODE"] = "1"
        if research_home is None:
            environment.pop("RESEARCH_HOME", None)
        else:
            environment["RESEARCH_HOME"] = str(research_home)
        command = [sys.executable, str(INITIALIZER), slug, "--cwd", str(cwd)]
        if root_argument is not None:
            command.extend(["--root", str(root_argument)])
        if project_key is not None:
            command.extend(["--project-key", project_key])
        return subprocess.run(
            command,
            cwd=cwd,
            env=environment,
            check=check,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    def test_temporary_home_uses_dot_research_fallback(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            home = base / "home"
            cwd = base / "work"
            home.mkdir()
            cwd.mkdir()
            result = self.run_initializer("fallback-topic", cwd=cwd, home=home)
            target = Path(result.stdout.splitlines()[0])
            self.assertEqual(target, home / ".research" / "standalone" / "fallback-topic")
            self.assertEqual({path.name for path in target.iterdir()}, EXPECTED_FILES)

    def test_research_home_overrides_home(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            home = base / "home"
            override = base / "research-root"
            cwd = base / "work"
            home.mkdir()
            cwd.mkdir()
            result = self.run_initializer(
                "override-topic", cwd=cwd, home=home, research_home=override
            )
            target = Path(result.stdout.splitlines()[0])
            self.assertEqual(target, override / "standalone" / "override-topic")
            self.assertFalse((home / ".research").exists())

    def test_git_origin_derives_owner_and_repository_project_key(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            home = base / "home"
            repository = base / "widget"
            research_home = base / "research"
            home.mkdir()
            subprocess.run(["git", "init", "-b", "main", str(repository)], check=True, stdout=subprocess.DEVNULL)
            subprocess.run(
                [
                    "git",
                    "-C",
                    str(repository),
                    "remote",
                    "add",
                    "origin",
                    "https://github.com/acme/widget.git",
                ],
                check=True,
            )
            result = self.run_initializer(
                "origin-topic",
                cwd=repository,
                home=home,
                research_home=research_home,
            )
            self.assertIn("project_key=acme--widget", result.stdout.splitlines())
            self.assertTrue((research_home / "acme--widget" / "origin-topic").is_dir())

    def test_scp_git_origin_derives_owner_and_repository_project_key(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            home = base / "home"
            repository = base / "widget"
            research_home = base / "research"
            home.mkdir()
            subprocess.run(
                ["git", "init", "-b", "main", str(repository)],
                check=True,
                stdout=subprocess.DEVNULL,
            )
            subprocess.run(
                [
                    "git",
                    "-C",
                    str(repository),
                    "remote",
                    "add",
                    "origin",
                    "git@github.com:acme/widget.git",
                ],
                check=True,
            )
            result = self.run_initializer(
                "origin-topic",
                cwd=repository,
                home=home,
                research_home=research_home,
            )
            self.assertIn("project_key=acme--widget", result.stdout.splitlines())
            self.assertTrue((research_home / "acme--widget" / "origin-topic").is_dir())

    def test_git_repository_without_origin_uses_local_repository_name(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            home = base / "home"
            repository = base / "Local Widget"
            research_home = base / "research"
            home.mkdir()
            subprocess.run(["git", "init", "-b", "main", str(repository)], check=True, stdout=subprocess.DEVNULL)
            result = self.run_initializer(
                "local-topic",
                cwd=repository,
                home=home,
                research_home=research_home,
            )
            self.assertIn("project_key=local--local-widget", result.stdout.splitlines())

    def test_rerun_preserves_artifacts_and_reports_created_none(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            home = base / "home"
            cwd = base / "work"
            research_home = base / "research"
            home.mkdir()
            cwd.mkdir()
            first = self.run_initializer(
                "stable-topic", cwd=cwd, home=home, research_home=research_home
            )
            target = Path(first.stdout.splitlines()[0])
            brief = target / "brief.md"
            brief.write_text("retained research brief\n", encoding="utf-8")

            second = self.run_initializer(
                "stable-topic", cwd=cwd, home=home, research_home=research_home
            )
            self.assertEqual(brief.read_text(encoding="utf-8"), "retained research brief\n")
            self.assertIn("created=none", second.stdout.splitlines())

    def test_manifest_uses_schema_two_stable_keys_and_utc_timestamps(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            home = base / "home"
            cwd = base / "work"
            research_home = base / "research"
            home.mkdir()
            cwd.mkdir()
            result = self.run_initializer(
                "manifest-topic", cwd=cwd, home=home, research_home=research_home
            )
            manifest = json.loads(
                (Path(result.stdout.splitlines()[0]) / "manifest.json").read_text(
                    encoding="utf-8"
                )
            )
            self.assertEqual(manifest["schema_version"], 2)
            self.assertEqual(set(manifest), MANIFEST_KEYS)
            self.assertRegex(manifest["created_at"], UTC_TIMESTAMP)
            self.assertRegex(manifest["updated_at"], UTC_TIMESTAMP)

    def test_documented_manifest_keys_match_generated_and_expected_keys(self) -> None:
        text = MANIFEST_SCHEMA.read_text(encoding="utf-8")
        match = re.search(r"^```json\s*$\n(.*?)^```\s*$", text, re.MULTILINE | re.DOTALL)
        self.assertIsNotNone(match, "missing required-fields JSON example")
        documented_keys = set(json.loads(match.group(1)))

        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            home = base / "home"
            cwd = base / "work"
            home.mkdir()
            cwd.mkdir()
            result = self.run_initializer("topic", cwd=cwd, home=home)
            generated_keys = set(
                json.loads(
                    (Path(result.stdout.splitlines()[0]) / "manifest.json").read_text(
                        encoding="utf-8"
                    )
                )
            )

        self.assertEqual(documented_keys, MANIFEST_KEYS)
        self.assertEqual(generated_keys, MANIFEST_KEYS)

    def test_required_artifact_invariants_match_templates_and_contract(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            home = base / "home"
            cwd = base / "work"
            home.mkdir()
            cwd.mkdir()
            result = self.run_initializer("topic", cwd=cwd, home=home)
            target = Path(result.stdout.splitlines()[0])

            for name, expected in EXPECTED_HEADINGS.items():
                with self.subTest(artifact=name, invariant="headings"):
                    generated = (target / name).read_text(encoding="utf-8")
                    documented = self.documented_example(name, "markdown")
                    self.assertEqual(self.headings(generated), expected)
                    self.assertEqual(self.headings(documented), expected)

            for name, expected in EXPECTED_TABLE_COLUMNS.items():
                with self.subTest(artifact=name, invariant="table columns"):
                    generated = (target / name).read_text(encoding="utf-8")
                    documented = self.documented_example(name, "markdown")
                    self.assertEqual(self.table_columns(generated), expected)
                    self.assertEqual(self.table_columns(documented), expected)

    def test_optional_artifacts_are_documented_but_not_generated(self) -> None:
        text = ARTIFACT_TEMPLATES.read_text(encoding="utf-8")
        self.assertIn("## facts.csv", text)
        self.assertIn("## findings.md", text)
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            home = base / "home"
            cwd = base / "work"
            home.mkdir()
            cwd.mkdir()
            result = self.run_initializer("topic", cwd=cwd, home=home)
            target = Path(result.stdout.splitlines()[0])
            self.assertFalse((target / "facts.csv").exists())
            self.assertFalse((target / "findings.md").exists())

    def test_malformed_manifest_is_rejected_without_mutation(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            original = b'{"schema_version": SECRET}'
            home, cwd, research_home, target = self.write_existing_manifest(base, original)
            result = self.run_initializer(
                "topic",
                cwd=cwd,
                home=home,
                research_home=research_home,
                project_key="project",
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("manifest.json must contain valid JSON", result.stderr)
            self.assertNotIn("SECRET", result.stderr)
            self.assertEqual((target / "manifest.json").read_bytes(), original)
            self.assertEqual({path.name for path in target.iterdir()}, {"manifest.json"})

    def test_invalid_manifest_shapes_are_rejected_without_mutation(self) -> None:
        invalid_cases: list[tuple[str, object, str]] = [
            ("root", [], "root must be a JSON object"),
            ("schema type", {**self.valid_manifest(), "schema_version": True}, "schema_version"),
            ("schema version", {**self.valid_manifest(), "schema_version": 3}, "schema_version"),
            ("missing key", {key: value for key, value in self.valid_manifest().items() if key != "goal"}, "goal"),
        ]
        for field in LIST_MANIFEST_FIELDS:
            invalid_cases.append(
                (f"{field} type", {**self.valid_manifest(), field: "not-a-list"}, field)
            )
        for field in MANIFEST_KEYS - LIST_MANIFEST_FIELDS - {"schema_version"}:
            invalid_cases.append(
                (f"{field} type", {**self.valid_manifest(), field: []}, field)
            )

        for name, manifest, expected_error in invalid_cases:
            with self.subTest(name=name), tempfile.TemporaryDirectory() as temporary:
                base = Path(temporary)
                original = (json.dumps(manifest) + "\n").encode()
                home, cwd, research_home, target = self.write_existing_manifest(base, original)
                result = self.run_initializer(
                    "topic",
                    cwd=cwd,
                    home=home,
                    research_home=research_home,
                    project_key="project",
                    check=False,
                )
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(expected_error, result.stderr)
                self.assertEqual((target / "manifest.json").read_bytes(), original)
                self.assertEqual({path.name for path in target.iterdir()}, {"manifest.json"})

    def test_valid_resume_preserves_populated_data_and_extension_keys(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            manifest = self.valid_manifest()
            manifest["extension"] = {"owner": "research-team"}
            original = (json.dumps(manifest) + "\n").encode()
            home, cwd, research_home, target = self.write_existing_manifest(base, original)
            brief = target / "brief.md"
            brief.write_text("retained research brief\n", encoding="utf-8")

            self.run_initializer(
                "topic",
                cwd=cwd,
                home=home,
                research_home=research_home,
                project_key="project",
            )
            resumed = json.loads((target / "manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(resumed["created_at"], manifest["created_at"])
            self.assertEqual(resumed["goal"], manifest["goal"])
            self.assertEqual(resumed["questions"], manifest["questions"])
            self.assertEqual(resumed["source_status"], manifest["source_status"])
            self.assertEqual(resumed["extension"], manifest["extension"])
            self.assertEqual(brief.read_text(encoding="utf-8"), "retained research brief\n")
            self.assertRegex(resumed["updated_at"], UTC_TIMESTAMP)

    def test_malicious_slug_is_sanitized_to_one_path_segment(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            home = base / "home"
            cwd = base / "work"
            research_home = base / "research"
            home.mkdir()
            cwd.mkdir()
            result = self.run_initializer(
                "../../Outside / topic",
                cwd=cwd,
                home=home,
                research_home=research_home,
            )
            target = Path(result.stdout.splitlines()[0])
            self.assertEqual(target, research_home / "standalone" / "outside-topic")
            self.assertEqual(target.relative_to(research_home).parts, ("standalone", "outside-topic"))
            self.assertFalse((base / "Outside").exists())

    def test_symlink_below_root_refuses_escape_before_outside_write(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            home = base / "home"
            cwd = base / "work"
            research_home = base / "research"
            outside = base / "outside"
            home.mkdir()
            cwd.mkdir()
            research_home.mkdir()
            outside.mkdir()
            (research_home / "project").symlink_to(outside, target_is_directory=True)

            result = self.run_initializer(
                "escaped-topic",
                cwd=cwd,
                home=home,
                root_argument=research_home,
                project_key="project",
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Refusing path outside research root", result.stderr)
            self.assertFalse((outside / "escaped-topic").exists())


if __name__ == "__main__":
    unittest.main()
