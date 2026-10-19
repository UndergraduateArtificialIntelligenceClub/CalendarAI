# Syllabus Parser Evaluation Harness

This directory contains evaluation tools to benchmark and validate the LLM parser against ground-truth syllabus test cases. It allows measuring whether prompt modifications, temperature changes, or model upgrades improve or degrade deadline extraction accuracy.

## Test Set Fixtures

Ground truth fixtures live in [`tests/fixtures/`](../../tests/fixtures/). Each test case consists of:
1. `<course>_<format>.txt`: An anonymized plain text syllabus representing common University of Alberta course outline styles.
2. `<course>_<format>.expected.json`: Hand-annotated expected deadlines conforming to the `Deadline` schema in [`backend/models.py`](../models.py).

### Included Test Cases
- `cmput174_table`: Markdown/ASCII table format with assessment components and exam dates.
- `cmput272_paragraph`: Prose/paragraph format with inline problem set and midterm schedules.
- `math125_odd_dates`: Non-standard date phrasing (e.g., "Week 7", "Oct. 3rd", "3/10 into the semester").
- `stat252_mixed`: Bullet list combining computer labs, midterm exam, and a project deadline.
- `engl102_schedule`: Chronological weekly schedule tracking essays, drafts, peer review, and portfolio submissions.

### Privacy Policy & Redaction Notice
In accordance with repository guidelines for public repositories:
- All personal instructor details, emails, office numbers, and TA contact information have been redacted or replaced with anonymized placeholders (`[Department Staff]`, `[cs-undergrad-advising@ualberta.ca]`).
- Only publicly distributable course outline descriptions and schedule structures are included. If adding new syllabi containing unredacted private contact information, add them to `.gitignore` or share them internally on Discord instead of committing raw personal data.

---

## Running the Evaluation

### 1. Validate Fixtures Schema Compliance
To verify that all fixtures comply with the `Deadline` Pydantic model and that `source_text` snippets exist verbatim in syllabus text:

```bash
# Direct fixture validation
python tests/validate_fixtures.py

# Or via eval runner
python backend/eval/run_eval.py --validate-only
```

### 2. Run Evaluation Against Live `/parse` Endpoint
When the backend server is running (implementing `POST /parse`):

```bash
# Start backend in a separate terminal
uvicorn backend.main:app --reload

# Run evaluation against default endpoint (http://localhost:8000/parse)
python backend/eval/run_eval.py

# Or specify a custom backend URL
python backend/eval/run_eval.py --api-url http://127.0.0.1:8000/parse
```

### 3. Run in Mock Mode
To verify the evaluation scoring and reporting logic without spinning up an active backend server:

```bash
python backend/eval/run_eval.py --mock
```

---

## Evaluation Metrics

The script outputs a summary table reporting:
- **Expected**: Total number of human-annotated deadlines in ground truth.
- **Found**: Total deadlines returned by parser.
- **Matched (TP)**: Correctly identified deadlines (matched on title/topic and category).
- **Date Accuracy**: Percentage of matched deadlines that have the exact expected ISO `YYYY-MM-DD` date.
- **Precision / Recall / F1**: Comprehensive retrieval accuracy metrics.
- **Date Mismatches**: Specific itemized discrepancies when dates differ.
