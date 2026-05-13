---
description: "Generate failing tests (RED state) for feature"
agent: matd-qa
tools:
  - 'filesystem/read'
  - 'filesystem/write'
  - 'bash/execute'
scripts:
  validate_red: scripts/validate_red_state.py
  escalate: scripts/escalate_broken_tests.py
exit_codes:
  0: "Success - valid RED state confirmed"
  1: "Validation failure - tests passing (GREEN) or no valid RED failures"
  2: "Escalation required - tests broken (TEST_BROKEN or ENV_BROKEN)"
---

# Test Generation Workflow (Multi-Agent TDD Phase 3)

Spawn @matd-qa agent to write failing tests (RED state) for a feature specification.

## Usage

`/speckit.matd.test $FEATURE_ID [--run-tests] [--allow-non-test-files --justification "reason"]`

**Arguments**:
- `$FEATURE_ID`: Feature identifier (e.g., 'feat-123')
- `--run-tests`: Run tests and validate RED state after generation
- `--allow-non-test-files`: Allow modifications outside test file patterns (requires --justification)
- `--justification`: Reason for bypassing file gate

## Workflow

### 1. Find Spec

Search locations (first found wins):
- `docs/features/${FEATURE_ID}.md`
- `docs/specs/${FEATURE_ID}-spec.md`
- `docs/specs/${FEATURE_ID}.md`
- `.specify/specs/${FEATURE_ID}.md`

❌ **Exit 1** if not found

### 2. Extract Acceptance Criteria

```bash
# Extract AC from spec using inline regex
acceptance_criteria=$(sed -n '/^## Acceptance Criteria/,/^## /p' "$spec_file" | \
  grep -E '^\s*-\s+AC-' | sed 's/^\s*-\s*//')

# Validate at least one AC exists
if [[ -z "$acceptance_criteria" ]]; then
  echo "Error: No acceptance criteria found in spec"
  exit 1
fi
```

### 3. Load Configuration

Load `.specify/harness-tdd-config.yml` or use defaults:
- Agent: `matd-qa`, timeout: 30 minutes
- Test patterns: `tests/**/*.py`, `**/test_*.py`, `**/*_test.py`
- Valid RED codes: `MISSING_BEHAVIOR`, `ASSERTION_MISMATCH`, `AssertionError`, `NameError`, `AttributeError`
- Escalate codes: `TEST_BROKEN`, `ENV_BROKEN`, `SyntaxError`, `ImportError`

### 4. Invoke matd-qa Agent

Build agent context and invoke @matd-qa:

```bash
# Prepare agent context
cat > /tmp/agent-context-${FEATURE_ID}.txt <<EOF
Feature: ${FEATURE_ID}
Spec: ${spec_file}

Acceptance Criteria:
${acceptance_criteria}

File Patterns: ${test_patterns}
Valid RED Codes: MISSING_BEHAVIOR, ASSERTION_MISMATCH

$([[ -n "$bypass_justification" ]] && echo "⚠️ BYPASS ACTIVE: $bypass_justification" || echo "File gate enforced: test files only")

Instructions:
- Write failing tests (RED state) for all AC
- Tests MUST fail with valid RED codes
- NO implementation code
- Timeout: ${agent_timeout} minutes
EOF

# Invoke matd-qa subagent
invoke_subagent matd-qa \
  --context "/tmp/agent-context-${FEATURE_ID}.txt" \
  --mode "red-state" \
  --output "tests/"
```

### 5. Validate RED State (if --run-tests)

```bash
if [[ "$run_tests" == "true" ]]; then
  python3 scripts/validate_red_state.py "${FEATURE_ID}" --project-root .
  
  case $? in
    0) echo "✓ Valid RED state" ;;
    1) echo "✗ Tests passing or no failures"; exit 1 ;;
    2) python3 scripts/escalate_broken_tests.py --file evidence.json; exit 2 ;;
  esac
fi
```

### 6. Generate Test Design Artifact

```bash
# Extract feature name from spec
feature_name=$(grep -m1 '^# ' "$spec_file" | sed 's/^# //')

# Render test-design artifact using SpecKit
specify artifact render test-design \
  --feature-id "$FEATURE_ID" \
  --var "feature_name=$feature_name" \
  --var "acceptance_criteria=$acceptance_criteria" \
  --var "spec_file=$spec_file" \
  --var "timestamp=$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
  --var "status=draft" \
  --var "bypass_info=${bypass_justification:-none}" \
  --template templates/test-design-template.md \
  --output "docs/tests/test-design/${FEATURE_ID}-test-design.md"
```

## Exit Codes

- **0**: Success (agent spawned, artifact created, valid RED if --run-tests)
- **1**: Validation failure (spec not found, no AC, tests GREEN, no valid RED failures)
- **2**: Escalation required (tests broken, system error)

## Configuration

Default `.specify/harness-tdd-config.yml`:

```yaml
agents:
  test_agent: matd-qa
artifacts:
  test_design:
    path: 'docs/tests/test-design/{feature_id}-test-design.md'
test_framework:
  type: pytest
  file_patterns: ['tests/**/*.py', '**/test_*.py', '**/*_test.py']
  failure_codes:
    valid_red: [MISSING_BEHAVIOR, ASSERTION_MISMATCH, AssertionError, NameError, AttributeError]
    invalid_escalate: [TEST_BROKEN, ENV_BROKEN, SyntaxError, ImportError]
```

## Related Commands

- `/speckit.matd.implement` - Implement feature (requires valid RED state)
- `/speckit.matd.review` - Review implementation and tests
- `/speckit.matd.commit` - Validate evidence and create git commit
