# PRIES Plugin Smoke Test Checklist

**Purpose:** Lightweight verification that the PRIES plugin is installed
and discoverable by Claude Code and OpenCode.

Run through this checklist after any structural change to the plugin
(new agents, renamed skills, command rewrites).

---

## Prerequisites

- `harness-tooling` repo cloned, `feat/pries-workflow` branch checked out.
- `.claude/` and `.opencode/` symlinks present (`ls -la .claude .opencode`
  shows symlinks to `../.agents/...`).

## Resolution checks

### Commands

- [ ] `/pries-implement` resolves (file exists at
      `.agents/commands/pries-implement.md`).
- [ ] `/pries-review-only` resolves.
- [ ] `/pries-test-only` resolves.
- [ ] `/pries-validate` resolves.

```bash
ls .agents/commands/pries-*.md
# Expect 4 files.
```

### Agents

- [ ] `.agents/agents/pries-pm.md` exists with both `skills:` (Claude)
      and `permission.skill:` (OpenCode) frontmatter blocks.
- [ ] `.agents/agents/pries-check.md` — same.
- [ ] `.agents/agents/pries-simplify.md` — same.
- [ ] `.agents/agents/pries-test.md` — same, with restrictive write/edit
      ACL on test-only patterns.
- [ ] `.agents/agents/pries-make.md` — same, with denial of git/pip/curl.

```bash
for f in .agents/agents/pries-*.md; do
  echo "=== $f ==="
  grep -E "^(skills:|permission:)" "$f" | head -3
done
```

### Skills

- [ ] `.agents/skills/stdd-test-author-constrained/SKILL.md` exists with
      valid frontmatter.
- [ ] `.agents/skills/review-check-correctness/SKILL.md` exists.
- [ ] `.agents/skills/stdd-make-constrained-implementation/SKILL.md`
      exists.
- [ ] `.agents/skills/review-orchestrate-dual-review/SKILL.md` exists.
- [ ] `.agents/skills/stdd-pm-linear-integration/SKILL.md` exists.
- [ ] `.agents/skills/review-simplify-complexity/SKILL.md` exists.

```bash
ls .agents/skills/stdd-test-author-constrained \
   .agents/skills/review-check-correctness \
   .agents/skills/stdd-make-constrained-implementation \
   .agents/skills/review-orchestrate-dual-review \
   .agents/skills/stdd-pm-linear-integration \
   .agents/skills/review-simplify-complexity
# Each should contain SKILL.md.
```

## Frontmatter validity

- [ ] Each skill has `name:` matching its directory name.
- [ ] Each skill has a `description:` field with at least 80 chars.
- [ ] Each agent has both Claude (`skills:` array) and OpenCode
      (`permission:` block) frontmatter.

```bash
# Quick sanity check: skill names match dirs.
for d in .agents/skills/stdd-test-author-constrained \
         .agents/skills/review-check-correctness \
         .agents/skills/stdd-make-constrained-implementation \
         .agents/skills/review-orchestrate-dual-review \
         .agents/skills/stdd-pm-linear-integration \
         .agents/skills/review-simplify-complexity; do
  expected=$(basename "$d")
  actual=$(grep "^name:" "$d/SKILL.md" | head -1 | awk '{print $2}')
  [[ "$expected" == "$actual" ]] && echo "OK $expected" || echo "MISMATCH $expected -> $actual"
done
```

## Skill reference integrity

- [ ] Every skill listed in `pries-pm.md`'s `skills:` exists in
      `.agents/skills/`.
- [ ] Same for `pries-check.md`, `pries-simplify.md`, `pries-test.md`,
      `pries-make.md`.

```bash
# Manual cross-check: each skill in agent frontmatter must exist.
for agent in .agents/agents/pries-*.md; do
  echo "=== $agent ==="
  awk '/^skills:/{flag=1;next} /^[a-zA-Z]/{flag=0} flag && /^  - /{print $2}' "$agent" | \
    while read skill; do
      [[ -d ".agents/skills/$skill" ]] && echo "  OK $skill" || echo "  MISSING $skill"
    done
done
```

## STA-001 example dispatch (dry run)

- [ ] `.agents/examples/pries/sta2e-vtt/example-ticket.md` parses
      against the `stdd-pm-linear-integration` markdown-fallback schema.
- [ ] Acceptance criteria in the ticket reference at least one NFR ID.
- [ ] Example ticket points to file paths consistent with the
      `pries-pm` draft-manifest output format.

## Convergence detection (paper-test)

Walk through `pries-implement.md` Phase 5 by hand:

- [ ] Cycle 1 produces N findings.
- [ ] Cycle 2 produces 0 new BLOCKER/CRITICAL — orchestrator should
      proceed.
- [ ] Cycle 3 with 1 new BLOCKER — orchestrator should NOT declare
      converged.

The skill `review-orchestrate-dual-review` documents this rule in the
"Convergence loop" section.

## Validate command — paper test

- [ ] `pries-validate.md` returns PASS when:
  - `docs/governance/` artefacts are valid.
  - All NFRs have TEST_STRATEGY entries.
  - Pyramid drift within tolerance.
  - Contracts (NFR ID format, priorities, EARS) clean.
- [ ] Returns FAIL with specific violations otherwise.

## Documentation

- [ ] `.agents/docs/pries-workflow-integration.md` exists and references
      Phase 0 governance artefacts.
- [ ] `.agents/docs/pries-workflow-usage.md` exists with at least one
      end-to-end example.
- [ ] `.agents/examples/pries/sta2e-vtt/` contains the five example files
      (ticket, plan, tests, implementation, review).

## Sign-off

When all boxes are checked, the plugin is ready to dispatch against a
real ticket. Re-run after any structural edit.
