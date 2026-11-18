#!/usr/bin/env python3
"""Benchmark-owned extraction and scalar calculation; harness owns comparison."""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import sys
import xml.etree.ElementTree as ET

import numpy as np

ROOT = Path(__file__).resolve().parents[1]


def frequency(t, y, cycles=8):
    t, y = np.asarray(t), np.asarray(y)
    if len(t) < 50 or not np.all(np.isfinite(t)) or not np.all(np.isfinite(y)):
        raise ValueError("Insufficient or nonfinite displacement samples")
    if np.any(np.diff(t) <= 0) or np.max(np.diff(t)) > 0.015:
        raise ValueError("History must have increasing times and no missing 0.01 s outputs")
    if abs(t[-1] - 10.0) > 1e-6:
        raise ValueError("Simulation has not reached 10 seconds")
    late = t >= 6.0
    tt, yy = t[late], y[late]
    level = float(np.mean(yy))
    if np.ptp(yy) < 1e-4:
        raise ValueError("No resolved flag oscillation")
    indices = np.flatnonzero((yy[:-1] <= level) & (yy[1:] > level))
    crossings = tt[indices] + (level - yy[indices]) * (
        tt[indices + 1] - tt[indices]) / (yy[indices + 1] - yy[indices])
    if len(crossings) < cycles + 1:
        raise ValueError("Fewer than eight complete late-time periods")
    selected = crossings[-cycles - 1:]
    periods = np.diff(selected)
    if np.std(periods) / np.mean(periods) > 0.10:
        raise ValueError("Late-time periods vary by more than 10%; frequency unreliable")
    return {"frequency_hz": float(cycles / (selected[-1] - selected[0])),
            "cycles": cycles, "window_start_s": float(selected[0]),
            "window_end_s": float(selected[-1]), "crossing_level_cm": level,
            "period_cv": float(np.std(periods) / np.mean(periods)),
            "crossing_times_s": selected.tolist()}


def prepare():
    tree = ET.parse(ROOT / "case/solver.xml")
    for tag, expected in [("Number_of_time_steps", 10000),
                          ("Time_step_size", 0.001),
                          ("Spectral_radius_of_infinite_time_step", 0.5),
                          ("Continue_previous_simulation", 0)]:
        if float(tree.findtext(".//" + tag)) != expected:
            raise ValueError(f"Unexpected {tag}")
    for tag in ("Mesh_file_path", "Face_file_path"):
        for element in tree.iter(tag):
            if not (ROOT / "case" / element.text.strip()).is_file():
                raise FileNotFoundError(element.text)
    for line in (ROOT / "reference/input_sha256.txt").read_text().splitlines():
        digest, relative = line.split("  ", 1)
        if hashlib.sha256((ROOT / relative).read_bytes()).hexdigest() != digest:
            raise ValueError(f"Input checksum mismatch: {relative}")
    if list((ROOT / "case").glob("*-procs")):
        raise ValueError("Existing case/*-procs output: move it outside case before a fresh run")
    if (ROOT / "case/STOP_SIM").exists():
        raise ValueError("Remove STOP_SIM before running")


def extract(run_dir=None):
    import vtk
    directories = [Path(run_dir)] if run_dir else list((ROOT / "case").glob("*-procs"))
    if len(directories) != 1:
        raise ValueError("Expected exactly one MPI output directory")
    paths = sorted(directories[0].glob("result_*.vtu"),
                   key=lambda p: int(p.stem.split("_")[-1]))
    if not paths:
        raise ValueError("No VTU results")
    reader = vtk.vtkXMLUnstructuredGridReader()
    rows = []
    tip_id = None
    for path in paths:
        reader.SetFileName(str(path)); reader.Update()
        grid = reader.GetOutput()
        displacement = grid.GetPointData().GetArray("Displacement")
        if displacement is None:
            displacement = grid.GetPointData().GetArray("FS_Displacement")
        clock = grid.GetFieldData().GetArray("TimeValue")
        if displacement is None or clock is None:
            raise ValueError(f"Missing displacement or TimeValue in {path}")
        ids = grid.GetPointData().GetArray("GlobalNodeID")
        if tip_id is None:
            distance = [sum((grid.GetPoint(i)[j] - (9.5, 6.0, 0.0)[j])**2
                            for j in range(3)) for i in range(grid.GetNumberOfPoints())]
            index = int(np.argmin(distance))
            if distance[index] > 1e-10:
                raise ValueError("Cannot locate reference flag tip (9.5,6,0)")
            tip_id = int(ids.GetTuple1(index)) if ids is not None else None
        elif ids is not None:
            matches = [i for i in range(grid.GetNumberOfPoints())
                       if int(ids.GetTuple1(i)) == tip_id]
            if len(matches) != 1:
                raise ValueError("Flag-tip GlobalNodeID missing or ambiguous")
            index = matches[0]
        rows.append((clock.GetTuple1(0), displacement.GetTuple(index)[1]))
    out = ROOT / "validation"
    out.mkdir(exist_ok=True)
    with (out / "tip_y.csv").open("w", newline="") as stream:
        writer = csv.writer(stream); writer.writerow(["time_s", "tip_y_cm"])
        writer.writerows(rows)
    measure(out / "tip_y.csv")


def measure(path):
    data = np.loadtxt(path, delimiter=",", skiprows=1)
    # Existing ParaView exports have Time, dx, dy; native histories have t, dy.
    result = frequency(data[:, 0], data[:, -1])
    out = ROOT / "validation"; out.mkdir(exist_ok=True)
    (out / "frequency_diagnostics.json").write_text(json.dumps(result, indent=2) + "\n")
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["prepare", "extract", "evaluate", "measure"])
    parser.add_argument("--run-dir")
    parser.add_argument("--csv", type=Path)
    args = parser.parse_args()
    if args.action == "prepare": prepare()
    elif args.action == "extract": extract(args.run_dir)
    else:
        result = measure(args.csv or ROOT / "validation/tip_y.csv")
        print(format(result["frequency_hz"], ".12g"))


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(f"FSI benchmark: {error}", file=sys.stderr)
        sys.exit(1)
