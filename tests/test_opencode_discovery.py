from __future__ import annotations

import hashlib
import http.server
import json
import os
import shutil
import subprocess
import sys
import tempfile
import threading
import unittest
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator


ROOT = Path(__file__).resolve().parents[1]
EXPECTED_OPENCODE_VERSION = "1.18.27"
SKILL_NAME = "research-workflow"


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format: str, *args: object) -> None:
        pass


@contextmanager
def serve(directory: Path) -> Iterator[http.server.ThreadingHTTPServer]:
    handler = lambda *args, **kwargs: QuietHandler(  # noqa: E731
        *args, directory=str(directory), **kwargs
    )
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield server
    finally:
        server.shutdown()
        server.server_close()
        thread.join()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class OpenCodeDiscoveryTests(unittest.TestCase):
    def require_supported_opencode(self) -> str:
        executable = shutil.which("opencode")
        if executable is None:
            if os.environ.get("REQUIRE_OPENCODE") == "1":
                self.fail("REQUIRE_OPENCODE=1 but opencode is unavailable")
            self.skipTest("opencode is unavailable")
        result = subprocess.run(
            [executable, "--version"],
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.assertEqual(result.returncode, 0, "opencode --version failed")
        self.assertEqual(result.stdout.strip(), EXPECTED_OPENCODE_VERSION)
        return executable

    def isolated_environment(self, base: Path) -> tuple[dict[str, str], Path, Path]:
        home = base / "home"
        config = base / "config"
        cache = base / "cache"
        data = base / "data"
        state = base / "state"
        for path in (home, config, cache, data, state):
            path.mkdir(parents=True)
        environment = os.environ.copy()
        environment.update(
            {
                "HOME": str(home),
                "XDG_CONFIG_HOME": str(config),
                "XDG_CACHE_HOME": str(cache),
                "XDG_DATA_HOME": str(data),
                "XDG_STATE_HOME": str(state),
                "OPENCODE_DISABLE_PROJECT_CONFIG": "1",
                "OPENCODE_DISABLE_EXTERNAL_SKILLS": "1",
                "PYTHONDONTWRITEBYTECODE": "1",
            }
        )
        return environment, config, cache

    def write_config(self, config_root: Path, url: str) -> None:
        config_directory = config_root / "opencode"
        config_directory.mkdir(parents=True, exist_ok=True)
        (config_directory / "opencode.json").write_text(
            json.dumps(
                {
                    "$schema": "https://opencode.ai/config.json",
                    "skills": {"urls": [url]},
                }
            )
            + "\n",
            encoding="utf-8",
        )

    def copy_registry(self, destination: Path) -> dict[str, object]:
        index = json.loads((ROOT / "index.json").read_text(encoding="utf-8"))
        destination.mkdir(parents=True)
        shutil.copy2(ROOT / "index.json", destination / "index.json")
        skills = index["skills"]
        self.assertIsInstance(skills, list)
        for skill in skills:
            self.assertIsInstance(skill, dict)
            name = skill["name"]
            for file_name in skill["files"]:
                source = ROOT / name / file_name
                target = destination / name / file_name
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, target)
        return index

    def run_debug_skill(
        self, executable: str, environment: dict[str, str], cwd: Path
    ) -> list[dict[str, object]]:
        result = subprocess.run(
            [executable, "debug", "skill"],
            cwd=cwd,
            env=environment,
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.assertEqual(result.returncode, 0, "opencode debug skill failed")
        try:
            decoded = json.loads(result.stdout)
        except json.JSONDecodeError:
            self.fail("opencode debug skill stdout was not JSON")
        self.assertIsInstance(decoded, list)
        return [entry for entry in decoded if isinstance(entry, dict)]

    def assert_cached_payload_matches(
        self, source_root: Path, cache_skill: Path, index: dict[str, object]
    ) -> None:
        skills = index["skills"]
        assert isinstance(skills, list)
        skill = next(
            entry
            for entry in skills
            if isinstance(entry, dict) and entry.get("name") == SKILL_NAME
        )
        files = skill["files"]
        assert isinstance(files, list)
        for file_name in files:
            assert isinstance(file_name, str)
            self.assertEqual(
                sha256(cache_skill / file_name),
                sha256(source_root / SKILL_NAME / file_name),
                f"cached hash differs for {file_name}",
            )

    def test_local_registry_download_and_atomic_refresh(self) -> None:
        executable = self.require_supported_opencode()
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            served = base / "served"
            working = base / "working"
            working.mkdir()
            index = self.copy_registry(served)
            environment, config_root, cache_root = self.isolated_environment(base / "xdg")

            with serve(served) as server:
                self.write_config(
                    config_root,
                    f"http://127.0.0.1:{server.server_port}/",
                )
                entries = self.run_debug_skill(executable, environment, working)
                matches = [entry for entry in entries if entry.get("name") == SKILL_NAME]
                self.assertEqual(len(matches), 1)
                expected_skill_file = cache_root / "opencode" / "skills" / SKILL_NAME / "SKILL.md"
                self.assertEqual(matches[0].get("location"), str(expected_skill_file))

                cache_skill = expected_skill_file.parent
                self.assertEqual(
                    (cache_skill / ".opencode-version").read_text(encoding="utf-8").strip(),
                    "0.1.0",
                )
                self.assert_cached_payload_matches(served, cache_skill, index)

                marker = "\nAtomic refresh marker.\n"
                served_skill = served / SKILL_NAME / "SKILL.md"
                served_skill.write_text(
                    served_skill.read_text(encoding="utf-8") + marker,
                    encoding="utf-8",
                )
                index["skills"][0]["version"] = "0.1.1"  # type: ignore[index]
                (served / "index.json").write_text(
                    json.dumps(index, indent=2) + "\n", encoding="utf-8"
                )

                refreshed_entries = self.run_debug_skill(executable, environment, working)
                refreshed_matches = [
                    entry for entry in refreshed_entries if entry.get("name") == SKILL_NAME
                ]
                self.assertEqual(len(refreshed_matches), 1)
                self.assertIn(marker.strip(), expected_skill_file.read_text(encoding="utf-8"))
                self.assertEqual(
                    (cache_skill / ".opencode-version").read_text(encoding="utf-8").strip(),
                    "0.1.1",
                )
                self.assertFalse(
                    list(cache_skill.parent.glob(f"{SKILL_NAME}.tmp-*")),
                    "temporary refresh directory remains",
                )
                self.assertFalse(
                    list(cache_skill.parent.glob(f"{SKILL_NAME}.old-*")),
                    "old refresh directory remains",
                )

    def test_external_registry_when_configured(self) -> None:
        registry_url = os.environ.get("REGISTRY_TEST_URL")
        if not registry_url:
            self.skipTest("REGISTRY_TEST_URL is not configured")
        expected_version = os.environ.get("REGISTRY_EXPECTED_VERSION")
        if not expected_version:
            self.fail("REGISTRY_EXPECTED_VERSION is required with REGISTRY_TEST_URL")
        executable = self.require_supported_opencode()

        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            working = base / "working"
            working.mkdir()
            environment, config_root, cache_root = self.isolated_environment(base / "xdg")
            self.write_config(config_root, registry_url)
            entries = self.run_debug_skill(executable, environment, working)
            matches = [entry for entry in entries if entry.get("name") == SKILL_NAME]
            self.assertEqual(len(matches), 1)

            cache_skill = cache_root / "opencode" / "skills" / SKILL_NAME
            self.assertEqual(matches[0].get("location"), str(cache_skill / "SKILL.md"))
            self.assertEqual(
                (cache_skill / ".opencode-version").read_text(encoding="utf-8").strip(),
                expected_version,
            )
            index = json.loads((ROOT / "index.json").read_text(encoding="utf-8"))
            self.assert_cached_payload_matches(ROOT, cache_skill, index)

            research_home = base / "research"
            initializer_environment = environment.copy()
            initializer_environment["RESEARCH_HOME"] = str(research_home)
            result = subprocess.run(
                [
                    sys.executable,
                    str(cache_skill / "scripts" / "init_workspace.py"),
                    "public-endpoint-smoke",
                ],
                cwd=working,
                env=initializer_environment,
                check=False,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            self.assertEqual(result.returncode, 0, "cached initializer failed")
            manifest = json.loads(
                (
                    research_home
                    / "standalone"
                    / "public-endpoint-smoke"
                    / "manifest.json"
                ).read_text(encoding="utf-8")
            )
            self.assertEqual(manifest["schema_version"], 2)


if __name__ == "__main__":
    unittest.main()
