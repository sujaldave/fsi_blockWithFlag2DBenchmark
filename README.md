# FSI square block with flexible flag

Single-case svMultiPhysics benchmark: rho infinity 0.5, 10,000 steps of
0.001 s, ending at 10 s. Input XML and meshes are copied byte-for-byte from
the local channel-block-flag_2D case accompanying the 40-procs-rho0p5 results.
No MATLAB, plotting, digitized curves, restart files, or solver results are
required or committed. Meshes are supplied because preserving the tested
discretization is preferable to introducing a new mesh generator.

## Reference and acceptance

M. Esmaily-Moghadam et al., *A bi-partitioned iterative algorithm for solving
linear systems arising from incompressible flow problems*, Computer Methods
in Applied Mechanics and Engineering 286 (2015), 40-62, section 3.4,
Figures 8-10. Page 59 states an approximate oscillation period of 0.32 s
for all compared methods, giving **f_ref = 3.125 Hz**. Figure 10 compares
against Bazilevs et al., *Isogeometric fluid-structure interaction: theory,
algorithms, and computations*, Computational Mechanics 43 (2008), 3-37.

The one scientific acceptance scalar is the transverse flag-tip frequency:

`abs(f_run - 3.125) <= 0.05 * 3.125` (Hz).

This is a proposed 5% engineering tolerance, not a tolerance stated by the
article or a demonstrated architecture envelope. Bounds are 2.96875 to
3.28125 Hz. It tests the dominant oscillation frequency only, 
not displacement amplitude, stresses, mesh convergence, or full waveform correctness.

The run must reach 10 s. In t >= 6 s, compute the mean y displacement,
interpolate positive-going crossings of this level linearly between actual
samples, and use the last nine crossings (eight complete periods):
`f = 8 / (crossing[-1] - crossing[-9])`. No filtering, curve fitting, phase
shifts, or amplitude scaling are performed. Insufficient cycles, nonfinite
data, missing output intervals, negligible oscillation, and period coefficient
of variation above 10% raise errors rather than returning a passing scalar.
These are data-validity guards, not extra literature acceptance scalars.

`validation/frequency_diagnostics.json` records the actual crossing times,
window, frequency, and period variability; `validation/tip_y.csv` contains
the extracted samples. The harness writes `results.json` with reference,
tolerance, measured value, status, timings, and execution environment.

## Physical and numerical setup

CGS units: channel 19.5 x 12 cm, block 1 x 1 cm, flag 4 x 0.06 cm;
reference tip (9.5, 6, 0) cm. Fluid density 1.18e-3 g/cm^3, viscosity
1.82e-4 g/(cm s), inlet speed 51.3 cm/s. Solid density 0.1 g/cm^3,
Young's modulus 2.5e6 g/(cm s^2), Poisson ratio 0.35. The XML preserves
the inlet sign convention (-51.3), slip top/bottom walls, fixed block and
flag root, outlet backflow coefficient 0.2, ALE mesh equation and interface
projection. Q2 mesh paths and all boundary surfaces are included. The supplied 
XML uses `nHK` plus `M94`; the paper specifies St. Venant-Kirchhoff elasticity. 
The paper also uses rho infinity 0.2 and runs for 5 s; this benchmark uses the
rho infinity 0.5 setup and extends to 10 s. It is a frequency validation
against that literature case, not an exact reproduction of every method.
The input requires a solver with Trilinos GMRES and `trilinos-ml`; the
mesh equation uses FSILS CG. No fallback changes these choices.

## Installation and one-command execution

Use Python 3.14 to match the packaging checks (the harness declares >=3.12).
Use an svMultiPhysics build with the
required Trilinos/ML support, plus MPI compatible with that build.

```bash
python3.14 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pip install -e /absolute/path/to/svMultiPhysics/benchmarks/svbenchmark
./allRun --solver /absolute/path/to/svmultiphysics --ranks 40
```

Until PR #736 is merged, install the harness from its reviewed head branch.
See `docs/INTEGRATION.md` for the pinned commit and upload/PR instructions.
`--ranks` defaults to 4 for convenience; use 40 to match the existing run.
MPI ranks, executable, launcher, and launcher arguments are execution-context
options, intentionally absent from benchmark.toml. Example launcher option:
`--mpi-arg=--bind-to --mpi-arg=none`. All commands use the active environment's
`python`, including the manifest, so activate the same environment first.

Outputs are kept for diagnosis. Preprocessing refuses an existing
`case/*-procs` directory or STOP_SIM file, preventing stale results from being
mistaken for a fresh run. Move old output outside `case/` before rerunning.
Cleanup is optional in the current harness and is deliberately omitted.
The wrapper returns nonzero on a failed criterion or execution error.

To evaluate existing outputs without rerunning the solver:

```bash
python scripts/benchmark.py extract --run-dir /absolute/path/to/40-procs-rho0p5
python scripts/benchmark.py evaluate
```

The evaluation command emits exactly one float on stdout; errors go to stderr.
No fresh 10 s solve was performed during packaging. The existing exported
rho0p5 history gives approximately 3.097505 Hz with this eight-cycle method,
about 0.88% below the reference. See `docs/ASSUMPTIONS.md` for limitations.

## Layout

```
benchmark.toml          harness schema 1 manifest
allRun                 local execution context and report writer
case/solver.xml        unchanged current input
case/mesh/             two volume meshes and eight boundary surfaces
scripts/benchmark.py   input checks, extraction, frequency scalar
reference/             source description and input checksums
docs/                  assumptions, harness review, PR draft and workflow
```

Mesh redistribution and code licensing should follow the original owners'
terms. This package does not invent a license for the supplied mesh assets;
confirm their provenance/redistribution permission before public upload.
