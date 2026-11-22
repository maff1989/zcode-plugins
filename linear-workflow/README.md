# Linear Workflow

ZCode plugin: the official Linear MCP server plus adapted `linear-project-strategy` and `qa`
skills for Linear-based project work.

## Contents

- `.mcp.json` — one `linear` HTTP MCP server at `https://mcp.linear.app/mcp`, read-write OAuth.
- `skills/linear-project-strategy` — board review, strategy, and sanctioned board-driving
  procedure, including its `references/` write-path and system-state verification notes.
- `skills/qa` — conversational bug filing, Linear first with a GitHub fallback.
- `commands/` — `/linear-review`, `/linear-capture`, and `/linear-qa`.

## Slash commands

- `/linear-review <project>` — read-only review and implementation strategy for a project or
  initiative.
- `/linear-capture <findings>` — capture unfiled work as Linear cards.
- `/linear-qa [description]` — conversational QA, filed to Linear with a GitHub fallback.

## Install

1. **Plugin Marketplace → Add → Add Plugin Marketplace**, and paste this repository's root
   directory (the directory containing `marketplace.json`).
2. **Personal → maff1989-plugins → Linear Workflow → Install**.
3. **Settings → MCP → `linear` → Open authorization**, then approve read-write access for the
   Linear workspace in the browser.
4. Start a new session. The Linear tools appear in the tool list under the plugin namespace; the
   skills refer to tool basenames such as `get_project`, `list_issues`, and `save_issue`, and the
   three slash commands appear in the `/` menu.

The bundled skills only take precedence when same-named user-scope skills are disabled. If your
ZCode install already provides those copies, turn them off in **Settings → Skills** so the
plugin's adapted versions load. The user-scope copies are left untouched.

## Authentication

OAuth is per host and per Linear workspace. Tokens refresh on a roughly 25-day window; a
`401 invalid_token` means re-authorize from **Settings → MCP**. No API key or token is stored in
this repository.

## Multiple workspaces

The plugin ships one server named `linear`. For a second workspace, add a user-scope HTTP MCP
server through **Settings → MCP → New MCP Server** (type HTTP) under a different name, for
example `linear-work`, with the same URL and OAuth settings. The equivalent configuration is:

```json
{
  "mcp": {
    "servers": {
      "linear-work": {
        "type": "http",
        "url": "https://mcp.linear.app/mcp",
        "oauth": {
          "type": "authorization_code",
          "clientName": "ZCode Linear Workflow",
          "scope": "read write"
        }
      }
    }
  }
}
```

ZCode isolates OAuth tokens by server name and URL, so the entries do not share an authorization
context. Authorize each one separately.

## Sharing with another host

Add this marketplace on the other host (repository URL or copied directory), install the plugin,
and complete the OAuth flow there. A headless host needs a browser or a forwarded callback for
the one-time authorization.

## Updating

Edit the source, bump `version` in `.zcode-plugin/plugin.json` and `marketplace.json`, then refresh
the marketplace and update the installed plugin in **Settings → Plugins**.
