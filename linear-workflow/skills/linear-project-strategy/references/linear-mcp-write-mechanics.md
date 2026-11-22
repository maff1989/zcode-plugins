# Linear write path: mechanics that cost time

Scope: creating initiatives/projects/issues, attaching links, and writing bodies once.
The read path (identifiers, `fields`, query-complexity ceiling) is in SKILL.md § Tool mechanics.

## Initiatives are plan-gated — the planning shape is not

- `save_initiative` **with** `leadTeam` is rejected on lower plans:
  `Subscribe to the Business plan to access team initiatives in your workspace.`
- The **same call without `leadTeam` succeeds** and creates a workspace-level initiative
  (`leadTeam: null`). `save_project(addInitiatives: ["I-N"])` accepts it unchanged.
- So the refusal is about the team attachment, not about initiatives existing. Retrying the
  team-attached form with different payload fields never works; drop `leadTeam` and move on.
  Report the shape you actually got (workspace-level) instead of describing the tiering as blocked.

## Project visibility is not on the write tool

`save_project` exposes no visibility/private field (`additionalProperties: false`). A project
intended as internal is created workspace-visible like any other.

- Create it anyway; carrying a half-enforced tier is better than abandoning the model.
- Make "flip these N projects to private in the UI" an explicit hand-off item, listed by
  identifier, in the same reply that reports the tree.
- Never say the tier is enforced when only the naming says so.

## Link attachments (Resources)

- `links: [{url, title}]` is **append-only**: existing links are never removed and identical
  URLs are not deduplicated, so re-running a create that carries links doubles them.
- **Rate limited at roughly 3–4 attachments per minute.** Exceeding it does *not* fail the call —
  the issue saves, and the response carries a `warnings` array naming each dropped link
  (`Ratelimit exceeded - You're trying to attach links too often.`).
  **Always read `warnings`.** A success payload with the fields you asked for is not proof the
  links landed; the drop is reported only there.
- Retry pattern: batch ≤3 links, sleep ~60 s between batches, then re-read the issue and diff
  `attachments` against the intended set before reporting coverage.
- Use the artifact that proves the claim, not the repo root:
  commit URL · PR URL · release/tag URL · CI **run** URL · `/compare/<sha>...<sha>` for a range ·
  `/blob/<branch>/<path>` for a file anchor.
- **Blob URLs need the repo's real default branch.** Confirm it (`git branch --show-current`,
  `git symbolic-ref refs/remotes/origin/HEAD`, or the clone's own docs) — a `main` that is
  really `master` yields 404s that look like deleted files.
- Title each link as `<repo>@<shortsha> — <what it proves>`. Resources then read as an evidence
  list a human can audit, not a pile of URLs.

## Descriptions: write once, link explicitly

- **The body is the creation-time record and is never patched afterwards.** Post-creation actions
  belong in comments (SKILL.md). The normalisation notes below matter only for what a reader sees
  in the body you created.
- A bare short SHA or `#123` in a body is dead text a reader cannot click. Wrap it explicitly:
  `` [`<sha>`](<commit url>) `` — Linear's own autolinking is inconsistent across forms
  (it turns `owner/repo#N` into an entity, and leaves a bare 9-hex SHA alone).
- **The stored body is not the body you sent.** Linear normalises inline URLs to
  `[text](<url>)` (angle-bracketed) and substitutes PR references with entity elements. Read the
  `save_*` response if you need to know what a reader will see.
- **Never write an angle-bracket placeholder** such as `<the release card>` into a body: in the
  stored text it reads as a link target and renders mangled. Name the card's identifier once it
  exists, or describe it in words.
- If a body is wrong after creation, add a comment that supplies the correction. Do not rewrite the
  body; a corrected body loses the record of what was known when the card was filed.

## Encoding an ordering Linear does not have

There is no rank field. Encode the review's global order twice: `priority` for the tier
(1 Urgent / 2 High / 3 Medium / 4 Low) **and** a `Rank N of M` line at the end of each body.
Cards get spread across projects, where the tier alone loses their order relative to each other,
and a flat tier list is indistinguishable from no ranking at all.
