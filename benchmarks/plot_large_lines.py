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
    fig.canvas.draw()
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
    fig.canvas.draw()
    panned = time.perf_counter()
    plt.close(fig)
    return created - start, drawn - created, panned - drawn


def _median_ms(fn, repeats: int) -> float:
    samples = []
    for _ in range(repeats):
        start = time.perf_counter()
        fn()
        samples.append((time.perf_counter() - start) * 1000.0)
    samples.sort()
    return samples[len(samples) // 2]


def _zoom_interaction(x: np.ndarray, y: np.ndarray, *, decimate: bool, repeats: int) -> dict[str, float]:
    fig, axes = plt.subplots(figsize=(10, 5), dpi=100)
    plotter = MatplotlibAxesPlotter(axes)
    plotter.line_decimation_enabled = decimate
    # Smooth curves are heavily collapsed by Matplotlib path simplification.
    # Noisy ADC-like data preserves frequent direction changes, which better
    # represents the target worst case and makes decimation speedup visible.
    rng = np.random.default_rng(1234)
    noisy = rng.standard_normal(x.size) * 100.0
    plotter.plot(x, noisy, linewidth=0.8)
    fig.canvas.draw()
    displayed_points = len(axes.lines[0].get_xdata())
    xmin = float(x.min())
    xmax = float(x.max())
    xspan = xmax - xmin
    lo = xmin + 0.45 * xspan
    hi = xmin + 0.55 * xspan
    y0 = float(noisy.min())
    y1 = float(noisy.max())
    yspan = y1 - y0 or 1.0

    def zoom_once() -> None:
        axes.set_xlim(lo, hi)
        fig.canvas.draw()

    zoom_samples = []
    for _ in range(repeats):
        axes.set_xlim(xmin, xmax)
        fig.canvas.draw()
        start = time.perf_counter()
        zoom_once()
        zoom_samples.append((time.perf_counter() - start) * 1000.0)
    zoom_samples.sort()
    zoom_redraw_ms = zoom_samples[len(zoom_samples) // 2]

    plotter.begin_zoom_box(axes, lo, y0)
    blit_active = plotter._zoom_box_blit is not None
    frame_index = 0

    def drag_once() -> None:
        nonlocal frame_index
        frame_index += 1
        fraction = 0.2 + 0.6 * (frame_index / max(1, repeats * 2))
        hi_i = lo + (hi - lo) * fraction
        top_i = y0 + yspan * fraction
        plotter.update_zoom_box(axes, lo, y0, hi_i, top_i)

    box_drag_frame_ms = _median_ms(drag_once, repeats * 2)
    plotter.end_zoom_box()
    plt.close(fig)
    return {
        "displayed_points": float(displayed_points),
        "zoom_redraw_ms": zoom_redraw_ms,
        "box_drag_frame_ms": box_drag_frame_ms,
        "blit_active": float(blit_active),
    }


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


def _run_zoom_case(name: str, result: dict[str, float]) -> None:
    print(name)
    print(f"  displayed_points  {int(result['displayed_points'])}")
    print(f"  zoom_redraw_ms    {result['zoom_redraw_ms']:.3f}")
    print(f"  box_drag_frame_ms {result['box_drag_frame_ms']:.3f}")
    print(f"  blit_active       {bool(result['blit_active'])}")


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
    print()
    _run_zoom_case("zoom_decimation_on", _zoom_interaction(x, y, decimate=True, repeats=args.repeats))
    _run_zoom_case("zoom_decimation_off", _zoom_interaction(x, y, decimate=False, repeats=args.repeats))


if __name__ == "__main__":
    main()
