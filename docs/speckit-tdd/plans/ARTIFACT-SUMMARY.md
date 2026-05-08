# Artifact Summary: Multi-Agent TDD Workflow

**Version:** 1.0  
**Date:** 2026-05-07

This document summarizes all artifacts in the Multi-Agent TDD Workflow system, their purposes, and configuration.

---

## Artifact Overview

| Artifact | Mandatory | Step | Agent | Path Template |
|----------|-----------|------|-------|---------------|
| Test Design | ✅ Yes | 7 | @test | `docs/tests/test-design/{feature_id}-test-design.md` |
| Implementation Notes | ❌ No | 8 | @make | `docs/implementation/{feature_id}-implementation-notes.md` |
| Arch Review | ✅ Yes | 9 | @check | `docs/reviews/arch-review/{feature_id}-arch-review.md` |
| Code Review | ✅ Yes | 9 | @simplify | `docs/reviews/code-review/{feature_id}-code-review.md` |
| Workflow Summary | ✅ Yes | 10 | (orchestrator) | `docs/workflow/{feature_id}-workflow-summary.md` |

---

## Artifact Details

### 1. Test Design (Mandatory)

**Purpose:** Documents test strategy, acceptance criteria mapping, and RED state validation.

**Created by:** @test agent (Step 7: Write Tests)

**Content:**
- Test strategy (unit, integration, edge cases)
- Acceptance criteria → test case mapping
- RED state validation (failure codes)
- Files created (test file list)
- Escalations (NOT_TESTABLE, BLOCKED)
- Decision (next step routing)

**Template Sections:**
```markdown
# Test Design: {{feature_name}}
## Test Strategy
## Acceptance Criteria Mapping
## RED State Validation
## Escalations
## Decision
```

**Configurable:**
- Path: `.specify/harness-tdd-config.yml` → `artifacts.test_design.path`
- Template: `.specify/harness-tdd-config.yml` → `artifacts.test_design.template`
- Cannot toggle mandatory (constitutional requirement)

**Gates:**
- File gate: Only test file patterns allowed
- RED state gate: Valid failure codes required

---

### 2. Implementation Notes (Optional)

**Purpose:** Documents implementation approach, RED → GREEN evidence, refactoring.

**Created by:** @make agent (Step 8: Implement)

**Content:**
- Implementation approach description
- Files modified table
- RED → GREEN evidence (test outputs before/after)
- Refactoring description
- Integration validation results (test suite, linting, type checking)
- Additional notes

**Template Sections:**
```markdown
# Implementation Notes: {{feature_name}}
## Implementation Approach
## Files Modified
## RED → GREEN Evidence
## Refactoring
## Integration Validation
## Notes
```

**Configurable:**
- Path: `.specify/harness-tdd-config.yml` → `artifacts.implementation_notes.path`
- Template: `.specify/harness-tdd-config.yml` → `artifacts.implementation_notes.template`
- Mandatory: `.specify/harness-tdd-config.yml` → `artifacts.implementation_notes.mandatory` (default: false)

**Gates:**
- TDD entry validation: Tests must fail before implementation
- GREEN state gate: Tests must pass after implementation
- Integration validation: Project test suite must pass

---

### 3. Architecture Review (Mandatory)

**Purpose:** Validates safety constraints and architectural quality.

**Created by:** @check agent (Step 9: Final Review)

**Content:**
- Safety constraints (security, data integrity, backward compatibility)
- Architectural concerns (design patterns, separation, dependencies, testability)
- Recommended actions
- Escalations (blockers, tech debt, risky refactors)
- Verdict rationale (ACCEPTABLE | NEEDS_REVISION | BLOCKED)
- Conflicts with @simplify (safety wins)
- Review cycle tracking

**Template Sections:**
```markdown
# Architecture Review: {{feature_name}}
## Safety Constraints
## Architectural Concerns
## Recommended Actions
## Escalations
## Verdict Rationale
## Review Cycle
```

**Configurable:**
- Path: `.specify/harness-tdd-config.yml` → `artifacts.arch_review.path`
- Template: `.specify/harness-tdd-config.yml` → `artifacts.arch_review.template`
- Cannot toggle mandatory (constitutional requirement)

**Gates:**
- Safety constraints non-bypassable
- BLOCKED verdict requires human escalation
- Max 3 review cycles

---

### 4. Code Review (Mandatory)

**Purpose:** Analyzes code complexity, duplication, and readability.

**Created by:** @simplify agent (Step 9: Final Review)

**Content:**
- Complexity analysis (cyclomatic, nesting, function length)
- Code duplication percentage
- Readability assessment (naming, structure, comments)
- Recommendations (high, medium, optional priority)
- Trade-offs documented (performance vs readability, etc.)
- Conflicts with @check (safety wins)
- Verdict rationale (ACCEPTABLE | NEEDS_REVISION)
- Review cycle tracking

**Template Sections:**
```markdown
# Code Review: {{feature_name}}
## Complexity Analysis
## Code Duplication
## Readability Assessment
## Recommendations
## Trade-Offs Documented
## Conflicts with @check
## Verdict Rationale
## Review Cycle
```

**Configurable:**
- Path: `.specify/harness-tdd-config.yml` → `artifacts.code_review.path`
- Template: `.specify/harness-tdd-config.yml` → `artifacts.code_review.template`
- Cannot toggle mandatory (constitutional requirement)

**Gates:**
- @check safety constraints override @simplify complexity suggestions
- Max 3 review cycles

---

### 5. Workflow Summary (Mandatory)

**Purpose:** Comprehensive record of TDD workflow execution, evidence, and outcomes.

**Created by:** Orchestrator (Step 10: Commit, PR, Wrap-Up)

**Content:**
- Run metadata (timestamps, duration, status)
- TDD evidence (test counts, RED → GREEN cycles, coverage)
- Review outcomes (@check and @simplify verdicts, cycles, conflicts)
- Unresolved items (blockers, escalations, follow-ups)
- Artifacts generated table
- PR information (URL, status, Linear link)
- Manual overrides documentation
- Metrics (cycle time, review cycles, coverage, complexity)
- Lessons learned
- Sign-off checklist

**Template Sections:**
```markdown
# Workflow Summary: {{feature_name}}
## TDD Evidence
## Review Outcomes
## Unresolved Items
## Artifacts Generated
## PR Information
## Manual Overrides
## Metrics
## Lessons Learned
## Sign-Off
```

**Configurable:**
- Path: `.specify/harness-tdd-config.yml` → `artifacts.workflow_summary.path`
- Template: `.specify/harness-tdd-config.yml` → `artifacts.workflow_summary.template`
- Cannot toggle mandatory (constitutional requirement)

**Gates:**
- All mandatory artifacts must exist before workflow summary creation
- Evidence requirements must be met (test outputs, integration results)

---

## Configuration Reference

### Mandatory vs Optional (Current Defaults)

| Artifact | Mandatory | Rationale |
|----------|-----------|-----------|
| Test Design | ✅ Yes | TDD discipline requires test planning |
| Implementation Notes | ❌ No | Valuable but not critical (evidence in test outputs) |
| Arch Review | ✅ Yes | Safety constraints non-negotiable |
| Code Review | ✅ Yes | Quality standards non-negotiable |
| Workflow Summary | ✅ Yes | Audit trail and evidence capture |

### Toggling Optional Artifacts

Edit `.specify/harness-tdd-config.yml`:

```yaml
artifacts:
  implementation_notes:
    mandatory: true  # Change to true to require

  # Add custom optional artifact:
  custom_artifact:
    path: "docs/custom/{feature_id}.md"
    template: ".specify/templates/custom-template.md"
    mandatory: false
    step: 9  # Which step creates it
```

**Note:** Cannot toggle mandatory artifacts to optional (constitutional violation).

---

## Template Customization Guide

### Customize Existing Template

1. Copy template to workspace:
```bash
cp .specify/templates/test-design-template.md \
   .specify/templates/custom-test-design-template.md
```

2. Edit template (add/remove sections, change structure)

3. Update config to use custom template:
```yaml
artifacts:
  test_design:
    template: ".specify/templates/custom-test-design-template.md"
```

### Add Custom Artifact

1. Create template:
```bash
cat > .specify/templates/security-review-template.md <<'EOF'
# Security Review: {{feature_name}}

**Feature ID:** {{feature_id}}

## Vulnerabilities Found
{{list_vulnerabilities}}

## Security Score
{{score}}/100
EOF
```

2. Add to config:
```yaml
artifacts:
  security_review:
    path: "docs/reviews/security-review/{feature_id}-security-review.md"
    template: ".specify/templates/security-review-template.md"
    mandatory: false
    step: 9
```

3. Modify workflow to create artifact (requires extension customization)

---

## Template Variables

All templates support these placeholders:

| Variable | Description | Example |
|----------|-------------|---------|
| `{{feature_name}}` | Human-readable feature name | "User Login" |
| `{{feature_id}}` | Feature identifier | "feat-123" |
| `{{timestamp}}` | Creation timestamp | "2026-05-07T14:30:00Z" |
| `{{agent_name}}` | Agent that created artifact | "@test" |
| `{{status}}` | Current workflow status | "RED", "GREEN", "BLOCKED" |

Additional variables per artifact (see template files for full list).

---

## Artifact Lifecycle

### Creation Sequence

```
Step 7: @test creates test_design
  ↓
Step 8: @make creates implementation_notes (optional)
  ↓
Step 9: @check creates arch_review (parallel)
Step 9: @simplify creates code_review (parallel)
  ↓
Step 10: Orchestrator creates workflow_summary
```

### Validation Points

1. **Step 7 → 8:** test_design must exist
2. **Step 8 → 9:** Evidence artifacts must exist (test outputs)
3. **Step 9 → 10:** arch_review and code_review must exist
4. **Step 10:** All mandatory artifacts must exist

### Archival (Post-Merge)

After PR merge, artifacts remain in workspace:
- Active artifacts: Reference for future work
- Searchable: grep, ripgrep across all workflow summaries
- Auditability: Historical record of decisions

**Future Enhancement:** Spec-kit-archive integration to move to `specs_archive/`.

---

## Summary

**Total Artifacts:** 5 (3 mandatory, 2 optional by default)

**Customization Options:**
- ✅ Paths (all artifacts)
- ✅ Templates (all artifacts)
- ✅ Mandatory flag (optional artifacts only)
- ✅ Add custom artifacts (via config + extension)

**Constitutional Constraints:**
- ❌ Cannot remove mandatory artifacts
- ❌ Cannot skip gate validations
- ❌ Cannot bypass evidence requirements

For questions or issues, see [Constitution](CONSTITUTION-Multi-Agent-TDD.md) and [PRD](PRD-Multi-Agent-TDD-Workflow.md).
