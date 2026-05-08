# Phase 3 Implementation Plan: Discovery & Solution Design

**Status:** Ready to Execute (after Slice 8 complete)  
**Complexity:** 13 story points  
**Priority:** P0 — required for v1.0  
**Sources:** PHASE3-GRILLING-QUESTIONS.md (answered), phase3-gap-learnings.md, Agentic Engineering Workflow.png

---

## Overview

Phase 3 adds the Discovery and Solution Design phases to the multi-agent TDD workflow. Two new commands are introduced, plus supporting templates and artifact infrastructure.

**Constraint:** Phase 3 is **NOT** integrated into `/execute` — users run these commands manually as a separate upstream workflow.

---

## Scope

| Slice | Command/Artifact | Story Points | Dependencies |
|-------|-----------------|-------------|--------------|
| 7a | Templates: PRD + System Constitution | 2 | None |
| 7b | Templates: ADR + Solution Design (C2/C3) | 2 | None |
| 7c | `/speckit.multi-agent.discover` command | 3 | 7a |
| 7d | `/speckit.multi-agent.solution-design` command | 5 | 7a, 7b, c4-* agents |
| 7a+7b | Templates can be built in parallel | — | — |
| 7c+7d | Commands must be sequential (7c → 7d for full flow) | — | — |

**Critical Path:** Templates (7a/7b parallel) → /discover (7c) → /solution-design (7d)

---

## Artifact Reference

### PRD (`${feature_id}-prd.md`)

**Created by:** `/speckit.multi-agent.discover`  
**Sections (from Agentic Engineering Workflow.png Discovery panel):**

```
---
type: prd
feature_id: ${feature_id}
version: 1.0
status: draft | approved
---

# PRD: ${feature_title}

## What & Why
## Business Value
## Measurability
## Goals & No-goals
## Risks & Stories
## Dependencies
## People
## Metrics
```

**Behaviour on re-run:** Merge/update (not overwrite). Warn user if PRD already exists, then proceed.

---

### System Constitution (`technical-constitution.md`)

**Created/extended by:** `/speckit.multi-agent.discover`  
**Scope:** System-wide (not per-feature). Lives in `system-name-agent-workspace` repository.  
**Sections (from Agentic Engineering Workflow.png Discovery panel):**

```
---
type: system-constitution
version: 1.0
---

# System Constitution: ${system_name}

## Tech Radar
## Team Tech Skills
## Compliance & Governance

## Non-Functional Requirements
### Observability
### Testing Strategy
### Performance
### Scalability
### Reliability
```

**Behaviour on re-run:** Silently extend/merge (no warning). Constitution is shared state.

---

### ADR (`${feature_id}-adr.md`)

**Created by:** `/speckit.multi-agent.solution-design`  
**Structure:** Nygard pattern, compact (2 pages max).  
**Solution count:** Agent suggests 3 (minimum 2), user moderates.

```
---
type: adr
feature_id: ${feature_id}
status: proposed | accepted | superseded
decision_date: ${date}
---

# ADR: ${decision_title}

## Context & Problem Statement

## Decision Criteria
(Fixed set: performance, maintainability, cost, complexity — extend if user requests)

## Solution Alternative 1: ${name}
### Description
### C1 Context Diagram (mermaid)
### C2 Container Diagram (mermaid)
### Pros / Cons

## Solution Alternative 2: ${name}
### Description
### C1 Context Diagram (mermaid)
### C2 Container Diagram (mermaid)
### Pros / Cons

## Solution Alternative 3: ${name}
### Description
### C1 Context Diagram (mermaid)
### C2 Container Diagram (mermaid)
### Pros / Cons

## Recommendation
(Agent recommends, user confirms and decides)

## Decision
## Consequences
```

**User Review Gate:** Agent presents ADR, user confirms chosen solution before C2/C3 generation proceeds.

---

### Solution Design (`${feature_id}-solution-design.md`)

**Created by:** `/speckit.multi-agent.solution-design` (after ADR approved)  
**Based on:** Chosen solution from ADR, C2/C3 levels (Container + Component).  
**Note:** C4 Code level is implicit in implementation; not in this artifact.

```
---
type: solution-design
feature_id: ${feature_id}
adr_ref: ${feature_id}-adr.md
status: draft
---

# Solution Design: ${feature_title}

## Decomposition View
### C2 Container Diagram (mermaid)
### C3 Component Diagram (mermaid)

## Dependency View
### Internal Dependencies
### External Dependencies
### Coupling Analysis

## Interface View
### External API Contracts
### Internal Interface Definitions
### Event Schemas (if applicable)

## Data Design View
### Data Flow Diagram (mermaid)
### Entity-Relationship Diagram (mermaid)
### Key Schemas
```

---

## Slice 7a: PRD + System Constitution Templates (2 pts)

**Tasks:**
- S7a-001: Create `templates/prd-template.md` with YAML frontmatter and all sections (1 pt)
- S7a-002: Create `templates/system-constitution-template.md` with all NFR sections (1 pt)

**Acceptance criteria:**
- [ ] Both templates have valid YAML frontmatter
- [ ] All required sections present (per diagram)
- [ ] Templates include brief inline guidance per section
- [ ] Templates registered in `harness-tdd-config.yml.template` under `artifacts.types`

---

## Slice 7b: ADR + Solution Design Templates (2 pts)

**Tasks:**
- S7b-001: Create `templates/adr-template.md` with 3-alternative structure and C1/C2 mermaid placeholders (1 pt)
- S7b-002: Create `templates/solution-design-template.md` with 4-view structure and C2/C3/ERD mermaid placeholders (1 pt)

**Acceptance criteria:**
- [ ] ADR template has sections for 3 alternatives (each with C1 + C2 diagram blocks)
- [ ] Solution Design template has Decomposition/Dependency/Interface/Data views
- [ ] Each mermaid block has a starter skeleton (not empty)
- [ ] Templates registered in `harness-tdd-config.yml.template`

---

## Slice 7c: `/speckit.multi-agent.discover` Command (3 pts)

**File:** `commands/discover.md`  
**Skills used:** `general-grill-with-docs`  
**Agent:** None (orchestrator uses grill-me directly)

**Workflow:**
```
Step 1: Check prerequisites (feature_id provided, spec artifact exists?)
  - If PRD already exists: mention it and proceed
  - If spec exists: load it as context for grill-me

Step 2: Load existing context
  - Load spec artifact if exists
  - Load system constitution if exists (for context, not to overwrite)

Step 3: Run grill-me session (general-grill-with-docs skill)
  - Relentless questioning throughout artifact generation
  - Goal: fill all PRD sections to consensus
  - Allow user to defer unknowns (saved as open questions)
  - Stop: when agent reaches consensus OR user signals done

Step 4: Generate/update PRD
  - Fill template with grill-me outputs
  - Merge with existing PRD if present
  - Save unanswered questions to ${feature_id}-open-questions.md

Step 5: Generate/update System Constitution
  - Extract tech constraints, NFRs raised during grill-me
  - Merge into existing system constitution (no warning)
  - If no constitution exists: create from template

Step 6: Validate artifacts (call validate_artifact_structure.py)
  - Post-generation check, warn-only
  - Escalate to human with diagnostics if issues found

Step 7: Report
  - Show artifacts created/updated
  - Show open questions if any
  - Suggest: "Run /speckit.multi-agent.solution-design ${feature_id} next"
```

**Acceptance criteria:**
- [ ] Command uses grill-with-docs skill throughout
- [ ] PRD created with all required sections
- [ ] System Constitution extended/created silently
- [ ] Open questions saved to separate file (not in PRD)
- [ ] Re-run merges, does not overwrite
- [ ] Artifact validation runs post-generation (warn, not block)

---

## Slice 7d: `/speckit.multi-agent.solution-design` Command (5 pts)

**File:** `commands/solution-design.md`  
**Skills used:** `arch-mermaid-diagrams`, `arch-c4-architecture`, `arch-smart-docs`  
**Agents invoked:** `c4-context`, `c4-container`, `c4-component` (sequential)

**Workflow:**
```
Step 1: Validate prerequisites
  - Validate c4-* agents exist (fail fast if missing)
  - Check PRD exists: if missing, warn about spec drift and ask user for problem description
  - Check System Constitution exists: if missing, warn
  - Load: PRD + Constitution + spec + ADR (if exists) + codebase (if src/ exists)

Step 2: Codebase analysis (if no deepwiki/C4 analysis available)
  - Use arch-smart-docs skill to scan src/ for components
  - Only if no existing c4 analysis or deepwiki docs found

Step 3: Generate ADR
  - Agent generates 3 solution alternatives (minimum 2)
  - Each alternative: description + C1 Context + C2 Container mermaid diagrams
  - Fixed comparison criteria: performance, maintainability, cost, complexity
  - Agent recommends solution with rationale
  - PAUSE: present ADR to user for review and decision

Step 4: User confirms solution choice
  - User selects alternative (or accepts recommendation)
  - Update ADR status: proposed → accepted
  - Note chosen solution for C2/C3 generation

Step 5: Invoke c4-context agent (sequential)
  - Context: PRD + Constitution + ADR (chosen solution) + codebase analysis
  - Task: Generate C1 Context diagram for chosen solution
  - Output: C1 section in solution-design.md
  - On contradiction: interrupt, ask user for resolution

Step 6: Invoke c4-container agent (sequential)
  - Context: ALL previous (PRD + Constitution + ADR + C1 output + codebase)
  - Task: Generate C2 Container diagram
  - Output: C2 section in solution-design.md
  - On contradiction: interrupt, ask user for resolution

Step 7: Invoke c4-component agent (sequential)
  - Context: ALL previous (PRD + Constitution + ADR + C1 + C2 output + codebase)
  - Task: Generate C3 Component diagram
  - Output: C3 section in solution-design.md
  - On contradiction: interrupt, ask user for resolution

Step 8: Generate remaining views
  - Dependency View: extract from C2/C3 outputs
  - Interface View: extract API contracts from C2/C3
  - Data Design View: data flow + ERD diagrams

Step 9: Validate artifacts (call validate_artifact_structure.py)
  - Post-generation check, warn-only
  - Escalate to human with diagnostics if issues found

Step 10: Report
  - Show ADR path
  - Show solution-design.md path
  - Suggest: "Run /speckit.plan ${feature_id} next (Refinement phase)"
```

**Acceptance criteria:**
- [ ] Validates c4-* agents exist before starting (fail fast)
- [ ] Warns if PRD/Constitution missing, proceeds with user input
- [ ] ADR generates 3 alternatives with C1/C2 mermaid per alternative
- [ ] User review gate: pauses after ADR, waits for solution confirmation
- [ ] C4 agents invoked sequentially with full cumulative context
- [ ] Interrupts on contradiction, requests user resolution
- [ ] Solution Design artifact has all 4 views
- [ ] Artifact validation runs post-generation (warn, not block)

---

## Integration with Phase 2

### Warnings Added to Existing Commands

Per Q13a/Q13b (warn-only, do not block):

**`commands/test.md`** — add to Step 1 (Prerequisites):
```
If ${feature_id}-solution-design.md does not exist:
⚠️ Warning: No solution design found. Tests will be based on spec only.
         Consider running /speckit.multi-agent.solution-design first.
Proceed anyway.
```

**`commands/commit.md`** — add to Step 1 (Validation):
```
Check for Phase 3 artifacts:
- PRD: ${feature_id}-prd.md
- System Constitution: technical-constitution.md
- Solution Design: ${feature_id}-solution-design.md

If any missing:
⚠️ Warning: Phase 3 artifacts missing. Commit proceeds but completeness reduced.
```

### Minimum Artifact Set for Commit

Per Q13c (required = block, missing = warn only):
- ✅ PRD — required (warn if missing)
- ✅ System Constitution — required, may pre-exist (warn if missing)
- ✅ C4 diagrams — Container level sufficient for existing systems (warn if missing)
- ✅ Review artifacts — Arch review + Code review (BLOCK if missing — Phase 2 gate)
- ⬜ ADR — warn if missing
- ⬜ Test design — warn if missing
- ⬜ Implementation notes — optional
- ⬜ Workflow summary — generated by /commit

---

## Configuration Updates

Add to `harness-tdd-config.yml.template` under `artifacts.types`:

```yaml
artifacts:
  types:
    # Existing
    spec: "spec"
    test_design: "test-design"
    impl_notes: "impl-notes"
    arch_review: "arch-review"
    code_review: "code-review"
    workflow_summary: "workflow-summary"
    
    # New (Phase 3)
    prd: "prd"
    system_constitution: "technical-constitution"
    adr: "adr"
    solution_design: "solution-design"
    open_questions: "open-questions"

artifacts:
  mandatory:
    # Existing
    test_design: true
    arch_review: true
    code_review: true
    workflow_summary: true
    
    # New (warn-only)
    prd: false         # warn if missing, don't block
    system_constitution: false
    adr: false
    solution_design: false
```

---

## Extension Manifest Update

Add to `extension.json`:

```json
"discover": {
  "file": "commands/discover.md",
  "description": "Discovery phase: generate PRD and System Constitution via grill-me",
  "usage": "/speckit.multi-agent.discover <feature-id>",
  "arguments": [
    {"name": "feature_id", "required": true, "description": "Feature identifier"}
  ]
},
"solution-design": {
  "file": "commands/solution-design.md",
  "description": "Solution Design: generate ADR and C2/C3 architecture diagrams",
  "usage": "/speckit.multi-agent.solution-design <feature-id>",
  "arguments": [
    {"name": "feature_id", "required": true, "description": "Feature identifier"}
  ]
}
```

---

## Open Points

- **Mermaid validation:** Deferred to after Phase 4. Install `mermaid-fixer` (https://github.com/sopaco/mermaid-fixer) in sandbox container.
- **Q17b (Global vs per-project config):** Recommendation — tech radar and team skills are good candidates for project-level defaults extracted from System Constitution; all other config stays per-project.

---

## Success Criteria

Phase 3 complete when:
- [ ] 4 templates created (PRD, System Constitution, ADR, Solution Design)
- [ ] `/speckit.multi-agent.discover` generates PRD + extends System Constitution
- [ ] `/speckit.multi-agent.discover` re-run merges correctly
- [ ] `/speckit.multi-agent.solution-design` validates agents, creates ADR with 3 alternatives
- [ ] User review gate pauses for solution confirmation
- [ ] c4-* agents invoked sequentially with cumulative context
- [ ] Solution Design artifact contains all 4 views
- [ ] Phase 2 commands warn (not block) on missing Phase 3 artifacts
- [ ] Extension manifest updated with 2 new commands

---

## Change Proposal: Remove Structural Markdown Tests

**Status:** Proposed
**Date:** 2026-05-08
**Scope:** Test suite cleanup — applies to remaining Phase 3 work (S7d, extension.json) and existing Phase 2/Slice 8 test files
**Driver:** Question raised — is unit-testing markdown files for structural content (e.g., "does this file contain `## Step 5`?") reasonable for a static template package that creates no running service?

---

### Context

This project ships a **static SpecKit extension package**:

- Markdown command files (`commands/*.md`) — interpreted by LLM agents at runtime, not executed
- Markdown templates (`templates/*.md`) — filled by agents, not executed
- Python helper scripts (`scripts/`, `lib/`) — actual runtime logic
- Hook handlers (`hooks/handlers/*.py`) — Python enforcement logic

The current test suite mixes two fundamentally different test categories:

1. **Python logic tests** — drive functions, assert behaviour. Standard unit tests.
2. **Markdown structural tests** — open a `.md` file, `assert "## Step 5" in content`, etc. These test that human-authored prose contains specific section headings.

Markdown structural tests were planned as TDD-RED scaffolding for command authoring (S7c, S8-001..S8-005) — they expressed *what the markdown should describe*. Once the markdown is written and the workflow operates as intended end-to-end, these tests primarily lock the prose against editorial change. They do not catch behavioural regressions because there is no behaviour to regress in a `.md` file.

---

### Inventory: What Exists Today

`grep -l "\.md" tests/unit/*.py` returns 12 files, but only 6 of them are **purely structural markdown tests**. The others read markdown as fixtures for Python logic under test (e.g., `test_extract_acceptance_criteria.py` reads a sample spec.md to feed the parser).

**Test file counts (`grep -c "def test_"`):**

| File | Tests | Category | Verdict |
|---|---|---|---|
| `test_command_commit.py` | 6 | Structural markdown (commit.md) | **REMOVE** |
| `test_command_discover.py` | 54 | Structural markdown (discover.md) | **REMOVE** |
| `test_command_implement.py` | 6 | Structural markdown (implement.md) | **REMOVE** |
| `test_command_review.py` | 14 | Structural markdown (review.md) | **REMOVE** |
| `test_command_test.py` | 7 | Structural markdown (test.md) | **REMOVE** |
| `test_templates.py` | 56 | Structural markdown (templates/*.md) | **REMOVE** |
| `test_jira_local.py` | 9 | Python logic (`lib/jira_local.py`) | KEEP |
| `test_validate_artifact_structure.py` | 39 | Python logic (script) — uses .md fixtures | KEEP |
| `test_validate_feature_artifacts.py` | 12 | Python logic (script) | KEEP |
| `test_extract_acceptance_criteria.py` | 11 | Python logic — uses .md fixtures | KEEP |
| `test_detect_review_convergence.py` | 39 | Python logic (script) | KEEP |
| `test_tdd_sequence_enforcer.py` | 29 | Python logic (hook handler) | KEEP |
| `test_escalate_broken_tests.py` | 8 | Python logic | KEEP |
| `test_evidence_gate_enforcer.py` | 22 | Python logic | KEEP |
| `test_file_gate_enforcer.py` | 11 | Python logic | KEEP |
| `test_parse_pytest_output.py` | 10 | Python logic | KEEP |
| `test_run_integration_checks.py` | 22 | Python logic | KEEP |
| `test_validate_green_state.py` | 15 | Python logic | KEEP |
| `test_validate_red_state.py` | 11 | Python logic | KEEP |

**Removal totals:** 6 files, ~143 test cases.
**Retained:** 13 files, ~238 test cases of genuine Python logic.

---

### What Protection Do Structural Markdown Tests Provide?

| Protection | Worth keeping a test suite for? |
|---|---|
| Catch accidental deletion of a step heading | No — `git diff` and PR review catch this trivially |
| Validate YAML frontmatter parses | Yes — but belongs in a single linter pass, not ~150 unit tests |
| Catch "did the author forget to mention `agent_timeout`?" | No — runtime behaviour proves this; if the agent ignores config the workflow fails end-to-end |
| Lock prose wording (`"partial results"`, `"escalate to human"`) | No — this is editorial drift, not regression |
| Verify cross-file references (template paths, skill names) | Partially — better handled by `lib/validate_manifests.py` already in repo |

The **structural drift risk** is real (someone could delete a Step 5) but the **cost-to-protection ratio is poor**: ~143 tests with high maintenance overhead (every prose edit risks breaking 3-5 tests) protect against an editorial mistake that PR review catches for free.

---

### What to Remove

Delete these 6 test files entirely:

- `tests/unit/test_command_commit.py`
- `tests/unit/test_command_discover.py`
- `tests/unit/test_command_implement.py`
- `tests/unit/test_command_review.py`
- `tests/unit/test_command_test.py`
- `tests/unit/test_templates.py`

**Removal scope is clean** — none of these files exercise Python logic; they exclusively assert string presence in markdown files.

---

### What to Keep

All Python logic tests stay untouched:

- All `scripts/*.py` tests (`validate_artifact_structure`, `validate_feature_artifacts`, `extract_acceptance_criteria`, `detect_review_convergence`, `parse_pytest_output`, `run_integration_checks`, `validate_green_state`, `validate_red_state`, `escalate_broken_tests`).
- All `lib/*.py` tests (`jira_local.py`).
- All `hooks/handlers/*.py` tests (`tdd_sequence_enforcer`, `evidence_gate_enforcer`, `file_gate_enforcer`).

Tests that **incidentally** use markdown as test fixtures (e.g., `test_extract_acceptance_criteria.py` constructs a sample spec.md to feed the parser) are kept as-is — they test Python parsing logic, not markdown structure.

---

### Replacement Strategy

A single lightweight CI-level structural validator replaces ~143 unit tests:

**1. Reuse existing `lib/validate_manifests.py`** (already in repo):
   - Validates `extension.json` structure
   - Validates YAML config (`harness-tdd-config.yml.template`)
   - Validates agent definition files
   - Run in pre-commit / CI: `python lib/validate_manifests.py --all`

**2. Add `yamllint` for frontmatter** (one-liner in pre-commit):
   ```yaml
   - repo: https://github.com/adrienverge/yamllint
     hooks:
       - id: yamllint
         files: ^(commands|templates)/.*\.md$
         args: ['-d', 'relaxed']
   ```
   Catches malformed frontmatter across all 9 commands and 8 templates in a single pass.

**3. Optional lightweight structure-check script** (~30 LOC, replaces `test_templates.py`):
   - One YAML manifest declaring required sections per template type
   - One Python function: walks `templates/` and `commands/`, asserts each declared section heading exists
   - Run in CI; one assertion per file, not 56
   - Single source of truth — when the spec changes, edit the manifest, not 3 test files

**Net result:** Same protection (frontmatter validity, presence of required sections), one-tenth the surface area, far less editorial coupling.

---

### Impact on Acceptance Criteria

Acceptance criteria across SLICE8-CONFIG-PLAN.md and PHASE3-IMPLEMENTATION-PLAN.md were **never explicitly worded as "unit tests for markdown structure exist"**. They are worded as behavioural outcomes (e.g., "Config `parallel_enabled: true` triggers parallel dispatch instructions in command markdown"). The test suite added structural markdown tests as the *enforcement mechanism* for these criteria.

No criterion needs **rewording** — what changes is the *verification mechanism*:

| Plan / Slice | AC (excerpt) | Old verification | New verification |
|---|---|---|---|
| SLICE8 S8-001 | "Config `parallel_enabled: true` triggers parallel dispatch instructions" | `test_command_review.py::test_step7_has_parallel_enabled_true_branch` | Manual review + end-to-end run + structure-check script |
| SLICE8 S8-002 | "Each command passes timeout value to agent invocation instructions" | `test_command_{test,implement,review,commit}.py` timeout tests | yamllint + end-to-end run with config |
| SLICE8 S8-003 | "Script validates YAML frontmatter syntax" | `test_validate_artifact_structure.py` (KEEP) | unchanged |
| SLICE8 S8-004 | "Convergence detected when two consecutive cycles produce same findings" | `test_detect_review_convergence.py` (KEEP) | unchanged |
| SLICE8 S8-005 | "Commit command calls jira_local when `auto_create_stories: true`" | `test_jira_local.py` (KEEP) — Python side is tested | unchanged for Python; commit.md side moves to E2E |
| Slice 7a/7b | "Templates have valid YAML frontmatter, all required sections present" | `test_templates.py::Test{SystemConstitution,SolutionDesign}Template` | yamllint + structure-check manifest |
| Slice 7c | "Command uses grill-with-docs skill throughout, PRD created with all required sections" | `test_command_discover.py` | yamllint frontmatter + manual PR review + Phase 4 dogfood test |
| Slice 7d | (still to be authored — see story-point impact below) | (would have been `test_command_solution_design.py`) | Skip structural tests entirely |

**One Validation Checklist item in SLICE8-CONFIG-PLAN.md should be reworded:**

- Current: "All 5 features implemented" + a bullet for each feature
- Add: "End-to-end smoke test of /review with parallel_enabled=true and =false produces correct artifacts"
- Add: "Pre-commit yamllint passes on all `commands/*.md` and `templates/*.md`"

---

### Story Point Impact

| Task | Original estimate | New estimate | Delta |
|---|---|---|---|
| S7d `/speckit.multi-agent.solution-design` command | 5 pts | **3 pts** | −2 pts |
| extension.json update | (sub-task of slice integration, ~0.5 pt) | unchanged | 0 |
| New: structure-check manifest + script | — | +1 pt | +1 |
| New: yamllint + pre-commit hook config | — | +0.5 pt | +0.5 |
| Removal of 6 test files | — | 0 (mechanical delete) | 0 |

**Net for remaining Phase 3 work:** **−0.5 pts** (5 → 4.5)

Rationale for S7d reduction: the original 5-pt estimate budgets ~40-50% for authoring the structural test file (≥50 unit tests akin to `test_command_discover.py`). Removing that scope, the command-authoring + agent-orchestration logic is **3 pts**.

---

### Risks of Removal

1. **Loss of TDD-RED scaffolding for new commands.** Mitigation: structure-check manifest serves the same purpose at a fraction of the maintenance cost. New command authoring follows: write manifest entry → write command → run structure-check → run E2E.
2. **Editorial regressions go uncaught until E2E.** Mitigation: yamllint catches the only failure mode that auto-detection helps with (frontmatter syntax). Section drift is caught by the structure-check manifest.
3. **No automated check that "Step 5 is named X."** Mitigation: this is the right level of looseness for prose. Section-name churn during authoring is a feature, not a bug.

---

### Recommendation: GO

**Rationale:**

- These tests test the wrong layer. Markdown is a static asset interpreted at runtime by an LLM. Asserting `"## Step 5"` in a string proves nothing about whether the agent will follow Step 5.
- The maintenance cost is high (6 files, 143 tests, every prose edit cascades) and grows linearly with each new command/template.
- The **real** protection (frontmatter validity, required-section presence) is recoverable with `yamllint` + a ~30 LOC structure-check script driven by a single YAML manifest.
- Python logic tests remain untouched — the genuine "behaviour" surface keeps full coverage.
- Reduces remaining S7d cost from 5 pts to 3 pts, plus a small one-time +1.5 pt investment in the replacement validators (net **−0.5 pt** for Phase 3).

**Suggested execution order:**

1. Author `lib/validate_artifact_sections.py` + section-manifest YAML (1 pt).
2. Wire `yamllint` + new validator into pre-commit and CI (0.5 pt).
3. Delete the 6 structural test files in a single commit referencing this proposal.
4. Author S7d (`commands/solution-design.md`) without an accompanying structural test file — verify via E2E + section-manifest entry.
5. Update `extension.json` (sub-task of S7d, no change).
6. Update SLICE8-CONFIG-PLAN.md Validation Checklist with the new yamllint + smoke-test items.

**No-go conditions** (would flip recommendation to KEEP):

- If the project intends to ship structural markdown tests as a *runtime guardrail* (e.g., to validate user-installed extensions). Currently it does not.
- If editorial churn protection is more valuable than ease of revision. Given the project is in active authoring (Phase 3 not yet complete), the opposite is true.
