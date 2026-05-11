---
name: code-graph-context
description: Use CodeGraphContext (CGC) to index a repo into a graph database and query it via MCP in the harness sandbox. Apply when the user wants semantic/code-graph search, call graphs, indexing, or needs to query code relationships. CGC runs in a separate cgc container accessible via MCP through docker exec.
license: MIT
---

# CodeGraphContext (CGC) — Harness Sandbox Integration

## When to use this skill

- Indexing or re-indexing a codebase for AI or CLI queries in the harness sandbox
- Querying code relationships, call graphs, or performing semantic code search
- Understanding how CGC integrates with the multi-container sandbox environment
- Troubleshooting CGC MCP server connectivity or indexing issues

## Sandbox Architecture

In the harness sandbox, CGC runs as a **separate sidecar container** (`cgc` service in docker-compose.yml):

```
┌──────────────────────────────────────────────────┐
│  harness-agent-${PROJECT_NAME}                   │
│  ├─ Claude Code CLI                              │
│  ├─ OpenCode CLI                                 │
│  ├─ Gemini CLI                                   │
│  └─ MCP client config → docker exec to cgc ───┐  │
└────────────────────────────────────────────────│──┘
                                                 │
                                                 ▼
                        ┌────────────────────────────────────┐
                        │  harness-cgc-${PROJECT_NAME}        │
                        │  ├─ CodeGraphContext CLI            │
                        │  ├─ Graph database (Kùzu/Neo4j)     │
                        │  └─ MCP stdio server                │
                        └────────────────────────────────────┘
```

The agent container talks to CGC via MCP using `docker exec` into the cgc container. The cgc container is built from the user's fork at `${WORKSPACE_ROOT}/CodeGraphContext/` and persists its index in the `cgc_data` named volume.

## Core Workflow in Harness Sandbox

### 1. Start the CGC service

The cgc service is controlled via docker compose profiles:

```bash
# From harness-sandbox directory or via bin/harness wrapper
docker compose --profile cgc up -d          # Start agent + cgc
docker compose --profile full up -d         # Start agent + cgc + litho
```

### 2. Index your codebase

**From the host** (recommended for initial indexing):
```bash
# Navigate to your project
cd /path/to/your/project

# Index using cgc from the cgc container
docker exec -i harness-cgc-${PROJECT_NAME} cgc index /workspace/${PROJECT_NAME}
```

**From inside the agent container:**
```bash
# The cgc CLI is available via docker exec wrapper
cgc index .
```

### 3. Query via MCP

Once indexed, the agent CLIs can query CGC through MCP tools:
- `codegraph_find_code` — semantic code search
- `analyze_code_relationships` — call graphs, dependencies
- `add_code_to_graph` — incremental indexing
- Additional tools defined in CodeGraphContext MCP server

### 4. Verify CGC is running

```bash
# Check cgc container status
docker compose ps cgc

# Check logs
docker compose logs cgc

# Test direct access
docker exec -i harness-cgc-${PROJECT_NAME} cgc --version
```

## MCP Configuration

The harness sandbox pre-configures MCP access to CGC. The MCP server runs via:

```bash
docker exec -i harness-cgc-${PROJECT_NAME} codegraphcontext mcp start
```

This is configured in the agent CLI settings (e.g., `~/.claude/config.json` for Claude Code):

```json
{
  "mcpServers": {
    "codegraphcontext": {
      "command": "docker",
      "args": [
        "exec",
        "-i",
        "harness-cgc-YOUR_PROJECT_NAME",
        "codegraphcontext",
        "mcp",
        "start"
      ]
    }
  }
}
```

Replace `YOUR_PROJECT_NAME` with your actual `PROJECT_NAME` from `.env`.

## Agent Behavior Guidelines

- **Index before querying**: If the user hasn't indexed yet, suggest indexing the workspace first
- **Fuzzy symbol search**: On Kùzu/Falkor backends, matching is typo-tolerant (edit distance); on Neo4j, preserve **original casing** for camelCase symbols
- **Path checks**: If `Repository.path` is missing in the DB, suggest cleaning stale `Repository` nodes
- **Workspace paths**: Inside the container, projects are at `/workspace/${PROJECT_NAME}/`; CGC should index from there

## Database Backend Options

CGC supports multiple graph database backends:

| Backend | Use Case | Configuration |
|---------|----------|---------------|
| **Kùzu** (default) | Local-first, embedded, fast | No external service needed |
| **Falkor** | Cloud-hosted, team sharing | Requires Falkor API credentials |
| **Neo4j** | Enterprise, advanced queries | Requires Neo4j instance |

Configure via environment variables in the cgc container or `~/.codegraphcontext/.env`:
- `DEFAULT_DATABASE=kuzu|falkor|neo4j`
- `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD` (for Neo4j)
- `FALKOR_API_KEY` (for Falkor)

## Troubleshooting

### CGC container not starting
```bash
# Check if CodeGraphContext is present in workspace
ls -la ${WORKSPACE_ROOT}/CodeGraphContext/

# Rebuild cgc service
docker compose build cgc
docker compose --profile cgc up -d
```

### MCP connection failing
```bash
# Verify cgc container is running
docker compose ps cgc

# Test MCP server directly
docker exec -i harness-cgc-${PROJECT_NAME} codegraphcontext mcp start

# Check agent CLI config has correct PROJECT_NAME in docker exec command
```

### Indexing fails
```bash
# Check cgc logs
docker compose logs cgc

# Verify workspace mount
docker exec harness-cgc-${PROJECT_NAME} ls -la /workspace/

# Check database configuration
docker exec harness-cgc-${PROJECT_NAME} cgc doctor
```

### Index not persisting
The index is stored in the `cgc_data` named volume. If you remove the container without `--volumes`, the index persists.

```bash
# To fully reset (WARNING: deletes all indexed data)
docker compose down
docker volume rm harness-sandbox_cgc_data
docker compose --profile cgc up -d
```

## Common Patterns

### Index multiple projects in workspace
```bash
# CGC container has access to entire /workspace/ mount
docker exec -i harness-cgc-${PROJECT_NAME} cgc index /workspace/sta2e-vtt-lite
docker exec -i harness-cgc-${PROJECT_NAME} cgc index /workspace/harness-tooling
```

### Force re-index
```bash
docker exec -i harness-cgc-${PROJECT_NAME} cgc index --force /workspace/${PROJECT_NAME}
```

### Query from CLI (for testing)
```bash
# Find code containing pattern
docker exec -i harness-cgc-${PROJECT_NAME} cgc find "authentication"

# Run custom query
docker exec -i harness-cgc-${PROJECT_NAME} cgc query "MATCH (f:Function) WHERE f.name CONTAINS 'login' RETURN f"
```

## References

- **CGC Source**: `/workspace/CodeGraphContext/` (in container)
- **CGC CLI entry**: `codegraphcontext.cli.main`
- **MCP server implementation**: `codegraphcontext.server`, `tool_definitions.py`
- **Harness sandbox compose**: `/workspace/harness-sandbox/docker-compose.yml`
- **CGC data volume**: `cgc_data` (named volume, persists across container restarts)

## Key Architectural Rules

- CGC container is **stateful** (persists index in named volume)
- Agent container is **stateless** (queries CGC via MCP, no local graph)
- Code is **bind-mounted** from host (workspace root pattern)
- CGC sees the same code as the agent container at `/workspace/`
- MCP communication uses **stdio over docker exec** (not HTTP/WebSocket)

---

*Adapted from CodeGraphContext upstream documentation for harness sandbox multi-container environment.*
