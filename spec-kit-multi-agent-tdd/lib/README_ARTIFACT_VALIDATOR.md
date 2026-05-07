# Artifact Validator

Validates TDD workflow artifacts for completeness, structure, and TDD compliance.

## Purpose

The artifact validator automates Step 10 (commit) validation by checking:
- All mandatory artifacts exist
- Each artifact has required sections/headers
- Evidence timestamps show RED before GREEN (TDD compliance)
- Both RED and GREEN state evidence is documented

## Usage

### Basic Validation

```bash
python lib/validate_artifacts.py feat-123
```

### Specify Artifacts Directory

```bash
python lib/validate_artifacts.py feat-123 --artifacts-dir ./custom_artifacts
```

### Verbose Output

```bash
python lib/validate_artifacts.py feat-123 --verbose
```

### JSON Output

```bash
python lib/validate_artifacts.py feat-123 --format json
```

## Exit Codes

- **0**: All validations passed
- **1**: Validation failures (missing artifacts or malformed structure)
- **2**: Critical error (can't read files, etc.)

## Validated Artifacts

### Mandatory Artifacts

1. **Test Design** (`feat-123-test-design.md`)
   - Required sections: Test Design, Test Strategy, Acceptance Criteria Mapping, RED State Validation, Escalations, Decision

2. **Architecture Review** (`feat-123-arch-review.md`)
   - Required sections: Architecture Review, Architecture Assessment, Findings, Decision

3. **Code Review** (`feat-123-code-review.md`)
   - Required sections: Code Review, Code Quality Assessment, Findings, Decision

4. **Workflow Summary** (`feat-123-workflow-summary.md`)
   - Required sections: Workflow Summary, Workflow Overview, Artifact Trail, Implementation Summary, Quality Assurance, Commit Information

### Optional Artifacts

- **Implementation Notes** (`feat-123-implementation-notes.md`)

## TDD Compliance Checks

The validator enforces TDD methodology by verifying:

### 1. Timestamp Validation

Extracts and compares timestamps from workflow summary:
```
RED State Timestamp: 2024-01-15T10:30:00Z
GREEN State Timestamp: 2024-01-15T11:45:00Z
```

**Requirement**: RED timestamp MUST be before GREEN timestamp.

### 2. Evidence Validation

Checks for presence of both RED and GREEN state evidence:

**RED State Indicators:**
- "RED State:"
- "RED State Timestamp:"
- "MISSING_BEHAVIOR"
- "ASSERTION_MISMATCH"

**GREEN State Indicators:**
- "GREEN State:"
- "GREEN State Timestamp:"
- "All tests passing"
- "tests passing"

## Example Output

### Valid Artifacts

```
============================================================
Artifact Validation Report: feat-123
============================================================

Status: ✓ VALID

============================================================
```

### Invalid Artifacts

```
============================================================
Artifact Validation Report: feat-123
============================================================

Status: ✗ INVALID

Artifacts:
  ✗ test_design: MISSING
  ✓ arch_review: exists ✓ structure
  ✓ code_review: exists ✓ structure
  ✗ workflow_summary: exists ✗ structure
    Missing: Quality Assurance

Evidence:
  ✗ RED/GREEN transition
  ✗ Timestamps: RED state timestamp not found

Errors:
  - Mandatory artifact missing: test_design
  - workflow_summary missing sections: Quality Assurance
  - Evidence validation failed: RED state evidence missing
  - Timestamp validation failed: RED state timestamp not found

============================================================
```

### JSON Format

```json
{
  "feature_id": "feat-123",
  "valid": true,
  "artifacts": {
    "test_design": {
      "exists": true,
      "valid_structure": true,
      "missing_sections": []
    },
    "arch_review": {
      "exists": true,
      "valid_structure": true,
      "missing_sections": []
    },
    "code_review": {
      "exists": true,
      "valid_structure": true,
      "missing_sections": []
    },
    "workflow_summary": {
      "exists": true,
      "valid_structure": true,
      "missing_sections": []
    }
  },
  "evidence": {
    "red_green_transition": true,
    "timestamps_valid": true,
    "message": "RED (2024-01-15T10:30:00Z) before GREEN (2024-01-15T11:45:00Z)"
  },
  "errors": []
}
```

## Integration with Workflow

The validator should be run in Step 10 (Commit & Document) before creating the commit:

1. All agents complete their tasks (Steps 7-9)
2. Orchestrator runs validator: `validate_artifacts.py feat-123`
3. If validation passes (exit code 0), proceed with commit
4. If validation fails (exit code 1), review errors and fix artifacts
5. If critical error (exit code 2), investigate filesystem/permission issues

## Testing

Run the test suite:

```bash
cd /path/to/spec-kit-multi-agent-tdd
source .venv/bin/activate
python -m pytest tests/test_validate_artifacts.py -v
```

Generate test artifacts:

```bash
# Create test artifacts directory
mkdir -p test_artifacts

# Generate artifacts using templates
python lib/generate_artifact.py test-design-template feat-test "Test Feature" --output test_artifacts/feat-test-test-design.md --force
python lib/generate_artifact.py arch-review-template feat-test "Test Feature" --output test_artifacts/feat-test-arch-review.md --force
python lib/generate_artifact.py code-review-template feat-test "Test Feature" --output test_artifacts/feat-test-code-review.md --force
python lib/generate_artifact.py workflow-summary-template feat-test "Test Feature" --output test_artifacts/feat-test-workflow-summary.md --force

# Add timestamps to workflow summary
# Edit test_artifacts/feat-test-workflow-summary.md and add under Quality Assurance:
# **Test Evidence:**
# - RED State Timestamp: 2024-01-15T10:30:00Z
# - GREEN State Timestamp: 2024-01-15T11:45:00Z
# - RED State: MISSING_BEHAVIOR confirmed
# - GREEN State: All tests passing

# Validate
python lib/validate_artifacts.py feat-test --artifacts-dir test_artifacts --verbose
```

## Implementation Details

### Section Detection

The validator uses regex patterns to match section headers:
- Markdown headers: `# Section` or `## Section`
- Bold text: `**Section:**` or `**Section**`
- Word boundary matching for plain text

### Timestamp Parsing

Timestamps are extracted using regex and parsed as ISO 8601 format:
- Pattern: `YYYY-MM-DDTHH:MM:SSZ` or `YYYY-MM-DDTHH:MM:SS±HH:MM`
- Comparison uses datetime objects for accurate ordering

### Error Reporting

All validation errors are collected and reported together:
- Missing mandatory artifacts
- Malformed structure (missing sections)
- Invalid evidence (missing RED/GREEN states)
- Invalid timestamps (GREEN before RED)

## Time Savings

This automation saves approximately **3 hours** of manual artifact validation per feature before PR review.
