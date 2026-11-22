# System State Verification

Running a project description's claims against the **served** system, not just the working tree. Load
this when a review has to say what is public *right now* rather than what the repository contains.
Every probe here is read-only and safe to run during a review pass.

## Probe set

**Public surfaces exist and respond**

```bash
for u in <url1> <url2> ...; do
  printf '%-30s %s\n' "$u" "$(curl -s -o /dev/null -w '%{http_code} %{redirect_url}' -m 12 "$u")"
done
```

A `30x` plus a populated `redirect_url` is a finding, not a pass: check whether the redirect target
is the domain you believe is canonical, or the opposite of it.

**Hostname vs transport** — separate a dead host from a broken one

```bash
for h in <host1> <host2>; do printf '%-28s %s\n' "$h" "$(dig +short "$h" A | tr '\n' ' ')"; done
```

- Empty answer + failed fetch → **NXDOMAIN**: the URL is published somewhere (config, docs, another
  repo's `runtimeConfig`) and resolves to nothing.
- Answer present + failed fetch → **not DNS**. Test transport: a bare `curl` failing while
  `curl -k` returns `200` means an **untrusted certificate** — the site is up and every browser
  shows a security interstitial. Never collapse that into "site is down".
- `000` is not an HTTP status. It is curl's "no response"; always pair it with the two checks above.

**Which directory actually deploys**

Read the build entry, not the README: `Dockerfile`, `.github/workflows/*`, deploy scripts, IaC. It
names the directory that ships (`ADD <dir> .`, the CI working directory). Then cross-check against
commit activity:

```bash
git log --since=<date> --name-only --format= | awk -F/ '{print $1}' | sort | uniq -c | sort -rn | head
```

Newest activity and the deployed directory disagreeing is a reportable gap: the rewrite is real work
that is not yet the site. Confirm cheaply against the live build by grepping a font or asset name
that only one of the two builds references.

**Repository visibility and remote health**

```bash
gh repo list <org> --limit 100 --json name,visibility,isArchived,description,pushedAt
gh api repos/<owner>/<name>          # 404 against a working `git remote -v` = dangling origin
npm view <scope>/<pkg> version       # 404 = the shared package was never published
```

`pushedAt` is also the staleness signal: a repo whose last push predates the project's window is a
candidate for "superseded", which changes whether it belongs in scope.

## Repository inventory

One walk of the code root, bounded depth, extracting manifest facts. The point is the **column**
across repos (library tiers, lockfile counts, visibility), not any single row.

The script below is an example; adapt `ROOT`, `NOISE`, and `WANT` to the repositories you are
inventorying.

```python
import os, json, subprocess
ROOT = "<path-to-code-root>"  # directory containing the repositories to inventory
NOISE = {"node_modules", ".git", ".nuxt", ".output", "dist", "coverage", ".turbo",
         ".worktrees", ".disabled", "target", ".venv"}  # add project-specific dirs
WANT = ("nuxt", "vue", "react", "next", "svelte", "tailwindcss", "@nuxt/ui",
        "@nuxt/ui-pro", "@tailwindcss/vite", "wxt", "quasar", "pinia")  # adapt to the repos
for d in sorted(os.listdir(ROOT)):
    p = os.path.join(ROOT, d)
    pkg = os.path.join(p, "package.json")
    if not os.path.isfile(pkg):
        continue
    m = json.load(open(pkg))
    deps = {**(m.get("dependencies") or {}), **(m.get("devDependencies") or {})}
    fw = {k: deps[k] for k in deps if k in WANT}
    remote = subprocess.run(["git", "-C", p, "remote", "get-url", "origin"],
                            capture_output=True, text=True).stdout.strip()
    print(d, m.get("private"), fw, remote,
          sorted(x for x in os.listdir(p) if x not in NOISE))
```

**Exclude the noise directories or the inventory lies.** `.worktrees/`, `.disabled/`, `target/` and
`dist/` hold full or partial copies of the tree; a naive walk lists the same component three times
and buries the real count. Filter by name *before* enumerating, and when a count looks inflated,
check for a worktree directory before trusting it. Add the repository set's own cache, output, and
worktree directories to `NOISE` before the first run.

Manifest-declared files are worth their byte size: a committed generated stylesheet in the tens or
hundreds of KB is evidence that a styling pipeline is bypassed, and a manifest whose build-tool
`content` globs cover only `node_modules` is evidence the same pipeline does not see the source at
all. Report the pipeline state, not just the dependency version.

## Interpreting the result

| Signal | What it means for the plan |
|---|---|
| Deployed dir ≠ most-active dir | The rewrite is not the site; the strategy must account for a cutover step |
| Canonical domain redirects away from itself | Brand/DNS decision is open, not a design detail |
| Published URL is NXDOMAIN / 000 | The surface does not exist; do not treat it as a consumer of the new contract |
| Untrusted certificate | Ops finding attached to that surface; it is visible to every visitor |
| Shared package unpublished (404) | No distribution mechanism exists yet — a decision gate, not an assumption |
| Flagged repos private | A "public reference point" premise needs a visibility decision beyond the new repo |
| Library majors split across the repository set | Root cause of "no unified apparatus"; a component contract can only bind the tier that can consume it |
| Several lockfiles in one app | Package-manager ambiguity; resolve before adding tooling to that repo |
