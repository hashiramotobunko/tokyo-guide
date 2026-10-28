# Applied release patches

## 0001-editorial-checks-data-triggers.patch
This patch was applied to the release branch before publication. It is retained only as an audit record.

## 0002 — run the editorial checks when the photographs change (2026-10-28)

`0002-ci-run-editorial-checks-on-photo-assets.patch` adds `assets/photos/**` to the workflow's
path filter, so a change to a street photograph re-runs the checks. It could not be pushed from
the implementation session (an OAuth app cannot write `.github/workflows/**` without the
`workflow` scope). Apply it with a token that has that scope:

```
git apply docs/patches/0002-ci-run-editorial-checks-on-photo-assets.patch
git commit -am "CI: run editorial checks when the photographs change" && git push
```

Or edit the file in the GitHub web interface and add the single line `      - 'assets/photos/**'`
directly under `      - 'assets/editorial/**'`.
