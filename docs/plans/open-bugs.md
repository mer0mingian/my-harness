# Open Bugs

These bugs have been observed on the test agent workspace located in `/home/minged01/repositories/sta2e-agent-workspace/.`

Deploy a separate Opus agent to investigate each agents. Create a spec using specify skill for each issue, do not apply changes.

Have each subagent ask clarifying questions.

## Invalid Char in .harness.yml

Reading MCP configuration: /home/minged01/repositories/sta2e-agent-workspace/.harness.yml

+ ```
  local overrides: /home/minged01/repositories/sta2e-agent-workspace/.harness.local.yml
  File "/home/minged01/repositories/sta2e-agent-workspace/.harness.yml", line 37
  role: Marketplace — skills, agents, commands, plugin manifests
  ^
  SyntaxError: invalid character '—' (U+2014)
  [+] up 2/2
  ```

## Default to stony compose profile

- The wrapper **does not** support `--profile stony` for compose overlays.
- The build of the stony image is far too complicated. Add a tag for building the private image instead, let latest point to stony.
- harness up should support --profile private
- harness up should not need additional flags for cgc, litho, if they are configured to start from .harness.yml.
- consolidate the .env and .env.stony into one file. on non-corporate deployment of the sandbox, CA part should be ignored
- check if there is an overlap between .env.stony, .env. and .litho.toml, and remove it from the .env files

## Claude in workspace has weird agent yml files

```
~/repositories/sta2e-agent-workspace/.claude/agents$ ll
total 28
drwxr-xr-x 2 minged01 minged01 4096 May 13 22:43 ./
drwxr-xr-x 3 minged01 minged01 4096 May 13 22:43 ../
-rw-r--r-- 1 minged01 minged01    0 May 13 22:43 .gitkeep
-rw-r--r-- 1 minged01 minged01 2215 May 13 22:43 arch-specialist.yml
-rw-r--r-- 1 minged01 minged01 2148 May 13 22:43 dev-specialist.yml
-rw-r--r-- 1 minged01 minged01 2181 May 13 22:43 qa-specialist.yml
-rw-r--r-- 1 minged01 minged01 2307 May 13 22:43 review-specialist.yml
-rw-r--r-- 1 minged01 minged01 1762 May 13 22:43 test-specialist.yml
```

Agents are defined as md files. These seem to come from an outdated version of the matd plugin. Please

## Error on Claude Code startup on Host machine

```
 ~/repositories/sta2e-agent-workspace
  ⎿ SessionStart:startup says: Plugin hook error: /bin/sh: 1:
    /home/minged01/.claude/plugins/cache/superpowers-marketplace/superpowers/4.0.0/hooks/run-hook.cmd: not found
  ⎿ SessionStart:startup says: Plugin hook error: /bin/sh: 1:
    /home/minged01/.claude/plugins/cache/superpowers-marketplace/superpowers/4.0.0/hooks/run-hook.cmd: not found
```

Also claude seems to be configured to use outdated models!?!
