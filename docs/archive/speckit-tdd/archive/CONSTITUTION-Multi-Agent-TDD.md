# Constitution: Multi-Agent TDD Workflow

**Version:** 1.0  
**Applies To:** harness-agents + harness-tdd-workflow  
**Last Updated:** 2026-05-07  
**Status:** Draft

---

## Purpose

This constitution defines the immutable principles, non-negotiable constraints, and quality standards for the **Multi-Agent TDD Workflow** system. All implementations, configurations, and customizations MUST align with these principles.

---

## Core Principles

### Principle 1: Test-First Discipline

**Principle:** Tests MUST be written before implementation code.

**Rationale:** Prevents untested code, ensures clear acceptance criteria, enables confident refactoring.

**Enforcement:**
- `/speckit.multi-agent.implement` validates RED state before allowing implementation
- Step 7 (@test) MUST complete before Step 8 (@make)
- Implementation blocked if tests pass prematurely (behavior already exists)

**Non-Negotiable:**
- Cannot skip test generation
- Cannot bypass RED state validation
- Cannot implement without failing tests

**Exceptions:**
- `NOT_TESTABLE` tasks (approved by @check agent)
- Infrastructure/tooling tasks (documented in spec)

---

### Principle 2: Evidence-Based Completion

**Principle:** No task is "done" without verifiable evidence.

**Rationale:** Prevents "works on my machine" claims, enables reproducible builds, creates audit trail.

**Enforcement:**
- RED → GREEN evidence required (test output snapshots)
- Integration test results required
- Regression test results required
- Workflow summary artifact MUST include all evidence

**Non-Negotiable:**
- Cannot claim completion without test output
- Cannot skip integration validation
- Cannot proceed to Step 10 without evidence artifacts

**Evidence Requirements:**
```markdown
## Required Evidence (Step 8 → Step 9)
1. Test output BEFORE implementation (RED state)
2. Test output AFTER implementation (GREEN state)
3. Regression test results (project test suite)
4. Linting/type-checking results
5. Coverage report (if applicable)
```

---

### Principle 3: Agent Specialization

**Principle:** Each agent has a single, well-defined responsibility.

**Rationale:** Prevents context pollution, enables parallel work, maintains expertise boundaries.

**Enforcement:**
- Agent definitions MUST specify `capabilities` and `constraints`
- Task routing MUST respect agent boundaries
- Cross-agent coordination MUST go through orchestrator (not direct)

**Agent Responsibilities (Non-Negotiable):**

| Agent | Responsibility | MUST Do | MUST NOT Do |
|-------|----------------|---------|-------------|
| `@test` | Write failing tests | Validate RED state, file gate enforcement | Write implementation code |
| `@make` | Implement features | Achieve GREEN state, refactor | Skip tests, modify test behavior, **alter any test code** |
| `@check` | Architecture review | Safety constraints, design critique | Rewrite code directly |
| `@simplify` | Code review | Complexity analysis, readability | Override safety constraints |
| `@qa` | Acceptance validation | Criteria checklist, QA reports | Approve failing tests |

**Critical Constraint: Test Immutability**

Developer agents (`@make`, `@check`, `@simplify`, `@qa`) are **NEVER** permitted to modify test code under any circumstances. This includes:
- Altering test assertions
- Changing test setup/teardown
- Modifying test fixtures or mocks
- Adjusting expected values
- Commenting out failing tests
- Skipping tests via decorators
- Renaming tests to bypass CI patterns

**Rationale:** Tests define the contract. If tests are wrong, only `@test` can fix them. Developer agents making tests pass by changing assertions undermines TDD discipline and creates false GREEN states.

**Enforcement:**
- File gate validation: No test file modifications allowed in Step 8 (@make implementation)
- Read-only permissions: Developer agents have no write access to test directories
- Violation detection: Git diff analysis flags any test file changes by non-@test agents
- Immediate abort: Any test modification attempt by developer agents terminates workflow

**Valid Test Changes:**
- `@test` agent during Step 7 (initial test authoring)
- `@test` agent after `NOT_TESTABLE` sign-off (test correction)
- Human developer with documented justification (manual override)

**Violations:**
- @test writing implementation → abort, escalate
- @make modifying test code → **abort immediately, escalate, log security incident**
- @make modifying test assertions → **abort immediately, escalate, log security incident**
- @check/@simplify/@qa altering tests → **abort immediately, escalate**
- @simplify overriding @check safety → @check wins, log conflict

---

### Principle 4: Configurable Rigor, Non-Bypassable Gates

**Principle:** Teams can configure workflow details, but cannot bypass quality gates.

**Rationale:** Enables team adaptation while maintaining baseline quality standards.

**Configurable:**
- Artifact paths and templates
- Agent assignment rules
- Review cycle limits (1-5)
- Human gating points
- Failure code handling

**Non-Configurable (Gates):**
- RED state validation (Step 7 → 8)
- Integration test execution (Step 8)
- Arch review execution (Step 9)
- Code review execution (Step 9)
- Evidence capture (Step 8 → 10)

**Gate Failure Responses:**
```yaml
# .specify/harness-tdd-config.yml
gate_failures:
  test_validation_failed:
    action: "abort"  # Cannot override to "continue"
  arch_review_blocked:
    action: "escalate_human"  # Cannot override to "auto_approve"
  integration_tests_failed:
    action: "abort"  # Cannot override to "continue"
```

---

### Principle 5: Artifact Integrity

**Principle:** Artifacts are the source of truth, not agent memory.

**Rationale:** Prevents context drift, enables offline review, creates audit trail.

**Enforcement:**
- Each step MUST write artifacts before proceeding
- Artifacts MUST match configured templates
- Workflow summary MUST reference all artifacts
- Mandatory artifacts cannot be skipped

**Artifact Chain (Non-Negotiable):**
```
Spec (input) 
  → Test Design (Step 7) 
  → Implementation Notes (Step 8) 
  → Arch Review (Step 9) 
  → Code Review (Step 9) 
  → Workflow Summary (Step 10) 
  → Git Commit + PR
```

**Missing Artifact Handling:**
- Mandatory artifact missing → abort workflow
- Optional artifact missing → log warning, continue
- Malformed artifact → abort, request template fix

---

### Principle 6: Human Authority Over Automation

**Principle:** Humans can override any automated decision, but overrides MUST be documented.

**Rationale:** AI agents assist, humans decide. Automation bias prevention.

**Enforcement:**
- Manual gate mode available for all steps
- Override documentation required in workflow summary
- Three-strike escalation (3 review cycles → human intervention)

**Override Documentation Format:**
```markdown
## Manual Overrides (in workflow summary)

### Arch Review Override
- **Gate:** arch_review
- **Agent Verdict:** NEEDS_REVISION
- **Human Decision:** APPROVED (override)
- **Justification:** Technical debt acceptable for MVP, tracked in TECH-DEBT-123
- **Approver:** @architect-lead (timestamp)
```

**Non-Overridable:**
- RED state validation (tests MUST fail before implementation)
- File gate enforcement (only test files in Step 7)
- Evidence capture (cannot skip test output)

---

### Principle 7: Deterministic Execution

**Principle:** Same inputs produce same outputs (agent assignments, artifact content structure).

**Rationale:** Enables reproducibility, debugging, and team trust in automation.

**Enforcement:**
- Agent routing based on task metadata (not prompt interpretation)
- Artifact templates are code (versioned, reviewed)
- Execution logs capture all decisions

**Determinism Requirements:**
```yaml
# Task metadata (in tasks.md frontmatter)
---
task_id: TASK-007
type: "test_generation"  # Deterministic routing
agent: "@test"            # Explicit assignment
artifact: "test_design"   # Known template
files: ["tests/acceptance/login.test.ts"]
---
```

**Non-Deterministic Failures:**
- Prompt-based routing → replace with metadata routing
- Agent "decides" which artifact to create → template config decides
- Variable agent responses → structured output formats

---

### Principle 8: Superpowers Independence

**Principle:** No dependencies on external skill repositories (superpowers, marketplace).

**Rationale:** Self-contained system, no version conflicts, team-controlled evolution.

**Enforcement:**
- Agent definitions are local YAML files
- Workflow logic is extension code (Python + markdown)
- Templates are local files
- No remote skill fetching

**Allowed Dependencies:**
- Claude Code CLI (runtime)
- SpecKit (extension framework)
- GitHub CLI (PR creation)
- Git (version control)

**Forbidden Dependencies:**
- superpowers skills (any)
- External skill marketplaces
- Remote agent definitions
- Proprietary orchestration services

---

## Workflow Invariants

### Invariant 1: Step Sequence

Steps 7, 8, 9, 10 MUST execute in order. No skipping.

**Exceptions:**
- Step 7 → Step 9 (if `NOT_TESTABLE`)
- Step 9 early exit (convergence detection)

### Invariant 2: Review Loop Bounded

Maximum 3 review cycles (Step 9). Fourth iteration escalates to human.

**Rationale:** Prevents infinite loops, forces human decision on persistent issues.

**Implementation:** Review command loops internally up to 3 times, then exits and requires manual re-invocation.

**Conflict Resolution:** When @check (architecture) and @simplify (code quality) provide contradicting recommendations:
- Workflow escalates to user with exit code 2
- Presents both recommendations with context
- Provides at least 2 resolution options
- Includes orchestrator's recommendation
- Requires explicit human decision

**Example Conflict:**
```
@check: Add abstraction layer for database access
@simplify: Keep implementation inline, complexity low

Options:
1. Follow @check (prioritize architecture/safety)
2. Follow @simplify (prioritize simplicity/readability)
3. Hybrid approach: [orchestrator recommendation]

Recommendation: Option 1 - Safety constraints take precedence in this context
```

### Invariant 3: File Gate Enforcement

Step 7 output MUST match test file patterns. Non-test files → abort.

**Patterns (configurable):**
- `**/test_*.py`
- `**/*_test.py`
- `**/conftest.py`

### Invariant 4: Evidence Before Commit/Merge

Git commit and PR creation (Step 10) blocked until all evidence artifacts exist and validate.

**Required Artifacts:**
- Test design (Step 7) with RED state evidence
- Implementation notes (Step 8) with GREEN state evidence
- Arch review (Step 9) with verdict
- Code review (Step 9) with verdict
- Workflow summary (Step 10) with complete evidence chain

**Git Commit Execution Model:**

Commit command (`/speckit.multi-agent.commit`) performs actual git operations:
1. Validates all evidence using `lib/evidence_validator.validate_all()`
2. Halts if validation fails (exit code 1) with detailed error message
3. Generates commit message from workflow summary
4. Executes `git commit -m "<message>"` with Co-Authored-By trailer
5. Updates local Jira story state to "Done" (simple stories only)
6. Reports commit SHA and success

**Note:** PR creation deferred to Phase 3 (larger stories/epics). Phase 2 commits directly to current branch.

---

## Quality Standards

### QS-1: Test Coverage

**Requirement:** All spec requirements MUST have corresponding tests.

**Validation:** Test design artifact MUST map requirements to test cases.

**Threshold:** 100% requirement coverage (not code coverage).

### QS-2: Review Rigor

**Requirement:** Both @check and @simplify MUST review implementation.

**Validation:** Review artifacts MUST exist with non-empty findings.

**Threshold:** At least 1 finding per review (or explicit "no concerns" statement).

### QS-3: Evidence Completeness

**Requirement:** Workflow summary MUST include all TDD evidence.

**Validation:** Summary artifact MUST contain:
- RED state test output
- GREEN state test output
- Integration test results
- Review verdicts

### QS-4: Artifact Template Compliance

**Requirement:** All artifacts MUST match configured templates.

**Validation:** Template sections present, no missing headers.

**Threshold:** 100% template compliance (mandatory sections).

### QS-5: Evidence Validation Before Commit

**Requirement:** Commit command (Step 10) MUST validate all constitutional evidence before executing git commit.

**Validation:** Uses `lib/evidence_validator.validate_all()` to check:
- Test design artifact exists with RED state evidence
- Implementation notes exist with GREEN state evidence  
- Architecture review artifact exists with verdict
- Code review artifact exists with verdict
- Workflow summary exists with complete evidence

**Enforcement:**
- Validation failure → exit code 1 (halt workflow)
- Missing artifacts → detailed error message listing gaps
- Cannot proceed to git commit without complete evidence

**Implementation:** `commands/commit.py` calls validation before any git operations.

---

## Local Jira State Machine

**Purpose:** Track workflow progress through local story files (`.specify/epics/` structure) until Jira API integration in Phase 3.

**State Transitions:**

```
To Do → Creating Tests → Implementing → Reviewing → Done/Cancelled
```

**State Definitions:**

| State | Trigger | Actions |
|-------|---------|---------|
| **To Do** | Story created | Initialize story file |
| **Creating Tests** | `test` command invoked | Update state, timestamp |
| **Implementing** | `implement` command invoked (RED validated) | Update state, timestamp |
| **Reviewing** | `review` command invoked | Update state, timestamp |
| **Done** | `commit` command success (simple story) | Update state, link artifacts, set completion timestamp |
| **Cancelled** | User cancellation | Update state, add reason |

**Hooks:**

- **Agent Invocation Hook:** Triggered when command starts, updates story state to reflect active phase
- **Agent Response Hook:** Triggered when command completes successfully, advances story state

**Commit Rules:**

- **Simple Stories:** Git commit after individual story completes (Done state)
- **Bigger Stories/Epics:** PR creation after all child stories complete (handled by execute orchestrator in Phase 3)

**Implementation:** Uses `lib/jira_local.py` functions:
- `update_story_status(story_id, status, project_root, jira_root)`
- `link_artifacts_to_story(story_id, artifacts, project_root, jira_root)`

---

## Failure Handling

### Failure Class: Test Validation Failed

**Trigger:** Tests pass when they should fail (Step 7 → 8 transition)

**Response:**
1. Abort workflow
2. Document in `docs/workflow/{feature_id}-failure.md`
3. Escalate to human:
   - Behavior already exists → task may be wrong
   - Test quality concerns → @check diagnoses → @test fixes → retry

**No Auto-Recovery:** Human must approve retry.

### Failure Class: Integration Tests Failed

**Trigger:** Project test suite fails after implementation (Step 8)

**Response:**
1. Abort workflow
2. Capture regression details in implementation notes
3. Revert implementation OR fix regression
4. Re-run Step 8

**Auto-Recovery:** If fix within 1 cycle, continue. Else escalate.

### Failure Class: Review Convergence Failed

**Trigger:** 3 review cycles with unresolved issues (Step 9)

**Response:**
1. Stop automated review loop
2. Escalate to human reviewer
3. Document persistent issues in workflow summary
4. Human decision: approve with debt, request major refactor, or reject

**No Auto-Recovery:** Human decision required.

### Failure Class: Gate Bypass Attempt

**Trigger:** Configuration tries to disable mandatory gate

**Response:**
1. Log warning
2. Override config (re-enable gate)
3. Notify team lead via workflow summary
4. Continue with gate enabled

**No Override Allowed:** Constitutional gates cannot be bypassed via config.

---

## Prohibited Patterns

### ❌ Prohibited: Test-After Implementation

Writing tests after code is written violates Principle 1.

**Detection:** File modification timestamps (implementation before tests).

**Response:** Abort workflow, request TDD compliance.

### ❌ Prohibited: Evidence-Free Completion

Claiming task completion without test output violates Principle 2.

**Detection:** Missing evidence artifacts at Step 9 → 10 transition.

**Response:** Block PR creation, request evidence.

### ❌ Prohibited: Agent Boundary Violation

@test writing implementation code violates Principle 3.

**Detection:** Implementation files in @test output (file gate).

**Response:** Abort Step 7, discard output, escalate.

### ❌ Prohibited: Silent Configuration Override

Disabling gates without documentation violates Principle 4.

**Detection:** Config changes to `gate_failures` without commit message explanation.

**Response:** Reject config change, request justification.

### ❌ Prohibited: Superpowers Dependency

Importing superpowers skills violates Principle 8.

**Detection:** `.specify/superb-config.yml` references or skill imports.

**Response:** Abort extension installation, request removal.

---

## Amendment Process

This constitution can only be amended through:

1. **Proposal:** Team member drafts amendment with rationale
2. **Review:** Architect team reviews for principle conflicts
3. **Approval:** 2/3 team consensus required
4. **Documentation:** Amendment logged with version bump
5. **Migration:** Grace period (2 sprints) for workflow updates

**Emergency Amendments:** Security/safety issues can bypass consensus (architect authority).

---

## Validation Checklist

Before any workflow execution, validate:

- [ ] All agent definitions present (5 specialists)
- [ ] All artifact templates present (5 mandatory)
- [ ] Configuration file valid (`.specify/harness-tdd-config.yml`)
- [ ] Gates enabled (no bypasses)
- [ ] File patterns configured (test validation)
- [ ] Evidence paths writable (artifact directories exist)
- [ ] No superpowers references (grep check)

**Pre-Execution Command:** `/speckit.multi-agent.validate-constitution`

---

## Appendix: Rationale for Key Decisions

### Why Test-First (Principle 1)?

**Historical Context:** Teams without TDD discipline accumulate technical debt, write brittle code, fear refactoring.

**Alternative Rejected:** Test-after (too easy to skip, lower coverage, less design benefit).

**Trade-Off:** Slower initial velocity, but faster long-term (fewer bugs, confident refactors).

### Why Evidence-Based (Principle 2)?

**Historical Context:** "Works on my machine" claims led to production incidents, difficult debugging.

**Alternative Rejected:** Trust-based completion (no audit trail, no reproducibility).

**Trade-Off:** More ceremony (artifact writing), but higher confidence (verifiable outcomes).

### Why Agent Specialization (Principle 3)?

**Historical Context:** General-purpose agents produced lower-quality output across all tasks (jack-of-all-trades problem).

**Alternative Rejected:** Single agent for all steps (context pollution, inconsistent quality).

**Trade-Off:** More coordination overhead, but better outcomes per task.

### Why No Superpowers (Principle 8)?

**Historical Context:** External dependency led to version conflicts, unclear ownership, hard-to-debug issues.

**Alternative Rejected:** Reuse superpowers skills (less code to write, but tight coupling).

**Trade-Off:** More initial development, but full team control and independence.

---

## Glossary

**@test:** Test specialist agent (Step 7)  
**@make:** Implementation specialist agent (Step 8)  
**@check:** Architecture reviewer agent (Step 9)  
**@simplify:** Code reviewer agent (Step 9)  
**@qa:** QA validator agent (acceptance criteria)

**RED State:** Tests fail (expected before implementation)  
**GREEN State:** Tests pass (achieved by implementation)  
**File Gate:** Validation that only allowed file types were modified  
**Evidence Artifact:** Document containing verifiable test outputs  
**Gate:** Non-bypassable quality checkpoint  
**Convergence Detection:** Same review findings twice → stop loop  

---

**Constitutional Authority:** This document supersedes all configuration, customization, and automation logic. When in conflict, constitution wins.
