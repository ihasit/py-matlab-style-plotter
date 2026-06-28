"""Benchmark large 2D line plotting against raw Matplotlib.

Defaults match the stress case used during optimization: 8 lines with
1,024,000 points each. Use ``--repeats`` to reduce runtime while iterating.
"""

from __future__ import annotations

import argparse
import gc
import time
import tracemalloc

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np

from py_matlab_style_plotter import AxesLimits, MatplotlibAxesPlotter


def _make_data(line_count: int, point_count: int) -> tuple[np.ndarray, np.ndarray]:
    x = np.linspace(0.0, 1000.0, point_count, dtype=np.float64)
    y = np.empty((line_count, point_count), dtype=np.float64)
    for index in range(line_count):
        y[index] = np.sin(x * (0.01 + index * 0.001)) + index * 0.2
    return x, y


def _raw_matplotlib(x: np.ndarray, y: np.ndarray) -> tuple[float, float, float]:
    fig, axes = plt.subplots(figsize=(10, 5), dpi=100)
    start = time.perf_counter()
    for row in y:
        axes.plot(x, row, linewidth=0.8)
    created = time.perf_counter()
    fig.canvas.draw()
    drawn = time.perf_counter()
    axes.set_xlim(100.0, 900.0)
    fig.canvas.draw()
    panned = time.perf_counter()
    plt.close(fig)
    return created - start, drawn - created, panned - drawn


def _plotter_matrix(x: np.ndarray, y: np.ndarray) -> tuple[float, float, float]:
    fig, axes = plt.subplots(figsize=(10, 5), dpi=100)
    plotter = MatplotlibAxesPlotter(axes)
    start = time.perf_counter()
    plotter.plot(x, y.T, linewidth=0.8)
    created = time.perf_counter()
    fig.canvas.draw()
    drawn = time.perf_counter()
    plotter.set_limits(axes, AxesLimits((100.0, 900.0), tuple(axes.get_ylim())))
    panned = time.perf_counter()
    plt.close(fig)
    return created - start, drawn - created, panned - drawn


def _plotter_separate(x: np.ndarray, y: np.ndarray) -> tuple[float, float, float]:
    fig, axes = plt.subplots(figsize=(10, 5), dpi=100)
    plotter = MatplotlibAxesPlotter(axes)
    plotter.hold("on")
    start = time.perf_counter()
    for row in y:
        plotter.plot(x, row, linewidth=0.8)
    created = time.perf_counter()
    fig.canvas.draw()
    drawn = time.perf_counter()
    plotter.set_limits(axes, AxesLimits((100.0, 900.0), tuple(axes.get_ylim())))
    panned = time.perf_counter()
    plt.close(fig)
    return created - start, drawn - created, panned - drawn


def _run_case(name: str, repeats: int, callback, x: np.ndarray, y: np.ndarray) -> None:
    results = []
    tracemalloc.start()
    for _ in range(repeats):
        gc.collect()
        results.append(callback(x, y))
    _current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    values = np.asarray(results, dtype=float)
    print(name)
    print(f"  create_s       mean/min {values[:, 0].mean():.3f} {values[:, 0].min():.3f}")
    print(f"  first_draw_s   mean/min {values[:, 1].mean():.3f} {values[:, 1].min():.3f}")
    print(f"  pan_redraw_s   mean/min {values[:, 2].mean():.3f} {values[:, 2].min():.3f}")
    print(f"  peak_memory_mb {peak / 1024 / 1024:.1f}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--lines", type=int, default=8)
    parser.add_argument("--points", type=int, default=1_024_000)
    parser.add_argument("--repeats", type=int, default=3)
    args = parser.parse_args()

    x, y = _make_data(args.lines, args.points)
    print(f"matplotlib={matplotlib.__version__} lines={args.lines} points={args.points}")
    print(f"data_mb={(x.nbytes + y.nbytes) / 1024 / 1024:.1f}")
    _run_case("raw_matplotlib", args.repeats, _raw_matplotlib, x, y)
    _run_case("plotter_matrix", args.repeats, _plotter_matrix, x, y)
    _run_case("plotter_separate", args.repeats, _plotter_separate, x, y)


if __name__ == "__main__":
    main()
