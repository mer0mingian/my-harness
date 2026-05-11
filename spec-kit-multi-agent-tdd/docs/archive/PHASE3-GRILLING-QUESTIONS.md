# Phase 3 Grilling Questions

**Date:** 2026-05-08
**Purpose:** Detailed questioning to validate Phase 3 scope and design before implementation
**Instructions:** Answer each question in-line below the question text

---

## Command Architecture & Sequencing

### Q1: Discover Command Scope
The `/speckit.matd.discover` command uses grill-me to generate spec and Technical Constitution.

**Q1a:** Should /discover create ONLY those 2 artifacts, or are there other Discovery Panel artifacts from workflow.svg we should include?

**ANSWER:** No, these two are sufficient.

**Q1b:** If user runs /discover twice for the same feature, should it:
- A) Overwrite existing spec/Constitution
- B) Merge/update existing artifacts
- C) Error and require --force flag

**ANSWER:** B, commands are natural language and do not have force flags

**Q1c:** Should /discover validate that the feature doesn't already have a spec artifact before starting grill-me, or always proceed?

**ANSWER:** Mention but proceed anyway if spec already exists. If constitution exists, just extend/merge it, but do not warn.

---

### Q2: Solution-Design Standalone Mode
You said /solution-design can run without /discover but should warn about spec drift.

**Q2a:** What specifically should the warning message say? Suggest exact wording.

**ANSWER:** No exact wording needed. Just instruct the agent to warn.

**Q2b:** Should the command proceed after warning, or require user confirmation (Y/N prompt)?

**ANSWER:** Proceed after warning.

**Q2c:** If spec/Constitution are missing, where should /solution-design look for problem context?
- Spec artifact only?
- User input (ask for problem description)?
- Fail with "run /discover first"?

**ANSWER:** User input. What is mean twith spec artifact? This should be the spec.

---

### Q3: Execute Command Integration
Current /execute orchestrates: test → implement → review → commit

**Q3a:** Should /execute be extended to include Phase 3 commands?
- Option A: discover → solution-design → test → implement → review → commit
- Option B: Keep /execute as-is, create new /execute-full for complete workflow
- Option C: Make Phase 3 completely separate (user runs manually)

**ANSWER:** C

**Q3b:** If integrated, should discover and solution-design steps be optional (flags like --skip-discover)?

**ANSWER:** -

**Q3c:** Should /execute stop if /discover or /solution-design fail, or continue to test phase?

**ANSWER:** -

---

## ADR Template Design

### Q4: Solution Alternative Count
Default is 3 solution alternatives in ADR.

**Q4a:** Should template enforce exactly 3, or allow user to specify N via argument (e.g., `--alternatives=5`)?

**ANSWER:** Instruct the agent to suggest 3 solutions, do not enforce.

**Q4b:** What's the MINIMUM number of alternatives that makes sense? (1 would be "no comparison", 2 is minimal)

**ANSWER:** 2

**Q4c:** If comparing 3+ solutions, should template include a summary comparison table (matrix view)?

**ANSWER:** Fall back to C1/C2 levels only and group solution approaches into 2-3 groups. Fill ADRs with groups.

---

### Q5: ADR Comparison Criteria
What dimensions should ADR compare solutions on?

**Q5a:** Should criteria be:
- Fixed set (same for all ADRs: performance, maintainability, cost, complexity)
- Problem-specific (agent determines relevant criteria from spec/Constitution)
- User-defined (grill-me asks "what matters most for this decision?")

**ANSWER:** A, extend if requested by user

**Q5b:** Should criteria be weighted (e.g., performance: 30%, cost: 50%, complexity: 20%)?

**ANSWER:** No, user will take the decision and evaluate manually

**Q5c:** Does Technical Constitution influence weighting? (e.g., if Constitution says "optimize for maintainability", that gets higher weight)

**ANSWER:** -

---

### Q6: ADR and C4 Relationship
ADR compares approaches, C4 diagrams detail the chosen one.

**Q6a:** Should ADR include HIGH-LEVEL C4 sketches for EACH alternative (to compare architectures visually)?

**ANSWER:** yes

**Q6b:** Or should ADR be text-only comparison, and C4 diagrams only show the CHOSEN solution?

**ANSWER:** no

**Q6c:** At what point is the solution "chosen"?
- Agent recommends, user confirms in ADR review?
- Automatic based on scoring matrix?
- Part of /solution-design is user selecting from 3 options?

**ANSWER:** Agent recommends, user confirms in ADR review and decides

---

## C4 Agent Integration

### Q7: C4 Agent Invocation Pattern
Markdown command must invoke c4-context, c4-container, c4-component, c4-code agents.

**Q7a:** Should invocation be:
- Sequential (Context completes → feed output to Container → feed to Component → Code)
- Parallel (all 4 agents run simultaneously with same input)
- Hybrid (Context first, then Container+Component+Code in parallel)

**ANSWER:** Needs to be sequential. Each agent must know about the ADR and previous agents output. If this leads to contradictions/inconsistencies, interrupt and let the user provide resolving information.

**Q7b:** What if a c4-* agent is missing (not installed)? Should command:
- Fail entirely
- Skip that level and warn
- Generate placeholder template for user to fill manually

**ANSWER:** Alll agents should be installed together with the plugin. Throw error at speckit-extension install. Raise error if agent is missing during process.

**Q7c:** Should /solution-design validate c4-* agents exist BEFORE starting ADR creation, or discover missing agents mid-execution?

**ANSWER:** before

---

### Q8: C4 Agent Context Requirements
What context do c4-* agents need?

**Q8a:** For c4-context agent, which inputs are REQUIRED?
- [X] spec
- [X] Technical Constitution
- [X] ADR (or at least the chosen solution summary)
- [X] Existing codebase (for brownfield projects)
- [ ] User description (from grill-me or command arg)

**ANSWER:**

**Q8b:** Do lower C4 levels need ALL previous levels, or just the immediate parent?
- c4-container needs: Context only? Or Context + spec + Constitution?
- c4-component needs: Container only? Or Container + Context?

**ANSWER:** All

**Q8c:** Should /solution-design read existing code to inform diagrams (e.g., scan src/ for actual components)?

**ANSWER:** Yes, but only if no c4-description available. IT can come from deepwiki/litho or previous c4 analyses.

---

### Q9: C4 Diagram Format
C4 agents should generate mermaid diagrams.

**Q9a:** Do the c4-* agents in /harness-tooling/.agents/agents already generate mermaid? Or do WE generate mermaid based on their narrative output?

**ANSWER:** Instruc the agents to create the mermaid diagrams

**Q9b:** If agents don't generate mermaid, should /solution-design command:
- Include mermaid generation logic (convert narrative → diagram)
- Invoke a separate "diagram-generator" subagent
- Leave as TODO for user to create diagrams manually

**ANSWER:** dna

**Q9c:** Should diagrams be validated (syntax check, render test) before finalizing artifacts?

**ANSWER:** perhaps. the sandbox environment that the team will work in has access to the litho/deepwiki container. We can install https://github.com/sopaco/mermaid-fixer there. Defer this as an open-point after phase 4. do not fix until then.

---

## Artifact Structure & Relationships

### Q10: spec Structure
spec is created by /discover via grill-me.

**Q10a:** Should spec be:
- Single file (docs/features/${feature_id}-spec.md)
- Multiple files (prd-overview.md, user-stories.md, acceptance-criteria.md)
- Section within spec artifact (no separate file)

**ANSWER:** spec should be a single file, breakdown to Epics/Stories happens during the refinement phase

**Q10b:** What sections MUST spec contain? Suggest minimal required structure.

**ANSWER:** Check the /home/minged01/repositories/harness-workplace/workflow.svg . The "Discovery" panel defines that is part of the spec and must-haves for the System Consitution. Let the user confirm.

**Q10c:** Should spec follow a template, or be free-form based on grill-me conversation?

**ANSWER:** spec needs to have a template. Overlay the user input from the diagram with the content of the specs generate with the /speckit.specify command. Let the user confirm.

---

### Q11: Technical Constitution Scope
What goes in Technical Constitution vs. spec?

**Q11a:** spec defines WHAT (features, user stories). Technical Constitution defines... ?
- Non-functional requirements (performance, scalability, security)?
- Technology constraints (must use Python 3.11, PostgreSQL)?
- Design principles (microservices, event-driven)?
- ALL of the above?

**ANSWER:** see response to Q10. Important: spec does not cover user stories. These are represented as Epics and derived from the spec during refinement. spec only contains the description what user functionality is desired, i.e. Job to be Done. Make a web research to understand the difference and let the user confirm.
Must Haves:
- C1-Level description
- NFRs
  - Observability
  - Testing Strategy
  - Performance
  - Scalability
  - Reliability
- Tech Radar
- Team Tech Skills
- Compliance & Governance
Note that this expands the scope from principles to follow significantly.

**Q11b:** Should Technical Constitution be feature-specific, or project-wide (shared across all features)?

**ANSWER:** It should be system-wide and may contain infos about company policies and team principles.

**Q11c:** If project-wide, where should it live? (docs/architecture/? .specify/? Root?)

**ANSWER:** It will live in the `system-name-agent-workspace` repository.

---

### Q12: Artifact Validation
Config has `validate_artifacts: true` but implementation is missing (G5).

**Q12a:** What should artifact validation check?
- [X] Required sections present (based on template)
- [X] YAML frontmatter valid
- [ ] Markdown syntax valid
- [X] Cross-references exist (e.g., ADR references spec)
- [X] File size reasonable (not empty, not > 10 pages)

**ANSWER:** see checkmarks

**Q12b:** Should validation be:
- Pre-commit hook (block commit if invalid)
- Post-generation check (warn but don't block)
- On-demand tool (user runs manually)

**ANSWER:** post-generation check

**Q12c:** If validation fails, should command:
- Auto-fix (regenerate artifact)
- Prompt user to fix manually
- Escalate to human with diagnostics

**ANSWER:** Escalate to human with diagnostics

---

## Workflow Integration & Evidence

### Q13: Evidence Chain for Phase 3
Phase 2 enforces RED→GREEN with evidence artifacts.

**Q13a:** Should /test command validate that /solution-design artifacts exist before generating tests?
- Required (can't write tests without architecture understanding)
- Optional (warn if missing)
- Independent (tests can be written from spec alone)

**ANSWER:** Warn if anything is missing

**Q13b:** Should /commit validate that Phase 3 artifacts exist alongside Phase 2 artifacts?

**ANSWER:** Yes, but only warn if non-existing

**Q13c:** What's the MINIMUM artifact set for a valid commit in full workflow?
- [ ] Spec --> in spec
- [X] spec --> contains requirements
- [X] Technical Constitution --> System Constitution, might pre-exist for established system
- [ ] ADR
- [X] C4 diagrams (all 4 levels? or just Context?) --> for existing system, container-only suffices
- [ ] Test design
- [ ] Implementation notes
- [X] Review artifacts --> What is this? PR Draft?
- [ ] Workflow summary

**ANSWER:** see notes above

---

### Q14: Grill-Me Integration
/discover uses grill-me skill for questioning.

**Q14a:** Should grill-me run at START of /discover (to build spec from scratch), or throughout (iterative refinement)?

**ANSWER:** throughout

**Q14b:** How many questions should grill-me ask before generating spec?
- Fixed count (e.g., minimum 10 questions)
- Until consensus (agent satisfied with understanding)
- User-controlled (user says "stop, I've given enough info")

**ANSWER:** Until consensus, but allow user defer for clarification of unknowns

**Q14c:** Should grill-me questions be saved as artifact (docs/features/${feature_id}-discovery-questions.md)?

**ANSWER:** no, only unanswered questions

---

### Q15: Review Cycle for Phase 3
Phase 2 has max 3 review cycles for /review command.

**Q15a:** Should /discover have review cycles?
- Agent generates spec → user reviews → agent refines based on feedback → repeat?
- Or: grill-me is inherently interactive, no separate review needed?

**ANSWER:** no, only invoke manually

**Q15b:** Should /solution-design have review cycles?
- Agent proposes 3 solutions → user picks one → agent generates C4 → user reviews → refine?

**ANSWER:** No, only invoke manually

**Q15c:** Should review cycles be configurable per command, or global setting?

**ANSWER:** no autoamted review cycles for these phases

---

## Configuration & Customization

### Q16: Slice 8 Scope Confirmation
Missing implementations: parallel execution, timeout enforcement, artifact validation, convergence detection, local Jira auto-create.

**Q16a:** Are all 5 missing features REQUIRED for Phase 3, or can some be Phase 4 enhancements?

**ANSWER:** Make these 5 a separate phase before phase 3, as we're re-scoping a bit. they will need to be re-evaluated

**Q16b:** Should Slice 8 also add NEW config options (beyond template), or just implement existing ones?

**ANSWER:** just implement existing ones

**Q16c:** Priority order for Slice 8 implementations? (1 = highest priority)
- 1 Parallel execution (for /review parallel agents)
- 2 Agent timeout enforcement
- 3 Artifact validation
- 4 Convergence detection (review cycles)
- 5 Local Jira auto-create

**ANSWER:** see numbers above

---

### Q17: Per-Project vs Global Config
Config template goes in .specify/harness-tdd-config.yml (per-project).

**Q17a:** Should there also be global config (~/.claude/harness-tdd-defaults.yml)?
- User-wide defaults (agent preferences, log level)
- Project config overrides global

**ANSWER:** no, installed with speckit extension per project

**Q17b:** What config options make sense globally vs per-project?

**ANSWER:** make a recommendation

**Q17c:** If global config conflicts with project config, which wins?

**ANSWER:** project

---

## Story Point Calibration

### Q18: Reference Task Estimation
Let's calibrate story points using Phase 2 tasks we've completed.

**Q18a:** Converting test.py → test.md (we did this) was how many story points?
- 1 (trivial)
- 2 (simple)
- 3 (moderate)
- 5 (complex)

**ANSWER:** Cannot answer. How many tokens were required for the task?

**Q18b:** Creating validate_red_state.py script (350 lines, complex pytest parsing) was how many points?

**ANSWER:** Cannot answer. How many tokens were required for the task?

**Q18c:** Full architectural correction plan (research + 10 scripts + 3 hooks + 5 markdown commands) was how many points total?

**ANSWER:**  Cannot answer. How many tokens were required for the task?

---

### Q19: Phase 3 Task Estimation
Estimate these Phase 3 tasks:

**Q19a:** Create ADR template (markdown file with sections, comparison matrix) = 2 points

**ANSWER:** including research

**Q19b:** Create 4 C4 templates (context, container, component, code - each with mermaid diagram section) = 3 points

**ANSWER:** including research

**Q19c:** Implement /discover command (grill-me integration, artifact generation, validation) = 3 points

**ANSWER:** see inline

**Q19d:** Implement /solution-design command (ADR creation, c4-* agent orchestration, diagram generation) = 5 points

**ANSWER:** see inline

**Q19e:** Implement Slice 8 config features (5 missing implementations) = 8 points

**ANSWER:** see inline

---

### Q20: Phase 3 Total Complexity
Original estimate: 7-9 hours for Phase 3 (before /solution-design was added).

**Q20a:** With NEW scope (2 commands + templates + config), what's your estimate in story points for ENTIRE Phase 3?

**ANSWER:** 13+

**Q20b:** Should Phase 3 be split into smaller slices beyond 7a (discover) and 7b (solution-design) and 8 (config)?

**ANSWER:** no

**Q20c:** What's the CRITICAL PATH (longest dependency chain) through Phase 3 tasks?

**ANSWER:** see diagram and commands reference

---

## Open Questions

### Q21: Template Discovery
You mentioned extracting artifact names from workflow.svg.

**Q21a:** The diagram is 3.6MB. Should we extract a text-based artifact list manually, or write a parser?

**ANSWER:** you may also parse from /home/minged01/repositories/harness-workplace/Agentic Engineering Workflow.png


**Q21b:** Are there artifacts in workflow.svg NOT mentioned in our current plan (beyond spec, Constitution, ADR, C4)?

**ANSWER:** check this yourself. there is testing strategy mentioned in refinement phase. this is derived from the spec. It is not a separate artifact

**Q21c:** Should workflow.svg be regenerated to match final Phase 3 scope, or is it a reference only?

**ANSWER:** reference only

---

### Q22: Blockers & Risks
What could prevent Phase 3 from succeeding?

**Q22a:** Biggest risk you foresee in Phase 3 implementation?

**ANSWER:** spec drift. need regular consolidation by asking user questions

**Q22b:** Are c4-* agents tested and working? Or do we need to validate/fix them before /solution-design?

**ANSWER:** tested and working

**Q22c:** Should we prototype /discover with grill-me BEFORE building full command, or trust it will work?

**ANSWER:** trust it will work

---

## Summary Question

### Q23: Ready to Proceed?
After answering above questions:

**Q23a:** Any changes to the Phase 3 approach based on your answers?

**ANSWER:** ready to proceed

**Q23b:** Confidence level (1-10) that Phase 3 scope is now well-defined?

**ANSWER:** not high, since I have clarified some things. please check the /home/minged01/repositories/harness-workplace/Agentic Engineering Workflow.png and validate this corresponds with your expectations

**Q23c:** Should we create a Phase 3 implementation plan NOW, or iterate on answers first?

**ANSWER:** Create plan for plan 2 slice 8 and then create the phase 3 plan

---

## Instructions for Next Steps

1. Answer all questions in-line (replace "**ANSWER:**" with your response)
2. Save this file with answers
3. I will review answers and generate:
   - Updated Phase 3 roadmap with story points
   - Detailed task breakdown
   - Template designs (ADR + 4 C4)
   - Command specifications (/discover, /solution-design)
   - Slice 8 implementation plan
