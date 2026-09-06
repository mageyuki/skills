import json
import re
import unittest
from pathlib import Path

from test_registry import public_privacy_errors


ROOT = Path(__file__).resolve().parents[1]
SKILL_DOCUMENT = ROOT / "intent-discovery/SKILL.md"
CASES = ROOT / "tests/evals/intent-discovery/cases.tsv"
CONVERSATIONS = ROOT / "tests/evals/intent-discovery/conversations.tsv"
RUBRIC = ROOT / "tests/evals/intent-discovery/rubric.txt"
EVALUATION_DOCUMENT = ROOT / "docs/superpowers/evals/2026-09-04-intent-discovery.md"
EXPECTED_CASE_IDS = (
    "control-established-solution-design",
    "control-direct-bugfix",
    "discover-problem-uncertain",
    "discover-target-user-uncertain",
    "discover-value-hypothesis-uncertain",
    "discover-direction-uncertain",
    "discover-three-direction-cap",
    "discover-research-required",
    "discover-research-failure",
    "discover-evidence-resumed-handoff",
    "discover-evidence-resumed-override",
    "discover-no-go",
    "discover-deferred",
    "discover-handoff-ready",
)
EXPECTED_CONVERSATIONS = {
    "question-cadence": (
        "We have six weeks to launch an AI planner for independent consultants. The team has built calendar sync, but we still cannot state which recurring planning problem is worth solving. What should we do next?",
        "We interviewed no users yet. We only know three consultants currently stitch together calendars and spreadsheets; keep going from that context and ask what matters next rather than choosing the product for us.",
    ),
    "research-resumption": (
        "We must choose whether an outage assistant starts with hospital IT or small SaaS teams. We have no comparative evidence about incident frequency, switching cost, or willingness to pilot, and leadership wants a decision today.",
        "Here are the frozen interview findings: nine of ten small SaaS teams report weekly paging pain and seven would pilot; eight hospital IT teams report nine-to-eighteen-month procurement and none will pilot before certification. Resume discovery with this evidence.",
    ),
}
TERMINALS = {
    "HANDOFF_READY",
    "RESEARCH_REQUIRED",
    "NO_GO",
    "DEFERRED",
    "USER_OVERRIDE",
}
BRIEF_FIELDS = {
    "Problem",
    "Target user",
    "Current alternatives",
    "Value hypothesis",
    "Evidence and assumptions",
    "Chosen direction",
    "Non-goals",
    "Open risks",
}


class IntentDiscoveryContractTests(unittest.TestCase):
    def required_text(self, path: Path) -> str:
        self.assertTrue(
            path.is_file() and not path.is_symlink(),
            f"missing required regular file: {path.relative_to(ROOT)}",
        )
        return path.read_text(encoding="utf-8")

    def section(self, text: str, heading: str) -> str:
        match = re.search(
            rf"^## {re.escape(heading)}\s*$\n(.*?)(?=^## |\Z)",
            text,
            re.MULTILINE | re.DOTALL,
        )
        self.assertIsNotNone(match, f"missing section: {heading}")
        assert match is not None
        return match.group(1)

    def tsv_rows(self, path: Path) -> list[tuple[str, ...]]:
        return [
            tuple(line.split("\t"))
            for line in self.required_text(path).splitlines()
        ]

    def test_skill_has_public_identity_and_output_schema(self) -> None:
        # A renamed skill, changed closing state, or missing brief field must fail.
        skill_text = self.required_text(SKILL_DOCUMENT)
        frontmatter = re.match(r"\A---\n(.*?)\n---(?:\n|\Z)", skill_text, re.DOTALL)
        self.assertIsNotNone(frontmatter, "missing YAML frontmatter")
        assert frontmatter is not None
        identity = dict(
            line.split(":", 1)
            for line in frontmatter.group(1).splitlines()
            if ":" in line
        )
        self.assertEqual(identity.get("name", "").strip(), "intent-discovery")

        terminal_section = self.section(skill_text, "Terminal states")
        terminals = re.findall(r"^### ([A-Z_]+)\s*$", terminal_section, re.MULTILINE)
        self.assertEqual(len(terminals), len(TERMINALS))
        self.assertEqual(set(terminals), TERMINALS)

        brief = self.section(skill_text, "Direction brief")
        found_fields = {
            field
            for field in BRIEF_FIELDS
            if re.search(
                rf"^(?:[-*]|\d+\.)\s+(?:\*\*|`)?{re.escape(field)}(?:\*\*|`)?\s*:",
                brief,
                re.MULTILINE,
            )
        }
        self.assertEqual(found_fields, BRIEF_FIELDS)

    def test_public_metadata_has_name_version_and_file_list(self) -> None:
        # Missing, duplicate, or version-skewed registry metadata must fail.
        index = json.loads((ROOT / "index.json").read_text(encoding="utf-8"))
        self.assertEqual(
            [
                entry
                for entry in index["skills"]
                if isinstance(entry, dict) and entry.get("name") == "intent-discovery"
            ],
            [
                {
                    "name": "intent-discovery",
                    "version": "0.1.0",
                    "files": ["SKILL.md"],
                }
            ],
        )

        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        rows = re.findall(r"^\| `intent-discovery` \|.*$", readme, re.MULTILINE)
        self.assertEqual(len(rows), 1)
        columns = [column.strip() for column in rows[0].strip("|").split("|")]
        self.assertEqual(columns[:2], ["`intent-discovery`", "`0.1.0`"])

    def test_cases_preserve_original_coverage_and_usable_columns(self) -> None:
        # A missing case, malformed pressure set, or generator-hint leak must fail.
        rows = self.tsv_rows(CASES)
        self.assertTrue(all(len(row) == 3 for row in rows))
        self.assertEqual(tuple(row[0] for row in rows), EXPECTED_CASE_IDS)
        forbidden = (
            "intent-discovery",
            "expected answer",
            "rubric",
            *(terminal.lower() for terminal in TERMINALS),
            *(case_id.lower() for case_id in EXPECTED_CASE_IDS),
        )
        for case_id, pressures, scenario in rows:
            with self.subTest(case_id=case_id):
                values = pressures.split("+")
                self.assertGreaterEqual(len(values), 3)
                self.assertTrue(all(re.fullmatch(r"[a-z0-9-]+", value) for value in values))
                self.assertEqual(len(values), len(set(values)))
                self.assertTrue(scenario.strip())
                self.assertFalse(any(value in scenario.lower() for value in forbidden))

    def test_conversations_are_fixed_user_turns_only(self) -> None:
        # A fabricated assistant turn or changed follow-up context must fail.
        rows = self.tsv_rows(CONVERSATIONS)
        self.assertTrue(all(len(row) == 3 for row in rows))
        self.assertEqual(
            {row[0]: row[1:] for row in rows},
            EXPECTED_CONVERSATIONS,
        )

    def test_public_evaluation_sources_do_not_leak_private_data(self) -> None:
        # Every present public evaluation artifact must reject private evidence.
        paths = [CASES, CONVERSATIONS, RUBRIC]
        paths.extend(
            path
            for path in (SKILL_DOCUMENT, EVALUATION_DOCUMENT)
            if path.exists()
        )
        for path in paths:
            with self.subTest(path=path.relative_to(ROOT)):
                text = self.required_text(path)
                self.assertEqual(
                    public_privacy_errors(path.relative_to(ROOT).as_posix(), text),
                    [],
                )

    def test_evaluation_report_covers_every_public_fixture(self) -> None:
        # A final report that omits an original case or conversation must fail.
        evaluation_text = self.required_text(EVALUATION_DOCUMENT)
        for fixture_id in (*EXPECTED_CASE_IDS, *EXPECTED_CONVERSATIONS):
            with self.subTest(fixture_id=fixture_id):
                self.assertIn(fixture_id, evaluation_text)


if __name__ == "__main__":
    unittest.main()
