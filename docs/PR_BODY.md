# Add block-with-flag FSI frequency benchmark (rhoInf 0.5)

Adds a reproducible 10 s ALE FSI case with the tested Q2 fluid/flag meshes,
rhoInf 0.5 solver input, and schema-1 benchmark.toml for svbenchmark. The
evaluation returns transverse tip frequency from the last eight complete
cycles. Reference is 3.125 Hz from the approximate 0.32 s period reported
by Esmaily-Moghadam et al. (2015), section 3.4, p.59/Figure 10. Proposed
acceptance is 5% relative error.

The case preserves the current nHK/M94 input and Trilinos GMRES/ML solve.
The paper uses StVK; this difference is explicit, and the benchmark assesses
frequency alone. It includes no rhoInf sweep, plots, MATLAB, checkpoints or
solver outputs. MPI configuration remains in SolveExecutionContext.

Related: #662, #664. Depends on the harness introduced in #736.

Validation performed during packaging:
- Loaded manifest with the inspected harness head.
- Existing rhoInf0.5 exported history: 3.097505 Hz over eight final cycles
  (approximately 0.88% error); no new full solve during packaging.
- Input XML and mesh checksums recorded.
- Direct extraction from all 1,000 existing VTUs matched that CSV frequency;
  actual svbenchmark evaluation returned pass. See docs/VALIDATION.md.

Before marking ready, fill in fresh run evidence:
- svMultiPhysics commit/build: TO FILL AFTER FRESH RUN
- platform/MPI/ranks: TO FILL AFTER FRESH RUN
- harness revision and results.json: TO FILL AFTER FRESH RUN
- measured frequency/window/status: TO FILL AFTER FRESH RUN

Review requested: tolerance justification, material-model distinction, mesh
redistribution permission, final case path and manual/scheduled registration.
