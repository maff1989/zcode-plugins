---
description: Run a conversational QA session and file the bug in Linear (GitHub fallback).
argument-hint: "[bug description, or 'start a QA session']"
skills: qa
---

Run a QA session for the problem described by the user:

$ARGUMENTS

Follow the `qa` skill. Resolve the tracker first: Linear when the repository uses it, GitHub
otherwise. For Linear, read the team's states and labels before the first write, create with
`save_issue`, and return the issue URL. Keep the issue body durable and free of file paths or
implementation details.
