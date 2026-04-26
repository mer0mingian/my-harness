# Skill Naming Resolution — Recommendation

**Date:** 2026-04-26  
**Status:** Decision Required  
**Blocking:** Phase 3+ of workflow runtime implementation  

---

## 1. The Challenge

Phase R research discovered a **systematic directory/frontmatter mismatch** affecting 19 of 52 marketplace skills:

| Directory Name | Frontmatter `name:` | Pattern Match |
|---|---|---|
| `review-differential-review/` | `differential-review` | ❌ `review-*` fails |
| `review-systematic-debugging/` | `systematic-debugging` | ❌ `review-*` fails |
| `stdd-openspec/` | `openspec` | ❌ `stdd-*` fails |
| `stdd-pm-openspec/` | `pm-openspec` | ❌ `stdd-pm-*` fails |
| *(15 more with same pattern)* | | |

### Root Cause

The **agentskills.io specification** (Anthropic, Dec 2025) keys skill identity on the frontmatter `name:` field, not the directory structure:

> "The skill name is the unique identifier and must be declared in SKILL.md frontmatter. Tooling locates skills by scanning for SKILL.md files and reading the name field."

The **resolver** (`scan_marketplace()`) correctly implements this:

```python
for p in root.rglob("SKILL.md"):
    post = frontmatter.load(p)
    skill = Skill.model_validate(dict(post.metadata))
    catalog.skills[skill.name] = skill  # ← keys on frontmatter name
```

### Immediate Impact

**Workflow manifests using prefix-based skill assignment fail:**

```yaml
# stdd-feat/workflow.yaml
phases:
  - name: specification
    driver: pm-orchestrator
    skills: [stdd-pm-*]  # ← resolves to 0 skills (expected 2)
  
  - name: review
    driver: review-orchestrator
    skills: [review-*]    # ← resolves to 0 skills (expected 5)
```

**Smoke test output:**
```
stdd-* expansion: 5 skills ✓
review-* expansion: 0 skills ✗ (expected 5)
```

This breaks the **prefix-based minimal-exposure principle** — the core workflow design pattern.

---

## 2. User Principles (Design Constraints)

1. **Minimal skill exposure**: Subagents should see only skills required for their role.
2. **Prefix-based assignment**: `skills: [review-*]` should "just work" for review-phase agents.
3. **Shared skill naming**: Skills used across workflows get simplified prefixes (`stdd-`, `review-`, `general-`).
4. **Workflow plugin bundling**: A workflow plugin delivers agents + skills + hooks as one installable unit.
5. **High skill quality**: Every skill must justify its existence through:
   - **Specificity** — solves a well-defined problem, not a grab-bag of tangential concerns
   - **Composability** — works with other skills without overlap or conflict
   - **Discoverability** — name + description make the purpose instantly clear
   - **Progressive disclosure** — metadata loads cheaply; full content loads on-demand

---

## 3. Options Analysis

### Option A: Rename Frontmatter `name:` Fields (Include Prefix)

**Change 19 SKILL.md frontmatter blocks:**
```diff
 ---
-name: differential-review
+name: review-differential-review
 description: Systematic code review with differential analysis
 ---
```

**Pros:**
- ✅ **agentskills.io compliant** — `name:` is authoritative per spec
- ✅ **Zero resolver changes** — glob expansion works immediately
- ✅ **Directory/name alignment** — human-readable structure matches machine identity
- ✅ **Portable** — other agentskills.io tooling will resolve correctly
- ✅ **Discoverable** — `name: review-differential-review` signals category at a glance

**Cons:**
- ⚠️ **Breaking change** for agents declaring `skills: [differential-review]` (must update to `review-differential-review`)
- ⚠️ **Longer names** in agent frontmatter (but glob patterns mitigate: `skills: [review-*]`)

**Effort:** 19 file edits, 1-line change each. Est. 15 minutes.

---

### Option B: Key Resolver on Directory Name (Violate Spec)

**Change resolver to extract skill name from directory path instead of frontmatter:**
```python
for p in root.rglob("SKILL.md"):
    skill_name = p.parent.name  # ← use directory name
    post = frontmatter.load(p)
    skill = Skill.model_validate(dict(post.metadata))
    skill.name = skill_name  # ← override frontmatter
    catalog.skills[skill_name] = skill
```

**Pros:**
- ✅ **No SKILL.md edits** — existing files unchanged

**Cons:**
- ❌ **agentskills.io violation** — breaks interop with external tooling (VS Code extensions, claude.ai skill browser, future community tools)
- ❌ **Inconsistent with Anthropic guidance** — the spec is explicit about `name:` being authoritative
- ❌ **Fragile** — directory renames require careful synchronization
- ❌ **Non-portable** — skills exported to other marketplaces will fail to load correctly
- ❌ **Quality risk** — incentivizes lazy naming (directory structure becomes source of truth, frontmatter becomes stale metadata)

**Effort:** 10 lines of resolver code. Ongoing maintenance burden tracking directory/frontmatter drift.

---

### Option C: Dual-Key Catalog (Support Both)

**Build catalog keyed on both directory name AND frontmatter name:**
```python
for p in root.rglob("SKILL.md"):
    dir_name = p.parent.name
    post = frontmatter.load(p)
    skill = Skill.model_validate(dict(post.metadata))
    catalog.skills[skill.name] = skill      # frontmatter key
    catalog.skills[dir_name] = skill        # directory alias
```

**Pros:**
- ✅ **Backward compatible** — existing agent `skills: [differential-review]` references keep working

**Cons:**
- ❌ **Ambiguity** — `review-differential-review` and `differential-review` resolve to same skill
- ❌ **Namespace pollution** — 70 keys for 52 skills (19 duplicates)
- ❌ **Poor discoverability** — two names for one skill violates "name is unique identifier" principle
- ❌ **Glob confusion** — does `skills: [review-*]` match `review-differential-review` or `differential-review`? Both? Neither?
- ❌ **Quality degradation** — allows sloppy naming to persist indefinitely

**Effort:** 15 lines of resolver code. Ongoing confusion explaining dual-naming to users.

---

## 4. Recommendation: **Option A (Rename Frontmatter)**

### Rationale

**Option A is the only choice that preserves all five user principles:**

| Principle | Option A | Option B | Option C |
|---|:---:|:---:|:---:|
| Minimal exposure | ✅ | ✅ | ⚠️ |
| Prefix-based assignment | ✅ | ✅ | ❌ |
| Shared skill naming | ✅ | ❌ | ❌ |
| Plugin bundling | ✅ | ✅ | ✅ |
| High quality | ✅ | ❌ | ❌ |

**Quality implications:**

- **Specificity**: Prefixed names force precise categorization. `review-differential-review` is unambiguous; `differential-review` could plausibly belong to multiple workflows.
  
- **Composability**: Glob patterns require consistent naming. `skills: [review-*, stdd-tdd]` is self-documenting; `skills: [differential-review, systematic-debugging, stdd-tdd]` obscures the review/dev boundary.
  
- **Discoverability**: Marketplace browsers (future feature) will group skills by prefix. `review-*` skills cluster together; unprefixed skills scatter alphabetically.
  
- **Progressive disclosure**: The pydantic-ai-skills `advertise()` surface exposes `name + description`. Prefixed names let agents filter irrelevant categories before reading descriptions:
  ```python
  # Agent sees 52 skill names at startup:
  ["alpine-js-patterns", "review-differential-review", "stdd-tdd", ...]
  
  # Review agent filters:
  candidates = [s for s in all_skills if s.startswith("review-")]
  # → ["review-differential-review", "review-systematic-debugging", ...]
  # → load descriptions only for 5 skills, not 52
  ```

**Spec compliance**: agentskills.io is an **open standard** backed by Microsoft, OpenAI, Atlassian, Figma, Cursor, and GitHub. Violating the spec (Option B) or creating spec-incompatible aliases (Option C) forfeits interoperability with the broader ecosystem.

**Migration path**: The 19 affected skills are **internal marketplace content**, not published to agentskills.io yet. This is the last low-cost opportunity to align before external adoption.

---

## 5. Implementation Plan

### Phase 1: Bulk Rename (15 minutes)

**Script-assisted bulk edit** of 19 SKILL.md files:

```python
# scripts/align_skill_names.py
from pathlib import Path
import frontmatter

MISMATCHES = {
    ".agents/skills/review-differential-review": "review-differential-review",
    ".agents/skills/review-systematic-debugging": "review-systematic-debugging",
    # ... (17 more)
}

for skill_dir, correct_name in MISMATCHES.items():
    skill_md = Path(skill_dir) / "SKILL.md"
    post = frontmatter.load(skill_md)
    post.metadata["name"] = correct_name
    frontmatter.dump(post, skill_md)
```

### Phase 2: Update Agent References (10 minutes)

**Find agents declaring unprefixed names:**
```bash
cd .agents/agents
grep -r 'skills:' . | grep -E '(differential-review|systematic-debugging|openspec)'
```

**Update to prefixed or glob form:**
```diff
 skills:
-  - differential-review
-  - systematic-debugging
+  - review-*
```

### Phase 3: Validator Pass (5 minutes)

```bash
python -m harness_workflow.validate .agents --strict
```

Expected: 0 errors, ≤20 warnings (down from 24 after fixing YAML inline-dict quoting).

### Phase 4: Resolver Smoke Test (2 minutes)

```python
from harness_workflow.resolver import scan_marketplace, expand_globs
catalog = scan_marketplace(Path(".agents"))
assert len(expand_globs(["review-*"], catalog)) == 5  # ← must pass
```

**Total effort:** ~30 minutes to unblock Phase 3+.

---

## 6. Long-Term Quality Gates

To prevent regression, add **pre-commit hook** enforcing directory/name alignment:

```python
# .git/hooks/pre-commit
import sys
from pathlib import Path
import frontmatter

for skill_md in Path(".agents/skills").rglob("SKILL.md"):
    post = frontmatter.load(skill_md)
    expected_name = skill_md.parent.name
    actual_name = post.metadata.get("name")
    if actual_name != expected_name:
        print(f"❌ {skill_md}: name mismatch")
        print(f"   Directory: {expected_name}")
        print(f"   Frontmatter: {actual_name}")
        sys.exit(1)
```

Integrate into **validator strict mode**:
```bash
python -m harness_workflow.validate .agents --strict --check-alignment
```

---

## 7. Decision Required

**Approve Option A** to proceed with Phase 3+ implementation, or **request alternative** if business constraints override technical recommendation.

**Blocking:** State manager, enforcement hooks, workflow compiler, `/new-workflow` command.

**Timeline impact:** Each day of delay pushes Phase 9 delivery (full OpenCode parity + docs).
