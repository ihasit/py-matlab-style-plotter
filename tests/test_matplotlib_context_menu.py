import unittest

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
        self.assertEqual(len(disabled_style_items), 3)

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
