---
name: stdd-pm-linear-integration
description: Linear CLI wrapper for issue fetch, status update, and comment posting,
  with markdown-fallback simulation reading from docs/tickets/*.md when Linear is
  unavailable. Generates file manifests from issue acceptance criteria. Use when
  @pries-pm needs to ingest a ticket, validate references to NFRs, and build the
  task specification for downstream PRIES phases.
---
# STDD PM: Linear Integration

Issue-management skill for the PRIES `@pries-pm` agent. Wraps the Linear
CLI for the operations the workflow needs and provides a markdown fallback
when the CLI is unavailable (offline, sandbox without auth, MVP mode).

## When to use

- The `/pries-implement <ISSUE-ID>` command starts and the PM agent needs
  the ticket body and metadata.
- A status transition (`In Progress`, `In Review`, `Done`) must be made.
- A comment must be posted (e.g., draft PR link, completion summary).
- The agent must validate that a ticket references the expected NFR IDs
  and acceptance criteria.

## Operations

### 1. Fetch issue

**Linear mode**:

```bash
linear issue view <ID> --json
```

Parse JSON for: `title`, `description`, `state`, `priority`, `labels`,
`assignee`, `comments[].body`. Capture the raw JSON in the run report
for traceability.

**Markdown fallback** (when `linear` is not on PATH or `LINEAR_API_KEY`
is unset):

```
docs/tickets/<ID>.md
```

Expected schema (see example below). The agent treats this file as the
source of truth for the issue.

### 2. Update status

**Linear mode**:

```bash
linear issue update <ID> --state "In Progress"
```

**Markdown fallback**: append a status line to `docs/tickets/<ID>.md`:

```markdown
## Status Log
- 2026-04-26T10:32:00Z — In Progress (started by @pries-pm)
```

### 3. Add comment

**Linear mode**:

```bash
linear issue comment <ID> --body "<markdown>"
```

**Markdown fallback**: append to a `## Comments` section in the ticket
file with timestamp and author.

## Markdown fallback ticket schema

`docs/tickets/<ID>.md`:

```markdown
# <Issue Title>

**Issue ID:** <ID>
**Type:** Feature | Bug | Chore
**Priority:** P0 | P1 | P2 | P3
**State:** Backlog | In Progress | In Review | Done

## User Stories
- As a <role>, I want <goal>, so that <value>.

## Acceptance Criteria
- AC-1: <testable statement>
- AC-2: <testable statement>

## Related Artifacts
- NFR-PERF-002 (multiplayer sync latency)
- TECHNICAL_CONSTITUTION.md §2.1 (FastAPI + WebSockets)
- TEST_STRATEGY.md (Playwright E2E pattern)

## Status Log
- ...

## Comments
- ...
```

## File-manifest generation

After parsing the ticket, the PM produces a draft file manifest by:

1. Grep the codebase for symbols mentioned in acceptance criteria.
2. Trace imports to identify the modules likely to change.
3. List candidate test files matching `tests/<area>/test_*.py`.
4. Output a structured manifest for @pries-make's `mode: tdd` dispatch.

The PM does **not** modify production code; only `docs/tickets/` is
write-allowed.

## NFR validation

If `docs/governance/NFR_CATALOG.md` exists:

- Confirm each NFR ID referenced in the ticket exists in the catalog.
- For unreferenced surfaces (e.g., a perf-sensitive endpoint without a
  perf NFR), flag a recommendation to run `/governance-add-nfr`.

## Constraints

- **Linear CLI commands only** for shell access. No `git`, no installs.
- **Read-only against the codebase** except for `docs/tickets/`.
- **Never delete issues**, even when the CLI supports it.
- **Always pass `--json`** to Linear queries for structured parsing.
- New issues created by this skill **MUST** pass `--state Backlog`
  explicitly so Linear does not auto-assign them to Triage.

## Output contract

```yaml
ticket:
  id: STA-001
  title: "Real-time Momentum Pool Synchronization"
  state: "In Progress"
  priority: P0
  acceptance_criteria:
    - "WebSocket connection established on scene activation"
    - "Updates broadcast within 200 ms (NFR-PERF-002)"
    - "Graceful degradation if WebSocket unavailable"
    - "E2E test validates multi-client sync"
  nfr_refs: [NFR-PERF-002]
  related_constitution_sections: ["§2.1 — Real-time"]
draft_file_manifest:
  src:
    - app/api/momentum.py
    - app/services/broadcast.py
  tests:
    - tests/api/test_momentum.py
notes: "Used markdown fallback; Linear CLI not authenticated in sandbox."
```

## Anti-patterns

- Hard-failing when the Linear CLI is missing (use the markdown fallback).
- Mutating production code from the PM agent.
- Updating Linear state to `Done` from the PM agent (that belongs to the
  final commit/PR phase).
- Inventing NFR IDs that don't appear in `NFR_CATALOG.md`.
