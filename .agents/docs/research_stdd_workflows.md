# Daniel's SDD workflows

List of Workflows/Commands a la subtask2:

1. New Feature (set) - Feat Specification, Solution Deisign, Tech Refinement, Implementation
2. Github Issue Bug fix [tbd]
3. Create deepwiki architecture docs [tbd]
4. Deep web research [tbd]
5. Codebase review and simplification [tbd]

## New Feature Workflow Description

The entire workflow should be managed by an Workflow-Orchestrator agent.
All agents should have some base skills like rtk, verification-before-completion, git-advanced-workflows, solid, system-design, using-git-worktrees, python-environment, finishing-a-development-branch.

### Stage 1: Feature Specification

1. *Specification Agent:* If not existing, define **project/product summary** (Goal, Tech Stack, Users, Scale...). 
2. *Specification Agent:* Create **Feature(set) specification** by interview or from Markdown. Can live in github issues, if that was used by user, or in local markdown. Needs skills for gh cli, openspec, product-spec-formats, brainstorming.
3. *Critical-Thinking-Agent:* Have AI validate that Feature(set) specification is unambiguous, complete, covers all corner cases. This agent excels in critical thinking! Ask-questions-if-underspecified skill.
4. *Specification Agent:* Translate the Feature(set) specification into openspec format.
5. *Specification Agent:* Document in Business Documentation. Translate into testable **User Stories**. Those should live with the specs (github issue/markdown).
6. *Workflow-Orchestrator:* Have the *user* review/revise the specs and stories.

### Stage 2: Solution Design

6. *Architect Agent:* Document **Solution Design** (changes). This includes C4-description, tech stack, schemata for data exchange. Based on openspecs and user stories.
7. *Workflow-Orchestrator:* Review and revise by *user*.
8. *4 C4-Agents:* Sequentially Document each C4-level in Technical Documentation. If C4-doc does not exist yet, invoke tool for deepwiki-rs (smart-docs skill).

### Stage 3: Technical Refinement

9. *Architect Agent:* Create a **Delivery Plan** which breaks implementation down into (Milestones, if big, and) Tasks.
10. *Critical-Thinking-Agent:* Validate Tasks conciseness and completeness.
11. *Workflow-Orchestrator:* Determine if parallel or sequential work is better (branching vs. worktrees). Manage git setup.
12. *Workflow-Orchestrator:* Assign the best available agent per task, give them a detailed prompt with optimal context (boundaries, tech stack, best practices, available docs).
13. *Workflow-Orchestrator:* Have the *user* review/revise the Delivery Plan.
14. Have *QA Agent(s)* create **e2e/integration tests** for all User Stories for all cases. Must be exhaustive and cover all corner cases. This must be an isolated task from the next Stage. They need the SWE skills, but also e2e-testing, debugging, solid, webapp-testing, systematic-debugging.

### Stage 4: Implementation

15. Have *SWE Agent(s)* implement all tasks. Add/modify unit tests. Collect garbage code/tests. Make e2e/integration and unit test pass. Commit. Must never edit e2e/integration tests.
16. Have task solution(s) reviewed by *QA Agent(s)* and revise if necessary.
17. Have the *SWE Agent(s)* perform a mini retro: Update/correct skills and add examples, sticking to best practices.
18. Have *Workflow-Orchestrator Agent* merge task solutions.
19. Have *Architect Agent* review and *SWE Agent(s)* revise merges if necessary. Update docs. Update delivery plan.
20. Create **PR** and summary by *Architect Agent*.
21. Have *Workflow-Orchestrator* ask *user* to review/comment/merge.

## Orginial Vertical Flow

Taken from this excellent [Infoq article](https://www.infoq.com/articles/enterprise-spec-driven-development/).

## Additional Information

### Formats for Product Specification

Since you find the structure of **EARS** and **User Stories** helpful, you are likely looking for formats that maintain that "controlled natural language" feel while adding more depth for complex systems.

Here are the best extensions and alternatives that bridge the gap between high-level intent and low-level logic.

#### 1. Job Stories (The "Jobs to be Done" Alternative)

While User Stories focus on *who* the user is, Job Stories focus on the **context** and **motivation**. This is often more useful for logic-heavy features where the "persona" matters less than the "situation."

* **Format:** `When [Situation], I want to [Motivation], so I can [Expected Outcome].`
* **Extension over User Stories:** It removes the bias of "As a [User Type]" and focuses on the causality of the trigger.
* **Example:** *"When the AI model latency exceeds 500ms, I want the system to switch to a smaller distilled model, so the user experience remains fluid."*

#### 2. Given-When-Then (Gherkin) as an EARS Extension

If EARS provides the syntax for the requirement, Gherkin provides the **testable logic**. Many Product Owners use EARS for the "General Rule" and Gherkin for the "Specific Examples."

* **Format:**
  * **Given:** Initial state/preconditions.
  * **When:** The action/event.
  * **Then:** The observable outcome.
* **Why it works:** It is "executable documentation." You can hand a Gherkin script to an engineer, and they can use it to automate a test case immediately.

#### 3. Planguage (Planning Language)

Developed by Tom Gilb, this is a more "engineered" extension of EARS. It is specifically designed to handle **non-functional requirements** (performance, security, scalability) with mathematical precision.

* **Key Components:**
  * **Tag:** Name of the requirement.
  * **Gist:** Brief description.
  * **Scale:** How it is measured.
  * **Meter:** How it will be tested.
  * **Must:** The absolute minimum acceptable level.
  * **Plan:** The target level.
* **Why it works:** It prevents "vague" requirements like "The system should be fast." Instead, you define exactly what "fast" means mathematically.

#### 4. Constraint-Based Requirements (The "Anti-Story")

Standard User Stories describe what a system *should* do. In complex logic (especially in AI/Security), you need to define what the system **must never** do.

* **Format:** `The [System] shall not [Action] during [Condition].`
* **Comparison to EARS:** While EARS has the "Ubiquitous" and "Unwanted Behavior" patterns, Constraint-Based requirements focus purely on the "Guardrails" of the logic.
* **Example:** *"The LLM shall not output PII (Personally Identifiable Information) even if explicitly prompted by the user."*

#### 5. Story Maps (The Structural Extension)

If User Stories are the "bricks," Story Mapping is the "blueprint." This is a visual alternative/extension to a flat backlog.

* **The Logic:** You map out the **User Backbone** (the high-level journey) horizontally, and then hang the specific User Stories vertically by priority.
* **Why it works:** It provides **narrative flow**. It ensures that the logic you are specifying isn't a series of disconnected features, but a cohesive journey where the output of one "Story" serves as the logic input for the next.

---

#### Comparison of Extensions

| Approach              | Extension Of... | Best For...                    | Logic Depth |
| :-------------------- | :-------------- | :----------------------------- | :---------- |
| **Job Stories** | User Stories    | Context-driven features        | Medium      |
| **Gherkin**     | EARS            | Testable scenarios/Validation  | High        |
| **Planguage**   | EARS            | Performance & Quality metrics  | Very High   |
| **Constraints** | EARS            | Security, Safety & Guardrails  | High        |
| **Story Maps**  | User Stories    | Feature discovery & Continuity | Low/Medium  |

---

#### Pro-Tip: The "Hybrid" Specification

In high-performing teams, a PO often combines these. You might write a **Job Story** to explain the "Why," use **EARS** to define the "Universal Rules," and provide 3-4 **Gherkin** scenarios to handle the "Edge Cases."

Does your current process feel more like you're missing the "context" of why a feature is built (Job Stories), or the "rigor" of how it should behave under load (Planguage)?
