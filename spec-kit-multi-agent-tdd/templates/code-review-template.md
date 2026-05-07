# Code Review: {{feature_name}}

**Feature ID:** {{feature_id}}  
**Reviewer:** @review  
**Status:** {{status}}  
**Created:** {{timestamp}}

## Review Scope

_What aspects of the code are being reviewed:_
- [ ] Code quality and readability
- [ ] Test coverage and quality
- [ ] Error handling
- [ ] Performance
- [ ] Security
- [ ] Documentation

## Code Quality Assessment

### Readability & Maintainability
_Is the code easy to understand and maintain?_

**Verdict:** `[APPROVED | CONCERNS | BLOCKED]`

**Details:**
- Naming conventions: `[EXCELLENT | GOOD | NEEDS_WORK]`
- Code complexity: `[LOW | MEDIUM | HIGH]`
- Documentation: `[COMPREHENSIVE | ADEQUATE | INSUFFICIENT]`

### Test Quality
_Are the tests comprehensive and well-written?_

**Test Coverage:**
- Lines covered: _X%_
- Branches covered: _X%_
- Critical paths tested: `[YES | NO]`

**Test Quality:**
- Test clarity: `[EXCELLENT | GOOD | NEEDS_WORK]`
- Test independence: `[YES | NO]`
- Edge cases covered: `[YES | PARTIALLY | NO]`

### Error Handling
_How does the code handle errors and edge cases?_

**Error Handling Assessment:**
- Error paths tested: `[YES | PARTIALLY | NO]`
- Error messages clear: `[YES | NO]`
- Graceful degradation: `[YES | NO]`

## Findings

### Strengths
_What was done well:_
- ✓ _Positive finding 1_
- ✓ _Positive finding 2_

### Concerns
_Issues that should be addressed but don't block merge:_

| ID | File/Line | Concern | Severity | Recommendation |
|----|-----------|---------|----------|----------------|
| C1 | file.py:42 | _description_ | Low/Medium | _suggestion_ |

### Blockers
_Critical issues that must be fixed before merge:_

| ID | File/Line | Blocker | Impact | Required Action |
|----|-----------|---------|--------|-----------------|
| B1 | file.py:123 | _description_ | High | _must do_ |

## Code Smells Detected

_Potential issues to address:_
- [ ] Long functions (>50 lines)
- [ ] Deep nesting (>3 levels)
- [ ] Duplicated code
- [ ] Magic numbers
- [ ] Dead code
- [ ] TODO comments

**Details:**
- _Specific instances with line numbers_

## Security Review

_Security considerations:_
- [ ] Input validation present
- [ ] SQL injection risks mitigated
- [ ] XSS vulnerabilities addressed
- [ ] Authentication/authorization correct
- [ ] Sensitive data handling appropriate

**Issues:** _none | list_

## Performance Review

_Performance considerations:_
- [ ] No N+1 queries
- [ ] Efficient algorithms used
- [ ] Resource cleanup proper
- [ ] No obvious bottlenecks

**Concerns:** _none | list_

## Review Cycle

**Cycle:** {{cycle_number}} / {{max_cycles}}

**Previous Findings:** _(if cycle > 1)_
- _List findings from previous cycle_

**Convergence Check:** _(if enabled)_
- New findings same as previous? `[YES | NO]`
- Action: `[CONTINUE | ESCALATE_DEADLOCK]`

## Decision

**Verdict:** `[APPROVED | REQUEST_CHANGES | BLOCKED]`

**Justification:**
_Explain the verdict and next steps_

**Route:** `[proceed_to_commit | return_to_implementation | escalate]`

---

**Verification Checklist:**
- [ ] All code quality concerns documented
- [ ] Test quality assessed
- [ ] Security reviewed
- [ ] Performance considered
- [ ] Blockers clearly identified
- [ ] Verdict justified
