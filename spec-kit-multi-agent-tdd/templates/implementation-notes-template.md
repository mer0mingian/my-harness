# Implementation Notes: {{feature_name}}

**Feature ID:** {{feature_id}}  
**Agent:** {{agent_name}}  
**Status:** {{status|default("draft")}}  
**Created:** {{timestamp}}

## Implementation Summary

_High-level overview of what was implemented:_
- Key components modified/created
- Architectural approach taken
- Design patterns applied

## Implementation Details

### Files Changed
- `path/to/file1.py` - _description of changes_
- `path/to/file2.py` - _description of changes_

### Key Decisions
_Document important implementation decisions:_

**Decision 1:** _Decision title_
- **Context:** _Why this decision was needed_
- **Options considered:** _Alternatives evaluated_
- **Chosen approach:** _What was implemented_
- **Rationale:** _Why this approach was best_

### Code Structure
_Describe the code organization:_
- Class/module structure
- Function responsibilities
- Data flow

## RED→GREEN Evidence

This section documents the complete TDD cycle for test-driven development verification.

### RED State (Initial/Before Implementation)

**Test Failure Output:**
```
# Paste failing test output here (before implementation)
# Show test names, error messages, assertion failures
```

**Failed Tests:**
- [ ] Test name(s) that failed in RED state
- [ ] Expected failures per test-design

### GREEN State (After Implementation)

**Test Passing Output:**
```
# Paste passing test output here (after implementation)
# All tests from test-design must pass
```

**Test Results Summary:**
- Total tests: _X_
- Passing: _X_
- Coverage percentage: _X%_

### Evidence Verification

- [ ] RED state tests match test-design expectations
- [ ] GREEN state: all tests passing
- [ ] No test skips or xfails in final state
- [ ] Coverage meets or exceeds baseline
- [ ] Test execution time acceptable

## Refactoring

_Document refactoring activities performed during the implementation:_

### Code Cleanup
- [ ] Item description: _what was refactored and why_

### Optimization Work
- [ ] Item description: _performance improvements, simplifications_

### Code Quality Improvements
- [ ] Item description: _style, readability, maintainability enhancements_

**Note:** Refactoring was driven by test feedback and occurred during GREEN state development.

## Integration Validation

_Verification that the implementation integrates properly with existing codebase:_

### System Integration Tests
- [ ] Tested with existing feature X: _outcome_
- [ ] Tested with existing feature Y: _outcome_
- [ ] No breaking changes to public APIs
- [ ] Backward compatibility verified: _yes/no/n.a._

### Cross-Module Validation
- [ ] Dependencies properly declared
- [ ] Import paths verified
- [ ] Configuration changes compatible with existing setup
- [ ] Database migrations (if any) tested: _description_

### Runtime Integration
- [ ] Startup/initialization behavior verified
- [ ] Error handling for edge cases
- [ ] Logging/monitoring integration complete
- [ ] Performance impact assessment: _negligible/acceptable/needs review_

## Technical Debt / Future Work

_Note any shortcuts taken or follow-up work needed:_
- [ ] _Item description_ (priority: low/medium/high)

## Escalations

_Any issues requiring architectural review or decisions:_
- [ ] _Issue description_ (assigned to: @agent-name)

## Decision

**Route:** `[review | escalate]`

**Justification:**
_Explain why implementation is ready for review OR why escalation is needed_

---

**Verification Checklist:**
- [ ] All tests passing (GREEN state)
- [ ] Code follows project conventions
- [ ] No commented-out code or debug statements
- [ ] Documentation updated (if applicable)
- [ ] No breaking changes to existing APIs
- [ ] Ready for code review
