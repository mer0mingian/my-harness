# Phase 3 Gap Learnings

**Date:** 2026-05-08  
**Purpose:** Document responses to architectural gaps identified during Phase 3 planning

---

## G1: Command Naming and Sequencing

**Issue:** /plan command name misleading - doesn't just plan, it discovers requirements.

**Resolution:**
- Rename: `/speckit.multi-agent.plan` → `/speckit.multi-agent.discover`
- Purpose: Generate PRD and Technical Constitution via grill-me questioning
- Sequence: /discover runs BEFORE /solution-design
- Standalone: /solution-design CAN run without /discover, but warns about spec drift risk
- Rationale: Discovery establishes user motivation and logic; solution design without it risks misalignment

**Impact on Documentation:**
- Update all references from "plan" to "discover"
- Workflow sequence: discover → solution-design → test → implement → review → commit
- Warning message: "Running /solution-design without /discover increases spec drift risk"

---

## G2: ADR Template Structure

**Research:** [ADR Best Practices](https://github.com/joelparkerhenderson/architecture-decision-record)

**Template Requirements:**
- **Format:** Markdown, compact (2 pages max)
- **Structure:** Context → Decision → Consequences (Nygard pattern)
- **Solution Count:** Default 3 alternatives, user-modifiable
- **C4 Integration:** Include C4 Context + Container diagrams for EACH alternative (enables visual comparison of approaches)
- **Evaluation Logic:** Consistent framework to discover, categorize, evaluate, weight pros/cons
- **Sections:**
  1. Title and metadata
  2. Status (proposed/accepted/superseded)
  3. Context and problem statement
  4. Decision criteria and constraints
  5. Solution Alternative 1 (description + C4 Context + C4 Container diagrams)
  6. Solution Alternative 2 (description + C4 Context + C4 Container diagrams)
  7. Solution Alternative 3 (description + C4 Context + C4 Container diagrams)
  8. Comparison matrix (pros/cons weighted across criteria)
  9. Decision and rationale (chosen alternative)
  10. Consequences and implications

**Note:** ADR focuses on high-level comparison (Context/Container). Detailed architecture (Component/Code levels) goes in separate Solution Design artifact.

**Sources:**
- [GitHub ADR Repository](https://github.com/joelparkerhenderson/architecture-decision-record)
- [Microsoft Azure ADR Guide](https://learn.microsoft.com/en-us/azure/well-architected/architect-role/architecture-decision-record)
- [AWS ADR Best Practices](https://aws.amazon.com/blogs/architecture/master-architecture-decision-records-adrs-best-practices-for-effective-decision-making/)

---

## G3: Claude Code Subagent Invocation & Skills

**Research:** [Claude Code Subagents Guide](https://code.claude.com/docs/en/sub-agents)

**Invocation Methods:**
1. **Explicit:** `/agent <agent-name>` or "Use @agent-name to..."
2. **Natural language:** "Invoke the c4-context agent with..."
3. **From markdown:** Instruct in command body: "Delegate to @c4-context with context: [...]"

**YAML Frontmatter for Tool and Skill Access:**
```yaml
---
name: solution-design
description: "Create ADR and Solution Design with C4 architecture diagrams"
agents:
  - c4-context
  - c4-container
  - c4-component
  - c4-code
skills:
  - 'arch-mermaid-diagrams'      # Mermaid syntax for all diagram types
  - 'arch-c4-architecture'       # C4 model documentation patterns
  - 'arch-smart-docs'            # Codebase architecture analysis
  - 'general-grill-with-docs'    # Domain-aware questioning, updates CONTEXT.md
tools:
  - Read
  - Write
  - Glob
  - Bash(tree:*, find:*, grep:*)
---
```

**Skill Rationale:**
- **arch-mermaid-diagrams:** Provides comprehensive mermaid syntax reference for C4Context, C4Container, C4Component, sequenceDiagram, classDiagram, flowchart
- **arch-c4-architecture:** Guides C4 model workflow (Context→Container→Component→Deployment), includes examples and best practices
- **arch-smart-docs:** Enables codebase analysis to inform architecture diagrams (pattern recognition, dependency mapping)
- **general-grill-with-docs:** For /discover command - grills user with domain awareness, updates CONTEXT.md and ADRs inline

**Tools for Architecture Agents:**
- **Read/Write:** Read PRD/Constitution/codebase, write diagram files
- **Glob:** Find relevant code files to analyze structure
- **Bash(tree/find/grep):** Explore project structure, detect patterns

**Subagent Prompt Pattern:**
```markdown
## Step 3: Generate C4 Context Diagram

Invoke @c4-context agent with arch-c4-architecture and arch-mermaid-diagrams skills:

**Context:**
- PRD: ${prd_content}
- Technical Constitution: ${constitution_content}
- Feature: ${feature_id}
- Codebase: (agent can Glob/Read to analyze)

**Task:**
Generate C4 Context diagram showing:
- System boundary
- External actors (users, systems)
- High-level interactions

**Output:**
Create: docs/architecture/${feature_id}-c4-context.md
Format: Narrative + mermaid C4Context diagram
Skills: Use arch-c4-architecture for workflow, arch-mermaid-diagrams for syntax
```

**Sources:**
- [Create Custom Subagents](https://code.claude.com/docs/en/sub-agents)
- [Claude Code Subagents Guide](https://medium.com/@sathishkraju/claude-code-subagents-the-complete-guide-to-ai-agent-delegation-d0a9aba419d0)

---

## G4: Artifact Flow Understanding (CONFIRMED VIA DIAGRAM)

**Diagram Source:** `Agentic Engineering Workflow.png`

### PRD Must-Have Sections (Discovery Panel)
- What & Why
- Business Value
- Measurability
- Goals & No-goals
- Risks & Stories
- Dependencies
- People
- Metrics

### System Constitution Must-Have Sections (Discovery Panel)
- Tech Radar
- Team Tech Skills
- Compliance & Governance
- NFRs: Testing Strategy, Performance, Scalability, Reliability

### Solution Design Output (Solution Design Panel)
- ADR (approved solution)
- **C2/C3 Views** (Container + Component levels — NOT C1 Context or C4 Code)
- Diagrams
- Data Flow

### Refinement Inputs (Refinement Panel)
- C2/C3 Views + Diagrams, data flow (from Solution Design)
- Consolidate internal interfaces
- Testing Strategy (derived here, not in implementation)
- → Produces: vertical slices (Epic, Story, Task)

### PRD ↔ Spec Relationship
- PRD = upstream context (What & Why, business motivation, Job-to-be-Done)
- Spec = SpecKit technical specification (acceptance criteria, user stories format)
- PRD does NOT contain user stories — these are derived as Epics during Refinement
- Both are inputs to Solution Design

## G4: Artifact Flow Understanding (CORRECTED)

**Workflow.svg Analysis:**
- Discovery Panel contains: PRD, Technical Constitution (confirmed via grep)
- Solution Design phase creates: ADR, Solution Design artifact
- Phase flow: Discovery → Solution → Implementation → Review → Commit

**Key Correction:**
- **ADR** includes only C4 Context/Container levels (high-level comparison)
- **Solution Design** is a NEW artifact type containing 4 detailed views

**Artifact Influence Chain:**

```
/discover (Slice 7a)
├── PRD (Product Requirements Document)
│   ├── User stories, acceptance criteria
│   └── Success metrics, constraints
│
└── Technical Constitution
    ├── Non-functional requirements (performance, scalability, security)
    ├── Technology constraints (Python 3.11, PostgreSQL)
    └── Design principles (microservices, event-driven)

/solution-design (Slice 7b)
├── ADR (Architecture Decision Record)
│   ├── Input: PRD (problem), Tech Constitution (constraints)
│   ├── Compares: 3 solution approaches
│   ├── Includes: C4 Context + Container diagrams for EACH approach
│   └── Output: Chosen solution with rationale
│
└── Solution Design Artifact (NEW - detailed architecture)
    ├── Decomposition View
    │   ├── C4 Context diagram (system + external actors)
    │   ├── C4 Container diagram (apps, databases, services)
    │   ├── C4 Component diagram (internal structure)
    │   └── C4 Code diagram (class/module relationships)
    │
    ├── Dependency View
    │   ├── Component coupling analysis
    │   ├── Dependency graph (internal + external)
    │   └── Circular dependency detection
    │
    ├── Interface View
    │   ├── External API contracts (OpenAPI, gRPC)
    │   ├── Internal interface definitions
    │   └── Event schemas (if event-driven)
    │
    └── Data Design View
        ├── Entity-relationship diagrams
        ├── Database schemas
        ├── Data flow diagrams
        └── State machine diagrams (if applicable)
```

**Flow Summary:**
1. **PRD** defines WHAT (user stories, acceptance criteria)
2. **Technical Constitution** defines HOW (constraints, tech choices, principles)
3. **ADR** compares 3 solution approaches with C4 Context/Container for each → user chooses one
4. **Solution Design** elaborates chosen solution with 4 detailed views (all 4 C4 levels + dependencies + interfaces + data)
5. Implementation phases use Solution Design as blueprint

**Artifact Files Created:**
- `/discover`: `${feature_id}-prd.md`, `technical-constitution.md` (or update existing)
- `/solution-design`:
  - `${feature_id}-adr.md` (includes 3 approaches with Context/Container diagrams)
  - `${feature_id}-solution-design.md` (contains all 4 views with detailed diagrams)

---

## G5: Config Template Implementation Gaps

**Current Template Coverage (harness-tdd-config.yml.template):**
- ✅ Agent assignments (lines 8-13)
- ✅ Artifact paths and types (lines 16-41)
- ✅ Quality gates (lines 45-52)
- ✅ Planning config with grill-me (lines 54-60)
- ✅ Test framework config (lines 63-86)
- ✅ Workflow execution (lines 89-97)
- ✅ Local Jira structure (lines 100-107)
- ✅ Logging (lines 110-116)

**Missing Implementations:**
1. **Parallel execution** (line 93: `parallel_enabled: false`)
   - TODO: Implement parallel agent dispatch for /review command
   - Requires: Agent orchestration logic to spawn @arch-specialist + @review-specialist concurrently
   
2. **Agent timeout enforcement** (line 95: `agent_timeout: 30`)
   - TODO: Add timeout wrapper in helper scripts that spawn subagents
   - Mechanism: subprocess.run(..., timeout=config.agent_timeout * 60)
   
3. **Artifact validation against templates** (line 97: `validate_artifacts: true`)
   - TODO: Create script/validate_artifact_structure.py
   - Logic: Parse template YAML frontmatter, validate output has required sections
   
4. **Convergence detection** (line 52: `convergence_detection: true`)
   - TODO: Implement in /review command cycle logic
   - Algorithm: Hash review findings, detect if N consecutive cycles produce identical output
   
5. **Local Jira auto-creation** (line 107: `auto_create_stories: true`)
   - TODO: Enhance lib/jira_local.py with auto-folder creation
   - Trigger: When /commit runs, create .specify/epics/${epic_id}/${story_id}.md if missing

**Suggested Slice 8 Scope:**
- Implement missing config features above (5 items)
- Add config validation script (ensure .specify/harness-tdd-config.yml is valid)
- Document config options in docs/CONFIG-GUIDE.md
- Create config migration script for version updates

---

## G6: Story Point Estimation

**Research:** [Atlassian Story Points Guide](https://www.atlassian.com/agile/project-management/estimation)

**Definition:**
Story points estimate COMPLEXITY, RISK, and EFFORT combined, not hours. Relative estimation technique used in Agile.

**Measurement Factors:**
- Volume of work (how much to do)
- Complexity (how hard)
- Risk/uncertainty (how much unknown)

**Empirically Valid Technique:**
**Planning Poker** - Team-based estimation using Fibonacci sequence (1, 2, 3, 5, 8, 13, 21)
- Each member estimates independently
- Discuss outliers
- Converge to consensus
- Proven to reduce bias, improve forecasting

**Coding Agent Skill:**
No existing skill found for automated story point estimation. Human judgment required.

**Proposed Calibration:**
- 1 point: Trivial (update documentation, simple config change)
- 2 points: Simple (create template file, straightforward script)
- 3 points: Moderate (convert Python command to markdown, research and summarize)
- 5 points: Complex (implement command with multiple scripts, integrate new library)
- 8 points: Very complex (multi-agent orchestration, new architectural pattern)
- 13 points: Highly complex (full workflow implementation, extensive integration)

**Sources:**
- [Atlassian Story Points](https://www.atlassian.com/agile/project-management/estimation)
- [Scrum.org Why Story Points](https://www.scrum.org/resources/blog/why-do-we-use-story-points-estimating)
- [Story Points Complexity](https://www.eficode.com/blog/why-story-points-are-a-measure-of-complexity-not-effort)

**Recommendation for Phase 3:**
Use Planning Poker approach with user during grilling phase to calibrate estimates.

---

## Summary

**Key Decisions:**
1. **Command renamed:** /plan → /discover (generates PRD + Technical Constitution)
2. **ADR template:** 2-page Nygard pattern, 3 solutions default, includes C4 Context/Container for EACH approach
3. **Solution Design artifact (NEW):** Separate document with 4 views:
   - Decomposition View (all 4 C4 levels: Context, Container, Component, Code)
   - Dependency View (coupling analysis, dependency graphs)
   - Interface View (API contracts, event schemas)
   - Data Design View (ERD, schemas, data flow diagrams)
4. **Subagent skills:** arch-mermaid-diagrams, arch-c4-architecture, arch-smart-docs, general-grill-with-docs
5. **Artifact flow:** PRD + Tech Constitution (from /discover) → ADR compares 3 approaches → Solution Design elaborates chosen approach
6. **Slice 8:** Implement 5 missing config features + validation + docs
7. **Story points:** Planning Poker, Fibonacci scale, manual calibration

**Artifacts Created by Phase 3:**
- `/discover`: `${feature_id}-prd.md`, `technical-constitution.md`
- `/solution-design`: `${feature_id}-adr.md`, `${feature_id}-solution-design.md`

**Next Steps:**
1. ✅ Write refined grilling questions (PHASE3-GRILLING-QUESTIONS.md)
2. Update roadmap with /discover rename and story point estimates
3. Create ADR template (includes C4 Context/Container comparison)
4. Create Solution Design template (with 4 views)
5. Define /discover and /solution-design commands
