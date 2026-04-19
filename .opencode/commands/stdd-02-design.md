---
description: "Stage 2: Solution Design"
agent: daniels-workflow-orchestrator
subtask: true
return:
  # 1. Architect drafts the technical blueprint
  - /subtask {agent: daniels-architect-agent && as: design_draft} Based on specs from Stage 1, create `openspec/changes/<slug>/design.md` with C4 descriptions, data schemata, and API modifications.
  
  # 2. Sequential C4 Documentation Updates
  - /subtask {agent: c4-context} Update Level 1 System Context diagrams.
  - /subtask {agent: c4-container} Update Level 2 Container diagrams.
  - /subtask {agent: c4-component} Update Level 3 Component diagrams.
  
  # 3. Technical Docs Sync
  - /subtask {agent: daniels-architect-agent} Sync the technical design with the project Deepwiki using the `smart-docs` skill.
  
  # 4. User approval gate
  - "Stage 2 (Solution Design) complete. Architectural blueprint and C4 diagrams have been updated in the OpenSpec folder and Deepwiki. Please review. Reply with 'Approved' to move to Stage 3 (Technical Refinement)."
---
# Solution Design Phase

Initiating technical blueprinting. I will coordinate the Architect and C4 agents to define the "How" and update all architectural documentation.
