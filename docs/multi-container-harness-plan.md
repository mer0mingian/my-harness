# Multi-container harness strategy

I want to build an automated software engineering harness. It not only depends on high discipline during specification of requested features, but also on high quality tooling.

## Tools to integrate

1. Nvidia OpenShell for isolation of a multi-agent sandbox (using community container with sandbox added)
2. Chloe inside the sandbox for multiplexing agent clis.
3. deepwiki-rs/litho for documentation of C4-architecture and automated updates
   1. Extension for C4 mermaid diagrams with skill
   2. Extension for drawio-diagrams from C4 by script
4. Automated workflow plugin installation inside the sandbox based on my personally defined workflows for all agents (this repo)
5. rtk (rust token killer) inside the sandbox for reduced token usage
6. Code Graph Context (graph-based code memory system) for remembering similar code usage
   1. requires independent db management, it needs to run outside of the sandbox and be available via mcp/web api
7. Haft service and MCP server for tracking open questions and engineering decisions within one repo
   1. requires independent db management, it needs to run outside of the sandbox and be available via mcp/web api
8. Special reflection hooks inside the workflows to improve code usage and create PRs on the plugin marketplace
   1. claude-reflect-system
   2. opencode-skill-evolution
9. Project-overlapping business knwoledge (graphiti)
   1. requires independent db management, it needs to run outside of the sandbox and be available via mcp/web api
   2. This can be my personal setup, i.e. dbs can run on my machine
10. token monitoring for the sandbox, e.g. by code burn
11. Integration of company Enterprise Architecture policies into Claude Code rules
