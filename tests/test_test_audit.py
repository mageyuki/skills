import re
import unittest
from pathlib import Path

from test_registry import load_index


ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = ROOT / "test-audit"
# A pointer into one project's tree dangles once the skill is installed elsewhere.
PROJECT_FILE_REFERENCE = re.compile(r"`(?:tests|integrations|scripts|src|Makefile)\b[^`]*`")
PROJECT_FILE_NAME = re.compile(r"`[\w./-]+\.(?:py|mjs|js|ts|sh)`")
HOST_ROLE = re.compile(r"\b(?:Controller|Workers?)\b")
PINNED_SOURCE = re.compile(
    r"https://github\.com/(?:openclaw/openclaw|anomalyco/opencode)/blob/[0-9a-f]{40}/"
)


class TestAuditContractTests(unittest.TestCase):
    def payload(self) -> dict[str, str]:
        entry = next(
            skill for skill in load_index(ROOT)["skills"] if skill["name"] == "test-audit"
        )
        return {
            name: (SKILL_ROOT / name).read_text(encoding="utf-8")
            for name in entry["files"]
        }

    def test_reference_files_are_reachable_from_skill(self) -> None:
        # An unlinked reference is shipped but never loaded by a consuming agent.
        payload = self.payload()
        for name in set(payload) - {"SKILL.md"}:
            self.assertIn(f"({name})", payload["SKILL.md"], name)

    def test_payload_stands_alone_in_any_project(self) -> None:
        # Installers do not have the source project's files, runner or roles.
        for name, text in self.payload().items():
            for pattern in (PROJECT_FILE_REFERENCE, PROJECT_FILE_NAME, HOST_ROLE):
                self.assertEqual(pattern.findall(text), [], f"{name}: {pattern.pattern}")

    def test_adapted_guidance_keeps_pinned_attribution(self) -> None:
        # Moving source links lose which upstream revision the criteria came from.
        for name, text in self.payload().items():
            self.assertRegex(text, PINNED_SOURCE, name)


if __name__ == "__main__":
    unittest.main()
