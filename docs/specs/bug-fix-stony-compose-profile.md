# Bug Fix Spec: Default to Stony Compose Profile (Cluster)

**Status:** Ready for implementation
**Date:** 2026-05-14
**Scope:** `harness-sandbox/` only (wrapper + compose + env restructure; hard cutover)
**Target branch:** `feat/default-stony-compose-profile` in `/home/minged01/repositories/harness-workplace/harness-sandbox`
**Backward compatibility:** None. Hard cutover. Old `.env.stony`, `docker-compose-stony.yml`, and undocumented flags are deleted.

---

## 1. Bug Cluster Summary

This spec resolves four tightly coupled defects that all surface around the corporate ("stony") sandbox profile:

| # | Defect                                                                                                                                     | Severity |
|---|--------------------------------------------------------------------------------------------------------------------------------------------|----------|
| 1 | `bin/harness` does not support a `--profile` CLI flag; corporate setup is implicit (filename-driven) and undocumented in `usage()`.        | High     |
| 2 | `docker-compose-stony.yml` is deprecated but still on disk and still referenced in `CORPORATE_SETUP.md` / `bin/harness`; sources of truth fork. | High     |
| 3 | Configuration is duplicated across `.env`, `.env.stony.example`, and `litho.toml.example` (PROJECT_NAME, DEEPWIKI_OUTPUT, SSL vars, etc.).  | High     |
| 4 | `.harness.yml` already implicitly enables `cgc`/`litho`/`deepwiki` compose profiles via `mcp_servers.*.profile`, but there is no top-level `compose_profiles:` key and no `default-build` selector — corporate vs personal is filename-detected, not declared. | High     |

The fix introduces explicit declarative configuration in `.harness.yml`, restructures `.env` to secrets-only, removes all deprecated stony artefacts, and surfaces `--corporate` / `--private` flags in the wrapper.

---

## 2. Glossary (terminology used throughout this spec)

| Term         | Meaning                                                                                                                                                            |
|--------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **stony**    | Synonym for **corporate**. Build/run variant that bakes the Cloudflare Zero Trust CA cert into the image. `:latest` and `:stony` tags both point at this build.    |
| **private**  | Personal / non-corporate variant. No CA cert installed. Image tagged `:private`. Used by users who do not need to talk to Stepstone-internal hosts.                |
| **corporate** | User-facing CLI synonym for `stony`. `harness build --corporate` and `harness build --stony` are equivalent.                                                       |
| **profile**  | Two senses, disambiguated below:                                                                                                                                   |
|              | - *Build profile* (`stony` / `private`): chooses which image to build/run.                                                                                          |
|              | - *Compose profile* (`cgc`, `litho`, `docs`, `full`): docker-compose `profiles:` field, gates optional services. |

---

## 3. Current Behaviour vs Desired Behaviour

### 3.1 Issue #1 — Wrapper CLI lacks `--profile` / `--corporate` / `--private`

**Current behaviour** (`bin/harness`, lines 50-66):

```bash
# Auto-detects which env file to use, prefers .env.stony over .env
if [[ -f "${HARNESS_SANDBOX_DIR}/.env.stony" ]]; then
  ENV_FILE="${HARNESS_SANDBOX_DIR}/.env.stony"
  echo "Using corporate configuration: .env.stony"
elif [[ -f "${HARNESS_SANDBOX_DIR}/.env" ]]; then
  ENV_FILE="${HARNESS_SANDBOX_DIR}/.env"
fi
```

- The choice of corporate vs personal is **filename-driven** (presence of `.env.stony`).
- `usage()` documents `harness up`, `harness shell`, `harness down`, etc., but **no `--profile`, no `--corporate`, no `--private` flag**.
- `CORPORATE_SETUP.md` line 148 advertises `bin/harness --profile cgc up`, but the wrapper does not parse `--profile`. The command silently falls through to `up` and ignores the flag.
- There is no way to *build* the image from the wrapper. Users must memorise:
  ```bash
  docker build -t harness-sandbox:stony --build-arg CA_CERT_CONTEXT_PATH=cert/cloudflare.crt .
  docker build -t harness-litho:stony -f litho/Dockerfile --build-arg CA_CERT_CONTEXT_PATH=cert/cloudflare.crt .
  ```

**Desired behaviour:**

```text
harness build [--corporate|--stony|--private]  Build agent + litho images
harness up    [--corporate|--stony|--private]  Start sandbox with the selected build
harness down                                    Stop and remove all containers
harness shell                                   Open agent container shell
harness cgc shell                               Open cgc container shell
harness docs analyze                            Run litho
harness init [path]                             Scaffold workspace from template
harness help                                    Show usage
```

Resolution order for which build variant to use (highest precedence first):
1. Explicit CLI flag: `--corporate` / `--stony` / `--private`.
2. `default-build:` field in the project's `.harness.yml`.
3. Repo-level fallback: `stony` (per user decision: `:latest == stony`).

### 3.2 Issue #2 — `docker-compose-stony.yml` is deprecated but still present

**Current behaviour:**
- `harness-sandbox/docker-compose-stony.yml` exists (155 lines).
- File header says: *"⚠️ DEPRECATION NOTICE (2026-05-10) — kept for reference only."*
- All corporate SSL env vars and cert mounts have already been migrated into `docker-compose.yml` via conditional `${VAR:-}` substitution (see `docker-compose.yml` lines 160-175, 277-310).
- `CORPORATE_SETUP.md` lines 234-246 explicitly call it out as deprecated *but kept*.
- `.env.stony.example` still exists (375+ lines) and duplicates most of `.env.example`.

**Desired behaviour:**
- `docker-compose-stony.yml` **deleted** from disk.
- `.env.stony.example` **deleted** from disk.
- All corporate vs personal switching driven by `${AGENT_IMAGE:-harness-sandbox:stony}` and `${CLOUDFLARE_BUNDLE_PATH:-/dev/null}` in the single `docker-compose.yml`.
- A single `.env.example` (secrets only) covers both build variants.

### 3.3 Issue #3 — Configuration duplication across `.env`, `.env.stony`, `litho.toml`

**Current behaviour:**

| Variable / key             | Defined in `.env.example` | Defined in `.env.stony.example` | Defined in `litho.toml.example` | Used by |
|----------------------------|---------------------------|----------------------------------|---------------------------------|---------|
| `PROJECT_NAME`             | line 103                  | line 81                          | -                               | compose, wrapper |
| `PROJECT_PATH`             | line 104                  | line 82                          | -                               | (legacy, unused) |
| `WORKING_DIR`              | line 105                  | line 83                          | -                               | (legacy, unused) |
| `MARKETPLACE_PATH`         | line 106                  | line 84                          | -                               | (legacy, unused) |
| `ANTHROPIC_API_KEY`        | line 216                  | line 290 (as `${CLAUDE_API_KEY}`) | -                              | agent runtime |
| `CLAUDE_API_KEY`           | -                         | line 286                         | -                               | corporate agent |
| `LITHO_LLM_API_KEY`        | -                         | (derived)                        | line 38 (`api_key_env`)         | litho runtime |
| `DEEPWIKI_OUTPUT`          | line 367                  | line 327                         | line 20 (`output_path`)         | litho |
| `DEEPWIKI_WATCH`           | line 376                  | line 328                         | -                               | litho |
| `RTK_ENABLED`              | line 428                  | line 340                         | -                               | agent |
| `RTK_TELEMETRY_DISABLED`   | line 437                  | line 341                         | -                               | agent |
| `CORPORATE_MODE`           | -                         | line 117                         | -                               | (boolean, redundant once build flag exists) |
| `CLOUDFLARE_BUNDLE_PATH`   | -                         | line 152                         | -                               | compose |
| `SSL_CERT_FILE` (+ 7 more) | -                         | lines 179-186                    | -                               | compose env passthrough |

Three problems compound:
1. Same key in two `.env*` files — drift inevitable.
2. Same value expressible in `litho.toml` and `.env` — ambiguous precedence (currently `.env` wins via the `LITHO_LLM_API_KEY` indirection, but `output_path` directly conflicts).
3. Non-secrets (`PROJECT_NAME`, `DEEPWIKI_WATCH`, `RTK_ENABLED`) live in `.env`, which is git-ignored and per-user, so team-shared configuration leaks into per-user state.

**Desired behaviour** (per user decision):

| File              | Contains                                                                                                                                        | Tracked? |
|-------------------|-------------------------------------------------------------------------------------------------------------------------------------------------|----------|
| `.env`            | **Secrets only.** API keys, personal tokens, bearer tokens. Nothing else.                                                                       | gitignored |
| `litho.toml`      | Litho / deepwiki runtime config (model names, exclusions, output path). Unchanged in scope.                                                     | per-project |
| `.harness.yml`    | All other harness config: `default-build`, `compose_profiles`, `mcp_servers`, `plugins`, `speckit`, and project-shared non-secret env values.   | committed |

`.harness.yml` wins on overlap. If a non-secret value also appears in `.env`, the wrapper warns and ignores the `.env` value.

### 3.4 Issue #4 — No explicit `compose_profiles` or `default-build` in `.harness.yml`

**Current behaviour** (`bin/harness`, lines 244-266):

The wrapper *already* derives compose profiles from `.harness.yml`, but only by walking `mcp_servers.<name>.profile`. There is no top-level `compose_profiles:` list, so the user cannot say "always start with `cgc`+`litho`" without enabling an MCP server they may not want.

**Desired behaviour:**

`.harness.yml` gains two top-level keys:

```yaml
# .harness.yml
default-build: stony           # stony | corporate (synonym) | private

compose_profiles:               # explicit list, OR'd with profiles derived from mcp_servers
  - cgc
  - litho

mcp_servers:                    # unchanged
  codegraphcontext:
    enabled: true
    profile: cgc

plugins:                        # unchanged
  - matd
  - harness-cgc-skill
  - harness-deepwiki-skill

speckit:
  init: true
```

Resolution rules (wrapper, in `harness up`):
1. Start with profiles from `compose_profiles:`.
2. Union with profiles from enabled `mcp_servers.*.profile`.
3. Deduplicate.
4. Emit `--profile X` for each unique value to `docker compose`.

---

## 4. Root Cause Analysis

| # | Symptom                                                  | Root cause                                                                                                                                                  |
|---|----------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 1 | `bin/harness --profile X up` silently ignored.           | The case statement in `bin/harness` (line 231) dispatches on `$1` directly. Flags are never parsed; documentation in `CORPORATE_SETUP.md` describes an aspirational interface, not the shipped one. |
| 2 | Two ways to run corporate (`-f docker-compose-stony.yml` vs filename detection of `.env.stony`). | Mid-migration state. The 2026-05-10 deprecation note exists but the file was kept "just in case" and never deleted, leaving two competing code paths.       |
| 3 | Same value defined in 2-3 places.                        | `.env.stony.example` was created as a copy of `.env.example` with corporate values overlaid; nobody factored out the shared keys. `litho.toml` was added later as a third path for litho-specific values. |
| 4 | Corporate vs personal is filename-driven.                | The wrapper was written before `.harness.yml` was introduced. The two configuration models — filename-detected env vs declarative YAML — were never reconciled. |

---

## 5. Proposed Changes

### 5.1 `bin/harness` wrapper script

**File:** `/home/minged01/repositories/harness-workplace/harness-sandbox/bin/harness`

#### 5.1.1 Add flag parser (before the `case "${CMD}"` block)

After the existing auto-detection block, before line 228 (`CMD="${1:-help}"`), insert a flag parser:

```bash
# ============================================================================
# Flag parsing (--corporate / --stony / --private)
# ============================================================================
# Build/runtime variant. Order of precedence:
#   1. Explicit CLI flag (--corporate / --stony / --private)
#   2. default-build: field in .harness.yml
#   3. Repo default: "stony"
BUILD_VARIANT=""

POSITIONAL=()
while (( $# )); do
  case "$1" in
    --corporate|--stony) BUILD_VARIANT="stony"; shift ;;
    --private)           BUILD_VARIANT="private"; shift ;;
    --)                  shift; POSITIONAL+=("$@"); break ;;
    *)                   POSITIONAL+=("$1"); shift ;;
  esac
done
set -- "${POSITIONAL[@]}"
```

#### 5.1.2 Add `parse_harness_yml_top_level()` helper

New function that reads `default-build:` and `compose_profiles:` from `.harness.yml`:

```bash
# Returns: "<build_variant>|<space-separated-profiles>"
# e.g.    "stony|cgc litho"
# Falls back to "stony|" if .harness.yml absent or keys missing.
parse_harness_yml_top_level() {
  local project_dir="$1"
  local harness_yml="${project_dir}/.harness.yml"

  if [[ ! -f "$harness_yml" ]]; then
    echo "stony|"
    return 0
  fi

  python3 <<'PY' "$harness_yml"
import sys, yaml
try:
    with open(sys.argv[1]) as f:
        data = yaml.safe_load(f) or {}
except Exception:
    print("stony|")
    sys.exit(0)
db = (data.get("default-build") or "stony").strip().lower()
if db == "corporate":
    db = "stony"
profiles = data.get("compose_profiles") or []
if not isinstance(profiles, list):
    profiles = []
print(f"{db}|{' '.join(str(p) for p in profiles)}")
PY
}
```

#### 5.1.3 Replace `.env.stony` auto-detection (lines 50-66)

Delete the `.env.stony` priority block. Replace with:

```bash
ENV_FILE=""
if [[ -f "${HARNESS_SANDBOX_DIR}/.env" ]]; then
  ENV_FILE="${HARNESS_SANDBOX_DIR}/.env"
fi

if [[ -n "$ENV_FILE" ]]; then
  set -a
  # shellcheck disable=SC1091
  source "$ENV_FILE"
  set +a
fi
```

#### 5.1.4 Rewrite the `up` case

Replace the existing `up)` block (lines 232-315) with logic that:

1. Resolves `BUILD_VARIANT` (flag > yaml > "stony").
2. Computes `AGENT_IMAGE` and `LITHO_IMAGE` from `BUILD_VARIANT`:
   - `stony` → `harness-sandbox:stony`, `harness-litho:stony`
   - `private` → `harness-sandbox:private`, `harness-litho:private`
3. If the chosen image is missing locally:
   - For `private`: auto-build it (see 5.1.5).
   - For `stony`: fail with a clear pointer to `harness build --corporate`.
4. Computes the profile set by unioning `compose_profiles:` with `mcp_servers.*.profile`.
5. Exports `AGENT_IMAGE` and `LITHO_IMAGE` so `docker compose` interpolates them.
6. Invokes `docker compose --env-file .env <profile flags> up -d`.

Skeleton:

```bash
up)
  require_docker
  check_anthropic_auth
  cd "${HARNESS_SANDBOX_DIR}"

  YML_PARSED=$(parse_harness_yml_top_level "$PROJECT_DIR")
  YML_DEFAULT_BUILD="${YML_PARSED%%|*}"
  YML_PROFILES="${YML_PARSED#*|}"

  : "${BUILD_VARIANT:=${YML_DEFAULT_BUILD:-stony}}"

  case "$BUILD_VARIANT" in
    stony)   AGENT_IMAGE="harness-sandbox:stony"  ; LITHO_IMAGE="harness-litho:stony"  ;;
    private) AGENT_IMAGE="harness-sandbox:private"; LITHO_IMAGE="harness-litho:private";;
    *) echo "ERROR: unknown build variant '$BUILD_VARIANT'" >&2; exit 2 ;;
  esac
  export AGENT_IMAGE LITHO_IMAGE

  # Auto-build private image if missing
  if [[ "$BUILD_VARIANT" == "private" ]] && ! docker image inspect "$AGENT_IMAGE" >/dev/null 2>&1; then
    echo "Private image $AGENT_IMAGE missing; building..."
    "$0" build --private
  fi
  if [[ "$BUILD_VARIANT" == "stony" ]] && ! docker image inspect "$AGENT_IMAGE" >/dev/null 2>&1; then
    echo "ERROR: corporate image $AGENT_IMAGE not built." >&2
    echo "       Run: $(basename "$0") build --corporate" >&2
    exit 1
  fi

  # Compose profile flags: union of compose_profiles + mcp_servers profiles
  MCP_SERVER_PROFILES=$(parse_mcp_servers "$PROJECT_DIR")
  ALL_PROFILES=""
  for p in $YML_PROFILES; do
    ALL_PROFILES+=" $p"
  done
  for sp in $MCP_SERVER_PROFILES; do
    p="${sp#*:}"
    [[ -n "$p" ]] && ALL_PROFILES+=" $p"
  done
  # Deduplicate
  ALL_PROFILES=$(printf '%s\n' $ALL_PROFILES | awk '!seen[$0]++' | xargs -r)
  PROFILE_FLAGS=""
  for p in $ALL_PROFILES; do PROFILE_FLAGS+=" --profile $p"; done

  COMPOSE_CMD="docker compose"
  [[ -n "$ENV_FILE" ]] && COMPOSE_CMD+=" --env-file $ENV_FILE"
  echo "Build variant : $BUILD_VARIANT (agent=$AGENT_IMAGE litho=$LITHO_IMAGE)"
  echo "Compose profiles:$PROFILE_FLAGS"
  $COMPOSE_CMD $PROFILE_FLAGS up -d
  ;;
```

#### 5.1.5 Add `build` subcommand

New case in the dispatcher:

```bash
build)
  require_docker
  cd "${HARNESS_SANDBOX_DIR}"

  : "${BUILD_VARIANT:=stony}"

  case "$BUILD_VARIANT" in
    stony)
      # 1. Verify cloudflare-cert-installer repo is on host
      CERT_INSTALLER_REPO="${CLOUDFLARE_CERT_INSTALLER:-${WORKSPACE_ROOT}/cloudflare-cert-installer}"
      if [[ ! -f "${CERT_INSTALLER_REPO}/cloudflare.crt" ]]; then
        echo "ERROR: cloudflare-cert-installer not found." >&2
        echo "       Expected: ${CERT_INSTALLER_REPO}/cloudflare.crt" >&2
        echo "       Clone from: ssh://git@stash.stepstone.com:7999/zd/cloudflare-cert-installer.git" >&2
        echo "       Or set CLOUDFLARE_CERT_INSTALLER=/path/to/repo and retry." >&2
        exit 1
      fi
      # 2. Stage cert + installer into build context
      cp "${CERT_INSTALLER_REPO}/cloudflare.crt"               cert/cloudflare.crt
      cp "${CERT_INSTALLER_REPO}/cloudflare-cert-installer.sh" cert/cloudflare-cert-installer.sh
      # 3. Build agent + litho with CA cert AND tag :latest := :stony
      docker build -t harness-sandbox:stony -t harness-sandbox:latest \
        --build-arg CA_CERT_CONTEXT_PATH=cert/cloudflare.crt .
      docker build -t harness-litho:stony -t harness-litho:latest \
        -f litho/Dockerfile \
        --build-arg CA_CERT_CONTEXT_PATH=cert/cloudflare.crt .
      ;;
    private)
      # No cert; uses cert/.placeholder default
      docker build -t harness-sandbox:private .
      docker build -t harness-litho:private -f litho/Dockerfile .
      ;;
    *) echo "ERROR: unknown build variant '$BUILD_VARIANT'" >&2; exit 2 ;;
  esac
  ;;
```

> Note on "install for all supported systems": the corporate Dockerfile already runs `update-ca-certificates` (Debian-family). The build copies the installer script into the build context so it can also be executed inside the image during build for parity with the host installer's "configure curl/pip/npm/git/node" steps. The Dockerfile may need to invoke `cloudflare-cert-installer.sh --all` after the cert copy — out of scope for this spec; track as a follow-up if image-side coverage is incomplete.

#### 5.1.6 Update `usage()`

Replace the help text (lines 76-119) to document:

- `harness build [--corporate|--private]`
- `harness up [--corporate|--private]`
- All other commands accept `--corporate`/`--private` but only `up` and `build` act on it.
- Remove all references to `.env.stony`.
- Add a line: `Build/profile selection: .harness.yml default-build (override with --corporate/--private)`.

### 5.2 docker-compose files

**File:** `/home/minged01/repositories/harness-workplace/harness-sandbox/docker-compose.yml`

Required edits:
1. Change default of `AGENT_IMAGE` from `harness-sandbox:base` to `harness-sandbox:stony` (line 115): `${AGENT_IMAGE:-harness-sandbox:stony}`.
2. Add `${LITHO_IMAGE:-harness-litho:stony}` to the litho service definition (find current literal image: tag in the `litho:` service block).
3. Delete all comment references to `.env.stony` and `docker-compose-stony.yml` (lines 162-175, 277-310 retain functionality but the comments must point at `.harness.yml` / `harness build` instead).
4. Remove the `--profile docs` legacy alias if it was added solely for stony parity; keep only `cgc`, `litho`, `full`.

**File to delete:** `/home/minged01/repositories/harness-workplace/harness-sandbox/docker-compose-stony.yml`

### 5.3 `.env` restructuring (secrets only)

**File:** `/home/minged01/repositories/harness-workplace/harness-sandbox/.env.example`

After cutover, `.env.example` contains **only secrets**. Move every non-secret out.

| Variable                    | Action                                                                                                                                              |
|-----------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------|
| `ANTHROPIC_API_KEY`         | KEEP in `.env` (secret).                                                                                                                              |
| `CLAUDE_API_KEY`            | KEEP in `.env` (secret). Replaces the `.env.stony`-only variant.                                                                                      |
| `LITHO_LLM_API_KEY`         | KEEP in `.env` (secret). Defaults to `ANTHROPIC_API_KEY` if unset (compose-side `${LITHO_LLM_API_KEY:-${ANTHROPIC_API_KEY}}`).                         |
| `BITBUCKET_PERSONAL_TOKEN`  | KEEP in `.env` (secret).                                                                                                                              |
| `CONFLUENCE_PERSONAL_TOKEN` | KEEP in `.env` (secret).                                                                                                                              |
| `JIRA_PERSONAL_TOKEN`       | KEEP in `.env` (secret).                                                                                                                              |
| `AWS_BEARER_TOKEN_BEDROCK`  | KEEP in `.env` (secret).                                                                                                                              |
| `PROJECT_NAME`              | DELETE from `.env`. Auto-detected by wrapper; can be set in `.harness.yml` if override needed.                                                        |
| `PROJECT_PATH`              | DELETE from `.env`. Unused since RT-003 single-mount.                                                                                                 |
| `WORKING_DIR`               | DELETE from `.env`. Unused.                                                                                                                           |
| `MARKETPLACE_PATH`          | DELETE from `.env`. Unused.                                                                                                                           |
| `WORKSPACE_ROOT`            | DELETE from `.env`. Auto-detected by wrapper.                                                                                                         |
| `CORPORATE_MODE`            | DELETE. Redundant; `default-build:` now drives this.                                                                                                  |
| `CLOUDFLARE_BUNDLE_PATH`    | DELETE from `.env`. Not needed when cert is baked into image. Compose's `/dev/null` fallback covers the legacy mount.                                 |
| `SSL_CERT_FILE` (+ 7 more)  | DELETE from `.env`. Now hard-coded in compose as conditional `${VAR:-}`; corporate image bakes the cert path into the trust store anyway.             |
| `DEEPWIKI_OUTPUT`           | DELETE from `.env`. Owned by `litho.toml.output_path`.                                                                                                |
| `DEEPWIKI_WATCH`            | DELETE from `.env`. Move to `.harness.yml` under a new `litho:` section (or keep in `litho.toml`).                                                    |
| `RTK_ENABLED`               | DELETE from `.env`. Move to `.harness.yml` under a new `tooling:` section.                                                                            |
| `RTK_TELEMETRY_DISABLED`    | DELETE from `.env`. Move to `.harness.yml`.                                                                                                           |
| `AWS_PROFILE`               | KEEP in `.env`. Not strictly a secret but per-user.                                                                                                   |
| `AWS_DEFAULT_REGION`        | MOVE to `.harness.yml` under `tooling:`.                                                                                                              |
| `BITBUCKET_URL`, `JIRA_URL`, `CONFLUENCE_URL` | MOVE to `.harness.yml` (team-shared, non-secret URLs).                                                                              |
| `BITBUCKET_DEFAULT_PROJECT` | MOVE to `.harness.yml`.                                                                                                                               |
| `AGENT_IMAGE`, `LITHO_IMAGE` | DELETE from `.env`. Set by the wrapper after resolving `BUILD_VARIANT`.                                                                              |

Resulting `.env.example` after cutover is roughly 30 lines (down from 510): one section per secret with a one-line description.

### 5.4 `.harness.yml` schema (additions)

**File:** `/home/minged01/repositories/harness-workplace/harness-sandbox/workspace-template/.harness.yml`
(also update `harness-sandbox/.harness.yml.example`)

Add the following top-level keys:

```yaml
# Build variant used by `harness up` and `harness build` when no CLI flag is passed.
# Values:
#   stony     — Corporate build with Cloudflare CA cert (alias: corporate). Tag :stony, :latest.
#   private   — Personal build without corporate cert. Tag :private.
default-build: stony

# Compose profiles that always start, on top of those implied by enabled mcp_servers.
# Final set = compose_profiles ∪ {profile for each enabled mcp_servers.*.profile}
compose_profiles:
  - cgc
  - litho

# Non-secret runtime configuration moved out of .env
tooling:
  rtk:
    enabled: true
    telemetry_disabled: true
  aws:
    default_region: eu-west-1

# Team-shared service URLs (non-secret; tokens stay in .env)
services:
  bitbucket:
    url: https://bitbucket.stepstone.com
    default_project: ""
  jira:
    url: https://jira.stepstone.com
  confluence:
    url: https://confluence.stepstone.com

# Litho documentation tuning (overrides litho.toml for harness-managed knobs)
litho:
  watch: true
```

Schema rules:
- `default-build` must be exactly one of `stony`, `corporate`, `private`. The wrapper normalises `corporate` to `stony`.
- `compose_profiles` is a list of strings; unknown profile names are passed verbatim to `docker compose` (which will warn).
- Keys under `tooling:`, `services:`, `litho:` are passed into the container as env vars via a wrapper-generated `.harness.env` file (see 5.5 below) so existing compose `env_file:` semantics keep working.

### 5.5 Wrapper-generated `.harness.env`

To pass non-secret `.harness.yml` values into the container without re-introducing duplication in `.env`, the wrapper writes a transient `.harness.env` file (gitignored, regenerated on every `harness up`) that compose loads via a second `--env-file`:

```bash
$COMPOSE_CMD --env-file .env --env-file .harness.env $PROFILE_FLAGS up -d
```

`.harness.env` is created by a new helper function `materialise_harness_env()` that flattens `.harness.yml.tooling`, `.harness.yml.services`, and `.harness.yml.litho` into uppercase `KEY=value` lines (e.g. `RTK_ENABLED=true`, `BITBUCKET_URL=https://...`, `DEEPWIKI_WATCH=true`).

Add `.harness.env` to `harness-sandbox/.gitignore`.

---

## 6. Files to Delete

Hard-delete these in the cutover commit:

| Path                                                                                                       | Reason                                                                                |
|------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------|
| `harness-sandbox/docker-compose-stony.yml`                                                                 | Deprecated since 2026-05-10; functionality fully merged into `docker-compose.yml`.    |
| `harness-sandbox/.env.stony.example`                                                                       | Duplicates `.env.example`; corporate-vs-personal now driven by `default-build:`.      |
| `harness-sandbox/.env.stony` (if present in any developer working copy)                                    | Replaced by single `.env`.                                                            |
| `harness-sandbox/litho/Dockerfile.old`                                                                     | Pre-unified-Dockerfile artefact, no longer referenced.                                |
| `harness-sandbox/litho/Dockerfile.stony`                                                                   | Replaced by unified `litho/Dockerfile` with `CA_CERT_CONTEXT_PATH` build arg.         |
| `harness-sandbox/litho/DOCKERFILE_REFACTOR_NOTES.md`                                                       | Historical commentary on the unification; archive to `.analysis/` if needed.          |
| `harness-sandbox/litho/PATTERN_COMPARISON.md`                                                              | Same as above.                                                                        |
| `harness-sandbox/litho/BUILD_VERIFICATION.md`                                                              | Same as above.                                                                        |
| `harness-sandbox/MIGRATION-CORPORATE-SETUP.md` (if present anywhere; referenced by `docker-compose-stony.yml` header) | Migration is complete after this spec lands.                                  |
| `harness-sandbox/verify-corporate-setup.sh`                                                                | Re-evaluate: if its checks are unique, fold into `harness build --corporate` post-build verification; otherwise delete. Default: delete. |

Documentation edits (not deletions):
- `harness-sandbox/CORPORATE_SETUP.md` — rewrite for the new CLI; remove all `.env.stony` references; replace manual `docker build` commands with `harness build --corporate`.
- `harness-sandbox/README.md` — update quick-start to the new flag-driven flow.
- `harness-sandbox/CLI_USAGE.md` — re-document `up`, `build`, `--corporate`, `--private`, `.harness.yml` schema.

---

## 7. Migration Strategy — Hard Cutover

This is a breaking change. No legacy paths preserved.

### 7.1 Commit order (single feature branch, single PR recommended)

1. **Commit 1 — schema & wrapper:** Update `bin/harness` with flag parser, `build` subcommand, `parse_harness_yml_top_level`, new `up` logic. Update `workspace-template/.harness.yml` and `.harness.yml.example` with `default-build` + `compose_profiles` + `tooling`/`services`/`litho` blocks.
2. **Commit 2 — compose & env restructure:** Update `docker-compose.yml` defaults. Rewrite `.env.example` to secrets-only. Add `.harness.env` to `.gitignore`.
3. **Commit 3 — deletions:** Remove all files listed in Section 6.
4. **Commit 4 — docs:** Rewrite `CORPORATE_SETUP.md`, `README.md`, `CLI_USAGE.md`. Add a top-level migration note in `harness-sandbox/CHANGELOG.md` (or `CLAUDE.md`).

### 7.2 Developer migration steps (for each user with an existing checkout)

```bash
cd harness-workplace/harness-sandbox

# 1. Pull the new branch
git fetch && git checkout feat/default-stony-compose-profile

# 2. Delete local .env.stony if it exists
rm -f .env.stony

# 3. Migrate secrets to the new .env
#    (keep ANTHROPIC_API_KEY, CLAUDE_API_KEY, *_PERSONAL_TOKEN, AWS_BEARER_TOKEN_BEDROCK)
#    Move BITBUCKET_URL, JIRA_URL, etc. to your project's .harness.yml

# 4. Add default-build to project .harness.yml
echo 'default-build: stony' >> /path/to/project/.harness.yml

# 5. Rebuild
bin/harness build --corporate     # or --private

# 6. Restart
bin/harness down
bin/harness up
```

### 7.3 No rollback path

Per user decision: no backward compatibility. If someone needs the old workflow they can check out the pre-cutover tag.

---

## 8. Validation Steps

After implementation, the following must all pass before merging.

### 8.1 Wrapper unit checks

```bash
# 1. Help text mentions new flags
bin/harness help | grep -E -- '--corporate|--private'   # expect matches

# 2. Unknown flag is rejected cleanly
bin/harness --bogus up                                   # expect: ERROR with usage()

# 3. Flag precedence over .harness.yml
cd /tmp && mkdir test-private && cd test-private
echo 'default-build: stony' > .harness.yml
bin/harness --private up                                 # expect: "Build variant: private"
```

### 8.2 Build matrix

```bash
# Corporate build (requires cloudflare-cert-installer repo at expected path)
bin/harness build --corporate
docker image inspect harness-sandbox:stony   >/dev/null && echo OK
docker image inspect harness-sandbox:latest  >/dev/null && echo OK
docker image inspect harness-litho:stony     >/dev/null && echo OK
docker image inspect harness-litho:latest    >/dev/null && echo OK

# Verify cert is in the image
docker run --rm harness-sandbox:stony ls -l /usr/local/share/ca-certificates/ \
  | grep -i cloudflare                                   # expect match

# Private build (no cert required)
bin/harness build --private
docker image inspect harness-sandbox:private >/dev/null && echo OK
docker run --rm harness-sandbox:private ls /usr/local/share/ca-certificates/ \
  | grep -i cloudflare                                   # expect NO match
```

### 8.3 Compose-profile resolution

```bash
cat > /tmp/test-proj/.harness.yml <<'YML'
default-build: stony
compose_profiles: [cgc]
mcp_servers:
  litho:
    enabled: true
    profile: litho
YML
cd /tmp/test-proj && bin/harness up 2>&1 | grep "Compose profiles"
# expect: "Compose profiles: --profile cgc --profile litho" (order may vary, both present)

# Deduplication: compose_profiles and mcp_servers both name "cgc"
cat > /tmp/test-proj/.harness.yml <<'YML'
default-build: stony
compose_profiles: [cgc, litho]
mcp_servers:
  codegraphcontext: { enabled: true, profile: cgc }
YML
cd /tmp/test-proj && bin/harness up 2>&1 | grep "Compose profiles"
# expect: each of cgc, litho appears exactly once
```

### 8.4 Deletion verification

```bash
test ! -e harness-sandbox/docker-compose-stony.yml      && echo "OK: stony compose removed"
test ! -e harness-sandbox/.env.stony.example            && echo "OK: stony env removed"
test ! -e harness-sandbox/litho/Dockerfile.old          && echo "OK"
test ! -e harness-sandbox/litho/Dockerfile.stony        && echo "OK"
grep -rn "docker-compose-stony" harness-sandbox/        # expect: no output
grep -rn "\.env\.stony"          harness-sandbox/       # expect: no output
grep -rn "CORPORATE_MODE"         harness-sandbox/      # expect: no output
```

### 8.5 End-to-end smoke

```bash
# In a project directory with a valid .harness.yml
bin/harness build --corporate
bin/harness up
bin/harness shell
# inside container:
curl -I https://bitbucket.stepstone.com                  # expect: HTTP 2xx/3xx, no SSL error
echo "$ANTHROPIC_API_KEY" | head -c 8                    # expect: sk-ant- (from .env)
echo "$BITBUCKET_URL"                                    # expect: https://... (from .harness.env)
echo "$RTK_ENABLED"                                      # expect: true (from .harness.env)
exit
bin/harness down
```

### 8.6 Secrets hygiene

```bash
# .env must contain only secret-shaped keys
grep -vE '^(#|$|.*(KEY|TOKEN|SECRET|PASSWORD|API_KEY|BEARER|AWS_PROFILE)=)' \
  harness-sandbox/.env.example                           # expect: no output
```

---

## 9. Out of Scope

- Changes to `harness-tooling/` (skills, agents, commands).
- Changes to the litho Rust source or deepwiki-rs upstream.
- Re-evaluating `verify-corporate-setup.sh` behaviour beyond the delete-or-fold decision in Section 6.
- Adding non-Debian CA-installer coverage to the Dockerfile (tracked separately).
- Touching `sta2e-vtt-lite/` or `sta2e-vtt-lite-system/`.

---

## 10. References

- `harness-sandbox/bin/harness` — current wrapper.
- `harness-sandbox/docker-compose.yml` — current compose (already supports conditional corporate vars).
- `harness-sandbox/docker-compose-stony.yml` — deprecated overlay (to delete).
- `harness-sandbox/.env.example`, `.env.stony.example` — current env files.
- `harness-sandbox/workspace-template/.harness.yml`, `.harness.yml.example` — current schema.
- `harness-sandbox/CORPORATE_SETUP.md` — current corporate setup docs (to rewrite).
- `cloudflare-cert-installer/README.md` — cert installer reference.
- Prior bug fix: `docs/specs/bug-fix-invalid-char-harness-yml.md` (template `.harness.yml` em-dash fix; merge order: this spec depends on that one having landed since both touch the template).
