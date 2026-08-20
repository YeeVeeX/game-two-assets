"""Validator for docs/temporal-questions.json — the machine-readable register
of the fifteen banked runtime temporal questions (a)-(o) plus the x0
banking-reversal head, transcribed from the v4-v11 calibration verdicts.

Written BEFORE the register was filled (v12 pre-registration equivalent for a
docs sprint). The register's law: every ``verbatim_condition`` (and every
optional origin/current-register quote) must be a whitespace-normalized
substring of its named source file — prose in the design doc may paraphrase,
the JSON may not. Whitespace normalization collapses every whitespace run
(spaces, newlines, tabs, CR) to a single space on BOTH sides of the match;
every non-whitespace byte must survive verbatim (em-dashes, arrows, minus
signs, markdown markers included).

Fail direction is exercised with synthetic bad registers AND with in-memory
mutations of the real one (paraphrase drift, missing id, duplicate id, bad
source path, bad status, empty capture requirements).
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
REGISTER_PATH = REPO_ROOT / "docs" / "temporal-questions.json"

MANDATORY_IDS = [chr(c) for c in range(ord("a"), ord("o") + 1)] + ["x0"]
QUESTION_STATUSES = {"severity-only", "fusion-question", "banking-reversal-head"}
SECONDARY_STATUS = "recorded-not-measured"
REQUIRED_FIELDS = (
    "id",
    "origin_sprint",
    "source_file",
    "verbatim_condition",
    "status",
    "capture_requirements",
    "adjudication_artifact",
    "routing",
)
# Optional quote pairs: when the first field is present the second must be
# too, and the quote is held to the same normalized-substring law.
OPTIONAL_QUOTE_PAIRS = (
    ("origin_verbatim_condition", "origin_source_file"),
    ("current_register_verbatim", "current_register_file"),
)


def normalize_ws(text: str) -> str:
    """Collapse every whitespace run to a single space (both match sides)."""
    return " ".join(text.split())


def quote_in_file(quote: str, path: Path) -> bool:
    """True when ``quote`` (normalized) is a substring of the normalized file."""
    if not path.is_file():
        return False
    haystack = normalize_ws(path.read_text(encoding="utf-8"))
    needle = normalize_ws(quote)
    return bool(needle) and needle in haystack


def validate_register(register: dict, repo_root: Path) -> list[str]:
    """Return a list of violations (empty == valid)."""
    errors: list[str] = []

    questions = register.get("questions")
    if not isinstance(questions, list) or not questions:
        return ["register.questions missing or empty"]
    secondary = register.get("recorded_not_measured", [])
    if not isinstance(secondary, list):
        errors.append("register.recorded_not_measured must be a list when present")
        secondary = []

    # -- id completeness / uniqueness (global, both sections) ---------------
    q_ids = [item.get("id") for item in questions]
    missing = [i for i in MANDATORY_IDS if i not in q_ids]
    if missing:
        errors.append(f"missing mandatory ids: {missing}")
    unexpected = [i for i in q_ids if i not in MANDATORY_IDS]
    if unexpected:
        errors.append(f"unexpected ids in questions section: {unexpected}")
    all_ids = q_ids + [item.get("id") for item in secondary]
    dupes = sorted({i for i in all_ids if all_ids.count(i) > 1})
    if dupes:
        errors.append(f"duplicate ids: {dupes}")

    # -- per-item schema + quote law ----------------------------------------
    def check_item(item: dict, allowed_statuses: set[str], section: str) -> None:
        item_id = item.get("id", "<missing id>")
        label = f"{section}[{item_id}]"
        for field in REQUIRED_FIELDS:
            if field not in item:
                errors.append(f"{label}: missing field {field!r}")
        if item.get("status") not in allowed_statuses:
            errors.append(
                f"{label}: status {item.get('status')!r} not in {sorted(allowed_statuses)}"
            )
        reqs = item.get("capture_requirements")
        if not isinstance(reqs, list) or not reqs or not all(
            isinstance(r, str) and r.strip() for r in reqs
        ):
            errors.append(f"{label}: capture_requirements must be a non-empty list of strings")
        for text_field in ("origin_sprint", "adjudication_artifact", "routing"):
            value = item.get(text_field)
            if not isinstance(value, str) or not value.strip():
                errors.append(f"{label}: {text_field} must be a non-empty string")

        def check_quote(quote_field: str, path_field: str, required: bool) -> None:
            quote = item.get(quote_field)
            rel = item.get(path_field)
            if quote is None and rel is None:
                if required:
                    errors.append(f"{label}: missing {quote_field}/{path_field}")
                return
            if quote is None or rel is None:
                errors.append(f"{label}: {quote_field} and {path_field} must appear together")
                return
            path = repo_root / rel
            if not path.is_file():
                errors.append(f"{label}: {path_field} does not exist: {rel}")
                return
            if not quote_in_file(quote, path):
                errors.append(
                    f"{label}: {quote_field} is not a whitespace-normalized "
                    f"substring of {rel}"
                )

        check_quote("verbatim_condition", "source_file", required=True)
        for quote_field, path_field in OPTIONAL_QUOTE_PAIRS:
            check_quote(quote_field, path_field, required=False)

    for item in questions:
        check_item(item, QUESTION_STATUSES, "questions")
    for item in secondary:
        check_item(item, {SECONDARY_STATUS}, "recorded_not_measured")

    # -- carry chain (optional top-level): quotes proving (a)-(m) carried ----
    for idx, link in enumerate(register.get("carry_chain", [])):
        rel = link.get("file")
        quote = link.get("verbatim")
        if not rel or not quote:
            errors.append(f"carry_chain[{idx}]: needs file + verbatim")
            continue
        path = repo_root / rel
        if not path.is_file():
            errors.append(f"carry_chain[{idx}]: file does not exist: {rel}")
        elif not quote_in_file(quote, path):
            errors.append(
                f"carry_chain[{idx}]: verbatim is not a whitespace-normalized "
                f"substring of {rel}"
            )

    return errors


def load_register(path: Path = REGISTER_PATH) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


class TestTemporalRegister(unittest.TestCase):
    """PASS direction: the committed register validates against the live repo."""

    def test_register_file_exists_and_parses(self) -> None:
        self.assertTrue(REGISTER_PATH.is_file(), f"missing {REGISTER_PATH}")
        register = load_register()
        self.assertIsInstance(register, dict)

    def test_register_valid(self) -> None:
        errors = validate_register(load_register(), REPO_ROOT)
        self.assertEqual(errors, [], "register violations:\n" + "\n".join(errors))

    def test_all_sixteen_ids_present_once(self) -> None:
        register = load_register()
        ids = [q["id"] for q in register["questions"]]
        self.assertEqual(sorted(ids), sorted(MANDATORY_IDS))
        self.assertEqual(len(ids), 16)


class TestValidatorFailDirections(unittest.TestCase):
    """FAIL direction: the validator must reject bad registers loudly."""

    def _valid(self) -> dict:
        return load_register()

    def test_paraphrased_quote_rejected(self) -> None:
        register = self._valid()
        item = register["questions"][0]
        # Simulate paraphrase drift: same meaning, different bytes.
        item["verbatim_condition"] = (
            "the ready-again beat should still read as an unlock cue at speed"
        )
        errors = validate_register(register, REPO_ROOT)
        self.assertTrue(
            any("whitespace-normalized substring" in e for e in errors),
            f"paraphrase drift not caught: {errors}",
        )

    def test_single_character_drift_rejected(self) -> None:
        register = self._valid()
        item = register["questions"][-1]
        item["verbatim_condition"] = item["verbatim_condition"].replace("0", "O", 1)
        errors = validate_register(register, REPO_ROOT)
        self.assertTrue(any("whitespace-normalized substring" in e for e in errors))

    def test_missing_id_rejected(self) -> None:
        register = self._valid()
        register["questions"] = [q for q in register["questions"] if q["id"] != "n"]
        errors = validate_register(register, REPO_ROOT)
        self.assertTrue(any("missing mandatory ids" in e and "'n'" in e for e in errors))

    def test_duplicate_id_rejected(self) -> None:
        register = self._valid()
        register["questions"].append(dict(register["questions"][0]))
        errors = validate_register(register, REPO_ROOT)
        self.assertTrue(any("duplicate ids" in e for e in errors))

    def test_bad_source_path_rejected(self) -> None:
        register = self._valid()
        register["questions"][2]["source_file"] = "reviews/calibration-v99/verdict.md"
        errors = validate_register(register, REPO_ROOT)
        self.assertTrue(any("does not exist" in e for e in errors))

    def test_bad_status_rejected(self) -> None:
        register = self._valid()
        register["questions"][1]["status"] = "advisory"
        errors = validate_register(register, REPO_ROOT)
        self.assertTrue(any("status" in e for e in errors))

    def test_empty_capture_requirements_rejected(self) -> None:
        register = self._valid()
        register["questions"][3]["capture_requirements"] = []
        errors = validate_register(register, REPO_ROOT)
        self.assertTrue(any("capture_requirements" in e for e in errors))

    def test_secondary_section_status_enforced(self) -> None:
        register = self._valid()
        if not register.get("recorded_not_measured"):
            self.skipTest("no secondary section present")
        register["recorded_not_measured"][0]["status"] = "fusion-question"
        errors = validate_register(register, REPO_ROOT)
        self.assertTrue(any("recorded_not_measured" in e and "status" in e for e in errors))

    def test_synthetic_register_against_synthetic_source(self) -> None:
        # Fully synthetic register + source file in a temp tree: proves the
        # validator's matching is source-driven, not repo-coincidental.
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            src = root / "verdict.md"
            src.write_text(
                "replay capture should verify (z) the synthetic\n"
                "  condition   reads as one event at 60 tps (banked).\n",
                encoding="utf-8",
            )
            item = {
                "id": "a",
                "origin_sprint": "v0",
                "source_file": "verdict.md",
                "verbatim_condition": (
                    "the synthetic condition reads as one event at 60 tps"
                ),
                "status": "fusion-question",
                "capture_requirements": ["r1"],
                "adjudication_artifact": "apng",
                "routing": "none",
            }
            register = {"questions": [item]}
            errors = validate_register(register, root)
            # Only the *missing mandatory ids* complaint may fire — the quote
            # itself (wrapped + double-spaced in the source) must match.
            self.assertFalse(
                any("whitespace-normalized substring" in e for e in errors),
                f"wrapped/multi-space quote should match after normalization: {errors}",
            )
            item["verbatim_condition"] = "a condition nobody wrote"
            errors = validate_register(register, root)
            self.assertTrue(any("whitespace-normalized substring" in e for e in errors))


if __name__ == "__main__":
    unittest.main()
