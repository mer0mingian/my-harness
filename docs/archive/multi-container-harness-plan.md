> **DEPRECATED 2026-04-21** — superseded by
> [../harness-v1-master-plan.md](../harness-v1-master-plan.md) and
> [../harness-v1-agent-tasks.md](../harness-v1-agent-tasks.md). Kept for historical reference only.

# Multi-container harness strategy

I want to build an automated software engineering harness. It not only depends on high discipline during specification of requested features, but also on high quality tooling.

## Tools to integrate

1. [Nvidia OpenShell](https://github.com/NVIDIA/OpenShell) for isolation of a multi-agent sandbox (using community container with sandbox added)
2. [Chloe](https://github.com/kevinedry/chloe) inside the sandbox for multiplexing agent clis.
3. [deepwiki-rs/litho](https://github.com/sopaco/deepwiki-rs) for documentation of C4-architecture and automated updates
   1. Extension for C4 mermaid diagrams with skill
   2. Extension for drawio-diagrams from C4 by script
4. Automated workflow plugin installation inside the sandbox based on my personally defined workflows for all agents (this repo)
5. [rtk (rust token killer)](https://github.com/rtk-ai/rtk) inside the sandbox for reduced token usage
6. [Code Graph Context](https://github.com/CodeGraphContext/CodeGraphContext) (graph-based code memory system) for remembering similar code usage
   1. requires independent db management, it needs to run outside of the sandbox and be available via mcp/web api
7. [Haft service and MCP server](https://github.com/m0n0x41d/haft) for tracking open questions and engineering decisions within one repo
   1. requires independent db management, it needs to run outside of the sandbox and be available via mcp/web api
8. Special reflection hooks inside the workflows to improve code usage and create PRs on the plugin marketplace
   1. [claude-reflect-system](https://github.com/haddock-development/claude-reflect-system)
   2. [opencode-skill-evolution](https://github.com/bigknoxy/opencode-skill-evolution)
9. Project-overlapping business knowledge ([graphiti](https://github.com/getzep/graphiti))
   1. requires independent db management, it needs to run outside of the sandbox and be available via mcp/web api
   2. This can be my personal setup, i.e. dbs can run on my machine
10. token monitoring for the sandbox, e.g. by [CodeBurn](https://github.com/getagentseal/codeburn)
11. Integration of company Enterprise Architecture policies into Claude Code rules


## Notes

There mentioned gemini cli sandbox for openshell can be found [here](https://github.com/NVIDIA/OpenShell-Community/tree/main/sandboxes/gemini).
