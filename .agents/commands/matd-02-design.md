---
description: "Stage 2: Solution Design"
agent: matd-orchestrator
subtask: true
return:
  # 1. Architect drafts the technical blueprint
  - /subtask {agent: matd-architect && as: design_draft} Based on specs from Stage 1, create `openspec/changes/<slug>/design.md` with C4 descriptions, data schemata, and API modifications.
  
  # 2. Sequential C4 Documentation Updates (all via matd-architect with level-specific instructions)
  - /subtask {agent: matd-architect && as: c4_context} Create C4 Context diagram focusing ONLY on system boundary and external actors. Use arch-c4-architecture skill with references/c4-level-context.md guidance. Show: user personas, external systems, system boundaries. Exclude: internal structure, technology choices, deployment details.
  
  - /subtask {agent: matd-architect && as: c4_container} Create C4 Container diagram focusing ONLY on high-level containers. Use arch-c4-architecture skill with references/c4-level-container.md guidance. Show: deployable units, databases, technology stack, inter-container communication. Exclude: internal components, code-level details, infrastructure nodes.
  
  - /subtask {agent: matd-architect && as: c4_component} Create C4 Component diagram focusing ONLY on internal components. Use arch-c4-architecture skill with references/c4-level-component.md guidance. Show: logical groupings, component interfaces, internal dependencies. Exclude: class details, deployment info, external systems.
  
  - /subtask {agent: matd-architect && as: c4_code} Create C4 Code diagram ONLY IF complexity warrants detailed documentation. Use arch-c4-architecture skill with references/c4-level-code.md guidance. Show: class hierarchies, database schemas, sequence diagrams for key flows. If not needed, document why this level was skipped.
  
  # 3. Technical Docs Sync
  - /subtask {agent: matd-architect} Sync the technical design with the project Deepwiki using the `arch-smart-docs` skill.
  
  # 4. User approval gate
  - "Stage 2 (Solution Design) complete. Architectural blueprint and C4 diagrams have been updated in the OpenSpec folder and Deepwiki. Please review. Reply with 'Approved' to move to Stage 3 (Technical Refinement)."
---
# Solution Design Phase

Initiating technical blueprinting. I will coordinate the Architect to define the "How" and update all architectural documentation using progressive C4 disclosure (Context → Container → Component → Code as needed).
