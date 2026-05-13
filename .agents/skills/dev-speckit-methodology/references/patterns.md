# Common SpecKit Workflow Patterns

## Pattern: Adding a Feature to Existing Project

```
1. /speckit.specify <new feature description>
2. /speckit.clarify <focus areas>
3. /speckit.plan <tech alignment with existing stack>
4. /speckit.tasks
5. /speckit.implement
```

## Pattern: Parallel Exploration (Same Spec, Different Stacks)

```
# Branch 1: React + PostgreSQL
git checkout 001-photo-albums
/speckit.plan Use React, TypeScript, PostgreSQL
/speckit.tasks
/speckit.implement

# Branch 2: Svelte + SQLite
git checkout -b 001-photo-albums-svelte
/speckit.plan Use Svelte, SQLite, minimal deps
/speckit.tasks
/speckit.implement

# Compare outcomes, merge preferred approach
```

## Pattern: Brownfield Modernization

```
1. /speckit.specify Migrate feature X to modern stack
2. Use brownfield extension if available
3. /speckit.clarify existing constraints, data migration
4. /speckit.plan gradual migration strategy
5. /speckit.tasks with incremental delivery phases
6. /speckit.implement phase by phase
```

## Pattern: Blocked During Implementation

```
# If implementation hits a blocker:
1. STOP executing immediately
2. Document the blocker clearly
3. Ask human for guidance (don't guess)
4. Options:
   - Update tasks.md with new approach
   - Revise plan.md if architectural change needed
   - Refine spec.md if requirements were unclear
5. Resume from corrected phase
```

## Pattern: Multi-Feature Sprint

```
# Constitution once per project
/speckit.constitution <project principles>

# For each feature:
Feature 1:
  /speckit.specify <feature 1 description>
  /speckit.clarify
  /speckit.plan
  /speckit.tasks
  /speckit.implement

Feature 2:
  /speckit.specify <feature 2 description>
  /speckit.clarify
  /speckit.plan
  /speckit.tasks
  /speckit.implement
```

## Pattern: Iterative Refinement

```
# Initial pass (MVP)
/speckit.specify Build basic photo gallery
/speckit.clarify focus on core features only
/speckit.plan minimal viable tech stack
/speckit.tasks
/speckit.implement

# Enhancement pass (v2)
/speckit.specify Add album sharing and comments
/speckit.clarify integration with existing data model
/speckit.plan extend existing architecture
/speckit.tasks
/speckit.implement
```

## Pattern: Cross-Team Dependencies

```
# Feature depends on another team's API
1. /speckit.specify <feature description with dependency>
2. /speckit.clarify document API requirements, expected contract
3. /speckit.plan include contract mocks, integration tests
4. Create contracts/ with expected API schema
5. /speckit.tasks mark API integration tasks with dependency note
6. /speckit.implement with mocked API first
7. Replace mocks when real API available
```

## Pattern: Spike/Research Phase

```
# For uncertain technical decisions
1. /speckit.specify <feature description>
2. /speckit.clarify note areas requiring research
3. Before /speckit.plan, conduct spike:
   - Create spike branch
   - Prototype alternatives
   - Document findings in research.md
4. /speckit.plan with validated tech choices
5. /speckit.tasks
6. /speckit.implement
```
