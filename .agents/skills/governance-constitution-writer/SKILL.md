---
name: governance-constitution-writer
description: Generate or amend TECHNICAL_CONSTITUTION.md from interview output and
  repo signals. Enforces RFC-2119 keywords, required sections, and rationale
  capture. Use when @governance-constitution-author needs to author or update the
  constitution.
---
# Governance Constitution Writer

Templates and rules for producing `docs/governance/TECHNICAL_CONSTITUTION.md`.

## When to use

- Authoring a new constitution from interview output.
- Amending an existing constitution (preserve approved sections, mark new ones).
- Validating a hand-written constitution against the schema.

## Required sections (in order)

1. **Header**: project name, version, last updated date, governance rule.
2. **1. Technology Preferences**: Backend, Frontend, Testing, Infrastructure
   subsections. Each subsection lists tools/versions with one-line rationale.
3. **2. Solution Approach Constraints**: Architecture patterns, API design,
   data access, error handling. Use `MUST`/`MUST NOT`/`SHOULD` (RFC-2119).
4. **3. Code Quality Standards**: Naming conventions, documentation rules,
   linter/formatter/type-checker config.
5. **4. Security Baseline**: AuthN/AuthZ, data protection, dependency
   management.
6. **5. Amendment Process**: minor vs major, approval requirements.
7. **Appendix: Tooling Reference**: table of tool, version, config file.

## RFC-2119 discipline

- `MUST` / `MUST NOT`: hard rules. Violation blocks merge.
- `SHOULD` / `SHOULD NOT`: strong default. Violation requires written rationale.
- `MAY` / `OPTIONAL`: explicit opt-in. Default off.

Every `MUST`/`MUST NOT` line needs a rationale or a link to an ADR. If the user
gave no rationale, write `Rationale: TBD — pending architect input` rather than
inventing one.

## Source mapping

Map interview blocks to constitution sections:

| Interview block          | Constitution section                    |
| ------------------------ | --------------------------------------- |
| Block 2 (tech stack)     | 1. Technology Preferences               |
| Block 3 (solution)       | 2. Solution Approach Constraints        |
| Block 4 (security)       | 4. Security Baseline                    |
| Repo signals (linter)    | 3. Code Quality Standards               |

## Authoring workflow

1. Load template `.agents/templates/governance/TECHNICAL_CONSTITUTION.template.md`.
2. Substitute project metadata.
3. Fill section 1 from `tech_stack` map (omit subsections with no input —
   never invent placeholder tools).
4. Fill section 2 from `solution` map. Convert each `true` to a `MUST`, each
   `false` to a `MUST NOT`, each "depends" to a `SHOULD`.
5. Fill section 4 from `security` map.
6. Pull section 3 defaults from repo signals (`pyproject.toml`,
   `package.json`, `.editorconfig`).
7. Run schema check (see `governance-validate-artifacts` skill).

## Amendment mode

When the file already exists:

- Diff existing sections against new interview output.
- Preserve any line tagged `<!-- approved: YYYY-MM-DD -->` unchanged.
- Add new lines under `## Pending Amendments` for human review.
- Bump version (semver: minor for new section, patch for clarification).

## Output checklist

- [ ] All seven required sections present and populated.
- [ ] Every `MUST`/`MUST NOT` has rationale or `TBD` marker.
- [ ] Header version, date, governance line filled.
- [ ] Appendix tooling table at least lists language + dep manager + linter +
      type checker + test runner.
- [ ] File validates against `constitution.schema.json`.
