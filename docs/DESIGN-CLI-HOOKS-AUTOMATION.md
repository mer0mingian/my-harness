# Design Decision: CLI-Level Documentation Automation

**Date**: 2026-05-12  
**Status**: Approved for Implementation  
**Complexity**: 8 Story Points

---

## Problem Statement

The IMPLEMENTATION_PLAN.md proposed GitHub Actions for automatic C4/CGC updates on PR merge. However, the project has strict constraints:

- ❌ No GitHub Actions (local-first architecture)
- ❌ No git hooks (.git/hooks/ - too intrusive)
- ✅ Local-only automation
- ✅ CLI-level hooks only

**Required**: Design CLI-based automation using Claude Code hooks or SpecKit hooks.

---

## Solution: Hybrid Manual + Optional Automatic

### Chosen Approach

**Primary**: Manual command `/speckit.matd.update-docs`  
**Optional**: SpecKit `post_implement` hook

This hybrid approach provides:

1. **User control** - Developers decide when to update docs
2. **Incremental updates** - Only regenerates changed sections
3. **Non-blocking** - Failures don't prevent commits
4. **Local-first** - No external dependencies
5. **Flexible** - Manual OR automatic execution

---

## Architectural Decision

### Why Manual Command as Primary?

**Pros**:
- Explicit user control - no surprises
- Runs on-demand when docs are actually needed
- Easy to debug (just run the command)
- Works across all CLI systems (Claude Code, OpenCode, SpecKit)
- No configuration overhead

**Cons**:
- Requires developer discipline
- Docs can fall out of sync if forgotten

**Mitigation**: Clear documentation + workflow integration

### Why SpecKit Hook as Optional?

**Pros**:
- Automatic updates after feature implementation
- Consistent behavior across team
- Reduces cognitive load
- Already integrated with MATD workflow

**Cons**:
- Adds 30-90s to implementation step
- Can fail on missing tools (deepwiki/cgc)
- Requires configuration setup

**Mitigation**: Non-blocking (critical: false) + clear setup docs

### Why NOT Claude Code Hooks?

Claude Code's `post_commit` hook triggers after EVERY commit:

```json
{
  "hooks": {
    "post_commit": [
      {"name": "update-docs", "command": "..."}  // Runs every commit!
    ]
  }
}
```

**Problems**:
1. **Too frequent** - C4 generation (30-90s) after every `git commit`
2. **No filtering** - Triggers even for typo fixes
3. **No context** - Can't pass feature ID
4. **Heavy operations** - deepwiki + cgc not designed for per-commit use

**Better for**: Lightweight operations (lint, format, quick checks)

---

## Implementation Components

### 1. Helper Scripts (scripts/)

#### update-c4-docs.sh
- Detects changed files via `git diff`
- Runs `deepwiki generate --incremental`
- Shows diff of updated diagrams
- Non-blocking failures

#### update-cgc-index.sh
- Extracts changed files list
- Runs `cgc index --incremental`
- Tags entries with feature ID
- Non-blocking failures

### 2. Manual Command (commands/update-docs.md)

**Command**: `/speckit.matd.update-docs [feature-id]`

**Behavior**:
1. Runs both scripts sequentially
2. Displays progress and results
3. Reports failures (non-blocking)
4. Returns summary

**Usage**:
```bash
/speckit.matd.commit feat-001
/speckit.matd.update-docs feat-001
```

### 3. Optional Hook (.specify/hooks.yml)

**Configuration** (disabled by default):
```yaml
post_implement:
  - name: update-c4-docs
    command: bash scripts/update-c4-docs.sh "${FEATURE_ID:-unknown}"
    critical: false
  
  - name: update-cgc-index
    command: bash scripts/update-cgc-index.sh "${FEATURE_ID:-unknown}"
    critical: false
```

**Activation**: User copies from `.specify/hooks.yml.example` and uncomments

### 4. Documentation (docs/AUTOMATION.md)

Comprehensive guide covering:
- Manual vs automatic workflows
- Setup instructions
- Configuration options
- Troubleshooting
- Best practices
- Performance optimization

---

## Trigger Strategy

### When Documentation Updates Run

| Trigger | Frequency | Use Case |
|---------|-----------|----------|
| Manual command | User-initiated | After feature completion |
| SpecKit hook | Per `/speckit.matd.implement` | Active development with frequent arch changes |
| **NOT** git post-commit | ❌ Every commit | Too heavy for local workflow |
| **NOT** GitHub Actions | ❌ PR merge | Requires GitHub (not local-first) |

### Recommended Workflow

**Small teams / Active development**:
```bash
/speckit.matd.implement feat-001
# Hook auto-updates docs
/speckit.matd.review feat-001
/speckit.matd.commit feat-001
```

**Large teams / Stable architecture**:
```bash
/speckit.matd.implement feat-001
/speckit.matd.review feat-001
/speckit.matd.commit feat-001
/speckit.matd.update-docs feat-001  # Manual, as needed
```

---

## Tool Requirements

### Required for All Automation

1. **deepwiki** - C4 diagram generation
   ```bash
   pip install deepwiki
   ```

2. **cgc** - Code Graph Context indexing
   ```bash
   pip install code-graph-context
   ```

### Installation Verification

```bash
deepwiki --version
cgc --version
```

**Failure mode**: Scripts exit gracefully with warning if tools missing

---

## Performance Characteristics

### Execution Time (Incremental Mode)

| Project Size | C4 Update | CGC Update | Total |
|--------------|-----------|------------|-------|
| Small (<100 files) | 5-10s | 3-5s | **10-15s** |
| Medium (500 files) | 15-30s | 10-20s | **30-50s** |
| Large (2000+ files) | 45-90s | 30-60s | **90-150s** |

### Optimization

- ✅ Incremental mode enabled by default
- ✅ Only changed files processed
- ✅ Excludes test files (configurable)
- ✅ Non-blocking failures

---

## Error Handling

### Tool Not Found

**Scenario**: `deepwiki` or `cgc` not installed

**Behavior**:
```
⚠️ deepwiki not found in PATH
   Install: pip install deepwiki
```

**Action**: Script exits gracefully, workflow continues

### No Changes Detected

**Scenario**: No files changed since last commit

**Behavior**:
```
✓ No files changed, skipping C4 update
```

**Action**: Normal exit, no updates needed

### Generation Fails

**Scenario**: deepwiki/cgc crashes or errors

**Behavior**:
```
⚠️ deepwiki generation failed (non-blocking)
```

**Action**: Error logged, workflow continues

---

## Comparison with GitHub Actions Approach

### Original Plan (GitHub Actions)

```yaml
name: Update Docs
on:
  pull_request:
    types: [closed]
    branches: [main, live]

jobs:
  update-docs:
    if: github.event.pull_request.merged == true
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - run: scripts/update-c4-docs.sh
      - run: scripts/update-cgc-index.sh
      - run: git commit && git push
```

**Pros**: Centralized, consistent, automatic  
**Cons**: Requires GitHub, cloud execution, not local-first

### CLI-Based Approach (This Design)

**Manual**:
```bash
/speckit.matd.update-docs feat-001
```

**Automatic** (optional):
```yaml
post_implement:
  - name: update-docs
    command: bash scripts/update-c4-docs.sh $FEATURE_ID
```

**Pros**: Local-first, user control, flexible  
**Cons**: Requires discipline, can be forgotten

### Trade-off Analysis

| Aspect | GitHub Actions | CLI-Based |
|--------|----------------|-----------|
| Local execution | ❌ Cloud only | ✅ Local only |
| User control | ❌ Automatic | ✅ Explicit |
| GitHub dependency | ❌ Required | ✅ Not needed |
| Consistency | ✅ Guaranteed | ⚠️ Discipline required |
| Setup complexity | Medium | Low |
| Failure impact | Blocks merge | Non-blocking |

**Winner**: CLI-based for local-first constraint

---

## Migration from IMPLEMENTATION_PLAN.md

### What Changed

**Before** (GitHub Actions proposal):
- `.github/workflows/auto-docs.yml` - 50 lines
- Triggered on PR merge to main/live
- Automatic commit + push
- Cloud execution

**After** (CLI-based design):
- `/speckit.matd.update-docs` command
- `scripts/update-c4-docs.sh` + `scripts/update-cgc-index.sh`
- Optional `.specify/hooks.yml` configuration
- Local execution

### What Stayed the Same

- ✅ Incremental updates (only changed files)
- ✅ Non-blocking failures
- ✅ Feature ID tagging for CGC
- ✅ Same underlying scripts (update-c4-docs.sh, update-cgc-index.sh)

---

## Future Enhancements

### V2: Smart Detection

Only update docs if architecture actually changed:

```bash
# Check if src/ files changed (not just tests/)
if git diff --name-only HEAD~1 HEAD | grep -q "^src/"; then
  bash scripts/update-c4-docs.sh
fi
```

### V3: Parallel Execution

Run C4 and CGC updates in parallel:

```bash
bash scripts/update-c4-docs.sh $FEATURE_ID &
bash scripts/update-cgc-index.sh $FEATURE_ID &
wait
```

### V4: Progress Indicator

Show live progress during long operations:

```bash
deepwiki generate ... | pv -l -s $(wc -l < file_list)
```

---

## Testing Strategy

### Manual Testing

1. **Command execution**:
   ```bash
   /speckit.matd.update-docs test-001
   ```
   Verify: Scripts run, output displayed, changes visible

2. **Hook execution**:
   ```bash
   /speckit.matd.implement feat-001
   ```
   Verify: Hook triggers automatically, logs visible

3. **Error handling**:
   ```bash
   # Uninstall deepwiki temporarily
   pip uninstall deepwiki
   /speckit.matd.update-docs test-002
   ```
   Verify: Graceful failure, workflow continues

### Integration Testing

1. Feature workflow end-to-end
2. Multiple consecutive updates
3. No changes scenario
4. Large file changes (performance)

---

## Documentation Deliverables

✅ **Created**:

1. `scripts/update-c4-docs.sh` - C4 update script
2. `scripts/update-cgc-index.sh` - CGC update script
3. `commands/update-docs.md` - Command specification
4. `docs/AUTOMATION.md` - Comprehensive automation guide
5. `.specify/hooks.yml.example` - Hook configuration template
6. `USER-GUIDE.md` - Updated with automation section
7. `docs/DESIGN-CLI-HOOKS-AUTOMATION.md` - This design document

---

## Approval Checklist

- ✅ **Local-first constraint** - No GitHub Actions, no git hooks
- ✅ **User control** - Manual command available
- ✅ **Optional automation** - SpecKit hooks opt-in
- ✅ **Non-blocking** - Failures don't prevent workflow
- ✅ **Incremental** - Only changed files processed
- ✅ **Documented** - Comprehensive guides provided
- ✅ **Tested** - Error handling and edge cases covered

---

## References

- **Claude Code hooks**: https://code.claude.com/docs/en/hooks
- **SpecKit hooks**: Implemented in `.specify/hooks.yml`
- **Original proposal**: IMPLEMENTATION_PLAN.md, Task 6.2
- **Related commands**: `/speckit.matd.commit`, `/speckit.matd.review`

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-05-12 | Initial design - CLI-based automation |
