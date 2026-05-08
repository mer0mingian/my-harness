# Technical-Governance Branch Analysis

**Date:** 2026-05-08  
**Reviewer:** Claude Code  
**Decision:** ARCHIVE (do not merge)

## Executive Summary

The feat/technical-governance branch contains an alternative "Phase 0" governance workflow that conflicts with the current SpecKit multi-agent TDD extension (Phases 1-3 complete on dev branch). The branch should be archived, not merged.

## Branch Overview

- **Divergence Point:** Commit 8034741 ("updated docs")
- **Commits Since Divergence:** 50 commits on dev, 6 commits on feat/technical-governance
- **Changes:** 337 files changed, 7,464 insertions(+), 57,798 deletions(-)
- **Net Effect:** -50,334 lines (massive deletion)

## What the Branch Contains

### Added (7,464 lines)

1. **Governance Skills** (5 new skills):
   - governance-interview-tech-stack
   - governance-constitution-writer
   - governance-nfr-writer
   - governance-test-strategy-writer
   - governance-validate-artifacts

2. **Governance Agents** (4 new agents):
   - governance-lead
   - governance-constitution-author
   - governance-nfr-specialist
   - governance-test-architect

3. **Governance Commands** (4 new commands):
   - /governance-setup
   - /governance-update-constitution
   - /governance-add-nfr
   - /governance-validate

4. **Documentation & Templates**:
   - docs/governance-workflow.md
   - docs/technical-governance-integration.md
   - templates/governance/ (3 templates)
   - examples/governance/sta2e-vtt/ (4 example artifacts)
   - schemas/governance/ (3 JSON schemas)

### Deleted (57,798 lines)

The branch **deleted the entire SpecKit multi-agent TDD extension**:

1. **Complete spec-kit-multi-agent-tdd/ directory**:
   - All commands (commit.md, discover.md, execute.md, implement.md, review.md, test.md)
   - All Python implementations (execute.py, implement.py, test.py)
   - All libraries (parse_test_evidence.py, validate_artifacts.py, etc.)
   - All tests (92+ test files)
   - All hooks and handlers
   - extension.json manifest

2. **SpecKit Documentation**:
   - docs/speckit-tdd/plans/ (7 planning documents)
   - spec-kit-multi-agent-tdd/docs/ (all reference documentation)

3. **Marketplace Skills**:
   - arch-c4-architecture (entire skill)
   - arch-mermaid-diagrams (entire skill)
   - dev-backend-to-frontend-handoff (entire skill)
   - Multiple other mature skills

4. **PRIES Workflow Artifacts**:
   - All PRIES agents (pries-check.md, pries-make.md, etc.)
   - All PRIES commands
   - All PRIES examples and documentation

## Architectural Conflict

### Current Architecture (dev branch)

The SpecKit multi-agent TDD extension represents **Phases 1-3 completed work**:

- Phase 1: Core TDD commands (implement, test, review)
- Phase 2: Orchestration and validation
- Phase 3: Discovery and solution-design commands
- Currently working on: Phase 4 (migration to new architecture)

**Key artifacts on dev:**
- spec-kit-multi-agent-tdd/ complete implementation
- .agents/speckit/multi-agent/commands/
- Full test suite with evidence-based validation
- Markdown-based command architecture (ADR-003)

### Technical-Governance Approach

The governance branch proposes a **different "Phase 0"** that:

1. Runs **before** SpecKit workflow
2. Generates governance artifacts (constitution, NFR catalog, test strategy)
3. Uses these artifacts to **constrain** the BMAD/PRIES workflow

**Conceptual conflict:**
- SpecKit workflow is **already implemented** (Phases 1-3)
- Governance workflow assumes SpecKit **doesn't exist yet**
- The branch deleted SpecKit to make room for governance approach

## Why Archive (Not Merge)

### 1. Complete Supersession

The governance concepts are valuable but should be integrated into the **existing** SpecKit extension, not replace it:

- Constitution concepts → Already in `docs/speckit-tdd/plans/CONSTITUTION-Multi-Agent-TDD.md`
- NFR tracking → Should be added to existing workflow, not precede it
- Test strategy → Already encoded in SpecKit test commands

### 2. Destructive Changes

Merging would delete:
- 3 months of completed SpecKit work
- 92+ passing test files
- All Phase 1-3 deliverables
- Mature marketplace skills unrelated to governance

### 3. Architectural Mismatch

- **Governance assumes:** Blank slate, start with constraints
- **Reality:** SpecKit TDD workflow already operational
- **Correct approach:** Enhance SpecKit with governance features

### 4. Timeline Inconsistency

The branch was created ~50 commits ago when the architecture was different. It does not account for:

- ADR-003 (markdown-based commands)
- PRIES workflow archival decision
- Documentation reorganization (commit 69d2547)
- Current Phase 4 migration work

## Salvageable Concepts

These governance concepts should be preserved and integrated into SpecKit:

1. **Governance Skills** (5 skills):
   - Interview-driven tech stack documentation
   - Constitution authoring with RFC-2119
   - NFR catalog with EARS notation
   - Test strategy with pyramid ratios
   - Schema-based validation

2. **Integration Points**:
   - How governance artifacts feed BMAD phases
   - NFR cross-referencing in test designs
   - Constitution enforcement in architecture reviews

3. **STA2E VTT Example**:
   - Real-world example artifacts
   - Validation patterns

## Recommended Actions

### 1. Archive the Branch

Similar to ADR-003 (PRIES archival):

```bash
# On feat/technical-governance
echo "[ARCHIVAL DOC]" > BRANCH_ARCHIVED.md
git add BRANCH_ARCHIVED.md
git commit -m "docs: archive technical-governance branch (superseded by SpecKit integration)"
git push origin feat/technical-governance

# Delete branch
git checkout dev
git branch -d feat/technical-governance
git push origin --delete feat/technical-governance
```

### 2. Create Integration Task

Create a new task to integrate governance concepts into SpecKit:

- **New command:** `/speckit-govern` (runs before first feature)
- **Location:** spec-kit-multi-agent-tdd/commands/govern.md
- **Integrates:** Constitution, NFR catalog, test strategy generation
- **Uses:** Existing SpecKit infrastructure, not replacement

### 3. Document Decision

Create ADR-004 documenting:
- Why technical-governance was archived
- How governance concepts will be integrated into SpecKit
- Migration path for the 5 governance skills

## Conclusion

**Decision: ARCHIVE**

The feat/technical-governance branch represents valuable thinking about project governance, but it fundamentally conflicts with the existing SpecKit implementation by deleting it entirely. The correct path is to:

1. Archive this branch
2. Preserve the governance concepts
3. Integrate them into the existing SpecKit extension as enhancement

This maintains architectural continuity while capturing the governance workflow value.

## References

- Current SpecKit: `spec-kit-multi-agent-tdd/` on dev branch
- ADR-003: PRIES workflow archival (similar case)
- Documentation reorganization: Commit 69d2547
- Phase 4 migration: Current worktree work
