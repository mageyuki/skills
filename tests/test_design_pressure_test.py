import json
import re
import unittest
from pathlib import Path

from test_registry import public_privacy_errors


ROOT = Path(__file__).resolve().parents[1]
SKILL_DOCUMENT = ROOT / "design-pressure-test/SKILL.md"
CASES = ROOT / "tests/evals/design-pressure-test/cases.tsv"
RUBRIC = ROOT / "tests/evals/design-pressure-test/rubric.txt"
EVALUATION_DOCUMENT = ROOT / "docs/superpowers/evals/2026-09-04-design-pressure-test.md"
EXPECTED_CASE_IDS = (
    "pressure-clear",
    "pressure-revision-required",
    "pressure-blocked",
    "pressure-explicit-low-risk",
    "pressure-architectural-trigger",
    "pressure-high-risk-trigger",
    "pressure-uncertain-trigger",
    "pressure-no-spec-edit",
    "pressure-no-self-approval",
    "pressure-no-next-process",
)
OUTCOMES = {"CLEAR", "REVISION_REQUIRED", "BLOCKED"}
REPORT_FIELDS = {
    "Outcome",
    "Assumptions tested",
    "Evidence and observations",
    "Consequence",
    "Required revision or blocker",
}


class DesignPressureTestContractTests(unittest.TestCase):
    def required_text(self, path: Path) -> str:
        self.assertTrue(
            path.is_file() and not path.is_symlink(),
            f"missing required regular file: {path.relative_to(ROOT)}",
        )
        return path.read_text(encoding="utf-8")

    def tsv_rows(self, path: Path) -> list[tuple[str, ...]]:
        return [
            tuple(line.split("\t"))
            for line in self.required_text(path).splitlines()
        ]

    def test_skill_has_public_identity_and_report_schema(self) -> None:
        # A renamed skill, invalid outcome, or missing report field must fail.
        skill_text = self.required_text(SKILL_DOCUMENT)
        frontmatter = re.match(r"\A---\n(.*?)\n---(?:\n|\Z)", skill_text, re.DOTALL)
        self.assertIsNotNone(frontmatter, "missing YAML frontmatter")
        assert frontmatter is not None
        identity = dict(
            line.split(":", 1)
            for line in frontmatter.group(1).splitlines()
            if ":" in line
        )
        self.assertEqual(identity.get("name", "").strip(), "design-pressure-test")

        outcomes = re.findall(r"^### ([A-Z][A-Z_]*)\s*$", skill_text, re.MULTILINE)
        self.assertEqual(len(outcomes), len(OUTCOMES))
        self.assertEqual(set(outcomes), OUTCOMES)

        found_fields = {
            field
            for field in REPORT_FIELDS
            if re.search(
                rf"^(?:[-*]|\d+\.)\s+(?:\*\*|`)?{re.escape(field)}(?:\*\*|`)?\s*:",
                skill_text,
                re.MULTILINE,
            )
        }
        self.assertEqual(found_fields, REPORT_FIELDS)

    def test_public_metadata_has_name_version_and_file_list(self) -> None:
        # Missing, duplicate, or version-skewed registry metadata must fail.
        index = json.loads((ROOT / "index.json").read_text(encoding="utf-8"))
        self.assertEqual(
            [
                entry
                for entry in index["skills"]
                if isinstance(entry, dict)
                and entry.get("name") == "design-pressure-test"
            ],
            [
                {
                    "name": "design-pressure-test",
                    "version": "0.1.0",
                    "files": ["SKILL.md"],
                }
            ],
        )

        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        rows = re.findall(r"^\| `design-pressure-test` \|.*$", readme, re.MULTILINE)
        self.assertEqual(len(rows), 1)
        columns = [column.strip() for column in rows[0].strip("|").split("|")]
        self.assertEqual(columns[:2], ["`design-pressure-test`", "`0.1.0`"])

    def test_cases_preserve_approved_coverage_and_usable_columns(self) -> None:
        # A missing case, malformed pressure set, or generator-hint leak must fail.
        rows = self.tsv_rows(CASES)
        self.assertTrue(all(len(row) == 3 for row in rows))
        self.assertEqual(tuple(row[0] for row in rows), EXPECTED_CASE_IDS)
        forbidden = (
            "design-pressure-test",
            "expected answer",
            "rubric",
            *(case_id.lower() for case_id in EXPECTED_CASE_IDS),
            *(
                variant
                for outcome in OUTCOMES
                for variant in (
                    outcome.lower(),
                    outcome.lower().replace("_", " "),
                    outcome.lower().replace("_", "-"),
                )
            ),
        )
        for case_id, pressures, scenario in rows:
            with self.subTest(case_id=case_id):
                values = pressures.split("+")
                self.assertEqual(len(values), 3)
                self.assertTrue(
                    all(re.fullmatch(r"[a-z0-9-]+", value) for value in values)
                )
                self.assertEqual(len(values), len(set(values)))
                self.assertIn("approved", scenario.lower())
                self.assertRegex(scenario, r"(?i)\b(?:design|specification)\b")
                self.assertFalse(any(value in scenario.lower() for value in forbidden))

    def test_canonical_rubric_has_outcome_and_report_schema(self) -> None:
        # A rubric that cannot score the public response contract must fail.
        rubric_text = self.required_text(RUBRIC)
        self.assertEqual(
            set(re.findall(r"\b(?:CLEAR|REVISION_REQUIRED|BLOCKED)\b", rubric_text)),
            OUTCOMES,
        )
        for field in REPORT_FIELDS:
            with self.subTest(field=field):
                self.assertRegex(rubric_text, rf"(?m)^- {re.escape(field)}:")
        self.assertIn("INCONCLUSIVE", rubric_text)

    def test_public_evaluation_sources_do_not_leak_private_data(self) -> None:
        # Every present public evaluation artifact must reject private evidence.
        paths = [CASES, RUBRIC]
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

    def test_evaluation_report_covers_every_public_fixture_and_outcome(self) -> None:
        # A final report that omits a case or allowed product outcome must fail.
        evaluation_text = self.required_text(EVALUATION_DOCUMENT)
        for value in (*EXPECTED_CASE_IDS, *sorted(OUTCOMES)):
            with self.subTest(value=value):
                self.assertIn(value, evaluation_text)


if __name__ == "__main__":
    unittest.main()
