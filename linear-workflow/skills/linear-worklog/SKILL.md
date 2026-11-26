---
name: linear-worklog
description: "Use whenever work touches a Linear issue, project, or initiative — including a Linear URL or <TEAM>-### identifier, a branch or commit naming Linear work, or a repository/PR whose work is tracked in Linear. Keeps the board true as work happens: comments on pushed commit ranges, PR opens and merges, releases, and publishes; moves status at verified milestones; files follow-ups for gaps; and reconciles merged work that was never closed. Use even when the user does not explicitly ask for a Linear update."
version: 1.5.2
author: linear-workflow contributors
license: MIT
compatibility: "Requires git, Python 3.10+, GitHub CLI (gh), npm, and the Linear MCP tools. The evidence script is read-only; all Linear writes go through the MCP."
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

## Review Posture

A review request is read-only unless the user says otherwise. State the posture at the start: "review only, no writes." Separate factual defects from new work:

- A stale relation, a status that contradicts the forge, or a description that contradicts its target date is a factual defect. Put the exact fix in the review as a proposed write, with the tool call and the values.
- A new gap or follow-up is a proposed card. Put the title, body, and home in the review.

If the user then asks for the worklog pass, apply the proposed writes and file the cards. Do not leave a known defect as prose that the next session has to rediscover.

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

## Concurrent Sessions and Other Writers

The user may run side conversations that also write to Linear. Treat another session's comment as a claim:

- Read it, follow its links, and verify the status and evidence it asserts.
- Do not skip a write because "it is already recorded" unless the existing comment carries the evidence the card's done-when needs.
- Never edit another writer's comment. Append a correction or a note naming what you verified.
- If the other session is still active on the card, do not race its status changes. Add a short note identifying the owning session and the state you observed, or wait.
- When two sessions could write the same card, the session that owns the current work owns the card. Say which session that is in the comment.

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

## Read in One Pass

Board-wide reads are a common source of noise and latency. Read once and reuse:

- For board facts, call `list_issues` once with an explicit `fields` list (for example `id`,
  `title`, `status`, `statusType`, `projectId`, `updatedAt`) and filter by `project` or `team`.
  Do not walk a board one `get_issue` at a time.
- `list_issues` does not return relations. Call `get_issue(id, includeRelations: true)` only for
  the cards whose relations change the answer; do not fetch every card to audit the graph.
- Emit independent reads in one turn — several tool calls together — rather than one read per
  thought. Reuse the results for the rest of the session; do not re-fetch an issue you already read.
- Read comments only for the target card and the cards you are about to write to.

## Available Scripts

- **`scripts/collect-evidence.py`** — a read-only snapshot of the facts a worklog comment needs: branch, head, base/merge-base, commits, working tree, PR, tag/release, package version, and npm dist-tags. It never writes to Linear.

  ```bash
  python3 scripts/collect-evidence.py --repo <path> [--issue TEAM-###] [--json]
  ```

  Run it before writing the comment. Use `--json` when you want to hand the result to another tool. Use `--help` for the full interface.

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

`In Progress` starts when the branch or worktree is created, or when a subagent is dispatched, not when the PR opens. A card that says `Todo` while an agent is working in a worktree misreports the active set.

Never mark `Done` for "code written". Done requires the card's own observation, on the remote, with a link. A local branch, a local test run, or a green build that has not produced the published artifact is not Done.

Default rulings:

- A PR merged into the default branch closes its linked issue in the same pass when the done-when is met.
- A port PR open against a draft base is `In Review`, not `Done`.
- A library card whose remaining criterion is consumer pinning may stay `Done` only when the pin is explicitly delegated in a comment naming the consumer cards.
- Target dates are accurate because the roadmap consumes them. When a description disagrees, fix the description, not the date.

### Merge claims and bulk notices

A merge notice is a pointer, not evidence. This holds for a single PR, for "all PRs merged", and for a handoff prompt that lists merges. Enumerate the PRs this session owns, query each one for `state`, `mergedAt`, `mergeCommit`, and `headRefOid`, and confirm the default branch contains the merge commit. A closed PR is not a merged PR. A PR with `REVIEW_REQUIRED` is not mergeable by the agent. If the claim and the forge disagree, correct the record and name the still-open PR before doing anything else.

After a bulk notice, check every card that the notice could have closed. Do not close a card because the notice was plural.

### Asking for a ruling

Do not ask an open question about a done-when, a status, or a scope change. Post a decision package on the card:

- The current text, quoted.
- Why it cannot be met as written, with the evidence.
- The proposed replacement, quoted.
- What moves to which card, if anything.
- Your recommendation, labelled as yours.
- The one question the user answers.

An unsatisfiable done-when is a definition defect, not a reason to close early or to rewrite the body silently.

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

### Closing a card must not orphan its outputs

Before `Done`, walk the card's outputs, not only its done-when. If the card produced a decision, a question, a follow-up, or a document promise that is not actioned, give it a home: a new card, an existing card, or an explicit waiver in the closing comment. Link the output and record the mapping. A card whose deliverable is a list of open decisions is not complete when the list exists; it is complete when every decision has an owner.

## What to Log, and When

One comment per externally visible event, not per file edit or WIP commit.

1. **Pushed commit range / PR opened** — one comment with the branch, base, head SHA, PR URL, what changed, the verification commands and results, and what remains open.
2. **PR merged** — one comment with the PR number, merge/squash commit SHA, the final default-branch SHA, and the tag or release that contains it, if any. Close the issue in the same pass if its done-when is satisfied.
3. **Release / tag / npm publish / deploy** — one comment with the tag and commit, the workflow run URL and conclusion, the assets or package version, and what was verified on the published artifact, not just the build.
4. **Gap or out-of-scope work** — one comment plus a follow-up card in its owning project (see Follow-Up Cards), unless the user has said not to create cards.
5. **Project milestone** — a project status update via `save_status_update`, not a comment on every issue.
6. **Subagent report** — the parent turns the report into one event comment and the status move it supports; a subagent never writes to Linear.

Write the comment before ending the turn in which the event happened. Do not defer it to a future session, and do not rely on a GitHub integration to create the record: a PR that is not auto-linked is still work that happened.

## Parked Work and Handoffs

A session can end with work that is not an event yet: an unpushed branch, a held PR, a release waiting on a publisher, or a decision waiting on the user. Before ending the turn, post a resume block on the owning card:

- Branch, head SHA, worktree path, and whether it is on a remote.
- What is done and verified, with the command or URL.
- The exact next observation, and who owns it (agent or user).
- The blocker, if any, and what must not be touched.
- The date of the checkpoint.

This is a comment, not a status change. It makes the card the source of the handoff. A handoff prompt is then assembled from the cards plus a fresh repo read, never from conversation memory alone.

A handoff prompt carries: repo SHAs and worktree state, the board's open set with each card's gate, the merges and releases since the last handoff with their SHAs, the rules that bind the next session, the do-not-redo list, and one ordered next action per batch. Every claim in it is read in the session that writes it.

## Reconcile at the Wave Boundary

An event comment keeps one card true. It does not keep the project true. Run a reconciliation sweep at every wave boundary: when the last known PR merges, before a handoff prompt, before ending a turn with no work in flight, and whenever the user asks "what is left" or "is Linear up to date". Do not write "the board is current" from memory.

The sweep, in order:

1. Re-read every open card in the project, not just the ones touched this session.
2. Re-read every card touched this session, including Done ones, and check its outputs: decisions, questions, follow-ups, and document promises. An open decision with no card is a gap.
3. Search the repositories for claims the work invalidated: version pins, "not adopted", "TODO", tool names, and README promises. A stale claim is a card or a fix, not a note.
4. List cards in adjacent projects whose titles contain the work's nouns (package, tool, version, surface) and check whether this session's work closed them.
5. Record the sweep on the project as a status update or a comment: what was checked, what was already true, what was filed, and what was left.

The sweep is not a status report. It is the pass that makes the report true.

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

## Publication Labels

A public surface such as the Lotusia roadmap publishes only objects that are deliberately labeled in Linear. Two rules hold for every gate of this shape:

1. **Labels are two-level and namespace-separated.** Initiatives and projects each have their own label namespace, and the same display name can exist in both with different IDs. An initiative label does not label that initiative's projects, and a project label does nothing unless its initiative is labeled too. Read and write both levels.
2. **A label write replaces the whole set.** `save_project(labels=[...])` and `projectUpdate(input: { labelIds })` replace every label on the object. Read the current set, union the publication label into it, and write the union back. Sending only the new label silently drops the rest.

Mechanics:

- **Projects:** `save_project(id, labels=[...])` accepts the label name and works through the MCP. Read `labels` back from the response.
- **Initiatives:** `save_initiative(id, labels=[...])` applies initiative labels even though the tool's declared schema omits `labels`; the hosted server accepts it (verified 2026-11-26). Read `labels` back from the response. If a future server rejects the undocumented argument, apply the label in the Linear UI, or use a direct GraphQL `initiativeUpdate` with `labelIds` and a write-capable `LINEAR_API_KEY` (the roadmap `.env` key is read-only). The MCP OAuth grant remains the normal path.
- When you need IDs (a GraphQL fallback or an exact read), resolve them by name at use time (`initiativeLabels` and `projectLabels` in GraphQL, or `list_initiative_labels` and `list_project_labels` in the MCP). IDs are workspace-specific; never hardcode them. The MCP writes accept the name directly, and the object type selects the namespace.
- Read back after writing. Confirm the label name on the initiative and on every project, then let the consuming sync run. A successful mutation is not proof the public page renders: the gate may also require the parent initiative, a dated window, or a separate sync.

Never apply a publication label without an explicit ruling that the object is public. The label is the publication act.

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
- A board review fetched every issue with `get_issue` to inspect relations — use `list_issues` with fields for the board and fetch relations only for the cards that change the answer.
- A parent was closed while a child was still open because team auto-close was assumed — check the children; do not assume team auto-close.
- A bulk "all merged" notice was trusted and one PR was still open with `REVIEW_REQUIRED`: enumerate the PRs and verify each against the forge.
- A side conversation's comment was treated as complete, and the facts it omitted had to come from a later handoff: verify its links and evidence before skipping a write.
- A card closed `Done` while its document still held five gaps and fourteen open questions, so the rulings had no card: give every open decision an owner before closing.
- A card said `Todo` while an agent was working in a worktree: move it to `In Progress` at dispatch or worktree creation.
- A publication label was applied to projects but not to their initiative, and the page stayed empty: the gate is two-level, and the two labels are different namespaces.
- A label write dropped unrelated labels because it sent only the new one: read the current set and write the union.

## Quick Checklist

- [ ] Target issue resolved, not guessed
- [ ] Current status and done-when read
- [ ] Board reads batched: `list_issues` fields first; `get_issue` only where relations matter
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
- [ ] Publication labels applied at both levels, with read-back, when a public surface is in scope
- [ ] No duplicate, no secret, no body rewrite
- [ ] Review posture stated, and factual defects proposed as exact writes
- [ ] Other sessions' comments verified, not trusted
- [ ] Every merge in a bulk notice verified against the forge
- [ ] Wave-boundary sweep run before "the board is current" or a handoff
- [ ] Parked work has a resume block on its card
- [ ] Closed cards' decisions and questions have owners
- [ ] Decision packages used for unmeetable done-whens
