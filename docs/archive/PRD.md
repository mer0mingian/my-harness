# Product Requirements Document (PRD)

## 1. Product Overview

A specialized marketplace for OpenSpecs-compliant agents that allows teams to install a high-performance, 4-phase software engineering workflow.

## 2. Functional Requirements

### FR1: Selective Installation

* Users MUST be able to install individual phases independently (e.g., `plugin install discovery@openspecs`).
* The marketplace MUST support a "Core" installation that includes shared skills.

### FR2: Subagent Isolation

* Agents in the `Discovery` phase MUST NOT have visibility into `Implementation` skills.
* Instructions for the `Architect` in Phase 1 MUST be distinct and isolated from the `Architect` in Phase 2 to prevent system prompt pollution.

### FR3: Naming & Namespace

* All skill directories MUST follow the pattern: `[phase_prefix]-[agent_role]-[skill_name]`.
* Shared skills MUST use the `general-` prefix.

### FR4: Command-Driven Invocation

* Each plugin MUST register specific slash-commands (e.g., `/refine`) that act as entry points for the subagents.

## 3. Technical Constraints

* **Compatibility:** Must support both `claude` (Anthropic) and `opencode` (Open Source) CLI environments.
* **Context Management:** Subagents must be configured with a "Maximum Tool Count" (suggested < 5 per agent) to ensure high reliability.
* **Persistence:** Artifacts must be written to the local filesystem in a standardized directory (e.g., `./.openspecs/artifacts/`) to allow state recovery.

## 4. User Workflow (Example)

1. **Setup:** `plugin marketplace add my-team-repo`
2. **Install:** `plugin install 01-discovery`
3. **Execute:** User types `/discovery "I want to build a payment gateway"`.
4. **Process:** Claude Code identifies the command, loads the `01-discovery` plugin, spawns the `disc-arch` subagent, and grants it access ONLY to `disc-arch-analyzer` and `general-file-manager`.
5. **Output:** Subagent creates `/.openspecs/artifacts/discovery.md`.

## 5. Success Metrics

* **Instruction Clarity:** 0% cross-contamination between Phase 1 and Phase 2 agent instructions.
* **Token Efficiency:** 30-50% reduction in system prompt size compared to a monolithic agent approach.
* **Extensibility:** Ability for a developer to add a 5th phase (e.g., `05-testing`) by creating a new folder and updating `marketplace.json`.
