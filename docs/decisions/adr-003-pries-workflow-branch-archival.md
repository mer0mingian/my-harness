# ADR 003: Archive feat/pries-workflow Branch

**Status:** Accepted  
**Date:** 2026-05-08  
**Decision Makers:** Development Team

## Context

The feat/pries-workflow branch was created as an early implementation of a multi-agent PRIES (Propose, Refine, Implement, Evaluate, Ship) workflow. This branch contained:

- 5 PRIES workflow agents
- 4 workflow commands in TOML format
- 6 skills (P0-P2 priority levels)
- Python-based command executables
- Integration guides and STA2E VTT example workflows

During development, a cleaner architecture emerged that better aligned with SpecKit methodology and Test-Driven Development principles.

## Decision

We decided to archive and delete the feat/pries-workflow branch because:

1. **Complete Supersession**: All PRIES workflow concepts have been reimplemented in the spec-kit-multi-agent-tdd extension with superior architecture
2. **No Unique Value**: Nothing on the branch provides value not already captured in the current implementation
3. **Maintenance Burden**: Keeping the branch would create confusion and maintenance overhead
4. **Architectural Mismatch**: TOML/Python approach doesn't align with our markdown-based command architecture

## Consequences

### Positive

- **Cleaner Repository**: Removes obsolete implementation reducing cognitive load
- **Clear Direction**: Single authoritative implementation (spec-kit-multi-agent-tdd)
- **Better Architecture**: Markdown-based commands are simpler and more maintainable
- **Proper Documentation**: Archival document preserved on branch before deletion

### Neutral

- **Historical Record**: Branch commits preserved in git reflog for 90 days
- **Archival Document**: BRANCH_ARCHIVED.md committed to branch before deletion

### Migration Path

All PRIES concepts mapped to spec-kit-multi-agent-tdd:

| PRIES Phase | spec-kit-multi-agent-tdd Command |
|-------------|----------------------------------|
| Propose     | solution-design                  |
| Refine      | review (iterative)               |
| Implement   | implement (TDD-based)            |
| Evaluate    | test + review                    |
| Ship        | commit                           |

## Implementation

1. Created BRANCH_ARCHIVED.md on feat/pries-workflow documenting supersession
2. Committed and pushed archival document
3. Deleted local branch: `git branch -d feat/pries-workflow`
4. Deleted remote branch: `git push origin --delete feat/pries-workflow`
5. Documented decision in this ADR

## References

- Current implementation: `spec-kit-multi-agent-tdd/` on dev branch
- Agent definitions: `.agents/plugins/harness-agents/`
- Last commit on archived branch: c263f24
