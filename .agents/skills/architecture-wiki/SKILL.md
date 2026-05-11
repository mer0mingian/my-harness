---
name: architecture-wiki
description: Generate and maintain C4 architecture documentation using deepwiki CLI (Litho). Use when generating C4 diagrams (context, container, component, code), analyzing codebase architecture, creating technical documentation, or understanding system design from source code. The deepwiki CLI is pre-installed in the harness sandbox agent container.
license: MIT
---

# Architecture Wiki (Deepwiki/Litho) — Harness Sandbox Integration

## When to use this skill

- Generating C4 architecture documentation from source code
- Creating or updating Context, Container, Component, and Code diagrams
- Analyzing codebase structure and dependencies for technical documentation
- Onboarding new developers with auto-generated architecture docs
- Validating implementation against architecture blueprints
- Detecting architecture drift between design and code

## Deepwiki in the Harness Sandbox

In the harness sandbox, **deepwiki CLI** is pre-installed in the agent container and available at `/workspace/`. The typical workflow:

```
┌──────────────────────────────────────────────────────────┐
│  harness-agent-${PROJECT_NAME}                           │
│  ├─ /workspace/${PROJECT_NAME}/     ← your project code  │
│  ├─ deepwiki CLI (litho)            ← doc generator      │
│  ├─ uv, rtk, other dev tools                             │
│  └─ Claude Code / OpenCode / Gemini CLI                  │
└──────────────────────────────────────────────────────────┘
```

The deepwiki tool analyzes your mounted project code and generates C4 documentation into an output directory (typically `docs/deepwiki` or `docs/architecture`).

## Core Workflow

### 1. Generate documentation for current project

From inside the agent container (or via `docker compose exec`):

```bash
# Basic usage - analyze current directory
deepwiki generate . --output docs/deepwiki

# With specific language (8 languages supported)
deepwiki generate . --output docs/architecture --language en

# With custom config
deepwiki generate . --config deepwiki.toml --output docs/c4
```

### 2. Mount external knowledge (optional)

Deepwiki supports RAG-style integration of external documentation:

```bash
# Include existing ADRs, domain docs, or reference materials
deepwiki generate . \
  --output docs/deepwiki \
  --include-docs ./docs/decisions/*.md \
  --include-docs ./docs/domain/*.pdf
```

This enriches the analysis with business context, architectural decisions, and domain knowledge.

### 3. Configure LLM backend

Deepwiki supports both cloud APIs and local Ollama:

**Cloud APIs** (default):
- Requires `OPENAI_API_KEY` or `ANTHROPIC_API_KEY` in environment
- Best for comprehensive analysis with GPT-4 or Claude

**Local Ollama** (privacy-sensitive environments):
```bash
# Start Ollama service (if not already running)
ollama serve

# Generate with local model
deepwiki generate . --output docs/deepwiki --llm ollama --model llama3
```

### 4. View generated documentation

```bash
# Generated files structure:
docs/deepwiki/
├── 01_context_diagram.md      # C4 Level 1 - System Context
├── 02_container_diagram.md    # C4 Level 2 - Container Architecture
├── 03_component_diagram.md    # C4 Level 3 - Component Details
├── 04_code_diagram.md         # C4 Level 4 - Code Elements
└── diagrams/
    ├── context.mmd            # Mermaid diagram source
    ├── container.mmd
    ├── component.mmd
    └── code.mmd
```

## Configuration

### Project-level config (deepwiki.toml)

Create `deepwiki.toml` in your project root for persistent settings:

```toml
[output]
path = "docs/architecture"
language = "en"

[llm]
provider = "openai"  # or "anthropic" or "ollama"
model = "gpt-4"
cache_dir = ".deepwiki_cache"

[analysis]
include_patterns = ["src/**/*.rs", "src/**/*.py"]
exclude_patterns = ["**/test/**", "**/node_modules/**"]

[knowledge]
external_docs = [
    "docs/decisions/*.md",
    "docs/domain/*.md"
]
```

### Environment variables

Set in `.env` or docker-compose environment:

```bash
# LLM API credentials
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# Cache settings (reduce API costs)
DEEPWIKI_CACHE_DIR=/workspace/.deepwiki_cache
```

## Supported Languages

Deepwiki analyzes **12+ programming languages**:
- **Backend**: Rust, Python, Java, Go, C#, C++, PHP
- **Frontend**: JavaScript, TypeScript, Swift, Kotlin
- **Modern frameworks**: React, Vue, Next.js, etc.

It also generates documentation in **8 human languages**:
- English, Chinese, Japanese, Korean, Spanish, French, German, Portuguese

## Agent Behavior Guidelines

### When to generate documentation

1. **Session start**: If working in a new project without existing C4 docs
2. **Architecture changes**: After significant structural changes to the codebase
3. **Onboarding**: When new team members need to understand the system
4. **Code review**: To validate implementation against intended architecture
5. **User request**: Explicitly asked to generate or update architecture docs

### Analysis depth considerations

| Project Size | Recommended Approach | Notes |
|--------------|---------------------|-------|
| < 10 files | Full analysis, all levels | Fast, comprehensive |
| 10-100 files | Full analysis with caching | Enable cache to speed up re-runs |
| 100-1000 files | Selective analysis by module | Use include/exclude patterns |
| 1000+ files | Module-by-module analysis | Generate per-module, then aggregate |

### Cost optimization

**Enable caching** to reduce LLM API costs (90%+ cache hit rate on re-runs):
```bash
deepwiki generate . --output docs/deepwiki --cache-dir .deepwiki_cache
```

Cache is MD5-based and safely reuses previous LLM responses for unchanged code.

## Common Patterns

### Incremental updates
```bash
# Re-generate only if code changed
deepwiki generate . --output docs/deepwiki --cache-dir .cache --incremental
```

### Database documentation
```bash
# Include SQL schema analysis
deepwiki generate . \
  --output docs/deepwiki \
  --include-sql schema/*.sql \
  --generate-erd
```

### Multi-language projects
```bash
# Analyze heterogeneous codebase
deepwiki generate . \
  --output docs/deepwiki \
  --languages rust,python,typescript
```

## Integration with Project Workflow

### CI/CD integration
```yaml
# Example GitHub Actions workflow
- name: Generate architecture docs
  run: |
    docker compose exec agent deepwiki generate /workspace/${PROJECT_NAME} \
      --output /workspace/${PROJECT_NAME}/docs/architecture \
      --cache-dir /workspace/.deepwiki_cache
      
- name: Commit updated docs
  run: |
    git add docs/architecture/
    git commit -m "docs: update C4 architecture diagrams" || true
```

### Pre-commit hook
```bash
# .git/hooks/pre-commit
#!/bin/bash
# Regenerate docs if source code changed
if git diff --cached --name-only | grep -q "^src/"; then
  deepwiki generate . --output docs/deepwiki --cache-dir .cache
  git add docs/deepwiki/
fi
```

## Troubleshooting

### Deepwiki command not found
```bash
# Verify installation in agent container
docker compose exec agent which deepwiki

# If missing, check Dockerfile includes deepwiki installation
# Or install manually: pip install deepwiki-rs
```

### LLM API rate limits
```bash
# Switch to local Ollama
docker compose exec agent deepwiki generate . \
  --output docs/deepwiki \
  --llm ollama \
  --model llama3

# Or enable aggressive caching
deepwiki generate . --output docs/deepwiki --cache-dir .cache --cache-ttl 30d
```

### Large project analysis timeouts
```bash
# Analyze by subdirectory
deepwiki generate src/backend --output docs/backend_architecture
deepwiki generate src/frontend --output docs/frontend_architecture

# Or exclude heavy dependencies
deepwiki generate . \
  --output docs/deepwiki \
  --exclude-patterns "**/node_modules/**,**/target/**,**/.venv/**"
```

### Missing dependencies in analysis
```bash
# Include external docs for context
deepwiki generate . \
  --output docs/deepwiki \
  --include-docs docs/decisions/*.md \
  --include-docs docs/domain/*.md \
  --include-sql schema/*.sql
```

## References

- **Deepwiki source**: `/workspace/deepwiki-rs/` (if mounted in workspace)
- **CLI entry**: `deepwiki` binary in agent container PATH
- **Documentation output**: `docs/deepwiki/` or `docs/architecture/` (configurable)
- **Cache location**: `.deepwiki_cache/` (configurable via `--cache-dir`)
- **Config file**: `deepwiki.toml` (project root, optional)

## Key Features

1. **Multi-Language Support** — 12+ programming languages analyzed automatically
2. **Dual LLM Support** — Cloud APIs (OpenAI, Claude) and local Ollama for privacy
3. **External Knowledge Integration** — RAG-style chunking of existing docs, ADRs, domain materials
4. **Intelligent Caching** — MD5-based response caching reduces API costs, enables offline replay
5. **8-Language i18n** — Generate docs in English, Chinese, Japanese, Korean, Spanish, French, German, Portuguese
6. **Read-Only Analysis** — Never modifies source code; strict safety guarantee

## Key Constraints

1. **Read-Only Operation** — Deepwiki never modifies source code
2. **LLM Dependency** — Requires LLM API access or local Ollama server
3. **Command-Line Interface** — No GUI; designed for CLI/CI/CD workflows
4. **Static Analysis Only** — Does not execute code or interact with runtime systems

## Success Metrics

| Metric | Target |
|--------|--------|
| Documentation coverage | All significant components documented |
| Onboarding time | < 1 day for new developers to understand architecture |
| Documentation freshness | Auto-updated on every generation (always current) |
| Cost efficiency | 90%+ cache hit rate for re-runs |

---

**See also:**
- [Project Essence](references/PROJECT-ESSENCE.md) — What deepwiki is and why it exists
- [Architecture](references/ARCHITECTURE.md) — How deepwiki components fit together
- [Maintenance Guide](meta/MAINTENANCE.md) — How to maintain generated documentation

---

*Adapted from deepwiki-rs documentation for harness sandbox single-container environment.*
