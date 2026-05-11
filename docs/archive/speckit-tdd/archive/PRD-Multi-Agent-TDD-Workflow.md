# Product Requirements Document: Multi-Agent TDD Workflow

**Version:** 1.0  
**Date:** 2026-05-07  
**Status:** Draft  
**Owner:** Harness Sandbox Team

---

## Executive Summary

A dual-plugin architecture providing **deterministic, multi-agent TDD workflow** for SpecKit-based development. Replaces superpowers dependency with native agent coordination and PRIES-compliant workflow automation.

---

## Problem Statement

Current SpecKit workflows lack:
1. **Deterministic agent routing** — prompt-based orchestration varies
2. **PRIES workflow compliance** — no native support for steps 7-10 (Write Tests → Implement → Review → Commit)
3. **Configurable artifact templates** — hardcoded paths/formats
4. **Human-in-the-loop gating** — all-or-nothing automation
5. **Superpowers independence** — tight coupling to external skills

---

## Solution Overview

### Architecture: Dual Plugin System

```
┌─────────────────────────────────────────────────────────┐
│ Claude Code Plugin: harness-agents                      │
│ - Agent definitions (.claude/agents/*.yml)              │
│ - Agent runtime coordination                            │
│ - Reusable across projects (not SpecKit-specific)       │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│ SpecKit Extension: harness-tdd-workflow                 │
│ - Custom command: /speckit.multi-agent.implement        │
│ - PRIES workflow steps 7-10                             │
│ - Configurable artifact templates                       │
│ - Optional human gating                                 │
└─────────────────────────────────────────────────────────┘
```

---

## Requirements

### Functional Requirements

#### FR-1: Claude Code Plugin — harness-agents

**FR-1.1: Agent Definitions**
- Provide 5 specialist agent definitions:
  - `test-specialist` — writes tests, validates RED state
  - `dev-specialist` — implements features, achieves GREEN state
  - `qa-specialist` — validates acceptance criteria, runs QA gates
  - `arch-specialist` — reviews architecture, design decisions
  - `review-specialist` — code review, security analysis

**FR-1.2: Agent Runtime**
- Command: `/agents.spawn <agent-name> <task-description>`
- Command: `/agents.assign-task <task-id> <agent-name>`
- Metadata tracking: agent assignments, task handoffs, execution logs

**FR-1.3: Installation**
- Installable from harness-tooling: `claude plugin install harness-tooling/.claude-plugin/harness-agents`
- Auto-creates `.claude/agents/` directory with agent definitions

---

#### FR-2: SpecKit Extension — harness-tdd-workflow

**FR-2.1: PRIES Workflow (Steps 7-10)**

Command: `/speckit.multi-agent.implement [--gate-mode=auto|manual]`

**Step 7: Write Tests** (@test agent)
- Input: Task spec from `docs/tasks/active/###-tasks.md`
- Output: Test files (`tests/acceptance/*.test.ts`)
- Artifact: `docs/tests/test-design/###-test-design.md`
- Gate: Validate RED state with structured failure codes
  - `MISSING_BEHAVIOR` → valid RED (proceed)
  - `ASSERTION_MISMATCH` → valid RED (proceed)
  - `TEST_BROKEN` → fix required
  - `ENV_BROKEN` → blocked
- File gate: Only test file patterns allowed (`**/test_*.py`, `**/*_test.py`)
- Decision table:
  - `TESTS_READY` + no escalation → Step 8
  - `TESTS_READY` + escalation → Arch review first
  - `NOT_TESTABLE` → Arch sign-off required
  - `BLOCKED` → Investigate root cause

**Step 8: Implement** (@make agent)
- Input: Task spec + pre-written tests
- TDD validation: Verify tests fail (RED) before implementation
- Output: Implementation code
- Artifact: `docs/implementation/###-implementation-notes.md`
- Gate: RED → GREEN evidence
  - Test output before (failing)
  - Test output after (passing)
  - Regression test results
- Refactor while maintaining GREEN
- Integration validation: Run project test suite + linting

**Step 9: Final Review** (@check + @simplify agents in parallel)
- Input: Full implementation diff
- Output: Review findings
- Artifacts:
  - `docs/reviews/arch-review/###-arch-review.md` (@check)
  - `docs/reviews/code-review/###-code-review.md` (@simplify)
- Gate: Review loop (max 3 cycles)
  - Merge findings (@check safety wins over @simplify complexity)
  - If ACCEPTABLE → Step 10
  - If issues → fix, re-review
  - Convergence detection: same findings twice = stop early
- Human gate option: If `--gate-mode=manual`, wait for approval

**Step 10: Commit, PR, Wrap-Up**
- Actions:
  1. Commit with conventional commit message
  2. Create draft PR: `gh pr create --draft`
  3. Post Linear comment (if configured)
  4. Write workflow summary: `.opencode/workflow-summary.md`
- Artifacts:
  - Git commit
  - GitHub PR (draft)
  - `docs/workflow/###-workflow-summary.md`
- PR body includes:
  - Summary, Linear link
  - Acceptance criteria checklist
  - Files changed
  - TDD summary (RED→GREEN evidence)
  - Escalations and resolutions
  - Blockers, review verdicts

**FR-2.2: Configurable Artifact Templates**

Configuration file: `.specify/harness-tdd-config.yml`

```yaml
artifacts:
  test_design:
    path: "docs/tests/test-design/{feature_id}-test-design.md"
    template: ".specify/templates/test-design-template.md"
    mandatory: true
  
  implementation_notes:
    path: "docs/implementation/{feature_id}-implementation-notes.md"
    template: ".specify/templates/implementation-notes-template.md"
    mandatory: false
  
  arch_review:
    path: "docs/reviews/arch-review/{feature_id}-arch-review.md"
    template: ".specify/templates/arch-review-template.md"
    mandatory: true
  
  code_review:
    path: "docs/reviews/code-review/{feature_id}-code-review.md"
    template: ".specify/templates/code-review-template.md"
    mandatory: true
  
  workflow_summary:
    path: "docs/workflow/{feature_id}-workflow-summary.md"
    template: ".specify/templates/workflow-summary-template.md"
    mandatory: true

gate_modes:
  default: "auto"  # auto | manual
  manual_gates:
    - "arch_review"     # Always require human approval
    # - "code_review"   # Optional: uncomment to gate code review
```

**FR-2.3: Installation**
- Installable from harness-tooling: `specify extension add harness-tdd-workflow --from ../harness-tooling/.speckit-extensions/harness-tdd-workflow`
- Auto-creates `.specify/harness-tdd-config.yml` with defaults

---

#### FR-3: Grill-Me Planning Integration

**FR-3.1: Custom Planning Command**

Command: `/speckit.multi-agent.plan [--mode=interactive|batch]`

Replaces: `/speckit.plan` (built-in)

**Workflow:**
1. Read spec from `specs/###-feature.md`
2. Invoke Matt Pocock's grill-me skill for interactive planning
   - Agent asks clarifying questions
   - User provides answers
   - Agent refines plan based on responses
3. Generate plan with TDD phases pre-structured
4. Output: `docs/plans/active/###-plan.md`

**Modes:**
- `interactive` (default): Grill-me session with user
- `batch`: Skip grill-me, use spec as-is

**Integration:**
```yaml
# .specify/harness-tdd-config.yml
planning:
  skill: "grill-me"  # Matt Pocock's skill
  skill_path: ".claude/marketplace-skills/grill-me/"
  interactive_by_default: true
```

---

### Non-Functional Requirements

**NFR-1: Determinism**
- Same inputs → same agent assignments (no prompt variance)
- Auditable execution logs for each step
- Reproducible workflow runs

**NFR-2: Performance**
- Full workflow (steps 7-10) completes in <10 minutes for typical feature
- Agent spawn time <5 seconds
- Artifact generation <2 seconds per artifact

**NFR-3: Extensibility**
- Teams can add custom agents (new YAML files)
- Teams can add custom artifacts (config + templates)
- Teams can customize gate logic (YAML configuration)

**NFR-4: No Superpowers Dependency**
- Zero references to superpowers skills
- Self-contained agent coordination
- No external skill dependencies

---

## Artifact Details

### Artifact Summary

| Artifact | Path | Mandatory | Template | Generated By |
|----------|------|-----------|----------|--------------|
| Test Design | `docs/tests/test-design/###.md` | ✅ Yes | ✅ Configurable | Step 7 (@test) |
| Implementation Notes | `docs/implementation/###.md` | ❌ No | ✅ Configurable | Step 8 (@make) |
| Arch Review | `docs/reviews/arch-review/###.md` | ✅ Yes | ✅ Configurable | Step 9 (@check) |
| Code Review | `docs/reviews/code-review/###.md` | ✅ Yes | ✅ Configurable | Step 9 (@simplify) |
| Workflow Summary | `docs/workflow/###-summary.md` | ✅ Yes | ✅ Configurable | Step 10 |

### Artifact Content (Guesses — Configurable via Templates)

**Test Design Template** (`test-design-template.md`):
```markdown
# Test Design: {feature_name}

**Feature ID:** {feature_id}  
**Agent:** @test  
**Status:** {RED|GREEN|BLOCKED}

## Test Strategy
- Unit tests: {list}
- Integration tests: {list}
- Edge cases: {list}

## RED State Validation
- Failure code: {MISSING_BEHAVIOR|ASSERTION_MISMATCH}
- Test output: {snippet}

## Escalations
{any blockers or concerns}
```

**Implementation Notes Template** (`implementation-notes-template.md`):
```markdown
# Implementation Notes: {feature_name}

**Feature ID:** {feature_id}  
**Agent:** @make  
**TDD Cycle:** {RED → GREEN}

## Implementation Approach
{description}

## Files Modified
{list of changed files}

## RED → GREEN Evidence
### Before (RED)
```
{test output showing failures}
```

### After (GREEN)
```
{test output showing passes}
```

## Refactoring
{any refactoring done while maintaining green}

## Integration Validation
- Test suite: {PASS|FAIL}
- Linting: {PASS|FAIL}
- Type checking: {PASS|FAIL}
```

**Arch Review Template** (`arch-review-template.md`):
```markdown
# Architecture Review: {feature_name}

**Feature ID:** {feature_id}  
**Agent:** @check  
**Verdict:** {ACCEPTABLE|NEEDS_REVISION|BLOCKED}

## Safety Constraints
- [ ] No security vulnerabilities
- [ ] No data loss risks
- [ ] No backward compatibility breaks

## Architectural Concerns
{findings}

## Recommended Actions
{action items}

## Escalations
{blockers or major concerns}
```

**Code Review Template** (`code-review-template.md`):
```markdown
# Code Review: {feature_name}

**Feature ID:** {feature_id}  
**Agent:** @simplify  
**Verdict:** {ACCEPTABLE|NEEDS_REVISION}

## Complexity Analysis
- Cyclomatic complexity: {score}
- Code duplication: {percentage}
- Readability: {score}

## Recommendations
{simplification suggestions}

## Merge Decision
{rationale for verdict}
```

**Workflow Summary Template** (`workflow-summary-template.md`):
```markdown
# Workflow Summary: {feature_name}

**Feature ID:** {feature_id}  
**Run Timestamp:** {datetime}  
**Status:** {COMPLETED|BLOCKED|PARTIAL}

## TDD Evidence
- Tests written: {count}
- RED → GREEN cycles: {count}
- Coverage: {percentage}

## Review Outcomes
- Arch review verdict: {ACCEPTABLE|etc}
- Code review verdict: {ACCEPTABLE|etc}
- Review cycles: {count}

## Unresolved Items
{blockers, escalations, follow-ups}

## Artifacts Generated
- Test design: {path}
- Implementation notes: {path}
- Arch review: {path}
- Code review: {path}

## PR Link
{GitHub PR URL}
```

---

## User Stories

**US-1: Developer Implements Feature with TDD**
- As a developer, I want to run `/speckit.multi-agent.implement` and have tests written before code, so I follow TDD discipline without manual coordination.

**US-2: Team Lead Gates Critical Reviews**
- As a team lead, I want to configure `--gate-mode=manual` for arch reviews, so I can approve risky changes before implementation proceeds.

**US-3: QA Specialist Validates Acceptance**
- As a QA specialist, I want my agent to automatically validate acceptance criteria and generate QA reports, so nothing is missed.

**US-4: Architect Reviews Design**
- As an architect, I want the @check agent to flag architectural concerns before code is written, so we avoid costly refactors later.

**US-5: Junior Dev Uses Interactive Planning**
- As a junior developer, I want `/speckit.multi-agent.plan --mode=interactive` to ask me clarifying questions, so my plan is complete before I start coding.

---

## Success Criteria

1. ✅ Full workflow (steps 7-10) completes end-to-end without errors
2. ✅ Agent assignments are deterministic (same task → same agent)
3. ✅ All mandatory artifacts generated
4. ✅ Human gating works when configured
5. ✅ Zero superpowers dependencies
6. ✅ Grill-me planning integration functional
7. ✅ Both plugins installable from harness-tooling
8. ✅ Team can customize artifacts via templates

---

## Out of Scope

- Steps 1-6 of PRIES workflow (specification, planning phases)
- Integration with remote agents (local-only for v1)
- Multi-repo branching (handled by existing SpecKit presets)
- Voice-based workflow (future enhancement)

---

## Dependencies

- Claude Code CLI (agent runtime)
- SpecKit v0.7.1+ (extension API)
- GitHub CLI (PR creation)
- Matt Pocock's grill-me skill (optional, for planning)

---

## Risks

| Risk | Severity | Mitigation |
|------|----------|------------|
| Agent routing bugs | High | Unit tests for routing logic |
| Template format changes | Medium | Versioned templates with migration guide |
| Gate bypass bugs | High | Explicit gate validation in code |
| Grill-me skill unavailable | Low | Graceful fallback to batch mode |

---

## Timeline

- **Week 1:** Build harness-agents plugin (agent definitions + runtime)
- **Week 2:** Build harness-tdd-workflow extension (steps 7-10)
- **Week 3:** Integration testing + template refinement
- **Week 4:** Team validation + documentation

---

## Appendix: Configuration Example

```yaml
# .specify/harness-tdd-config.yml (complete example)
version: "1.0"

agents:
  test_agent: "test-specialist"
  implementation_agent: "dev-specialist"
  qa_agent: "qa-specialist"
  arch_reviewer: "arch-specialist"
  code_reviewer: "review-specialist"

artifacts:
  test_design:
    path: "docs/tests/test-design/{feature_id}-test-design.md"
    template: ".specify/templates/test-design-template.md"
    mandatory: true
  implementation_notes:
    path: "docs/implementation/{feature_id}-implementation-notes.md"
    template: ".specify/templates/implementation-notes-template.md"
    mandatory: false
  arch_review:
    path: "docs/reviews/arch-review/{feature_id}-arch-review.md"
    template: ".specify/templates/arch-review-template.md"
    mandatory: true
  code_review:
    path: "docs/reviews/code-review/{feature_id}-code-review.md"
    template: ".specify/templates/code-review-template.md"
    mandatory: true
  workflow_summary:
    path: "docs/workflow/{feature_id}-workflow-summary.md"
    template: ".specify/templates/workflow-summary-template.md"
    mandatory: true

gates:
  default_mode: "auto"  # auto | manual
  manual_gates:
    - "arch_review"
  max_review_cycles: 3
  convergence_detection: true

planning:
  skill: "grill-me"
  skill_path: ".claude/marketplace-skills/grill-me/"
  interactive_by_default: true
  fallback_to_batch: true

validation:
  test_file_patterns:
    - "**/test_*.py"
    - "**/*_test.py"
    - "**/conftest.py"
  failure_codes:
    valid_red:
      - "MISSING_BEHAVIOR"
      - "ASSERTION_MISMATCH"
    invalid:
      - "TEST_BROKEN"
      - "ENV_BROKEN"
```
