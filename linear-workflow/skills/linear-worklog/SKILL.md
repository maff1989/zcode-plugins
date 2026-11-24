---
name: linear-worklog
description: "Use whenever work touches a Linear issue, project, or initiative — including a Linear URL or <TEAM>-### identifier, a branch or commit naming Linear work, or a repository/PR whose work is tracked in Linear. Keeps the board true as work happens: comments on pushed commit ranges, PR opens and merges, releases, and publishes; moves status at verified milestones; files follow-ups for gaps; and reconciles merged work that was never closed. Use even when the user does not explicitly ask for a Linear update."
version: 1.4.1
author: linear-workflow contributors
license: MIT
compatibility: "Requires git, Python 3.10+, GitHub CLI (gh), npm, and the Linear MCP tools. The evidence script is read-only; all writes go through Linear MCP."
metadata:
  tags: [linear, worklog, delivery, accountability, mcp]
  related_skills: [qa]
---

# Linear Worklog

## When to Use

Any task where Linear work is in play:

- the user gives a Linear URL, `<TEAM>-###` identifier, or names a project/initiative;
- the working branch or a commit names a Linear issue (`<team>-353-...`, `<TEAM>-353`);
- a PR, release, tag, npm publish, or deploy belongs to tracked work;
- the user asks to reconcile a board, close merged work, or capture missed updates.

This is a standing rule, not an optional add-on. If commit/PR/release activity happened, the owning issue must say so before the turn ends. Do not wait to be asked.

For a read-only board review, do not use the write path: read the board, verify claims, and return the analysis. The `/linear-review` command is the read-only entry point. For filing a bug from conversational QA, use `qa`. This skill is for work that is being done and recorded.

## The One Rule

The board is a record of what is true now. A green card is a claim; the remote is the evidence.

A merged PR with an open card is a board defect. A Done card whose own done-when is unmet is a worse defect, because it hides risk. Fix both in the same pass that discovers them.

## Delegation

When implementation is delegated to subagents, the parent agent owns every Linear write. Subagents must not write to Linear — no comments, issues, status changes, project updates, or follow-up cards. They do not need to read it either; the parent hands off the card identifier, done-when, current status, and the user's rulings.

Why: the board is a single record with one writer. Parallel subagents writing directly race, duplicate comments, move statuses without the full context, and can publish internal detail on a public card. The parent holds the whole task, the cross-repo evidence, and the user's decisions.

Handoff requirements:

- Give each subagent its card identifier, branch name, done-when, and the exact report format.
- State explicitly: do not call Linear tools; do not move statuses; do not file cards.
- Require the report to carry branch, base, head SHA, commits, files changed, verification commands and results, evidence (txids, run URLs, error strings), and open items.
- On report, the parent writes the event comment, moves the status the evidence supports, and files follow-ups. A subagent's summary is not a worklog record.

## Resolve the Target First

Use this order:

1. An explicit issue URL or `<TEAM>-###` identifier in the request.
2. The current branch name: `git branch --show-current` → `<owner>/<team>-353-...` → `<TEAM>-353`.
3. A `<TEAM>-###` trailer in the commits being reported: `git log --format=%B <range>`.
4. A Linear issue or project link in the PR body.
5. The project named in the request.
6. `list_issues(query=<repo|package|title>)`, but only if the match is unambiguous.

Never guess a target. If the match is ambiguous, ask once and record the chosen target in the first comment. If no target exists, report the work in the final answer and ask which card should own it. Do not write to a random project.

Read the target before writing:

- `get_issue(id, includeRelations: true)` — done-when, due date, status, relations.
- `list_comments(issueId)` — the latest state and what has already been recorded.
- `list_issue_statuses(team)` and `list_issue_labels(team)` — only use names that exist.
- `get_project(projectId)` — target date and project state, if the work is project-level.

The issue's own done-when is the only legitimate source of Done. The due date and project target date are the roadmap source of truth.

## Available Scripts

- **`scripts/collect-evidence.py`** — a read-only snapshot of the facts a worklog comment needs: branch, head, base/merge-base, commits, working tree, PR, tag/release, package version, and npm dist-tags. It never writes to Linear.

Run it before writing the comment:

```bash
python3 scripts/collect-evidence.py --repo <path> [--issue TEAM-###] [--json]
```

Use `--json` when you want to hand the result to another tool. Use `--help` for the full interface.

## Detailed References

- Read [`references/linear-write-mechanics.md`](references/linear-write-mechanics.md) before the first Linear write in a session, or when a write is rejected, an attachment is dropped, or a description patch fails.
- Read [`references/evidence-recipes.md`](references/evidence-recipes.md) when the collector is unavailable, when a release asset needs verification, or when interpreting an odd PR/release/npm result.

## Status Rules

| Event | Status |
|---|---|
| Branch created or first commit pushed; work started | `Todo` → `In Progress` |
| PR opened or updated and verification is recorded | `In Progress` → `In Review` (if the team has that state) |
| PR merged, every done-when criterion true and verified on the remote | `Done` |
| PR merged, but a done-when criterion is still open | Stay `In Progress` or `In Review`; comment the open items |
| Done-when includes a consumer pin, release, or deploy | Do not close until that evidence exists, unless the user explicitly delegates it; record the delegation and name the owning cards |
| A Done card's criterion is found unmet | Reopen it; a green card suppresses the work an open one would expose |

Never mark `Done` for "code written". Done requires the card's own observation, on the remote, with a link. A local branch, a local test run, or a green build that has not produced the published artifact is not Done.

Default rulings:

- A PR merged into the default branch closes its linked issue in the same pass when the done-when is met.
- A port PR open against a draft base is `In Review`, not `Done`.
- A library card whose remaining criterion is consumer pinning may stay `Done` only when the pin is explicitly delegated in a comment naming the consumer cards.
- Target dates are accurate because the roadmap consumes them. When a description disagrees, fix the description, not the date.

## Done-When: Checklist or Subissues

A done-when item is either a live body checklist or a subissue, never both. Duplicate live representations drift. When subissues are used, the parent body either keeps the original checklist as the creation record or replaces it with a pointer to the child set; either way the body is not updated and the children are the live state.

### Choose the representation

| Shape | Use |
|---|---|
| 1 to 3 tightly coupled criteria, one evidence artifact, or a single short task | Body checklist |
| 3 or more independent criteria, multiple owners or teams, or a long-running card whose per-criterion progress matters | Subissues, one level deep |

Subissues are issues: they inherit the parent's team, priority, and project, they appear in project rollups, and they get their own identifiers and comments. That is the cost. Do not create them for documentary checks that share one artifact.

### If you use subissues

1. Keep the parent body's done-when as the original contract, or replace it with a pointer in the same edit that adds the mapping comment. Do not maintain it afterwards. For a new parent, write the pointer directly; do not duplicate the criteria.
2. Create the children in the parent's project and team. A criterion owned by another project is a linked issue (`relatedTo` or `blocks`), not a child. A cross-project child makes the parent's progress depend on work outside its scope.
3. Comment on the parent with the mapping: each done-when line, the child identifier that owns it, and the evidence the child must carry.
4. Each child carries one observation and its own evidence before `Done`. Do not mark a child done on a status click or a green build that has not produced the observation.
5. The parent's `Done` requires every child `Done` or explicitly waived in a comment. Do not rely on team automation. A team with `autoCloseParentIssues` and `autoCloseChildIssues` unset will not close the parent or children automatically. A sandbox check confirmed the parent stayed `Todo` after all four children were `Done`; the close was explicit.
6. Adding, removing, canceling, or reparenting a child is an amendment. Comment why and re-check the parent's done-when. A canceled child is a scope change, not evidence of completion.
7. One level only. A child with its own checklist is a sign the parent should be a project, not a card.

Set priority, assignee, and due date explicitly. In a pilot, the MCP created a child at priority 0 and unassigned even though the parent was High and assigned; the UI's inheritance did not apply through the tool. Team and project were correct because they were passed explicitly.

### Reading the set

- Create: `save_issue(team, project, parentId=<parent>, title, ...)`.
- Read: `list_issues(parentId=<parent>)`; `get_issue` returns `parentId` but not the children.
- Update: `save_issue(id, state=...)`.
- Remove: set `parentId` to null. The MCP has no delete or archive; canceling is a status, not a deletion.

### Pilot before converting

Do not convert existing cards wholesale. Try the representation on one card, record the mapping comment, and compare the board noise and the closure discipline before adopting it for a class of work.

## What to Log, and When

One comment per externally visible event, not per file edit or WIP commit.

1. **Pushed commit range / PR opened** — one comment with the branch, base, head SHA, PR URL, what changed, the verification commands and results, and what remains open.
2. **PR merged** — one comment with the PR number, merge/squash commit SHA, the final default-branch SHA, and the tag or release that contains it, if any. Close the issue in the same pass if its done-when is satisfied.
3. **Release / tag / npm publish / deploy** — one comment with the tag and commit, the workflow run URL and conclusion, the assets or package version, and what was verified on the published artifact, not just the build.
4. **Gap or out-of-scope work** — one comment plus a follow-up card in its owning project (see Follow-Up Cards), unless the user has said not to create cards.
5. **Project milestone** — a project status update via `save_status_update`, not a comment on every issue.
6. **Subagent report** — the parent turns the report into one event comment and the status move it supports; a subagent never writes to Linear.

Write the comment before ending the turn in which the event happened. Do not defer it to a future session, and do not rely on a GitHub integration to create the record: a PR that is not auto-linked is still work that happened.

## Follow-Up Cards

File a card when:

- the work is outside the issue's stated scope;
- a gap is discovered that no card owns;
- a consumer pin, verification, or release has no card.

### Classify the gap, then choose the home

A follow-up does not inherit its project from the card that discovered it. Classify the work first:

| Gap | Home |
|---|---|
| In scope, and the discovering project's done-when needs it | Same project |
| CI, build, release tooling, deployment, repo hygiene, developer workflow | The matching project under the internal engineering-operations initiative (or the workspace's equivalent) |
| A consumer pin, release, or deploy owned by another team | That team's project, cross-linked |
| A durable theme with no project | Propose a new project under the right initiative; ask the user once |

Before creating, search for an existing home: `list_issues(project=...)` for the likely project, then `list_projects` and `list_initiatives`. Never default to the current project because it is convenient. A card in the wrong project distorts project progress, hides the work from the team that should own it, and can make a roadmap project look gated by engineering debt it does not depend on. If two projects fit, ask the user once rather than guessing.

The workspace rule: an internal engineering-operations initiative exists precisely for work that "makes roadmap items true but is not itself public roadmap progress." Release, CI, deployment, and repo-hygiene gaps belong there, not on the roadmap project that surfaced them. Match the project's stated scope, not just the initiative name. If no project in that initiative covers the gap's discipline, propose a new project and ask; do not force the nearest one.

### Relationship, not dependency

- `relatedTo`: context only. Use it for a follow-up the discovering project can complete without.
- `blocks` / `blockedBy`: a real completion dependency. Use only when the other card's done-when cannot be met without this one, and say so in the body.
- If unsure, use `relatedTo`. Never add `blocks` to keep two cards near each other.

Record the home and the relationship in the follow-up body, and link the discovering card in the comment.

### Filing rules

- Status: `Todo` for a known gap, `Backlog` when it is not yet scheduled. Never `In Progress` on creation.
- Priority: the user's triage, not the priority of the card that discovered it.
- Done-when: an observation, not an action.
- Visibility: internal engineering projects may be private. Do not carry a public-facing label, an internal hostname, or customer data into one. When moving a card from a public project, re-check its labels and existing comments for public-safe content.

### Relocating a misfiled card

When a follow-up landed in the wrong place:

1. `save_issue(id, project=<home>)`. If the team changes, the identifier prefix changes, so fix every link that names the old identifier.
2. Re-read the issue; confirm project, team, identifier, labels, and relations.
3. Remove relations that imply a dependency the work does not have (`removeRelatedTo`); keep `relatedTo` when it is useful context.
4. Comment on the moved card and on the discovering card with the new home and why.
5. Do not move a real blocker without re-evaluating the blocking relation first.

If the user has said not to create cards, put the proposed title, body, and intended home in the comment and stop. The gap is still recorded; the decision to file it stays visible.

## Project Updates and Dates

- Project and issue target dates are the roadmap source of truth.
- If a description contradicts its target date, fix the description with `patch`. Name the target date and the reason in the status update. Never move the date to match prose.
- Post a project status update at a release, milestone, or completion: shipped, open, target. Keep it factual and link the evidence.

## Idempotency and Read-Back

Before writing, `list_comments` and search for the SHA, tag, PR URL, or run URL. If it is already recorded, do not duplicate it. If your own earlier comment is materially wrong, update it by ID or append a correction; never edit someone else's comment.

After writing, read back:

- `get_issue` for status, attachments, and the updated state.
- `list_comments` for the new comment.
- `get_project` after a description patch.

Read the write response's `warnings`; link attachments can be silently dropped when rate-limited. Retry in small batches, then re-read and diff the attachments against what you intended.

## Public Safety

A card carrying a public-facing label may be rendered publicly. Keep comments factual, public-safe, and free of secrets, tokens, internal hostnames, and personal data. Redact anything that exposes internal infrastructure when the card is public. When in doubt, write as if the reader is outside the organization.

## Templates

### Work event

```text
**<date>: <event>.**

- <branch/PR/tag + links>
- Changed: <...>
- Verified: <command, result, run URL>
- Open: <...>
```

### Merge

```text
**<date>: merged.**

- PR #<n> squash-merged as [`<sha>`](<commit url>); `<default branch>` is now `<sha>`.
- Contained in `<tag>` (<release url>).
- Open on this card: <...>
```

### Release

```text
**<date>: `<tag>` published.**

- Tag `<tag>` at `<sha>`; run <id> <conclusion>.
- Assets: <count> including `SHA256SUMS`; `<artifact>` reports `<version>`.
- Verified: <checksum, command>.
- Open: <...>
```

### Follow-up card

```text
## Symptom
...

## Anchors
- <path:line>, <run id>, <PR>

## Observed vs expected
...

## Scope / why pre-existing
...

## Home
- Project: <project> (<initiative>)
- Relationship: <relatedTo|blocks> <card> (<why>)

## Done when
- <observation, not action>
```

## Gotchas (from real reconciliations)

- A PR merged but the card is still open — close it in the same pass.
- A card is Done while its own consumer pin, release, or deploy criterion is unmet — reopen, or delegate explicitly and record it.
- A release card is closed on a green build while the release body or operator announcement is still open — keep it in progress.
- A port PR is done and open, but its base is a draft PR — `In Review`, not `Done`.
- Two commits on one issue produce two comments — one comment per event is enough; use the range.
- A comment claims a test count or a green run that was never re-run — quote the run URL or the test output.
- A description is rewritten to stay current — append a comment instead. The one exception is an explicit user ruling that the description is wrong.
- A GitHub integration did not auto-link the PR — add the link or comment yourself. The work still happened.
- A subagent wrote its own Linear comment — the board now has two writers; reconcile it, and restate the no-Linear rule in every handoff.
- A follow-up was filed in the current project because it was convenient — the project now looks responsible for engineering debt it does not depend on. Move it to the owning project and cross-link.
- A follow-up carries `blocks` while the discovering project can complete without it — downgrade to `relatedTo`.
- A card moved to another team kept its old identifier in comments — fix the links, not the history.
- A card updates both a body checklist and subissues for the same criteria, and the two disagree — the body is the creation record; update only the children and record amendments in comments.
- A subissue lives in another project, so the parent's progress now depends on work outside its scope — reparent it or replace it with a linked issue.
- A parent was closed while a child was still open because team auto-close was assumed — check the children; do not assume team auto-close.

## Quick Checklist

- [ ] Target issue resolved, not guessed
- [ ] Current status and done-when read
- [ ] Done-when representation chosen: checklist or subissues, not both
- [ ] If subissues: mapping comment present, and the parent closes only after every child is Done or waived
- [ ] Delegated work reported to the parent; subagents made no Linear writes
- [ ] `scripts/collect-evidence.py` run, or the manual recipes followed
- [ ] Event comment written with links and evidence
- [ ] Status moved only to what the evidence supports
- [ ] Follow-up classified and placed in its owning project/initiative, not by convenience
- [ ] Relations reflect dependency, not proximity
- [ ] Moved cards re-read, re-linked, and commented on both sides
- [ ] Read-back confirms the write
- [ ] No duplicate, no secret, no body rewrite
