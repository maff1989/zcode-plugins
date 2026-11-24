# Evidence recipes

Use `scripts/collect-evidence.py` first. This file is the manual fallback and the interpretation guide. Every command is read-only.

## Git

- Branch: `git branch --show-current` (empty means detached HEAD).
- Head: `git rev-parse HEAD`.
- Default base: `git symbolic-ref refs/remotes/origin/HEAD` → strip `refs/remotes/`; fall back to `origin/main`, `origin/master`, `main`, `master`.
- Merge base: `git merge-base <base> HEAD`.
- Range: `git log --oneline --no-decorate <merge-base>..HEAD`.
- Dirty tree: `git status --porcelain`.
- Tag at HEAD: `git describe --tags --exact-match HEAD` (failure is normal).
- Remote: `git remote get-url origin`.
- Never quote a local branch as if it were pushed. Check `git log origin/<branch>..HEAD` or `git status -sb`.

## GitHub PR

- `gh pr list --head <branch> --state all --json number,title,state,url,baseRefName,headRefOid,mergedAt,mergeCommit --limit 5`.
- Prefer the PR whose `headRefOid` equals the current head.
- Merge evidence: `mergedAt` non-null and `mergeCommit.oid`; then confirm the default branch contains it with `git merge-base --is-ancestor <merge-sha> origin/<default>`.
- A PR whose base is another PR's branch is not merged into the default branch. That is `In Review`, not `Done`.

## GitHub release

- `gh release view <tag> --json tagName,name,isDraft,isPrerelease,publishedAt,url,assets`.
- `gh run list --limit 10 --json databaseId,name,headBranch,headSha,status,conclusion,event,createdAt`.
- A tag is not a release; a draft release is not published; a published release with a missing asset is not complete.
- For a release, verify the tag's commit, the run's `headSha`, and the asset's checksum and reported version.

## npm

- `npm view <pkg> dist-tags --json` — `latest` is what consumers get.
- `npm view <pkg>@<version> version dist.tarball --json`.
- `npm view <pkg> time --json` — publish timestamps; the output is large, so filter it.
- Publish can be asynchronous: a green workflow may precede the metadata being visible. Re-check before declaring a version live.

## Published artifact

- Download the asset from the release URL, not from the build directory.
- Verify `SHA256SUMS` or the registry's integrity/attestation.
- Run the published binary's `--version` or the package's smoke import.
- A green build is not proof of the published artifact. The artifact is the proof.

## What each event needs

| Event | Minimum evidence |
|---|---|
| Push / PR open | branch, base, head SHA, PR URL, verification command and result |
| PR merge | PR number, merge SHA, default-branch SHA, containing tag/release |
| Release | tag, tag commit, run URL and conclusion, asset count, checksum, published version |
| npm publish | version, `latest` dist-tag, tarball URL, install/import smoke test |
| Deploy | commit, environment, deploy URL/run, smoke check |
| Port / cross-implementation | source tree, target tree, both test results, cross-node run if claimed |

## Traps

- A short SHA or bare `#123` in a comment: link it.
- A local branch, uncommitted work, or a local tag presented as shipped: check the remote.
- Green CI with no release asset: the release may still be missing.
- A release body generated from commits is not an operator notice. Check for the operator notice, activation note, or signing note.
- A port branch based on a draft PR: the PR is open, but the work is not on the target branch.
- A consumer pin: `^0.3.1` does not resolve to `0.4.1`; check the declared range.
