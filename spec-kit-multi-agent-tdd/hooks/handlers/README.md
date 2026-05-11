# Hook Handlers

Pre-commit hook handlers for constitutional enforcement of TDD workflow.

## Evidence Gate Enforcer

**File**: `evidence_gate_enforcer.py`

Blocks git commits without valid evidence artifacts. Ensures RED-before-GREEN TDD compliance.

### Hook Type
- **Trigger**: PreToolUse (before Bash tool executes git commit)
- **Condition**: `tool == "Bash" && args.command.contains("git commit")`

### Usage

**Input** (JSON from stdin):
```json
{
  "tool": "Bash",
  "args": {
    "command": "git commit -m 'feat-123: Add feature'"
  },
  "context": {
    "feature_id": "feat-123"
  }
}
```

**Output** (JSON to stdout):
```json
{
  "action": "allow",
  "reason": "All evidence artifacts valid for feat-123",
  "validation_report": {
    "feature_id": "feat-123",
    "valid": true,
    "artifacts": {...},
    "evidence": {...},
    "errors": []
  }
}
```

### Exit Codes
- `0`: Allow commit (all evidence valid)
- `2`: Block commit (missing or invalid evidence)

### Feature ID Extraction

The handler extracts `feature_id` in the following order:

1. **Context** (highest priority): `context.feature_id`
2. **Commit message prefix**: `feat-123: message`
3. **Commit message brackets**: `[feat-123] message`

### Validation

Calls `lib/validate_artifacts.py` to validate:

- Mandatory artifacts exist (test-design, arch-review, code-review, workflow-summary)
- Template sections are present
- RED state timestamp < GREEN state timestamp
- RED and GREEN evidence exists

### Examples

**Allow commit (valid artifacts)**:
```bash
echo '{"tool":"Bash","args":{"command":"git commit -m feat-999"},"context":{"feature_id":"feat-999"}}' | \
  python3 hooks/handlers/evidence_gate_enforcer.py
# Exit code: 0
```

**Block commit (missing artifacts)**:
```bash
echo '{"tool":"Bash","args":{"command":"git commit -m feat-123"},"context":{"feature_id":"feat-123"}}' | \
  python3 hooks/handlers/evidence_gate_enforcer.py
# Exit code: 2
```

**Pass through non-git commands**:
```bash
echo '{"tool":"Bash","args":{"command":"ls -la"},"context":{}}' | \
  python3 hooks/handlers/evidence_gate_enforcer.py
# Exit code: 0 (no validation)
```

### Testing

Run unit tests:
```bash
python3 -m pytest tests/unit/test_evidence_gate_enforcer.py -v
```

All 22 tests should pass.

## TDD Sequence Enforcer

**Status**: Implemented (separate file)

Enforces RED-before-GREEN sequence in TDD workflow.
