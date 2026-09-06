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
EXPECTED_OPENCODE_VERSION = "1.18.29"


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


def catalog(index: dict[str, object]) -> dict[str, dict[str, object]]:
    skills = index["skills"]
    assert isinstance(skills, list)
    return {
        str(entry["name"]): entry
        for entry in skills
        if isinstance(entry, dict)
    }


def expected_versions(index: dict[str, object]) -> dict[str, str]:
    return {
        name: str(entry["version"])
        for name, entry in catalog(index).items()
    }


def assert_cached_registry_matches(
    source_root: Path, cache_root: Path, index: dict[str, object]
) -> None:
    for name, entry in catalog(index).items():
        cache_skill = cache_root / "opencode" / "skills" / name
        skill_file = cache_skill / "SKILL.md"
        version_file = cache_skill / ".opencode-version"
        assert skill_file.is_file() and not skill_file.is_symlink(), skill_file
        assert version_file.is_file() and not version_file.is_symlink(), version_file
        assert version_file.read_text(encoding="utf-8").strip() == str(entry["version"])

        files = entry["files"]
        assert isinstance(files, list)
        for file_name in files:
            assert isinstance(file_name, str)
            cached_file = cache_skill / file_name
            assert cached_file.is_file() and not cached_file.is_symlink(), cached_file
            assert sha256(cached_file) == sha256(source_root / name / file_name)


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

    def assert_discovery_matches_catalog(
        self,
        entries: list[dict[str, object]],
        cache_root: Path,
        index: dict[str, object],
    ) -> None:
        for name in catalog(index):
            matches = [entry for entry in entries if entry.get("name") == name]
            self.assertEqual(len(matches), 1, f"expected one discovery match for {name}")
            self.assertEqual(
                matches[0].get("location"),
                str(cache_root / "opencode" / "skills" / name / "SKILL.md"),
            )

    def test_local_registry_download_and_atomic_refresh(self) -> None:
        # A multi-skill registry must download, discover, and atomically refresh by name.
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
                self.assert_discovery_matches_catalog(entries, cache_root, index)
                assert_cached_registry_matches(served, cache_root, index)

                original_versions = expected_versions(index)
                refresh_name = sorted(catalog(index))[0]
                refresh_entry = catalog(index)[refresh_name]
                self.assertEqual(refresh_entry["version"], "0.1.0")
                marker = "\nAtomic refresh marker.\n"
                served_skill = served / refresh_name / "SKILL.md"
                served_skill.write_text(
                    served_skill.read_text(encoding="utf-8") + marker,
                    encoding="utf-8",
                )
                refresh_entry["version"] = "0.1.1"
                updated_versions = dict(original_versions)
                updated_versions[refresh_name] = "0.1.1"
                self.assertEqual(expected_versions(index), updated_versions)
                (served / "index.json").write_text(
                    json.dumps(index, indent=2) + "\n", encoding="utf-8"
                )

                refreshed_entries = self.run_debug_skill(executable, environment, working)
                self.assert_discovery_matches_catalog(refreshed_entries, cache_root, index)
                expected_skill_file = (
                    cache_root / "opencode" / "skills" / refresh_name / "SKILL.md"
                )
                cache_skill = expected_skill_file.parent
                self.assertIn(marker.strip(), expected_skill_file.read_text(encoding="utf-8"))
                self.assertEqual(
                    (cache_skill / ".opencode-version").read_text(encoding="utf-8").strip(),
                    "0.1.1",
                )
                assert_cached_registry_matches(served, cache_root, index)
                self.assertFalse(
                    list(cache_skill.parent.glob(f"{refresh_name}.tmp-*")),
                    "temporary refresh directory remains",
                )
                self.assertFalse(
                    list(cache_skill.parent.glob(f"{refresh_name}.old-*")),
                    "old refresh directory remains",
                )

    def test_external_registry_when_configured(self) -> None:
        # An external registry must expose exactly the locally expected skill catalog.
        registry_url = os.environ.get("REGISTRY_TEST_URL")
        if not registry_url:
            self.skipTest("REGISTRY_TEST_URL is not configured")
        expected_catalog_text = os.environ.get("REGISTRY_EXPECTED_CATALOG")
        if not expected_catalog_text:
            self.fail("REGISTRY_EXPECTED_CATALOG is required with REGISTRY_TEST_URL")
        try:
            expected_catalog = json.loads(expected_catalog_text)
        except json.JSONDecodeError:
            self.fail("REGISTRY_EXPECTED_CATALOG must be valid JSON")
        local_index = json.loads((ROOT / "index.json").read_text(encoding="utf-8"))
        self.assertEqual(expected_catalog, expected_versions(local_index))
        executable = self.require_supported_opencode()

        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            working = base / "working"
            working.mkdir()
            environment, config_root, cache_root = self.isolated_environment(base / "xdg")
            self.write_config(config_root, registry_url)
            entries = self.run_debug_skill(executable, environment, working)
            self.assert_discovery_matches_catalog(entries, cache_root, local_index)
            assert_cached_registry_matches(ROOT, cache_root, local_index)

            research_home = base / "research"
            initializer_environment = environment.copy()
            initializer_environment["RESEARCH_HOME"] = str(research_home)
            research_cache_skill = (
                cache_root / "opencode" / "skills" / "research-workflow"
            )
            result = subprocess.run(
                [
                    sys.executable,
                    str(research_cache_skill / "scripts" / "init_workspace.py"),
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
