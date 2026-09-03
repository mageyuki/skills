from __future__ import annotations

import json
import os
import re
import subprocess
import tempfile
import unittest
from pathlib import Path, PurePosixPath


ROOT = Path(__file__).resolve().parents[1]
SEMVER = re.compile(r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$")
SAFE_NAME = re.compile(r"^[A-Za-z0-9._-]+$")

_PRIVATE_MARKERS = (
    ("private mageyuki home path", "/home/mageyuki"),
    ("private repository identity", "mageyuki/opencode-config"),
    ("service state filename", "service.json"),
    ("private controller policy", "OpenCode is the sole Controller"),
    ("private implementation lane", "implementer-architectural"),
    ("private review lane", "reviewer-critical"),
)
_PRIVATE_PATTERNS = (
    ("user-specific absolute home path", re.compile(r"/(?:home|Users)/[^/\s]+/")),
    (
        "authorization bearer credential literal",
        re.compile(r"Authorization\s*:\s*Bearer\s+\S+", re.IGNORECASE),
    ),
    ("GitHub fine-grained credential literal", re.compile(r"github_pat_[A-Za-z0-9_]{20,}")),
    ("GitHub credential literal", re.compile(r"gh[pousr]_[A-Za-z0-9]{20,}")),
    ("API credential literal", re.compile(r"sk-[A-Za-z0-9]{16,}")),
    (
        "PEM private-key header",
        re.compile(r"-----BEGIN (?:[A-Z0-9]+ )*PRIVATE KEY-----"),
    ),
)
_MARKDOWN_LINK = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")


def load_index(root: Path) -> dict[str, object]:
    value = json.loads((root / "index.json").read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("index root must be an object")
    return value


def listed_payload(root: Path, name: str, files: list[str]) -> set[Path]:
    return {root / name / PurePosixPath(file_name) for file_name in files}


def _is_ignored_bytecode(root: Path, path: Path) -> bool:
    relative = path.relative_to(root)
    looks_like_bytecode = "__pycache__" in relative.parts or path.suffix in {
        ".pyc",
        ".pyo",
    }
    if not looks_like_bytecode:
        return False
    result = subprocess.run(
        ["git", "-C", str(root), "check-ignore", "-q", "--", relative.as_posix()],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    return result.returncode == 0


def actual_payload(root: Path, name: str) -> set[Path]:
    skill_root = root / name
    if not skill_root.exists() and not skill_root.is_symlink():
        return set()

    payload: set[Path] = set()
    for directory, directory_names, file_names in os.walk(skill_root, followlinks=False):
        current = Path(directory)
        for directory_name in list(directory_names):
            path = current / directory_name
            if path.is_symlink():
                payload.add(path)
                directory_names.remove(directory_name)
            elif _is_ignored_bytecode(root, path):
                directory_names.remove(directory_name)
        for file_name in file_names:
            path = current / file_name
            if not _is_ignored_bytecode(root, path):
                payload.add(path)
    return payload


def _safe_name(name: object) -> bool:
    return (
        isinstance(name, str)
        and name not in {"", ".", ".."}
        and "\x00" not in name
        and "\\" not in name
        and "/" not in name
        and SAFE_NAME.fullmatch(name) is not None
    )


def _safe_file_path(file_name: object) -> bool:
    if not isinstance(file_name, str):
        return False
    if "\x00" in file_name or "\\" in file_name:
        return False
    parts = file_name.split("/")
    if any(part in {"", ".", ".."} for part in parts):
        return False
    return not PurePosixPath(file_name).is_absolute()


def _frontmatter(text: str) -> dict[str, str]:
    lines = text.splitlines()
    if not lines or lines[0] != "---":
        return {}
    try:
        end = lines.index("---", 1)
    except ValueError:
        return {}

    values: dict[str, str] = {}
    for line in lines[1:end]:
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        values[key.strip()] = value.strip().strip("'\"")
    return values


def _path_has_symlink(skill_root: Path, file_name: str) -> bool:
    current = skill_root
    for part in file_name.split("/"):
        current = current / part
        if current.is_symlink():
            return True
    return False


def _relative_link_errors(skill_root: Path, path: Path, text: str) -> list[str]:
    errors: list[str] = []
    resolved_skill_root = skill_root.resolve()
    for match in _MARKDOWN_LINK.finditer(text):
        raw_target = match.group(1).strip()
        if raw_target.startswith("<") and raw_target.endswith(">"):
            raw_target = raw_target[1:-1]
        target = raw_target.split("#", 1)[0].split("?", 1)[0]
        if (
            not target
            or target.startswith(('/', '#'))
            or re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:", target)
        ):
            continue
        resolved = (path.parent / target).resolve()
        try:
            resolved.relative_to(resolved_skill_root)
        except ValueError:
            errors.append(
                f"escaping relative Markdown link in {path.relative_to(skill_root.parent)}"
            )
            continue
        if not resolved.exists():
            errors.append(
                f"unresolved relative Markdown link in {path.relative_to(skill_root.parent)}"
            )
    return errors


def _git_show(root: Path, revision: str, relative_path: str) -> bytes | None:
    result = subprocess.run(
        ["git", "-C", str(root), "show", f"{revision}:{relative_path}"],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    return result.stdout if result.returncode == 0 else None


def _version_errors(
    root: Path,
    base_revision: str,
    current_skills: list[dict[str, object]],
) -> list[str]:
    if not base_revision or re.fullmatch(r"0+", base_revision):
        return []
    old_index_bytes = _git_show(root, base_revision, "index.json")
    if old_index_bytes is None:
        return []
    try:
        old_index = json.loads(old_index_bytes.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return ["base index is malformed"]
    if not isinstance(old_index, dict) or not isinstance(old_index.get("skills"), list):
        return ["base index is malformed"]

    old_by_name = {
        skill.get("name"): skill
        for skill in old_index["skills"]
        if isinstance(skill, dict) and isinstance(skill.get("name"), str)
    }
    errors: list[str] = []
    for current in current_skills:
        name = current.get("name")
        if not _safe_name(name) or name not in old_by_name:
            continue
        old = old_by_name[name]
        old_files = old.get("files")
        current_files = current.get("files")
        changed = old_files != current_files
        old_safe_files = {
            file_name
            for file_name in old_files if _safe_file_path(file_name)
        } if isinstance(old_files, list) else set()
        current_safe_files = {
            file_name
            for file_name in current_files if _safe_file_path(file_name)
        } if isinstance(current_files, list) else set()
        for file_name in old_safe_files | current_safe_files:
            old_bytes = _git_show(root, base_revision, f"{name}/{file_name}")
            current_path = root / str(name) / PurePosixPath(file_name)
            current_bytes = (
                current_path.read_bytes()
                if current_path.is_file() and not _path_has_symlink(root / str(name), file_name)
                else None
            )
            if old_bytes != current_bytes:
                changed = True
        if changed and old.get("version") == current.get("version"):
            errors.append(f"payload changed without version change: {name}")
    return errors


def validate_registry(root: Path, base_revision: str | None = None) -> list[str]:
    errors: list[str] = []
    try:
        index = load_index(root)
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError):
        return ["malformed index.json"]

    if set(index) != {"skills"}:
        errors.append("index keys must be exactly: skills")
    skills = index.get("skills")
    if not isinstance(skills, list):
        return errors + ["skills must be a list"]

    seen_names: set[str] = set()
    current_skills: list[dict[str, object]] = []
    for position, skill in enumerate(skills):
        if not isinstance(skill, dict):
            errors.append(f"skill entry {position} must be an object")
            continue
        current_skills.append(skill)
        if set(skill) != {"name", "version", "files"}:
            errors.append(f"skill entry {position} keys must be exactly: files, name, version")

        name = skill.get("name")
        if not _safe_name(name):
            errors.append(f"unsafe skill name at entry {position}")
            continue
        assert isinstance(name, str)
        if name in seen_names:
            errors.append(f"duplicate skill name: {name}")
        seen_names.add(name)

        version = skill.get("version")
        if not isinstance(version, str) or SEMVER.fullmatch(version) is None:
            errors.append(f"invalid semantic version for {name}")

        files = skill.get("files")
        if not isinstance(files, list):
            errors.append(f"files must be a list for {name}")
            continue

        safe_files: list[str] = []
        seen_files: set[str] = set()
        for file_name in files:
            if not _safe_file_path(file_name):
                errors.append(f"unsafe file path for {name}")
                continue
            assert isinstance(file_name, str)
            if file_name in seen_files:
                errors.append(f"duplicate file path for {name}: {file_name}")
                continue
            seen_files.add(file_name)
            safe_files.append(file_name)
        if "SKILL.md" not in files:
            errors.append(f"missing SKILL.md listing for {name}")

        skill_root = root / name
        if skill_root.is_symlink():
            errors.append(f"symlink in served skill tree: {name}")
            continue
        if not skill_root.is_dir():
            errors.append(f"missing skill directory: {name}")
            continue

        for file_name in safe_files:
            path = skill_root / PurePosixPath(file_name)
            if _path_has_symlink(skill_root, file_name):
                errors.append(f"symlink in served skill tree: {name}/{file_name}")
            if not path.is_file():
                errors.append(f"missing listed file: {name}/{file_name}")

        listed = listed_payload(root, name, safe_files)
        actual = actual_payload(root, name)
        for path in sorted(actual):
            if path.is_symlink():
                errors.append(f"symlink in served skill tree: {path.relative_to(root)}")
        for path in sorted(actual - listed):
            errors.append(f"unlisted payload file: {path.relative_to(root)}")
        for path in sorted(listed - actual):
            errors.append(f"listed payload is not a regular file: {path.relative_to(root)}")

        skill_file = skill_root / "SKILL.md"
        if skill_file.is_file() and not skill_file.is_symlink():
            try:
                frontmatter = _frontmatter(skill_file.read_text(encoding="utf-8"))
            except UnicodeError:
                errors.append(f"non-UTF-8 payload file: {name}/SKILL.md")
            else:
                if frontmatter.get("name") != name:
                    errors.append(f"frontmatter name mismatch for {name}")
                description = frontmatter.get("description", "")
                if not description.startswith("Use when ") or not description[9:].strip():
                    errors.append(f"missing or non-actionable description for {name}")

        for path in sorted(actual | listed):
            if not path.is_file() or path.is_symlink():
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeError:
                errors.append(f"non-UTF-8 payload file: {path.relative_to(root)}")
                continue
            relative = path.relative_to(root)
            for category, marker in _PRIVATE_MARKERS:
                if marker in text:
                    errors.append(f"{category} in {relative}")
            for category, pattern in _PRIVATE_PATTERNS:
                if pattern.search(text):
                    errors.append(f"{category} in {relative}")
            if path.suffix.lower() == ".md":
                errors.extend(_relative_link_errors(skill_root, path, text))

    comparison_base = base_revision or os.environ.get("REGISTRY_BASE_SHA")
    if comparison_base:
        errors.extend(_version_errors(root, comparison_base, current_skills))
    return errors


class RegistryContractTests(unittest.TestCase):
    def make_registry(
        self,
        *,
        skill_text: str | None = None,
        files: list[str] | None = None,
        version: str = "0.1.0",
    ) -> Path:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name)
        (root / "research-workflow").mkdir()
        (root / "research-workflow" / "SKILL.md").write_text(
            skill_text
            or "---\nname: research-workflow\ndescription: Use when a research question needs evidence.\n---\n",
            encoding="utf-8",
        )
        self.write_index(
            root,
            {
                "skills": [
                    {
                        "name": "research-workflow",
                        "version": version,
                        "files": files if files is not None else ["SKILL.md"],
                    }
                ]
            },
        )
        return root

    def write_index(self, root: Path, index: object) -> None:
        (root / "index.json").write_text(
            json.dumps(index, indent=2) + "\n", encoding="utf-8"
        )

    def assert_error_category(self, root: Path, category: str) -> None:
        errors = validate_registry(root)
        self.assertTrue(
            any(category in error for error in errors),
            msg=f"expected error category {category!r}; got categories {errors!r}",
        )

    def test_live_registry_contract(self) -> None:
        self.assertEqual(
            validate_registry(ROOT, os.environ.get("REGISTRY_BASE_SHA")), []
        )

    def test_main_push_uses_event_before_sha_as_registry_base(self) -> None:
        workflow_lines = (ROOT / ".github" / "workflows" / "ci.yml").read_text(
            encoding="utf-8"
        ).splitlines()
        run_index = workflow_lines.index("        run: |")
        step_start = max(
            index
            for index, line in enumerate(workflow_lines[:run_index])
            if line.startswith("      - ")
        )

        before_sha = "1234567890abcdef1234567890abcdef12345678"
        context = {"github.event.before": before_sha}
        step_environment: dict[str, str] = {}
        for index in range(step_start, run_index):
            if workflow_lines[index] != "        env:":
                continue
            for line in workflow_lines[index + 1 : run_index]:
                if not line.startswith("          "):
                    break
                key, raw_value = line.strip().split(":", 1)
                expression = re.fullmatch(
                    r"\$\{\{\s*([^}]+?)\s*\}\}", raw_value.strip()
                )
                if expression and expression.group(1) in context:
                    step_environment[key] = context[expression.group(1)]

        script_lines: list[str] = []
        for line in workflow_lines[run_index + 1 :]:
            if not line.startswith("          "):
                break
            script_lines.append(line[10:])
        script = "\n".join(script_lines)

        with tempfile.TemporaryDirectory() as temporary:
            temporary_root = Path(temporary)
            capture = temporary_root / "registry-base"
            fake_bin = temporary_root / "bin"
            fake_bin.mkdir()
            fake_python = fake_bin / "python3"
            fake_python.write_text(
                "#!/bin/sh\n"
                "set -eu\n"
                'printf "%s" "$REGISTRY_BASE_SHA" > "$CAPTURE_PATH"\n',
                encoding="utf-8",
            )
            fake_python.chmod(0o755)

            environment = os.environ.copy()
            environment.pop("GITHUB_EVENT_BEFORE", None)
            environment.pop("PUSH_BEFORE_SHA", None)
            environment.update(
                {
                    "CAPTURE_PATH": str(capture),
                    "GITHUB_REF_NAME": "main",
                    "PATH": f"{fake_bin}{os.pathsep}{environment['PATH']}",
                    **step_environment,
                }
            )
            result = subprocess.run(
                [
                    "bash",
                    "--noprofile",
                    "--norc",
                    "-eu",
                    "-o",
                    "pipefail",
                    "-c",
                    script,
                ],
                cwd=ROOT,
                env=environment,
                check=False,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(capture.read_text(encoding="utf-8"), before_sha)

    def test_payload_change_requires_version_change(self) -> None:
        root = self.make_registry()
        subprocess.run(["git", "init", "-b", "main", str(root)], check=True, stdout=subprocess.DEVNULL)
        subprocess.run(["git", "-C", str(root), "config", "user.name", "Registry Test"], check=True)
        subprocess.run(["git", "-C", str(root), "config", "user.email", "registry@example.invalid"], check=True)
        subprocess.run(["git", "-C", str(root), "add", "."], check=True)
        subprocess.run(["git", "-C", str(root), "commit", "-m", "initial"], check=True, stdout=subprocess.DEVNULL)
        base = subprocess.run(
            ["git", "-C", str(root), "rev-parse", "HEAD"],
            check=True,
            text=True,
            stdout=subprocess.PIPE,
        ).stdout.strip()

        skill_file = root / "research-workflow" / "SKILL.md"
        skill_file.write_text(skill_file.read_text(encoding="utf-8") + "\nChanged.\n", encoding="utf-8")
        subprocess.run(["git", "-C", str(root), "add", "."], check=True)
        subprocess.run(["git", "-C", str(root), "commit", "-m", "payload change"], check=True, stdout=subprocess.DEVNULL)
        self.assertTrue(
            any(
                "payload changed without version change" in error
                for error in validate_registry(root, base)
            )
        )

        self.write_index(
            root,
            {
                "skills": [
                    {
                        "name": "research-workflow",
                        "version": "0.1.1",
                        "files": ["SKILL.md"],
                    }
                ]
            },
        )
        self.assertFalse(
            any(
                "payload changed without version change" in error
                for error in validate_registry(root, base)
            )
        )

    def test_malformed_json_is_rejected(self) -> None:
        root = self.make_registry()
        (root / "index.json").write_text("{", encoding="utf-8")
        self.assert_error_category(root, "malformed index.json")

    def test_index_and_skill_keys_are_closed(self) -> None:
        root = self.make_registry()
        index = load_index(root)
        index["extra"] = True
        self.write_index(root, index)
        self.assert_error_category(root, "index keys")

        del index["extra"]
        skills = index["skills"]
        assert isinstance(skills, list) and isinstance(skills[0], dict)
        skills[0]["extra"] = True
        self.write_index(root, index)
        self.assert_error_category(root, "skill entry 0 keys")

    def test_invalid_semantic_versions_are_rejected(self) -> None:
        for version in ("1", "1.0", "01.0.0", "1.0.0-beta", "v1.0.0"):
            with self.subTest(version=version):
                self.assert_error_category(
                    self.make_registry(version=version), "invalid semantic version"
                )

    def test_duplicate_skill_names_are_rejected(self) -> None:
        root = self.make_registry()
        index = load_index(root)
        skills = index["skills"]
        assert isinstance(skills, list)
        skills.append(dict(skills[0]))
        self.write_index(root, index)
        self.assert_error_category(root, "duplicate skill name")

    def test_unsafe_skill_names_are_rejected_before_path_use(self) -> None:
        for name in ("", ".", "..", "/", "foo/bar", "foo\\bar", "bad\x00name"):
            with self.subTest(label=repr(name)):
                root = self.make_registry()
                index = load_index(root)
                skills = index["skills"]
                assert isinstance(skills, list) and isinstance(skills[0], dict)
                skills[0]["name"] = name
                self.write_index(root, index)
                self.assert_error_category(root, "unsafe skill name")

    def test_unsafe_file_paths_are_rejected_before_path_use(self) -> None:
        paths = (
            "",
            ".",
            "./SKILL.md",
            "foo//SKILL.md",
            "foo/../SKILL.md",
            "..",
            "../SKILL.md",
            "foo/bar/..",
            "/abs",
            "C:\\abs",
            "bad\x00path",
        )
        for file_name in paths:
            with self.subTest(label=repr(file_name)):
                root = self.make_registry(files=["SKILL.md", file_name])
                self.assert_error_category(root, "unsafe file path")

    def test_duplicate_and_missing_file_paths_are_rejected(self) -> None:
        self.assert_error_category(
            self.make_registry(files=["SKILL.md", "SKILL.md"]),
            "duplicate file path",
        )
        self.assert_error_category(
            self.make_registry(files=["SKILL.md", "missing.md"]),
            "missing listed file",
        )

    def test_skill_listing_requires_skill_file(self) -> None:
        self.assert_error_category(
            self.make_registry(files=[]), "missing SKILL.md listing"
        )

    def test_unlisted_payload_file_is_rejected(self) -> None:
        root = self.make_registry()
        (root / "research-workflow" / "extra.md").write_text("extra\n", encoding="utf-8")
        self.assert_error_category(root, "unlisted payload file")

    def test_frontmatter_identity_and_actionable_description_are_required(self) -> None:
        self.assert_error_category(
            self.make_registry(
                skill_text="---\nname: another-skill\ndescription: Use when evidence is needed.\n---\n"
            ),
            "frontmatter name mismatch",
        )
        for description_line in ("", "description: Research process."):
            with self.subTest(description=description_line):
                text = "---\nname: research-workflow\n" + description_line + "\n---\n"
                self.assert_error_category(
                    self.make_registry(skill_text=text),
                    "missing or non-actionable description",
                )

    def test_relative_markdown_links_must_resolve_inside_skill(self) -> None:
        self.assert_error_category(
            self.make_registry(
                skill_text="---\nname: research-workflow\ndescription: Use when evidence is needed.\n---\n[missing](references/missing.md)\n"
            ),
            "unresolved relative Markdown link",
        )
        root = self.make_registry(
            skill_text="---\nname: research-workflow\ndescription: Use when evidence is needed.\n---\n[outside](../outside.md)\n"
        )
        (root / "outside.md").write_text("outside\n", encoding="utf-8")
        self.assert_error_category(root, "escaping relative Markdown link")

    def test_file_and_directory_symlinks_are_rejected(self) -> None:
        root = self.make_registry(files=["SKILL.md", "linked.md"])
        outside = root / "outside.md"
        outside.write_text("outside\n", encoding="utf-8")
        (root / "research-workflow" / "linked.md").symlink_to(outside)
        self.assert_error_category(root, "symlink in served skill tree")

        root = self.make_registry()
        outside_directory = root / "outside"
        outside_directory.mkdir()
        (root / "research-workflow" / "linked-directory").symlink_to(
            outside_directory, target_is_directory=True
        )
        self.assert_error_category(root, "symlink in served skill tree")

    def test_skill_directory_symlink_is_not_traversed(self) -> None:
        root = self.make_registry()
        skill_root = root / "research-workflow"
        outside = root / "outside-skill"
        skill_root.rename(outside)
        (outside / "SKILL.md").write_text(
            "---\nname: research-workflow\ndescription: Use when evidence is needed.\n---\n"
            + "Authorization: "
            + "Bearer "
            + "outside-value\n",
            encoding="utf-8",
        )
        skill_root.symlink_to(outside, target_is_directory=True)

        errors = validate_registry(root)
        self.assertTrue(any("symlink in served skill tree" in error for error in errors))
        self.assertFalse(any("credential literal" in error for error in errors))

    def test_untracked_ignored_bytecode_is_not_payload(self) -> None:
        root = self.make_registry()
        (root / ".gitignore").write_text("__pycache__/\n*.py[cod]\n.coverage\n", encoding="utf-8")
        subprocess.run(["git", "init", "-b", "main", str(root)], check=True, stdout=subprocess.DEVNULL)
        cache = root / "research-workflow" / "__pycache__"
        cache.mkdir()
        (cache / "module.pyc").write_bytes(b"untracked bytecode")
        self.assertEqual(validate_registry(root), [])

    def test_tracked_ignored_bytecode_is_still_payload(self) -> None:
        root = self.make_registry()
        (root / ".gitignore").write_text("__pycache__/\n*.py[cod]\n.coverage\n", encoding="utf-8")
        subprocess.run(["git", "init", "-b", "main", str(root)], check=True, stdout=subprocess.DEVNULL)
        cache = root / "research-workflow" / "__pycache__"
        cache.mkdir()
        bytecode = cache / "module.pyc"
        bytecode.write_bytes(b"tracked bytecode")
        subprocess.run(
            ["git", "-C", str(root), "add", "-f", "--", str(bytecode.relative_to(root))],
            check=True,
        )
        self.assert_error_category(root, "unlisted payload file")

    def test_private_policy_markers_are_rejected_without_echoing_values(self) -> None:
        markers = (
            "/home/" + "mageyuki/private",
            "mageyuki/" + "opencode-config",
            "service" + ".json",
            "OpenCode is the sole " + "Controller",
            "implementer-" + "architectural",
            "reviewer-" + "critical",
            "/Users/" + "someone/private",
        )
        for marker in markers:
            with self.subTest(marker_kind=marker.split("/")[0]):
                root = self.make_registry()
                (root / "research-workflow" / "SKILL.md").write_text(
                    "---\nname: research-workflow\ndescription: Use when evidence is needed.\n---\n"
                    + marker
                    + "\n",
                    encoding="utf-8",
                )
                errors = validate_registry(root)
                self.assertTrue(any(" in research-workflow/SKILL.md" in error for error in errors))
                self.assertTrue(all(marker not in error for error in errors))

    def test_credential_literal_categories_are_rejected_without_echoing_values(self) -> None:
        literals = (
            "Authorization: " + "Bearer " + "example-token-value",
            "github_" + "pat_" + "A" * 20,
            "gh" + "p_" + "B" * 20,
            "s" + "k-" + "C" * 16,
            "-----BEGIN " + "PRIVATE KEY-----",
        )
        for literal in literals:
            with self.subTest(literal_kind=literal[:2]):
                root = self.make_registry()
                (root / "research-workflow" / "SKILL.md").write_text(
                    "---\nname: research-workflow\ndescription: Use when evidence is needed.\n---\n"
                    + literal
                    + "\n",
                    encoding="utf-8",
                )
                errors = validate_registry(root)
                self.assertTrue(any("credential literal" in error or "private-key" in error for error in errors))
                self.assertTrue(all(literal not in error for error in errors))

    def test_malformed_field_types_are_rejected(self) -> None:
        root = self.make_registry()
        for value, category in (
            ([], "malformed index.json"),
            ({"skills": {}}, "skills must be a list"),
            ({"skills": [None]}, "must be an object"),
            (
                {"skills": [{"name": "research-workflow", "version": "0.1.0", "files": {}}]},
                "files must be a list",
            ),
        ):
            with self.subTest(category=category):
                self.write_index(root, value)
                self.assert_error_category(root, category)


if __name__ == "__main__":
    unittest.main()
