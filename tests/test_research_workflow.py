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
UTC_TIMESTAMP = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")


class ResearchWorkspaceInitializerTests(unittest.TestCase):
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
