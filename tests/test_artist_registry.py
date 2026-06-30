import unittest

import matplotlib

matplotlib.use("Agg")

from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure
import numpy as np

from py_matlab_style_plotter import MatplotlibAxesPlotter


N = 25_000


def _figure_with_axes(count=1):
    fig = Figure(figsize=(6, 4), dpi=100)
    FigureCanvasAgg(fig)
    if count == 1:
        axes = fig.add_subplot(111)
        fig.canvas.draw()
        return fig, axes
    axes = [fig.add_subplot(1, count, index + 1) for index in range(count)]
    fig.canvas.draw()
    return fig, axes


def _series(count=N):
    x = np.linspace(0.0, 100.0, count)
    y = np.sin(x) + 0.1 * np.cos(17.0 * x)
    return x, y


class ArtistRegistryTest(unittest.TestCase):
    def test_register_existing_raw_line_gets_decimated(self):
        fig, ax = _figure_with_axes()
        x, y = _series()
        (line,) = ax.plot(x, y)
        plotter = MatplotlibAxesPlotter(ax)

        self.assertFalse(hasattr(line, "_pmsp_full_xy"))
        registered = plotter.register_existing_artists(ax)
        fig.canvas.draw()

        self.assertIn(line, registered)
        self.assertTrue(hasattr(line, "_pmsp_full_xy"))
        self.assertLess(len(line.get_xdata()), N)

    def test_register_below_threshold_is_ignored(self):
        fig, ax = _figure_with_axes()
        x, y = _series(1000)
        (line,) = ax.plot(x, y)
        plotter = MatplotlibAxesPlotter(ax)

        registered = plotter.register_existing_artists(ax)

        self.assertNotIn(line, registered)
        self.assertFalse(hasattr(line, "_pmsp_full_xy"))
        self.assertEqual(len(line.get_xdata()), 1000)

    def test_refresh_after_set_data_updates_original_cache(self):
        fig, ax = _figure_with_axes()
        x, y = _series()
        (line,) = ax.plot(x, y)
        plotter = MatplotlibAxesPlotter(ax)
        plotter.register_existing_artists(ax)
        new_y = np.full_like(x, 1234.0)

        line.set_data(x, new_y)
        plotter.refresh_registered_artists(ax)
        original_x, original_y = plotter.get_original_data(line)

        self.assertEqual(len(original_x), N)
        self.assertEqual(len(original_y), N)
        self.assertTrue(np.isclose(float(np.mean(original_y)), 1234.0, atol=1.0))

    def test_auto_refresh_on_draw_picks_up_set_data(self):
        fig, ax = _figure_with_axes()
        x, y = _series()
        (line,) = ax.plot(x, y)
        plotter = MatplotlibAxesPlotter(ax)
        plotter.register_existing_artists(ax)
        plotter.auto_refresh_on_draw = True
        new_y = np.full_like(x, 1234.0)

        line.set_data(x, new_y)
        fig.canvas.draw()
        _original_x, original_y = plotter.get_original_data(line)

        self.assertTrue(np.isclose(float(np.mean(original_y)), 1234.0, atol=1.0))

    def test_restore_full_resolution_returns_full_display_data(self):
        fig, ax = _figure_with_axes()
        x, y = _series()
        (line,) = ax.plot(x, y)
        plotter = MatplotlibAxesPlotter(ax)
        plotter.register_existing_artists(ax)
        self.assertLess(len(line.get_xdata()), N)

        plotter.restore_full_resolution(ax)

        self.assertEqual(len(line.get_xdata()), N)

    def test_colorbar_axes_is_not_registerable(self):
        fig, ax = _figure_with_axes()
        image = ax.imshow(np.arange(100).reshape(10, 10))
        colorbar = fig.colorbar(image, ax=ax)
        x, y = _series()
        (line,) = ax.plot(x, y)
        plotter = MatplotlibAxesPlotter(ax)

        self.assertIs(plotter._is_registerable_axes(colorbar.ax), False)
        registered = plotter.register_existing_artists(list(fig.axes))

        self.assertIn(line, registered)
        self.assertFalse(hasattr(colorbar.ax, "_pmsp_decimation_cid"))

    def test_unregister_artists_restores_and_cleans_callbacks(self):
        fig, ax = _figure_with_axes()
        x, y = _series()
        (line,) = ax.plot(x, y)
        plotter = MatplotlibAxesPlotter(ax)
        plotter.register_existing_artists(ax)
        self.assertTrue(hasattr(ax, "_pmsp_decimation_cid"))

        plotter.unregister_artists(ax)

        self.assertEqual(len(line.get_xdata()), N)
        self.assertFalse(hasattr(line, "_pmsp_full_xy"))
        self.assertFalse(getattr(ax, "_pmsp_decimated_lines", None))
        self.assertFalse(hasattr(ax, "_pmsp_decimation_cid"))

    def test_multi_axes_independent_management(self):
        fig, axes = _figure_with_axes(2)
        x, y = _series()
        (line_a,) = axes[0].plot(x, y)
        (line_b,) = axes[1].plot(x, y + 1.0)
        plotter = MatplotlibAxesPlotter(axes[0])

        registered = plotter.register_existing_artists(axes)

        self.assertIn(line_a, registered)
        self.assertIn(line_b, registered)
        self.assertEqual(len(axes[0]._pmsp_decimated_lines), 1)
        self.assertEqual(len(axes[1]._pmsp_decimated_lines), 1)
        self.assertIsNot(axes[0]._pmsp_decimated_lines, axes[1]._pmsp_decimated_lines)

    def test_get_original_data_falls_back_for_unmanaged_line(self):
        fig, ax = _figure_with_axes()
        x, y = _series(1000)
        (line,) = ax.plot(x, y)
        plotter = MatplotlibAxesPlotter(ax)

        data = plotter.get_original_data(line)

        self.assertIsNotNone(data)
        self.assertEqual(len(data[0]), 1000)
        self.assertEqual(len(data[1]), 1000)

    def test_auto_register_existing_hook(self):
        fig, axes = _figure_with_axes(2)
        x, y = _series()
        (line,) = axes[0].plot(x, y)
        plotter = MatplotlibAxesPlotter(axes[0])
        self.assertFalse(hasattr(line, "_pmsp_full_xy"))

        plotter.auto_register_existing = True
        plotter.set_active_axes(axes[1])
        plotter.set_active_axes(axes[0])

        self.assertTrue(hasattr(line, "_pmsp_full_xy"))


if __name__ == "__main__":
    unittest.main()
