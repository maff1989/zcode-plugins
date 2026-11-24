#!/usr/bin/env python3
"""Collect read-only git/GitHub/npm evidence for a Linear worklog comment.

This script never writes to Linear or to git. It reads the local repository,
the GitHub CLI, and the npm registry, then prints a compact evidence snapshot
that can be pasted into a Linear comment or consumed as JSON.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

EXIT_NOT_GIT = 3


def github_slug(remote: str | None) -> str | None:
    """Return owner/repo from a GitHub remote URL, or None."""
    if not remote:
        return None
    match = re.search(r"github\.com[:/]([^/]+)/([^/]+?)(?:\.git)?/?$", remote)
    if not match:
        return None
    return f"{match.group(1)}/{match.group(2)}"


def github_remotes(repo: Path) -> list[str]:
    """Return unique GitHub owner/repo slugs for this repo, origin first."""
    names = git_ok(repo, "remote")
    if not names:
        return []
    slugs: list[str] = []
    for name in names.splitlines():
        slug = github_slug(git_ok(repo, "remote", "get-url", name))
        if slug and slug not in slugs:
            slugs.append(slug)
    origin = github_slug(git_ok(repo, "remote", "get-url", "origin"))
    if origin and origin in slugs:
        slugs.remove(origin)
        slugs.insert(0, origin)
    return slugs


def find_pr(
    repo: Path,
    remotes: list[str],
    branch: str | None,
    head: str,
    warnings: list[str],
) -> dict[str, Any] | None:
    """Find the PR for this branch/head across all GitHub remotes."""
    fields = (
        "number,title,state,url,baseRefName,headRefName,headRefOid,"
        "mergedAt,mergeCommit"
    )
    candidates: list[dict[str, Any]] = []

    if branch:
        for slug in remotes:
            prs, err = gh_json(
                repo,
                [
                    "pr",
                    "list",
                    "--repo",
                    slug,
                    "--head",
                    branch,
                    "--state",
                    "all",
                    "--json",
                    fields,
                    "--limit",
                    "5",
                ],
            )
            if err:
                warnings.append(f"gh pr list --head ({slug}): {err}")
            elif prs:
                candidates.extend(prs)

    if not candidates:
        for slug in remotes:
            prs, err = gh_json(
                repo,
                [
                    "pr",
                    "list",
                    "--repo",
                    slug,
                    "--state",
                    "all",
                    "--json",
                    fields,
                    "--limit",
                    "50",
                ],
            )
            if err:
                warnings.append(f"gh pr list ({slug}): {err}")
            elif prs:
                candidates.extend(prs)

    seen: set[str] = set()
    unique: list[dict[str, Any]] = []
    for candidate in candidates:
        url = candidate.get("url")
        if url and url not in seen:
            seen.add(url)
            unique.append(candidate)

    match = next(
        (
            p
            for p in unique
            if p.get("headRefOid") == head
            or (p.get("mergeCommit") or {}).get("oid") == head
        ),
        None,
    )
    if match is None and branch:
        match = next((p for p in unique if p.get("headRefName") == branch), None)
    return match


def run(cmd: list[str], cwd: Path, timeout: int = 45) -> tuple[str | None, str | None]:
    """Run a read-only command. Return (stdout, error)."""
    try:
        proc = subprocess.run(
            cmd,
            cwd=str(cwd),
            text=True,
            capture_output=True,
            timeout=timeout,
        )
    except FileNotFoundError:
        return None, f"missing command: {cmd[0]}"
    except subprocess.TimeoutExpired:
        return None, f"timed out: {' '.join(cmd)}"
    if proc.returncode != 0:
        detail = (proc.stderr or proc.stdout).strip()
        return None, detail or f"{' '.join(cmd)} exited {proc.returncode}"
    return proc.stdout.strip(), None


def git(repo: Path, *args: str) -> tuple[str | None, str | None]:
    return run(["git", *args], repo)


def git_ok(repo: Path, *args: str) -> str | None:
    out, _ = git(repo, *args)
    return out or None


def resolve_base(repo: Path, requested: str | None) -> tuple[str | None, list[str]]:
    warnings: list[str] = []
    if requested:
        if git_ok(repo, "rev-parse", "--verify", "--quiet", f"{requested}^{{commit}}"):
            return requested, warnings
        return None, [f"base ref not found: {requested}"]

    sym, _ = git(repo, "symbolic-ref", "refs/remotes/origin/HEAD")
    if sym:
        candidate = sym.removeprefix("refs/remotes/")
        if git_ok(repo, "rev-parse", "--verify", "--quiet", f"{candidate}^{{commit}}"):
            return candidate, warnings

    for candidate in ("origin/main", "origin/master", "main", "master"):
        if git_ok(repo, "rev-parse", "--verify", "--quiet", f"{candidate}^{{commit}}"):
            return candidate, warnings
    return None, ["no base ref found; the commit range is omitted"]


def gh_json(repo: Path, args: list[str]) -> tuple[Any | None, str | None]:
    out, err = run(["gh", *args], repo)
    if out is None:
        return None, err
    try:
        return json.loads(out), None
    except json.JSONDecodeError:
        return None, "gh returned non-JSON output"


def collect(repo: Path, issue: str | None, requested_base: str | None) -> dict[str, Any]:
    warnings: list[str] = []
    branch = git_ok(repo, "branch", "--show-current") or None
    head = git_ok(repo, "rev-parse", "HEAD")
    if not head:
        raise RuntimeError("cannot resolve HEAD")

    base, base_warnings = resolve_base(repo, requested_base)
    warnings.extend(base_warnings)

    merge_base: str | None = None
    commits: list[str] = []
    if base:
        merge_base = git_ok(repo, "merge-base", base, "HEAD")
        if not merge_base:
            warnings.append(f"no merge-base with {base}; using {base} as the range start")
            merge_base = base
        log = git_ok(repo, "log", "--oneline", "--no-decorate", f"{merge_base}..HEAD")
        commits = log.splitlines() if log else []

    status = git_ok(repo, "status", "--porcelain")
    dirty_paths = status.splitlines() if status else []
    tag_at_head = git_ok(repo, "describe", "--tags", "--exact-match", "HEAD")
    remote = git_ok(repo, "remote", "get-url", "origin")
    remotes = github_remotes(repo)
    origin_slug = remotes[0] if remotes else None
    gh_ready = bool(remotes) and shutil.which("gh") is not None
    if not shutil.which("gh"):
        warnings.append("gh not found; PR and release evidence omitted")
    elif not remotes:
        warnings.append("no GitHub remote found; PR and release evidence omitted")

    pr: dict[str, Any] | None = None
    if gh_ready:
        pr = find_pr(repo, remotes, branch, head, warnings)

    latest_release: dict[str, Any] | None = None
    if gh_ready and origin_slug:
        releases, rel_err = gh_json(
            repo,
            [
                "release",
                "list",
                "--repo",
                origin_slug,
                "--limit",
                "3",
                "--json",
                "tagName,name,isLatest,publishedAt,isDraft,isPrerelease",
            ],
        )
        if rel_err:
            warnings.append(f"gh release list ({origin_slug}): {rel_err}")
        elif releases:
            latest_release = next((r for r in releases if r.get("isLatest")), releases[0])
            tag = latest_release.get("tagName")
            if tag:
                detail, detail_err = gh_json(
                    repo,
                    [
                        "release",
                        "view",
                        str(tag),
                        "--repo",
                        origin_slug,
                        "--json",
                        "tagName,name,isDraft,isPrerelease,publishedAt,url,assets",
                    ],
                )
                if detail_err:
                    warnings.append(
                        f"gh release view {tag} ({origin_slug}): {detail_err}"
                    )
                elif isinstance(detail, dict):
                    assets = detail.get("assets") or []
                    detail["asset_count"] = len(assets) if isinstance(assets, list) else None
                    latest_release = detail

    package: dict[str, Any] | None = None
    pkg_path = repo / "package.json"
    if pkg_path.is_file():
        try:
            pkg = json.loads(pkg_path.read_text(encoding="utf-8"))
            name = pkg.get("name")
            version = pkg.get("version")
            if isinstance(name, str) and name and isinstance(version, str) and version:
                package = {"name": name, "version": version}
        except (json.JSONDecodeError, OSError) as exc:
            warnings.append(f"package.json: {exc}")

    npm_dist_tags: dict[str, str] | None = None
    if package and package.get("name"):
        if shutil.which("npm"):
            out, npm_err = run(
                ["npm", "view", str(package["name"]), "dist-tags", "--json"], repo
            )
            if out:
                try:
                    npm_dist_tags = json.loads(out)
                except json.JSONDecodeError:
                    warnings.append("npm view returned non-JSON")
            elif npm_err:
                warnings.append(f"npm view: {npm_err}")
        else:
            warnings.append("npm not found; registry evidence omitted")

    return {
        "repo": str(repo),
        "issue": issue,
        "branch": branch,
        "head": head,
        "base": base,
        "merge_base": merge_base,
        "commits": commits,
        "working_tree": {"clean": not dirty_paths, "paths": dirty_paths},
        "tag_at_head": tag_at_head,
        "remote": remote,
        "github_remotes": remotes,
        "release_repo": origin_slug,
        "pr": pr,
        "latest_release": latest_release,
        "package": package,
        "npm_dist_tags": npm_dist_tags,
        "warnings": warnings,
    }


def to_markdown(data: dict[str, Any]) -> str:
    lines: list[str] = ["## Evidence snapshot", ""]
    lines.append(f"- Repo: `{data['repo']}`")
    if data["issue"]:
        lines.append(f"- Issue: `{data['issue']}`")
    lines.append(f"- Branch: `{data['branch'] or '(detached HEAD)'}`")
    lines.append(f"- Head: `{data['head']}`")
    if data["base"]:
        lines.append(f"- Base: `{data['base']}` (merge-base `{data['merge_base']}`)")
    else:
        lines.append("- Base: not resolved")

    tree = data["working_tree"]
    if tree["clean"]:
        tree_text = "clean"
    else:
        tree_text = f"dirty ({len(tree['paths'])} paths)"
    lines.append(f"- Working tree: {tree_text}")

    commits: list[str] = data["commits"]
    if commits:
        lines.append(f"- Commits since base ({len(commits)}):")
        for commit in commits[:20]:
            lines.append(f"  - `{commit}`")
        if len(commits) > 20:
            lines.append(f"  - … {len(commits) - 20} more")
    else:
        lines.append("- Commits since base: none")

    pr = data["pr"]
    if pr:
        merge = pr.get("mergeCommit") or {}
        merge_sha = merge.get("oid") if isinstance(merge, dict) else None
        merge_text = f", merge `{merge_sha[:12]}`" if merge_sha else ""
        lines.append(
            f"- PR: [#{pr.get('number')} {pr.get('state')}]({pr.get('url')}) "
            f"base `{pr.get('baseRefName')}`{merge_text}"
        )
    else:
        lines.append("- PR: none found for this branch")

    if data["tag_at_head"]:
        lines.append(f"- Tag at HEAD: `{data['tag_at_head']}`")
    release = data["latest_release"]
    if release:
        asset_count = release.get("asset_count")
        asset_text = f" ({asset_count} assets)" if asset_count is not None else ""
        lines.append(
            f"- Latest release: [`{release.get('tagName')}`]"
            f"({release.get('url')}) published {release.get('publishedAt')}{asset_text}"
        )
    package = data["package"]
    if package:
        lines.append(f"- Package: `{package.get('name')}@{package.get('version')}`")
    if data["npm_dist_tags"]:
        lines.append(
            f"- npm dist-tags: `{json.dumps(data['npm_dist_tags'], sort_keys=True)}`"
        )

    warnings: list[str] = data["warnings"]
    if warnings:
        lines.append("")
        lines.append("Warnings:")
        for warning in warnings:
            lines.append(f"- {warning}")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="collect-evidence.py",
        description=(
            "Collect read-only git, GitHub, and npm evidence for a Linear worklog comment. "
            "The script never writes to Linear or to git."
        ),
        epilog=(
            "Exit codes: 0 success, 2 invalid arguments, 3 not a git repository. "
            "Missing gh or npm is reported as a warning, not a failure."
        ),
    )
    parser.add_argument("--repo", default=".", help="repository path (default: current directory)")
    parser.add_argument("--issue", help="Linear issue identifier, e.g. TEAM-123 (label only)")
    parser.add_argument(
        "--base",
        help="base ref for the commit range (default: origin/HEAD, origin/main, origin/master)",
    )
    parser.add_argument("--json", action="store_true", help="emit JSON instead of Markdown")
    args = parser.parse_args()

    repo = Path(args.repo).expanduser().resolve()
    if not repo.exists():
        parser.error(f"--repo does not exist: {repo}")

    if not shutil.which("git"):
        print("error: git not found; install git and retry", file=sys.stderr)
        return EXIT_NOT_GIT

    top = git_ok(repo, "rev-parse", "--show-toplevel")
    if not top:
        print(f"error: not a git repository: {repo}", file=sys.stderr)
        return EXIT_NOT_GIT
    repo = Path(top)

    try:
        data = collect(repo, args.issue, args.base)
    except RuntimeError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return EXIT_NOT_GIT

    if args.json:
        print(json.dumps(data, indent=2))
    else:
        print(to_markdown(data))
    for warning in data["warnings"]:
        print(f"warning: {warning}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
