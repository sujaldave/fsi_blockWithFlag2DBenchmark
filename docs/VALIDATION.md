# Packaging validation, 2026-11-11

Harness head: 82f4179946ceb9a74acd8cdb84a8ce830119174c.
Python: 3.14 in the existing postprocessing environment.

- Manifest loaded through `svbenchmark.load_benchmark`.
- Input preparation checked XML settings, every mesh/face path and SHA256.
- Fluid mesh: 45,704 points, 11,304 cells; bounds (0,19.5)x(0,12) cm.
- Flag mesh: 605 points, 120 cells; bounds (5.5,9.5)x(5.97,6.03) cm.
- Extraction read all 1,000 original `result_*.vtu` files from the existing
  40-procs-rho0p5 directory, yielding 1,000 samples at 0.01 s intervals.
- VTU extraction and the earlier exported CSV gave identical frequencies:
  3.0975052212543837 Hz.
- Last eight complete cycles span 7.35373328294474 to 9.936456935872199 s;
  period coefficient of variation is 0.0046638511 (approximately 0.47%).
- Actual `svbenchmark.runner.run_evaluation` returned `pass` for reference
  3.125 Hz and rtol 0.05 (relative error approximately 0.00879833).
- A synthetic 3.125 Hz sinusoid recovered frequency within 0.001 Hz;
  non-oscillating and incomplete histories raised errors.

No fresh solver invocation was performed. These checks exercise the manifest,
inputs, direct VTU extraction, scalar calculation and harness comparison,
but do not establish a fresh full-workflow solve on this computer or another
architecture. Generated validation files are ignored by Git; this document
records the evidence without committing simulation outputs.
