# Phase 4 Migration: Python to Markdown Commands

## Summary

As of **commit e6c892f** (May 7, 2026), all workflow commands were converted from Python (`.py`) to Markdown (`.md`) format with YAML frontmatter.

## Deleted Files (Phase 4 Cleanup)

The following Python command files were removed as they are superseded by `.md` equivalents:

- `commands/execute.py` (7.9KB) → `commands/execute.md` (13KB)
- `commands/implement.py` (26.4KB) → `commands/implement.md` (18.4KB)  
- `commands/test.py` (28.1KB) → `commands/test.md` (10.2KB)

## Why the Change?

**Before (Python):**
- Commands were Python scripts with embedded logic
- Platform-specific (required Python interpreter)
- Mixed orchestration with validation code
- Hard to modify for non-developers

**After (Markdown):**
- Commands are natural language orchestration instructions
- Cross-platform compatible (15+ agent CLIs)
- Separation of concerns: orchestration (`.md`) vs validation (`scripts/*.py`)
- Easier to read, audit, and customize

## Validation Logic Preserved

The validation logic from the Python commands was extracted and moved to helper scripts:

| Old Location | New Location | Purpose |
|--------------|--------------|---------|
| `test.py` | `scripts/validate_red_state.py` | RED state validation |
| `implement.py` | `scripts/validate_green_state.py` | GREEN state validation |
| `implement.py` | `scripts/run_integration_checks.py` | Integration checks |
| `execute.py` | `commands/execute.md` | Orchestration (now markdown) |

## Breaking Changes

1. **Direct Python invocation no longer works:**
   ```bash
   # OLD (removed)
   python3 commands/implement.py feat-123
   
   # NEW (use agent CLI)
   /speckit.matd.implement feat-123
   ```

2. **Integration tests deprecated:**
   - `tests/integration/test_command_execute_e2e.sh` (deprecated)
   - `tests/integration/test_command_implement_e2e.sh` (deprecated)
   
   These tests invoked Python scripts directly and are no longer relevant.

3. **Configuration unchanged:**
   - `.specify/harness-tdd-config.yml` format remains the same
   - Helper scripts in `scripts/` directory still used

## Migration Commit Reference

- **Commit:** e6c892f
- **Date:** May 7, 2026
- **Author:** Daniel Mingers
- **Message:** "feat: complete Phase 4 - convert commands to markdown format"

## See Also

- `ARCHITECTURAL-CORRECTION-PLAN.md` Phase 4
- `extension.json` (updated command file references)
- `hooks/config.yml` (constitutional enforcement hooks)
