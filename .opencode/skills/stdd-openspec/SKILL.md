---
name: stdd-openspec
description: Master the OpenSpec artifact-guided workflow for AI-assisted development. Use this skill when proposing, designing, or implementing new features.
---
# OpenSpec Skill

Master the OpenSpec artifact-guided workflow for AI-assisted development. Use this skill when proposing, designing, or implementing new features.

## Workflow Structure

Every feature or change must be isolated in its own directory: `openspec/changes/<change-name>/`.
This directory must contain the following artifacts:

1. **proposal.md**: Define the *Why* and the *What*.
2. **specs/**: Define the *Rules* and *Scenarios*.
3. **design.md**: Define the *How* (Technical Architecture).
4. **tasks.md**: The implementation checklist.

## Lifecycle Rules

1. **Iterate Before Coding**: Ensure the `proposal.md` and `specs/` are fully validated by the user before moving to `design.md` or `tasks.md`.
2. **Strict Adherence**: During implementation, code must strictly satisfy the criteria defined in the `specs/` directory and follow the checklist in `tasks.md`.
3. **No Ghost Features**: Do not implement features that are not explicitly documented in the OpenSpec artifacts.

## References & Examples

See [references/examples.md](references/examples.md) for concrete examples of OpenSpec artifacts.
