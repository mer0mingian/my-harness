# SpecKit Troubleshooting Guide

## "Command not found: specify"

**Cause:** SpecKit CLI not installed

**Solutions:**

```bash
# Install via uv
uv tool install specify-cli --from git+https://github.com/github/spec-kit.git

# Or via pipx
pipx install git+https://github.com/github/spec-kit.git

# Verify
specify version
```

## "No .specify/ directory found"

**Cause:** Project not initialized with SpecKit

**Solution:**

```bash
# Initialize project
specify init --here --integration <claude|copilot|gemini>

# Verify
ls .specify/
```

## "Constitution not found"

**Cause:** Constitution not created yet (Phase 0 skipped)

**Solution:**

```bash
# Create constitution first
/speckit.constitution <your project principles>

# Verify
cat .specify/memory/constitution.md
```

## "Spec has [NEEDS CLARIFICATION] markers"

**Cause:** Specification incomplete or ambiguous

**Solution:**

```bash
# Run clarify before planning
/speckit.clarify

# Manually review and address each marker
# Then verify
grep -r "NEEDS CLARIFICATION" specs/
```

## "Plan violates constitutional gates"

**Cause:** Implementation plan doesn't adhere to project principles

**Solutions:**

1. **Simplify the plan** to pass gates
2. **Document justified complexity** in Complexity Tracking section of plan.md
3. **Revise constitution** if gates are too restrictive (rare)

**Example:**

```markdown
## Complexity Tracking

### Article VII Gate: 3-Project Maximum
✅ PASS: Using 2 projects (API + Frontend)

### Article VIII Gate: No Framework Wrapping
❌ FAIL: Created custom ORM abstraction
⚠️ JUSTIFICATION: Team lacks Entity Framework expertise, abstraction
reduces onboarding friction. Will reassess after 2 sprints.
```

## "Tasks out of order / missing dependencies"

**Cause:** Task generation missed dependency relationships

**Solution:**

Manually edit `tasks.md` to correct ordering:

```markdown
### Correct Order (Dependencies First)

1. Create database schema (data layer)
2. Create domain models (business logic)
3. Create service layer (orchestration)
4. Create API endpoints (interface)
5. Create frontend components (presentation)
```

Then run `/speckit.implement`

## "Implementation fails: Missing tool"

**Cause:** Required tool not installed (dotnet, npm, docker, etc.)

**Solution:**

Check plan.md for required tools, install missing ones:

```bash
# Example for .NET project
dotnet --version || sudo apt install dotnet-sdk-8.0

# Example for Node project
node --version || nvm install 20

# Example for Docker
docker --version || sudo apt install docker.io
```

## "Tests fail after implementation"

**Cause:** Implementation doesn't match test expectations

**Solution:**

1. Review test output for specific failures
2. Check if tests reflect current acceptance criteria
3. Fix implementation to pass tests (TDD principle)
4. If tests are wrong, update tests and document why

**Do NOT skip or ignore failing tests**

## "Browser shows errors not visible in CLI"

**Cause:** Client-side JavaScript errors don't appear in server logs

**Solution:**

1. Open browser developer console (F12)
2. Check Console tab for JavaScript errors
3. Check Network tab for failed API calls
4. Copy full error messages back to agent
5. Agent can fix based on actual runtime errors

## "Workflow seems stuck between phases"

**Cause:** Unclear which phase to execute next

**Solution:**

Use the decision tree:

```
Do you have .specify/memory/constitution.md?
├─ NO → Phase 0: /speckit.constitution
└─ YES
   └─ Do you have a spec.md for this feature?
      ├─ NO → Phase 1: /speckit.specify
      └─ YES
         └─ Does spec have [NEEDS CLARIFICATION]?
            ├─ YES → Phase 2: /speckit.clarify
            └─ NO
               └─ Do you have plan.md?
                  ├─ NO → Phase 3: /speckit.plan
                  └─ YES
                     └─ Do you have tasks.md?
                        ├─ NO → Phase 4: /speckit.tasks
                        └─ YES → Phase 5: /speckit.implement
```

## "Extension not loading"

**Cause:** Extension not properly installed or configured

**Solution:**

```bash
# Check installed extensions
specify extension list

# Reinstall extension
specify extension remove <ext-name>
specify extension add <ext-name>

# Verify extension commands are available
ls .claude/commands/ | grep <ext-name>
```

## "Git branch not created during /speckit.specify"

**Cause:** Git repository not initialized or auto-branch creation disabled

**Solution:**

```bash
# Manual branch creation
git checkout -b 001-feature-name

# Or initialize git
git init
git add .
git commit -m "Initial commit"

# Then retry
/speckit.specify <feature description>
```

## "Cannot find feature context from branch"

**Cause:** Not on a feature branch or branch name doesn't match pattern

**Solution:**

```bash
# Check current branch
git branch --show-current

# Should match: NNN-feature-name (e.g., 001-photo-albums)
# If not, switch to correct branch
git checkout 001-photo-albums

# Or specify feature explicitly
/speckit.plan --feature 001-photo-albums
```

## "Parallel tasks causing conflicts"

**Cause:** Tasks marked `[P]` are actually dependent or touch same files

**Solution:**

1. Review tasks.md for incorrect `[P]` markers
2. Remove `[P]` from tasks with shared dependencies
3. Re-run `/speckit.implement` in corrected order

**Rule:** Only mark tasks parallel if they:
- Touch different files
- Have no shared dependencies
- Can be executed in any order

## "Constitution principles conflict"

**Cause:** Contradictory or impossible-to-satisfy principles

**Solution:**

Review constitution.md for conflicts:

```markdown
# CONFLICT EXAMPLE:
Article III: Strict TDD (tests before implementation)
Article VII: Ship fast, iterate later (implementation speed over quality)

# RESOLUTION:
Pick one based on project phase:
- Greenfield/MVP: Allow fast iteration
- Production: Enforce strict TDD
```

Document resolution in constitution.

## Getting Help

If none of these solutions work:

1. Check SpecKit GitHub issues: https://github.com/github/spec-kit/issues
2. Review extension documentation if using extensions
3. Check AI agent integration docs
4. Verify SpecKit version is up-to-date: `specify version`
