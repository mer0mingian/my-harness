# Phase 2 Slice 8: Config Feature Implementations

**Status:** Ready to Execute  
**Complexity:** 8 story points  
**Priority:** P0 — blocks Phase 3 (must complete before /discover and /solution-design)  
**Source:** ROADMAP-Multi-Agent-TDD.md Slice 8, re-scoped via grilling Q16

---

## Scope

Implement the 5 config options already declared in `harness-tdd-config.yml.template` that have no backing implementation. No new config options are added.

Priority order (from Q16c):

| # | Feature | Config Key | Target File |
|---|---------|-----------|-------------|
| 1 | Parallel execution for /review | `workflow.parallel_enabled` | `commands/review.md` |
| 2 | Agent timeout enforcement | `workflow.agent_timeout` | All commands invoking agents |
| 3 | Artifact validation (post-generation) | `validate_artifacts: true` | New script |
| 4 | Convergence detection in review cycles | `gates.convergence_detection` | `commands/review.md` |
| 5 | Local Jira auto-folder creation | `jira.auto_create_stories` | `lib/jira_local.py` |

---

## Task Breakdown

### S8-001: Parallel agent dispatch in /review (2 pts)

**File:** `commands/review.md`

**Current behaviour:** Review command invokes @arch-specialist then @review-specialist sequentially.

**Target behaviour:** When `workflow.parallel_enabled: true`, spawn both agents concurrently; when `false`, sequential (current behaviour preserved).

**Implementation:**
- Read config value `workflow.parallel_enabled` at start of review command
- Add conditional branch in Step 3 (Invoke Agents):
  - `parallel_enabled: true` → instruct simultaneous invocation of both agents, merge results
  - `parallel_enabled: false` → existing sequential flow
- Use `orchestrate-dispatching-parallel-agents` skill pattern for dispatch instructions
- Merge: combine findings from both agents, apply safety-wins conflict resolution

**Acceptance criteria:**
- [ ] `commands/review.md` has valid YAML frontmatter
- [ ] End-to-end run with `parallel_enabled: true` invokes both agents concurrently
- [ ] End-to-end run with `parallel_enabled: false` falls back to sequential (no regression)
- [ ] Review artifacts still generated correctly in both modes

---

### S8-002: Agent timeout enforcement (1 pt)

**Files:** `commands/test.md`, `commands/implement.md`, `commands/review.md`, `commands/commit.md`

**Current behaviour:** No timeout on agent tasks.

**Target behaviour:** Each command reads `workflow.agent_timeout` (minutes) and includes it in agent delegation instructions.

**Implementation:**
- Each command reads `.specify/harness-tdd-config.yml` → `workflow.agent_timeout`
- Default: 30 minutes if config missing
- Add to every agent invocation step: "Complete this task within ${agent_timeout} minutes. If not done, output partial results and escalate."
- On timeout signal from agent, escalate to human with partial artifacts saved

**Acceptance criteria:**
- [ ] All four updated command files have valid YAML frontmatter
- [ ] End-to-end run with a configured `agent_timeout` shows the value reaching agent invocations in test, implement, review, commit
- [ ] Default 30min used if config absent (verified by E2E run with config omitted)

---

### S8-003: Artifact structure validation script (3 pts)

**File:** `scripts/validate_artifact_structure.py` (new helper script)

**Trigger:** Post-generation check (not blocking hook) — warn but don't block.

**Validates:**
- Required sections present (based on artifact template YAML frontmatter)
- YAML frontmatter valid and parseable
- Cross-references exist (e.g., ADR references PRD path)
- File size reasonable (not empty, not > 50KB / ~10 pages)

**Output:** JSON validation report with per-check results.

**Exit codes:** 0=all valid, 1=warnings (non-blocking), 2=error (escalate)

**On failure:** Escalate to human with diagnostics (do not auto-fix, do not block).

**Integration:**
- Called at end of each command that generates artifacts
- Referenced in `hooks/config.yml` as PostToolUse (warn-only)

**Acceptance criteria:**
- [ ] Script validates YAML frontmatter syntax
- [ ] Script checks required sections via template registry
- [ ] Script checks cross-references between artifacts
- [ ] Script checks file size bounds
- [ ] Exit code 1 for warnings, 2 for errors
- [ ] JSON output parseable by calling commands

---

### S8-004: Convergence detection in review cycles (1 pt)

**File:** `commands/review.md`, `scripts/detect_review_convergence.py` (new helper)

**Current behaviour:** Review repeats up to `gates.max_review_cycles` times regardless of findings.

**Target behaviour:** When `gates.convergence_detection: true`, detect if consecutive review cycles produce identical findings — stop early.

**Algorithm:**
1. After each review cycle, hash the key findings from both review artifacts
2. If hash matches previous cycle: convergence detected → stop cycling
3. If `max_review_cycles` reached without convergence: escalate

**Implementation:**
- Simple hash comparison script (not ML)
- Hash: extract bullet points / findings list → sort → SHA256
- Update review command to call script between cycles

**Acceptance criteria:**
- [ ] Convergence detected when two consecutive cycles produce same findings
- [ ] Early stop triggered on convergence
- [ ] Max cycles still enforced as hard limit if no convergence

---

### S8-005: Local Jira auto-folder creation (1 pt)

**File:** `lib/jira_local.py`

**Current behaviour:** `auto_create_stories: true` is declared but not implemented.

**Target behaviour:** When `/commit` runs and `jira.auto_create_stories: true`, create folder structure:
```
.specify/epics/${epic_id}/
  ${story_id}.md  ← created from story template
```

**Implementation:**
- Add `auto_create_story_structure(feature_id, epic_id, story_id)` to `lib/jira_local.py`
- Called from `commands/commit.md` Step 1 (pre-commit)
- Uses `jira.root` config for base path
- Only creates if folder/file doesn't exist (idempotent)

**Acceptance criteria:**
- [ ] Python `lib/jira_local.py` `auto_create_story_structure` covered by pytest
- [ ] End-to-end commit run with `auto_create_stories: true` creates `.specify/epics/{epic_id}/{story_id}.md` if missing
- [ ] Idempotent (no error if already exists)
- [ ] Skipped silently when `auto_create_stories: false`

---

## Validation Checklist

- [ ] All 5 features implemented
- [ ] `scripts/validate_artifact_structure.py` works standalone: `python3 scripts/validate_artifact_structure.py feat-test`
- [ ] `scripts/detect_review_convergence.py` works standalone
- [ ] End-to-end smoke test of `/review` with `parallel_enabled=true` and `=false` produces correct artifacts
- [ ] End-to-end run shows configured `agent_timeout` reaches agent invocations in test, implement, review, commit
- [ ] Jira auto-create tested with real folder structure
- [ ] YAML frontmatter on all modified `commands/*.md` files validates (yamllint or equivalent)
- [ ] No regressions in existing Phase 2 commands (re-run end-to-end test)

---

## Open Points

- **Mermaid diagram validation** (Q9c): deferred to after Phase 4. Install `mermaid-fixer` from `https://github.com/sopaco/mermaid-fixer` in sandbox container when ready.

---

## Dependencies

- Phase 2 commands (test.md, implement.md, review.md, commit.md) must be complete ✅
- `harness-tdd-config.yml.template` defines the config schema ✅
- `lib/jira_local.py` exists as base for S8-005 ✅
