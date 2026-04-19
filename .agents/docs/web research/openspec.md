# OpenSpec Documentation

OpenSpec is an artifact-guided framework for AI-assisted development, designed to align human and AI intent before code is written. It creates a lightweight spec layer to ensure predictability and organization.

## Philosophy
- Fluid, not rigid
- Iterative, not waterfall
- Easy, not complex
- Built for both greenfield and brownfield projects

## Core Concepts & Artifacts

OpenSpec organizes each new feature or change into its own directory under `openspec/changes/`. When you propose a new feature, OpenSpec creates a structured set of artifacts:

1.  `proposal.md`: Explains *why* the change is being made and *what* is changing.
2.  `specs/`: Contains detailed requirements and scenarios (often user stories or Gherkin).
3.  `design.md`: Outlines the technical approach and architectural decisions.
4.  `tasks.md`: Provides an implementation checklist.

## Workflow

The standard OpenSpec workflow revolves around three main phases:

1.  **Propose (`/opsx:propose`)**: 
    - You provide an idea.
    - The AI generates the `proposal.md`, `specs/`, `design.md`, and `tasks.md`.
    - Human and AI iterate on these artifacts until aligned.
2.  **Apply (`/opsx:apply`)**: 
    - The AI implements the checklist defined in `tasks.md`.
    - Code is written and verified against the specs.
3.  **Archive (`/opsx:archive`)**: 
    - Once the feature is complete and merged, the change directory is moved to an archive (e.g., `openspec/changes/archive/`).
    - The main system specs are updated.

## Integration with Daniel's SDD Workflow

In Daniel's Spec-Driven Development (SDD) Workflow, OpenSpec serves as the structural foundation for **Stage 1 (Feature Specification)** and **Stage 2 (Solution Design)**. 
- The `daniels-spec-agent` will utilize the OpenSpec format to generate the proposal and specs.
- The `daniels-design-agent` will contribute to the `design.md` and `tasks.md`.
- This ensures all artifacts are standardized and easily readable by the `daniels-impl-agent` during the execution phase.
