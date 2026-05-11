# C4 Architecture Improvement Proposal

**Status:** Awaiting Review  
**Created:** 2026-05-08  
**Related:** MATD Plugin (M2 complete)

---

## Problem

Current approach uses 4 separate C4 specialist agents (`matd-c4-context`, `matd-c4-container`, `matd-c4-component`, `matd-c4-code`) that the architect delegates to. This creates:
- Redundant agent definitions (each is specialized wrapper around the same architect)
- Complex delegation chains (orchestrator → architect → C4 specialist)
- Maintenance overhead (4 agents to update when C4 practices evolve)

## Proposed Solution

**Single architect with level-specific instructions:**
- Keep `matd-architect` as the sole architecture agent
- Create enhanced `arch-c4-architecture` skill with level-specific guidance
- Update `stdd-02-design.md` command to call `matd-architect` 4 times with level-specific instructions
- Deprecate the 4 C4 specialist agents

## Enhanced Skill Structure

```
.agents/skills/arch-c4-architecture/
├── SKILL.md                           # Main skill (enhanced)
│   └── Sections:
│       - Overview of C4 model
│       - How to focus on a specific level
│       - When to use each level
│       - Cross-level consistency checks
│
└── references/
    ├── c4-syntax.md                   # Existing (keep)
    ├── common-mistakes.md             # Existing (keep)
    ├── advanced-patterns.md           # Existing (keep)
    ├── c4-level-context.md            # NEW: Context level guide
    ├── c4-level-container.md          # NEW: Container level guide
    ├── c4-level-component.md          # NEW: Component level guide
    ├── c4-level-code.md               # NEW: Code level guide
    └── c4-best-practices.md           # NEW: Industry best practices
```

### New Reference Files Content

**c4-level-context.md** - Extracted from matd-c4-context.md + web research
- System boundary and external actors
- External systems and their relationships
- Business context and user personas
- When to use Context diagrams
- Examples from real systems

**c4-level-container.md** - Extracted from matd-c4-container.md + web research
- High-level technology choices
- Containers (apps, databases, file systems)
- Inter-container communication
- When to use Container diagrams
- Examples from real systems

**c4-level-component.md** - Extracted from matd-c4-component.md + web research
- Components within containers
- Component responsibilities
- Internal APIs and interfaces
- When to use Component diagrams
- Examples from real systems

**c4-level-code.md** - Extracted from matd-c4-code.md + web research
- Classes, interfaces, database schemas
- Sequence diagrams for key flows
- When to use Code diagrams (rarely)
- Examples from real systems

**c4-best-practices.md** - Web research compilation
- Simon Brown's C4 model guidelines
- Common anti-patterns to avoid
- Tool recommendations (Structurizr, PlantUML, Mermaid)
- Progressive disclosure principles
- Consistency guidelines across levels

## Updated Command Pattern

**Before (stdd-02-design.md):**
```markdown
Delegate to matd-c4-context agent for Context diagram
Delegate to matd-c4-container agent for Container diagram
Delegate to matd-c4-component agent for Component diagram
Delegate to matd-c4-code agent for Code diagram
```

**After (stdd-02-design.md):**
```markdown
Call matd-architect with:
  "Create C4 Context diagram focusing only on system boundary and external actors.
   Use arch-c4-architecture skill with references/c4-level-context.md guidance."

Call matd-architect with:
  "Create C4 Container diagram focusing only on high-level containers.
   Use arch-c4-architecture skill with references/c4-level-container.md guidance."

Call matd-architect with:
  "Create C4 Component diagram focusing only on internal components.
   Use arch-c4-architecture skill with references/c4-level-component.md guidance."

Call matd-architect with:
  "Create C4 Code diagram only if complexity warrants it.
   Use arch-c4-architecture skill with references/c4-level-code.md guidance."
```

## Agent Cleanup

**Keep:**
- `matd-architect.md` - Main architecture agent (enhanced with C4 skills)

**Deprecate:**
- `matd-c4-context.md` → Extract content to reference file, mark as deprecated
- `matd-c4-container.md` → Extract content to reference file, mark as deprecated
- `matd-c4-component.md` → Extract content to reference file, mark as deprecated
- `matd-c4-code.md` → Extract content to reference file, mark as deprecated

**Rationale:** These agents are thin wrappers. Their knowledge belongs in skill references, not separate agent files.

## Universal Agent Skills

All agents should have:
- `general-verification-before-completion` ✓ (needs verification)
- `stdd-ask-questions-if-underspecified` ✓ (needs verification)

Only architect and orchestrator need:
- `orchestrate-dispatching-parallel-agents`
- `orchestrate-executing-plans`
- `orchestrate-subagent-driven-development`

## Implementation Tasks

### Task 1: Web Research (Subagent)
Search for:
- "C4 model best practices Simon Brown"
- "C4 architecture Context Container Component Code guide"
- "C4 model common mistakes"
- "progressive disclosure architecture diagrams"

Compile findings into `c4-best-practices.md`

### Task 2: Extract C4 Agent Content (Subagent)
For each matd-c4-*.md agent:
- Extract the "what to focus on" guidance
- Extract examples and patterns
- Create corresponding reference file
- Add deprecation notice to original agent file

### Task 3: Enhance arch-c4-architecture/SKILL.md (Subagent)
Add sections:
- "Working with Specific C4 Levels" (how to instruct architect)
- Level selection decision tree
- Cross-level consistency checks
- Reference to new level-specific files

### Task 4: Update stdd-02-design.md (Subagent)
Replace 4 separate agent calls with 4 matd-architect calls with level-specific instructions

### Task 5: Verify Universal Skills (Manual)
Audit all matd-* agents to ensure:
- `general-verification-before-completion` in skills list
- `stdd-ask-questions-if-underspecified` in skills list
- Only architect + orchestrator have orchestrate-* skills

## Review Questions

~~1. **Deprecation approach**: Should we delete C4 specialist agents or mark as deprecated with redirect?~~
~~2. **Plugin distribution**: Should deprecated agents stay in MATD plugin or move to separate legacy plugin?~~
~~3. **Command naming**: Keep `stdd-02-design.md` or rename to `matd-02-design.md` for consistency?~~

## Approved Decisions (2026-05-08)

1. **Delete C4 agents** - No deprecation markers, clean deletion
2. **No legacy plugin** - Delete agents entirely from repository
3. **Rename commands** - All `stdd-*.md` → `matd-*.md` for consistency

## Implementation Status

**Status:** Approved - Ready for execution  
**C4 agents to delete:**
- matd-c4-context.md
- matd-c4-container.md
- matd-c4-component.md
- matd-c4-code.md

**Commands to rename:**
- stdd-02-design.md → matd-02-design.md
- (Audit for other stdd-* commands)

---

**OpenCode plugin development:** Marked as future work, not part of current plan.
