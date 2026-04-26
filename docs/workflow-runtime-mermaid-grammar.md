# Mermaid sequenceDiagram Grammar Subset for Tier 1 Authoring
**Phase R deliverable — D4 — 2026-04-23**
This is a specification for the compiler front-end (`compiler/mermaid_sequence.py`).
Companion: `docs/notes/workflow-runtime-baseline.md` (D1–D3), `docs/WORKFLOW_ORCHESTRATOR_REQUIREMENTS.md` §18 Tier 1.

---

## 1. Accepted Constructs

### 1.1 `participant` — agent declarations

```
participant <id> as <display-name>
```

- Each `participant` line maps to one entry in `WorkflowManifest.agents`.
- The `id` becomes the agent's internal identifier (used in message arrows).
- The `as` display name is stored as `agent.display_name`.
- `actor` keyword: accepted as a synonym for `participant`; treated identically.

**Example:**
```
participant PM as Product Manager
participant Arch as Architect
participant TW as Test Writer
participant Impl as Implementer
participant Rev as Reviewer
participant Orc as Orchestrator
```

---

### 1.2 `->>` sync messages — phase declarations

```
<from-id>->><to-id>: <phase-name> [<metadata>]
```

- Each `participant A ->> participant B: label` line declares one **phase**.
- `from-id` is the **driver agent** initiating the phase.
- `to-id` is the **primary worker agent** (or same as driver for self-directed phases).
- `label` is `phase.name`.
- Optional `[<metadata>]` bracket suffix carries per-phase metadata (see §2).
- Arrow variants `->`, `->>`, `-->>` are all accepted; the compiler ignores the async/dotted distinction and treats all as synchronous phase transitions.

**Example:**
```
Orc->>PM: fetch-issue [skills: stdd-pm-*; writes: docs/tickets/**; max_iter: 1]
PM->>Arch: decompose [skills: stdd-arch-*; writes: docs/plans/**; max_iter: 1]
```

---

### 1.3 `par` blocks — parallel phases

```
par <label>
    <from>->><to>: <phase-name> [<metadata>]
and
    <from>->><to>: <phase-name> [<metadata>]
end
```

- A `par` block maps to a **parallel phase group** in `WorkflowManifest`.
- The block label (after `par`) is stored as `phase_group.name`.
- Each arm inside the block becomes a sub-phase with its own driver/worker/metadata.
- All arms are launched concurrently; the workflow advances only when all arms complete.
- `and` separates arms; unlimited arms supported (though >4 is unusual).

**Example:**
```
par parallel-review
    Rev->>Rev: design-review [skills: review-*; writes: none; max_iter: 3; converge: same_findings_twice]
and
    Rev->>Rev: simplicity-review [skills: review-*; writes: none; max_iter: 3; converge: same_findings_twice]
end
```

---

### 1.4 `loop` blocks — convergence-gated phases

```
loop <convergence-expression>
    <from>->><to>: <phase-name> [<metadata>]
end
```

- A `loop` block maps to a **convergence-gated phase** in `WorkflowManifest`.
- The label (after `loop`) is parsed as a convergence expression: `<rule>, max=<n>`.
- Supported convergence rules: `same_findings_twice`, `all_tests_pass`, `no_issues_found`.
- If `max=<n>` is present, it overrides any `max_iter` from the message metadata inside the block.
- The body of the loop contains exactly one message line (the repeating phase).

**Example:**
```
loop same_findings_twice, max=3
    Rev->>Rev: adversarial-review [skills: review-*; writes: none]
end
```

---

### 1.5 `note over` — phase annotations

```
note over <id>[, <id2>]: <text>
```

- Maps to `phase.annotation` on the most-recently declared phase or phase group.
- Multi-participant notes (`over A, B`) are stored on the enclosing phase group.
- Free-form text; not structured by the compiler. Surfaced in `workflow.mmd` output verbatim.

**Example:**
```
note over TW, Impl: Each work unit is processed in a fan-out loop (max 2 parallel)
```

---

## 2. Bracket-Metadata Convention

Per-phase metadata is encoded in a `[key: value; key: value]` suffix on message labels. This is the primary mechanism for carrying per-phase constraints and configuration inline in the diagram.

### 2.1 Syntax

```
<from>->><to>: <phase-name> [key: value; key: value; ...]
```

- Brackets are optional. A message without brackets is a valid phase with defaults.
- Keys are lowercase, underscored (`max_iter`, not `max-iter`).
- Multi-value fields use comma separation within the value: `skills: stdd-pm-*, stdd-arch-*`.
- Semicolons separate key-value pairs.
- Leading/trailing whitespace inside brackets is stripped.

### 2.2 Accepted keys

| Key | Type | Example | Maps to |
|---|---|---|---|
| `skills` | Comma-sep glob list | `stdd-pm-*, review-*` | `phase.skills` |
| `writes` | Comma-sep glob | `docs/plans/**, src/**` | `phase.constraints.write_access` |
| `reads` | Comma-sep glob | `docs/**, openspec/**` | `phase.constraints.read_scope` |
| `model` | String | `claude-opus` | `phase.model` |
| `max_iter` | Integer | `3` | `phase.convergence.max_iterations` |
| `converge` | Rule name | `same_findings_twice` | `phase.convergence.convergence_rule` |
| `bash_scope` | Enum | `sandboxed_pytest`, `sandboxed_no_pip_git`, `none` | `phase.constraints.bash_scope` |
| `external_apis` | Comma-sep | `linear, github` | `phase.constraints.external_apis` |
| `output` | Filename | `work_units.json` | `phase.output.artifact` |
| `gate` | Rule name | `pytest_shows_red` | `phase.output_gate.validation` |
| `workers` | Comma-sep agent ids | `Rev1, Rev2` | `phase.workers` |
| `no_write` | Boolean flag | `true` | `phase.constraints.write_access: none` |

**Rules:**
- Unknown keys emit a **compiler warning** and are stored in `phase.extensions` (passthrough).
- `max_iter` inside a `loop` block body is overridden by the `loop` label's `max=<n>`.
- `converge` inside a message body is overridden by the `loop` label's convergence rule.

### 2.3 Examples

```
Orc->>PM: fetch-issue [skills: stdd-pm-*; writes: docs/tickets/**; max_iter: 1]
TW->>TW: write-failing-tests [skills: stdd-test-*; writes: test_*.py,tests/**; bash_scope: sandboxed_pytest; gate: pytest_shows_red]
Impl->>Impl: implement-to-green [skills: stdd-impl-*; writes: src/**,lib/**; bash_scope: sandboxed_no_pip_git; gate: pytest_shows_green]
Orc->>Orc: commit-and-pr [skills: general-git-*; writes: git_operations_only; gate: all_tests_pass]
```

---

## 3. Deferred or Rejected Constructs

| Construct | Status | Rationale |
|---|---|---|
| `alt / else / opt` | **Deferred to v1.1** | Conditional branching requires a richer AST than the v1 phase manifest supports. Model in `phase.extensions` as a custom field until schema is extended. |
| `activate / deactivate` | **Ignored** | Activation bars convey timing in UML; they carry no phase-manifest semantics. The compiler silently skips these lines. |
| `autonumber` | **Ignored** | Display decoration only; phases are already ordered by line position. |
| `link` / `links` | **Rejected for v1** | Mermaid link decorators have no manifest equivalent. |
| Inline HTML in labels | **Rejected** | HTML in message labels breaks the bracket-metadata parser. The compiler errors on any label containing `<`. |
| `zenuml` front-end | **Deferred to v1.1** | The `sequenceDiagram` subset is sufficient for v1. zenuml adds a second parser with minimal authoring benefit until `alt/else` is needed. |
| `rect` (background fill) | **Ignored** | Display-only; no manifest semantics. |
| `box` / `destroy` | **Ignored** | Introduced in recent Mermaid versions; no manifest equivalent. |
| `critical / break` | **Rejected** | These constructs imply error-path branching; not in the v1 phase model. |

---

## 4. Worked Example — TDD Workflow (11-Phase)

This is the **acceptance artifact** for Phase 5 compiler tests. It expresses the TDD orchestration workflow from `WORKFLOW_ORCHESTRATOR_REQUIREMENTS.md` §Concrete Example in the mermaid subset, followed by the compiled YAML the compiler must produce.

### 4.1 Mermaid source

```mermaid
sequenceDiagram
    participant Orc as Orchestrator
    participant PM as Product Manager
    participant Arch as Architect
    participant Rev as Reviewer
    participant TW as Test Writer
    participant Impl as Implementer
    participant IntTest as Integration Tester

    Orc->>Orc: setup [skills: stdd-pm-*; no_write: true; max_iter: 1]
    Orc->>PM: fetch-issue [skills: stdd-pm-*; external_apis: linear; writes: docs/tickets/**; max_iter: 1]

    par parallel-design-review
        Rev->>Rev: design-review [skills: review-*; no_write: true; max_iter: 3; converge: same_findings_twice]
    and
        Rev->>Rev: simplicity-review [skills: review-*; no_write: true; max_iter: 3; converge: same_findings_twice]
    end

    Arch->>Arch: decompose [skills: stdd-arch-*; writes: docs/plans/**; output: work_units.json; max_iter: 1]

    note over TW, Impl: Fan-out loop per work unit (max 2 parallel)
    loop all_tests_pass, max=20
        TW->>TW: write-failing-tests [skills: stdd-test-*; writes: test_*.py,tests/**; bash_scope: sandboxed_pytest; gate: pytest_shows_red]
        Impl->>Impl: implement-to-green [skills: stdd-impl-*; writes: src/**,lib/**; bash_scope: sandboxed_no_pip_git; gate: pytest_shows_green]
    end

    loop no_issues_found, max=1
        Rev->>Rev: adversarial-review [skills: review-*, general-git-*; no_write: true]
    end

    IntTest->>IntTest: integration-tests [skills: stdd-test-*; bash_scope: sandboxed_pytest; gate: all_tests_pass]
    Orc->>Orc: commit-and-pr [skills: general-git-*; writes: git_operations_only; gate: all_tests_pass]
```

### 4.2 Compiled YAML (hand-authored; compiler acceptance target)

```yaml
name: tdd-development
description: Test-driven development with parallel reviews and convergence gates.
runtime_min_version: "1.0"

agents:
  Orc:
    display_name: Orchestrator
  PM:
    display_name: Product Manager
  Arch:
    display_name: Architect
  Rev:
    display_name: Reviewer
  TW:
    display_name: Test Writer
  Impl:
    display_name: Implementer
  IntTest:
    display_name: Integration Tester

phases:
  - id: phase-1
    name: setup
    driver: Orc
    skills: [stdd-pm-*]
    constraints:
      write_access: none
    convergence:
      max_iterations: 1

  - id: phase-2
    name: fetch-issue
    driver: Orc
    worker: PM
    skills: [stdd-pm-*]
    constraints:
      write_access: [docs/tickets/**]
      external_apis: [linear]
    convergence:
      max_iterations: 1

  - id: phase-3
    name: parallel-design-review
    type: parallel_group
    phases:
      - id: phase-3a
        name: design-review
        driver: Rev
        skills: [review-*]
        constraints:
          write_access: none
        convergence:
          max_iterations: 3
          convergence_rule: same_findings_twice
      - id: phase-3b
        name: simplicity-review
        driver: Rev
        skills: [review-*]
        constraints:
          write_access: none
        convergence:
          max_iterations: 3
          convergence_rule: same_findings_twice

  - id: phase-4
    name: decompose
    driver: Arch
    skills: [stdd-arch-*]
    constraints:
      write_access: [docs/plans/**]
    output:
      artifact: work_units.json
    convergence:
      max_iterations: 1

  - id: phase-5
    name: test-first-loop
    type: convergence_loop
    annotation: "Fan-out loop per work unit (max 2 parallel)"
    convergence:
      max_iterations: 20
      convergence_rule: all_tests_pass
    phases:
      - id: phase-5a
        name: write-failing-tests
        driver: TW
        skills: [stdd-test-*]
        constraints:
          write_access: [test_*.py, tests/**]
          bash_scope: sandboxed_pytest
        output_gate:
          validation: pytest_shows_red

      - id: phase-5b
        name: implement-to-green
        driver: Impl
        skills: [stdd-impl-*]
        constraints:
          write_access: [src/**, lib/**]
          bash_scope: sandboxed_no_pip_git
        output_gate:
          validation: pytest_shows_green

  - id: phase-6
    name: adversarial-review
    type: convergence_loop
    convergence:
      max_iterations: 1
      convergence_rule: no_issues_found
    phases:
      - id: phase-6a
        name: adversarial-review
        driver: Rev
        skills: [review-*, general-git-*]
        constraints:
          write_access: none

  - id: phase-7
    name: integration-tests
    driver: IntTest
    skills: [stdd-test-*]
    constraints:
      bash_scope: sandboxed_pytest
    output_gate:
      validation: all_tests_pass

  - id: phase-8
    name: commit-and-pr
    driver: Orc
    skills: [general-git-*]
    constraints:
      write_access: git_operations_only
    output_gate:
      validation: all_tests_pass
```

### 4.3 Round-trip lossy fields (compiler must report, not silently drop)

The following fields from the requirements doc YAML cannot be recovered from the mermaid diagram and are either absent from the compiled output or reduced to defaults. The compiler's round-trip report must list them:

| Field | Present in req. YAML | In compiled YAML | Reason for loss |
|---|---|---|---|
| `phase.model` (e.g. `claude-opus`) | Yes, per phase | No (absent from mermaid) | Not in brackets; must be added to bracket metadata or authored directly in YAML |
| `concurrent_agents: 2` | Yes (phase 5) | No | Fan-out concurrency not representable in sequence notation; default = sequential within loop |
| `output_gate.file_pattern_check` | Yes | No | Not a supported bracket key in v1; captured as `phase.extensions` if present |
| `output_gate.coverage_threshold` | Yes | No | Same; captured as `phase.extensions` |
| `phase.agents.<worker>.model` | Yes (per-worker model) | No | Worker-level model not expressible in bracket metadata; requires YAML authoring |
| `phase.agents.<worker>.constraints` | Yes (per-worker) | No | Same |
| `gates.pre_commit / pre_push` | Yes (phase-8) | No | Gate sub-type not in v1 bracket keys; deferred |

---

## 5. Grammar BNF (compiler reference)

Minimal formal grammar for the parser in `mermaid_sequence.py`:

```
diagram       ::= "sequenceDiagram" NL statement*
statement     ::= participant | message | par_block | loop_block | note | ignored
participant   ::= ("participant" | "actor") ID ("as" TEXT)? NL
message       ::= ID "->>" ID ":" label NL
              |   ID "->" ID ":" label NL
              |   ID "-->" ID ":" label NL
              |   ID "-->>" ID ":" label NL
label         ::= TEXT ("[" metadata "]")?
metadata      ::= kv_pair (";" kv_pair)*
kv_pair       ::= KEY ":" VALUE
par_block     ::= "par" TEXT NL message ("and" NL message)* "end" NL
loop_block    ::= "loop" TEXT NL message* "end" NL
note          ::= "note over" ID ("," ID)* ":" TEXT NL
ignored       ::= ("activate" | "deactivate" | "autonumber" | "rect" | "end" ...) NL
```

The parser is line-oriented. Indentation is not significant. `ID` must match `[a-zA-Z][a-zA-Z0-9_-]*`. `TEXT` is any printable text not containing `[` or `]` (when part of a label before brackets).
