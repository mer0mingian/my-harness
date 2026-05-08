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
