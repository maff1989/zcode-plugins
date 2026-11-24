# ZCode plugins

A ZCode plugin marketplace for Linear workflows.

## Marketplace

- Marketplace name: `maff1989-plugins`
- Plugin: `linear-workflow` — the official Linear MCP server plus the worklog and QA workflows.

## Install

1. **Plugin Marketplace → Add → Add Plugin Marketplace**, and paste this repository's URL or a
   local checkout path.
2. **Personal → maff1989-plugins → Linear Workflow → Install**.
3. **Settings → MCP → `linear` → Open authorization**, then approve read-write access for the
   Linear workspace.
4. Start a new session so the plugin's skills, slash commands, and MCP tools load.

## Layout

```text
marketplace.json          # marketplace catalog
linear-workflow/          # the plugin
  .zcode-plugin/plugin.json
  .mcp.json               # Linear HTTP MCP server with OAuth
  commands/               # linear-review, linear-capture, linear-qa
  skills/                 # linear-worklog, qa
```

## Commands

- `/linear-review <project>` — read-only project review and implementation strategy.
- `/linear-capture <findings>` — capture unfiled work as Linear cards.
- `/linear-qa [description]` — conversational QA filed to Linear (GitHub fallback).

## License

MIT — see [LICENSE](LICENSE).
