---
description: Review a Linear project or initiative read-only and produce an implementation strategy.
argument-hint: "<linear project URL, P-TEAM-id, or project name>"
skills: linear-worklog
---

Review the Linear project or initiative described by the user:

$ARGUMENTS

Follow the `linear-worklog` skill for target resolution, board reads, and status rules, but treat
this command as analysis only: do not write comments, create or update issues, move statuses, or
patch descriptions.

Read the board in one pass: use `list_issues` with an explicit `fields` list for board-wide facts,
and call `get_issue(includeRelations: true)` only for the cards whose relations change the answer.
Emit independent reads together rather than one per thought, and reuse each read.

Read the project, its issues, documents, and relations; verify the description's claims against
the workspace; and return the board-fact table, findings, and decision gates.
