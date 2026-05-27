# conda-forge feedstock — draft recipe for PTSA 3.0.6

This dir holds a draft conda-forge recipe (`recipe/meta.yaml` +
`build.sh` + `bld.bat`) suitable for submission to
[conda-forge/staged-recipes](https://github.com/conda-forge/staged-recipes).

**This is staging, not the published recipe.** PTSA's published
binaries on `anaconda.org/pennmem` come from `conda.recipe/` at
the repo root. Once submitted and merged into conda-forge,
`conda-forge/ptsa-feedstock` becomes the canonical home and the
pennmem channel becomes a fallback.

## Submission flow

1. **Fork** <https://github.com/conda-forge/staged-recipes>.
2. **Copy this dir** into the fork: `recipes/ptsa/meta.yaml`,
   `recipes/ptsa/build.sh`, `recipes/ptsa/bld.bat`.
3. **Fill in the placeholders** in `recipes/ptsa/meta.yaml`:
   * `sha256:` — once a `v3.0.6` git tag exists, compute via
     `curl -sL https://github.com/pennmem/ptsa/archive/refs/tags/v3.0.6.tar.gz | sha256sum`.
   * `extra.recipe-maintainers` — list of GitHub usernames that
     will own the feedstock (at minimum, whoever does the
     submission; ideally also another pennmem maintainer).
4. **Open a pull request** to staged-recipes with title
   `Add ptsa recipe`. conda-forge's CI will build on
   linux-64 / osx-64 / osx-arm64 / win-64.
5. **Address review feedback.** Common asks: license file
   inclusion, lint nits, run_constrained additions.
6. **On merge**, a new repo `conda-forge/ptsa-feedstock`
   auto-spawns. From then on, version bumps land as PRs filed by
   the conda-forge update bot; you just review + merge.

## Pre-submission checklist

* `conda-smithy recipe-lint recipe/` returns clean (install
  `conda-smithy` via `mamba install -c conda-forge conda-smithy`)
* `recipe/meta.yaml` has no `# TODO` left in the file
* The PTSA git tag the `source.url` points at actually exists
* `LICENSE` is shipped in the source tarball (PTSA already does)
* `about:` section is complete (home, license, summary,
  description, dev_url, doc_url)
* `extra.recipe-maintainers` lists at least one real GitHub
  username

## Local sanity-build

To validate the recipe builds before submission:

```bash
# Substitute the source temporarily for a local path build
conda-build conda-forge/recipe/ --python=3.11 --no-anaconda-upload \
    --output-folder=/tmp/cf-out/ \
    --no-test  # skip remote URL fetch
```

(The recipe in this dir currently uses the upstream URL pattern;
for local-tree testing, swap `source.url`/`source.sha256` for
`source.path: /home1/rdehaan/dependencies/ptsa` temporarily.)
