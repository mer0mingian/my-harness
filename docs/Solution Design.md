# Part 1: Solution Design (SD)

## 1. System Architecture

The system follows a **Hierarchical Plugin Architecture**. A central "Marketplace" repository hosts multiple independent plugins (one for each of the 4 OpenSpecs phases).

### 1.1 Orchestration Model

* **The Main Agent:** Claude Code (or OpenCode) remains the primary interface.
* **Subagent Spawning:** When a user executes a phase command (e.g., `/discovery`), the Main Agent initializes a "Phase Session." It invokes the specific subagent defined in that phase's plugin.
* **Scope Isolation:** By using the Plugin Manifest (`plugin.json`), we restrict the available tools (skills) and instructions to only those registered within that specific plugin directory.

### 1.2 Repository Structure

The repository is structured as a **Monorepo with a Symlink Registry** to handle shared skills without code duplication.

```text
openspecs-framework/
├── .claude-plugin/
│   └── marketplace.json            # Registry for selective installation
│
├── core-skills/                    # Source of truth for shared skills
│   ├── general-file-manager/
│   │   └── SKILL.md
│   └── general-git-client/
│       └── SKILL.md
│
├── plugins/
│   ├── 01-discovery/
│   │   ├── .claude-plugin/
│   │   │   └── plugin.json         # Registers commands: /discovery, /disc-arch
│   │   ├── agents/
│   │   │   └── arch.agent.md       # "Discovery Architect"
│   │   └── skills/
│   │       ├── disc-arch-analyzer/ # Phase-specific skill
│   │       │   └── SKILL.md
│   │       └── general-file-manager -> ../../../core-skills/general-file-manager # SYMLINK
│   │
│   ├── 02-solution-design/
│   │   ├── .claude-plugin/
│   │   │   └── plugin.json         # Registers commands: /design, /sol-arch
│   │   ├── agents/
│   │   │   └── arch.agent.md       # "Solution Design Architect"
│   │   └── skills/
│   │       ├── sol-arch-db-spec/
│   │       │   └── SKILL.md
│   │       └── general-file-manager -> ../../../core-skills/general-file-manager # SYMLINK
│   │
│   ├── 03-refinement/
│   └── 04-implementation/
│
└── shared-docs/
    └── artifact-schemas/           # Path and Schema definitions for data exchange
```

### 1.3 Skill Management & Symlinking

* **Local Skills:** Unique skills reside directly in the `plugins/[phase]/skills/` folder. They follow the `[phase]-[agent]-[skill]` naming convention.
* **Shared Skills:** To maintain compatibility with both Claude Code and OpenCode, shared skills are stored in `core-skills/`.
* **Symlink Strategy:** During development/deployment, shared skills are symlinked into the `skills/` folder of individual plugins. This ensures that the Agent Plugin Standard sees them as "local" to that plugin, granting the subagent access, while keeping the marketplace logic clean.

### 1.4 Data Exchange (The Artifact Pipeline)

Communication between phases is **asynchronous and artifact-based**:

1. **Phase 1** generates an artifact (e.g., `discovery-spec.md`) at a path defined by the Orchestrator.
2. **Phase 2** subagent is spawned. The Orchestrator provides the path to the Phase 1 artifact as part of the subagent's initialization prompt.
3. **Cross-talk:** If "brainstorming" is required, the Orchestrator passes a JSON-wrapped summary of Subagent A's output to Subagent B's tool input.

---
