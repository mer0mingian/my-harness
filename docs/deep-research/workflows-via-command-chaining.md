
# Technical Report: Orchestration and Implementation of Multi-Agent Workflows

This document summarizes the architectural decisions, tool comparisons, and concrete implementation steps for building sequential, multi-stage AI agent pipelines. The focus lies on initial visual modeling and subsequent native execution in agentic development environments (**OpenCode** and  **Claude Code** ).

---

## 1. Visual Modeling and Code Extraction

For the definition of agents, their roles, and the assignment of tools (including MCP servers), visual open-source frameworks are utilized. The goal is to export these definitions as "Open Code" (JSON/YAML).

### Evaluated Frameworks

1. **LangFlow:** The recommended standard for code-centric integration. Based on LangChain. It exports detailed JSON files that have a 1:1 correspondence to Python classes and can be loaded programmatically.
2. **Dify:** Offers a clean, YAML-based Domain Specific Language (DSL). Excellent for human readability and "Infrastructure-as-Code" approaches, though it requires more overhead for native Python execution compared to LangFlow.
3. **Flowise:** JSON-based, primarily focused on Node.js/JavaScript and rapid API deployments.

| **Feature**            | **LangFlow**        | **Dify**             | **Flowise**  |
| ---------------------------- | ------------------------- | -------------------------- | ------------------ |
| **Focus**              | Scientific/Complex        | Enterprise Agent Ops       | Rapid Prototyping  |
| **Export Format**      | JSON                      | YAML                       | JSON               |
| **Code Integrability** | High (via Python Library) | Medium (via API/Self-Host) | High (via API/SDK) |

**Decision:** **LangFlow** is preferred for the graphic design phase and seamless transition into code artifacts.

---

## 2. Integration into OpenCode: Architecture and Scoping

Since OpenCode operates text-based, the visual LangFlow logic is integrated as a "Skill" (Tool) via an orchestration script.

### 2.1 Directory Structure (Scoping)

To prevent the global manager agent from being distracted by workflow-specific specialists, the file system is used as a namespace:

**Plaintext**

```
.opencode/
└── agents/
    ├── manager.md               # Central Orchestrator
    └── dev_workflow/            # Encapsulated Workflow
        ├── architect.md
        ├── coder.md
        ├── reviewer.md
        └── tester.md
└── tools/
    ├── common/                  # Global Tools
    └── dev_workflow_tools/      # Workflow-specific Skills
```

### 2.2 The Orchestration Skill (Python)

A central script (`.opencode/tools/trigger_dev_pipeline.py`) acts as a self-documenting tool. It is called by the manager agent and controls the sub-agents:

**Python**

```
import opencode_sdk

def trigger_dev_pipeline(feature_name: str, complexity: str = "medium"):
    """
    Starts a specialized 4-agent chain.
    Args:
        feature_name (str): Name of the feature.
        complexity (str): Depth of detail ('low', 'medium', 'high').
    """
    architect = opencode_sdk.get_agent("dev_workflow/architect")
    design_doc = architect.run(input=feature_name, tools=["file_search"])

    coder = opencode_sdk.get_agent("dev_workflow/coder")
    code_result = coder.run(input=design_doc, tools=["python_executor"])

    return f"Pipeline completed for {feature_name}."
```

### 2.3 Deterministic Workflows in OpenCode (subtask2)

To prevent OpenCode from solving complex tasks in an unstructured chat history, the `subtask2` plugin is employed. It enforces isolated contexts and the sequential passing of variables (via `$RESULT`).

**Installation from the Debug Branch:**

The `.opencode.json` must use the GitHub reference syntax to load specific commits:

**JSON**

```
{
  "plugins": [
    "github:spoons-and-mirrors/subtask2#debug"
  ]
}
```

---

## 3. Paradigm Comparison: OpenCode vs. Claude Code

The nature of task orchestration differs fundamentally between the platforms:

| **Aspect**          | **OpenCode (with subtask2)** | **Claude Code (Native)**              |
| ------------------------- | ---------------------------------- | ------------------------------------------- |
| **Philosophy**      | Explicit, plugin-driven pipeline.  | Implicit, prompt-driven delegation.         |
| **Delegation**      | Hardcoded chaining (Step 1 -> 2).  | Autonomous creation of ephemeral sub-tasks. |
| **Context Passing** | Specific variables and scripts.    | The file system (Repo) as Shared Memory.    |
| **Strictness**      | Enforced by plugin syntax.         | Enforced by the orchestrator prompt.        |

---

## 4. Native Implementation in Claude Code ("Daniel's Feat Dev Workflow")

Claude Code requires no external plugins for this architecture. Control is handled entirely through Markdown files in the `.claude/agents/` directory.

### 4.1 Agent Definitions

**The Orchestrator (`manager.md`):**

**Markdown**

```
# Role: Feature Development Orchestrator
Steer the "Daniel's Feat Dev Workflow" sequentially.

1. **Design:** Trigger `Agent("Architect")` -> Output: `docs/design.md`.
2. **Implementation:** Trigger `Agent("Engineer")` -> Input: `docs/design.md`.
3. **Review:** Trigger `Agent("Reviewer")`. If criticized: Return to Step 2.
4. **Validation:** Trigger `Agent("Tester")`.
5. **Reflection:** Only after success of Step 4: Command the Engineer to perform the skill update.
```

**The Sub-Agent (`engineer.md`) with Reflective Behavior:**

**Markdown**

```
# Role: Lead Engineer
Implement features. Tools: `write_file`, `edit_file`, `python_executor`.

## Learning Protocol (POST-APPROVAL):
Execute this ONLY if the Manager has confirmed validation:
1. Read your own session history (`tool_use` logs).
2. Filter: Identify successful solution paths. Ignore approaches rejected by the Manager.
3. Use `edit_file` to correct inaccuracies in your `.claude/tools/` descriptions based on the successful attempts.
```

### 4.2 Scenario Execution: Failed E2E-Framework & Self-Healing

The system handles errors and subsequent learning (reflection) through strict context separation and status releases:

1. **Failed Attempt:** The Engineer installs a framework with too many dependencies in its isolated sub-task session.
2. **Intervention:** The Orchestrator (Manager) rejects this during the review phase and orders a rollback. This attempt is marked as "rejected" in the Engineer's session history.
3. **Success through Trial & Error:** The Engineer builds a custom solution, undergoes several failed trials within its session, and finally presents a functioning version.
4. **Validation & Approval:** The Tester confirms the functionality; the Manager grants final approval.
5. **Post-Execution Reflection:** The Manager now triggers the Engineer’s learning process.
6. **Selective Skill Update:** The Engineer reads its logs. It ignores the initial framework (as it was rejected) and the intermediate errors of the custom solution. It extracts only the functioning parameters of the custom solution and updates its own skill descriptions in the repository (via `edit_file`).

### Conclusion

The native architecture in Claude Code enables complex, self-healing workflows without external scripts. Strict sequencing and filtered learning are ensured by the combination of file system context, session isolation, and precise prompting within the orchestrator agent.
