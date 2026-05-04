# AI Developer Tools Installation Guide

Prerequisites: npm, python3, pip, uv

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
# Install via install script (no cargo needed)
curl -fsSL https://raw.githubusercontent.com/rtk-ai/rtk/master/install.sh | sh
# Or via Homebrew
brew install rtk
# Verify
rtk --version
# Update (re-run install script)
curl -fsSL https://raw.githubusercontent.com/rtk-ai/rtk/master/install.sh | sh
```

### 5. OpenSpecs (Spec-Driven Development)

```bash
# Install (required for OpenCode OpenSpec plugin)
npm install -g @fission-ai/openspec@latest
# Source: https://github.com/Fission-AI/OpenSpec?tab=readme-ov-file
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
sudo apt-get install wget gpg
wget -qO- https://releases.warp.dev/linux/keys/warp.asc | gpg --dearmor > warpdotdev.gpg
sudo install -D -o root -g root -m 644 warpdotdev.gpg /etc/apt/keyrings/warpdotdev.gpg
sudo sh -c 'echo "deb [arch=amd64 signed-by=/etc/apt/keyrings/warpdotdev.gpg] https://releases.warp.dev/linux/deb stable main" > /etc/apt/sources.list.d/warpdotdev.list'
rm warpdotdev.gpg
sudo apt update && sudo apt install warp-terminal

# Alternetive
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

---

## One-Line Update All

```bash
# npm tools
npm update -g @anthropic-ai/claude-code @google/gemini-cli @fission-ai/openspec opencode-ai skills codeburn

# pip tools
pip install --upgrade codegraphcontext

# RTK (install script)
curl -fsSL https://raw.githubusercontent.com/rtk-ai/rtk/master/install.sh | sh

# Warp (system package manager)
sudo apt update && sudo apt install warp-terminal
```
