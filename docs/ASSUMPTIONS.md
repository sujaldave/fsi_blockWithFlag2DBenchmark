# Assumptions and decisions for review

1. The current `channel-block-flag_2D/solver.xml` and its referenced meshes
   describe the latest intended rho infinity 0.5 run. There is no per-run
   archived XML proving that the existing 40-process results used this exact
   file; checksums fix the inputs from packaging onward.
2. Preserve nHK/M94 rather than replacing it with the paper's StVK material.
   This is a disclosed model difference, so agreement in frequency alone
   does not establish full constitutive or waveform equivalence.
3. Preserve all current linear/nonlinear solver settings, mesh settings,
   boundaries, output cadence, and restart cadence; require Trilinos/ML.
4. Run from rest for 10 s with rho infinity 0.5, even though the reference
   paper ran 5 s with its stated rho infinity 0.2.
5. Use the approximate published 0.32 s period (3.125 Hz), rather than a
   digitized plot or any present-run measurement, as the reference.
6. A 5% relative frequency tolerance is provisional and requires scientific
   maintainer agreement; it is not taken from the article or established by
   architecture, MPI-rank, mesh, or time-step convergence studies.
7. Eight complete final cycles within t >= 6 s meet the requested final
   5-10-period window. Crossing times use linear interpolation of unsmoothed
   samples; the mean over t >= 6 s defines the crossing level.
8. A 10% maximum period coefficient of variation, 1e-4 cm minimum range,
   and 0.015 s maximum output gap are data-validity policies. They guard
   against unresolved/irregular signals but do not prove statistical stationarity.
9. The tip is the reference-coordinate centerline node (9.5,6,0) cm.
   VTU point coordinates are reference coordinates as in the existing
   extraction workflow; GlobalNodeID is used to follow the point when present.
10. VTU files contain TimeValue and Displacement (or FS_Displacement), with
    unchanged topology when GlobalNodeID is unavailable. One MPI result
    directory exists per clean case. Serial/nonstandard output directory
    naming needs an adapter or the explicit --run-dir extraction option.
11. MPI ranks are hardware-dependent execution settings; the wrapper default
    is 4 and --ranks 40 matches the existing run. Rank independence is not
    yet demonstrated. No solver binary or MPI runtime is distributed.
12. Use Python 3.14, the interpreter used to check this package. The inspected
    harness declares Python >=3.12 following review; older supported versions
    have not been tested during packaging.
13. Include the tested small meshes directly. No remeshing, mesh convergence,
    spectral-radius study, MATLAB, plot, source PDF, or restart is included.
14. Keep outputs for diagnosis and omit optional cleanup. Refuse stale run
    directories instead of deleting user data automatically.
15. This is a manual/scheduled scientific benchmark, not a cheap per-commit
    CI test. A new full 10 s solve is left to the user/hardware allocation;
    existing results are used to exercise extraction and evaluation now.
16. Repository upload and PR creation are future user actions. No remote
    repository, issue, comment, commit, or PR is created by this task.
17. Mesh authorship/redistribution permission and the desired public license
    need confirmation before publication; no ownership/license is inferred.
18. Future upstream placement is proposed as
    `benchmarks/cases/fsi/block_with_flag_2d/`. The PR README inconsistently
    mentions singular `benchmark/`; the actual code tree is `benchmarks/`.
    Recheck final naming and registration after the harness merges.
