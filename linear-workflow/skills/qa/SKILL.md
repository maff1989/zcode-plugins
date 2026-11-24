---
name: qa
description: "Use when filing bugs: conversational QA into Linear issues, with GitHub issues as the fallback."
version: 1.1.2
author: linear-workflow contributors
license: MIT
metadata:
  tags: [qa, bugs, linear, github]
---

# QA Session

Run an interactive QA session. Describe problems you're encountering. I'll clarify, explore the codebase for context, and file issues in the project's tracker — Linear when the repository uses it, GitHub otherwise — that are durable, user-focused, and use the project's domain language.

## For each issue raised

### 1. Listen and lightly clarify

Let you describe the problem in your own words. I'll ask **at most 2-3 short clarifying questions**:

- What you expected vs what actually happened
- Steps to reproduce (if not obvious)
- Whether it's consistent or intermittent

I won't over-interview. If the description is clear enough, I'll move on.

### 2. Explore the codebase in background

While talking, I'll explore the relevant area to:

- Learn the domain language (check the project's domain-language doc, if one exists)
- Understand what the feature is supposed to do
- Identify the user-facing behavior boundary
- Check which bounded context this belongs to (check the project's context map, if one exists)

This helps me write a better issue — but the issue itself will NOT reference files, line numbers, or implementation details.

### 3. Assess scope

Before filing, decide: **single issue or breakdown?**

**Break down when:**
- Fix spans multiple independent areas
- Clearly separable concerns exist
- Multiple distinct failure modes or symptoms

**Keep as single when:**
- One behavior wrong in one place
- Symptoms share the same root behavior

### 4. Choose the tracker and file the issue(s)

**Linear (default when the repo uses it).** Look for a Linear signal: `AGENTS.md` or docs naming a
Linear team key or workspace, a `linear.app` project link, or a project already driven through
`linear-worklog`. Resolve the team and its vocabulary at call time — `list_teams`, then
`list_issue_statuses(team=<KEY>)` and `list_issue_labels(team=<KEY>)` — and create with the Linear
`save_issue` tool. Use only state and label names those reads returned. For a breakdown, create
the parent first and pass `parentId` on each sub-issue; express a blocker with `blockedBy`, not a
prose line. The body is immutable after creation: put corrections in a comment.

**GitHub (fallback when the repo is tracked there).** Signals: a `.github/ISSUE_TEMPLATE`
directory, recent `gh issue list` results, and no Linear signal. Create with `gh issue create`.
If the tracker is genuinely unclear, ask one question — "Linear or GitHub?" — rather than guessing.

Either way, file and share URLs without asking for review first.

**All issues must be durable** — they should still make sense after major refactors.

#### Single issue template

```markdown
## What happened

[Actual behavior in plain language, using domain terms]

## What I expected

[Expected behavior]

## Steps to reproduce

1. [Concrete, numbered steps]
2. [Use domain terms, not module names]
3. [Include relevant inputs, flags, config]

## Additional context

[Extra observations — use domain language, don't cite files]
```

#### Breakdown template (per sub-issue)

```markdown
## Parent issue

<identifier — `<TEAM>-123` in Linear, `#123` in GitHub> or "Reported during QA session"

## What's wrong

[This specific behavior problem, just this slice]

## What I expected

[Expected behavior for this slice]

## Steps to reproduce

1. [Steps specific to THIS issue]

## Blocked by

- <identifier> or "None — can start immediately"

## Additional context

[Relevant to this slice]
```

### Rules for all issues

- **No file paths or line numbers** — they go stale
- **Use the project's domain language** (from the project's domain-language doc)
- **Describe behaviors, not code** — "the experiment stats show 0 visitors" not "getExperimentStats() returns empty"
- **Reproduction steps are mandatory**
- **Keep it concise** — readable in 30 seconds
- **In Linear, correct the record with a comment** — the body is creation-time evidence, not a mutable summary

After filing, I'll share all issue URLs and ask: "Next issue, or are we done?"

### 5. Continue the session

Keep going until you're done. Each issue is independent.

## Related capabilities

If the environment provides companion skills for holistic context, domain modeling, or
tracer-bullet TDD, use them before or after filing.
