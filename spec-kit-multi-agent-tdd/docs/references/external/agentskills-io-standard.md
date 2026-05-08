# AgentSkills.io Open Standard

**Source:** https://agentskills.io/home  
**Extracted:** 2026-05-07  
**Specification Version:** Current as of May 2026

## Executive Summary

AgentSkills.io is an **open industry standard** for packaging and distributing reusable AI agent capabilities. Originally developed by Anthropic and released as an open standard, it has been adopted by 35+ major AI coding platforms including Claude Code, GitHub Copilot, VS Code, Cursor, OpenCode, Gemini CLI, and many others.

**Core Concept:** A skill is a folder containing a `SKILL.md` file with metadata and instructions, plus optional bundled resources (scripts, references, templates).

**Key Innovation:** Progressive disclosure architecture loads only what's needed (metadata → instructions → resources), minimizing context overhead while maximizing agent capabilities.

---

## Standard Overview

### What is AgentSkills.io?

Agent Skills are a **lightweight, open format** for extending AI agent capabilities with specialized knowledge and workflows. The standard defines:

1. **Directory structure** for packaging skills
2. **YAML frontmatter schema** for metadata
3. **Markdown instruction format** for agent guidance
4. **Progressive disclosure pattern** for context-efficient loading
5. **Discovery and activation mechanisms** for agent integration

### Problem Statement

AI agents are increasingly capable but often lack the context needed for reliable real-world work:

- **Missing domain expertise**: Agents don't know company-specific processes, team conventions, or specialized workflows
- **Lack of procedural knowledge**: Generic training data doesn't capture specific tool usage patterns or edge cases
- **Context fragmentation**: Knowledge scattered across docs, runbooks, code comments, and tribal knowledge
- **Non-portable solutions**: Custom system prompts and agent configurations don't transfer between platforms

### Solution

Agent Skills solve these problems by:

- **Packaging procedural knowledge** into portable, version-controlled folders
- **Enabling cross-platform reuse**: Write once, use across any skills-compatible agent
- **Progressive disclosure**: Load only what's needed, when needed
- **Standardized discovery**: Agents automatically find and catalog available skills

### Governance

- **Maintainer**: Originally Anthropic, now community-maintained via GitHub
- **Development**: Open standard, accepts contributions from the broader ecosystem
- **Community**: Active development on [GitHub](https://github.com/agentskills/agentskills) and [Discord](https://discord.gg/MKPE9g8aUy)
- **Reference implementation**: `skills-ref` validation library available

---

## Skill Specification

### Directory Structure

A skill is a directory containing, at minimum, a `SKILL.md` file:

```
skill-name/
├── SKILL.md          # Required: metadata + instructions
├── scripts/          # Optional: executable code
├── references/       # Optional: documentation
├── assets/           # Optional: templates, resources
└── ...               # Any additional files or directories
```

**Design Principle:** The `SKILL.md` file is the only required component. Everything else is optional and added as needed.

### File Format: `SKILL.md`

The `SKILL.md` file must contain **YAML frontmatter** followed by **Markdown content**.

#### Required Fields

| Field         | Type   | Constraints                                                                                    | Purpose                                    |
|---------------|--------|------------------------------------------------------------------------------------------------|--------------------------------------------|
| `name`        | string | 1-64 chars, lowercase alphanumeric + hyphens, must match parent directory, no leading/trailing/consecutive hyphens | Unique identifier for the skill            |
| `description` | string | 1-1024 chars, non-empty                                                                        | What the skill does and when to use it     |

#### Optional Fields

| Field            | Type   | Constraints                                  | Purpose                                        |
|------------------|--------|----------------------------------------------|------------------------------------------------|
| `license`        | string | License name or reference                    | Legal terms for skill usage                    |
| `compatibility`  | string | 1-500 chars                                  | Environment requirements (product, packages, network) |
| `metadata`       | map    | String keys to string values                 | Arbitrary additional properties                |
| `allowed-tools`  | string | Space-separated tool names (experimental)    | Pre-approved tools for permission systems      |

#### Minimal Example

```markdown
---
name: skill-name
description: A description of what this skill does and when to use it.
---
```

#### Full Example

```markdown
---
name: pdf-processing
description: Extract PDF text, fill forms, merge files. Use when handling PDFs.
license: Apache-2.0
compatibility: Requires Python 3.14+ and uv
metadata:
  author: example-org
  version: "1.0"
allowed-tools: Bash(python:*) Read Write
---

# PDF Processing

## When to use this skill
Use this skill when the user needs to work with PDF files...

## Installation
Install dependencies: `uv pip install pdfplumber`

## Extraction workflow
1. Check file exists
2. Run `scripts/extract.py <input.pdf>`
3. Review output in `output/text.txt`

## Gotchas
- Scanned PDFs require OCR (use pdf2image + pytesseract)
- Some forms use non-standard field names
```

---

## Standard Format Details

### Name Field Requirements

**Validation Rules:**
- Must be 1-64 characters
- Only unicode lowercase alphanumeric (`a-z`) and hyphens (`-`)
- Cannot start or end with hyphen
- Cannot contain consecutive hyphens (`--`)
- Must match parent directory name

**Valid Examples:**
- `pdf-processing`
- `data-analysis`
- `code-review`

**Invalid Examples:**
- `PDF-Processing` (uppercase not allowed)
- `-pdf` (cannot start with hyphen)
- `pdf--processing` (consecutive hyphens)

### Description Field Guidelines

**Purpose:** The description serves two critical functions:
1. **Discovery**: Helps agents identify when a skill is relevant
2. **Activation**: Informs the agent's decision to load the skill

**Best Practices:**
- Include specific **keywords** that match task descriptions
- Describe **what** the skill does (capabilities)
- Describe **when** to use it (triggers)
- Mention specific **file types**, **APIs**, or **workflows** the skill handles

**Good Example:**
```yaml
description: Extracts text and tables from PDF files, fills PDF forms, and merges multiple PDFs. Use when working with PDF documents or when the user mentions PDFs, forms, or document extraction.
```

**Poor Example:**
```yaml
description: Helps with PDFs.
```

### Markdown Body Content

The body after frontmatter contains the **skill instructions**. There are **no format restrictions** - write whatever helps agents perform the task effectively.

**Recommended Sections:**
- Step-by-step instructions
- Examples of inputs and outputs
- Common edge cases and gotchas
- Tool/script invocation patterns
- Validation checkpoints

**Size Guidelines:**
- Keep `SKILL.md` under **500 lines** and **5000 tokens**
- Move detailed reference material to separate files
- Use progressive disclosure for large skills

---

## Progressive Disclosure Architecture

### Three-Tier Loading Strategy

Agent Skills use a **progressive disclosure pattern** where agents load increasingly detailed information only as needed:

| Tier | What's Loaded | When | Token Cost | Purpose |
|------|---------------|------|------------|---------|
| **1. Catalog** | `name` + `description` | Session start | ~50-100 tokens/skill | Discovery |
| **2. Instructions** | Full `SKILL.md` body | Skill activation | <5000 tokens (recommended) | Guidance |
| **3. Resources** | Scripts, references, assets | On-demand reference | Varies | Supporting materials |

### How It Works

**Stage 1: Startup Discovery**
```
Agent starts → Scans skill directories → Loads metadata for all skills
└─> Creates catalog: [{name: "pdf-processing", description: "..."}, ...]
└─> Total cost: 50-100 tokens × number of skills
```

**Stage 2: Task-Driven Activation**
```
User: "Extract text from this PDF"
└─> Agent matches task to skill description
    └─> Agent loads full SKILL.md instructions
        └─> Agent follows step-by-step guidance
```

**Stage 3: Resource Loading**
```
SKILL.md says: "Run scripts/extract.py"
└─> Agent reads scripts/extract.py
SKILL.md says: "See references/api-errors.md if status != 200"
└─> Agent reads references/api-errors.md only if error occurs
```

### Benefits

1. **Low baseline overhead**: 20 skills = ~1000-2000 tokens (catalog only)
2. **Context efficiency**: Only active skills consume significant tokens
3. **Scalability**: Agents can maintain large skill libraries
4. **Targeted loading**: Resources loaded only when referenced

---

## Implementation Examples

### Example 1: Simple Skill (No Scripts)

```
code-review/
└── SKILL.md
```

**SKILL.md:**
```markdown
---
name: code-review
description: Review code for security, performance, and style issues. Use when reviewing pull requests or code changes.
---

# Code Review Process

## What to Check

1. **Security**: SQL injection, XSS, authentication bypass
   - Use parameterized queries
   - Validate all user input
   - Check auth on every endpoint

2. **Performance**: N+1 queries, unnecessary loops
   - Index frequently queried columns
   - Batch operations where possible

3. **Style**: Follow project conventions
   - Consistent naming
   - Proper error handling
   - Meaningful comments

## Review Workflow

1. Read the changed files
2. Check each category above
3. Note issues with file:line references
4. Suggest specific fixes
```

### Example 2: Skill with Scripts

```
pdf-processing/
├── SKILL.md
└── scripts/
    ├── extract.py
    ├── fill_form.py
    └── validate.py
```

**SKILL.md:**
```markdown
---
name: pdf-processing
description: Extract text from PDFs, fill forms, validate outputs. Use for PDF manipulation tasks.
compatibility: Requires Python 3.14+ and pdfplumber
---

# PDF Processing

## Setup

Install dependencies:
```bash
uv pip install pdfplumber pdf2image pytesseract
```

## Text Extraction

For digital PDFs:
```bash
python scripts/extract.py input.pdf output.txt
```

For scanned PDFs (OCR required):
```bash
python scripts/extract.py --ocr input.pdf output.txt
```

## Form Filling

1. Analyze form: `python scripts/validate.py form.pdf`
2. Create field mapping (JSON file)
3. Fill form: `python scripts/fill_form.py form.pdf fields.json output.pdf`

## Gotchas

- Some scanned PDFs return empty text (use `--ocr` flag)
- Multi-column layouts may extract in wrong order
- Form field names are case-sensitive
```

### Example 3: Skill with Progressive Disclosure

```
database-migration/
├── SKILL.md
├── scripts/
│   ├── migrate.py
│   └── verify.py
└── references/
    ├── schema-changes.md
    ├── rollback-procedures.md
    └── common-errors.md
```

**SKILL.md:**
```markdown
---
name: database-migration
description: Safely execute database migrations with verification and rollback support. Use for schema changes, data migrations, or database updates.
---

# Database Migration

## Standard Workflow

1. **Verify environment**: `python scripts/verify.py`
2. **Backup database**: `python scripts/migrate.py --backup`
3. **Run migration**: `python scripts/migrate.py --execute`
4. **Verify results**: `python scripts/verify.py --post-migration`

## Error Handling

If migration fails:
1. Check error message
2. Load relevant reference: `references/common-errors.md`
3. If safe to rollback: `python scripts/migrate.py --rollback`

## Important

Read `references/schema-changes.md` before modifying table structure.
Read `references/rollback-procedures.md` if migration fails.
```

**Key Pattern:** The skill references supporting files but doesn't load them upfront. The agent reads them only when needed.

---

## Platform Support

### Adoption Status

**35+ platforms** support Agent Skills as of May 2026, including:

#### Major Coding Agents
- **Claude Code** (Anthropic) - Terminal, IDE, desktop, browser
- **GitHub Copilot** (Microsoft) - VS Code, GitHub
- **Cursor** - AI editor and coding agent
- **OpenCode** - Open source, multi-platform
- **Gemini CLI** (Google) - Terminal agent

#### IDE Integrations
- **VS Code** (Microsoft) - Editor integration
- **Junie** (JetBrains) - IntelliJ platform
- **Roo Code** - VS Code extension

#### Platform-Specific
- **Databricks Genie Code** - Data platform integration
- **Snowflake Cortex Code** - Analytics platform
- **Firebender** - Android development

#### Open Source Agents
- **OpenHands** - Cloud coding platform
- **Goose** (Block/Square) - Extensible agent
- **Mux** (Coder) - Parallel agents
- **Letta** - Stateful agents with memory
- **VT Code** - Multi-LLM support
- **nanobot** - Ultra-lightweight agent

#### Enterprise/Commercial
- **Factory** - AI-native dev platform
- **Amp** - Frontier coding agent
- **Ona** - Background agent platform
- **Kiro** - Spec-driven development
- **Workshop** - Cross-platform agent

#### Specialized
- **Mistral AI Vibe** - Mistral models
- **Command Code** - Learning agent
- **Qodo** - Code integrity platform
- **Laravel Boost** - Laravel best practices
- **Spring AI** - Java/Spring ecosystem

**Full list and documentation links:** https://agentskills.io/clients

---

## Comparison to Claude Code

### Similarities

1. **Structure**: Both use folder-based skill organization
2. **Metadata**: Both require name and description
3. **Progressive loading**: Both support on-demand resource loading
4. **Markdown format**: Both use markdown for instructions
5. **Cross-platform**: Both designed for multi-agent compatibility

### Key Differences

| Aspect | AgentSkills.io | Claude Code (.claude/skills) |
|--------|----------------|------------------------------|
| **Standard Status** | Open industry standard | Claude-specific (but compatible) |
| **File Name** | `SKILL.md` (required) | `SKILL.md` (convention) |
| **Frontmatter** | Strict YAML schema | More flexible |
| **Discovery Path** | `.agents/skills/` (convention) | `.claude/skills/` (native) |
| **Validation** | `skills-ref` validator available | Claude Code validates internally |
| **Governance** | Community-maintained | Anthropic-maintained |
| **Compatibility Field** | Explicit optional field | Not standardized |
| **Allowed-tools** | Experimental standard field | Not in standard |

### Interoperability

**Claude Code supports AgentSkills.io** through:
1. Scanning both `.claude/skills/` (native) and `.agents/skills/` (standard)
2. Parsing standard `SKILL.md` format
3. Supporting standard frontmatter fields
4. Following progressive disclosure pattern

**Migration Path:**
- Skills written for AgentSkills.io work in Claude Code with zero changes
- Claude Code skills work in other agents if they follow the standard
- Recommended: Place skills in `.agents/skills/` for maximum portability

---

## Relevance to SpecKit

### Direct Alignment

SpecKit's multi-agent architecture can leverage Agent Skills for:

1. **Skill Packaging**: Package SpecKit workflows as portable Agent Skills
2. **Cross-Agent Reuse**: Share BMAD methodology skills across Claude Code, OpenCode, Gemini CLI
3. **Progressive Disclosure**: Reduce context overhead in multi-agent orchestration
4. **Discovery Mechanism**: Standardized skill cataloging for agent marketplaces

### Implementation Opportunities

**Current SpecKit Skills → Agent Skills Migration:**

```
harness-tooling/.agents/                    # Current location
├── bmad-phase-0/                          # Could become skill
│   └── agent-orchestration/               # Already skill-like
├── orchestration/                         # Multiple skills
│   ├── parallel-dispatch/                 # → agent skill
│   ├── subagent-execution/                # → agent skill
│   └── worktree-management/               # → agent skill
└── testing/                               # Multiple skills
    ├── playwright-patterns/               # → agent skill
    └── verification-protocols/            # → agent skill
```

**Proposed Structure:**

```
harness-tooling/.agents/skills/            # Standard path
├── bmad-orchestration/
│   ├── SKILL.md                           # Standard format
│   ├── scripts/
│   │   └── create-phase.py
│   └── references/
│       └── BMAD-phases.md
├── parallel-dispatch/
│   ├── SKILL.md
│   └── scripts/
│       └── dispatch-agents.py
└── playwright-testing/
    ├── SKILL.md
    ├── scripts/
    │   └── run-tests.py
    └── references/
        └── test-patterns.md
```

### Benefits for Harness Project

1. **Marketplace Compatibility**: Skills installable by any AgentSkills.io-compatible client
2. **Cross-CLI Support**: Same skills work in Claude Code, OpenCode, Gemini CLI
3. **Standard Validation**: Use `skills-ref` library to validate skill format
4. **Community Patterns**: Leverage best practices from 35+ platform implementations
5. **Progressive Disclosure**: Reduce context overhead for large skill libraries

### Migration Considerations

**No Breaking Changes Required:**
- Current `.claude/skills/` continues to work in Claude Code
- Adding `.agents/skills/` symlinks enables cross-platform compatibility
- Existing `SKILL.md` files likely already compatible

**Recommended Actions:**
1. Validate existing skills with `skills-ref` tool
2. Add `.agents/skills/` to sandbox skill discovery paths
3. Update skill metadata to include standard fields
4. Add `compatibility` field for sandbox-specific requirements
5. Document skill installation for non-Claude agents

---

## Key Takeaways

### For Implementers

1. **Simple Core**: Only `SKILL.md` with frontmatter required
2. **Flexible Structure**: Add scripts/references/assets as needed
3. **Progressive Loading**: Design for three-tier disclosure
4. **Standard Paths**: Use `.agents/skills/` for interoperability
5. **Validation Available**: Use `skills-ref` library

### For Skill Authors

1. **Focus on Domain Knowledge**: What agents don't already know
2. **Optimize Descriptions**: Critical for discovery and activation
3. **Keep Instructions Concise**: Under 500 lines, under 5000 tokens
4. **Use Progressive Disclosure**: Move details to separate files
5. **Test Cross-Platform**: Validate in multiple agents

### For Platform Builders

1. **Three-Tier Loading**: Implement catalog → instructions → resources
2. **Standard Discovery**: Scan `.agents/skills/` in addition to native paths
3. **Lenient Parsing**: Maximize cross-platform compatibility
4. **Permission Allowlisting**: Enable resource access without prompts
5. **Context Protection**: Don't prune skill instructions during compaction

### For SpecKit Integration

1. **Standard Compliance**: Align harness skills with AgentSkills.io format
2. **Dual Compatibility**: Support both `.claude/skills/` and `.agents/skills/`
3. **Validation Integration**: Add `skills-ref` to CI/CD pipeline
4. **Marketplace Ready**: Skills installable by any compatible agent
5. **Progressive Disclosure**: Leverage for context-efficient multi-agent orchestration

---

## Reference Links

- **Official Site**: https://agentskills.io/
- **Specification**: https://agentskills.io/specification
- **Client Showcase**: https://agentskills.io/clients
- **Implementation Guide**: https://agentskills.io/client-implementation/adding-skills-support
- **Best Practices**: https://agentskills.io/skill-creation/best-practices
- **GitHub Repository**: https://github.com/agentskills/agentskills
- **Discord Community**: https://discord.gg/MKPE9g8aUy
- **Validation Tool**: https://github.com/agentskills/agentskills/tree/main/skills-ref

---

**Document Status:** Reference extracted from agentskills.io on 2026-05-07. For latest updates, consult official specification at https://agentskills.io/specification.
