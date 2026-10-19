#!/usr/bin/env python3
"""
Evaluation Runner for Syllabus Deadlines Parser.

Sends each syllabus in tests/fixtures to POST /parse, compares against the
hand-written ground truth expected deadlines, and computes performance scores.

Usage:
    # Run evaluation against a running backend server:
    python backend/eval/run_eval.py

    # Run in mock mode (simulates perfect parser matching expected fixtures):
    python backend/eval/run_eval.py --mock

    # Run schema validation only on fixtures:
    python backend/eval/run_eval.py --validate-only
"""

from __future__ import annotations

import argparse
import difflib
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

# Ensure tests/ directory is on sys.path to import validate_parsed_data
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR / "tests"))

try:
    from validate_fixtures import validate_parsed_data
except ImportError:
    # Fallback if invoked from another location
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from validate_fixtures import validate_parsed_data  # type: ignore


def normalize_title(title: str) -> str:
    """Normalize deadline title for fuzzy comparison."""
    return "".join(c.lower() for c in title if c.isalnum())


def match_deadlines(
    predicted: list[dict[str, Any]],
    expected: list[dict[str, Any]],
) -> dict[str, Any]:
    """
    Compare predicted deadlines against expected ground truth deadlines.
    Matches primarily by title/category and date.
    Returns scoring metrics for the syllabus.
    """
    matched_expected = set()
    matched_predicted = set()
    correct_dates = 0
    correct_categories = 0
    correct_weights = 0
    date_mismatches: list[dict[str, str]] = []

    # Attempt exact matches first
    for p_idx, p in enumerate(predicted):
        p_title_norm = normalize_title(p.get("title", ""))
        for e_idx, e in enumerate(expected):
            if e_idx in matched_expected:
                continue
            e_title_norm = normalize_title(e.get("title", ""))
            
            # Check title similarity
            similarity = difflib.SequenceMatcher(None, p_title_norm, e_title_norm).ratio()
            if similarity >= 0.7 or p_title_norm in e_title_norm or e_title_norm in p_title_norm:
                matched_expected.add(e_idx)
                matched_predicted.add(p_idx)

                # Check date match
                p_date = p.get("date")
                e_date = e.get("date")
                if p_date == e_date:
                    correct_dates += 1
                else:
                    date_mismatches.append({
                        "item": e.get("title", "Unknown"),
                        "expected": str(e_date),
                        "predicted": str(p_date),
                    })

                # Check category match
                if p.get("category") == e.get("category"):
                    correct_categories += 1

                # Check weight match
                p_weight = p.get("weight")
                e_weight = e.get("weight")
                if (p_weight is None and e_weight is None) or (
                    p_weight is not None and e_weight is not None and abs(float(p_weight) - float(e_weight)) < 0.1
                ):
                    correct_weights += 1
                break

    tp = len(matched_expected)
    fp = len(predicted) - len(matched_predicted)
    fn = len(expected) - len(matched_expected)

    precision = tp / len(predicted) if predicted else 0.0
    recall = tp / len(expected) if expected else 0.0
    f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
    date_accuracy = (correct_dates / tp) if tp > 0 else 0.0

    return {
        "expected_count": len(expected),
        "predicted_count": len(predicted),
        "true_positives": tp,
        "false_positives": fp,
        "false_negatives": fn,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "correct_dates": correct_dates,
        "date_accuracy": date_accuracy,
        "correct_categories": correct_categories,
        "correct_weights": correct_weights,
        "date_mismatches": date_mismatches,
    }


def call_parse_endpoint(url: str, text: str, timeout: int = 30) -> list[dict[str, Any]]:
    """Send syllabus text to POST /parse and parse JSON response."""
    payload = json.dumps({"text": text}).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        if resp.status != 200:
            raise RuntimeError(f"HTTP {resp.status}: {resp.read().decode('utf-8')}")
        return json.loads(resp.read().decode("utf-8"))


def run_evaluation(
    fixtures_dir: Path,
    api_url: str,
    mock: bool = False,
    validate_only: bool = False,
) -> int:
    """Run evaluation harness across all syllabus fixtures."""
    txt_files = sorted(fixtures_dir.glob("*.txt"))
    if not txt_files:
        print(f"Error: No .txt fixtures found in {fixtures_dir}", file=sys.stderr)
        return 1

    print("=" * 72)
    print("COHORT SYLLABUS PARSER EVALUATION HARNESS")
    print(f"Fixtures: {fixtures_dir}")
    print(f"Endpoint: {api_url} {'(MOCK MODE)' if mock else ''}")
    print("=" * 72)

    total_expected = 0
    total_predicted = 0
    total_tp = 0
    total_fp = 0
    total_fn = 0
    total_correct_dates = 0

    results: list[dict[str, Any]] = []

    for txt_file in txt_files:
        base_name = txt_file.stem
        json_file = fixtures_dir / f"{base_name}.expected.json"
        if not json_file.exists():
            json_file = fixtures_dir / f"{base_name}.json"

        if not json_file.exists():
            print(f"[SKIP] {txt_file.name}: No expected JSON found.")
            continue

        syllabus_text = txt_file.read_text(encoding="utf-8")
        with open(json_file, "r", encoding="utf-8") as f:
            expected_data = json.load(f)

        # Validate ground truth schema
        is_valid, errors = validate_parsed_data(expected_data, syllabus_text=syllabus_text)
        if not is_valid:
            print(f"[ERROR] Ground truth in {json_file.name} failed schema validation:")
            for err in errors:
                print(f"  - {err}")
            return 1

        if validate_only:
            print(f"[VALID] {base_name}: Schema compliant ({len(expected_data)} deadlines)")
            continue

        # Obtain parsed predictions
        if mock:
            predicted_data = expected_data
        else:
            try:
                predicted_data = call_parse_endpoint(api_url, syllabus_text)
            except urllib.error.URLError as e:
                print(
                    f"\n[ERROR] Unable to connect to backend at {api_url}: {e}\n"
                    "Hint: Start the backend server (`uvicorn main:app --reload`), or pass `--mock` to test evaluation scoring logic.",
                    file=sys.stderr,
                )
                return 2
            except Exception as e:
                print(f"[FAIL] {base_name}: Error during /parse call: {e}", file=sys.stderr)
                return 1

        # Validate predicted schema compliance
        pred_valid, pred_errors = validate_parsed_data(predicted_data, syllabus_text=syllabus_text)
        if not pred_valid:
            print(f"[WARN] {base_name}: Predictions failed schema validation:")
            for err in pred_errors:
                print(f"       - {err}")

        # Compute metrics
        metrics = match_deadlines(predicted_data, expected_data)
        metrics["name"] = base_name
        metrics["schema_valid"] = pred_valid
        results.append(metrics)

        total_expected += metrics["expected_count"]
        total_predicted += metrics["predicted_count"]
        total_tp += metrics["true_positives"]
        total_fp += metrics["false_positives"]
        total_fn += metrics["false_negatives"]
        total_correct_dates += metrics["correct_dates"]

    if validate_only:
        print(f"\nAll {len(txt_files)} syllabus fixtures verified successfully.")
        return 0

    # Print summary table
    print("\n" + "-" * 72)
    print(f"{'Syllabus':<25} {'Expected':<10} {'Found':<8} {'Matched':<10} {'Date Acc':<10} {'F1':<8}")
    print("-" * 72)
    for r in results:
        date_acc_str = f"{r['date_accuracy'] * 100:.1f}%"
        f1_str = f"{r['f1']:.2f}"
        print(
            f"{r['name']:<25} {r['expected_count']:<10} {r['predicted_count']:<8} "
            f"{r['true_positives']:<10} {date_acc_str:<10} {f1_str:<8}"
        )
        if r["date_mismatches"]:
            for mm in r["date_mismatches"]:
                print(f"   -> Date mismatch on '{mm['item']}': expected {mm['expected']}, got {mm['predicted']}")

    overall_prec = total_tp / total_predicted if total_predicted > 0 else 0.0
    overall_rec = total_tp / total_expected if total_expected > 0 else 0.0
    overall_f1 = (2 * overall_prec * overall_rec) / (overall_prec + overall_rec) if (overall_prec + overall_rec) > 0 else 0.0
    overall_date_acc = (total_correct_dates / total_tp) if total_tp > 0 else 0.0

    print("-" * 72)
    print(f"{'OVERALL TOTALS':<25} {total_expected:<10} {total_predicted:<8} {total_tp:<10} {overall_date_acc * 100:.1f}%    {overall_f1:.2f}")
    print("=" * 72)
    print(f"Overall Precision: {overall_prec * 100:.1f}%")
    print(f"Overall Recall:    {overall_rec * 100:.1f}%")
    print(f"Overall F1 Score:  {overall_f1:.2f}")
    print(f"Date Accuracy:     {overall_date_acc * 100:.1f}%")
    print("=" * 72)

    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate syllabus parser against test set fixtures.")
    parser.add_argument(
        "--fixtures-dir",
        type=Path,
        default=ROOT_DIR / "tests" / "fixtures",
        help="Path to syllabus fixtures directory (default: tests/fixtures)",
    )
    parser.add_argument(
        "--api-url",
        type=str,
        default="http://localhost:8000/parse",
        help="URL of the POST /parse backend endpoint (default: http://localhost:8000/parse)",
    )
    parser.add_argument(
        "--mock",
        action="store_true",
        help="Run eval using fixture expected output to demonstrate eval metrics without a running backend",
    )
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Only validate fixture schema compliance without invoking an endpoint",
    )

    args = parser.parse_args()
    return run_evaluation(
        fixtures_dir=args.fixtures_dir,
        api_url=args.api_url,
        mock=args.mock,
        validate_only=args.validate_only,
    )


if __name__ == "__main__":
    sys.exit(main())
