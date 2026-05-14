# Open Bugs

No open bugs at this time.

### Missing deepwiki/litho skills

The deepwiki/litho repository contains more skills than the ones integrated into our plugin here: /home/minged01/repositories/harness-workplace/harness-tooling/.agents/plugins/harness-deepwiki-skill/.claude-plugin/plugin.json
E.g:

- /home/minged01/repositories/harness-workplace/deepwiki-rs/assets/skill-litho/SKILL.md
- /home/minged01/repositories/harness-workplace/deepwiki-rs/.skills/ai-context-generator/SKILL.md
- /home/minged01/repositories/harness-workplace/deepwiki-rs/.ai-context/SKILL.md

Understand the setup of deepwiki/litho and extend our plugin by the skills required to operate deepwiki.
Make an assessment if the current integration by running deepwiki in a separate container attached to our sandbox is a good architectural choice. Consider that we are using the sandbox as a dev container and do not want it to be too heavy.

## Recently Resolved

All previously tracked bugs have been resolved and merged to `dev` branch:

1. **Litho container read-only mount failure** - Fixed nested mount conflict on harness up

   - Spec: [docs/specs/bug-fix-litho-readonly-mount.md](../specs/bug-fix-litho-readonly-mount.md)
   - Resolution: Moved litho cache to `/litho-cache` (sibling path), removed hardcoded `PROJECT_NAME`, added cache pre-creation
   - Story points: 3
2. **Invalid Char in .harness.yml** - Fixed em-dash characters in template

   - Spec: [docs/specs/bug-fix-invalid-char-harness-yml.md](../specs/bug-fix-invalid-char-harness-yml.md)
   - Resolution: Replaced 28 em-dash chars with ASCII hyphens
   - Story points: 1
3. **Default to stony compose profile** - Unified corporate/private build system

   - Spec: [docs/specs/bug-fix-stony-compose-profile.md](../specs/bug-fix-stony-compose-profile.md)
   - Resolution: Added `harness build --corporate/--private`, consolidated .env, deleted deprecated files
   - Story points: 13
4. **Wrong agent yml files** - Template shipped with .yml instead of .md

   - Spec: [docs/specs/bug-fix-wrong-agent-format.md](../specs/bug-fix-wrong-agent-format.md)
   - Resolution: Removed .yml files, added pre-commit hook, documented .md requirement
   - Story points: 2
5. **Claude startup errors** - Plugin path mismatch for all-my-skills

   - Spec: [docs/specs/bug-fix-claude-startup-errors.md](../specs/bug-fix-claude-startup-errors.md)
   - Resolution: Created .claude-plugin/plugin.json, fixed marketplace.json source path
   - Story points: 2

All fixes merged and pushed to origin/dev on 2026-05-14.
