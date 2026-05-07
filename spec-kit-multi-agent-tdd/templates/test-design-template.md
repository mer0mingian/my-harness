# Test Design: {{feature_name}}

**Feature ID:** {{feature_id}}  
**Agent:** @test  
**Status:** {{status|default("draft")}}  
**Created:** {{timestamp}}

## Test Strategy

_Document the overall testing approach for this feature. Include:_
- Test types to be implemented (unit, integration, e2e)
- Test coverage goals
- Testing tools and frameworks
- Key scenarios to validate

## Acceptance Criteria Mapping

_Map each acceptance criterion from the spec to test cases:_

| Criterion ID | Acceptance Criterion | Test Case(s) | Priority |
|--------------|---------------------|--------------|----------|
| AC-1         | _criterion text_    | _test names_ | High     |

## RED State Validation

_Document the expected RED state before implementation:_

{% if evidence is defined and evidence %}
**Test Output:**
```
Total: {{ evidence.total_tests }} tests
Passed: {{ evidence.passed }}
Failed: {{ evidence.failed }}
Errors: {{ evidence.errors }}
Skipped: {{ evidence.skipped }}
```

**Failure Analysis:**
{% for result in evidence.results %}
{% if result.status == "failed" or result.status == "error" %}
- {{ result.name }} ({{ result.file_path }}{% if result.line_number %}:{{ result.line_number }}{% endif %})
  - Failure code: `{{ result.failure_code }}`
  - Message: {{ result.error_message }}
{% endif %}
{% endfor %}

**Valid RED:** {{ 'YES' if valid_red else 'NO' }}  
**State:** {{ evidence.state }}
{% else %}
**Test Output:**
```
# Paste failing test output here
# Must show valid RED state (MISSING_BEHAVIOR, ASSERTION_MISMATCH)
```

**Failure Analysis:**
- Failure code: `[MISSING_BEHAVIOR | ASSERTION_MISMATCH]`
- Expected behavior: _what should happen_
- Current state: _what actually happens_
- Valid RED: `[YES | NO]`
{% endif %}

## Test Implementation Details

_Technical details about test implementation:_
- Test file locations
- Fixtures/mocks required
- Test data setup
- Dependencies to stub/mock

## Escalations

_Note any blockers, concerns, or architectural questions:_
- [ ] _Issue description_ (assigned to: @agent-name)

## Decision

**Route:** `[implement | escalate]`

**Justification:**
_Explain why tests are ready for implementation OR why escalation is needed_

---

**Verification Checklist:**
- [ ] All acceptance criteria mapped to test cases
- [ ] Tests written and executing
- [ ] Valid RED state confirmed
- [ ] No test framework errors
- [ ] No environment issues
- [ ] Implementation path clear
