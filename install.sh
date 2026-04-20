#!/usr/bin/env bash
# Install/update my-harness and wire it into Claude Code, OpenCode, and Gemini CLI.
#
# Source of truth: a single clone of the repo (default ~/.my-harness).
# Each CLI gets symlinks pointing into <src>/.agents/{skills,agents,commands}.
#
# Usage:
#   bash install.sh                                    # interactive
#   bash install.sh --scope user --clis all            # user scope, all CLIs
#   bash install.sh --scope project --clis claude,opencode
#   bash install.sh --scope user --src-dir ~/code/my-harness
#   bash install.sh --scope user --ssh                 # clone via SSH (needs keys)
#
# Remote one-liner:
#   bash <(curl -fsSL https://raw.githubusercontent.com/mer0mingian/my-harness/main/install.sh) --scope user --clis all

set -euo pipefail

REPO_URL_HTTPS="https://github.com/mer0mingian/my-harness.git"
REPO_URL_SSH="git@github.com:mer0mingian/my-harness.git"
DEFAULT_SRC_DIR="${HOME}/.my-harness"

SCOPE=""
CLIS=""
SRC_DIR="${DEFAULT_SRC_DIR}"
USE_SSH=0
TS="$(date +%Y%m%d-%H%M%S)"

log()  { printf '\033[36m[my-harness]\033[0m %s\n' "$*"; }
warn() { printf '\033[33m[my-harness] warn:\033[0m %s\n' "$*" >&2; }
die()  { printf '\033[31m[my-harness] error:\033[0m %s\n' "$*" >&2; exit 1; }

usage() {
  sed -n '2,14p' "$0" | sed 's/^# \{0,1\}//'
  exit "${1:-0}"
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --scope)    SCOPE="${2:-}"; shift 2 ;;
    --scope=*)  SCOPE="${1#*=}"; shift ;;
    --clis)     CLIS="${2:-}"; shift 2 ;;
    --clis=*)   CLIS="${1#*=}"; shift ;;
    --src-dir)  SRC_DIR="${2:-}"; shift 2 ;;
    --src-dir=*) SRC_DIR="${1#*=}"; shift ;;
    --ssh)      USE_SSH=1; shift ;;
    --https)    USE_SSH=0; shift ;;
    -h|--help)  usage 0 ;;
    *)          die "unknown flag: $1 (try --help)" ;;
  esac
done

# ---- Interactive fallback --------------------------------------------------
if [[ -z "$SCOPE" ]]; then
  printf 'Install scope? [u]ser (~/.claude, ~/.config/opencode, ~/.gemini) or [p]roject (./.claude, ./.opencode, ./.gemini): '
  read -r ans
  case "$ans" in
    u|U|user)    SCOPE="user" ;;
    p|P|project) SCOPE="project" ;;
    *)           die "invalid scope" ;;
  esac
fi
[[ "$SCOPE" == "user" || "$SCOPE" == "project" ]] || die "--scope must be 'user' or 'project'"

if [[ -z "$CLIS" ]]; then
  printf 'Which CLIs? comma list of [claude,opencode,gemini] or "all" [all]: '
  read -r ans
  CLIS="${ans:-all}"
fi
[[ "$CLIS" == "all" ]] && CLIS="claude,opencode,gemini"

# ---- Clone or update source of truth --------------------------------------
SRC_DIR="${SRC_DIR/#\~/$HOME}"
if [[ "$USE_SSH" -eq 1 ]]; then
  REPO_URL="$REPO_URL_SSH"
else
  REPO_URL="$REPO_URL_HTTPS"
fi

if [[ -d "$SRC_DIR/.git" ]]; then
  log "updating source at $SRC_DIR"
  git -C "$SRC_DIR" pull --ff-only
elif [[ -e "$SRC_DIR" ]]; then
  die "$SRC_DIR exists but is not a git repo; move it aside or pass --src-dir"
else
  log "cloning $REPO_URL into $SRC_DIR"
  git clone --depth 1 "$REPO_URL" "$SRC_DIR"
fi

AGENTS_SRC="$SRC_DIR/.agents"
[[ -d "$AGENTS_SRC/skills" && -d "$AGENTS_SRC/agents" && -d "$AGENTS_SRC/commands" ]] \
  || die "$AGENTS_SRC is missing skills/agents/commands — bad source?"

# ---- Scope → target roots -------------------------------------------------
if [[ "$SCOPE" == "user" ]]; then
  CLAUDE_ROOT="${HOME}/.claude"
  OPENCODE_ROOT="${HOME}/.config/opencode"
  GEMINI_ROOT="${HOME}/.gemini"
else
  CLAUDE_ROOT="$(pwd)/.claude"
  OPENCODE_ROOT="$(pwd)/.opencode"
  GEMINI_ROOT="$(pwd)/.gemini"
fi

# ---- Symlink helper --------------------------------------------------------
# link_into <target_link> <source_dir>
#   - ensures parent dir exists
#   - if target is already a symlink to source, no-op
#   - if target is a broken symlink, remove it
#   - if target is a real dir/file, back up as .bak.<ts>
link_into() {
  local target="$1" source="$2"
  mkdir -p "$(dirname "$target")"
  if [[ -L "$target" ]]; then
    local current
    current="$(readlink "$target")"
    if [[ "$current" == "$source" ]]; then
      log "ok: $target -> $source"
      return
    fi
    if [[ ! -e "$target" ]]; then
      rm "$target"
    else
      warn "replacing symlink $target (was -> $current)"
      rm "$target"
    fi
  elif [[ -e "$target" ]]; then
    warn "backing up existing $target -> ${target}.bak.${TS}"
    mv "$target" "${target}.bak.${TS}"
  fi
  ln -s "$source" "$target"
  log "linked: $target -> $source"
}

install_claude() {
  log "Claude Code → $CLAUDE_ROOT"
  link_into "$CLAUDE_ROOT/skills"   "$AGENTS_SRC/skills"
  link_into "$CLAUDE_ROOT/agents"   "$AGENTS_SRC/agents"
  link_into "$CLAUDE_ROOT/commands" "$AGENTS_SRC/commands"
}

install_opencode() {
  # OpenCode convention: singular `agent/` and `command/`.
  log "OpenCode → $OPENCODE_ROOT"
  link_into "$OPENCODE_ROOT/skills"  "$AGENTS_SRC/skills"
  link_into "$OPENCODE_ROOT/agent"   "$AGENTS_SRC/agents"
  link_into "$OPENCODE_ROOT/command" "$AGENTS_SRC/commands"
}

install_gemini() {
  # Gemini CLI reads TOML commands from <root>/commands; only .gemini.toml
  # files in the shared commands dir are relevant to it.
  log "Gemini CLI → $GEMINI_ROOT"
  link_into "$GEMINI_ROOT/commands" "$AGENTS_SRC/commands"
}

IFS=',' read -ra SELECTED <<<"$CLIS"
for cli in "${SELECTED[@]}"; do
  case "$(echo "$cli" | tr '[:upper:]' '[:lower:]' | xargs)" in
    claude)   install_claude   ;;
    opencode) install_opencode ;;
    gemini)   install_gemini   ;;
    "")       ;;
    *)        warn "unknown CLI: $cli (skipped)" ;;
  esac
done

log "done. scope=$SCOPE  source=$SRC_DIR"
log "update later with:  git -C $SRC_DIR pull"
