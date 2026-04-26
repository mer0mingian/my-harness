# Governance Plugin — Smoke Test

A reproducible end-to-end validation of the Technical Governance plugin. Use
this when changing any skill, agent, or schema in `.agents/.../governance*`.

---

## Prerequisites

- Python 3.12+
- `uv` (or `pip`) for running the validator script
- A clean checkout of `harness-tooling` on branch `feat/technical-governance`
- (Optional) Claude Code or OpenCode for the human-in-the-loop steps

```bash
cd harness-tooling
uv venv
uv pip install jsonschema pyyaml
```

---

## Step 1 — Schema validity

The three JSON schemas must themselves be valid Draft 2020-12 JSON Schema
documents.

```bash
python -c '
import json, sys
from pathlib import Path
from jsonschema import Draft202012Validator
schemas = [
    ".agents/schemas/governance/constitution.schema.json",
    ".agents/schemas/governance/nfr.schema.json",
    ".agents/schemas/governance/test-strategy.schema.json",
]
for s in schemas:
    data = json.loads(Path(s).read_text())
    Draft202012Validator.check_schema(data)
    print(f"OK {s}")
'
```

Expected: three `OK` lines.

---

## Step 2 — Validator script self-check

Validate the **example** artifacts (which are intentionally well-formed) by
copying them into the expected location and running the validator.

```bash
mkdir -p /tmp/governance-smoke/docs/governance
cp .agents/examples/governance/sta2e-vtt/*.md /tmp/governance-smoke/docs/governance/
python .agents/skills/governance-validate-artifacts/scripts/validate.py --root /tmp/governance-smoke
```

Expected: `overall: PASS` with `errors: 0`. A handful of warnings is
acceptable (e.g. rationale-missing on tightly-worded MUST lines).

---

## Step 3 — Validator catches a planted defect

Plant a known violation and confirm the validator reports it.

```bash
# Break the EARS keyword on NFR-PERF-001.
sed -i 's/the system shall return a response/the system MUST return a response/' \
    /tmp/governance-smoke/docs/governance/NFR_CATALOG.md
# (we removed "shall"; the sentence still has "when" so this passes — let's break harder)
sed -i 's/When a user requests data via any REST endpoint under `\/api\/v1\/`, the system shall return a response/A user gets data fast/' \
    /tmp/governance-smoke/docs/governance/NFR_CATALOG.md

python .agents/skills/governance-validate-artifacts/scripts/validate.py --root /tmp/governance-smoke
echo "exit code: $?"
```

Expected: `overall: FAIL`, an `ears_keyword_required` error on
`NFR-PERF-001`, exit code `1`.

Restore:

```bash
cp .agents/examples/governance/sta2e-vtt/NFR_CATALOG.md \
   /tmp/governance-smoke/docs/governance/NFR_CATALOG.md
```

---

## Step 4 — Validator catches a missing cross-reference

Reference a non-existent NFR from the test strategy and confirm the
cross-reference check fires.

```bash
sed -i 's/NFR-PERF-002, NFR-USE-001/NFR-PERF-999, NFR-USE-001/' \
    /tmp/governance-smoke/docs/governance/TEST_STRATEGY.md
python .agents/skills/governance-validate-artifacts/scripts/validate.py --root /tmp/governance-smoke
echo "exit code: $?"
```

Expected: `cross_reference` error mentioning `NFR-PERF-999`, exit code `1`.

Restore:

```bash
cp .agents/examples/governance/sta2e-vtt/TEST_STRATEGY.md \
   /tmp/governance-smoke/docs/governance/TEST_STRATEGY.md
```

---

## Step 5 — Symlink integrity

Confirm the per-CLI directories surface the new agents/skills/commands.

```bash
test -L .claude/skills && test -d .claude/skills/governance-interview-tech-stack && echo "OK .claude skills"
test -L .claude/agents && test -e .claude/agents/governance-lead.md && echo "OK .claude agents"
test -L .claude/commands && test -e .claude/commands/governance-setup.md && echo "OK .claude commands"
test -L .opencode/skills && test -d .opencode/skills/governance-interview-tech-stack && echo "OK .opencode skills"
test -L .opencode/agents && test -e .opencode/agents/governance-lead.md && echo "OK .opencode agents"
test -L .opencode/commands && test -e .opencode/commands/governance-setup.md && echo "OK .opencode commands"
```

Expected: six `OK` lines.

---

## Step 6 — Dual-CLI frontmatter sanity

Each agent file must contain both Claude-Code-style `skills:` and
OpenCode-style `permission.skill:` keys.

```bash
for f in .agents/agents/governance-*.md; do
    grep -q "^skills:" "$f" || { echo "MISS skills: $f"; exit 1; }
    grep -q "^permission:" "$f" || { echo "MISS permission: $f"; exit 1; }
    grep -qE "^\s+skill:" "$f" || { echo "MISS permission.skill: $f"; exit 1; }
    echo "OK $f"
done
```

Expected: four `OK` lines (one per governance agent), no `MISS`.

---

## Step 7 — Human dry-run (optional)

In Claude Code (or OpenCode):

1. Open a fresh repo.
2. Run `/governance-setup My Pilot Project`.
3. Watch `@governance-lead` ask the eight interview blocks.
4. Confirm three artifacts land in `docs/governance/`.
5. Run `/governance-validate` and expect `PASS` (or actionable `WARN`).

---

## Pass / fail criteria

The plugin passes the smoke test when **all of**:

- Steps 1, 5, 6 produce only `OK` lines.
- Step 2 produces `overall: PASS`.
- Steps 3 and 4 produce `overall: FAIL` with the expected rule names.
- (If executed) Step 7 produces three valid artifacts and a passing
  validation report.

Any deviation is a release blocker for the plugin.
