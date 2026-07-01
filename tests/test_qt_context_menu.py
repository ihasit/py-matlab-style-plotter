import subprocess
import sys
import unittest
from types import SimpleNamespace
from unittest import mock

import matplotlib

matplotlib.use("Agg")

try:
    from matplotlib.backends.qt_compat import QtWidgets  # noqa

    _HAS_QT = True
except Exception:
    _HAS_QT = False

from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure

from py_matlab_style_plotter import MatplotlibAxesPlotter, MatplotlibContextMenu, MouseButton


def _figure_axes():
    fig = Figure(figsize=(4, 3), dpi=100)
    FigureCanvasAgg(fig)
    ax = fig.add_subplot(111)
    fig.canvas.draw()
    return fig, ax


def _qt_figure_axes(parent):
    from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg

    fig = Figure(figsize=(4, 3), dpi=100)
    canvas = FigureCanvasQTAgg(fig)
    canvas.setParent(parent)
    ax = fig.add_subplot(111)
    canvas.draw()
    return fig, ax


def _walk_model(items):
    for item in items:
        yield item
        if item["kind"] == "submenu":
            yield from _walk_model(item["items"])


def _walk_actions(menu, keepalive=None):
    if keepalive is None:
        keepalive = []
    for action in menu.actions():
        yield action
        submenu = action.menu()
        if submenu is not None:
            keepalive.append(submenu)
            yield from _walk_actions(submenu, keepalive)


def _find_action(menu, text):
    keepalive = []
    for action in _walk_actions(menu, keepalive):
        if action.text() == text:
            return action, keepalive
    raise LookupError(text)


def _pixmap_darkness(pixmap):
    image = pixmap.toImage().convertToFormat(pixmap.toImage().Format.Format_RGBA8888)
    total = 0.0
    samples = 0
    for y in range(image.height()):
        for x in range(image.width()):
            color = image.pixelColor(x, y)
            alpha = color.alphaF()
            if alpha <= 0.0:
                continue
            luminance = (0.2126 * color.redF()) + (0.7152 * color.greenF()) + (0.0722 * color.blueF())
            total += (1.0 - luminance) * alpha
            samples += 1
    return 0.0 if samples == 0 else total / samples


class QtContextMenuTest(unittest.TestCase):
    def setUp(self):
        self._menus = []
        self._widgets = []
        if _HAS_QT:
            self.app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
            from py_matlab_style_plotter import QtContextMenu

            QtContextMenu.close_open_menus()
            QtContextMenu._open_menus.clear()

    def tearDown(self):
        for menu in self._menus:
            try:
                menu.hide()
            except RuntimeError:
                pass
        if _HAS_QT:
            from py_matlab_style_plotter import QtContextMenu

            QtContextMenu.close_open_menus()
            QtContextMenu._open_menus.clear()
        for widget in self._widgets:
            widget.close()

    def test_importing_library_does_not_load_qt(self):
        code = (
            "import sys, py_matlab_style_plotter; "
            "print(any(m.split('.')[0] in {'PySide6','PySide2','PyQt6','PyQt5'} for m in sys.modules))"
        )
        result = subprocess.run([sys.executable, "-c", code], check=True, capture_output=True, text=True)

        self.assertEqual(result.stdout.strip(), "False")

    def test_build_menu_model_structure(self):
        fig, ax = _figure_axes()
        plotter = MatplotlibAxesPlotter(ax)
        menu = MatplotlibContextMenu(fig, plotter)

        model = menu.build_menu_model()
        first = model[0]
        submenus = [item for item in model if item["kind"] == "submenu"]
        selection_required = [item for item in model if item["kind"] == "submenu" and item["label"] in {"Marker", "Line Style", "Color"}]

        self.assertGreater(len(model), 0)
        self.assertEqual(set(first.keys()), {"kind", "label", "method", "enabled", "checked", "icon_kind"})
        self.assertTrue(any(item["kind"] == "separator" for item in model))
        self.assertTrue(any(isinstance(item["items"], list) and item["items"] for item in submenus))
        self.assertTrue(selection_required)
        self.assertFalse(selection_required[0]["enabled"])

    @unittest.skipUnless(_HAS_QT, "Qt binding is not available")
    def test_qmenu_builds_with_expected_structure(self):
        from py_matlab_style_plotter import QtContextMenu

        fig, ax = _figure_axes()
        plotter = MatplotlibAxesPlotter(ax)
        qcm = QtContextMenu(fig, plotter)
        menu = qcm.build_qmenu()
        self._menus.append(menu)
        actions = menu.actions()
        submenu = next((action.menu() for action in actions if action.menu() is not None), None)

        self.assertIsInstance(menu, QtWidgets.QMenu)
        self.assertGreater(len(actions), 5)
        self.assertIsInstance(submenu, QtWidgets.QMenu)
        self.assertTrue(any(action.isCheckable() for action in _walk_actions(menu)))
        self.assertTrue(any(action.isSeparator() for action in actions))

    @unittest.skipUnless(_HAS_QT, "Qt binding is not available")
    def test_icons_render_non_null(self):
        from py_matlab_style_plotter.qt_context_menu import QtMenuIconFactory

        fig, ax = _figure_axes()
        plotter = MatplotlibAxesPlotter(ax)
        model = MatplotlibContextMenu(fig, plotter).build_menu_model()
        kinds = [item["icon_kind"] for item in _walk_model(model) if item.get("icon_kind")]
        representative = [
            next(kind for kind in kinds if kind.startswith("color_")),
            next(kind for kind in kinds if kind.startswith("marker_")),
            next(kind for kind in kinds if kind.startswith("line_")),
        ]
        factory = QtMenuIconFactory()

        for kind in representative:
            with self.subTest(kind=kind):
                icon = factory.icon(kind)
                pixmap = icon.pixmap(16, 16)
                self.assertFalse(icon.isNull())
                self.assertGreater(pixmap.width(), 0)

    @unittest.skipUnless(_HAS_QT, "Qt binding is not available")
    def test_enabled_icons_are_stronger_than_disabled_icons(self):
        from py_matlab_style_plotter.qt_context_menu import QtMenuIconFactory

        factory = QtMenuIconFactory()
        enabled = factory.icon("cursor", disabled=False).pixmap(16, 16)
        disabled = factory.icon("cursor", disabled=True).pixmap(16, 16)

        self.assertGreater(_pixmap_darkness(enabled), _pixmap_darkness(disabled))

    @unittest.skipUnless(_HAS_QT, "Qt binding is not available")
    def test_qmenu_forces_action_icons_visible(self):
        from py_matlab_style_plotter import QtContextMenu

        fig, ax = _figure_axes()
        plotter = MatplotlibAxesPlotter(ax)
        menu = QtContextMenu(fig, plotter).build_qmenu()
        self._menus.append(menu)

        icon_actions = [action for action in _walk_actions(menu) if not action.icon().isNull()]

        self.assertTrue(icon_actions)
        self.assertTrue(all(action.isIconVisibleInMenu() for action in icon_actions))

    @unittest.skipUnless(_HAS_QT, "Qt binding is not available")
    def test_action_dispatch_invokes_plotter(self):
        from py_matlab_style_plotter import QtContextMenu

        fig, ax = _figure_axes()
        plotter = MatplotlibAxesPlotter(ax)
        plotter.home = mock.Mock()
        qcm = QtContextMenu(fig, plotter)
        menu = qcm.build_qmenu()
        self._menus.append(menu)
        home_action, keepalive = _find_action(menu, "Home")
        self._menus.extend(keepalive)

        home_action.trigger()

        plotter.home.assert_called_once_with()

    @unittest.skipUnless(_HAS_QT, "Qt binding is not available")
    def test_right_click_opens_qt_menu(self):
        from matplotlib.backends.qt_compat import QtCore
        from py_matlab_style_plotter import QtContextMenu, QtContextMenuEventBridge

        fig, ax = _figure_axes()
        plotter = MatplotlibAxesPlotter(ax)
        qcm = QtContextMenu(fig, plotter)
        bridge = QtContextMenuEventBridge(plotter, fig.canvas, qcm)
        gui_event = SimpleNamespace(globalPosition=lambda: SimpleNamespace(toPoint=lambda: QtCore.QPoint(10, 10)))
        event = SimpleNamespace(button=MouseButton.RIGHT, x=10, y=10, inaxes=ax, guiEvent=gui_event, canvas=fig.canvas)

        bridge._on_button_press(event)

        self.assertIsInstance(qcm._menu, QtWidgets.QMenu)
        self._menus.append(qcm._menu)

    @unittest.skipUnless(_HAS_QT, "Qt binding is not available")
    def test_popup_closes_other_open_menus(self):
        from py_matlab_style_plotter import QtContextMenu

        widget = QtWidgets.QWidget()
        widget.resize(240, 180)
        widget.show()
        self.app.processEvents()
        self._widgets.append(widget)
        fig_a, ax_a = _qt_figure_axes(widget)
        fig_b, ax_b = _qt_figure_axes(widget)
        plotter_a = MatplotlibAxesPlotter(ax_a)
        plotter_b = MatplotlibAxesPlotter(ax_b)
        qcm_a = QtContextMenu(fig_a, plotter_a)
        qcm_b = QtContextMenu(fig_b, plotter_b)

        pos_a = widget.mapToGlobal(widget.rect().center())
        pos_b = pos_a.__class__(pos_a.x() + 10, pos_a.y() + 10)
        qcm_a.popup(pos_a, ax_a)
        self.app.processEvents()
        self.assertIsNotNone(qcm_a._menu)
        self.assertIn(qcm_a, QtContextMenu._open_menus)

        qcm_b.popup(pos_b, ax_b)
        self.app.processEvents()

        self.assertIsNotNone(qcm_b._menu)
        self.assertIsNone(qcm_a._menu)
        self.assertNotIn(qcm_a, QtContextMenu._open_menus)
        self.assertIn(qcm_b, QtContextMenu._open_menus)
        self._menus.append(qcm_b._menu)


if __name__ == "__main__":
    unittest.main()
