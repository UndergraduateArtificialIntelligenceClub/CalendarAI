"""
Unit test verifying all syllabus fixtures pass schema compliance.
Runs with pytest or python -m unittest.
"""

from __future__ import annotations

import unittest
from pathlib import Path

from validate_fixtures import validate_fixture_directory


class TestSyllabusFixtures(unittest.TestCase):
    def test_fixtures_schema_compliance(self):
        fixtures_dir = Path(__file__).resolve().parent / "fixtures"
        passed, failed, errors = validate_fixture_directory(fixtures_dir)
        self.assertGreater(passed, 0, "No syllabus fixtures were validated")
        self.assertEqual(
            failed,
            0,
            f"Fixture validation failed with {failed} errors:\n" + "\n".join(errors),
        )


if __name__ == "__main__":
    unittest.main()
