# ADR 004: Archive feat/technical-governance Branch

**Status:** Accepted  
**Date:** 2026-05-08  
**Decision Makers:** Development Team

## Context

The feat/technical-governance branch was created to implement a "Phase 0" governance workflow that would generate constitutional governance artifacts (technical constitution, NFR catalog, test strategy) before the main BMAD/PRIES implementation workflow.

The branch contained valuable concepts:

- 5 governance skills (interview, constitution writer, NFR writer, test strategy writer, validator)
- 4 governance agents (lead, constitution author, NFR specialist, test architect)
- 4 governance commands (/governance-setup, update, add-nfr, validate)
- STA2E VTT worked examples
- JSON schemas and validation tooling
- Integration documentation

However, the branch diverged from the main development line ~50 commits ago and made architectural decisions that conflict with the current SpecKit multi-agent TDD extension.

## Decision

We decided to archive and delete the feat/technical-governance branch because:

1. **Destructive Changes**: The branch deleted the entire `spec-kit-multi-agent-tdd/` implementation (Phases 1-3 completed work, 57,798 lines removed)
2. **Architectural Conflict**: Governance workflow assumes SpecKit doesn't exist yet, but SpecKit is already operational with 92+ tests
3. **Timeline Divergence**: Branch missed ADR-003 (markdown commands), documentation reorganization, and PRIES archival decisions
4. **Wrong Integration Point**: Governance concepts should enhance existing SpecKit, not precede or replace it

## What Was on the Branch

### Added (7,464 lines)

**Skills:**
- `governance-interview-tech-stack` - Structured 8-block interview filling gaps repo doesn't encode
- `governance-constitution-writer` - RFC-2119 enforced constitutional authoring
- `governance-nfr-writer` - ISO/IEC 25010 NFR catalog with EARS templates, stable NFR-<CAT>-NNN IDs
- `governance-test-strategy-writer` - Test pyramid ratios, Playwright patterns, CI matrix
- `governance-validate-artifacts` - Schema + EARS + RFC-2119 + cross-reference validation

**Agents:**
- `governance-lead` - Phase 0 orchestrator (interview → dispatch authors → validate)
- `governance-constitution-author` - Writes TECHNICAL_CONSTITUTION.md
- `governance-nfr-specialist` - Writes NFR_CATALOG.md
- `governance-test-architect` - Writes TEST_STRATEGY.md

**Commands:**
- `/governance-setup` - End-to-end Phase 0 entry point
- `/governance-update-constitution <section>` - Amend single section
- `/governance-add-nfr <subject>` - Add one NFR with stable ID
- `/governance-validate` - On-demand validation

**Documentation:**
- `docs/governance-workflow.md` - Usage guide
- `docs/technical-governance-integration.md` - BMAD/PRIES integration matrix
- `examples/governance/sta2e-vtt/` - 4 worked example artifacts
- `schemas/governance/` - 3 JSON schemas
- `templates/governance/` - 3 markdown templates

### Deleted (57,798 lines)

The branch deleted:

1. **Complete SpecKit Implementation**:
   - All spec-kit-multi-agent-tdd/commands/ (discover, solution-design, implement, test, review, commit)
   - All Python libraries (parse_test_evidence.py, validate_artifacts.py, test_runner.py)
   - All 92+ test files
   - extension.json manifest
   - All hooks and handlers

2. **SpecKit Documentation**:
   - docs/speckit-tdd/plans/ (7 planning documents)
   - All reference documentation

3. **Marketplace Skills**:
   - arch-c4-architecture (complete skill)
   - arch-mermaid-diagrams (complete skill)
   - dev-backend-to-frontend-handoff (complete skill)
   - Multiple other mature skills

4. **PRIES Workflow** (already archived per ADR-003):
   - All PRIES agents and commands
   - PRIES examples and integration docs

## Consequences

### Positive

- **Preserves Completed Work**: SpecKit Phases 1-3 remain intact on dev branch
- **Clearer Direction**: Governance will be integrated into SpecKit, not separate from it
- **Architectural Continuity**: Maintains markdown-based command architecture (ADR-003)
- **Salvages Concepts**: Governance skills and patterns preserved for integration

### Neutral

- **Historical Record**: Branch commits preserved in git reflog for 90 days
- **Archival Document**: BRANCH_ARCHIVED.md committed to branch before deletion

### Negative

- **Rework Required**: Governance concepts must be re-integrated into existing SpecKit
- **Delayed Feature**: Governance workflow not immediately available

## Alternative Considered: Merge and Refactor

We considered merging the governance concepts and then re-adding SpecKit. This was rejected because:

1. Would require massive conflict resolution (337 files)
2. Would break dev branch temporarily
3. Would lose git history continuity for SpecKit
4. Integration approach is architecturally superior anyway

## Migration Path

### Immediate Actions (Completed)

1. ✅ Created BRANCH_ARCHIVED.md on feat/technical-governance
2. ✅ Committed and pushed archival document
3. ✅ Deleted local branch: `git branch -d feat/technical-governance`
4. ✅ Deleted remote branch: `git push origin --delete feat/technical-governance`
5. ✅ Documented decision in this ADR

### Integration Plan (Future Work)

Governance concepts will be integrated into SpecKit as an enhancement:

#### Phase 1: Create /speckit-govern Command

New command: `spec-kit-multi-agent-tdd/commands/govern.md`

- Runs when starting new project (before first `/speckit-spec`)
- Generates `docs/governance/` directory with 3 artifacts
- Uses existing SpecKit infrastructure
- Optional: Can run standalone or as part of `/speckit-init`

#### Phase 2: Migrate Governance Skills

Move 5 governance skills from archived branch to `.agents/skills/`:

- Extract skills from branch history: `git show <commit>:.agents/skills/governance-*/`
- Adapt for SpecKit context (reference SpecKit artifacts)
- Update skill manifests for agentskills.io format compliance

#### Phase 3: Enhance SpecKit Commands

Integrate governance awareness into existing commands:

- `/speckit-spec` - Reads NFR catalog for acceptance criteria, cites NFR IDs
- `/speckit-design` - Validates ADRs against constitution Section 2
- `/speckit-test` - Enforces test strategy pyramid ratios
- `/speckit-review` - Checks NFR cross-references in implementation

#### Phase 4: Validation Integration

Add governance validation to SpecKit workflow:

- Pre-commit hook: Run `governance-validate-artifacts` if `docs/governance/` exists
- `/speckit-review` includes governance validation
- CI gate: Fail if NFR references broken

### Salvageable Artifacts

From archived branch history:

```bash
# View governance skills
git show feat/technical-governance:.agents/skills/governance-nfr-writer/SKILL.md

# Extract STA2E VTT examples
git show feat/technical-governance:.agents/examples/governance/sta2e-vtt/NFR_CATALOG.md

# Get JSON schemas
git show feat/technical-governance:.agents/schemas/governance/nfr.schema.json
```

## Relationship to Other Decisions

This archival follows the pattern established in:

- **ADR-003**: Archive feat/pries-workflow (PRIES concepts integrated into SpecKit)
- **Commit 04d0fa2**: Remove structural markdown tests (test strategy evolution)
- **Commit 69d2547**: Documentation reorganization (separate SpecKit from marketplace)

Pattern: When a branch proposes replacement architecture, archive it and integrate concepts into existing implementation.

## Implementation Notes

### Branch Commits Archived

```
d42d17a updated research and completed mapping of skills to pries workflow
2dfce4c fix(governance): enforce 70/20/10 test pyramid standard
ca9afeb docs(governance): add STA2E VTT example, integration docs, smoke test
0d85925 feat(governance): add Phase 0 agents and commands
88f90f8 feat(governance): add five governance skills (agentskills.io format)
b6b6014 feat(governance): add Phase 0 schemas and artifact templates
```

### Divergence Point

- Merge base: 8034741 ("updated docs")
- Commits on dev since divergence: 50
- Commits on feat/technical-governance: 6

### Current State

- SpecKit Phases 1-3: Complete on dev branch
- Phase 4 migration: In progress (worktree)
- Governance integration: Deferred to post-Phase 4

## References

- Archived branch final commit: [commit before deletion]
- Current SpecKit implementation: `spec-kit-multi-agent-tdd/` on dev branch
- ADR-003: PRIES workflow archival
- Documentation reorganization: Commit 69d2547
- Analysis document: `TECHNICAL-GOVERNANCE-ANALYSIS.md` (created during review)

## Success Criteria for Future Integration

The governance integration will be considered successful when:

1. ✅ `/speckit-govern` command creates valid governance artifacts
2. ✅ All 5 governance skills operational in SpecKit context
3. ✅ SpecKit commands reference NFR IDs from catalog
4. ✅ Validation runs in CI pipeline
5. ✅ STA2E VTT example works end-to-end with integrated workflow

---

**Decision:** Archive branch, integrate concepts into SpecKit as enhancement, not replacement.
