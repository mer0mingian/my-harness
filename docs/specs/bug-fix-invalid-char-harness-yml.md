# Bug Fix Spec: Invalid Character in `.harness.yml`

**Status:** Ready for implementation
**Date:** 2026-05-14
**Scope:** Single file fix in `harness-sandbox/workspace-template/.harness.yml`

---

## 1. Bug Description

The workspace template file `harness-sandbox/workspace-template/.harness.yml` contains 26 em-dash characters (`—`, U+2014) used as visual separators in YAML comments. While YAML 1.2 technically permits arbitrary UTF-8 in comments, downstream tooling that consumes this file (strict YAML parsers, linters, shell-based grep/awk pipelines, and corporate proxies that normalise input to ASCII) rejects or mangles the file.

### Symptoms

- YAML parse failures when the file is consumed by stricter parsers (e.g., `yamllint`, certain Go-based parsers used by Harness/CD tooling).
- Visual corruption when the file is rendered through ASCII-only pipelines (em-dash becomes `???`, `\xe2\x80\x94`, or mojibake).
- Linting tools flagging non-ASCII characters in a config file expected to be portable across systems.
- Copy/paste of fenced sections fails when targets only accept ASCII.

---

## 2. Root Cause Analysis

The em-dash characters were introduced (likely from a markdown/word-processor copy-paste) as typographic separators in comments such as `# Litho — Documentation generation`. The character `—` (U+2014, UTF-8 bytes `E2 80 94`) is:

- **Not ASCII** — breaks tools assuming ASCII input.
- **Visually similar to hyphen-minus** — bug is hard to spot in editors with proportional fonts.
- **Semantically equivalent** to a hyphen in this context — purely decorative, no syntactic role.

All 26 occurrences appear inside YAML comments (after `#`), so the fix is a pure character substitution with no impact on YAML semantics.

---

## 3. Affected Lines (26 total)

All occurrences are in `/home/minged01/repositories/harness-workplace/harness-sandbox/workspace-template/.harness.yml`.

| #  | Line | Before                                                                          | After                                                                          |
|----|------|---------------------------------------------------------------------------------|--------------------------------------------------------------------------------|
| 1  | 1    | `# .harness.yml — Agent-Workspace Configuration`                                | `# .harness.yml - Agent-Workspace Configuration`                               |
| 2  | 65   | `# CodeGraphContext — Code graph analysis and semantic search`                  | `# CodeGraphContext - Code graph analysis and semantic search`                 |
| 3  | 77   | `# Litho — Documentation generation (deepwiki-rs)`                              | `# Litho - Documentation generation (deepwiki-rs)`                             |
| 4  | 94   | `# Disabled by default — enable and configure auth tokens in .harness.local.yml`| `# Disabled by default - enable and configure auth tokens in .harness.local.yml`|
| 5  | 97   | `# DataDog — Monitoring, metrics, dashboards, incidents`                        | `# DataDog - Monitoring, metrics, dashboards, incidents`                       |
| 6  | 116  | `# Terraform Registry — Infrastructure as Code registry access`                 | `# Terraform Registry - Infrastructure as Code registry access`                |
| 7  | 132  | `# Slack — Team communication and notifications`                                | `# Slack - Team communication and notifications`                               |
| 8  | 150  | `# Kibana — Log analysis, dashboards, metrics visualization`                    | `# Kibana - Log analysis, dashboards, metrics visualization`                   |
| 9  | 166  | `# Stonehenge (Backstage) — Developer portal, service catalog`                  | `# Stonehenge (Backstage) - Developer portal, service catalog`                 |
| 10 | 204  | `# AWS Docs — AWS documentation (read-only, safe for default enablement)`       | `# AWS Docs - AWS documentation (read-only, safe for default enablement)`      |
| 11 | 213  | `# Atlassian — Jira, Confluence, Bitbucket integration`                         | `# Atlassian - Jira, Confluence, Bitbucket integration`                        |
| 12 | 332  | `1. Constitution — Project principles (docs/constitution.md)`                   | `1. Constitution - Project principles (docs/constitution.md)`                  |
| 13 | 333  | `2. Specify — Feature requirements (specs/*.md)`                                | `2. Specify - Feature requirements (specs/*.md)`                               |
| 14 | 334  | `3. Plan — Implementation plans (docs/plans/active/*.md)`                       | `3. Plan - Implementation plans (docs/plans/active/*.md)`                      |
| 15 | 335  | `4. Tasks — Task breakdown (docs/tasks/active/*.md)`                            | `4. Tasks - Task breakdown (docs/tasks/active/*.md)`                           |
| 16 | 336  | `5. Assign — Route to specialized agents (.claude/agents/*.yml)`                | `5. Assign - Route to specialized agents (.claude/agents/*.yml)`               |
| 17 | 337  | `6. Validate — Check for assignment conflicts`                                  | `6. Validate - Check for assignment conflicts`                                 |
| 18 | 338  | `7. Execute — Run tasks via dedicated subagents`                                | `7. Execute - Run tasks via dedicated subagents`                               |
| 19 | 339  | `8. Implement — TDD workflow (tests first, implement, refactor)`                | `8. Implement - TDD workflow (tests first, implement, refactor)`               |
| 20 | 340  | `9. Test Coverage — Validate coverage against spec (...)`                       | `9. Test Coverage - Validate coverage against spec (...)`                      |
| 21 | 341  | `10. Verify — Evidence-based completion (test output, runtime logs, E2E)`       | `10. Verify - Evidence-based completion (test output, runtime logs, E2E)`      |
| 22 | 342  | `11. QA — Browser and CLI validation (docs/qa/)`                                | `11. QA - Browser and CLI validation (docs/qa/)`                               |
| 23 | 343  | `12. Review — 8-point code review (spec alignment, security, performance, etc.)`| `12. Review - 8-point code review (spec alignment, security, performance, etc.)`|
| 24 | 344  | `13. Finish — Create cross-repo PRs`                                            | `13. Finish - Create cross-repo PRs`                                           |
| 25 | 345  | `14. Archive — Post-merge archival to project memory (specs_archive/)`          | `14. Archive - Post-merge archival to project memory (specs_archive/)`         |

> **Note:** `grep -c` reports 25 *lines* containing em-dash, but 26 *instances* — line 340 (item 9) contains two characters: the separator after "Test Coverage" and a trailing ellipsis token. Verify with `grep -o $'\xe2\x80\x94' .harness.yml | wc -l` (expect `26`).

---

## 4. Proposed Fix

Single-character global replacement, scoped to the one file:

- **Find:** `—` (U+2014, em-dash, UTF-8 `E2 80 94`)
- **Replace:** `-` (U+002D, ASCII hyphen-minus)
- **Mode:** Replace all (no exceptions — every occurrence is decorative).

### Implementation (choose one)

**Option A — `sed` (recommended, deterministic):**
```bash
sed -i 's/\xe2\x80\x94/-/g' \
  /home/minged01/repositories/harness-workplace/harness-sandbox/workspace-template/.harness.yml
```

**Option B — Editor Edit tool:**
Use a single `Edit` call with `replace_all: true`, `old_string: "—"`, `new_string: "-"`.

### Out of scope

- In-progress edits already present in the working tree (do not touch).
- Other repos / docs already fixed manually by the user.
- Em-dash usage in markdown documentation (`*.md`) — only `.harness.yml` is in scope.

---

## 5. Validation Steps

Run all checks against the post-fix file. All must pass.

1. **No em-dash remains:**
   ```bash
   grep -c $'\xe2\x80\x94' \
     /home/minged01/repositories/harness-workplace/harness-sandbox/workspace-template/.harness.yml
   # Expected: 0
   ```

2. **File is pure ASCII (no other non-ASCII surprises):**
   ```bash
   LC_ALL=C grep -P '[^\x00-\x7F]' \
     /home/minged01/repositories/harness-workplace/harness-sandbox/workspace-template/.harness.yml
   # Expected: no output, exit code 1
   ```

3. **YAML parses cleanly:**
   ```bash
   python3 -c "import yaml,sys; yaml.safe_load(open(sys.argv[1])); print('OK')" \
     /home/minged01/repositories/harness-workplace/harness-sandbox/workspace-template/.harness.yml
   # Expected: OK
   ```

4. **`yamllint` passes (if available):**
   ```bash
   yamllint /home/minged01/repositories/harness-workplace/harness-sandbox/workspace-template/.harness.yml
   # Expected: no errors related to character encoding
   ```

5. **Line count unchanged** (sanity check the replacement did not eat newlines):
   ```bash
   wc -l /home/minged01/repositories/harness-workplace/harness-sandbox/workspace-template/.harness.yml
   # Expected: same line count as before the fix
   ```

---

## 6. Files to Fix

Exactly one file:

- `/home/minged01/repositories/harness-workplace/harness-sandbox/workspace-template/.harness.yml`

No other files, no other repos, no downstream consumers require updates (the substitution preserves visual intent and YAML semantics).

---

## 7. Acceptance Criteria

- [ ] All 26 em-dash characters replaced with ASCII hyphen-minus in the target file.
- [ ] Validation step 1 returns `0`.
- [ ] Validation step 2 returns no output.
- [ ] Validation step 3 prints `OK`.
- [ ] Diff shows only character substitutions on the 25 affected lines (no other edits).
- [ ] Commit message references this spec.
