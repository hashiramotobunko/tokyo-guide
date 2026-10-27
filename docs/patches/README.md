# Patches that need the repository owner

## 0001-editorial-checks-data-triggers.patch
Adds `data/**` and `scripts/**` to the path filter of `.github/workflows/editorial-checks.yml` and lists `tests/essentials-layer.test.mjs` explicitly in the test step. A token without the `workflow` scope cannot push this file, so it is kept here as a patch.

### Option A — from a terminal
```
git checkout design/encounter-fashion-direction-20261023
git apply docs/patches/0001-editorial-checks-data-triggers.patch
git commit -am "CI: run editorial checks on data and script changes"
git push
```

### Option B — in the GitHub web interface (no local checkout needed)
1. Open https://github.com/hashiramotobunko/tokyo-guide/blob/design/encounter-fashion-direction-20261023/.github/workflows/editorial-checks.yml
2. Click the pencil icon (“Edit this file”).
3. Under `paths:` add two lines after `- 'tests/**'`:
   ```
         - 'data/**'
         - 'scripts/**'
   ```
4. In the step “Check original data, source, routes and accessibility hooks”, append ` tests/essentials-layer.test.mjs` to the end of the `run:` line.
5. Click “Commit changes…”, keep “Commit directly to the design/encounter-fashion-direction-20261023 branch”, and commit.
6. The Actions tab will show “Encounter Japan editorial checks” running on that commit; the PR checks list updates by itself.
