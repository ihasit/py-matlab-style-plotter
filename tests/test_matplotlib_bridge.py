import unittest
from types import SimpleNamespace

from py_matlab_style_plotter import InteractionMode, MatplotlibEventBridge, MouseButton


class FakeCanvas:
    def __init__(self):
        self.connected = []
        self.disconnected = []
        self._next_id = 1

    def mpl_connect(self, event_name, callback):
        cid = self._next_id
        self._next_id += 1
        self.connected.append((cid, event_name, callback))
        return cid

    def mpl_disconnect(self, cid):
        self.disconnected.append(cid)


class FakePlotter:
    def __init__(self):
        self.axes = "default_axes"
        self.active_axes = "active_axes"
        self.presses = []
        self.releases = []
        self.moves = []
        self.scrolls = []
        self.modes = []
        self.toggled_modes = []
        self.home_count = 0
        self.back_count = 0
        self.forward_count = 0
        self.delete_count = 0
        self.grid_count = 0
        self.legend_count = 0
        self.visibility_count = 0
        self.link_x_count = 0
        self.link_y_count = 0
        self.link_xy_count = 0
        self.clear_readout_count = 0
        self.axis_calls = []
        self.hold_calls = []
        self.view_calls = []
        self.view_3d_calls = []
        self.cancel_count = 0
        self.scroll_base_scales = []

    def on_mouse_press(self, event):
        self.presses.append(event)

    def on_mouse_release(self, event):
        self.releases.append(event)

    def on_mouse_move(self, event):
        self.moves.append(event)

    def on_scroll(self, event, base_scale=1.2):
        self.scrolls.append(event)
        self.scroll_base_scales.append(base_scale)

    def set_mode(self, mode):
        self.modes.append(InteractionMode(mode))

    def toggle_mode(self, mode):
        toggled = InteractionMode(mode)
        self.toggled_modes.append(toggled)
        return toggled

    def home(self):
        self.home_count += 1
        return True

    def back(self):
        self.back_count += 1
        return True

    def forward(self):
        self.forward_count += 1
        return True

    def handle_delete_key(self):
        self.delete_count += 1
        return True

    def toggle_grid(self):
        self.grid_count += 1

    def toggle_legend(self):
        self.legend_count += 1

    def toggle_selected_visibility(self):
        self.visibility_count += 1
        return True

    def toggle_link_x_axes(self):
        self.link_x_count += 1
        return True

    def toggle_link_y_axes(self):
        self.link_y_count += 1
        return True

    def toggle_link_xy_axes(self):
        self.link_xy_count += 1
        return True

    def axis(self, value):
        self.axis_calls.append(value)

    def hold(self, value):
        self.hold_calls.append(value)
        return True

    def view(self, value):
        self.view_calls.append(value)
        return True

    def view_3d(self, preset):
        self.view_3d_calls.append(preset)
        return True

    def clear_coordinate_readout(self):
        self.clear_readout_count += 1

    def cancel_interaction(self):
        self.cancel_count += 1


class LegacyViewPlotter:
    def __init__(self):
        self.axes = "default_axes"
        self.active_axes = "active_axes"
        self.view_3d_calls = []

    def view_3d(self, preset):
        self.view_3d_calls.append(preset)
        return True


class HelperOnlyPlotter:
    def __init__(self):
        self.axes = "default_axes"
        self.active_axes = "active_axes"
        self.grid_calls = []
        self.legend_calls = []

    def grid(self, value):
        self.grid_calls.append(value)
        return True

    def legend(self, value):
        self.legend_calls.append(value)
        return True


class MatplotlibEventBridgeTest(unittest.TestCase):
    def test_connect_and_disconnect_register_callbacks(self):
        canvas = FakeCanvas()
        bridge = MatplotlibEventBridge(FakePlotter(), canvas)

        bridge.connect()
        self.assertEqual(len(canvas.connected), 6)

        bridge.connect()
        self.assertEqual(len(canvas.connected), 6)

        bridge.disconnect()
        self.assertEqual(canvas.disconnected, [1, 2, 3, 4, 5, 6])

    def test_button_press_normalizes_event(self):
        plotter = FakePlotter()
        bridge = MatplotlibEventBridge(plotter, FakeCanvas())
        event = SimpleNamespace(
            inaxes="axes",
            x=11,
            y=22,
            xdata=1.5,
            ydata=2.5,
            button=1,
            step=0,
            key="shift+control",
            dblclick=True,
        )

        bridge._on_button_press(event)

        pointer = plotter.presses[0]
        self.assertEqual(pointer.axes, "axes")
        self.assertEqual(pointer.x, 11)
        self.assertEqual(pointer.y, 22)
        self.assertEqual(pointer.xdata, 1.5)
        self.assertEqual(pointer.ydata, 2.5)
        self.assertEqual(pointer.button, MouseButton.LEFT)
        self.assertEqual(pointer.modifiers, frozenset({"shift", "control"}))
        self.assertTrue(pointer.dblclick)

    def test_scroll_normalizes_step_to_unit_direction_by_default(self):
        plotter = FakePlotter()
        bridge = MatplotlibEventBridge(plotter, FakeCanvas())
        event = SimpleNamespace(inaxes="axes", x=0, y=0, xdata=1, ydata=2, button=None, step=3, key=None)

        bridge._on_scroll(event)

        self.assertEqual(plotter.scrolls[0].step, 1.0)
        self.assertEqual(plotter.scroll_base_scales[0], 1.2)

    def test_scroll_raw_mode_keeps_backend_step(self):
        plotter = FakePlotter()
        bridge = MatplotlibEventBridge(plotter, FakeCanvas())
        bridge.scroll_step_mode = "raw"
        event = SimpleNamespace(inaxes="axes", x=0, y=0, xdata=1, ydata=2, button=None, step=-4, key=None)

        bridge._on_scroll(event)

        self.assertEqual(plotter.scrolls[0].step, -4.0)

    def test_scroll_uses_configured_zoom_base_scale(self):
        plotter = FakePlotter()
        bridge = MatplotlibEventBridge(plotter, FakeCanvas())
        bridge.scroll_zoom_base_scale = 1.08
        event = SimpleNamespace(inaxes="axes", x=0, y=0, xdata=1, ydata=2, button=None, step=1, key=None)

        bridge._on_scroll(event)

        self.assertEqual(plotter.scroll_base_scales[0], 1.08)

    def test_scroll_step_mode_rejects_invalid_values(self):
        bridge = MatplotlibEventBridge(FakePlotter(), FakeCanvas())

        with self.assertRaises(ValueError):
            bridge.scroll_step_mode = "pixel"

    def test_scroll_zoom_base_scale_rejects_non_zooming_values(self):
        bridge = MatplotlibEventBridge(FakePlotter(), FakeCanvas())

        with self.assertRaises(ValueError):
            bridge.scroll_zoom_base_scale = 1.0

    def test_motion_outside_axes_clears_coordinate_readout(self):
        plotter = FakePlotter()
        bridge = MatplotlibEventBridge(plotter, FakeCanvas())
        event = SimpleNamespace(inaxes=None, x=0, y=0, xdata=None, ydata=None, button=None, step=0, key=None)

        bridge._on_motion(event)

        self.assertEqual(len(plotter.moves), 1)
        self.assertEqual(plotter.clear_readout_count, 1)

    def test_modifier_state_persists_across_pointer_events_until_key_release(self):
        plotter = FakePlotter()
        bridge = MatplotlibEventBridge(plotter, FakeCanvas())

        bridge._on_key_press(SimpleNamespace(key="shift"))
        bridge._on_motion(SimpleNamespace(inaxes="axes", x=1, y=2, xdata=3, ydata=4, button=None, step=0, key=None))
        bridge._on_button_release(SimpleNamespace(inaxes="axes", x=1, y=2, xdata=3, ydata=4, button=1, step=0, key=None))
        bridge._on_key_release(SimpleNamespace(key="shift"))
        bridge._on_button_press(SimpleNamespace(inaxes="axes", x=1, y=2, xdata=3, ydata=4, button=1, step=0, key=None))

        self.assertEqual(plotter.moves[0].modifiers, frozenset({"shift"}))
        self.assertEqual(plotter.releases[0].modifiers, frozenset({"shift"}))
        self.assertEqual(plotter.presses[0].modifiers, frozenset())

    def test_escape_clears_active_modifier_state(self):
        plotter = FakePlotter()
        bridge = MatplotlibEventBridge(plotter, FakeCanvas())

        bridge._on_key_press(SimpleNamespace(key="shift"))
        bridge._on_key_press(SimpleNamespace(key="escape"))
        bridge._on_button_press(SimpleNamespace(inaxes="axes", x=1, y=2, xdata=3, ydata=4, button=1, step=0, key=None))

        self.assertEqual(plotter.cancel_count, 1)
        self.assertEqual(plotter.presses[0].modifiers, frozenset())

    def test_modified_key_shortcuts_normalize_backend_key_strings(self):
        plotter = FakePlotter()
        bridge = MatplotlibEventBridge(plotter, FakeCanvas())

        bridge._on_key_press(SimpleNamespace(key="shift+b"))
        bridge._on_key_press(SimpleNamespace(key="shift+m"))
        bridge._on_key_press(SimpleNamespace(key="shift+o"))
        bridge._on_key_press(SimpleNamespace(key="shift+u"))
        bridge._on_key_press(SimpleNamespace(key="ctrl+x"))

        self.assertEqual(plotter.toggled_modes, [InteractionMode.BRUSH])
        self.assertEqual(plotter.axis_calls, ["manual", "off", "on"])
        self.assertEqual(plotter.link_x_count, 1)

    def test_key_shortcuts(self):
        plotter = FakePlotter()
        bridge = MatplotlibEventBridge(plotter, FakeCanvas())

        bridge._on_key_press(SimpleNamespace(key="escape"))
        bridge._on_key_press(SimpleNamespace(key="n"))
        bridge._on_key_press(SimpleNamespace(key="p"))
        bridge._on_key_press(SimpleNamespace(key="z"))
        bridge._on_key_press(SimpleNamespace(key="r"))
        bridge._on_key_press(SimpleNamespace(key="d"))
        bridge._on_key_press(SimpleNamespace(key="s"))
        bridge._on_key_press(SimpleNamespace(key="B"))
        bridge._on_key_press(SimpleNamespace(key="o"))
        bridge._on_key_press(SimpleNamespace(key="h"))
        bridge._on_key_press(SimpleNamespace(key="left"))
        bridge._on_key_press(SimpleNamespace(key="right"))
        bridge._on_key_press(SimpleNamespace(key="delete"))
        bridge._on_key_press(SimpleNamespace(key="backspace"))
        bridge._on_key_press(SimpleNamespace(key="v"))
        bridge._on_key_press(SimpleNamespace(key="g"))
        bridge._on_key_press(SimpleNamespace(key="l"))
        bridge._on_key_press(SimpleNamespace(key="x"))
        bridge._on_key_press(SimpleNamespace(key="y"))
        bridge._on_key_press(SimpleNamespace(key="b"))
        bridge._on_key_press(SimpleNamespace(key="a"))
        bridge._on_key_press(SimpleNamespace(key="t"))
        bridge._on_key_press(SimpleNamespace(key="e"))
        bridge._on_key_press(SimpleNamespace(key="f"))
        bridge._on_key_press(SimpleNamespace(key="i"))
        bridge._on_key_press(SimpleNamespace(key="m"))
        bridge._on_key_press(SimpleNamespace(key="q"))
        bridge._on_key_press(SimpleNamespace(key="w"))
        bridge._on_key_press(SimpleNamespace(key="M"))
        bridge._on_key_press(SimpleNamespace(key="O"))
        bridge._on_key_press(SimpleNamespace(key="U"))
        bridge._on_key_press(SimpleNamespace(key="j"))
        bridge._on_key_press(SimpleNamespace(key="k"))
        bridge._on_key_press(SimpleNamespace(key="2"))
        bridge._on_key_press(SimpleNamespace(key="3"))

        self.assertEqual(
            plotter.toggled_modes,
            [
                InteractionMode.PAN,
                InteractionMode.ZOOM,
                InteractionMode.ROTATE3D,
                InteractionMode.DATA_CURSOR,
                InteractionMode.SELECT,
                InteractionMode.BRUSH,
            ],
        )
        self.assertEqual(plotter.modes, [InteractionMode.NONE])
        self.assertEqual(plotter.cancel_count, 1)
        self.assertEqual(plotter.home_count, 1)
        self.assertEqual(plotter.back_count, 1)
        self.assertEqual(plotter.forward_count, 1)
        self.assertEqual(plotter.delete_count, 2)
        self.assertEqual(plotter.visibility_count, 1)
        self.assertEqual(plotter.grid_count, 1)
        self.assertEqual(plotter.legend_count, 1)
        self.assertEqual(plotter.link_x_count, 1)
        self.assertEqual(plotter.link_y_count, 1)
        self.assertEqual(plotter.link_xy_count, 1)
        self.assertEqual(
            plotter.axis_calls,
            ["auto", "tight", "equal", "fill", "image", "normal", "square", "vis3d", "manual", "off", "on", "ij", "xy"],
        )
        self.assertEqual(plotter.hold_calls, ["toggle"])
        self.assertEqual(plotter.view_calls, [2, 3])
        self.assertEqual(plotter.view_3d_calls, [])

    def test_view_shortcuts_fall_back_to_legacy_view_3d_method(self):
        plotter = LegacyViewPlotter()
        bridge = MatplotlibEventBridge(plotter, FakeCanvas())

        bridge._on_key_press(SimpleNamespace(key="2"))
        bridge._on_key_press(SimpleNamespace(key="3"))

        self.assertEqual(plotter.view_3d_calls, ["2d", "3d"])

    def test_grid_and_legend_shortcuts_fall_back_to_base_helpers(self):
        plotter = HelperOnlyPlotter()
        bridge = MatplotlibEventBridge(plotter, FakeCanvas())

        bridge._on_key_press(SimpleNamespace(key="g"))
        bridge._on_key_press(SimpleNamespace(key="l"))

        self.assertEqual(plotter.grid_calls, ["toggle"])
        self.assertEqual(plotter.legend_calls, ["toggle"])

    def test_apply_view_supports_toolbar_view_presets(self):
        plotter = FakePlotter()
        bridge = MatplotlibEventBridge(plotter, FakeCanvas())

        bridge.apply_view("xy")
        bridge.apply_view("xz")
        bridge.apply_view("yz")
        bridge.apply_view(2)
        bridge.apply_view(3)

        self.assertEqual(plotter.view_calls, ["xy", "xz", "yz", 2, 3])
        self.assertEqual(plotter.view_3d_calls, [])

    def test_apply_view_falls_back_to_legacy_view_3d_presets(self):
        plotter = LegacyViewPlotter()
        bridge = MatplotlibEventBridge(plotter, FakeCanvas())

        bridge.apply_view("xy")
        bridge.apply_view("xz")
        bridge.apply_view("yz")
        bridge.apply_view(2)
        bridge.apply_view(3)

        self.assertEqual(plotter.view_3d_calls, ["xy", "xz", "yz", "2d", "3d"])


if __name__ == "__main__":
    unittest.main()
