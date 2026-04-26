# PRIES Workflow to Harness Skills Mapping

**Status:** Analysis Complete  
**Date:** 2026-04-26  
**Context:** Mapping PRIES workflow phases to existing harness-tooling marketplace skills for STA2E VTT BMAD integration test project

---

## Overview

This document maps the five PRIES workflow phases (PM → Make → Test → Review → Simplify) to existing skills in the harness-tooling marketplace. The goal is to **reference** (not duplicate) legacy skills from sta2e_minimal_vtt when implementing the PRIES workflow plugin for both Claude Code and OpenCode.

### PRIES Phases

| Phase | Primary Agent | Purpose | Output |
|-------|--------------|---------|--------|
| **PM** | @pm | Fetch requirements from Linear, define acceptance criteria | Task specification, file manifest |
| **Make** | @make | Implement code changes per specification | Working code |
| **Test** | @test | Write failing tests (TDD RED phase) | Test files with classified failures |
| **Review** | @review orchestrator | Coordinate @check and @simplify reviews | Review findings |
| **Simplify** | @simplify | Identify unnecessary complexity | Simplification recommendations |

---

## Phase 1: PM (Product Management)

### PRIES PM Requirements
- Fetch Linear issues via CLI
- Parse task descriptions and acceptance criteria
- Identify relevant code context
- Generate file manifest (explicit list of files to modify/create)
- Define integration contracts for cross-task dependencies

### Mapped Harness Skills

| Skill | Relevance | Notes |
|-------|-----------|-------|
| **stdd-ask-questions-if-underspecified** | ✅ High | Validates requirement completeness before proceeding |
| **stdd-product-spec-formats** | ✅ High | Structured formats for requirements (Job Stories, Gherkin, OpenSpec) |
| **stdd-project-summary** | 🔶 Medium | Maintains project context (Goal, Tech Stack, User Stories) |
| **brainstorming** | 🔶 Medium | Creative requirement exploration if initial spec is vague |
| **arch-writing-plans** | 🔶 Medium | Generates implementation plans from requirements |
| **governance-nfr-writer** | 🔵 Low | Non-functional requirements if needed for complex features |

### Missing Capabilities
- **Linear CLI integration skill** — PRIES @pm agent directly uses bash `linear *` commands; harness has no dedicated Linear skill
- **File manifest generation** — No explicit skill for analyzing requirements → file list mapping

### Recommendation
Create new skill: `stdd-pm-linear-integration.md`
- Wrap Linear CLI operations (issue fetch, state management, comments)
- Generate file manifests from requirements analysis
- Reference: `/home/minged01/repositories/harness-workplace/harness-tooling/docs/reference-workflows-ppries/pm.md`

---

## Phase 2: Make (Implementation)

### PRIES Make Requirements
- Strict file modification constraints (only listed files)
- Immediate escalation on insufficient context
- Fresh verification evidence (no assumptions from prior runs)
- TDD mode support (implement to pass pre-written tests)
- Pattern preservation (maintain existing codebase conventions)

### Mapped Harness Skills

| Skill | Relevance | Notes |
|-------|-----------|-------|
| **orchestrate-executing-plans** | ✅ High | Executes structured implementation plans with constraints |
| **orchestrate-subagent-driven-development** | ✅ High | Multi-agent implementation with spec/code/review phases |
| **general-verification-before-completion** | ✅ High | **Critical** — enforces "no claims without fresh evidence" |
| **general-git-advanced-workflows** | 🔶 Medium | Git operations (though PRIES @make escalates git to caller) |
| **stdd-test-driven-development** | ✅ High | TDD workflow (RED → GREEN → REFACTOR) |
| **python-code-style** | 🔶 Medium | Code quality enforcement (linting, formatting) |
| **general-solid** | 🔶 Medium | SOLID principles for maintainable code |
| **python-design-patterns** | 🔶 Medium | Pattern application (KISS, DRY, SoC) |

### Skill Gaps
- **Strict file boundary enforcement** — PRIES @make requires hard constraints on writable files; harness skills are advisory
- **Escalation protocol** — PRIES @make escalates renames/deletes/out-of-scope changes; harness skills don't have formal escalation

### Recommendation
Enhance existing skills with enforcement metadata:
- Add `file_constraints` field to orchestrate-* skills for hard boundaries
- Create new skill: `stdd-make-constrained-implementation.md` with PRIES escalation rules

---

## Phase 3: Test (TDD Test Authoring)

### PRIES Test Requirements
- Writes failing tests BEFORE implementation (strict TDD RED)
- Failure classification: MISSING_BEHAVIOR, ASSERTION_MISMATCH (valid), TEST_BROKEN, ENV_BROKEN (invalid)
- File constraints: only `**/test_*.py`, `**/*_test.py`, `**/conftest.py`, test_data/fixtures
- Contract testing (public API, not implementation details)
- Escalation triggers: mixed failure codes, >2 mocks, nondeterministic behavior
- NOT_TESTABLE verdict requires @check sign-off

### Mapped Harness Skills

| Skill | Relevance | Notes |
|-------|-----------|-------|
| **stdd-test-driven-development** | ✅ High | Core TDD workflow |
| **review-e2e-testing-patterns** | 🔶 Medium | E2E test patterns (Playwright, Cypress) |
| **python-testing-uv-playwright** | 🔶 Medium | Playwright E2E with uv package manager |
| **general-python-environment** | 🔶 Medium | Testing setup (pytest, coverage, fixtures) |
| **review-systematic-debugging** | 🔵 Low | Debugging test failures (root cause analysis) |

### Missing Capabilities
- **Failure classification taxonomy** — PRIES defines 4 failure codes; harness skills don't enforce this categorization
- **File pattern enforcement** — PRIES restricts test file writes to specific glob patterns
- **NOT_TESTABLE workflow** — PRIES requires @check approval for untestable scenarios

### Recommendation
Create new skill: `stdd-test-author-constrained.md`
- Implement PRIES failure classification (MISSING_BEHAVIOR, ASSERTION_MISMATCH, etc.)
- Enforce file pattern restrictions
- Define NOT_TESTABLE escalation workflow
- Reference: `/home/minged01/repositories/harness-workplace/harness-tooling/docs/reference-workflows-ppries/test.md`

---

## Phase 4: Review (Orchestrated Dual Review)

### PRIES Review Requirements
- Orchestrator classifies input: uncommitted changes, commit, branch, PR, or plan document
- Gathers context: diffs, full files, project conventions (AGENTS.md, CONVENTIONS.md)
- Dispatches TWO mandatory reviewers: @check (correctness) and @simplify (complexity)
- Preserves native severity scales (no merging)
- @check verdict gates merge approval
- @simplify recommendations are advisory only

### Mapped Harness Skills

| Skill | Relevance | Notes |
|-------|-----------|-------|
| **review-differential-review** | ✅ High | Security-focused diff review (PRs, commits) |
| **orchestrate-dispatching-parallel-agents** | ✅ High | Parallel agent dispatch for independent tasks |
| **general-finishing-a-development-branch** | 🔶 Medium | Pre-merge validation workflow |
| **skill-auditor** | 🔵 Low | Skill quality review (different domain) |

### Skill Gaps
- **Dual reviewer orchestration** — Harness has parallel dispatch but no specific @check + @simplify pattern
- **Convention discovery** — PRIES auto-loads AGENTS.md, CONVENTIONS.md, .editorconfig; harness doesn't standardize this
- **Severity scale preservation** — No explicit requirement to preserve reviewer-native scales

### Recommendation
Create new skill: `review-orchestrate-dual-review.md`
- Orchestrate @check (correctness) and @simplify (complexity) in parallel
- Auto-discover project conventions (AGENTS.md, CONVENTIONS.md, .editorconfig)
- Report findings with preserved severity scales
- Reference: `/home/minged01/repositories/harness-workplace/harness-tooling/docs/reference-workflows-ppries/review.md`

---

## Phase 5: Simplify (Complexity Review)

### PRIES Simplify Requirements
- Identifies premature optimization, over-abstraction, YAGNI violations
- OUT OF SCOPE: security, reliability, correctness (deferred to @check)
- Protected patterns: retries, circuit breakers, auth/authz, audit logging, migrations
- "Not all complexity is bad" — justifies complexity for real operational needs
- Delete-test methodology: mentally remove component, justify in 1 sentence, verify usage

### Mapped Harness Skills

| Skill | Relevance | Notes |
|-------|-----------|-------|
| **general-solid** | ✅ High | SOLID principles include YAGNI, KISS |
| **python-code-style** | 🔶 Medium | Code quality (overlaps with simplification) |
| **review-differential-review** | 🔵 Low | Security/correctness focus (complementary) |

### Skill Gaps
- **Complexity-specific review framework** — PRIES @simplify has explicit protected patterns and delete-test methodology
- **Separation from correctness review** — Harness skills often blend simplification with correctness

### Recommendation
Create new skill: `review-simplify-complexity.md`
- Implement PRIES delete-test methodology
- Define protected operational patterns (retries, circuit breakers, etc.)
- Explicit scope boundary: NO security/reliability issues
- Reference: `/home/minged01/repositories/harness-workplace/harness-tooling/docs/reference-workflows-ppries/simplify.md`

---

## Phase 6: Check (Correctness Review)

### PRIES Check Requirements
**Note:** PRIES @check agent is referenced in review.md but not detailed in reference-workflows-ppries/. Based on review.md context:
- Evaluates correctness, risks, compliance
- Uses 8-point risk framework: Assumptions, Failure Modes, Edge Cases, Compatibility, Security, Ops, Scale, Testability
- Gates merge approval (blocking verdict)

### Mapped Harness Skills

| Skill | Relevance | Notes |
|-------|-----------|-------|
| **review-differential-review** | ✅ High | Security-focused review with adversarial mindset |
| **review-systematic-debugging** | 🔶 Medium | Root cause analysis for failures |
| **general-verification-before-completion** | ✅ High | Pre-completion validation checks |
| **governance-validate-artifacts** | 🔶 Medium | Artifact validation against schemas |

### Skill Gaps
- **8-point risk framework** — PRIES @check uses structured risk assessment; harness skills lack this taxonomy
- **Blocking verdict authority** — PRIES @check gates merges; harness reviews are advisory

### Recommendation
Create new skill: `review-check-correctness.md`
- Implement 8-point risk framework (Assumptions, Failure Modes, Edge Cases, Compatibility, Security, Ops, Scale, Testability)
- Define blocking verdict authority for merge gates
- Reference: infer from `/home/minged01/repositories/harness-workplace/harness-tooling/docs/reference-workflows-ppries/review.md` and README.md

---

## Cross-Cutting Skills

These skills support multiple PRIES phases:

| Skill | Supports Phases | Purpose |
|-------|----------------|---------|
| **orchestrate-finishing-a-development-branch** | All | Post-implementation workflow (tests pass → merge) |
| **general-using-git-worktrees** | PM, Make | Isolated feature development |
| **general-rtk-usage** | All | Token-optimized command execution (efficiency) |
| **arch-smart-docs** | PM, Review | Codebase documentation generation |
| **context-optimization** | All | Context management for long-running workflows |
| **multi-agent-patterns** | Review | Multi-agent coordination strategies |

---

## Summary: New Skills Required

To fully implement PRIES workflow, create these new skills:

1. **stdd-pm-linear-integration.md** — Linear CLI wrapper, file manifest generation
2. **stdd-make-constrained-implementation.md** — File boundary enforcement, escalation protocol
3. **stdd-test-author-constrained.md** — TDD with failure classification, file pattern restrictions
4. **review-orchestrate-dual-review.md** — @check + @simplify orchestration with convention discovery
5. **review-simplify-complexity.md** — Complexity review with protected patterns
6. **review-check-correctness.md** — 8-point risk framework, blocking verdict authority

### Skill Development Priority

**P0 (Required for minimal viable PRIES):**
- stdd-test-author-constrained.md (TDD is core to PRIES)
- review-check-correctness.md (gates approval)

**P1 (High value):**
- stdd-make-constrained-implementation.md (file boundaries prevent scope creep)
- review-orchestrate-dual-review.md (standardizes dual review pattern)

**P2 (Nice to have):**
- stdd-pm-linear-integration.md (can use raw bash Linear CLI initially)
- review-simplify-complexity.md (can use general-solid initially)

---

## Integration with BMAD Method

PRIES workflow aligns with **BMAD Phase 4: Implementation**. The BMAD phases (Analysis → PM → Architecture) produce artifacts that feed into PRIES PM phase:

```
┌─────────────────────────────────────────────────────────────┐
│          BMAD Phases 1-3 (Planning)                          │
│  Analysis → PM → Architecture                                │
│  Outputs: PRD, ADR, User Stories                             │
└───────────────────┬─────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────┐
│          PRIES Workflow (Implementation)                     │
│  PM → Make → Test → Review → Simplify                        │
│  Inputs: BMAD artifacts (requirements, architecture)         │
│  Outputs: Tested, reviewed code ready for merge             │
└─────────────────────────────────────────────────────────────┘
```

**BMAD Integration Points:**
- BMAD PRD → PRIES PM task specification
- BMAD ADR → PRIES Make implementation constraints
- BMAD User Stories → PRIES Test acceptance criteria

See [integration-bmad-method.md](integration-bmad-method.md) for full BMAD integration architecture.

---

## Actionable Next Steps

### For Opus Agent (Plugin Design Task)

When designing the PRIES workflow plugin:

1. **Reuse existing skills where possible:**
   - stdd-test-driven-development for basic TDD
   - orchestrate-executing-plans for Make phase
   - review-differential-review for Check phase baseline
   - general-solid for Simplify phase baseline

2. **Create new skills for PRIES-specific patterns:**
   - Prioritize P0 skills first (test-author-constrained, check-correctness)
   - Reference PRIES agent definitions in `/home/minged01/repositories/harness-workplace/harness-tooling/docs/reference-workflows-ppries/`
   - Maintain dual frontmatter (Claude Code + OpenCode) per harness standards

3. **Design workflow.yaml manifest:**
   - Define 5 phases (PM → Make → Test → Review → Simplify)
   - Map phase-specific skill sets per this document
   - Implement validation gates (Test failures must be classified, Check must approve)
   - Add convergence rules (Review max 3 iterations per PRIES README)

4. **Test compatibility:**
   - Plugin must work with both Claude Code and OpenCode
   - Skills from sta2e_minimal_vtt `.agents/` must be accessible via harness-tooling installation
   - Verify Linear CLI integration works in sandbox environment

### For User (Sandbox Prep Task)

Before triggering BMAD execution:

1. **Verify Linear CLI installed in sandbox**
2. **Test harness-tooling skill installation** (symlinks from `.claude/` and `.opencode/` to `.agents/`)
3. **Confirm deepwiki, rtk, uv available** in sandbox environment
4. **Validate CGC (CodeGraphContext) local deployment** (not remote for v1)

---

## References

### PRIES Workflow Documentation
- [PRIES README](reference-workflows-ppries/README.md) — Complete architecture
- [PRIES PM Agent](reference-workflows-ppries/pm.md) — Linear integration, requirements
- [PRIES Make Agent](reference-workflows-ppries/make.md) — Constrained implementation
- [PRIES Test Agent](reference-workflows-ppries/test.md) — TDD with failure classification
- [PRIES Review Orchestrator](reference-workflows-ppries/review.md) — Dual review coordination
- [PRIES Simplify Agent](reference-workflows-ppries/simplify.md) — Complexity reduction

### Harness Internal Documentation
- [integration-bmad-method.md](integration-bmad-method.md) — BMAD integration strategy
- [harness-v1-master-plan.md](harness-v1-master-plan.md) — v1 delivery scope
- [WORKFLOW_ORCHESTRATOR_REQUIREMENTS.md](WORKFLOW_ORCHESTRATOR_REQUIREMENTS.md) — Workflow runtime spec

### External Standards
- [agentskills.io](https://agentskills.io/) — Open standard for agent skills
- [Linear CLI Documentation](https://github.com/linearapp/linear/tree/master/packages/cli) — Linear API integration

---

**Document Status:** Complete  
**Created:** 2026-04-26  
**Next Action:** Hand off to Opus agent for PRIES workflow plugin design (Phase 5 of STA2E migration)
