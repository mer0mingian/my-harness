# Harness v1 — Agent task definitions

**Purpose:** Copy-pasteable subagent prompts to execute the plan in [harness-v1-master-plan.md](harness-v1-master-plan.md). Each task is self-contained: a fresh subagent sees only its own prompt and can complete the task without asking follow-up questions.

**Reading order:** Top-to-bottom is execution order, grouped by phase. Within a phase, tasks marked "parallel with" can run concurrently.

**Conventions used in every prompt:**
- Workspace parent directory: `/mnt/c/memory/`
- Marketplace repo: `/mnt/c/memory/my-harness/`
- Sandbox repo: `/mnt/c/memory/harness-sandbox/`
- Every prompt names explicitly: (a) what files the agent may write to, (b) what it MUST NOT touch, (c) expected response shape, (d) hard response length cap.
- No agent may `git commit`, `git push`, create branches, or delete files. Destructive or network-publishing actions stay in the main thread.
- Research agents return text only; they never call `Write` or `Edit`.

---

## Dependency DAG

```
Phase 0 (research, read-only, return text):
  R1 ─┐
  R2 ─┤
  R3 ─┤   all in parallel
  R4 ─┘
         │
         ▼ main thread synthesizes findings
         │
Phase 1 (sandbox build, write to harness-sandbox/):
  S1 ─┐
  S2 ─┤
  S3 ─┤   all in parallel (after synthesis)
  S4 ─┤
  S5 ─┘
         │
Phase 2 (marketplace restructure, write to my-harness/):
  M1 ──────────────► (review) ──► M1b (rename, optional)
  M2 ──────────────┐
                    ├─► M3 ─┐
                    │       │
                    ├─► M4 ─┼──► M6
                    │       │
                    └─► M5 ─┘
         │
Phase 3: D1 (parallel with M-tasks once M1 done)
Phase 4: V1 (after all above). V2 is manual, Daniel runs it.
```

---

# Phase 0 — Research

## R1 — Inventory my-harness current state

- **Agent:** Explore · **Model:** haiku
- **Writes files:** No
- **Depends on:** nothing · **Parallel with:** R2, R3, R4
- **Deliverable:** structured markdown report returned as the agent's final message

**Prompt:**
```
You are inventorying a repository so a master plan can be executed against
accurate facts. You are NOT modifying anything. Return a structured markdown
report and nothing else. Do not Write or Edit any file.

Repo under inventory: /mnt/c/memory/my-harness/

Produce a report with these sections, each clearly labelled. Keep under 800
words total.

## 1. Skills
List every subdirectory of .agents/skills/. For each:
- name
- whether the name carries one of the prefixes `stdd-`, `orchestrate-`,
  `review-`, `general-` (mark "prefixed" / "unprefixed")
- whether SKILL.md exists inside
Then summarize: total count, prefixed vs unprefixed count, full list of
unprefixed skill names.

## 2. Agents
List every file and subdirectory under .agents/agents/. Report:
- all .md files at the top level
- every subdirectory and, one level deep only, list its .md files
- flag any nesting deeper than one level

## 3. Commands
List every file under .agents/commands/ with its extension. Count .md, .toml,
.gemini.toml.

## 4. Existing CLI directories
For .claude/, .opencode/, .gemini/ (each at repo root):
- does it exist?
- if yes, list top-level entries; mark each entry as file, directory, or
  symlink (show target for symlinks)
- SPECIFICALLY flag any .toml files under .claude/commands/ — those are a
  known prior-plan error.

## 5. Plugin manifests
State presence/absence of each of these exact paths:
- .claude-plugin/plugin.json
- .opencode/opencode.jsonc
- opencode.jsonc (at repo root)
- .gemini/extensions/*/gemini-extension.json
- .mcp.json

## 6. Docs
List every file under /mnt/c/memory/my-harness/docs/ (recurse one level).

Rules:
- Use Glob, Grep, Read only.
- Never call Write, Edit, or Bash commands that modify the filesystem.
- Report facts, not recommendations.
- Cap: 800 words.
```

**Main-thread validation after return:** counts match ~40 skills; unprefixed list is actionable; nested agent dirs are enumerated; no hallucinated paths.

---

## R2 — OpenShell-Community Gemini Dockerfile

- **Agent:** Explore · **Model:** sonnet
- **Writes files:** No
- **Depends on:** nothing · **Parallel with:** R1, R3, R4
- **Deliverable:** structured report with exact Dockerfile contents + installation instructions for extension

**Prompt:**
```
You are researching the upstream base image our sandbox will extend. Return
a structured markdown report. Do not modify any file.

Inspect the pinned version of NVIDIA's OpenShell-Community Gemini sandbox:

- Repo root: https://github.com/NVIDIA/OpenShell-Community
- Pinned README: https://github.com/NVIDIA/OpenShell-Community/blob/36c558e929359830bf272868f42de7bf47bd2716/sandboxes/gemini/README.md
- Pinned Dockerfile: https://github.com/NVIDIA/OpenShell-Community/blob/36c558e929359830bf272868f42de7bf47bd2716/sandboxes/gemini/Dockerfile

A local clone exists at /mnt/c/memory/my-harness/.worktrees/OpenShell (not
guaranteed to be at the pinned commit). Prefer WebFetch on the pinned URLs
above for the source of truth; consult the local clone only for context.

Produce a report with these sections:

## 1. Base image chain
- What FROM does the pinned Dockerfile use?
- What Linux distro and version?

## 2. Packages and tools already installed
Enumerate every apt/yum/npm/pip/cargo/curl install in the pinned Dockerfile.
Group by package manager. Note which of these we will *already have* and
therefore do NOT need to add:
- gemini-cli (almost certainly present — confirm)
- git, curl, ca-certificates, build tools
- node/npm, python, rust (specify versions if stated)

## 3. User, workdir, entrypoint
- What USER is active at the end?
- What WORKDIR is set?
- What ENTRYPOINT / CMD is defined?
- Any exposed ports?

## 4. Volumes declared
Any VOLUME instructions?

## 5. Gaps to fill in a derived image
Given our v1 needs, list what is MISSING and must be added in a derived
Dockerfile. We need inside the container:
- Claude Code CLI (Anthropic's official `claude-code` npm package)
- OpenCode CLI (install script from https://opencode.ai or equivalent — find the
  canonical install instruction)
- Chloe (Rust binary — confirm install mechanism from upstream)
- rtk (rust token killer — confirm install mechanism from upstream)

For each, report the exact install command you recommend.

## 6. Build-time risks
Anything that would break a derived image: entrypoint overrides, non-root
user without sudo, read-only filesystem, tini conflicts, etc.

Rules:
- WebFetch allowed for the three pinned URLs above + any linked install docs
  for Claude Code, OpenCode, Chloe, rtk.
- Read allowed on /mnt/c/memory/my-harness/.worktrees/ contents.
- Do NOT write files.
- Cap: 1200 words.
```

**Main-thread validation after return:** FROM line is named exactly; install commands for Claude Code / OpenCode / Chloe / rtk are copy-pasteable; user/workdir/entrypoint are specified.

---

## R3 — Haft, CodeGraphContext, and litho service specs

- **Agent:** Explore · **Model:** sonnet
- **Writes files:** No
- **Depends on:** nothing · **Parallel with:** R1, R2, R4
- **Deliverable:** one compose-service stanza per tool, runnable and justified

**Prompt:**
```
You are researching how three tools run as Docker services for a local
docker-compose stack. Return a structured markdown report. Do not modify
files.

Each tool has a local clone under /mnt/c/memory/my-harness/.worktrees/:
- haft/
- CodeGraphContext/
- deepwiki-rs/  (this contains `litho`)

Supplement with the upstream README/docs via WebFetch if the local clone
is incomplete:
- https://github.com/m0n0x41d/haft
- https://github.com/CodeGraphContext/CodeGraphContext
- https://github.com/sopaco/deepwiki-rs

For each tool produce exactly these fields:

### {tool name}

**Role in harness:** one sentence describing what an agent uses it for.

**Runtime mode:** one of: "always-on MCP server", "on-demand CLI", "library
(not a service)".

**Upstream Docker image:** the official published image name:tag if one
exists. If none, state "none — must build from source" and give the
dockerfile path in the local clone.

**Dependencies:** other services/DBs required (e.g. Neo4j, Kuzu). Specify
version constraints.

**Exec command:** the exact command the container runs to serve MCP or
perform its function. E.g. `haft mcp --port 3333` or `cgc mcp start`.

**Ports exposed:** list.

**Volumes needed:** list (e.g. `/workspace/project` read-only for scanning,
or a named volume for a graph DB).

**Env vars:** list of required env vars (names only, don't invent values).

**Compose service stub:** a copy-pasteable YAML block for a
`docker-compose.services.yml` service. For `litho` specifically, include
`profiles: [docs]` and NO restart policy (it's fire-and-forget).

## Cross-tool notes
- Do they share a network? (Assume yes — all join `harness_net`.)
- Are their DBs local embedded (Kuzu/SQLite) or separate containers
  (Neo4j/FalkorDB)? Recommend the lightest viable option for a laptop.

Rules:
- Read, Glob, Grep, WebFetch allowed. No Write/Edit.
- For any uncertainty, explicitly mark "unverified — needs main-thread
  decision" instead of guessing.
- Cap: 1500 words.
```

**Main-thread validation:** each compose stub has valid YAML; ports don't collide; DB recommendation justifies "lightest viable" for local laptop use.

---

## R4 — Graphiti MCP server + DB stack

> **[Superseded — see CGC integration]** Graphiti as a separate personal-memory stack was dropped from v1; the corresponding `docker-compose.graphiti.yml` was deleted. CGC fulfils the structural code-graph role only — it does not replace Graphiti's long-term episodic memory. Section preserved for historical context.


- **Agent:** Explore · **Model:** sonnet
- **Writes files:** No
- **Depends on:** nothing · **Parallel with:** R1, R2, R3
- **Deliverable:** compose file content for `docker-compose.graphiti.yml`

**Prompt:**
```
You are researching how to run Graphiti as optional personal memory in an
isolated docker-compose file. Return a report. Do not modify files.

Local clone: /mnt/c/memory/my-harness/.worktrees/graphiti/
Upstream: https://github.com/getzep/graphiti

Focus first on the MCP server at `mcp_server/` in the repo.

Produce:

## 1. Graph DB choice for v1
Graphiti supports Neo4j, FalkorDB, Kuzu, Neptune. For a laptop-local
deployment that is easy to start and stop:
- recommend ONE backend
- justify (RAM footprint, startup time, persistence)
- state the exact image:tag to use

## 2. Service stanzas
Produce two docker-compose service stanzas (YAML, copy-pasteable):
1. The graph DB backend (image, ports, volume for persistence, env).
2. The Graphiti MCP server itself (image or build context, ports, env,
   depends_on).

## 3. Env vars required
List exactly. Group by:
- LLM API keys (OpenAI vs Anthropic vs Gemini — which is the minimum
  required set?)
- Embedding model
- DB connection strings

## 4. How an agent CLI reaches it
The Graphiti MCP server runs in a separate compose file but on the same
Docker network as the agent sandbox (`harness_net`). State the MCP URL or
command an agent would configure in `.mcp.json` / `opencode.jsonc` /
`gemini-extension.json` to talk to it.

## 5. Shutdown / omit story
Confirm that `docker compose -f docker-compose.yml up` (our main file)
does NOT start Graphiti. Confirm that running both files together works:
`docker compose -f docker-compose.yml -f docker-compose.graphiti.yml up`.
Flag any compose-file pitfalls (network naming, volume collisions).

Rules:
- WebFetch, Read, Glob allowed. No Write/Edit.
- Cap: 1000 words.
```

**Main-thread validation:** Single DB backend with rationale; `up` without the graphiti file confirmed to not start it; MCP URL format is concrete.

---

# Phase 1 — Sandbox build

All Phase 1 tasks operate on `/mnt/c/memory/harness-sandbox/`. They MUST NOT touch `/mnt/c/memory/my-harness/` in any way.

Each Phase 1 prompt assumes the main thread will substitute `{{R2_FINDINGS}}`, `{{R3_FINDINGS}}`, `{{R4_FINDINGS}}` placeholders with the relevant sections of the Phase 0 reports before launching the agent. The placeholders remain in this doc as a template; at runtime, main thread replaces them inline.

## S1 — Dockerfile

- **Agent:** general-purpose · **Model:** sonnet
- **Writes files:** Yes — `/mnt/c/memory/harness-sandbox/Dockerfile` ONLY
- **Depends on:** R2 synthesized · **Parallel with:** S2, S3, S4, S5
- **Deliverable:** a Dockerfile that builds successfully via `docker build`

**Prompt:**
```
Write a Dockerfile at /mnt/c/memory/harness-sandbox/Dockerfile. You may
only Write that single file. Do NOT touch any file in /mnt/c/memory/my-harness/.
Do NOT run `docker build` — verification is the main thread's job.

## Base image

Use the pinned NVIDIA OpenShell-Community Gemini sandbox image as the
base. Per R2:

{{R2_FINDINGS}}

## Required additions in the derived image

Install, layered in a single RUN where possible to keep layers tidy:

1. Claude Code CLI — via `npm install -g <package-name>` (use the package
   name R2 identified).
2. OpenCode CLI — via the install command R2 identified.
3. Chloe — via the install command R2 identified.
4. rtk — via the install command R2 identified.

## Dockerfile requirements

- Keep layers small. Combine apt/pip/npm installs into one RUN with
  `&& rm -rf /var/lib/apt/lists/*` style cleanup.
- Do NOT hardcode API keys or secrets. Any env vars are set via the
  compose file or runtime `.env`.
- Preserve the base image's USER and WORKDIR unless R2 flagged a blocker.
- Add a `HEALTHCHECK` only if trivially useful (e.g. `claude --version`);
  otherwise omit.
- Add a comment at the top stating the base image's upstream commit SHA
  for traceability.

## File format

Write exactly one Dockerfile. No extra files, no README here.

## Response shape

After writing, return a short message stating:
- the number of RUN layers
- the final USER / WORKDIR / ENTRYPOINT
- any TODO left inline in the Dockerfile for main-thread review
Cap: 150 words.
```

**Main-thread validation:** file exists; `docker build --no-cache .` succeeds on a clean machine; image <2GB final.

---

## S2 — docker-compose.yml (agent container)

- **Agent:** general-purpose · **Model:** sonnet
- **Writes files:** Yes — `/mnt/c/memory/harness-sandbox/docker-compose.yml`
- **Depends on:** nothing (runs in parallel with S1, S3, S4, S5)

**Prompt:**
```
Write /mnt/c/memory/harness-sandbox/docker-compose.yml. You may only Write
that file.

Contents: a single service named `agent`, defined as follows.

## Service requirements

- `build: .` (uses the sibling Dockerfile written by S1).
- `container_name: harness-agent-${PROJECT_NAME:-default}`.
- `hostname: harness-agent`.
- `command: ["sleep", "infinity"]` — long-running container; devs attach
  via `docker exec`.
- `stdin_open: true`, `tty: true`.
- Bind-mounts:
  - `${MARKETPLACE_PATH:-../my-harness}:/workspace/marketplace:ro`
  - `${PROJECT_PATH:-./project}:/workspace/project:rw`
  - `${HOME}/.claude:/home/sandbox/.claude:rw`
  - `${HOME}/.opencode:/home/sandbox/.opencode:rw`
  - `${HOME}/.gemini:/home/sandbox/.gemini:rw`
  - `./.env:/workspace/.env:ro`
- `env_file: .env`.
- Network: join external network `harness_net` (defined below).
- Working dir inside: `/workspace/project`.

## Networks

Declare `harness_net` as an external network (created once by the services
compose file). Marker: `external: true`.

## Volumes

None needed at this level — all data flows through bind mounts.

## Notes inside the file

Add top-of-file comments explaining:
- one container per project; override via `PROJECT_NAME` + `PROJECT_PATH`.
- the marketplace is ro; the project is rw.
- host-CLI dirs are bind-mounted so session files are readable from host
  (codeburn integration).

## Response shape

After writing, return:
- list of bind mounts (verified)
- the env_file path used
- confirmation that no service other than `agent` is declared
Cap: 150 words.
```

**Main-thread validation:** `docker compose config` prints valid output; no hidden secrets inlined.

---

## S3 — docker-compose.services.yml (Haft + CGC + litho)

- **Agent:** general-purpose · **Model:** sonnet
- **Writes files:** Yes — `/mnt/c/memory/harness-sandbox/docker-compose.services.yml`
- **Depends on:** R3 synthesized

**Prompt:**
```
Write /mnt/c/memory/harness-sandbox/docker-compose.services.yml.

Services to declare, using the exact stanzas R3 produced (below):

{{R3_FINDINGS}}

## Structure requirements

- Declare three services: `haft`, `codegraphcontext`, `litho`.
- `haft` and `codegraphcontext` are always-on: default restart policy
  `unless-stopped`.
- `litho` is on-demand: MUST have `profiles: [docs]` and NO restart
  policy.
- Any DB dependencies R3 identified as separate containers go in this
  file too, wired via `depends_on`.
- Declare the shared network: `harness_net`, `driver: bridge`, NOT
  external (this file creates it; compose.yml joins it as external).
- Declare named volumes for any DB persistence R3 specified.
- All services share `env_file: .env`.

## Port exposure

Expose ports only on localhost:
- `"127.0.0.1:<port>:<port>"`
Do NOT expose on `0.0.0.0` — laptop-local only.

## Response shape

After writing, return:
- services declared (names)
- which have `profiles: [docs]`
- named volumes created
- ports exposed (host:container)
Cap: 200 words.
```

**Main-thread validation:** `docker compose -f docker-compose.services.yml config` validates; litho does not appear in `docker compose -f docker-compose.services.yml ps` after `up`.

---

## S4 — docker-compose.graphiti.yml (optional)

> **[Superseded — see CGC integration]** The Graphiti compose file was deleted in a later revision; CGC runs as the external `cgc` service in `docker-compose.yml` and does not provide episodic memory. Section preserved for historical context.


- **Agent:** general-purpose · **Model:** sonnet
- **Writes files:** Yes — `/mnt/c/memory/harness-sandbox/docker-compose.graphiti.yml`
- **Depends on:** R4 synthesized

**Prompt:**
```
Write /mnt/c/memory/harness-sandbox/docker-compose.graphiti.yml.

Contents per R4:

{{R4_FINDINGS}}

## Constraints

- Declare TWO services: the chosen graph DB backend and `graphiti-mcp`.
- Both join the external network `harness_net` (declared in
  docker-compose.services.yml — mark as `external: true` here).
- Use named volumes for DB persistence.
- env_file: .env.
- Port exposure: localhost-only, same pattern as S3.
- This file is standalone — loading the main compose.yml must NOT
  accidentally start Graphiti.

## Top-of-file comment

Add a multi-line comment that includes this verbatim:
```
# Optional: Graphiti personal memory stack.
# Loaded explicitly:
#   docker compose -f docker-compose.yml -f docker-compose.graphiti.yml up -d
# Never loaded by default.
```

## Response shape

Return: services declared, ports, volumes, confirmation that the top
comment is present verbatim. Cap: 150 words.
```

**Main-thread validation:** top comment present; `docker compose config` succeeds; loading without this file does not mention graphiti.

---

## S5 — .env.example + bin/harness + docs

- **Agent:** general-purpose · **Model:** sonnet
- **Writes files:** Yes — all inside `/mnt/c/memory/harness-sandbox/`:
  - `.env.example`
  - `bin/harness` (executable shell script)
  - `docs/quickstart.md`
  - `docs/attach-patterns.md`
  - `docs/troubleshooting.md`
- **Depends on:** R2, R3, R4 synthesized

**Prompt:**
```
Write five files under /mnt/c/memory/harness-sandbox/. Only these five.

## 1. .env.example

Contain placeholder entries for every env var referenced by any of:
- docker-compose.yml (PROJECT_NAME, PROJECT_PATH, MARKETPLACE_PATH)
- docker-compose.services.yml (per R3)
- docker-compose.graphiti.yml (per R4)

Include API-key placeholders for Anthropic, OpenAI, Gemini, Groq. Every
line a placeholder like `ANTHROPIC_API_KEY=`. Group under comment headers:
`# LLM providers`, `# Project layout`, `# Haft`, `# CodeGraphContext`,
`# Graphiti (optional)`.

Include a top-of-file comment: `# Copy to .env and fill in real values.
Never commit .env.`

## 2. bin/harness

A bash shell script, executable via chmod on the committed file perms
(note: you cannot chmod through the Write tool; add a line to the
quickstart.md telling the user to run `chmod +x bin/harness` after clone).

Must support the following subcommands:
- `harness up [--project PATH]` — `docker compose up -d` the agent, binding
  PROJECT_PATH. Default project path = `$PWD`.
- `harness shell` — `docker exec -it harness-agent-${PROJECT_NAME:-default}
  /bin/bash`.
- `harness down` — `docker compose down`.
- `harness services up|down` — wraps `docker compose -f
  docker-compose.services.yml up -d` / `down`.
- `harness graphiti up|down` — wraps graphiti compose file.
- `harness docs analyze` — `docker compose -f docker-compose.services.yml
  --profile docs run --rm litho litho analyze /workspace/project`.
- `harness help` — print subcommand list.

Defensive posture:
- `set -euo pipefail`
- If `.env` is missing, print: "No .env found. Copy .env.example to .env
  and fill in values."
- If docker is not installed or not running, print a helpful error and
  exit 1.

## 3. docs/quickstart.md

Aim: a new dev clones both sibling repos, then runs four commands and has
a working sandbox. Include:
- prerequisites (Docker Desktop / WSL2 + Docker, git)
- `chmod +x bin/harness`
- `cp .env.example .env` + fill in at least ANTHROPIC_API_KEY
- `harness services up`
- `harness up`
- `harness shell` → dev is inside; `claude --version` and `opencode
  --version` both succeed.
Cap: 400 words.

## 4. docs/attach-patterns.md

Three short sections:
- VS Code Remote — Containers (reference the Dev Containers extension
  pattern; one paragraph).
- WSL bash + Windows Terminal direct attach (`harness shell`).
- chloe inside the sandbox (`harness shell` then `chloe`).
Cap: 300 words.

## 5. docs/troubleshooting.md

Cover: missing .env, port collisions (localhost-only so rare but list),
marketplace not found (MARKETPLACE_PATH resolution), services network
missing, how to reset state (`docker compose down -v`).
Cap: 300 words.

## Response shape
Return: list of files written + their byte counts. Cap: 80 words.
```

**Main-thread validation:** `bash -n bin/harness` passes; all 5 files exist; quickstart references real commands.

---

# Phase 2 — Marketplace restructure

All Phase 2 tasks operate on `/mnt/c/memory/my-harness/`. They MUST NOT touch `/mnt/c/memory/harness-sandbox/`.

## M1 — Skill naming audit (report only)

- **Agent:** general-purpose · **Model:** haiku
- **Writes files:** No — returns a report only
- **Depends on:** R1 complete · **Parallel with:** M2

**Prompt:**
```
You are auditing skill naming in /mnt/c/memory/my-harness/.agents/skills/.
Do NOT rename anything. Do NOT Write or Edit. Return a report.

A valid skill name carries one of these prefixes: `stdd-`, `orchestrate-`,
`review-`, `general-`.

For every subdirectory of .agents/skills/ that lacks a valid prefix:
1. Read its SKILL.md (first 50 lines is enough).
2. Infer which prefix best fits, based on content:
   - Feature-spec / TDD / openspec work → stdd-
   - Multi-agent dispatch / workflow orchestration → orchestrate-
   - Review, debugging, security → review-
   - Everything else (language tips, general utilities) → general-
3. Propose a new name: `<prefix>-<current-name>` unless the current name
   already describes itself better, in which case propose a cleaner rewrite.
4. State your confidence in one word: high | medium | low.

Return a markdown table with columns: current-name, proposed-name,
chosen-prefix, confidence, one-sentence rationale.

Rules: Glob, Read, Grep only. No Write/Edit. Cap: 600 words.
```

**Main-thread validation + follow-up:** main thread reviews the proposed renames; if ≥90% are high-confidence and obvious, spawn **M1b** (next). If not, main thread escalates to Daniel for decision.

---

## M1b — Execute skill renames (conditional)

- **Agent:** general-purpose · **Model:** haiku
- **Writes files:** Yes — `mv` on directory names inside `.agents/skills/`
- **Depends on:** M1 + Daniel's approval of the rename mapping
- **Parallel with:** nothing else in Phase 2 (acquires lock on skills/)

**Prompt:** *(templated — main thread substitutes the approved mapping)*
```
Rename skill directories inside /mnt/c/memory/my-harness/.agents/skills/
per this mapping approved by the user:

{{APPROVED_RENAME_MAPPING}}

For each rename:
1. Use Bash `git mv old new` inside the my-harness repo — this preserves
   git history. Use `git -C /mnt/c/memory/my-harness mv ...`.
2. If the target name already exists, abort with an error for that pair
   only; continue with the rest.
3. After all renames, run `git -C /mnt/c/memory/my-harness status` and
   include the output in your response.

Do NOT commit. Do NOT push. Do NOT modify any files outside
.agents/skills/.

Response: per-rename success/failure lines + final git status. Cap: 300 words.
```

**Main-thread validation:** git status shows only the expected renames; no stray changes.

---

## M2 — Flatten nested agent directories

- **Agent:** general-purpose · **Model:** sonnet
- **Writes files:** Yes — `git mv` operations in `.agents/agents/`
- **Depends on:** R1 complete · **Parallel with:** M1

**Prompt:**
```
You are flattening nested agent directories in /mnt/c/memory/my-harness/
.agents/agents/. Claude Code does not recurse into subdirectories under
`.claude/agents/`, so the canonical source must be flat. OpenCode tolerates
either.

Current nested subdirs (per R1 report): c4-architecture-agents/,
daniels-workflow-agents/, tdd-agents/ (verify by reading the directory —
R1 is the plan's inventory but re-check).

Procedure:
1. For every .md file inside a subdirectory of .agents/agents/:
   - If the filename already makes its category clear (e.g.
     `c4-architect.md`), move it up as-is: `git mv
     c4-architecture-agents/c4-architect.md ./c4-architect.md`.
   - If the filename is generic (`architect.md`, `reviewer.md`), prefix
     with the parent dir's category: `c4-architect.md`,
     `tdd-reviewer.md`.
2. After moving all .md files up, delete the now-empty subdir via
   `git -C /mnt/c/memory/my-harness rm -r <subdir>`.
3. DO NOT commit. DO NOT push.
4. After all operations, run `git -C /mnt/c/memory/my-harness status` and
   include in response.

Per-file rationale line in the response: `daniels-workflow-agents/
orchestrator.md → daniels-workflow-orchestrator.md` (prefixed because
filename was ambiguous).

Use Bash (git mv), Read, Glob. No Write to file contents. No commits.
Cap: 500 words.
```

**Main-thread validation:** no orphan empty subdirs; each moved file is reachable at the new top-level path; git status shows only moves, no content edits.

---

## M3 — .claude/ + .claude-plugin/ setup

- **Agent:** general-purpose · **Model:** sonnet
- **Writes files:** Yes — `/mnt/c/memory/my-harness/.claude/` tree and `.claude-plugin/plugin.json`
- **Depends on:** M1 (skills stable), M2 (agents flat) · **Parallel with:** M4, M5

**Prompt:**
```
Set up the Claude Code integration inside /mnt/c/memory/my-harness/.

## Directories / files to create

1. `.claude/settings.json` — JSON with:
   - `permissions.allow`: common read-only bash (`git status*`, `git log*`,
     `ls*`), `Read`, `Glob`, `Grep`. Nothing network.
   - `hooks`: empty object for now; structure it as a dict so future hooks
     land cleanly.
   - Top-of-file comment impossible in JSON — but add a sibling file
     `.claude/settings.README.md` explaining what's in settings.json and
     that hooks will be added in a later iteration.

2. Symlinks (use `ln -s` via Bash — WSL2 ext4 or NTFS-with-symlinks):
   - `.claude/skills` → `../.agents/skills`
   - `.claude/agents` → `../.agents/agents`
   - `.claude/commands` → `../.agents/commands`
   Abort if any target already exists; do NOT overwrite.

3. `.claude-plugin/plugin.json` — the marketplace manifest:
   ```json
   {
     "name": "multi-agent-harness",
     "version": "0.1.0",
     "description": "Daniel's STDD + orchestration + review workflows for Claude Code",
     "author": "Daniel Mingers",
     "homepage": "https://github.com/<TBD>",
     "skills": "skills",
     "agents": "agents",
     "commands": "commands"
   }
   ```
   The `<TBD>` is a deliberate placeholder — main thread substitutes when
   the GitHub repo URL is known.

## MUST NOT
- Do NOT create any .toml file under .claude/commands/ — Claude Code uses
  markdown for commands.
- Do NOT modify any file under .agents/.
- Do NOT commit.

Response: list of files created, symlink targets, output of
`ls -la .claude/`. Cap: 200 words.
```

**Main-thread validation:** `readlink` on each symlink resolves; `jq . .claude-plugin/plugin.json` parses; no TOML under `.claude/commands/`.

---

## M4 — .opencode/ setup with permission ACLs

- **Agent:** general-purpose · **Model:** sonnet
- **Writes files:** Yes — `.opencode/` directory (symlinks + jsonc)
- **Depends on:** M1, M2 · **Parallel with:** M3, M5

**Prompt:**
```
Set up the OpenCode integration inside /mnt/c/memory/my-harness/.

## Current state (per R1)

R1 will have reported existing .opencode/ symlinks. If they already exist
and point to .agents/..., leave them. If they point elsewhere, back them
up to `.opencode/OLD_<name>_<timestamp>` and recreate correctly. Never
silently overwrite.

## Create / ensure

1. Symlinks (same pattern as M3, targeting .agents/ at relative path):
   - `.opencode/skills`   → `../.agents/skills`
   - `.opencode/agents`   → `../.agents/agents`
   - `.opencode/commands` → `../.agents/commands`

2. `opencode.jsonc` at the repo ROOT (NOT inside .opencode/). Contents:
   ```jsonc
   {
     // OpenCode project config for the multi-agent harness.
     "$schema": "https://opencode.ai/config.json",
     "plugin": [
       "opencode-workflows",
       "opencode-yaml-hooks"
     ],
     "mcp": {
       // MCP server wiring populated in a later phase;
       // services run in the sibling harness-sandbox compose stack.
     }
   }
   ```

3. Do NOT edit any OpenCode agent frontmatter in this task. That is M6.

## MUST NOT

- Do NOT touch .agents/.
- Do NOT commit.

Response: list of symlinks created + their targets; contents of opencode.jsonc;
any backups made with old/new paths. Cap: 200 words.
```

**Main-thread validation:** opencode.jsonc valid JSONC (JSON with comments); symlinks resolve.

---

## M5 — .gemini/ extension scaffolding

- **Agent:** general-purpose · **Model:** sonnet
- **Writes files:** Yes — `.gemini/extensions/research/`
- **Depends on:** M1, M2 · **Parallel with:** M3, M4

**Prompt:**
```
Scaffold a Gemini CLI extension at /mnt/c/memory/my-harness/.gemini/
extensions/research/.

Per the harness v1 plan, Gemini CLI is scoped to *research* workflows
(not STDD feature dev). The extension should expose only `review-*` and
`general-*` skills, plus the STDD specification / research-adjacent
commands. It should NOT expose `stdd-` implementation skills like TDD.

## Files to create

1. `gemini-extension.json`:
   ```json
   {
     "name": "research",
     "version": "0.1.0",
     "description": "Research workflows for Gemini CLI: review, analysis, information gathering.",
     "contextFileName": "GEMINI.md",
     "mcpServers": {
       "codegraphcontext": {
         "command": "http",
         "url": "http://codegraphcontext:<PORT>/mcp",
         "comment": "Populated from R3 findings at runtime"
       }
     },
     "excludeTools": []
   }
   ```
   Replace `<PORT>` with the port R3 identified for CGC.

2. `GEMINI.md` — a short context file telling Gemini CLI: "You are a
   research assistant. Use the review-* and general-* skills. Do not
   attempt feature implementation." Cap: 150 words.

3. `skills/` — populate with symlinks to only the review-* and general-*
   skills under /mnt/c/memory/my-harness/.agents/skills/. Use relative
   paths (`../../../../.agents/skills/review-differential-review` etc.).
   Discover the list of matching skills via Glob on
   .agents/skills/review-* and general-*.

4. `commands/` — directory containing only the `.gemini.toml` command
   files. Discover via Glob on .agents/commands/*.gemini.toml and
   symlink each individual file (not the parent dir) into this folder.
   If no .gemini.toml files exist, create the empty directory and skip
   symlinking.

## MUST NOT
- Do NOT create STDD-prefixed skill symlinks here.
- Do NOT commit.
- Do NOT touch .agents/.

Response: list of skills linked (count + names), commands linked, contents
of gemini-extension.json. Cap: 250 words.
```

**Main-thread validation:** `jq . gemini-extension.json` passes; no `stdd-` symlinks in `skills/`; port substituted.

---

## M6 — Agent frontmatter updates (skills lists + permission ACLs)

- **Agent:** general-purpose · **Model:** sonnet
- **Writes files:** Yes — existing agent `.md` files under `.agents/agents/` (frontmatter only)
- **Depends on:** M3, M4, M5 (all CLI scaffolding in place)

**Prompt:**
```
You are updating YAML frontmatter of agent markdown files under
/mnt/c/memory/my-harness/.agents/agents/. You modify frontmatter ONLY,
never the body below the frontmatter.

Context: each agent file is the source of truth for all three CLIs. We
extend frontmatter with BOTH a Claude-Code-style `skills:` list AND an
OpenCode-style `permission:` block. Whichever CLI reads it will use the
fields it understands and ignore the others.

## For each agent file

1. Read the file and the body (to understand what skills the agent uses).
2. Determine the right skill prefixes for that agent. Guidance:
   - `daniels-workflow-orchestrator.md` / `daniels-orchestrator.md` →
     `stdd-` + `orchestrate-` + `general-`.
   - `daniels-architect.md` / c4-* / architect-themed → `orchestrate-` +
     `review-` + `general-`.
   - tdd-* → `stdd-` (TDD skills) + `general-`.
   - Everything else → ask via a comment line `# TODO: confirm skills`
     rather than guess.
3. Extend frontmatter:
   ```yaml
   ---
   # ...existing fields kept...
   skills:
     - stdd-ask-questions-if-underspecified   # explicit Claude Code list
     - ...
   permission:
     skill:
       "stdd-": allow        # OpenCode prefix ACL
       "orchestrate-": allow
       "general-": allow
       "": deny
   ---
   ```
4. Preserve all existing frontmatter keys unchanged. ONLY add `skills:`
   and `permission:` if absent. If they already exist, leave them and log
   "skipped: already configured".
5. For each file, also ensure the body is untouched — compare byte length
   of body before and after; if it changed, abort this file.

## MUST NOT
- Do NOT invent skill names. Use names that exist in .agents/skills/
  post-M1b. If M1b has not run, use names as they currently exist.
- Do NOT commit.
- Do NOT touch files outside .agents/agents/.

## Response
Per-file summary: file name + "added skills list + ACL" | "skipped
(already configured)" | "TODO comment inserted". Cap: 400 words.
```

**Main-thread validation:** `git diff .agents/agents/` shows only frontmatter changes; body byte lengths unchanged; no invalid skill names.

---

# Phase 3 — Docs consolidation

## D1 — Deprecate old plans + refresh top-level docs

- **Agent:** general-purpose · **Model:** sonnet
- **Writes files:** Yes — `docs/archive/`, `README.md`, `CLAUDE.md`
- **Depends on:** M1 complete (so the plan references a real state)
- **Parallel with:** M3, M4, M5, M6

**Prompt:**
```
Consolidate documentation inside /mnt/c/memory/my-harness/.

## 1. Archive prior plans

Move (git mv) these files into /mnt/c/memory/my-harness/docs/archive/:
- multi-container-harness-plan.md
- multi-agent-cli-harness-plan.md
- multi-agent-plugins-marketplace-plan.md

After moving, prepend a 3-line deprecation banner at the top of each
archived file:

```
> **DEPRECATED 2026-04-21** — superseded by
> [harness-v1-master-plan.md](harness-v1-master-plan.md) and
> [../harness-v1-agent-tasks.md](../harness-v1-agent-tasks.md). Kept for historical reference only.
```

Do NOT delete the archived files. Do NOT commit.

## 2. Refresh /mnt/c/memory/my-harness/CLAUDE.md

Write a CLAUDE.md at the marketplace repo root (overwrite if exists —
Read first, preserve any "session-specific" sections you find).

Content skeleton:

```markdown
# CLAUDE.md — my-harness (marketplace)

This is the MARKETPLACE repo. Sibling sandbox runtime lives at
../harness-sandbox. Parent workspace CLAUDE.md covers cross-repo scope.

## This repo's scope

Skills, agents, commands, plugin manifests consumed by Claude Code,
OpenCode, and Gemini CLI. Do NOT add Dockerfile or docker-compose here —
those belong in ../harness-sandbox.

## Canonical source

All skills, agents, commands live under .agents/. Per-CLI directories
(.claude/, .opencode/, .gemini/) are symlinks or thin wrappers.

## Skill naming

Every skill directory carries a workflow prefix: stdd-, orchestrate-,
review-, general-. Flat, no nesting.

## Agent frontmatter

Every agent file carries both a Claude Code skills: list AND an OpenCode
permission.skill ACL. Preserve both when editing.

## Plans

Master plan: [docs/harness-v1-master-plan.md](docs/harness-v1-master-plan.md)
Task definitions: [docs/harness-v1-agent-tasks.md](docs/harness-v1-agent-tasks.md)
Archived plans: [docs/archive/](docs/archive/)
```

## 3. Refresh /mnt/c/memory/my-harness/README.md

Should state: what the repo is (the marketplace), how to install per
CLI (Claude Code marketplace, OpenCode plugin, Gemini extension), where
the sandbox lives (sibling repo), link to docs/harness-v1-master-plan.md.

Cap: 400 words. Preserve any existing sections about tooling or credits
by reading the current README first.

## MUST NOT
- Do NOT commit.
- Do NOT touch files under .agents/, .claude/, .opencode/, .gemini/.

Response: list of files moved/written; confirmation that deprecation
banners were added. Cap: 200 words.
```

**Main-thread validation:** banners present verbatim; two new docs link from CLAUDE.md and README.md; archived files are under `docs/archive/` and not at `docs/` root.

---

# Phase 4 — Validation

## V1 — Symlink + manifest validation (automated)

- **Agent:** Explore · **Model:** haiku
- **Writes files:** No
- **Depends on:** All of Phase 1, 2, 3 complete

**Prompt:**
```
Validate the final state of the harness repos. Return a pass/fail report.
Do not modify files.

For /mnt/c/memory/my-harness/:
1. For each symlink under .claude/, .opencode/, .gemini/extensions/*/,
   verify that `readlink -f` resolves to a real path inside .agents/.
2. Parse .claude-plugin/plugin.json with `jq .`. Report valid/invalid.
3. Parse every gemini-extension.json under .gemini/extensions/*/ with
   `jq .`. Report valid/invalid.
4. Parse opencode.jsonc (remove // line comments first with `sed`, then
   `jq .`). Report valid/invalid.
5. Grep .claude/commands/ for `.toml` files — must report "none".
6. Grep .agents/skills/ for directories without the four allowed prefixes
   — must report "none" if M1b ran.
7. For every .md file in .agents/agents/, check that frontmatter contains
   BOTH `skills:` and `permission:` keys. Report any missing.

For /mnt/c/memory/harness-sandbox/:
8. Parse docker-compose.yml, docker-compose.services.yml,
   docker-compose.graphiti.yml each via `docker compose -f <file> config
   --quiet` (Bash). Report exit status per file.
9. Check bin/harness is parseable via `bash -n bin/harness`. Report.
10. Verify .env.example has non-empty lines and does NOT contain any real
    API key (grep for patterns `sk-ant-...`, `AIza...`, `sk-...`). Report.

Return a single markdown table: check number, description, status
(PASS/FAIL/WARN), detail. Cap: 600 words.

Rules: Bash allowed for jq/docker compose/sed/grep. No file writes.
```

**Main-thread validation:** all PASS or WARN is acceptable; any FAIL triggers a main-thread fix pass, not a re-delegation.

---

## V2 — Cross-CLI smoke test (manual, Daniel runs)

Not a subagent task. Main thread hands Daniel the exact commands after V1 passes. Commands include:
- `claude` at the marketplace repo; check that `/stdd-feat-workflow` appears in `/help`.
- `opencode` at same; check that the same command appears.
- `gemini` with the research extension loaded; check that research-scoped skills are listed.
- Then inside the sandbox: `harness up`, `harness shell`, `claude /stdd-feat-workflow test`.

Main thread prints the exact command sequence; Daniel runs; screenshots or success/failure goes back to main thread.

---

# Manual (non-delegated) steps

- `git remote add origin <URL>` + `git push -u origin main` for harness-sandbox. Requires Daniel to create the GitHub repo.
- Filling `.env` from `.env.example`.
- Moving the workspace from `/mnt/c/memory/` to WSL ext4.
- Registering each CLI's marketplace entry for the first time.

---

# Execution log (main thread keeps this current)

| Phase | Task | Launched at | Status | Notes |
|---|---|---|---|---|
| 0 | R1 | — | pending | |
| 0 | R2 | — | pending | |
| 0 | R3 | — | pending | |
| 0 | R4 | — | pending | |
| 1 | S1 | — | pending | |
| 1 | S2 | — | pending | |
| 1 | S3 | — | pending | |
| 1 | S4 | — | pending | |
| 1 | S5 | — | pending | |
| 2 | M1 | — | pending | |
| 2 | M1b | — | conditional | may be skipped if no unprefixed skills |
| 2 | M2 | — | pending | |
| 2 | M3 | — | pending | |
| 2 | M4 | — | pending | |
| 2 | M5 | — | pending | |
| 2 | M6 | — | pending | |
| 3 | D1 | — | pending | |
| 4 | V1 | — | pending | |
| 4 | V2 | — | manual | Daniel runs |
