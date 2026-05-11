# Test Evidence Parser

Automated parser for pytest output that extracts structured RED/GREEN state with failure classification codes. Used for TDD workflow gates (Steps 7, 8, 10).

## Features

- Parses pytest output (from stdin or file)
- Classifies failures into 4 codes:
  - `MISSING_BEHAVIOR` - Expected TDD failure (not implemented)
  - `ASSERTION_MISMATCH` - Expected TDD failure (assertion failed)
  - `TEST_BROKEN` - Invalid failure (test code broken)
  - `ENV_BROKEN` - Invalid failure (environment issue)
- Detects RED vs GREEN vs BROKEN state
- Extracts test counts, failure locations, error messages
- Outputs structured JSON or human-readable summary
- Exit codes: 0 (GREEN), 1 (RED), 2 (BROKEN)

## Installation

Requirements are already in `requirements.txt`:
```bash
# From spec-kit-multi-agent-tdd/
uv pip install -r requirements.txt
```

## Usage

### Basic Usage (stdin)

```bash
# Run tests and pipe to parser
pytest tests/ | python lib/parse_test_evidence.py

# With summary format
pytest tests/ | python lib/parse_test_evidence.py --format summary
```

### From File

```bash
# Parse saved pytest output
python lib/parse_test_evidence.py --input test_output.txt

# JSON output (default)
python lib/parse_test_evidence.py --input test_output.txt --format json

# Human-readable summary
python lib/parse_test_evidence.py --input test_output.txt --format summary
```

### With Custom Patterns

```bash
python lib/parse_test_evidence.py --patterns custom-patterns.yml
```

## Exit Codes

The parser returns different exit codes based on test state:

- `0` - GREEN (all tests pass)
- `1` - RED (valid TDD failures: MISSING_BEHAVIOR or ASSERTION_MISMATCH)
- `2` - BROKEN (invalid failures: TEST_BROKEN or ENV_BROKEN)
- `3` - Error (parsing failed or other error)

### Using Exit Codes in Scripts

```bash
# Capture exit code
pytest tests/ | python lib/parse_test_evidence.py
TEST_STATE=$?

if [ $TEST_STATE -eq 0 ]; then
    echo "Tests are GREEN - ready to proceed"
elif [ $TEST_STATE -eq 1 ]; then
    echo "Tests are RED - expected TDD state"
elif [ $TEST_STATE -eq 2 ]; then
    echo "Tests are BROKEN - escalate to human"
else
    echo "Parser error"
fi
```

## Output Formats

### JSON Format (default)

```json
{
  "state": "RED",
  "total_tests": 3,
  "passed": 1,
  "failed": 1,
  "errors": 1,
  "skipped": 0,
  "results": [
    {
      "name": "test_login",
      "status": "passed",
      "failure_code": null,
      "error_message": null,
      "file_path": "tests/test_auth.py",
      "line_number": null
    },
    {
      "name": "test_logout",
      "status": "failed",
      "failure_code": "ASSERTION_MISMATCH",
      "error_message": "AssertionError: assert False == True",
      "file_path": "tests/test_auth.py",
      "line_number": 15
    },
    {
      "name": "test_create_user",
      "status": "error",
      "failure_code": "ENV_BROKEN",
      "error_message": "ModuleNotFoundError: No module named 'api.users'",
      "file_path": "tests/test_api.py",
      "line_number": 5
    }
  ],
  "summary": "3 tests: 1 passed, 1 failed, 1 error (state: BROKEN)"
}
```

### Summary Format

```
============================================================
TEST EVIDENCE SUMMARY
============================================================
State: RED
Total Tests: 2
  Passed: 1
  Failed: 1
  Errors: 0
  Skipped: 0

Test Results:
------------------------------------------------------------
✗ test_login (failed) - MISSING_BEHAVIOR
  Error: NotImplementedError: login function not implemented
  Location: tests/test_auth.py:10

✓ test_logout (passed)
  Location: tests/test_auth.py

============================================================
2 tests: 1 passed, 1 failed (state: RED)
============================================================
```

## Failure Classification

### Valid RED States (Expected in TDD)

**MISSING_BEHAVIOR**
- `NotImplementedError`
- "not implemented" messages
- Abstract methods
- Functions with no implementation

**ASSERTION_MISMATCH**
- `AssertionError`
- "assert failed" messages
- "expected X but got Y" messages

### Invalid RED States (Escalate to Human)

**TEST_BROKEN**
- `SyntaxError`
- `IndentationError`
- `NameError`
- `ImportError` in test code
- `AttributeError` in test code

**ENV_BROKEN**
- `ModuleNotFoundError`
- Connection refused errors
- Permission denied errors
- File not found errors
- Timeout errors

## Configuration

Failure classification patterns are defined in `config/test-patterns.yml`:

```yaml
failure_codes:
  MISSING_BEHAVIOR:
    - "(?i)not implemented"
    - "(?i)notimplementederror"
    # ...
  
  ASSERTION_MISMATCH:
    - "(?i)assert.*failed"
    - "(?i)assertionerror"
    # ...
  
  TEST_BROKEN:
    - "(?i)syntaxerror"
    - "(?i)nameerror"
    # ...
  
  ENV_BROKEN:
    - "(?i)modulenotfounderror"
    - "(?i)connection.*refused"
    # ...
```

### Custom Patterns

Create a custom patterns file and pass it with `--patterns`:

```bash
python lib/parse_test_evidence.py --patterns my-patterns.yml
```

## Integration with TDD Workflow

### Step 7: Verify RED State

```bash
# Run tests and verify RED with valid failure code
pytest tests/ | python lib/parse_test_evidence.py --format summary

# Check exit code
if [ $? -eq 1 ]; then
    echo "✓ Tests are RED (expected)"
elif [ $? -eq 2 ]; then
    echo "✗ Tests are BROKEN (escalate)"
    exit 1
fi
```

### Step 8: Verify RED→GREEN Transition

```bash
# Save before state
pytest tests/ | python lib/parse_test_evidence.py > before.json

# Implement feature
# ...

# Verify GREEN state
pytest tests/ | python lib/parse_test_evidence.py --format summary

if [ $? -eq 0 ]; then
    echo "✓ Tests are GREEN (transition successful)"
else
    echo "✗ Tests are not GREEN"
    exit 1
fi
```

### Step 10: Commit with Evidence

```bash
# Generate evidence report
pytest tests/ | python lib/parse_test_evidence.py --format summary > test_evidence.txt

# Include in commit message
git commit -m "feat: implement login

Test Evidence:
$(cat test_evidence.txt)
"
```

## Testing

Run the parser's own tests:

```bash
# From spec-kit-multi-agent-tdd/
python -m pytest tests/test_parse_test_evidence.py -v
```

Test with sample fixtures:

```bash
# GREEN state
python lib/parse_test_evidence.py --input tests/fixtures/pytest_green.txt

# RED state (MISSING_BEHAVIOR)
python lib/parse_test_evidence.py --input tests/fixtures/pytest_red_missing_behavior.txt

# BROKEN state (ENV_BROKEN)
python lib/parse_test_evidence.py --input tests/fixtures/pytest_broken_env.txt
```

## Troubleshooting

### Parser Returns Empty Results

Check that pytest output format matches expected patterns. Run with `-v` to see more details:

```bash
pytest tests/ -v | python lib/parse_test_evidence.py
```

### Failure Classification Wrong

Check the patterns in `config/test-patterns.yml` and update as needed. You can also create a custom patterns file.

### Parser Errors

Enable debug output:

```bash
pytest tests/ | python lib/parse_test_evidence.py 2>&1 | tee debug.log
```

## Architecture

The parser consists of:

1. **Data Classes** (`TestResult`, `TestEvidence`)
   - Structured representation of test results and evidence

2. **Pattern Matching** (`classify_failure`)
   - Regex-based failure classification using patterns from YAML

3. **State Detection** (`detect_state`)
   - Logic for determining RED/GREEN/BROKEN state

4. **Parser** (`parse_pytest_output`)
   - Main parsing logic for pytest output
   - Handles multiple pytest output formats
   - Extracts test results, error messages, locations

5. **CLI** (`main`)
   - Argument parsing
   - Input/output handling
   - Exit code management

## Time Savings

This parser saves approximately 4 hours of manual test output analysis across 3 workflow executions by:

- Automating failure classification
- Providing structured evidence for gates
- Enabling scriptable workflow validation
- Reducing manual inspection of test outputs
