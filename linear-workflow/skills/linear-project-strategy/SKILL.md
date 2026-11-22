---
name: linear-project-strategy
description: "Use when the user provides a Linear link (e.g. `linear.app/.../project/...`), names a Linear project or initiative, or asks to review, populate, or drive a Linear board."
version: 1.5.1
author: linear-workflow contributors
license: MIT
metadata:
  tags: [linear, planning, strategy, analysis, mcp, proposal]
  related_skills: [qa]
---

# Linear Project → Implementation Strategy

## When to Use

The user drops a `linear.app/.../project/...` link (or names a project/initiative) and asks to
review it, plan it, or devise an implementation strategy. Default posture is **analysis only**:
the output lives in the reply — no files, no Linear mutations, no git.

The other entry point carries no Linear object at all: the user hands over a **session id**, or a
pile of findings from earlier work, and asks for the work to be captured as cards. If the
`session-history-recall` skill is installed, use its "Mine a session for unfiled work items"
procedure; otherwise mine the session transcript directly. This skill owns what happens next —
tiering, placement, bodies, relations, and the read-back.

## Procedure

1. **The URL is a login wall.** Fetching `linear.app/<ws>/project/<slug>/overview` returns the
   sign-in page, not the project. Never quote it as the project's content. Go straight to the
   Linear `get_project` tool with `query` = the URL's slug or the `P-<TEAM>-<n>` identifier — both
   resolve. The tool is exposed under a plugin-namespaced `mcp__…` name; read the exact name from
   the tool list rather than assuming `mcp__linear__`.
2. **Read the project wide in one turn:** `get_project(includeMembers, includeMilestones,
   includeResources)`, `list_issues(project=<slug>, includeArchived=true)`,
   `list_documents(projectId=<slug>)`.
3. **An empty project is a finding, not a dead end.** `issues: []`, `documents: []`,
   `resources: []`, `milestones: []` means the project is a spec with nothing decomposed — say so
   plainly and let it shape the strategy (that is why Phase 0 exists).
4. **Get the siblings.** `list_projects(initiative=<the project's initiative>, fields=[...])` with
   `description` included. Sibling target dates give the critical path and reveal dependency
   direction the board does not express; dependencies are often embedded in a description as
   `<project id=...>` references. A sibling with an earlier target date and higher priority is an
   input, not a neighbour.
5. **Then leave Linear — the description is intent, not state.** The description names paths, repos
   and files: verify each against disk before repeating the claim. A path named in a spec that does
   not exist is a finding worth reporting (it usually means staging was assumed, not created).
   Verify the **served** system too, not just the files: which directory actually deploys, whether
   the public hostnames resolve and respond, and which repos are public. A spec premised on
   "contributors need a public repository" is contradicted by private visibility of the flagship
   repos, and that contradiction is part of the analysis. Probe set and signal interpretation:
   `references/system-state-verification.md`.
6. **Inventory the real system** before proposing anything: package manifests across the
   repositories, theme/CSS entry points, framework and tooling versions, licence-relevant
   dependencies. Use `Read` / `Grep` / `Glob` — never read source files through the terminal.
   Read the *entry points* (app config, main.css, tailwind config).
   The finding is usually a **split across repos**, not the content of any one repo: the same
   conceptual layer (theme tokens, component library, build tooling) re-implemented per app, or
   defined once in the *least canonical* repo and consumed nowhere. Build a repo × entry-point
   matrix and read the column, not the file. The reverse also holds: before assuming a shared
   mechanism exists, check it is actually published (`npm view <scope>/<pkg>`).
7. **Answer the description's own questions from the workspace first.** Specs often ask something
   the repo already answers (a policy doc, an existing implementation). Quote the existing answer
   with its file and line instead of treating the question as open.
8. **After the first review the deliverable becomes a conversation — keep one live open-items
   list.** Requirements arrive across several turns and the user answers in batches, usually only
   the numbered subset in front of them. So: track asked-and-answered separately from still-open;
   each turn re-raise only the unanswered items, compactly, and never re-dump the earlier analysis;
   when answers arrive in bulk, close with a single consolidated numbered list of everything still
   open, grouped by blocking / non-blocking, each carrying the default you will apply if the user
   says "your call". When the scope changes shape mid-review (a surface is dropped, a different one
   is promoted, a "no migration in this project" boundary appears), restate the surface/scope model
   from scratch in that turn — carrying the earlier framing forward is how a superseded scope
   survives into the plan.

## When the user asks you to drive the board (sanctioned mutations)

Reviewing is read-only by default, but the review often ends with "use Linear issues as the todo
list". That is the explicit authorisation, and the procedure has its own order:

**The body is immutable after creation.** Create it complete — scope, acceptance, initial
blockers, rank — and never pass `description` or `patch` on an update. Every post-creation
action is a comment: status changes, dependency changes, scope changes, closure. A dependency
discovered after creation gets the relation **and** a comment naming the delta; the body's
`Blocked by` list stays as written. Why: the body records what was known when the card opened,
and rewriting it to stay current destroys the only evidence of how the work moved.

1. **Create the issues before doing the work.** The board is the plan; writing it afterwards defeats
   the purpose. Separate cards by phase, because they close at different times: *draft / spec* cards
   (close when the artefact lands), *gap* cards (stay open — a known hole with a named blocker is the
   point of the card), and *implementation slice* cards (stay open and unstarted). Give each gap its
   own card rather than burying it inside a completed one: a missing licence, an unregistered
   context, an unexplained exclusion each deserve to outlive the work that found them.
2. **Set dependencies at creation.** `blockedBy` is what makes the board express the critical path;
   a sliced plan in a comment does not. Re-read the cards afterwards to confirm the edges you
   intended are the edges that exist. Audit the edges already on the board the same way: a consumer
   card left `relatedTo` the contract card whose output it actually requires reads as parallel work
   and licenses starting against an unfinished contract — `blockedBy` is the honest edge, and the
   mis-edge is a review finding in its own right. Resolve every `blockedBy` target's **current
   status** before calling a card blocked: a blocker that is already Done is not a gate, and the
   relation left in place after closure is a stale edge. Conversely, a card whose latest comment
   names an open dependency that exists only as `relatedTo` is gated in practice while the graph
   says parallel. `list_issues` does not return relations; fetch each card with
   `get_issue(id, includeRelations: true)` to audit the actual graph.
3. **Do the work**, treating each card's acceptance criteria as the definition of done.
4. **Comment state, decisions and gaps per card before closing it.** Not a diff summary: what was
   produced, which decisions changed that card's scope, what is now known to be wrong, and what was
   deliberately not done. The card is what a future reader has instead of the conversation, so the
   measured numbers, the rejected alternatives and the resolved contradictions belong there.
5. **Close only what is actually complete.** A draft card closes when the draft exists; an
   implementation card does not close because a spec now describes it. Marking designed-but-unbuilt
   work done destroys the only signal that it is unbuilt. Before closing, walk the card's **own
   nouns** against the artifact — a card titled for several deliverables is routinely closed having
   produced one of them, because the acceptance criteria read as satisfied by the part that had
   visible content.   List or grep the artifact and confirm each named item is present. The gap is
   invisible in the summary you are about to write, and the board is the only place it would have
   been caught. **If the walk fails on a card that is already Done, reopen it** and put the evidence
   in a comment — status is a claim, not a fact, and a green card suppresses the work that an open
   one at least exposes.
6. **Verify by reading back** — `list_issues(project=...)` and check the statuses rather than trusting
   the write responses.

## Structuring a board that will be read publicly

When the tracker is — or is being primed to become — a **public accountability dashboard**, placement
is a claim about what the roadmap *is*. Tier before creating anything, because the tiers use
different Linear primitives:

- **Roadmap tier (public).** One initiative per durable theme (a release-cadence, a product
  surface), with one **dated** project per milestone. Cards here are deliverables an outsider can
  verify: the activation, the shipped release, the operator notice. Nothing internal belongs here
  even when it blocks a roadmap card — express that as `blockedBy` an internal card, so the public
  bar cannot turn green while the plumbing is red without exposing the plumbing.
- **Internal tier.** Work that makes roadmap items true but is not itself a public claim: CI
  coverage, verification harnesses, packaging, tooling. One plainly-named `Internal — …` initiative,
  its projects private, the initiative itself visible so the work is not invisible.
- **Private tier.** Security-sensitive or otherwise non-demonstrable work (monitoring, incident
  response). Its own project, **no initiative and no link from any public project**. Do not let the
  tiering argument demote it: "important but not publicly demonstrable" is a third category, not a
  contradiction to resolve by dropping the card.

**The boundary is verifiability, not secrecy.** Ask one question per card — *can an outsider confirm
this happened?* Yes → roadmap. No → internal. Apply it before sorting, not after.

**A launch project is the usual mis-tier.** Hosting, CI secrets, verification harnesses and
package publishing are internal even when they block a launch; filing them under the public
project makes the roadmap claim look closer than it is. Put them in the internal tier and let
`blockedBy` carry the dependency.

**A staged release has one gate per stage.** When the decision is a private or restricted first
publish with a public visibility flip later, the private-publish card is gated by the implementation
cards, not by the public-graduation card; the public card gates only the flip. A `blockedBy` from
private publish to public graduation is a mis-edge that makes executable work read as legally
blocked. Read the release document's stage headings, not the card body's original `Blocked by`
line, and check which stage the team is actually in.

**A theme needs more than one deliverable, and its name must be work.** Two failures recur when a board is primed for a public page. A theme named after a positioning line has nothing that can be finished or be late, so it gives a reader nothing to hold; name themes for the work (a release cadence, a public surface), and leave the slogan to the product copy it belongs to. A theme holding one project and no scoped future is an empty card with a project inside it — move that project into a sibling theme and retire the initiative rather than shipping a roadmap whose cards are mostly thin. Retirement is `status: Canceled` with the destination recorded in the initiative description, so the move stays legible to whoever reads the board next; promoting the project back out later is one `setInitiatives` call, which is why retiring is cheaper than keeping an empty theme alive.

State the resulting ratio out loud. On a first pass of engineering-debt cards, almost all of them
land internal; a board whose public side ends up with a handful of dated commitments is the correct
outcome, and saying so is what stops the next session from re-inflating it. Fold the trivial ones
(a stale doc line, a branch delete) into a sibling card rather than creating a card per file edit.

Write-path mechanics that this tiering depends on — the initiative plan gate and its workspace-level
workaround, project visibility not being settable by the tool, link-attachment rate limits and their
silent drops, body normalisation at creation, and encoding rank without a rank field:
`references/linear-mcp-write-mechanics.md`.

## Projects express outcomes; repos are labels

A project whose name is a repository name is not a tier, it is a collision: Linear's Project means a
dated outcome, so a repo-named project cannot sit under an initiative without duplicating it or
mis-describing both. The workaround is forced by Linear — an issue belongs to exactly one team and
carries no repo field — so the repo has to be expressed somewhere else. It goes on the issue as a
`repo:<name>` label, while the project and initiative tiers carry outcomes.

Diagnose by counting, never by reading names: list projects with `initiatives` in `fields`, then report
attached vs unattached and how many unattached names match directories in the workspace. A half-landed
tier (initiatives exist, older repo-named projects still unattached) is the normal intermediate state —
present it as a migration queue and never create a new initiative-attached project named after a repo.

**Attachment alone does not tell you whether the top tier is operational.** Count state per tier, not
just membership. Pull the whole team's issues in one call with an explicit field list (`id`, `title`,
`status`, `statusType`, `projectId`, `updatedAt`) rather than one call per project, bucket each issue by
whether its project appears in any initiative's project list, and report in-flight (`started`),
completed, and not-started per tier. The distributions do not mean the same thing:

| In-flight work sits | Reading |
|---|---|
| mostly in the unattached tier | the initiatives describe closed and future work; the repo-named tier is the real operating layer, and the top tier is reporting rather than management |
| mostly under initiatives | the restructure is real and the board can carry a work surface |
| nowhere (all completed or not-started) | the tier is a plan, not a programme — nothing is being executed in either tier |

Lead with the ratio, never an adjective: "every in-flight issue sits outside every initiative" is a
finding, "the board needs some tidying" is an opinion. Record the before-number in the review, because
it is also the only honest success metric for any restructure proposed afterwards — and it is the
number that decides whether a UI built on this tier will look busy or look idle.

Grouping finer than one initiative (an epoch, a release train) needs nesting Linear does not sell on
lower plans, so encode it as a label plus a name prefix and do the rollup as a saved view. Check the
plan gate before designing anything that nests (mechanics: the write-path reference).

## A second tracker becomes the third empty board

Before designing or recommending a work surface, state what it does that the existing surfaces do not.
A new tracker that also accepts free-text cards becomes a third empty board: intake is duplicated, the
authoritative list is ambiguous, and the new surface loses because the real work never leaves the old
one. Two empty boards already exist is the finding that kills a proposal, not a gap it fills.

The fix is structural, not motivational. Restrict intake to promoting an object that is already tracked
or confirming something already captured from the user's own sessions, and render the residue as an
`unsorted` bucket shown as visible debt rather than inviting arbitrary entry. Ask of every new surface:
*is there any way to type work in here that does not exist in the system of record?* If yes, remove it.

## Filing a follow-up card: where it goes and how it is defined

A review routinely ends in "where should this fix live and how should it be defined". Answer both from
the board's own shape, taken this session — team states, labels, cycles, milestones, templates, and the
project's existing cards — and propose only field values that exist. A team with no cycles gets no
`cycleId` invented for it; a project with no milestones gets none.

**Placement**

- **A completed parent cannot host new work.** File the card **flat in the same project** and link it
  `relatedTo: <parent>`. A child under a Done card makes the parent read as fully closed, which is
  precisely how follow-up work stops being visible; parent/child is the right shape only while the
  parent is still open (an epoch parent with a "fix X" child is that shape, and only then). Set
  `blocks` against the **next** still-open cycle card, never against the closed one.
- **Mine the parent's own body for unfiled follow-ups.** A description whose closing line lists
  "post-merge follow-ups (separate): …" with no identifiers is a board gap, not a plan. File them in
  the same pass, and check each against the repo before repeating the claim — a version string still
  at an older major proves the bump never happened. A project showing *zero* open issues while its
  most recent card names three outstanding follow-ups is the finding.
- **Split by close condition, not by topic.** Cards whose evidence differs — a deadline-driven
  coverage hole, a measurable flake, a pipeline property — close at different times and carry
  different priorities. One card holding three done-whens closes when the first is met.

**Definition**

- **The body mirrors the repo's debt-register fields**, because that is the shape the owner already
  keeps in a `TODO.md` entry and the two must not diverge: symptom · anchors (`path:line`, run and job
  ids) · observed vs expected · scope (and why it is pre-existing) · root cause · plan · done-when.
- **done-when names an observation, not an action.** "The boundary assertions execute in the run log,
  quoted", "N consecutive green runs", "the exclusion list no longer contains the name" — never "fix
  the test". An action-shaped criterion is satisfied by attempting the work.
- **A card closed before its own verification artefact existed is a definition defect, not just a
  missing card.** Compare `completedAt` against the timestamps of the run/build/release/publish that
  was supposed to verify it. When the card closed first, propose the missing line for the definition
  of done alongside the new card (for a release: *annotated tag pushed → tag-triggered run green →
  published assets from that tag's tree*); the missing criterion is why the loose end exists.
- **Reuse the board's own naming conventions** for known-hole cards instead of inventing a label — if
  the project already titles them with a `GAP:` prefix, that prefix *is* the convention.

Deliverable shape: board-fact table → placement recommendation with the one-line reason →
alternatives (A/B/C) → copy-paste card bodies → stop. Picking one is the user's call, not the review's.

## Tool mechanics

- **Linear tools are MCP tools with plugin-namespaced names.** Their basenames are the ones used
  here (`get_project`, `list_issues`, `save_issue`, …); the `mcp__…` prefix depends on how the
  plugin server is registered. Read the actual names from the tool list — do not assume
  `mcp__linear__`.
- Read a tool's parameter schema from the tool list before its first call this session; do not
  guess field names. If a call is rejected for an unknown field, re-read the schema and adapt.
- Batch independent reads in one turn — several tool calls, not one call at a time — then write.
- Read-only tools only unless the user asks for changes. Never `save_issue` / `save_project` /
  `save_comment` as a side effect of "reviewing".
- **Labels and workflow states are team-scoped — resolve them with `team: <KEY>` at call time.**
  A workspace-level `list_issue_labels` returns a narrower set than one team's own list (team-only
  labels such as a holding label are omitted from it), so a name remembered from an earlier session
  may simply not exist as seen from the workspace. Read `list_issue_statuses(team=…)` and
  `list_issue_labels(team=…)` immediately before the first write and use only the names returned.
  A team with no `Triage` state expresses intake as `Backlog` instead — do not assume the state set.
- **Identifiers resolve everywhere; UUIDs go stale.** `P-<TEAM>-<n>`, `I-<n>`, `<TEAM>-<n>` are accepted
  wherever a project, initiative or issue is named. A UUID transcribed from a previous session or
  retyped by hand fails as `Could not find project <uuid>` — source ids from a read in *this*
  session. Note also that a project's `initiatives` field carries the initiative's **uuid**, while
  the list tools speak in `I-N` identifiers; normalise before using it as a join key.
  **Three id spaces, one join.** `list_projects` returns `id` as the identifier (`P-<TEAM>-<n>`) but the
  `uuid` is a separate field you must name in `fields` or it is simply absent; an initiative's
  `projects[]` carries project **uuids**; and an issue's `projectId` is a **uuid**. So issue → project →
  initiative requires `uuid` on the project read — without it the only recourse is matching by name,
  which is a guess dressed as a join, and the fix costs a second round trip you can predict. Treat a
  team-wide issue pull as data rather than prose too: a few hundred issues is tens of kilobytes and
  spills to a file, so parse it in code and reduce to the fields you actually report.
- **Wide reads need an explicit `fields` list.** Several nested fields across ~50 projects trips
  Linear's query-complexity ceiling (`The query is too complex. Complexity: 12844. Maximum allowed:
  10000`). Name the fields you need and page rather than enumerating everything, and treat the
  ceiling error as a signal to narrow, not to retry the same query.
- **Read the workspace's shape at the start of every session.** Initiative attachment, project count
  and the label set all drift between sessions in a live workspace; a description of the board from
  an  earlier session is a claim about a past world. Quote counts only from a read taken this turn.
  **The same holds inside one conversation.** When the user reports work done outside it — a merge,
  a release, a deploy — re-read the repo (`git log`, `gh pr list`, `gh release view`) as well as the
  board before writing cards: a card list drafted earlier the same day can describe a world that no
  longer exists, and a headline card saying "push the branch" for an already-merged-and-released
  branch is the visible symptom. Diff the earlier plan against the live state and report which items
  closed themselves, rather than re-proposing them.
  **A project description's own status note is a claim, not a count.** Recount the states from
  `list_issues` instead of quoting the tally it asserts, and re-check any "this should be reset"
  instruction against the field it names — the note is written once while the cards keep moving, so it
  lags by roughly one closure. Card comments carry the same risk: a comment claiming a commit count,
  test count or clean extraction is a claim; `git rev-list --count` and the actual test run are the
  evidence.
- **Enumerate a board with `project:` / `team:`, not `query:`.** `query` is loose full-text across the
  whole workspace and returns unrelated projects' cards for a phrase like "functional test", with no
  signal that it did — use it only to look for an existing duplicate by title, and page
  `list_issues(project=…, fields=[…])` when you need the board itself.
- `save_issue` returns a computed `gitBranchName` alongside the identifier. When the work will end
  in a PR that a tracker-link gate checks, take that branch name rather than constructing one —
  the gate matches what Linear actually publishes.
- **A write that returns success can still have dropped part of itself.** Link attachments are
  rate limited and fail *per link* into a `warnings` array while the issue saves; initiative
  creation is plan-gated on the team attachment only. Read the response's warnings and re-read the
  object before reporting what was created — the write-path reference has both recipes.

## Output shape (default)

These are the defaults; adapt them when the user states a different preference.

- Lead with the project's actual state as a table (id, initiative, status, priority, target date,
  lead, counts, siblings), then the analysis. Facts first, then argument.
- **Root cause, not consequence enumeration.** Prefer "the only difference is X" over "here are N
  consequences of X". A list of symptoms reads as lazy analysis.
- **Every claim carries an anchor** — `file:line` or a tool result. No assertion without a
  verifiable anchor.
- **Phases ordered by marginal cost**, with the cheapest wave doubling as the regression test for
  whatever contract the project is establishing ("its pixels must not change").
- **State structural contradictions explicitly.** When a stated requirement is unsatisfiable as
  written, name it in its own section with the evidence and scope it into layers — do not quietly
  narrow it and do not silently comply.
- **List the decision gates as options (A/B/C/D) and STOP.** Do not select one, do not start
  implementing, do not write files. Mark each as needing the user's call. Presenting the options is
  the deliverable; picking one is a separate, later turn.
- **When the user invites questions (“grill me”), batch them.** Put every independent decision in
  one `AskUserQuestion` call, recommended option first, and use a free-text question only for a
  factual unknown that has no sensible options. A chain of one-question turns loses the plan's
  context and makes the user answer the same framing repeatedly.
- **When the question is "what is left", answer per card with the artifact's measured
  state, not the card's status.** `Todo` is a state the board already shows the user; what
  it cannot show is that the directory behind the card holds a README and a manifest and
  nothing else, or that the Done card's gate you just ran is green. Walk each open card's
  own nouns against the tree and print that beside the status, then separate work the board
  does not know about at all — dirty tree, unpushed commits, untracked files — because
  in-flight work is the part a board review is most likely to miss.
  **A green gate is not evidence until you read what it runs.** `build` and `typecheck`
  scripts that only `echo` a TODO, or a pack checker with a hardcoded package whitelist,
  produce a green run over a package with no source. Read the manifest scripts and the
  checker's list, and treat a manifest that names `dist/` entry points as a declaration,
  not proof the files exist.
- Close with exactly the open questions you need answered before proposing files.
- Keep "no changes yet" precise: no files created (not even a plan file), no ticket mutations, no
  commits. "Output here" means the chat.

## Pitfalls

- **A declared fresh start supersedes same-class documents.** When the user says a topic is a fresh
  start or a new model, existing documents of that class in the workspace are **not** precedent —
  do not mine them for the plan, and say plainly that you are not. Why: anchoring a new design on a
  superseded artifact reintroduces the exact decisions the user just discarded, and the plan reads
  as a defence of the old shape. Report the superseded documents you found and present their fate
  (archive / supersede / delete) as a decision gate — staying silent about them leaves them in place
  to re-anchor the next contributor.
  **A fresh start can carry a scoped carve-out.** When the user later names one surface as a
  baseline ("use X's existing implementation here"), restate the exception as the exact files and
  lines you will take from it and get that confirmed. An unbounded "baseline" silently re-imports
  every decision the fresh start discarded, and naming the boundary at the moment it is granted is
  the only defence.
- **The user's own claims about their own repos are claims, not constraints.** When the user asserts
  repository state mid-review ("only X has been migrated", "that repo is unused", "everything is on the
  new stack"), verify it against manifests, dependency versions and commit history before designing
  around it. Why: a wrong belief about their own repo silently removes the only instance of a
  capability from scope, and because the assertion came from the owner nothing later in the review
  re-checks it. Correct it plainly, with the evidence, and name what the scope decision changes —
  the correction is load-bearing when the excluded repo turns out to be the only one holding a
  needed asset.
- **Specs describe intent; the disk describes state.** Report the gap between them as a finding
  rather than resolving it silently in either direction.
- **The remote is not the disk: a Done card can be right while `origin` is behind.** Before reporting
  that a completed card produced no artifact, read the **local** clone — `git log origin/<default>..HEAD`
  and `git status --porcelain` — not a host API's view of the default branch. Acceptance work routinely
  sits in unpushed commits or in the working tree, so a remote tree shows a stub exactly where the
  implementation exists, and "closed with no artifact" becomes a retraction. Order the evidence:
  working tree → local history → remote. The inverse is the finding worth reporting: a card closed with
  its work still uncommitted or unpushed means the deliverable has not landed, and that in-flight work
  is unfiled work that belongs on the board.
- **Do not treat a project description's requirements as mutually consistent.** A single list often
  mixes a universal constraint with a framework-specific one; reconciling that is part of the
  analysis, not an obstacle to it.
- **Do not propose repo-legal artifacts** (a `LICENSE`, a copyright holder identity, public
  publication) while an entity/ownership question is open in a sibling project. State the blocker
  and the ordering instead.
- **The most recently edited directory is not the deployed one.** Read the build entry
  (Dockerfile, CI workflow, deploy script) to learn which directory ships, then compare it against
  per-directory commit activity. A rewrite can be complete, lint-green and months newer while
  production still serves the old directory; report that gap instead of describing the rewrite as
  the current site.
- **Never report "site down" from a bare HTTP probe.** A failed fetch has three unrelated causes
  with three different fixes: the hostname does not exist, the host resolves but refuses the
  connection, or the certificate is untrusted so a verifying client aborts while the site is up.
  Separate them before writing a single word about availability.
- **Repo visibility is state, and it routinely contradicts the spec's premise.** Enumerate the whole
  org's visibility rather than checking the one repo you happen to open, and verify each local
  clone's remote actually exists on the host: a 404 against a plausible `git remote` means
  local-only work with a dangling origin.
- **One research pass is enough.** This is a reading task: batch the fetches, then batch the file
  reads, then write. Do not interleave a fetch-write-fetch cycle.
