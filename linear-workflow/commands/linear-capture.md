---
description: Capture session findings or unfiled work as Linear cards.
argument-hint: "<session id, findings, or scope to capture>"
skills: linear-worklog
---

Capture the work described by the user as Linear cards:

$ARGUMENTS

Follow the `linear-worklog` skill's target resolution, follow-up classification, and write
mechanics. Resolve targets with a single `list_issues` read where possible; do not fetch every
card with `get_issue` unless its relations change the placement. Place each card in its owning
project, set relations at creation, write the body once, and read the cards back. Use only fields,
states, labels, cycles, and milestones returned by a read taken in this session. Report the
created identifiers and the read-back.
