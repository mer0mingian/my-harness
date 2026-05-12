# Automated Documentation in SpecKit MATD

**Status**: Production Ready  
**Date**: 2026-05-12

---

## Overview

The SpecKit MATD extension supports automated documentation updates after feature implementation. Two systems are available:

1. **Manual command** - Explicit user trigger (recommended)
2. **SpecKit hooks** - Automatic after implementation (optional)

Both use the same underlying scripts for C4 diagram generation and CGC indexing.

---

## Quick Start

### Manual Updates (Recommended)

After completing a feature:

```bash
/speckit.matd.commit feat-001          # Commit feature code
/speckit.matd.update-docs feat-001     # Update documentation
```

### Automatic Updates (Optional)

Enable in `.specify/hooks.yml`:

```yaml
post_implement:
  - name: update-c4-docs
    command: bash scripts/update-c4-docs.sh "${FEATURE_ID:-unknown}"
    critical: false
  
  - name: update-cgc-index
    command: bash scripts/update-cgc-index.sh "${FEATURE_ID:-unknown}"
    critical: false
```

---

## Architecture

### Components

```
┌─────────────────────────────────────────────────┐
│  User Triggers                                  │
│  • /speckit.matd.update-docs (manual)           │
│  • post_implement hook (automatic)              │
└────────────────┬────────────────────────────────┘
                 │
    ┌────────────┴────────────┐
    │                         │
    ▼                         ▼
┌─────────────────┐   ┌─────────────────┐
│ update-c4-docs  │   │ update-cgc-index│
│     .sh         │   │      .sh        │
└────────┬────────┘   └────────┬────────┘
         │                     │
         ▼                     ▼
    ┌─────────┐          ┌─────────┐
    │ deepwiki│          │   cgc   │
    │ generate│          │  index  │
    └────┬────┘          └────┬────┘
         │                    │
         ▼                    ▼
    docs/c4/              .cgc/index
```

### Data Flow

1. **Detection**: `git diff --name-only` identifies changed files
2. **C4 Update**: `deepwiki generate --incremental --changed-files`
3. **CGC Update**: `cgc index --incremental --files`
4. **Tagging**: Feature ID tags added to CGC entries
5. **Reporting**: Diffs and stats displayed

---

## Manual Command

### Usage

```bash
/speckit.matd.update-docs [feature-id]
```

### When to Use

| Situation | Recommendation |
|-----------|----------------|
| Feature complete | ✅ Always run after `/speckit.matd.commit` |
| Architecture changes | ✅ Run to update C4 diagrams |
| Refactoring | ✅ Run to reflect new structure |
| Bug fix (no arch changes) | ⚠️ Optional - likely no updates |
| Documentation edits | ❌ Skip - no code changes |
| Config tweaks | ❌ Skip - no code changes |

### Example Session

```bash
$ /speckit.matd.update-docs feat-auth-jwt

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Updating C4 diagrams (incremental)
Feature: feat-auth-jwt
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Changed files:
  - src/auth/jwt_handler.py
  - src/auth/middleware.py
  - tests/test_jwt.py

✓ C4 diagrams updated

 docs/c4/components.md | 12 +++++++++---
 1 file changed, 9 insertions(+), 3 deletions(-)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Updating CGC index (incremental)
Feature: feat-auth-jwt
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✓ CGC index updated

Total nodes: 847 (+3)
Total edges: 1,203 (+8)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Automatic Updates (SpecKit Hooks)

### Setup

1. **Copy example configuration**:
   ```bash
   cp spec-kit-multi-agent-tdd/.specify/hooks.yml.example .specify/hooks.yml
   ```

2. **Enable documentation hooks** (uncomment these lines):
   ```yaml
   post_implement:
     - name: update-c4-docs
       command: bash scripts/update-c4-docs.sh "${FEATURE_ID:-unknown}"
       critical: false
     
     - name: update-cgc-index
       command: bash scripts/update-cgc-index.sh "${FEATURE_ID:-unknown}"
       critical: false
   ```

3. **Test the hook**:
   ```bash
   /speckit.matd.implement feat-001
   # Hook runs automatically after implementation
   ```

### Hook Behavior

- **Trigger**: After `/speckit.matd.implement` completes successfully
- **Execution**: Runs both scripts sequentially
- **Failures**: Non-blocking (critical: false) - logged but don't stop workflow
- **Context**: `$FEATURE_ID` environment variable passed from command

### When to Enable

| Project Type | Recommendation |
|--------------|----------------|
| Active development | ✅ Enable - keeps docs in sync |
| Production maintenance | ⚠️ Optional - fewer arch changes |
| Prototype/POC | ❌ Skip - docs lag is acceptable |
| Team onboarding | ✅ Enable - always-fresh diagrams |

---

## Configuration

### Tool Installation

Both `deepwiki` and `cgc` must be installed:

#### Host Installation

```bash
pip install deepwiki code-graph-context
```

#### Container Installation

Add to `Dockerfile` or install in running container:

```dockerfile
RUN pip install deepwiki code-graph-context
```

Or manually:

```bash
docker-compose exec agent bash
pip install deepwiki code-graph-context
```

### Directory Structure

Ensure these directories exist (auto-created if missing):

```
project/
├── docs/c4/              # C4 diagram output
├── .cgc/                 # CGC index storage
│   ├── index.db
│   └── config.toml
└── scripts/
    ├── update-c4-docs.sh
    └── update-cgc-index.sh
```

### DeepWiki Configuration

Optional `deepwiki.yml` in project root:

```yaml
output_dir: docs/c4
incremental: true
exclude_patterns:
  - "tests/"
  - "migrations/"
  - "*.pyc"
```

### CGC Configuration

Optional `.cgc/config.toml` in project root:

```toml
[index]
incremental = true
max_file_size_mb = 5

[storage]
path = ".cgc/index.db"

[tagging]
enabled = true
prefix = "implementation:"
```

---

## Disabling Automation

### Temporary (One Feature)

Skip the hook with `--skip-hooks` flag:

```bash
/speckit.matd.implement feat-001 --skip-hooks
```

### Permanent (All Features)

Remove or comment out hooks in `.specify/hooks.yml`:

```yaml
post_implement:
  # - name: update-c4-docs
  #   command: ...  (commented out)
```

Or delete the entire hook section.

---

## Troubleshooting

### Hook Not Running

**Check 1**: Verify `.specify/hooks.yml` exists and is valid YAML

```bash
yamllint .specify/hooks.yml
```

**Check 2**: Verify scripts are executable

```bash
ls -l scripts/*.sh
# Should show -rwxr-xr-x permissions
```

**Check 3**: Test script manually

```bash
bash scripts/update-c4-docs.sh test
```

### Updates Slow or Hang

**Symptom**: Hook takes >5 minutes

**Diagnosis**:
```bash
# Check if incremental flag is working
grep "incremental" scripts/*.sh
```

**Solution**: Ensure `--incremental` flag passed to both tools

### Diagrams Not Updating

**Check 1**: Verify changed files detected

```bash
git diff --name-only HEAD~1 HEAD
```

**Check 2**: Run manually to see errors

```bash
bash -x scripts/update-c4-docs.sh feat-001
```

**Check 3**: Verify deepwiki installation

```bash
deepwiki --version
```

### CGC Index Growing Large

**Check size**:
```bash
du -sh .cgc/
```

**If >100MB**, prune old entries:
```bash
cgc prune --older-than 30d
```

Or compact the database:
```bash
cgc compact
```

---

## Best Practices

### 1. Run After Feature Completion

Don't run on every commit - only after feature work completes:

```bash
# ✅ Good workflow
/speckit.matd.test feat-001
/speckit.matd.implement feat-001
/speckit.matd.review feat-001
/speckit.matd.commit feat-001
/speckit.matd.update-docs feat-001  # Once at end

# ❌ Bad workflow
git commit -m "WIP"
/speckit.matd.update-docs          # Too frequent
git commit -m "Fix typo"
/speckit.matd.update-docs          # Too frequent
```

### 2. Commit Documentation Updates

After updates, commit the changes:

```bash
/speckit.matd.update-docs feat-001
git add docs/c4/ .cgc/
git commit -m "docs: update C4 and CGC for feat-001"
```

### 3. Review Changes Before Commit

Check what documentation changed:

```bash
/speckit.matd.update-docs feat-001
git diff docs/c4/           # Review diagram changes
git diff .cgc/config.toml   # Review index config
```

### 4. Feature ID Conventions

Use consistent feature IDs for better CGC tagging:

```bash
# ✅ Good - consistent format
feat-001, feat-002, feat-003
auth-login, auth-jwt, auth-rbac

# ❌ Bad - inconsistent
feature1, FEATURE-2, f03, login_feature
```

### 5. Hook Criticality

Keep documentation hooks non-blocking:

```yaml
post_implement:
  - name: update-c4-docs
    critical: false  # ✅ Good - don't block on doc failures
  
  # Compare with:
  - name: lint
    critical: true   # ✅ Good - block on code quality failures
```

---

## Performance

### Typical Execution Times

| Operation | Small Project (<100 files) | Medium Project (500 files) | Large Project (2000+ files) |
|-----------|---------------------------|----------------------------|----------------------------|
| C4 Update (incremental) | 5-10s | 15-30s | 45-90s |
| CGC Index (incremental) | 3-5s | 10-20s | 30-60s |
| **Total** | **10-15s** | **30-50s** | **90-150s** |

### Optimization Tips

1. **Use incremental mode** - Already enabled by default
2. **Exclude test files** - Add to `deepwiki.yml` exclude patterns
3. **Prune old CGC entries** - Run `cgc prune` monthly
4. **Run on merge to main** - Not on every feature branch commit

---

## Alternative: Claude Code Hooks

**Not recommended** for documentation automation because:

- Claude Code `post_commit` hook runs after EVERY commit (too frequent)
- No selective triggering based on file patterns
- Better suited for lightweight operations (lint, format)

However, if needed:

```json
{
  "hooks": {
    "post_commit": [
      {
        "name": "update-docs",
        "command": "bash scripts/update-docs-wrapper.sh"
      }
    ]
  }
}
```

Where `update-docs-wrapper.sh` does smart detection:

```bash
#!/bin/bash
# Only update if on main/live branch
current_branch=$(git branch --show-current)
if [[ "$current_branch" =~ ^(main|live)$ ]]; then
  bash scripts/update-c4-docs.sh
  bash scripts/update-cgc-index.sh
fi
```

---

## Related Documentation

- [Command Reference: update-docs](../commands/update-docs.md)
- [User Guide: MATD Workflow](../USER-GUIDE.md)
- [Hook Configuration: SpecKit hooks.yml](../.specify/hooks.yml.example)

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-05-12 | Initial documentation automation design |
