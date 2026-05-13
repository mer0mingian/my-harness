# Command: /speckit.matd.update-docs

**Purpose**: Update C4 diagrams and Code Graph Context index after feature implementation

**Category**: MATD Workflow (Documentation)

**Agent**: None (runs scripts directly)

---

## Overview

This command updates project documentation artifacts after completing feature work:

1. **C4 Diagrams** - Regenerates architecture diagrams incrementally
2. **CGC Index** - Reindexes changed files for Code Graph Context

Updates are **incremental** (only changed files) and **non-blocking** (failures don't prevent continuation).

---

## Usage

### Basic (Auto-detect changes)

```bash
/speckit.matd.update-docs
```

### With Feature ID (for tagging)

```bash
/speckit.matd.update-docs feat-001
```

---

## What It Does

### Step 1: Update C4 Diagrams

Runs `scripts/update-c4-docs.sh`:
- Detects changed files since last commit
- Runs `deepwiki generate . --output docs/c4 --incremental`
- Shows diff of updated diagrams

### Step 2: Update CGC Index

Runs `scripts/update-cgc-index.sh`:
- Extracts list of changed files
- Runs `cgc index --incremental --files <changed> --tag implementation:<feature-id>`
- Tags index entries with feature ID for traceability

### Step 3: Report Results

Displays summary:
- Files analyzed
- Diagrams updated
- Index entries added
- Any failures (non-blocking)

---

## When to Use

### ✅ DO Use After:

- Completing feature implementation
- Merging PRs to main/live branches
- Major refactoring that changes architecture
- Adding new modules/components

### ❌ DON'T Use For:

- Every single commit (too heavy)
- Documentation-only changes
- Configuration tweaks
- Small bug fixes

---

## Requirements

### Tools Required

1. **deepwiki** - C4 diagram generation
   ```bash
   pip install deepwiki
   ```

2. **cgc** - Code Graph Context indexing
   ```bash
   pip install code-graph-context
   ```

### File Structure

```
project/
├── docs/c4/              # C4 diagram output (auto-created)
├── .cgc/                 # CGC index storage (auto-created)
└── scripts/
    ├── update-c4-docs.sh
    └── update-cgc-index.sh
```

---

## Command Implementation

### Input Arguments

- `feature_id` (optional): Feature identifier for CGC tagging (default: "unknown")

### Output

Terminal output showing:
- Changed files detected
- C4 generation progress
- CGC indexing progress
- Summary of updates

### Artifacts Modified

- `docs/c4/**/*.md` - Updated C4 diagrams
- `.cgc/index.db` - Updated CGC index

---

## Error Handling

### Tool Not Found

**Error**: `deepwiki not found in PATH`

**Solution**:
```bash
# Install in host
pip install deepwiki

# Or install in container
docker-compose exec agent pip install deepwiki
```

### No Changes Detected

**Output**: `✓ No files changed, skipping update`

**Action**: Normal - no updates needed

### Generation Fails

**Output**: `⚠️ deepwiki generation failed (non-blocking)`

**Action**: Command continues - failures don't block workflow

---

## Integration with MATD Workflow

### Manual Trigger (Recommended)

After completing `/speckit.matd.commit`:

```bash
/speckit.matd.commit feat-001
/speckit.matd.update-docs feat-001
```

### Automatic Trigger (Optional)

Enable in `.specify/hooks.yml`:

```yaml
post_implement:
  - name: update-documentation
    command: bash scripts/update-c4-docs.sh $FEATURE_ID && bash scripts/update-cgc-index.sh $FEATURE_ID
    critical: false
    description: "Update C4 diagrams and CGC index"
```

See [AUTOMATION.md](../docs/AUTOMATION.md) for configuration details.

---

## Example Session

```bash
$ /speckit.matd.update-docs feat-001

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Updating C4 diagrams (incremental)
Feature: feat-001
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Changed files:
  - src/auth/login.py
  - tests/test_auth.py

Running deepwiki generate...
✓ C4 diagrams updated

 docs/c4/components.md | 12 +++++++++---
 1 file changed, 9 insertions(+), 3 deletions(-)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Updating CGC index (incremental)
Feature: feat-001
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Changed files: src/auth/login.py,tests/test_auth.py

Running cgc index...
✓ CGC index updated

Total nodes: 847
Total edges: 1,203
Indexed files: 156

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Documentation update complete
```

---

## Troubleshooting

### Updates Take Too Long

**Symptom**: Script runs for >5 minutes

**Solutions**:
1. Check if `--incremental` flag is being used
2. Verify git history not corrupted (`git fsck`)
3. Reduce scope with explicit file list

### Diagrams Not Updating

**Check**:
```bash
git status docs/c4/
```

**If clean**: No architectural changes detected (expected)
**If dirty**: Run `git add docs/c4/ && git commit -m "docs: update C4"`

### CGC Index Growing Large

**Check size**:
```bash
du -sh .cgc/
```

**If >100MB**: Consider pruning old tags
```bash
cgc prune --older-than 30d
```

---

## Related Commands

- `/speckit.matd.commit` - Validate and commit feature implementation
- `/speckit.matd.review` - Architecture and code review

---

## Configuration

No command-specific configuration required. Uses project-level settings:

- `docs/c4/` - C4 output directory (configurable in deepwiki.yml)
- `.cgc/` - CGC index storage (configurable in cgc.toml)

---

## Notes

- **Incremental only**: Never runs full regeneration
- **Non-blocking**: Failures logged but don't stop workflow
- **Local-first**: No external dependencies or API calls
- **Git-aware**: Uses `git diff` to detect changed files
- **Idempotent**: Safe to run multiple times

---

## Version History

| Version | Date       | Changes                   |
|---------|------------|---------------------------|
| 1.0     | 2026-05-12 | Initial implementation    |
