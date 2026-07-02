import unittest
import csv
import json
import tempfile
from pathlib import Path
from unittest import mock

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt

from py_matlab_style_plotter import (
    InteractionMode,
    MatplotlibAxesPlotter,
    MatplotlibContextMenu,
    MatplotlibContextMenuEventBridge,
)


class FakeMouseEvent:
    def __init__(self, x, y, *, axes, button):
        self.x = x
        self.y = y
        self.inaxes = axes
        self.button = button
        self.xdata = None
        self.ydata = None
        self.key = None


def _checked(model, submenu_label, item_label):
    submenu = next(item for item in model if item.get("label") == submenu_label)
    action = next(item for item in submenu["items"] if item.get("label") == item_label)
    return bool(action.get("checked"))


class MatplotlibContextMenuTest(unittest.TestCase):
    def test_right_click_opens_menu_without_creating_axes(self):
        fig, axes = plt.subplots()
        plotter = MatplotlibAxesPlotter(axes)
        menu = MatplotlibContextMenu(fig, plotter)
        bridge = MatplotlibContextMenuEventBridge(plotter, fig.canvas, menu)

        axes_count = len(fig.axes)
        event = FakeMouseEvent(100, 100, axes=axes, button=3)

        self.assertTrue(menu._on_press(event))
        self.assertEqual(len(fig.axes), axes_count)
        self.assertGreater(len(menu._items), 0)
        self.assertIs(menu.actions.bridge, bridge)

        menu.close()
        plt.close(fig)

    def test_public_open_opens_menu_without_private_method(self):
        fig, axes = plt.subplots()
        plotter = MatplotlibAxesPlotter(axes)
        menu = MatplotlibContextMenu(fig, plotter)

        menu.open(0.2, 0.8, axes)

        self.assertGreater(len(menu._items), 0)
        self.assertIs(plotter.active_axes, axes)
        menu.close()
        plt.close(fig)

    def test_context_menu_bridge_can_infer_canvas(self):
        fig, axes = plt.subplots()
        plotter = MatplotlibAxesPlotter(axes)
        menu = MatplotlibContextMenu(fig, plotter)

        bridge = MatplotlibContextMenuEventBridge(plotter, context_menu=menu)

        self.assertIs(bridge.canvas, fig.canvas)
        self.assertIs(menu.actions.bridge, bridge)
        plt.close(fig)

    def test_context_menu_bridge_accepts_menu_as_second_argument(self):
        fig, axes = plt.subplots()
        plotter = MatplotlibAxesPlotter(axes)
        menu = MatplotlibContextMenu(fig, plotter)

        bridge = MatplotlibContextMenuEventBridge(plotter, menu)

        self.assertIs(bridge.canvas, fig.canvas)
        self.assertIs(menu.actions.bridge, bridge)
        plt.close(fig)

    def test_menu_action_toggles_plotter_mode(self):
        fig, axes = plt.subplots()
        plotter = MatplotlibAxesPlotter(axes)
        menu = MatplotlibContextMenu(fig, plotter)
        MatplotlibContextMenuEventBridge(plotter, fig.canvas, menu)

        menu.actions.matlab_pan()

        self.assertEqual(plotter.mode, InteractionMode.PAN)
        self.assertIsNotNone(plotter._mode_label_artist)
        self.assertEqual(plotter._mode_label_artist.get_text(), "Pan")
        plt.close(fig)

    def test_right_click_opens_menu_in_zoom_mode(self):
        fig, axes = plt.subplots()
        plotter = MatplotlibAxesPlotter(axes)
        plotter.set_mode("zoom")
        menu = MatplotlibContextMenu(fig, plotter)

        event = FakeMouseEvent(100, 100, axes=axes, button=3)

        self.assertTrue(menu._on_press(event))
        self.assertGreater(len(menu._items), 0)

        menu.close()
        plt.close(fig)

    def test_right_click_another_axes_reopens_menu_with_one_click(self):
        fig, (axes_a, axes_b) = plt.subplots(1, 2)
        plotter = MatplotlibAxesPlotter(axes_a)
        menu = MatplotlibContextMenu(fig, plotter)

        x_a, y_a = axes_a.transAxes.transform((0.5, 0.5))
        x_b, y_b = axes_b.transAxes.transform((0.5, 0.5))

        self.assertTrue(menu._on_press(FakeMouseEvent(x_a, y_a, axes=axes_a, button=3)))
        first_patch = menu._items[0]["patch"]
        self.assertIs(plotter.active_axes, axes_a)

        self.assertTrue(menu._on_press(FakeMouseEvent(x_b, y_b, axes=axes_b, button=3)))

        self.assertGreater(len(menu._items), 0)
        self.assertIs(plotter.active_axes, axes_b)
        self.assertNotIn(first_patch, [item["patch"] for item in menu._items])

        menu.close()
        plt.close(fig)

    def test_menu_marks_current_mode_with_check(self):
        fig, axes = plt.subplots()
        plotter = MatplotlibAxesPlotter(axes)
        plotter.set_mode("brush")
        menu = MatplotlibContextMenu(fig, plotter)

        event = FakeMouseEvent(100, 100, axes=axes, button=3)

        self.assertTrue(menu._on_press(event))
        checked_lines = [line for line in fig.lines if line.get_gid() == "_py_matlab_style_context_menu_check"]
        self.assertEqual(len(checked_lines), 1)

        menu.close()
        plt.close(fig)

    def test_menu_size_stays_compact(self):
        fig, axes = plt.subplots()
        plotter = MatplotlibAxesPlotter(axes)
        menu = MatplotlibContextMenu(fig, plotter)

        event = FakeMouseEvent(100, 100, axes=axes, button=3)
        self.assertTrue(menu._on_press(event))

        self.assertLessEqual(menu._items[0]["menu_width"], 0.155)
        self.assertGreater(menu._items[0]["menu_width"], 0.10)
        self.assertLessEqual(menu._items[0]["menu_height"], 0.49)
        self.assertGreater(menu._items[0]["menu_height"], 0.36)

        menu.close()
        plt.close(fig)

    def test_menu_checks_display_link_and_selected_line_style_state(self):
        fig, axes = plt.subplots()
        line, = axes.plot([0, 1], [0, 1], label="a", marker="s", linestyle="--", color="#A2142F")
        axes.grid(True)
        axes.legend()
        plotter = MatplotlibAxesPlotter(axes)
        plotter.set_active_axes(axes)
        plotter.linked_axes_state["x"] = True
        plotter.select_line(line)
        menu = MatplotlibContextMenu(fig, plotter)

        model = menu.build_menu_model()

        self.assertTrue(_checked(model, "Display", "Grid"))
        self.assertTrue(_checked(model, "Display", "Legend"))
        self.assertTrue(_checked(model, "Link Axes", "Link X"))
        self.assertFalse(_checked(model, "Link Axes", "Link Y"))
        self.assertTrue(_checked(model, "Marker", "Square"))
        self.assertTrue(_checked(model, "Line Style", "Dashed"))
        self.assertTrue(_checked(model, "Color", "Red"))
        self.assertFalse(_checked(model, "Marker", "Circle"))

        plt.close(fig)

    def test_menu_model_includes_auto_view_and_export_data(self):
        fig, axes = plt.subplots()
        plotter = MatplotlibAxesPlotter(axes)
        menu = MatplotlibContextMenu(fig, plotter)

        model = menu.build_menu_model()
        view = next(item for item in model if item.get("label") == "View")
        export = next(item for item in model if item.get("label") == "Export Data")

        self.assertTrue(any(item.get("label") == "Auto View" and item.get("method") == "matlab_auto_view" for item in view["items"]))
        self.assertEqual([item.get("method") for item in export["items"]], ["matlab_export_csv", "matlab_export_json"])

        plt.close(fig)

    def test_menu_model_includes_color_scale_controls(self):
        fig, axes = plt.subplots()
        image = axes.imshow([[0, 1], [2, 3]])
        plotter = MatplotlibAxesPlotter(axes)
        plotter.set_active_axes(axes)
        menu = MatplotlibContextMenu(fig, plotter)

        model = menu.build_menu_model()
        color_scale = next(item for item in model if item.get("label") == "Color Scale")
        colormap = next(item for item in color_scale["items"] if item.get("label") == "Colormap")

        self.assertFalse(color_scale["enabled"] is False)
        self.assertIn("matlab_clim_auto", [item.get("method") for item in color_scale["items"]])
        self.assertIn("matlab_clim_set", [item.get("method") for item in color_scale["items"]])
        self.assertIn("matlab_colormap_hot", [item.get("method") for item in colormap["items"]])
        self.assertTrue(any(item.get("label") == "Viridis" and item.get("checked") for item in colormap["items"]))
        self.assertEqual(image.get_cmap().name, "viridis")

        plt.close(fig)

    def test_color_scale_menu_is_disabled_without_mappable_data(self):
        fig, axes = plt.subplots()
        plotter = MatplotlibAxesPlotter(axes)
        plotter.set_active_axes(axes)
        menu = MatplotlibContextMenu(fig, plotter)

        model = menu.build_menu_model()
        color_scale = next(item for item in model if item.get("label") == "Color Scale")

        self.assertFalse(color_scale["enabled"])
        plt.close(fig)

    def test_color_scale_actions_set_clim_and_colormap(self):
        fig, axes = plt.subplots()
        image = axes.imshow([[0, 1], [2, 3]])
        plotter = MatplotlibAxesPlotter(axes)
        plotter.set_active_axes(axes)
        menu = MatplotlibContextMenu(fig, plotter)

        menu.actions._prompt_text = lambda *_args: "0.25, 2.75"
        menu.actions.matlab_clim_set()
        menu.actions.matlab_colormap_hot()

        self.assertEqual(tuple(round(value, 2) for value in image.get_clim()), (0.25, 2.75))
        self.assertEqual(image.get_cmap().name, "hot")
        plt.close(fig)

    def test_auto_view_action_applies_tight_axis(self):
        fig, axes = plt.subplots()
        axes.plot([10, 20], [-5, 5])
        axes.set_xlim(0, 1)
        axes.set_ylim(0, 1)
        plotter = MatplotlibAxesPlotter(axes)
        plotter.set_active_axes(axes)
        menu = MatplotlibContextMenu(fig, plotter)

        menu.actions.matlab_auto_view()

        xlim = axes.get_xlim()
        ylim = axes.get_ylim()
        self.assertLessEqual(xlim[0], 10)
        self.assertGreaterEqual(xlim[1], 20)
        self.assertLessEqual(ylim[0], -5)
        self.assertGreaterEqual(ylim[1], 5)

        plt.close(fig)

    def test_export_actions_write_line_data_to_csv_and_json(self):
        fig, axes = plt.subplots()
        axes.set_title("export axes")
        axes.plot([0, 1, 2], [3, 4, 5], label="line a")
        plotter = MatplotlibAxesPlotter(axes)
        plotter.set_active_axes(axes)
        with tempfile.TemporaryDirectory() as tmpdir:
            paths = {
                "csv": Path(tmpdir) / "plot_data.csv",
                "json": Path(tmpdir) / "plot_data.json",
            }
            actions = menu_actions = MatplotlibContextMenu(fig, plotter).actions
            actions.export_path_provider = lambda fmt, _axes: paths[fmt]

            csv_path = menu_actions.matlab_export_csv()
            json_path = menu_actions.matlab_export_json()

            self.assertEqual(csv_path, paths["csv"])
            self.assertEqual(json_path, paths["json"])
            with paths["csv"].open(newline="", encoding="utf-8") as handle:
                rows = list(csv.DictReader(handle))
            self.assertEqual(rows[0]["artist_type"], "line")
            self.assertEqual(rows[0]["label"], "line a")
            self.assertEqual(rows[2]["x"], "2")
            self.assertEqual(rows[2]["y"], "5")
            data = json.loads(paths["json"].read_text(encoding="utf-8"))
            self.assertEqual(data["axes_title"], "export axes")
            self.assertEqual(data["artists"][0]["points"][1]["x"], 1)
            self.assertEqual(data["artists"][0]["points"][1]["y"], 4)

        plt.close(fig)

    def test_export_includes_3d_line_z_data(self):
        fig = plt.figure()
        axes = fig.add_subplot(111, projection="3d")
        axes.plot([0, 1], [2, 3], [4, 5], label="line3")
        plotter = MatplotlibAxesPlotter(axes)
        plotter.set_active_axes(axes)
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "plot3.json"
            actions = MatplotlibContextMenu(fig, plotter).actions
            actions.export_path_provider = lambda _fmt, _axes: path

            json_path = actions.matlab_export_json()

            self.assertEqual(json_path, path)
            data = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(data["artists"][0]["points"][0]["z"], 4)
            self.assertEqual(data["artists"][0]["points"][1]["z"], 5)

        plt.close(fig)

    def test_export_skips_internal_selection_highlight_artists(self):
        fig, axes = plt.subplots()
        line, = axes.plot([0, 1], [2, 3], label="line a")
        plotter = MatplotlibAxesPlotter(axes)
        plotter.set_active_axes(axes)
        plotter.select_line(line)
        menu = MatplotlibContextMenu(fig, plotter)

        data = menu.actions.collect_axes_data(axes)

        self.assertEqual(len(data["artists"]), 1)
        self.assertEqual(data["artists"][0]["label"], "line a")
        self.assertEqual(data["artists"][0]["points"][1]["y"], 3)
        plt.close(fig)

    def test_export_uses_qt_save_dialog_when_available(self):
        fig, axes = plt.subplots()
        axes.plot([0, 1], [2, 3], label="line a")
        plotter = MatplotlibAxesPlotter(axes)
        plotter.set_active_axes(axes)
        menu = MatplotlibContextMenu(fig, plotter)

        with tempfile.TemporaryDirectory() as tmpdir:
            selected = Path(tmpdir) / "chosen.csv"
            with mock.patch("matplotlib.backends.qt_compat.QtWidgets.QApplication.instance", return_value=object()):
                with mock.patch(
                    "matplotlib.backends.qt_compat.QtWidgets.QFileDialog.getSaveFileName",
                    return_value=(str(selected), "CSV files (*.csv)"),
                ) as dialog:
                    path = menu.actions.matlab_export_csv()

            self.assertEqual(path, selected)
            self.assertTrue(selected.exists())
            dialog.assert_called_once()

        plt.close(fig)

    def test_export_cancelled_qt_save_dialog_does_not_write_file(self):
        fig, axes = plt.subplots()
        axes.plot([0, 1], [2, 3], label="line a")
        plotter = MatplotlibAxesPlotter(axes)
        plotter.set_active_axes(axes)
        menu = MatplotlibContextMenu(fig, plotter)

        with mock.patch("matplotlib.backends.qt_compat.QtWidgets.QApplication.instance", return_value=object()):
            with mock.patch(
                "matplotlib.backends.qt_compat.QtWidgets.QFileDialog.getSaveFileName",
                return_value=("", "CSV files (*.csv)"),
            ):
                with mock.patch.object(menu.actions, "_tk_save_file_path", return_value=(None, False)):
                    path = menu.actions.matlab_export_csv()

        self.assertIsNone(path)
        self.assertIsNone(menu.actions.last_export_path)
        plt.close(fig)

    def test_menu_export_without_dialog_or_provider_does_not_write_default_file(self):
        fig, axes = plt.subplots()
        axes.plot([0, 1], [2, 3], label="line a")
        plotter = MatplotlibAxesPlotter(axes)
        plotter.set_active_axes(axes)
        menu = MatplotlibContextMenu(fig, plotter)

        with mock.patch.object(menu.actions, "_qt_widgets_module", return_value=None):
            with mock.patch.object(menu.actions, "_tk_save_file_path", return_value=(None, False)):
                path = menu.actions.matlab_export_csv()

        self.assertIsNone(path)
        self.assertIsNone(menu.actions.last_export_path)
        plt.close(fig)

    def test_export_uses_tk_save_dialog_when_qt_is_not_available(self):
        fig, axes = plt.subplots()
        axes.plot([0, 1], [2, 3], label="line a")
        plotter = MatplotlibAxesPlotter(axes)
        plotter.set_active_axes(axes)
        menu = MatplotlibContextMenu(fig, plotter)

        with tempfile.TemporaryDirectory() as tmpdir:
            selected = Path(tmpdir) / "chosen.json"
            with mock.patch.object(menu.actions, "_qt_widgets_module", return_value=None):
                with mock.patch.object(menu.actions, "_tk_save_file_path", return_value=(selected, True)) as dialog:
                    path = menu.actions.matlab_export_json()

            self.assertEqual(path, selected)
            self.assertTrue(selected.exists())
            dialog.assert_called_once_with("json")

        plt.close(fig)

    def test_export_provider_cancel_prevents_dialog_fallback(self):
        fig, axes = plt.subplots()
        axes.plot([0, 1], [2, 3], label="line a")
        plotter = MatplotlibAxesPlotter(axes)
        plotter.set_active_axes(axes)
        menu = MatplotlibContextMenu(fig, plotter)
        menu.actions.export_path_provider = lambda _fmt, _axes: None

        with mock.patch.object(menu.actions, "_qt_save_file_path") as qt_dialog:
            with mock.patch.object(menu.actions, "_tk_save_file_path") as tk_dialog:
                path = menu.actions.matlab_export_csv()

        self.assertIsNone(path)
        self.assertIsNone(menu.actions.last_export_path)
        qt_dialog.assert_not_called()
        tk_dialog.assert_not_called()
        plt.close(fig)

    def test_line_style_actions_apply_only_to_selected_line_and_refresh_legend(self):
        fig, axes = plt.subplots()
        line1, = axes.plot([0, 1], [0, 1], label="a", marker="o", color="blue")
        line2, = axes.plot([0, 1], [1, 0], label="b", marker="s", color="orange")
        axes.legend(loc="upper right")
        plotter = MatplotlibAxesPlotter(axes)
        plotter.select_line(line2)
        menu = MatplotlibContextMenu(fig, plotter)

        menu.actions.matlab_marker_triangle()
        menu.actions.matlab_color_red()

        self.assertEqual(line1.get_marker(), "o")
        self.assertEqual(line2.get_marker(), "^")
        self.assertEqual(line1.get_color(), "blue")
        self.assertEqual(line2.get_color(), menu.actions._COLORS["red"])

        legend = axes.get_legend()
        self.assertIsNotNone(legend)
        handles = getattr(legend, "legend_handles", getattr(legend, "legendHandles", []))
        self.assertEqual(handles[0].get_marker(), "o")
        self.assertEqual(handles[1].get_marker(), "^")
        self.assertEqual(handles[1].get_color(), menu.actions._COLORS["red"])

        plt.close(fig)

    def test_style_menu_is_disabled_without_selected_line(self):
        fig, axes = plt.subplots()
        line1, = axes.plot([0, 1], [0, 1], label="a", marker="o", color="blue")
        line2, = axes.plot([0, 1], [1, 0], label="b", marker="s", color="orange")
        plotter = MatplotlibAxesPlotter(axes)
        menu = MatplotlibContextMenu(fig, plotter)

        event = FakeMouseEvent(100, 100, axes=axes, button=3)
        self.assertTrue(menu._on_press(event))

        disabled_style_items = [
            item
            for item in menu._items
            if item["level"] == 0 and item["disabled"] and item["submenu"] is not None
        ]
        self.assertGreaterEqual(len(disabled_style_items), 3)

        marker_item = next(item for item in disabled_style_items if item["patch"].get_y() < 1.0)
        x = marker_item["patch"].get_x() + marker_item["patch"].get_width() / 2
        y = marker_item["patch"].get_y() + marker_item["patch"].get_height() / 2
        display_x, display_y = fig.transFigure.transform((x, y))
        self.assertTrue(menu._on_press(FakeMouseEvent(display_x, display_y, axes=axes, button=1)))

        self.assertTrue(all(item["level"] == 0 for item in menu._items))
        menu.actions.matlab_marker_triangle()
        menu.actions.matlab_color_red()
        self.assertEqual(line1.get_marker(), "o")
        self.assertEqual(line2.get_marker(), "s")
        self.assertEqual(line1.get_color(), "blue")
        self.assertEqual(line2.get_color(), "orange")

        menu.close()
        plt.close(fig)

    def test_right_click_line_selects_context_target_for_style_menu(self):
        fig, axes = plt.subplots()
        line, = axes.plot([0, 1], [0, 1], label="a", marker="o", color="blue")
        plotter = MatplotlibAxesPlotter(axes)
        menu = MatplotlibContextMenu(fig, plotter)
        x, y = axes.transData.transform((0.5, 0.5))

        event = FakeMouseEvent(x, y, axes=axes, button=3)
        event.xdata = 0.5
        event.ydata = 0.5
        self.assertTrue(menu._on_press(event))

        self.assertTrue(plotter.is_line_selected(line))
        style_items = [
            item
            for item in menu._items
            if item["level"] == 0 and item["submenu"] is not None and item["method"] is None
        ][:3]
        self.assertEqual([item["disabled"] for item in style_items], [False, False, False])

        menu.close()
        plt.close(fig)

    def test_marker_none_icon_is_not_x_marker(self):
        fig, axes = plt.subplots()
        plotter = MatplotlibAxesPlotter(axes)
        menu = MatplotlibContextMenu(fig, plotter)

        menu._draw_marker_icon("marker_none", 0.5, 0.5, 10)

        markers = [line.get_marker() for line in fig.lines]
        self.assertIn("o", markers)
        self.assertNotIn("x", markers)

        menu.close()
        plt.close(fig)

    def test_close_can_ignore_stale_artist_remove_errors(self):
        fig, axes = plt.subplots()
        plotter = MatplotlibAxesPlotter(axes)
        menu = MatplotlibContextMenu(fig, plotter)
        line = axes.axvline(0.5)
        menu._artists.append(line)
        line.remove()

        menu.close(ignore_remove_errors=True)

        self.assertEqual(menu._artists, [])
        plt.close(fig)


if __name__ == "__main__":
    unittest.main()
