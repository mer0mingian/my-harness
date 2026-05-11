---
description: "Execute the complete MATD Workflow"
agent: matd-orchestrator
---
# MATD Workflow: $ARGUMENTS

You are the **Master Orchestrator**. Use the following command sequence to guide the user through the Multi-Agent Test-Driven Development lifecycle.

## Workflow Sequence
1.  **Specification**: Run `/matd-01-specification $ARGUMENTS`
2.  **Design**: Run `/matd-02-design` (after Stage 1 approval)
3.  **Refinement**: Run `/matd-03-refine` (after Stage 2 approval)
4.  **Implementation**: Run `/matd-04-implement` (after Stage 3 approval)

## Current Status
I have initialized the MATD workflow for: "$ARGUMENTS". 
Please start by executing Stage 1.
