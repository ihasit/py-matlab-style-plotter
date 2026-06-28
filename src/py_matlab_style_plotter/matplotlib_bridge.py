"""Matplotlib canvas event bridge for MATLAB-like axes interaction."""

from __future__ import annotations

from typing import Any, Literal

from .interaction import InteractionMode, MouseButton, PointerEvent, View3DPreset
from .matplotlib_adapter import MatplotlibAxesPlotter


class MatplotlibEventBridge:
    """Connect Matplotlib canvas events to ``MatplotlibAxesPlotter``.

    The bridge is intentionally thin: it normalizes Matplotlib event objects and
    forwards them to the backend-neutral interaction state machine.
    """

    _EVENTS = {
        "button_press_event": "_on_button_press",
        "button_release_event": "_on_button_release",
        "motion_notify_event": "_on_motion",
        "scroll_event": "_on_scroll",
        "key_press_event": "_on_key_press",
        "key_release_event": "_on_key_release",
    }
    _MODIFIER_KEYS = {"shift", "control", "ctrl", "alt", "cmd", "super"}

    def __init__(self, plotter: MatplotlibAxesPlotter, canvas: Any | None = None) -> None:
        self.plotter = plotter
        self.canvas = canvas if canvas is not None else self._infer_canvas(plotter)
        self._connection_ids: list[int] = []
        self._active_modifiers: set[str] = set()
        self._scroll_zoom_base_scale = 1.2
        self._scroll_step_mode: Literal["unit", "raw"] = "unit"

    @property
    def scroll_zoom_base_scale(self) -> float:
        return self._scroll_zoom_base_scale

    @scroll_zoom_base_scale.setter
    def scroll_zoom_base_scale(self, value: float) -> None:
        scale = float(value)
        if scale <= 1.0:
            raise ValueError("scroll_zoom_base_scale must be greater than 1.0")
        self._scroll_zoom_base_scale = scale

    @property
    def scroll_step_mode(self) -> Literal["unit", "raw"]:
        return self._scroll_step_mode

    @scroll_step_mode.setter
    def scroll_step_mode(self, value: Literal["unit", "raw"] | str) -> None:
        normalized = str(value).lower()
        if normalized not in {"unit", "raw"}:
            raise ValueError("scroll_step_mode must be 'unit' or 'raw'")
        self._scroll_step_mode = normalized  # type: ignore[assignment]

    def connect(self) -> None:
        if self.canvas is None or self._connection_ids:
            return
        for event_name, handler_name in self._EVENTS.items():
            cid = self.canvas.mpl_connect(event_name, getattr(self, handler_name))
            self._connection_ids.append(cid)

    def disconnect(self) -> None:
        if self.canvas is None:
            self._connection_ids.clear()
            return
        for cid in self._connection_ids:
            self.canvas.mpl_disconnect(cid)
        self._connection_ids.clear()

    def set_mode(self, mode: InteractionMode | str) -> None:
        self.plotter.set_mode(mode)

    def toggle_mode(self, mode: InteractionMode | str) -> InteractionMode:
        return self.plotter.toggle_mode(mode)

    def apply_view(self, preset: View3DPreset | int) -> None:
        """Apply a MATLAB-like 3D view preset for toolbar/menu integrations."""

        view = getattr(self.plotter, "view", None)
        if view is not None:
            view(preset)
            return
        view_3d = getattr(self.plotter, "view_3d", None)
        if view_3d is not None:
            view_3d(self._legacy_view_3d_preset(preset))

    def _on_button_press(self, event: Any) -> None:
        self.plotter.on_mouse_press(self._to_pointer_event(event))

    def _on_button_release(self, event: Any) -> None:
        self.plotter.on_mouse_release(self._to_pointer_event(event))

    def _on_motion(self, event: Any) -> None:
        pointer_event = self._to_pointer_event(event)
        self.plotter.on_mouse_move(pointer_event)
        if pointer_event.axes is None and hasattr(self.plotter, "clear_coordinate_readout"):
            self.plotter.clear_coordinate_readout()

    def _on_scroll(self, event: Any) -> None:
        pointer_event = self._to_pointer_event(event)
        if self.scroll_step_mode == "unit":
            pointer_event = PointerEvent(
                axes=pointer_event.axes,
                x=pointer_event.x,
                y=pointer_event.y,
                xdata=pointer_event.xdata,
                ydata=pointer_event.ydata,
                button=pointer_event.button,
                step=self._unit_scroll_step(pointer_event.step),
                modifiers=pointer_event.modifiers,
                dblclick=pointer_event.dblclick,
            )
        self.plotter.on_scroll(pointer_event, base_scale=self.scroll_zoom_base_scale)

    def _unit_scroll_step(self, step: float) -> float:
        if step > 0:
            return 1.0
        if step < 0:
            return -1.0
        return 0.0

    def _on_key_press(self, event: Any) -> None:
        raw_key = getattr(event, "key", None)
        self._active_modifiers.update(self._normalize_modifiers(raw_key))
        key = self._normalize_key(raw_key)
        if key in {"escape", "esc"}:
            self._active_modifiers.clear()
            if hasattr(self.plotter, "cancel_interaction"):
                self.plotter.cancel_interaction()
            else:
                self.plotter.set_mode(InteractionMode.NONE)
        elif key == "n":
            self._active_modifiers.clear()
            self.plotter.set_mode(InteractionMode.NONE)
        elif key == "p":
            self.plotter.toggle_mode(InteractionMode.PAN)
        elif key == "z":
            self.plotter.toggle_mode(InteractionMode.ZOOM)
        elif key == "r":
            self.plotter.toggle_mode(InteractionMode.ROTATE3D)
        elif key == "d":
            self.plotter.toggle_mode(InteractionMode.DATA_CURSOR)
        elif key == "s":
            self.plotter.toggle_mode(InteractionMode.SELECT)
        elif key == "B":
            self.plotter.toggle_mode(InteractionMode.BRUSH)
        elif key == "o":
            self.plotter.hold("toggle")
        elif key == "h":
            self.plotter.home()
        elif key == "left":
            self.plotter.back()
        elif key == "right":
            self.plotter.forward()
        elif key in {"delete", "backspace"} and hasattr(self.plotter, "handle_delete_key"):
            self.plotter.handle_delete_key()
        elif key == "v" and hasattr(self.plotter, "toggle_selected_visibility"):
            self.plotter.toggle_selected_visibility()
        elif key == "g":
            self._toggle_grid()
        elif key == "l":
            self._toggle_legend()
        elif key == "x" and hasattr(self.plotter, "toggle_link_x_axes"):
            self.plotter.toggle_link_x_axes()
        elif key == "y" and hasattr(self.plotter, "toggle_link_y_axes"):
            self.plotter.toggle_link_y_axes()
        elif key == "b" and hasattr(self.plotter, "toggle_link_xy_axes"):
            self.plotter.toggle_link_xy_axes()
        elif key == "a":
            self.plotter.axis("auto")
        elif key == "t":
            self.plotter.axis("tight")
        elif key == "e":
            self.plotter.axis("equal")
        elif key == "f":
            self.plotter.axis("fill")
        elif key == "i":
            self.plotter.axis("image")
        elif key == "m":
            self.plotter.axis("normal")
        elif key == "q":
            self.plotter.axis("square")
        elif key == "w":
            self.plotter.axis("vis3d")
        elif key == "M":
            self.plotter.axis("manual")
        elif key == "O":
            self.plotter.axis("off")
        elif key == "U":
            self.plotter.axis("on")
        elif key == "j":
            self.plotter.axis("ij")
        elif key == "k":
            self.plotter.axis("xy")
        elif key == "2":
            self._apply_view_shortcut(2)
        elif key == "3":
            self._apply_view_shortcut(3)

    def _on_key_release(self, event: Any) -> None:
        self._active_modifiers.difference_update(self._normalize_modifiers(getattr(event, "key", None)))

    def _to_pointer_event(self, event: Any) -> PointerEvent:
        return PointerEvent(
            axes=getattr(event, "inaxes", None),
            x=getattr(event, "x", None),
            y=getattr(event, "y", None),
            xdata=getattr(event, "xdata", None),
            ydata=getattr(event, "ydata", None),
            button=self._normalize_button(getattr(event, "button", None)),
            step=float(getattr(event, "step", 0.0) or 0.0),
            modifiers=frozenset(self._active_modifiers | self._normalize_modifiers(getattr(event, "key", None))),
            dblclick=bool(getattr(event, "dblclick", False)),
        )

    def _normalize_button(self, button: Any) -> MouseButton | None:
        if button is None:
            return None
        if isinstance(button, MouseButton):
            return button
        if isinstance(button, int):
            return {
                1: MouseButton.LEFT,
                2: MouseButton.MIDDLE,
                3: MouseButton.RIGHT,
            }.get(button)
        name = getattr(button, "name", str(button)).lower()
        if name in {"left", "button1", "mousebutton.left"}:
            return MouseButton.LEFT
        if name in {"middle", "button2", "mousebutton.middle"}:
            return MouseButton.MIDDLE
        if name in {"right", "button3", "mousebutton.right"}:
            return MouseButton.RIGHT
        return None

    def _normalize_modifiers(self, key: str | None) -> frozenset[str]:
        if not key:
            return frozenset()
        parts = {part.lower() for part in key.replace("+", " ").split()}
        return frozenset(parts & self._MODIFIER_KEYS)

    def _normalize_key(self, key: str | None) -> str | None:
        if not key:
            return None
        raw_parts = key.replace("+", " ").split()
        parts = [part.lower() for part in raw_parts]
        if len(raw_parts) == 1 and parts[0] not in self._MODIFIER_KEYS:
            return raw_parts[0]
        key_parts = [part for part in parts if part not in self._MODIFIER_KEYS]
        if not key_parts:
            return None
        base_key = key_parts[-1]
        if "shift" in parts and len(base_key) == 1 and base_key.isalpha():
            return base_key.upper()
        return base_key

    def _apply_view_shortcut(self, preset: int) -> None:
        self.apply_view(preset)

    def _legacy_view_3d_preset(self, preset: View3DPreset | int) -> View3DPreset:
        if preset == 2:
            return "2d"
        if preset == 3:
            return "3d"
        return preset

    def _toggle_grid(self) -> None:
        toggle_grid = getattr(self.plotter, "toggle_grid", None)
        if toggle_grid is not None:
            toggle_grid()
            return
        grid = getattr(self.plotter, "grid", None)
        if grid is not None:
            grid("toggle")

    def _toggle_legend(self) -> None:
        toggle_legend = getattr(self.plotter, "toggle_legend", None)
        if toggle_legend is not None:
            toggle_legend()
            return
        legend = getattr(self.plotter, "legend", None)
        if legend is not None:
            legend("toggle")

    def _infer_canvas(self, plotter: MatplotlibAxesPlotter) -> Any | None:
        axes = plotter.active_axes or plotter.axes
        figure = getattr(axes, "figure", None)
        return getattr(figure, "canvas", None)
