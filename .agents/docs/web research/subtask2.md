# Subtask2 Plugin Documentation

The `subtask2` plugin enhances OpenCode's command system with advanced chaining, state management, and deterministic agent orchestration.

## Core Features

### 1. `return` - Chaining Logic
The `return` field defines the actions the Orchestrator takes after a command completes.
- **Prompt Returns**: Regular text in the array is sent as a **real user message** to the session.
- **Command Returns**: Strings starting with `/` (e.g., `/daniels-feat-design`) execute immediately.
- **Order of Execution**: `return` prompts execute sequentially. If a subtask is in the middle of a `return` chain, the chain pauses until that subtask finishes.
- **Bypassing Defaults**: Defining a `return` prevents OpenCode from injecting the generic "please summarize" message, keeping the context window focused.

### 2. `loop` - Conditional Execution
Run a command until a human-readable condition is met.
- **Pattern**: Orchestrator-decides. The main agent reads the subtask's work and evaluates if the `until` condition is satisfied.
- **Syntax**: `loop: { max: 5, until: "tests pass" }`.
- **Response**: The main session responds with `<subtask2 loop="break"/>` or `<subtask2 loop="continue"/>`.

### 3. Named Results & Context
- **Capture (`{as:name}`)**: Append this to any command call to save its output.
- **Reference (`$RESULT[name]`)**: Injects the saved output of a previous command into the current prompt. Essential for passing file paths or specific decisions between agents.
- **Turn Context (`$TURN[n]`)**: Injects message history. 
    - `$TURN[5]` (Last 5 turns)
    - `$TURN[*]` (All turns)
    - `$TURN[:3]` (3rd turn from end)

### 4. Inline Overrides & Ad-hoc Tasks
- **Syntax**: Commands support inline overrides using `&&` separators: `/cmd {agent:build && model:opus && as:result} arguments`.
- **`/subtask`**: Use this to invoke a subagent without a markdown file. **Requirement**: Must have a space between `/subtask` and `{`.
    - `/subtask {agent:daniels-spec-agent} Create the proposal`

## Implementation Patterns in SDD

### The "Controller" Pattern
A master command (`daniels-feat-workflow`) acts as a high-level state machine, using `return` prompts to present results to the user and wait for approval before manually triggering the next stage.

### The "Sequence" Pattern
Phase-specific commands (like `03-refine`) use the `return` array to delegate to specialized sub-agents (Architect -> Critical Thinker -> QA) in a deterministic chain, passing state via `$RESULT`.
