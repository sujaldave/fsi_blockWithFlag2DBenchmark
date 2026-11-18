# Harness compatibility and upload workflow

Inspected 2026-11-11: PR https://github.com/SimVascular/svMultiPhysics/pull/736,
branch `alexander02468/svMultiPhysics:feature/664-benchmark-harness`, head
`82f4179946ceb9a74acd8cdb84a8ce830119174c`.
Also inspected all available issue comments in #664 and #662, PR review
comments, local lidDriven2DBenchmark and 2DLidDrivenCavityBenchmark inputs,
and https://github.com/sujaldave/2DLidDrivenCavityBenchmark.

The current harness loads schema=1 TOML; preprocess/postprocess/evaluation
are named tables with argv and optional cwd. Solver tables accept input
and cwd. Evaluation commands print one float and use reference with exactly
one of atol/rtol. Relative comparisons are inclusive. SolveExecutionContext
owns executable, MPI launcher, arguments, and rank count. It calls commands
with check=True. Optional cleanup can be omitted.

PR review discusses undocumented keys, ignored `mpirank`, Python floor,
tolerance semantics, stderr propagation, and report tolerance types. This
package uses only implemented keys, reference_source, a nonzero frequency
reference with rtol, and an external context for MPI. It does not rely on
proposed one-sided comparisons or unmerged automatic registration. Unlike
the earlier cavity repository's custom allRun/configuration, this allRun is
a thin harness driver, not a second benchmark execution framework.

## Publish the standalone case

After confirming mesh permission and choosing a license, create an empty
GitHub repository `sujaldave/fsi_blockWithFlag2DBenchmark`. From this directory:

```bash
git init -b main
git add .
git status --short
git commit -m "Add rhoInf 0.5 block-with-flag FSI frequency benchmark"
git remote add origin git@github.com:sujaldave/fsi_blockWithFlag2DBenchmark.git
git push -u origin main
```

Check that no .venv, validation, results, or *-procs directory is staged.
Keep the case repo independent of a solver checkout. Record a tested solver
commit/build configuration and a successful fresh 10 s report in the PR;
do not call the existing-output evaluation a fresh end-to-end solve.

## Prepare the upstream PR after the harness merges

Fork SimVascular/svMultiPhysics, clone your fork separately, configure upstream,
then start from current upstream/main (use a clean checkout):

```bash
git fetch upstream
git switch -c codex/fsi-block-flag-benchmark upstream/main
mkdir -p benchmarks/cases/fsi/block_with_flag_2d
rsync -a --exclude .git --exclude .venv --exclude validation --exclude results.json \
  /absolute/path/to/fsi_blockWithFlag2DBenchmark/ \
  benchmarks/cases/fsi/block_with_flag_2d/
python -m pip install -e benchmarks/svbenchmark
python benchmarks/cases/fsi/block_with_flag_2d/allRun \
  --solver /absolute/path/to/svmultiphysics --ranks 40
git add benchmarks/cases/fsi/block_with_flag_2d
git diff --cached --stat
git commit -m "Add block-with-flag FSI frequency benchmark"
git push -u origin codex/fsi-block-flag-benchmark
```

Open a PR to SimVascular/svMultiPhysics main with `docs/PR_BODY.md` as the
starting description. Replace its test-status placeholders with actual new
run evidence. Link #662, #664, and #736 without claiming to close the umbrella
issues. Ask maintainers for a dedicated case issue and final directory naming.
If desired, open a draft PR before merge and mark it dependent on #736;
rebase onto upstream/main and retest once it lands. Avoid bundling the harness
implementation into the case PR.

The inspected harness has no automatic case-discovery CI registration in its
current tree; adding benchmark.toml makes the case loadable, not automatically
scheduled. Once registration exists, add this manifest's relative path to the
agreed manual/scheduled runner with its solver/MPI execution context. Ask for
that concrete registration in the PR rather than inventing a CI YAML now.

## Suggested issue update (post manually)

Prepared a rhoInf=0.5, 10 s block-with-flag FSI benchmark at
https://github.com/sujaldave/fsi_blockWithFlag2DBenchmark (publish first).
It follows PR #736 schema 1, preserves the tested XML/meshes, and emits one
frequency scalar over eight final cycles. Literature reference is 3.125 Hz
(approximately 0.32 s); proposed rtol is 5%. Please review the tolerance,
nHK-versus-StVK model difference, case placement and eventual scheduled
registration. Integration PR will depend on #736. Related: #662 and #664.
