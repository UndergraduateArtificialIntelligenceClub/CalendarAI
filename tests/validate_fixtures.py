#!/usr/bin/env python3
"""
Validation script for syllabus evaluation fixtures and parsed syllabus JSON data.
Verifies JSON schema compliance against the Deadline specification:
  - course: non-empty string (e.g. "CMPUT 174")
  - title: non-empty string (e.g. "Assignment 1")
  - date: ISO 8601 string "YYYY-MM-DD" representing a valid calendar date
  - category: one of ["assignment", "lab", "quiz", "midterm", "final", "other"]
  - source_text: non-empty string matching verbatim text from the syllabus
  - weight: float | None (optional, between 0.0 and 100.0)
"""

from __future__ import annotations

import argparse
import datetime
import json
import os
import re
import sys
from pathlib import Path
from typing import Any

# Allowed categories matching backend/models.py and frontend/src/types.ts
ALLOWED_CATEGORIES = {
    "assignment",
    "lab",
    "quiz",
    "midterm",
    "final",
    "other",
}

DATE_REGEX = re.compile(r"^\d{4}-\d{2}-\d{2}$")


class SchemaValidationError(Exception):
    """Raised when syllabus data fails schema compliance."""
    pass


def validate_deadline_dict(
    item: Any,
    item_index: int | None = None,
    syllabus_text: str | None = None,
) -> list[str]:
    """
    Validate a single parsed deadline dictionary against the Deadline schema.
    Returns a list of validation error messages (empty if valid).
    """
    errors: list[str] = []
    prefix = f"Item [{item_index}]: " if item_index is not None else ""

    if not isinstance(item, dict):
        return [f"{prefix}Expected dict, got {type(item).__name__}"]

    # Required fields
    required_fields = ["course", "title", "date", "category", "source_text"]
    for field in required_fields:
        if field not in item:
            errors.append(f"{prefix}Missing required field '{field}'")

    # Validate 'course'
    course = item.get("course")
    if course is not None:
        if not isinstance(course, str) or not course.strip():
            errors.append(f"{prefix}'course' must be a non-empty string, got {course!r}")

    # Validate 'title'
    title = item.get("title")
    if title is not None:
        if not isinstance(title, str) or not title.strip():
            errors.append(f"{prefix}'title' must be a non-empty string, got {title!r}")

    # Validate 'date' (YYYY-MM-DD)
    date_val = item.get("date")
    if date_val is not None:
        if not isinstance(date_val, str) or not DATE_REGEX.match(date_val):
            errors.append(f"{prefix}'date' must be in 'YYYY-MM-DD' format, got {date_val!r}")
        else:
            try:
                datetime.date.fromisoformat(date_val)
            except ValueError as e:
                errors.append(f"{prefix}'date' is not a valid calendar date ({e}): {date_val!r}")

    # Validate 'category'
    category = item.get("category")
    if category is not None:
        if category not in ALLOWED_CATEGORIES:
            errors.append(
                f"{prefix}'category' must be one of {sorted(ALLOWED_CATEGORIES)}, got {category!r}"
            )

    # Validate 'source_text'
    source_text = item.get("source_text")
    if source_text is not None:
        if not isinstance(source_text, str) or not source_text.strip():
            errors.append(f"{prefix}'source_text' must be a non-empty string")
        elif syllabus_text is not None:
            # Check verbatim or normalized presence
            cleaned_source = " ".join(source_text.split())
            cleaned_syllabus = " ".join(syllabus_text.split())
            if cleaned_source not in cleaned_syllabus:
                errors.append(
                    f"{prefix}'source_text' does not appear in syllabus text: {source_text!r}"
                )

    # Validate optional 'weight'
    if "weight" in item and item["weight"] is not None:
        weight = item["weight"]
        if not isinstance(weight, (int, float)):
            errors.append(f"{prefix}'weight' must be a float, int, or None, got {type(weight).__name__}")
        elif weight < 0.0 or weight > 100.0:
            errors.append(f"{prefix}'weight' must be between 0.0 and 100.0, got {weight}")

    return errors


def validate_parsed_data(
    data: Any,
    syllabus_text: str | None = None,
) -> tuple[bool, list[str]]:
    """
    Validate a list of deadline dictionaries.
    Returns (is_valid, error_list).
    """
    if not isinstance(data, list):
        return False, [f"Top-level payload must be a list of deadlines, got {type(data).__name__}"]

    if len(data) == 0:
        return False, ["Deadline list is empty; expected at least one deadline."]

    all_errors: list[str] = []
    total_weight = 0.0
    weights_provided = 0

    for i, item in enumerate(data):
        item_errors = validate_deadline_dict(item, item_index=i, syllabus_text=syllabus_text)
        all_errors.extend(item_errors)
        if isinstance(item, dict) and isinstance(item.get("weight"), (int, float)):
            total_weight += float(item["weight"])
            weights_provided += 1

    if weights_provided > 0 and total_weight > 100.5:
        all_errors.append(f"Sum of explicit deadline weights exceeds 100%: {total_weight:.1f}%")

    # Also validate against Pydantic model if available
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))
        from models import Deadline
        for i, item in enumerate(data):
            if isinstance(item, dict):
                try:
                    Deadline.model_validate(item)
                except Exception as pydantic_err:
                    all_errors.append(f"Pydantic validation error on item [{i}]: {pydantic_err}")
    except (ImportError, TypeError):
        # Python typing differences or pydantic not in path; fallback validator above already ran
        pass

    return len(all_errors) == 0, all_errors


def validate_fixture_directory(fixtures_dir: Path) -> tuple[int, int, list[str]]:
    """
    Validate all syllabus text and expected JSON pairs in a directory.
    Returns (num_passed, num_failed, error_messages).
    """
    txt_files = sorted(fixtures_dir.glob("*.txt"))
    if not txt_files:
        return 0, 0, [f"No .txt syllabus fixtures found in {fixtures_dir}"]

    passed = 0
    failed = 0
    errors: list[str] = []

    print(f"Validating fixtures in {fixtures_dir}...\n")

    for txt_file in txt_files:
        base_name = txt_file.stem
        # Check for both {name}.expected.json and {name}.json
        json_file = fixtures_dir / f"{base_name}.expected.json"
        if not json_file.exists():
            json_file = fixtures_dir / f"{base_name}.json"

        if not json_file.exists():
            failed += 1
            err = f"[FAIL] {txt_file.name}: Missing corresponding expected JSON file ({base_name}.expected.json)"
            print(err)
            errors.append(err)
            continue

        try:
            syllabus_text = txt_file.read_text(encoding="utf-8")
            with open(json_file, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            failed += 1
            err = f"[FAIL] {txt_file.name} / {json_file.name}: File read/JSON parse error: {e}"
            print(err)
            errors.append(err)
            continue

        is_valid, validation_errors = validate_parsed_data(data, syllabus_text=syllabus_text)

        if is_valid:
            passed += 1
            print(f"  [PASS] {txt_file.name} -> {json_file.name} ({len(data)} deadlines verified)")
        else:
            failed += 1
            print(f"  [FAIL] {txt_file.name} -> {json_file.name}:")
            for err in validation_errors:
                print(f"         - {err}")
                errors.append(f"{json_file.name}: {err}")

    return passed, failed, errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate syllabus fixtures and parsed deadline JSON data.")
    parser.add_argument(
        "--fixtures-dir",
        type=Path,
        default=Path(__file__).resolve().parent / "fixtures",
        help="Path to directory containing syllabus fixtures (default: tests/fixtures)",
    )
    parser.add_argument(
        "--file",
        type=Path,
        default=None,
        help="Path to a single JSON file to validate against Deadline schema",
    )
    parser.add_argument(
        "--syllabus",
        type=Path,
        default=None,
        help="Optional path to raw syllabus text to check source_text validity against",
    )

    args = parser.parse_args()

    if args.file:
        if not args.file.exists():
            print(f"Error: file not found: {args.file}", file=sys.stderr)
            return 1
        with open(args.file, "r", encoding="utf-8") as f:
            data = json.load(f)
        syllabus_text = args.syllabus.read_text(encoding="utf-8") if args.syllabus and args.syllabus.exists() else None
        is_valid, errors = validate_parsed_data(data, syllabus_text=syllabus_text)
        if is_valid:
            print(f"Valid! {args.file} conforms to Deadline schema ({len(data)} deadlines).")
            return 0
        else:
            print(f"Invalid {args.file}:", file=sys.stderr)
            for err in errors:
                print(f"  - {err}", file=sys.stderr)
            return 1

    passed, failed, errors = validate_fixture_directory(args.fixtures_dir)
    print(f"\nResult: {passed} passed, {failed} failed.")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
