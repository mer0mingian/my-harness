---
name: stdd-project-summary
description: Define and maintain the project/product summary (Goal, Tech Stack, Users, Scale). Use when starting a new project or onboarding agents to ensure they have the correct business context.
---
# Project Summary Skill

Master the definition and maintenance of the core project identity. This skill ensures all agents working on the project understand the "Big Picture".

## Core Components

A complete project summary must define:

1. **Vision & Goal**: What is the primary purpose of the application? What problem does it solve?
2. **Tech Stack**: What are the core languages, frameworks, and tools used? (e.g., FastAPI, SQLAlchemy, uv).
3. **Target Users**: Who are the primary users? (e.g., Star Trek Adventures Game Masters).
4. **Scale & Performance**: What is the expected load or performance requirement? (e.g., Personal tabletop use, < 10 concurrent players per session).
5. **Core Constraints**: Any "hard" rules or architectural mandates (e.g., Surgical changes only, strictly read-only orchestrators).

## Workflow

1. **Discovery**: Interview the user or analyze the existing README/documentation.
2. **Drafting**: Create `@docs/business/product_summary.md` with the sections above.
3. **Refinement**: Ask the user to validate the vision and tech stack choices.
4. **Maintenance**: Update the summary whenever a major architectural or business goal shift occurs.

## References & Examples

See [references/examples.md](references/examples.md) for a template and a filled-out example.
