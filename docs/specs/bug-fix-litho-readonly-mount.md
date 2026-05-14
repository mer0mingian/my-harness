# Bug Fix Spec: Litho Container Read-Only Mount Failure

**Status:** Ready for implementation
**Date:** 2026-05-14
**Scope:** docker-compose.yml mount configuration, .env PROJECT_NAME leak, wrapper pre-creation
**Story Points:** 3

---

## 1. Bug Description

The Litho service fails to start when using `harness up --profile litho` due to a read-only filesystem error when Docker attempts to create the mount point for the `.litho` cache directory.

### Symptoms

```
Error response from daemon: failed to create task for container: failed to create shim task: OCI runtime create failed: runc create failed: unable to start container process: error during container init: error mounting "/home/minged01/repositories/harness-workplace/sta2e-vtt-lite-system/.litho" to rootfs at "/workspace/.litho": create mountpoint for /workspace/.litho mount: make mountpoint "/workspace/.litho": mkdirat /var/lib/docker/rootfs/overlayfs/af931d74ef06c1806983f15dc3fcf3894ee065d9c7dd0b5f903070f3a87514bf/workspace/.litho: read-only file system
```

**Trigger:**
```bash
cd ~/repositories/sta2e-agent-workspace
harness up --profile litho
```

**Expected behavior:** Litho container starts successfully with read-only workspace and writable cache.

**Actual behavior:** Container creation fails with read-only filesystem error.

---

## 2. Root Cause Analysis

Docker's runc runtime attempts to create the mount point `/workspace/.litho` **inside the container's rootfs** before binding the host directory. This fails because `/workspace` is already mounted read-only by a previous volume declaration.

### The Conflicting Mount Configuration

File: `harness-sandbox/docker-compose.yml` (lines 382-401), `litho:` service:

```yaml
volumes:
  # (a) Whole workspace, READ-ONLY
  - ${WORKSPACE_ROOT:-..}:/workspace:ro

  # (b) Nested cache dir, READ-WRITE - target inside the read-only mount above
  - ${WORKSPACE_ROOT:-..}/${PROJECT_NAME:-project}/.litho:/workspace/.litho:rw
```

**Why this fails:**
1. Mount (a) binds the workspace as read-only to `/workspace`
2. Mount (b) attempts to bind `.litho` to `/workspace/.litho` (nested path)
3. Docker's runc needs to `mkdirat("/workspace/.litho")` in the container rootfs
4. The parent `/workspace` is already sealed by the read-only mount (a)
5. The kernel rejects the directory creation → OCI runtime error

**Why the agent service works:** The agent service mounts `/workspace` as `rw` (line 332-333), allowing Docker to auto-create nested mount targets.

### Secondary Defect: PROJECT_NAME Hardcoded in .env

`harness-sandbox/.env:82` hardcodes `PROJECT_NAME=sta2e-vtt-lite-system`. The wrapper at `bin/harness:52-57` sources this file with `set -a`, causing the env-file value to override the auto-detected project name from the invocation CWD.

**Impact:**
- User runs `harness up` from `~/repositories/sta2e-agent-workspace`
- Expected `PROJECT_NAME=sta2e-agent-workspace`
- Got `sta2e-vtt-lite-system` (wrong project)
- Affects container naming, cgc-index location, deepwiki output paths

---

## 3. Affected Components

### Files to Modify

1. **`harness-sandbox/docker-compose.yml`** (lines 382-401)
   - Litho service volume mounts need restructuring to avoid nested read-only conflict

2. **`harness-sandbox/.env`** (line 82)
   - Remove hardcoded `PROJECT_NAME=sta2e-vtt-lite-system`

3. **`harness-sandbox/bin/harness`** (after line 40, before compose up)
   - Add pre-creation of `.litho` cache directory

### Files to Clean (post-fix)

- `/home/minged01/repositories/harness-workplace/sta2e-vtt-lite-system/.litho` (root-owned residual directory)

---

## 4. Proposed Fix

### Fix A: Restructure Litho Volume Mounts (Primary)

**Recommended: Option A1 - Mount cache to sibling path**

Change `harness-sandbox/docker-compose.yml` litho `volumes:` block (lines 393-401):

**Before:**
```yaml
volumes:
  - ${WORKSPACE_ROOT:-..}:/workspace:ro
  - ${WORKSPACE_ROOT:-..}/${PROJECT_NAME:-project}/.litho:/workspace/.litho:rw
```

**After:**
```yaml
volumes:
  - ${WORKSPACE_ROOT:-..}:/workspace:ro
  - ${WORKSPACE_ROOT:-..}/${PROJECT_NAME:-project}/.litho:/litho-cache:rw
```

**Rationale:** Moves the cache directory to a sibling path outside `/workspace`, eliminating the nested-mount conflict entirely while preserving the read-only workspace guarantee.

**Additional changes required:**
- Update litho service `command:` (line 391) to reference `/litho-cache` instead of `/workspace/${PROJECT_NAME}/.litho`
- OR add symlink in Dockerfile from `/workspace/${PROJECT_NAME}/.litho` → `/litho-cache`

### Fix B: Remove PROJECT_NAME from .env (Required)

Delete line 82 from `harness-sandbox/.env`:

**Before:**
```bash
# Project-specific settings
PROJECT_NAME=sta2e-vtt-lite-system
```

**After:**
```bash
# Project-specific settings
# PROJECT_NAME is auto-detected by bin/harness from invocation CWD
# Override in project-local .env if needed, not here
```

**Rationale:** The sandbox-level `.env` is a template and must not pin a specific project. Let the wrapper's auto-detection (`bin/harness:13-40`) own the value.

### Fix C: Pre-create Cache Directory (Defense-in-depth)

Add to `harness-sandbox/bin/harness`, right before `docker compose up` invocation:

```bash
# Ensure litho cache directory exists with correct ownership
mkdir -p "${WORKSPACE_ROOT}/${PROJECT_NAME}/.litho"
```

**Rationale:** Ensures the host source directory exists and is user-owned (not root from failed Docker runs) before container startup.

### Fix D: Override WORKDIR for Litho Service (Required)

Add to `harness-sandbox/docker-compose.yml` litho service block (after `image:` line):

```yaml
container_name: harness-litho-${PROJECT_NAME:-default}

# Override Dockerfile WORKDIR to writable location (workspace is read-only)
# Litho doesn't need to cd into the project - it takes --project-path argument
working_dir: /tmp
```

**Root Cause:** The litho Dockerfile has `WORKDIR /workspace/project`, but the litho service mounts `/workspace` as read-only. During container initialization, Docker's runc attempts to create the working directory path, which fails with `mkdir /workspace/project: read-only file system`.

**Rationale:** Litho doesn't need to be in the project directory as its working directory - it takes `--project-path` as a command-line argument. Overriding to `/tmp` (or any writable location) allows the container to start while maintaining the read-only workspace mount.

**Additional benefit:** Adds `container_name` to match the naming pattern used by agent and cgc services.

---

## 5. Validation Steps

All checks must pass post-fix. Use rtk for all commands.

### Step 1: Clean Residual Root-Owned Directory

```bash
rtk sudo rm -rf /home/minged01/repositories/harness-workplace/sta2e-vtt-lite-system/.litho
# Expected: directory removed, no permission errors
```

### Step 2: Verify Environment Variable Resolution

```bash
cd ~/repositories/sta2e-agent-workspace
rtk bash -x ~/repositories/harness-workplace/harness-sandbox/bin/harness up --profile litho 2>&1 | rtk grep -E "WORKSPACE_ROOT|PROJECT_NAME" | rtk head
# Expected: PROJECT_NAME=sta2e-agent-workspace (or from .harness.yml metadata.name)
# Expected: WORKSPACE_ROOT=/home/minged01/repositories/harness-workplace
```

### Step 3: Validate Compose Configuration

```bash
cd ~/repositories/harness-workplace/harness-sandbox
WORKSPACE_ROOT=$(pwd)/.. PROJECT_NAME=sta2e-vtt-lite-system \
  rtk docker compose --profile litho config | rtk grep -A20 "litho:" | rtk head -40
# Expected: volumes section shows /litho-cache mount, no nested /workspace/.litho
```

### Step 4: Container Startup Test

```bash
cd ~/repositories/sta2e-agent-workspace
~/repositories/harness-workplace/harness-sandbox/bin/harness up --profile cgc --profile litho
rtk docker compose -p $(basename $PWD) ps litho
# Expected: State=Up/Running (not Created or Exited)
# Expected: No OCI runtime errors in output
```

### Step 5: Container Logs Check

```bash
rtk docker logs harness-litho-${PROJECT_NAME}
# Expected: Litho service output (help text or running state)
# Expected: No "read-only file system" errors
# Expected: No "mount failed" errors
```

### Step 6: Functional Validation

```bash
rtk docker exec harness-litho-${PROJECT_NAME} ls -la /workspace
# Expected: Read-only workspace mount visible

rtk docker exec harness-litho-${PROJECT_NAME} touch /litho-cache/probe
# Expected: File created successfully (writable cache)

rtk docker exec harness-litho-${PROJECT_NAME} ls -la /litho-cache/
# Expected: probe file exists, owned by container user
```

---

## 6. Implementation Order

Execute fixes in this sequence:

1. **Apply Fix B first** (remove PROJECT_NAME from .env)
   - Prevents incorrect project detection during testing
   
2. **Apply Fix A** (restructure volume mounts)
   - Core fix for the cache mount conflict
   
3. **Apply Fix D** (override WORKDIR in docker-compose.yml)
   - Prevents container init failure on read-only workspace
   
4. **Apply Fix C** (add cache pre-creation to wrapper)
   - Defense-in-depth to prevent permission issues

5. **Run validation steps 1-6** in order
   - Confirm each step passes before proceeding

6. **Test with both project directories**
   - From `~/repositories/sta2e-agent-workspace`
   - From `~/repositories/sta2e-vtt-lite-system`
   - Verify PROJECT_NAME auto-detection works for both

---

## 7. Acceptance Criteria

- [ ] Litho container starts successfully with `harness up` (default profiles include litho)
- [ ] No OCI runtime errors related to mount creation or WORKDIR
- [ ] Container named `harness-litho-${PROJECT_NAME}` (matches naming pattern)
- [ ] `/workspace` is mounted read-only in litho container
- [ ] `/litho-cache` is mounted read-write in litho container
- [ ] Container working directory is `/tmp` (not `/workspace/project`)
- [ ] `PROJECT_NAME` auto-detection works from any invocation directory
- [ ] `harness-sandbox/.env` does not contain hardcoded PROJECT_NAME
- [ ] `.litho` cache directory is user-owned (not root)
- [ ] All validation steps 1-6 pass
- [ ] Litho service can write to cache directory
- [ ] No residual root-owned directories remain

---

## 8. Rollback Plan

If the fix causes issues:

1. **Revert Fix A:**
   ```bash
   cd ~/repositories/harness-workplace/harness-sandbox
   rtk git checkout HEAD docker-compose.yml
   ```

2. **Revert Fix B:**
   ```bash
   rtk git checkout HEAD .env
   ```

3. **Revert Fix C:**
   ```bash
   rtk git checkout HEAD bin/harness
   ```

4. **Clean up test artifacts:**
   ```bash
   rtk sudo rm -rf */sta2e-*/.litho
   rtk docker compose down --remove-orphans
   ```

---

## 9. Related Documentation

- Mount conflict analysis: Root cause section above
- Docker bind mount behavior: https://docs.docker.com/storage/bind-mounts/
- OCI runtime spec: https://github.com/opencontainers/runtime-spec/blob/main/runtime.md
- Harness wrapper auto-detection: `harness-sandbox/bin/harness` lines 8-40

---

## 10. Future Improvements (Out of Scope)

These are noted but not part of this fix:

- Migrate litho configuration to use `.harness.yml` for cache path overrides
- Add validation hook to prevent nested read-only mount conflicts in compose files
- Document best practices for multi-container workspace mounts in harness docs
- Consider making `/workspace` path configurable per-service
