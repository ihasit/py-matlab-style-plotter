"""Qt-native context menu backend for Matplotlib figures."""

from __future__ import annotations

from typing import Any
import weakref

import numpy as np

from .matplotlib_bridge import MatplotlibEventBridge
from .matplotlib_context_menu import MatplotlibContextMenu, MatplotlibContextMenuActions, draw_menu_icon_on_axes


def _load_qt():
    try:
        from matplotlib.backends.qt_compat import QtCore, QtGui, QtWidgets
    except ImportError as exc:
        raise ImportError(
            "Qt context menu requires a Qt binding (PySide6/PyQt6/PyQt5). "
            "Install the 'qt' extra or run under a Qt Matplotlib backend."
        ) from exc
    return QtWidgets, QtGui, QtCore


class QtMenuIconFactory:
    def __init__(self, *, dpi: int = 16, size_px: int = 16) -> None:
        self.dpi = dpi
        self.size_px = size_px
        self._cache: dict[tuple[str, bool], Any] = {}

    def icon(self, kind: str | None, *, disabled: bool = False):
        _QtWidgets, QtGui, _QtCore = _load_qt()
        if kind is None:
            return None
        key = (kind, bool(disabled))
        if key in self._cache:
            return self._cache[key]
        try:
            icon = QtGui.QIcon()
            normal_pixmap = self._render_pixmap(QtGui, kind, disabled=False)
            disabled_pixmap = self._render_pixmap(QtGui, kind, disabled=True)
            icon.addPixmap(normal_pixmap, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
            icon.addPixmap(normal_pixmap, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On)
            icon.addPixmap(disabled_pixmap, QtGui.QIcon.Mode.Disabled, QtGui.QIcon.State.Off)
            icon.addPixmap(disabled_pixmap, QtGui.QIcon.Mode.Disabled, QtGui.QIcon.State.On)
            if disabled:
                icon = QtGui.QIcon(disabled_pixmap)
        except Exception:
            icon = QtGui.QIcon()
        self._cache[key] = icon
        return icon

    def _render_pixmap(self, QtGui: Any, kind: str, *, disabled: bool):
        from matplotlib.backends.backend_agg import FigureCanvasAgg
        from matplotlib.figure import Figure

        fig = Figure(figsize=(self.size_px / self.dpi, self.size_px / self.dpi), dpi=self.dpi)
        fig.patch.set_alpha(0.0)
        FigureCanvasAgg(fig)
        ax = fig.add_axes([0, 0, 1, 1])
        ax.set_axis_off()
        draw_menu_icon_on_axes(ax, kind, disabled=disabled)
        fig.canvas.draw()
        buf = np.asarray(fig.canvas.buffer_rgba())
        height, width, _channels = buf.shape
        image = QtGui.QImage(buf.tobytes(), width, height, width * 4, QtGui.QImage.Format.Format_RGBA8888).copy()
        return QtGui.QPixmap.fromImage(image)


class QtContextMenu:
    _open_menus: "weakref.WeakSet[QtContextMenu]" = weakref.WeakSet()

    def __init__(
        self,
        fig: Any,
        plotter: Any,
        actions: MatplotlibContextMenuActions | None = None,
        *,
        icon_factory: QtMenuIconFactory | None = None,
    ) -> None:
        self.fig = fig
        self.plotter = plotter
        self.actions = actions if actions is not None else MatplotlibContextMenuActions(None, plotter)
        self._menu_model_source = MatplotlibContextMenu(fig, plotter, self.actions)
        self.icons = icon_factory if icon_factory is not None else QtMenuIconFactory()
        self._menu = None

    @classmethod
    def close_open_menus(cls, *, _except: Any = None) -> None:
        for inst in list(cls._open_menus):
            if inst is _except:
                continue
            try:
                inst.close()
            except Exception:
                pass

    def build_qmenu(self, parent: Any = None):
        QtWidgets, _QtGui, _QtCore = _load_qt()
        menu = QtWidgets.QMenu(parent)
        menu._pmsp_owned_menus = []
        menu._pmsp_owned_actions = []
        menu._pmsp_owned_menu_actions = []
        self._populate_menu(menu, self._menu_model_source.build_menu_model(), root=menu)
        return menu

    def popup(self, global_pos: Any, axes: Any = None) -> None:
        QtWidgets, _QtGui, QtCore = _load_qt()
        if axes is not None:
            self.plotter.set_active_axes(axes)
        parent = self.fig.canvas if isinstance(getattr(self.fig, "canvas", None), QtWidgets.QWidget) else None
        type(self).close_open_menus(_except=self)
        menu = self.build_qmenu(parent)
        if not isinstance(global_pos, QtCore.QPoint):
            global_pos = QtCore.QPoint(int(global_pos[0]), int(global_pos[1]))
        self._menu = menu
        menu.aboutToHide.connect(lambda menu=menu: self._on_menu_hidden(menu))
        menu.popup(global_pos)
        type(self)._open_menus.add(self)

    def close(self) -> None:
        menu = self._menu
        type(self)._open_menus.discard(self)
        if menu is None:
            return
        try:
            menu.hide()
        except Exception:
            pass
        if self._menu is menu:
            self._menu = None

    def _on_menu_hidden(self, menu: Any) -> None:
        type(self)._open_menus.discard(self)
        if self._menu is menu:
            self._menu = None

    def _populate_menu(self, menu: Any, items: list[dict], *, root: Any) -> None:
        for item in items:
            kind = item["kind"]
            if kind == "separator":
                separator = menu.addSeparator()
                self._own_qaction(root, separator)
                continue
            if kind == "submenu":
                submenu = menu.addMenu(item["label"])
                self._own_qmenu(root, submenu)
                submenu.setEnabled(bool(item["enabled"]))
                icon = self.icons.icon(item.get("icon_kind"), disabled=not bool(item["enabled"]))
                if icon is not None:
                    action = submenu.menuAction()
                    action.setIcon(icon)
                    self._set_icon_visible_in_menu(action)
                self._populate_menu(submenu, item["items"], root=root)
                continue
            action = menu.addAction(item["label"])
            self._own_qaction(root, action)
            icon = self.icons.icon(item.get("icon_kind"), disabled=not bool(item["enabled"]))
            if icon is not None:
                action.setIcon(icon)
                self._set_icon_visible_in_menu(action)
            action.setEnabled(bool(item["enabled"]))
            if item.get("checked", False):
                action.setCheckable(True)
                action.setChecked(True)
            action.triggered.connect(self._make_handler(item["method"]))

    def _make_handler(self, method: str):
        return lambda *_args: getattr(self.actions, method)()

    def _set_icon_visible_in_menu(self, action: Any) -> None:
        setter = getattr(action, "setIconVisibleInMenu", None)
        if setter is None:
            return
        setter(True)

    def _own_qmenu(self, root: Any, submenu: Any) -> None:
        root._pmsp_owned_menus.append(submenu)
        root._pmsp_owned_menu_actions.append(submenu.menuAction())

    def _own_qaction(self, root: Any, action: Any) -> None:
        root._pmsp_owned_actions.append(action)


class QtContextMenuEventBridge(MatplotlibEventBridge):
    def __init__(
        self,
        plotter: Any,
        canvas: Any | None = None,
        context_menu: QtContextMenu | None = None,
    ) -> None:
        if isinstance(canvas, QtContextMenu) and context_menu is None:
            context_menu = canvas
            canvas = None
        if context_menu is None:
            raise TypeError("context_menu is required")
        super().__init__(plotter, canvas)
        self.context_menu = context_menu
        self.context_menu.actions.set_bridge(self)

    def _on_button_press(self, event: Any) -> None:
        if self._is_right_click(getattr(event, "button", None)):
            global_pos = self._global_pos_from_event(event)
            axes = getattr(event, "inaxes", None) or self.plotter.active_axes
            self.context_menu.popup(global_pos, axes)
            return
        super()._on_button_press(event)

    def _global_pos_from_event(self, event: Any) -> Any:
        gui = getattr(event, "guiEvent", None)
        global_position = getattr(gui, "globalPosition", None)
        if callable(global_position):
            return global_position().toPoint()
        global_pos = getattr(gui, "globalPos", None)
        if callable(global_pos):
            return global_pos()
        _QtWidgets, _QtGui, QtCore = _load_qt()
        canvas = self.context_menu.fig.canvas
        height = canvas.height() if hasattr(canvas, "height") else 0
        return canvas.mapToGlobal(QtCore.QPoint(int(event.x), int(height - event.y)))

    def _is_right_click(self, button: Any) -> bool:
        if button == 3:
            return True
        name = getattr(button, "name", str(button)).lower()
        return name in {"right", "button3", "mousebutton.right"}
