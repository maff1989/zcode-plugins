# Linear write mechanics

Scope: writing comments, statuses, links, descriptions, and project updates through the Linear MCP without losing evidence. `SKILL.md` is the policy; this file is the mechanics.

## The body is a creation record

- Create the body complete; do not rewrite it for post-creation events.
- Append comments for status changes, dependency changes, scope changes, and closure.
- Exception: the user explicitly says the description is wrong (for example, a target-date contradiction). Then patch the exact text and read it back.
- A bare SHA or `#123` in a body is dead text a reader cannot click. Wrap it explicitly: ``[`<sha>`](<commit url>)``.
- Linear normalizes inline URLs to angle-bracket form and substitutes PR references with entity elements. Read the write response if exact rendering matters.

## Comments

- `save_comment` with `issueId` creates; with `id` updates your own comment.
- `list_comments(issueId)` first; search for the SHA, tag, PR URL, or run URL you are about to record.
- Never edit someone else's comment.
- If your own comment is materially wrong, update it by ID or append a correction. Do not delete the record.
- Attachments embedded in comments are returned by `list_comments`; signed URLs expire in roughly five minutes.

## Status

- `list_issue_statuses(team)` immediately before the first write; use only names that exist.
- `save_issue(id, state)` changes status. `state` accepts a type, name, or ID.
- Read back `status` and `stateHistory`; a successful response is not proof the status you intended exists.
- Do not downgrade `In Review` to `In Progress` just because you are adding a comment.

## Links (Resources)

- `save_issue(links=[{url,title}])` is append-only; identical URLs are not deduplicated.
- The rate limit is roughly 3–4 attachments per minute. Exceeding it does not fail the call: the issue saves and the response carries a `warnings` array naming each dropped link.
- Always read `warnings`; a success payload with the fields you asked for is not proof the links landed.
- Batch at most 3, wait about 60 seconds, then re-read `attachments` and diff against the intended set.
- Use the artifact that proves the claim: commit URL, PR URL, release/tag URL, CI run URL, compare URL, or a blob URL on the repo's real default branch.
- Title links as `<repo>@<shortsha> — <what it proves>`.

## Description patches

- `save_project(patch=[...])` or `save_issue(patch=[...])` applies exact string replacements atomically.
- Every `old_string` must match exactly once. Zero or multiple matches abort the whole patch.
- Use patches only for an explicit user correction. Read back the stored description; Linear may normalize links and PR references.
- Do not use a patch to keep a description current; comments carry the history.

## Project updates

- `save_status_update(type="project", project=..., body=..., health=...)` posts a project update.
- Update by `id` only to correct your own update; otherwise post a new one. The old update is the historical record.
- Include shipped, open, and target. Name the target date and any correction explicitly.

## Read-back checklist

- `get_issue(id)` — status, attachments, `updatedAt`.
- `list_comments(issueId)` — the new comment is present.
- `get_project(id)` — description patch and target date.
- `get_status_updates(project=...)` — the new project update.
- Check `warnings` on every write.

## Public visibility

- A public-facing label may mean the card is rendered publicly. Keep comments factual and free of secrets, tokens, internal hostnames, and personal data.
- When in doubt, write as if the reader is outside the organization.
