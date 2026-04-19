# AI Developer Tools Installation Guide

Prerequisites: npm, python3, pip, uv, cargo (for Rust tools)

---

## Local Installation

### 1. Claude Code

```bash
# Install
npm install -g @anthropic-ai/claude-code
# Verify
claude --version
# Update
npm update -g @anthropic-ai/claude-code
```

### 2. Google Gemini CLI

```bash
# Install (stable)
npm install -g @google/gemini-cli@preview
# Or nightly: npm install -g @google/gemini-cli@nightly
# Verify
gemini --version
# Update
npm update -g @google/gemini-cli
```

### 3. OpenCode

```bash
# Install via npm
npm install -g opencode-ai
# Verify
opencode --version
# Update
npm update -g opencode-ai

# Alternative: Install script
curl -fsSL https://opencode.ai/install | bash
```

### 4. Rust Token Killer (RTK)

```bash
# Install (requires Rust)
cargo install --git https://github.com/rtk-ai/rtk
# Verify
rtk --version
# Update
cargo install --git https://github.com/rtk-ai/rtk --force
```

### 5. OpenSpecs (Spec-Driven Development)

```bash
# Install
npm install -g @fission-ai/openspec
# Initialize in project
openspec init
# Verify
openspec --version
# Update
npm update -g @fission-ai/openspec
```

### 6. CodeGraphContext

```bash
# Install via pip
pip install codegraphcontext
# Verify
codegraphcontext --version
# Update
pip install --upgrade codegraphcontext
```

### 7. haft (Skill Learning)

```bash
# Install skills CLI
npm install -g skills
# Install haft skill (all detected agents)
npx skills add m0n0x41d/haft
# Or globally
npx skills add m0n0x41d/haft -g
# Verify
npx skills ls
# Update
npx skills add m0n0x41d/haft
```

### 8. Warp (AI Terminal)

```bash
# Ubuntu/Debian
curl -L https://app.warp.dev/download?package=deb -o warp.deb && sudo dpkg -i warp.deb

# Verify
warp --version
# Update (via package manager)
sudo apt update && sudo apt install warp-terminal  # debian
```

### 9. CodeBurn (Token Analytics)

```bash
# Install
npm install -g codeburn
# Run without install
npx codeburn
# Verify
codeburn status
# Update
npm update -g codeburn
```

### 10. Graphiti (Knowledge Graph MCP)

```bash
# Install via npx (installer)
npx @hexmos/ipm i getzep/graphiti
# Or manually via pip
pip install graphiti
# Requires: Docker + Neo4j or FalkorDB
# See: https://github.com/getzep/graphiti
# Update
pip install --upgrade graphiti
```

---

## One-Line Update All

```bash
# npm tools
npm update -g @anthropic-ai/claude-code @google/gemini-cli @fission-ai/openspec opencode-ai skills codeburn

# pip tools  
pip install --upgrade codegraphcontext graphiti

# cargo tool
cargo install --git https://github.com/rtk-ai/rtk --force

# Warp (system package manager)
sudo apt update && sudo apt install warp-terminal
```
