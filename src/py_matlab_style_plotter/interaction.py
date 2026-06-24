"""Backend-neutral MATLAB-like axes interaction state.

The class in this module intentionally keeps drawing concerns out of the core
state machine. GUI integrations should translate toolkit events into
``PointerEvent`` objects and implement the small backend hooks.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from math import atan, cos, degrees, isfinite, radians, sin, tan
from typing import Any, cast, Iterable, Literal, overload, Sequence


LimitMode = Literal["auto", "manual"]
AspectMode = Literal["auto", "equal"]
BoxAspectMode = Literal["auto", "square", "vis3d"]
AspectRatioMode = Literal["auto", "manual"]
AxisDirection = Literal["normal", "reverse"]
AxisScale = Literal["linear", "log"]
AxisLayer = Literal["bottom", "top"]
TickDirection = Literal["in", "out", "both", "none"]
XAxisLocation = Literal["bottom", "top", "origin"]
YAxisLocation = Literal["left", "right", "origin"]
OnOff = Literal["on", "off"]
View3DPreset = Literal["2d", "3d", "xy", "xz", "yz"]
CameraMode = Literal["auto", "manual"]
CameraViewAngleMode = Literal["auto", "manual"]
CameraVectorMode = Literal["auto", "manual"]
CameraProjection = Literal["orthographic", "perspective"]
NextPlotMode = Literal["replace", "replacechildren", "add"]
ToolMotion = Literal["both", "horizontal", "vertical"]
Pan3DMode = Literal["camera", "limits"]
Zoom3DMode = Literal["camera", "limits"]
ZoomDirection = Literal["in", "out"]
ZoomRightClickAction = Literal["postcontextmenu", "inversezoom"]
RotateStyle = Literal["orbit", "box"]
LinkAxesAxis = Literal["x", "y", "xy"]


class InteractionMode(str, Enum):
    """Exclusive pointer interaction modes."""

    NONE = "none"
    PAN = "pan"
    ZOOM = "zoom"
    ROTATE3D = "rotate3d"
    DATA_CURSOR = "data_cursor"
    SELECT = "select"
    BRUSH = "brush"


class MouseButton(str, Enum):
    """Normalized mouse buttons used by the interaction state machine."""

    LEFT = "left"
    MIDDLE = "middle"
    RIGHT = "right"


@dataclass(frozen=True)
class AxesLimits:
    """Visible data limits for one axes."""

    xlim: tuple[float, float]
    ylim: tuple[float, float]
    zlim: tuple[float, float] | None = None
    clim: tuple[float, float] | None = None

    def normalized(self) -> "AxesLimits":
        """Return limits ordered low-to-high on each axis."""

        x0, x1 = self.xlim
        y0, y1 = self.ylim
        zlim = None
        if self.zlim is not None:
            z0, z1 = self.zlim
            zlim = (min(z0, z1), max(z0, z1))
        clim = None
        if self.clim is not None:
            c0, c1 = self.clim
            clim = (min(c0, c1), max(c0, c1))
        return AxesLimits((min(x0, x1), max(x0, x1)), (min(y0, y1), max(y0, y1)), zlim, clim)


@dataclass(frozen=True)
class ViewState:
    """One entry in the axes view history."""

    axes: Any
    limits: AxesLimits
    xlim_mode: LimitMode
    ylim_mode: LimitMode
    zlim_mode: LimitMode = "auto"
    clim_mode: LimitMode = "auto"
    xtick: tuple[float, ...] = ()
    ytick: tuple[float, ...] = ()
    ztick: tuple[float, ...] = ()
    xtick_mode: LimitMode = "auto"
    ytick_mode: LimitMode = "auto"
    ztick_mode: LimitMode = "auto"
    xticklabel: tuple[str, ...] = ()
    yticklabel: tuple[str, ...] = ()
    zticklabel: tuple[str, ...] = ()
    xticklabel_mode: LimitMode = "auto"
    yticklabel_mode: LimitMode = "auto"
    zticklabel_mode: LimitMode = "auto"
    xticklabel_rotation: float = 0.0
    yticklabel_rotation: float = 0.0
    zticklabel_rotation: float = 0.0
    xticklabel_rotation_mode: LimitMode = "auto"
    yticklabel_rotation_mode: LimitMode = "auto"
    zticklabel_rotation_mode: LimitMode = "auto"
    axes_title: tuple[str, ...] = ()
    xlabel_text: tuple[str, ...] = ()
    ylabel_text: tuple[str, ...] = ()
    zlabel_text: tuple[str, ...] = ()
    aspect: AspectMode = "auto"
    box_aspect: BoxAspectMode = "auto"
    data_aspect_ratio: tuple[float, float, float] = (1.0, 1.0, 1.0)
    data_aspect_ratio_mode: AspectRatioMode = "auto"
    plot_box_aspect_ratio: tuple[float, float, float] = (1.0, 1.0, 1.0)
    plot_box_aspect_ratio_mode: AspectRatioMode = "auto"
    axis_visible: bool = True
    grid_visible: bool = False
    minor_grid_visible: bool = False
    x_grid_visible: bool = False
    y_grid_visible: bool = False
    z_grid_visible: bool = False
    x_minor_grid_visible: bool = False
    y_minor_grid_visible: bool = False
    z_minor_grid_visible: bool = False
    x_minor_tick_visible: bool = False
    y_minor_tick_visible: bool = False
    z_minor_tick_visible: bool = False
    box_visible: bool = True
    legend_visible: bool = False
    x_direction: AxisDirection = "normal"
    y_direction: AxisDirection = "normal"
    z_direction: AxisDirection = "normal"
    x_scale: AxisScale = "linear"
    y_scale: AxisScale = "linear"
    z_scale: AxisScale = "linear"
    axis_layer: AxisLayer = "bottom"
    tick_direction: TickDirection = "in"
    tick_direction_mode: LimitMode = "auto"
    tick_length: tuple[float, float] = (0.01, 0.025)
    x_axis_location: XAxisLocation = "bottom"
    y_axis_location: YAxisLocation = "left"
    camera_mode: CameraMode = "auto"
    camera_view_angle_mode: CameraViewAngleMode = "auto"
    camera_position_mode: CameraVectorMode = "auto"
    camera_target_mode: CameraVectorMode = "auto"
    camera_up_vector_mode: CameraVectorMode = "auto"
    camera_projection: CameraProjection = "orthographic"
    hold_enabled: bool = False
    next_plot: NextPlotMode = "replace"
    color_order: tuple[tuple[float, float, float], ...] = ()
    line_style_order: tuple[str, ...] = ()
    next_series_index: int = 0
    camera: "Camera3DState | None" = None


@dataclass
class AxesUIState:
    """MATLAB axes properties tracked per concrete axes object."""

    xlim_mode: LimitMode = "auto"
    ylim_mode: LimitMode = "auto"
    zlim_mode: LimitMode = "auto"
    clim_mode: LimitMode = "auto"
    xtick: tuple[float, ...] = ()
    ytick: tuple[float, ...] = ()
    ztick: tuple[float, ...] = ()
    xtick_mode: LimitMode = "auto"
    ytick_mode: LimitMode = "auto"
    ztick_mode: LimitMode = "auto"
    xticklabel: tuple[str, ...] = ()
    yticklabel: tuple[str, ...] = ()
    zticklabel: tuple[str, ...] = ()
    xticklabel_mode: LimitMode = "auto"
    yticklabel_mode: LimitMode = "auto"
    zticklabel_mode: LimitMode = "auto"
    xticklabel_rotation: float = 0.0
    yticklabel_rotation: float = 0.0
    zticklabel_rotation: float = 0.0
    xticklabel_rotation_mode: LimitMode = "auto"
    yticklabel_rotation_mode: LimitMode = "auto"
    zticklabel_rotation_mode: LimitMode = "auto"
    axes_title: tuple[str, ...] = ()
    xlabel_text: tuple[str, ...] = ()
    ylabel_text: tuple[str, ...] = ()
    zlabel_text: tuple[str, ...] = ()
    aspect: AspectMode = "auto"
    box_aspect: BoxAspectMode = "auto"
    data_aspect_ratio: tuple[float, float, float] = (1.0, 1.0, 1.0)
    data_aspect_ratio_mode: AspectRatioMode = "auto"
    plot_box_aspect_ratio: tuple[float, float, float] = (1.0, 1.0, 1.0)
    plot_box_aspect_ratio_mode: AspectRatioMode = "auto"
    axis_visible: bool = True
    grid_visible: bool = False
    minor_grid_visible: bool = False
    x_grid_visible: bool = False
    y_grid_visible: bool = False
    z_grid_visible: bool = False
    x_minor_grid_visible: bool = False
    y_minor_grid_visible: bool = False
    z_minor_grid_visible: bool = False
    x_minor_tick_visible: bool = False
    y_minor_tick_visible: bool = False
    z_minor_tick_visible: bool = False
    box_visible: bool = True
    legend_visible: bool = False
    x_direction: AxisDirection = "normal"
    y_direction: AxisDirection = "normal"
    z_direction: AxisDirection = "normal"
    x_scale: AxisScale = "linear"
    y_scale: AxisScale = "linear"
    z_scale: AxisScale = "linear"
    axis_layer: AxisLayer = "bottom"
    tick_direction: TickDirection = "in"
    tick_direction_mode: LimitMode = "auto"
    tick_length: tuple[float, float] = (0.01, 0.025)
    x_axis_location: XAxisLocation = "bottom"
    y_axis_location: YAxisLocation = "left"
    camera_mode: CameraMode = "auto"
    camera_view_angle_mode: CameraViewAngleMode = "auto"
    camera_position_mode: CameraVectorMode = "auto"
    camera_target_mode: CameraVectorMode = "auto"
    camera_up_vector_mode: CameraVectorMode = "auto"
    camera_projection: CameraProjection = "orthographic"
    hold_enabled: bool = False
    next_plot: NextPlotMode = "replace"
    color_order: tuple[tuple[float, float, float], ...] = ()
    line_style_order: tuple[str, ...] = ()
    next_series_index: int = 0


@dataclass(frozen=True)
class Camera3DState:
    """3D camera state using MATLAB/Matplotlib view terminology."""

    azim: float
    elev: float
    roll: float = 0.0
    view_angle: float | None = None
    position: tuple[float, float, float] | None = None
    target: tuple[float, float, float] | None = None
    up_vector: tuple[float, float, float] | None = None


@dataclass(frozen=True)
class ToolState:
    """MATLAB-like exploration tool state snapshot."""

    mode: InteractionMode
    enable: Literal["on", "off"]
    active: bool
    motion: ToolMotion | None = None
    direction: ZoomDirection | None = None
    right_click_action: ZoomRightClickAction | None = None
    rotate_style: RotateStyle | None = None
    use_legacy_exploration_modes: Literal["on", "off"] = "off"


@dataclass(frozen=True)
class PlotSeries:
    """One normalized MATLAB-like ``plot`` series."""

    x: tuple[float, ...]
    y: tuple[float, ...]
    style: str | None = None
    properties: tuple[tuple[str, Any], ...] = ()
    line_spec: tuple[tuple[str, Any], ...] = ()


@dataclass(frozen=True)
class Plot3Series:
    """One normalized MATLAB-like ``plot3`` series."""

    x: tuple[float, ...]
    y: tuple[float, ...]
    z: tuple[float, ...]
    style: str | None = None
    properties: tuple[tuple[str, Any], ...] = ()
    line_spec: tuple[tuple[str, Any], ...] = ()


@dataclass(frozen=True)
class ErrorBarSeries:
    """One normalized MATLAB-like vertical ``errorbar`` series."""

    x: tuple[float, ...]
    y: tuple[float, ...]
    y_negative: tuple[float, ...]
    y_positive: tuple[float, ...]
    style: str | None = None
    properties: tuple[tuple[str, Any], ...] = ()
    line_spec: tuple[tuple[str, Any], ...] = ()


@dataclass(frozen=True)
class ScatterSeries:
    """One normalized MATLAB-like ``scatter`` series."""

    x: tuple[float, ...]
    y: tuple[float, ...]
    size: tuple[float, ...] | float | None = None
    color: Any | None = None
    properties: tuple[tuple[str, Any], ...] = ()
    line_spec: tuple[tuple[str, Any], ...] = ()


@dataclass(frozen=True)
class StemSeries:
    """One normalized MATLAB-like ``stem`` series."""

    x: tuple[float, ...]
    y: tuple[float, ...]
    style: str | None = None
    properties: tuple[tuple[str, Any], ...] = ()
    line_spec: tuple[tuple[str, Any], ...] = ()


@dataclass(frozen=True)
class BarSeries:
    """One normalized MATLAB-like vertical ``bar`` series."""

    x: tuple[float, ...]
    y: tuple[float, ...]
    style: str | None = None
    properties: tuple[tuple[str, Any], ...] = ()
    line_spec: tuple[tuple[str, Any], ...] = ()


@dataclass(frozen=True)
class AreaSeries:
    """One normalized MATLAB-like stacked ``area`` series."""

    x: tuple[float, ...]
    y: tuple[float, ...]
    baseline: tuple[float, ...]
    style: str | None = None
    properties: tuple[tuple[str, Any], ...] = ()
    line_spec: tuple[tuple[str, Any], ...] = ()


@dataclass(frozen=True)
class _PlotData:
    rows: tuple[tuple[float, ...], ...]

    @property
    def row_count(self) -> int:
        return len(self.rows)

    @property
    def column_count(self) -> int:
        return len(self.rows[0]) if self.rows else 0

    @property
    def is_vector(self) -> bool:
        return self.row_count <= 1 or self.column_count <= 1

    def as_vector(self) -> tuple[float, ...]:
        if self.row_count == 0:
            return ()
        if self.row_count == 1:
            return self.rows[0]
        if self.column_count == 1:
            return tuple(row[0] for row in self.rows)
        raise ValueError("data must be a vector")

    def column(self, index: int) -> tuple[float, ...]:
        return tuple(row[index] for row in self.rows)


@dataclass(frozen=True)
class PointerEvent:
    """Backend-neutral pointer event.

    ``xdata`` and ``ydata`` are coordinates in axes data space. Integrations
    should pass ``None`` when the pointer is outside the plotting area.
    """

    axes: Any | None
    x: float | None = None
    y: float | None = None
    xdata: float | None = None
    ydata: float | None = None
    button: Any | None = None
    step: float = 0.0
    modifiers: frozenset[str] = frozenset()
    dblclick: bool = False

    def normalized_button(self) -> MouseButton | None:
        if self.button is None:
            return None
        if isinstance(self.button, MouseButton):
            return self.button
        if isinstance(self.button, int):
            return {
                1: MouseButton.LEFT,
                2: MouseButton.MIDDLE,
                3: MouseButton.RIGHT,
            }.get(self.button)
        name = getattr(self.button, "name", str(self.button)).lower()
        if name in {"left", "button1", "mousebutton.left"}:
            return MouseButton.LEFT
        if name in {"middle", "button2", "mousebutton.middle"}:
            return MouseButton.MIDDLE
        if name in {"right", "button3", "mousebutton.right"}:
            return MouseButton.RIGHT
        try:
            return MouseButton(name)
        except ValueError:
            return None


@dataclass
class _DragState:
    axes: Any
    start_x: float
    start_y: float
    start_limits: AxesLimits
    modifiers: frozenset[str]
    start_view: ViewState | None
    start_screen_x: float | None = None
    start_screen_y: float | None = None
    start_camera: Camera3DState | None = None


@dataclass
class _ZoomDragState:
    axes: Any
    start_xdata: float
    start_ydata: float
    start_x: float | None
    start_y: float | None


@dataclass
class _BrushDragState:
    axes: Any
    start_xdata: float
    start_ydata: float


@dataclass
class _RotateDragState:
    axes: Any
    start_x: float
    start_y: float
    start_camera: Camera3DState
    start_view: ViewState | None


class MatlabLikeAxesBase:
    """MATLAB-like axes UI behavior independent from a plotting backend.

    The defaults intentionally follow MATLAB user expectations:

    - ``hold`` starts off
    - a user pan/zoom changes the corresponding limit modes to ``manual``
    - exactly one primary interaction mode is active
    - pointer clicks make an axes active before the action is handled
    """

    _VALID_NEXT_PLOT = {"replace", "replacechildren", "add"}
    _PLOT_PROPERTY_ALIASES = {
        "color": "color",
        "displayname": "label",
        "label": "label",
        "linestyle": "linestyle",
        "linewidth": "linewidth",
        "marker": "marker",
        "markeredgecolor": "markeredgecolor",
        "markerfacecolor": "markerfacecolor",
        "markersize": "markersize",
    }
    _LINE_SPEC_COLORS = set("rgbcmykw")
    _LINE_SPEC_LINESTYLES = ("--", "-.", ":", "-")
    _LINE_SPEC_MARKERS = ("square", "diamond", "pentagram", "hexagram", "none", "+", "o", "*", ".", "x", "_", "|", "s", "d", "^", "v", ">", "<", "p", "h")
    _LINE_SPEC_MARKER_ALIASES = {
        "square": "s",
        "diamond": "d",
        "pentagram": "p",
        "hexagram": "h",
    }
    DEFAULT_COLOR_ORDER: tuple[tuple[float, float, float], ...] = (
        (0.0, 0.4470, 0.7410),
        (0.8500, 0.3250, 0.0980),
        (0.9290, 0.6940, 0.1250),
        (0.4940, 0.1840, 0.5560),
        (0.4660, 0.6740, 0.1880),
        (0.3010, 0.7450, 0.9330),
        (0.6350, 0.0780, 0.1840),
    )
    DEFAULT_LINE_STYLE_ORDER: tuple[str, ...] = ("-",)
    _VIEW_3D_PRESETS: dict[View3DPreset, Camera3DState] = {
        "2d": Camera3DState(azim=0.0, elev=90.0),
        "xy": Camera3DState(azim=0.0, elev=90.0),
        "3d": Camera3DState(azim=-37.5, elev=30.0),
        "xz": Camera3DState(azim=0.0, elev=0.0),
        "yz": Camera3DState(azim=90.0, elev=0.0),
    }

    def __init__(self, axes: Any | None = None) -> None:
        self.axes = axes
        self.active_axes = axes
        self.hover_axes: Any | None = None
        self.mode = InteractionMode.NONE
        self.hold_enabled = False
        self.next_plot: NextPlotMode = "replace"
        self.color_order = self.DEFAULT_COLOR_ORDER
        self.line_style_order = self.DEFAULT_LINE_STYLE_ORDER
        self.next_series_index = 0
        self.xlim_mode: LimitMode = "auto"
        self.ylim_mode: LimitMode = "auto"
        self.zlim_mode: LimitMode = "auto"
        self.clim_mode: LimitMode = "auto"
        self.xtick: tuple[float, ...] = ()
        self.ytick: tuple[float, ...] = ()
        self.ztick: tuple[float, ...] = ()
        self.xtick_mode: LimitMode = "auto"
        self.ytick_mode: LimitMode = "auto"
        self.ztick_mode: LimitMode = "auto"
        self.xticklabel: tuple[str, ...] = ()
        self.yticklabel: tuple[str, ...] = ()
        self.zticklabel: tuple[str, ...] = ()
        self.xticklabel_mode: LimitMode = "auto"
        self.yticklabel_mode: LimitMode = "auto"
        self.zticklabel_mode: LimitMode = "auto"
        self.xticklabel_rotation = 0.0
        self.yticklabel_rotation = 0.0
        self.zticklabel_rotation = 0.0
        self.xticklabel_rotation_mode: LimitMode = "auto"
        self.yticklabel_rotation_mode: LimitMode = "auto"
        self.zticklabel_rotation_mode: LimitMode = "auto"
        self.axes_title: tuple[str, ...] = ()
        self.xlabel_text: tuple[str, ...] = ()
        self.ylabel_text: tuple[str, ...] = ()
        self.zlabel_text: tuple[str, ...] = ()
        self.axis_aspect: AspectMode = "auto"
        self.box_aspect: BoxAspectMode = "auto"
        self.data_aspect_ratio: tuple[float, float, float] = (1.0, 1.0, 1.0)
        self.data_aspect_ratio_mode: AspectRatioMode = "auto"
        self.plot_box_aspect_ratio: tuple[float, float, float] = (1.0, 1.0, 1.0)
        self.plot_box_aspect_ratio_mode: AspectRatioMode = "auto"
        self.axis_visible = True
        self.x_direction: AxisDirection = "normal"
        self.y_direction: AxisDirection = "normal"
        self.z_direction: AxisDirection = "normal"
        self.x_scale: AxisScale = "linear"
        self.y_scale: AxisScale = "linear"
        self.z_scale: AxisScale = "linear"
        self.axis_layer: AxisLayer = "bottom"
        self.tick_direction: TickDirection = "in"
        self.tick_direction_mode: LimitMode = "auto"
        self.tick_length: tuple[float, float] = (0.01, 0.025)
        self.x_axis_location: XAxisLocation = "bottom"
        self.y_axis_location: YAxisLocation = "left"
        self.camera_mode: CameraMode = "auto"
        self.camera_view_angle_mode: CameraViewAngleMode = "auto"
        self.camera_position_mode: CameraVectorMode = "auto"
        self.camera_target_mode: CameraVectorMode = "auto"
        self.camera_up_vector_mode: CameraVectorMode = "auto"
        self.camera_projection: CameraProjection = "orthographic"
        self._axes_ui_state: dict[Any, AxesUIState] = {}
        if axes is not None:
            self._save_axes_ui_state(axes)
        self.view_stack: list[ViewState] = []
        self.view_index = -1
        self._drag: _DragState | None = None
        self._zoom_drag: _ZoomDragState | None = None
        self._brush_drag: _BrushDragState | None = None
        self._rotate_drag: _RotateDragState | None = None
        self._rotate_azimuth_sensitivity = 0.0
        self._rotate_elevation_sensitivity = 0.0
        self._rotate_drag_pixel_threshold = 0.0
        self._rotate_style: RotateStyle = "orbit"
        self._elevation_limits = (-90.0, 90.0)
        self.rotate_azimuth_sensitivity = 0.18
        self.rotate_elevation_sensitivity = 0.12
        self.rotate_drag_pixel_threshold = 3.0
        self.elevation_limits = (-90.0, 90.0)
        self._pan_motion: ToolMotion = "both"
        self._pan_3d_mode: Pan3DMode = "camera"
        self._zoom_motion: ToolMotion = "both"
        self._zoom_3d_mode: Zoom3DMode = "camera"
        self._rotate_motion: ToolMotion = "both"
        self._zoom_direction: ZoomDirection = "in"
        self._zoom_right_click_action: ZoomRightClickAction = "postcontextmenu"
        self.zoom_click_scale = 0.5
        self.zoom_right_click_scale = 2.0
        self.zoom_drag_pixel_threshold = 3.0
        self.zoom_box_min_span_ratio = 1.0e-9
        self._linked: list[tuple[set[Any], LinkAxesAxis]] = []

    def set_active_axes(self, axes: Any | None) -> None:
        if self.active_axes is axes:
            return
        self._save_axes_ui_state(self.active_axes)
        old_hold = self.hold_enabled
        self.active_axes = axes
        self._load_axes_ui_state(axes)
        self.on_active_axes_changed(axes)
        if self.hold_enabled != old_hold:
            self.on_hold_changed(self.hold_enabled)
        self._select_latest_view_for_active_axes()

    def current_axes(self) -> Any | None:
        return self.active_axes

    def is_active_axes(self, axes: Any | None) -> bool:
        return self.active_axes is axes

    def set_mode(self, mode: InteractionMode | str) -> None:
        requested = InteractionMode(mode)
        previous = self.mode
        has_active_drag = self._drag is not None or self._zoom_drag is not None or self._brush_drag is not None or self._rotate_drag is not None
        if requested == previous and not has_active_drag:
            return
        self.mode = requested
        post_callbacks = self._active_action_post_callbacks()
        if self._drag is not None and self._view_changed_since(self._drag.axes, self._drag.start_view):
            self.push_current_view(self._drag.axes)
        if self._rotate_drag is not None and self._view_changed_since(self._rotate_drag.axes, self._rotate_drag.start_view):
            self.push_current_view(self._rotate_drag.axes)
        if self._zoom_drag is not None:
            self.end_zoom_box()
        if self._brush_drag is not None:
            self.end_brush_box()
        self._drag = None
        self._zoom_drag = None
        self._brush_drag = None
        self._rotate_drag = None
        for callback_mode, callback_event in post_callbacks:
            self.action_post_callback(callback_mode, callback_event)
        if self.mode != previous:
            self.on_mode_changed(self.mode)

    def toggle_mode(self, mode: InteractionMode | str) -> InteractionMode:
        """Toggle an exclusive interaction tool like MATLAB toolbar buttons."""

        requested = InteractionMode(mode)
        if requested == InteractionMode.NONE:
            self.set_mode(InteractionMode.NONE)
        elif self.mode == requested:
            self.set_mode(InteractionMode.NONE)
        else:
            self.set_mode(requested)
        return self.mode

    def active_mode(self) -> InteractionMode:
        return self.mode

    def is_mode_active(self, mode: InteractionMode | str) -> bool:
        return self.mode == InteractionMode(mode)

    def tool_state(self, mode: InteractionMode | str) -> ToolState:
        requested = InteractionMode(mode)
        active = self.mode == requested
        enable: Literal["on", "off"] = "on" if active else "off"
        if requested == InteractionMode.PAN:
            return ToolState(
                requested,
                enable,
                active,
                motion=self.pan_motion,
                use_legacy_exploration_modes=self.use_legacy_exploration_modes,
            )
        if requested == InteractionMode.ZOOM:
            return ToolState(
                requested,
                enable,
                active,
                motion=self.zoom_motion,
                direction=self.zoom_direction,
                right_click_action=self.zoom_right_click_action,
                use_legacy_exploration_modes=self.use_legacy_exploration_modes,
            )
        if requested == InteractionMode.ROTATE3D:
            return ToolState(
                requested,
                enable,
                active,
                motion=self.rotate_motion,
                rotate_style=self.rotate_style,
                use_legacy_exploration_modes=self.use_legacy_exploration_modes,
            )
        return ToolState(requested, enable, active)

    def pan_state(self) -> ToolState:
        return self.tool_state(InteractionMode.PAN)

    def zoom_state(self) -> ToolState:
        return self.tool_state(InteractionMode.ZOOM)

    def rotate3d_state(self) -> ToolState:
        return self.tool_state(InteractionMode.ROTATE3D)

    def pan(self, value: bool | str | None = None) -> InteractionMode:
        """MATLAB-like pan mode control accepting on/off/toggle."""

        return self._set_tool_mode(InteractionMode.PAN, value)

    def zoom(self, value: bool | str | None = None) -> InteractionMode:
        """MATLAB-like zoom mode control accepting on/off/toggle."""

        return self._set_tool_mode(InteractionMode.ZOOM, value)

    def rotate3d(self, value: bool | str | None = None) -> InteractionMode:
        """MATLAB-like rotate3d mode control accepting on/off/toggle."""

        return self._set_tool_mode(InteractionMode.ROTATE3D, value)

    def datacursormode(self, value: bool | str | None = None) -> InteractionMode:
        """MATLAB-like data cursor mode control accepting on/off/toggle."""

        return self._set_tool_mode(InteractionMode.DATA_CURSOR, value)

    def selectmode(self, value: bool | str | None = None) -> InteractionMode:
        """Selection mode control accepting on/off/toggle."""

        return self._set_tool_mode(InteractionMode.SELECT, value)

    def brush(self, value: bool | str | None = None) -> InteractionMode:
        """MATLAB-like brush mode control accepting on/off/toggle."""

        return self._set_tool_mode(InteractionMode.BRUSH, value)

    def plot(self, *args: Any, axes: Any | None = None, **kwargs: Any) -> list[Any]:
        """Draw MATLAB-like 2D line series on an axes.

        This template method owns MATLAB's axes lifecycle around plotting:
        active-axes selection, ``NextPlot``/``hold`` clearing, autoscaling, and
        view-history updates. Backends implement ``draw_plot_series`` for the
        actual line creation.
        """

        if axes is None and args and self.is_axes_handle(args[0]):
            axes = args[0]
            args = args[1:]
        axes = axes if axes is not None else self.require_active_axes()
        self.set_active_axes(axes)
        series = self.normalize_plot_args(args, kwargs)
        self.prepare_for_plot(axes)
        series = self._apply_plot_series_order(axes, series)
        artists = self.draw_plot_series(axes, series)
        self.after_plot(axes)
        return artists

    def plot3(self, *args: Any, axes: Any | None = None, **kwargs: Any) -> list[Any]:
        """Draw MATLAB-like 3D line series on an axes."""

        if axes is None and args and self.is_axes_handle(args[0]):
            axes = args[0]
            args = args[1:]
        axes = axes if axes is not None else self.require_active_axes()
        self.set_active_axes(axes)
        series = self.normalize_plot3_args(args, kwargs)
        self.prepare_for_plot(axes)
        series = self._apply_plot3_series_order(axes, series)
        artists = self.draw_plot3_series(axes, series)
        self.after_plot(axes)
        return artists

    def stairs(self, *args: Any, axes: Any | None = None, **kwargs: Any) -> list[Any]:
        """Draw MATLAB-like stairstep series on an axes."""

        if axes is None and args and self.is_axes_handle(args[0]):
            axes = args[0]
            args = args[1:]
        axes = axes if axes is not None else self.require_active_axes()
        self.set_active_axes(axes)
        series = self.normalize_plot_args(args, kwargs)
        series = [self._stairs_series(item) for item in series]
        self.prepare_for_plot(axes)
        series = self._apply_plot_series_order(axes, series)
        artists = self.draw_plot_series(axes, series)
        self.after_plot(axes)
        return artists

    def errorbar(self, *args: Any, axes: Any | None = None, **kwargs: Any) -> list[Any]:
        """Draw MATLAB-like vertical error-bar series on an axes."""

        if axes is None and args and self.is_axes_handle(args[0]):
            axes = args[0]
            args = args[1:]
        axes = axes if axes is not None else self.require_active_axes()
        self.set_active_axes(axes)
        series = self.normalize_errorbar_args(args, kwargs)
        self.prepare_for_plot(axes)
        series = self._apply_errorbar_series_order(axes, series)
        artists = self.draw_errorbar_series(axes, series)
        self.after_plot(axes)
        return artists

    def scatter(self, *args: Any, axes: Any | None = None, **kwargs: Any) -> list[Any]:
        """Draw MATLAB-like scatter series on an axes."""

        if axes is None and args and self.is_axes_handle(args[0]):
            axes = args[0]
            args = args[1:]
        axes = axes if axes is not None else self.require_active_axes()
        self.set_active_axes(axes)
        series = self.normalize_scatter_args(args, kwargs)
        self.prepare_for_plot(axes)
        series = self._apply_scatter_series_order(axes, series)
        artists = self.draw_scatter_series(axes, series)
        self.after_plot(axes)
        return artists

    def stem(self, *args: Any, axes: Any | None = None, **kwargs: Any) -> list[Any]:
        """Draw MATLAB-like stem series on an axes."""

        if axes is None and args and self.is_axes_handle(args[0]):
            axes = args[0]
            args = args[1:]
        axes = axes if axes is not None else self.require_active_axes()
        self.set_active_axes(axes)
        series = self.normalize_stem_args(args, kwargs)
        self.prepare_for_plot(axes)
        series = self._apply_stem_series_order(axes, series)
        artists = self.draw_stem_series(axes, series)
        self.after_plot(axes)
        return artists

    def bar(self, *args: Any, axes: Any | None = None, **kwargs: Any) -> list[Any]:
        """Draw MATLAB-like vertical bar series on an axes."""

        if axes is None and args and self.is_axes_handle(args[0]):
            axes = args[0]
            args = args[1:]
        axes = axes if axes is not None else self.require_active_axes()
        self.set_active_axes(axes)
        series = self.normalize_bar_args(args, kwargs)
        self.prepare_for_plot(axes)
        series = self._apply_bar_series_order(axes, series)
        artists = self.draw_bar_series(axes, series)
        self.after_plot(axes)
        return artists

    def area(self, *args: Any, axes: Any | None = None, **kwargs: Any) -> list[Any]:
        """Draw MATLAB-like stacked area series on an axes."""

        if axes is None and args and self.is_axes_handle(args[0]):
            axes = args[0]
            args = args[1:]
        axes = axes if axes is not None else self.require_active_axes()
        self.set_active_axes(axes)
        series = self.normalize_area_args(args, kwargs)
        self.prepare_for_plot(axes)
        series = self._apply_area_series_order(axes, series)
        artists = self.draw_area_series(axes, series)
        self.after_plot(axes)
        return artists

    def line(self, *args: Any, axes: Any | None = None, **kwargs: Any) -> list[Any]:
        """Add MATLAB-like line primitive without applying NextPlot clearing."""

        if axes is None and args and self.is_axes_handle(args[0]):
            axes = args[0]
            args = args[1:]
        axes = axes if axes is not None else self.require_active_axes()
        self.set_active_axes(axes)
        data_args, properties = self._split_plot_args_and_properties(args, kwargs)
        if len(data_args) == 2:
            series = self.normalize_plot_args(data_args, dict(properties))
            artists = self.draw_plot_series(axes, series)
        elif len(data_args) == 3:
            series3 = self.normalize_plot3_args(data_args, dict(properties))
            artists = self.draw_plot3_series(axes, series3)
        else:
            raise ValueError("line requires x, y or x, y, z data arguments")
        self.after_plot(axes)
        return artists

    def semilogx(self, *args: Any, axes: Any | None = None, **kwargs: Any) -> list[Any]:
        """MATLAB-like semilogx plot with logarithmic x scale."""

        return self._plot_with_axis_scales("log", "linear", *args, axes=axes, **kwargs)

    def semilogy(self, *args: Any, axes: Any | None = None, **kwargs: Any) -> list[Any]:
        """MATLAB-like semilogy plot with logarithmic y scale."""

        return self._plot_with_axis_scales("linear", "log", *args, axes=axes, **kwargs)

    def loglog(self, *args: Any, axes: Any | None = None, **kwargs: Any) -> list[Any]:
        """MATLAB-like loglog plot with logarithmic x and y scales."""

        return self._plot_with_axis_scales("log", "log", *args, axes=axes, **kwargs)

    def _plot_with_axis_scales(
        self,
        x_scale: AxisScale,
        y_scale: AxisScale,
        *args: Any,
        axes: Any | None = None,
        **kwargs: Any,
    ) -> list[Any]:
        if axes is None and args and self.is_axes_handle(args[0]):
            axes = args[0]
            args = args[1:]
        axes = axes if axes is not None else self.require_active_axes()
        artists = self.plot(*args, axes=axes, **kwargs)
        self.set_active_axes(axes)
        changed = False
        if self.x_scale != x_scale:
            self.x_scale = x_scale
            self.set_axis_scale(axes, "x", x_scale)
            changed = True
        if self.y_scale != y_scale:
            self.y_scale = y_scale
            self.set_axis_scale(axes, "y", y_scale)
            changed = True
        if changed:
            self._save_axes_ui_state(axes)
            self.push_current_view(axes)
        return artists

    def colororder(
        self,
        value: Sequence[Sequence[float]] | Literal["default"] | None = None,
        axes: Any | None = None,
    ) -> tuple[tuple[float, float, float], ...] | None:
        axes = axes if axes is not None else self.require_active_axes()
        if value is None:
            state = self._current_axes_ui_state(axes)
            return state.color_order or self.DEFAULT_COLOR_ORDER
        color_order = self.DEFAULT_COLOR_ORDER if value == "default" else self._normalize_color_order(value)
        state = self._current_axes_ui_state(axes)
        state.color_order = color_order
        state.next_series_index = 0
        self._axes_ui_state[axes] = state
        if axes is self.active_axes:
            self.color_order = color_order
            self.next_series_index = 0
        return None

    def linestyleorder(
        self,
        value: Sequence[str] | str | Literal["default"] | None = None,
        axes: Any | None = None,
    ) -> tuple[str, ...] | None:
        axes = axes if axes is not None else self.require_active_axes()
        if value is None:
            state = self._current_axes_ui_state(axes)
            return state.line_style_order or self.DEFAULT_LINE_STYLE_ORDER
        line_style_order = self.DEFAULT_LINE_STYLE_ORDER if value == "default" else self._normalize_line_style_order(value)
        state = self._current_axes_ui_state(axes)
        state.line_style_order = line_style_order
        state.next_series_index = 0
        self._axes_ui_state[axes] = state
        if axes is self.active_axes:
            self.line_style_order = line_style_order
            self.next_series_index = 0
        return None

    def nextseriesindex(self, value: int | None = None, axes: Any | None = None) -> int | None:
        axes = axes if axes is not None else self.require_active_axes()
        if value is None:
            return self._current_axes_ui_state(axes).next_series_index
        if not isinstance(value, int) or value < 0:
            raise ValueError("nextseriesindex must be a nonnegative integer")
        state = self._current_axes_ui_state(axes)
        state.next_series_index = value
        self._axes_ui_state[axes] = state
        if axes is self.active_axes:
            self.next_series_index = value
        return None

    def normalize_scatter_args(self, args: Sequence[Any], kwargs: dict[str, Any] | None = None) -> list[ScatterSeries]:
        """Normalize common MATLAB ``scatter`` calling forms."""

        data_args, properties = self._split_plot_args_and_properties(args, kwargs)
        if len(data_args) < 2:
            raise ValueError("scatter requires x and y data arguments")
        if len(data_args) > 4:
            raise ValueError("scatter supports x, y, optional size, and optional color")
        x_data = self._plot_data(data_args[0], "argument 1")
        y_data = self._plot_data(data_args[1], "argument 2")
        size_data = data_args[2] if len(data_args) >= 3 else None
        color_data = data_args[3] if len(data_args) >= 4 else None
        base_series = self._plot_series_from_data(x_data, y_data, None, properties)
        return [
            ScatterSeries(
                series.x,
                series.y,
                self._normalize_scatter_size(size_data, len(series.x)) if size_data is not None else None,
                self._normalize_scatter_color(color_data, len(series.x)) if color_data is not None else None,
                series.properties,
                series.line_spec,
            )
            for series in base_series
        ]

    def normalize_stem_args(self, args: Sequence[Any], kwargs: dict[str, Any] | None = None) -> list[StemSeries]:
        """Normalize common MATLAB ``stem`` calling forms."""

        return [
            StemSeries(series.x, series.y, series.style, series.properties, series.line_spec)
            for series in self.normalize_plot_args(args, kwargs)
        ]

    def normalize_bar_args(self, args: Sequence[Any], kwargs: dict[str, Any] | None = None) -> list[BarSeries]:
        """Normalize common MATLAB vertical ``bar`` calling forms."""

        return [
            BarSeries(series.x, series.y, series.style, series.properties, series.line_spec)
            for series in self.normalize_plot_args(args, kwargs)
        ]

    def normalize_area_args(self, args: Sequence[Any], kwargs: dict[str, Any] | None = None) -> list[AreaSeries]:
        """Normalize common MATLAB stacked ``area`` calling forms."""

        return self._area_series_from_plot_series(self.normalize_plot_args(args, kwargs))

    def normalize_errorbar_args(self, args: Sequence[Any], kwargs: dict[str, Any] | None = None) -> list[ErrorBarSeries]:
        """Normalize common MATLAB vertical ``errorbar`` calling forms."""

        data_args, properties = self._split_plot_args_and_properties(args, kwargs)
        if len(data_args) < 2:
            raise ValueError("errorbar requires y/e or x/y/e data arguments")
        style = None
        if data_args and isinstance(data_args[-1], str):
            style = data_args[-1]
            data_args = data_args[:-1]
        if len(data_args) == 2:
            x_data = None
            y_data = self._plot_data(data_args[0], "argument 1")
            negative_data = self._plot_data(data_args[1], "argument 2")
            positive_data = negative_data
        elif len(data_args) == 3:
            x_data = self._plot_data(data_args[0], "argument 1")
            y_data = self._plot_data(data_args[1], "argument 2")
            negative_data = self._plot_data(data_args[2], "argument 3")
            positive_data = negative_data
        elif len(data_args) == 4:
            x_data = self._plot_data(data_args[0], "argument 1")
            y_data = self._plot_data(data_args[1], "argument 2")
            negative_data = self._plot_data(data_args[2], "argument 3")
            positive_data = self._plot_data(data_args[3], "argument 4")
        else:
            raise ValueError("errorbar supports y/e, x/y/e, or x/y/negative/positive data")
        base_series = self._plot_series_from_data(x_data, y_data, style, properties)
        negatives = self._errorbar_error_columns(negative_data, len(base_series), len(base_series[0].x) if base_series else 0, "negative")
        positives = self._errorbar_error_columns(positive_data, len(base_series), len(base_series[0].x) if base_series else 0, "positive")
        return [
            ErrorBarSeries(series.x, series.y, negative, positive, series.style, series.properties, series.line_spec)
            for series, negative, positive in zip(base_series, negatives, positives)
        ]

    def normalize_plot3_args(self, args: Sequence[Any], kwargs: dict[str, Any] | None = None) -> list[Plot3Series]:
        """Normalize common MATLAB ``plot3`` calling forms into 3D line series."""

        if not args:
            raise ValueError("plot3 requires x, y, and z data arguments")
        data_args, properties = self._split_plot_args_and_properties(args, kwargs)
        if len(data_args) < 3:
            raise ValueError("plot3 requires x, y, and z data arguments")
        series: list[Plot3Series] = []
        index = 0
        while index < len(data_args):
            if index + 2 >= len(data_args):
                raise ValueError("plot3 data arguments must be x, y, z groups")
            first = data_args[index]
            second = data_args[index + 1]
            third = data_args[index + 2]
            if isinstance(first, str) or isinstance(second, str) or isinstance(third, str):
                raise ValueError("plot3 data arguments must be numeric x, y, z groups")
            x_data = self._plot_data(first, f"argument {index + 1}")
            y_data = self._plot_data(second, f"argument {index + 2}")
            z_data = self._plot_data(third, f"argument {index + 3}")
            index += 3
            style = None
            if index < len(data_args) and isinstance(data_args[index], str):
                style = data_args[index]
                index += 1
            series.extend(self._plot3_series_from_data(x_data, y_data, z_data, style, properties))
        return series

    def normalize_plot_args(self, args: Sequence[Any], kwargs: dict[str, Any] | None = None) -> list[PlotSeries]:
        """Normalize common MATLAB ``plot`` calling forms into line series."""

        if not args:
            raise ValueError("plot requires at least one data argument")
        data_args, properties = self._split_plot_args_and_properties(args, kwargs)
        if not data_args:
            raise ValueError("plot requires at least one data argument")
        series: list[PlotSeries] = []
        index = 0
        while index < len(data_args):
            first = data_args[index]
            if isinstance(first, str):
                raise ValueError(f"Unexpected line style without data at argument {index + 1}")
            if index + 1 < len(data_args) and not isinstance(data_args[index + 1], str):
                x_data = self._plot_data(first, f"argument {index + 1}")
                y_data = self._plot_data(data_args[index + 1], f"argument {index + 2}")
                index += 2
            else:
                x_data = None
                y_data = self._plot_data(first, f"argument {index + 1}")
                index += 1
            style = None
            if index < len(data_args) and isinstance(data_args[index], str):
                style = data_args[index]
                index += 1
            series.extend(self._plot_series_from_data(x_data, y_data, style, properties))
        return series

    def title(self, value: Any | None = None, axes: Any | None = None) -> tuple[str, ...] | None:
        return self._text_property("title", value, axes)

    def xlabel(self, value: Any | None = None, axes: Any | None = None) -> tuple[str, ...] | None:
        return self._text_property("xlabel", value, axes)

    def ylabel(self, value: Any | None = None, axes: Any | None = None) -> tuple[str, ...] | None:
        return self._text_property("ylabel", value, axes)

    def zlabel(self, value: Any | None = None, axes: Any | None = None) -> tuple[str, ...] | None:
        return self._text_property("zlabel", value, axes)

    def _text_property(
        self,
        kind: Literal["title", "xlabel", "ylabel", "zlabel"],
        value: Any | None,
        axes: Any | None,
    ) -> tuple[str, ...] | None:
        axes = axes if axes is not None else self.require_active_axes()
        attr = self._text_state_attr(kind)
        if value is None:
            text = self.get_axes_text(axes, kind)
            setattr(self, attr, text)
            return text
        text = self._normalize_text_value(value)
        if getattr(self, attr) == text:
            return None
        setattr(self, attr, text)
        self.set_axes_text(axes, kind, text)
        self._save_axes_ui_state(axes)
        self.push_current_view(axes)
        return None

    def _text_state_attr(self, kind: Literal["title", "xlabel", "ylabel", "zlabel"]) -> str:
        if kind == "title":
            return "axes_title"
        return f"{kind}_text"

    def _normalize_text_value(self, value: Any) -> tuple[str, ...]:
        if isinstance(value, str):
            return (value,)
        try:
            return tuple(str(item) for item in value)
        except TypeError:
            return (str(value),)

    def _normalize_color_order(self, value: Sequence[Sequence[float]]) -> tuple[tuple[float, float, float], ...]:
        try:
            rows = tuple(tuple(float(component) for component in row) for row in value)
        except (TypeError, ValueError) as exc:
            raise ValueError("colororder must be an N-by-3 numeric sequence") from exc
        if not rows or any(len(row) != 3 for row in rows):
            raise ValueError("colororder must be a nonempty N-by-3 numeric sequence")
        if any(not all(isfinite(component) and 0.0 <= component <= 1.0 for component in row) for row in rows):
            raise ValueError("colororder values must be finite numbers between 0 and 1")
        return rows

    def _normalize_line_style_order(self, value: Sequence[str] | str) -> tuple[str, ...]:
        styles = (value,) if isinstance(value, str) else tuple(value)
        if not styles:
            raise ValueError("linestyleorder must not be empty")
        valid_styles = set(self._LINE_SPEC_LINESTYLES) | {"none"}
        normalized = tuple(str(style).strip() for style in styles)
        if any(style not in valid_styles for style in normalized):
            raise ValueError("linestyleorder entries must be '-', '--', '-.', ':', or 'none'")
        return normalized

    def _split_plot_args_and_properties(
        self,
        args: Sequence[Any],
        kwargs: dict[str, Any] | None,
    ) -> tuple[tuple[Any, ...], tuple[tuple[str, Any], ...]]:
        properties: list[tuple[str, Any]] = []
        index = len(args)
        while index >= 2 and isinstance(args[index - 2], str) and self._is_plot_property_name(args[index - 2]):
            properties.insert(0, (self._normalize_plot_property_name(args[index - 2]), args[index - 1]))
            index -= 2
        properties.extend((self._normalize_plot_property_name(key), value) for key, value in (kwargs or {}).items())
        return tuple(args[:index]), tuple(properties)

    def _is_plot_property_name(self, value: str) -> bool:
        normalized = value.strip().replace("_", "").lower()
        return normalized in self._PLOT_PROPERTY_ALIASES

    def _normalize_plot_property_name(self, value: Any) -> str:
        raw = str(value)
        normalized = raw.strip().replace("_", "").lower()
        return self._PLOT_PROPERTY_ALIASES.get(normalized, raw)

    def _numeric_vector(self, value: Any, label: str) -> tuple[float, ...]:
        if isinstance(value, (str, bytes)):
            raise ValueError(f"{label} must be a numeric vector")
        try:
            vector = tuple(float(item) for item in value)
        except TypeError:
            vector = (float(value),)
        except ValueError as exc:
            raise ValueError(f"{label} must be a numeric vector") from exc
        if not vector:
            return ()
        if not all(isfinite(item) for item in vector):
            raise ValueError(f"{label} must contain only finite numeric values")
        return vector

    def _plot_data(self, value: Any, label: str) -> _PlotData:
        if isinstance(value, (str, bytes)):
            raise ValueError(f"{label} must be numeric plot data")
        if self._is_plot_row(value):
            rows = tuple(self._numeric_vector(row, label) for row in value)
            if not rows:
                return _PlotData(())
            width = len(rows[0])
            if any(len(row) != width for row in rows):
                raise ValueError(f"{label} matrix rows must have the same length")
            return _PlotData(rows)
        return _PlotData((self._numeric_vector(value, label),))

    def _is_plot_row(self, value: Any) -> bool:
        try:
            iterator = iter(value)
        except TypeError:
            return False
        for item in iterator:
            return not isinstance(item, (str, bytes)) and self._is_iterable(item)
        return False

    def _is_iterable(self, value: Any) -> bool:
        try:
            iter(value)
        except TypeError:
            return False
        return True

    def _plot_series_from_data(
        self,
        x_data: _PlotData | None,
        y_data: _PlotData,
        style: str | None,
        properties: tuple[tuple[str, Any], ...],
    ) -> list[PlotSeries]:
        if x_data is None:
            return self._plot_y_only_series(y_data, style, properties)
        if x_data.is_vector and not y_data.is_vector:
            x_values = x_data.as_vector()
            if len(x_values) != y_data.row_count:
                raise ValueError("x vector length must match y row count")
            line_spec = self._parse_line_spec(style)
            return [PlotSeries(x_values, y_data.column(column), style, properties, line_spec) for column in range(y_data.column_count)]
        if not x_data.is_vector and y_data.is_vector:
            y_values = y_data.as_vector()
            if x_data.row_count != len(y_values):
                raise ValueError("x row count must match y vector length")
            line_spec = self._parse_line_spec(style)
            return [PlotSeries(x_data.column(column), y_values, style, properties, line_spec) for column in range(x_data.column_count)]
        if not x_data.is_vector and not y_data.is_vector:
            if x_data.row_count != y_data.row_count or x_data.column_count != y_data.column_count:
                raise ValueError("x and y matrices must have the same shape")
            line_spec = self._parse_line_spec(style)
            return [
                PlotSeries(x_data.column(column), y_data.column(column), style, properties, line_spec)
                for column in range(y_data.column_count)
            ]
        x_values = x_data.as_vector()
        y_values = y_data.as_vector()
        if len(x_values) != len(y_values):
            raise ValueError("x and y data must have the same length")
        return [PlotSeries(x_values, y_values, style, properties, self._parse_line_spec(style))]

    def _plot_y_only_series(
        self,
        y_data: _PlotData,
        style: str | None,
        properties: tuple[tuple[str, Any], ...],
    ) -> list[PlotSeries]:
        if y_data.is_vector:
            y_values = y_data.as_vector()
            x_values = tuple(float(item) for item in range(1, len(y_values) + 1))
            return [PlotSeries(x_values, y_values, style, properties, self._parse_line_spec(style))]
        x_values = tuple(float(item) for item in range(1, y_data.row_count + 1))
        line_spec = self._parse_line_spec(style)
        return [PlotSeries(x_values, y_data.column(column), style, properties, line_spec) for column in range(y_data.column_count)]

    def _stairs_series(self, series: PlotSeries) -> PlotSeries:
        x_values, y_values = self._stairs_points(series.x, series.y)
        return PlotSeries(x_values, y_values, series.style, series.properties, series.line_spec)

    def _area_series_from_plot_series(self, series: Sequence[PlotSeries]) -> list[AreaSeries]:
        grouped: list[AreaSeries] = []
        baselines: dict[tuple[float, ...], tuple[float, ...]] = {}
        for item in series:
            baseline = baselines.get(item.x)
            if baseline is None:
                baseline = tuple(0.0 for _value in item.y)
            if len(baseline) != len(item.y):
                raise ValueError("area series with shared x data must have matching y lengths")
            top = tuple(base + value for base, value in zip(baseline, item.y))
            grouped.append(AreaSeries(item.x, top, baseline, item.style, item.properties, item.line_spec))
            baselines[item.x] = top
        return grouped

    def _stairs_points(self, x_values: tuple[float, ...], y_values: tuple[float, ...]) -> tuple[tuple[float, ...], tuple[float, ...]]:
        if len(x_values) != len(y_values):
            raise ValueError("stairs x and y data must have the same length")
        if len(x_values) <= 1:
            return x_values, y_values
        stepped_x = [x_values[0]]
        stepped_y = [y_values[0]]
        for index in range(1, len(x_values)):
            stepped_x.extend([x_values[index], x_values[index]])
            stepped_y.extend([y_values[index - 1], y_values[index]])
        return tuple(stepped_x), tuple(stepped_y)

    def _plot3_series_from_data(
        self,
        x_data: _PlotData,
        y_data: _PlotData,
        z_data: _PlotData,
        style: str | None,
        properties: tuple[tuple[str, Any], ...],
    ) -> list[Plot3Series]:
        xy_series = self._plot_series_from_data(x_data, y_data, style, properties)
        z_columns = self._plot3_z_columns(z_data, len(xy_series), len(xy_series[0].x) if xy_series else 0)
        if len(z_columns) != len(xy_series):
            raise ValueError("plot3 x, y, and z data must expand to the same number of series")
        return [
            Plot3Series(series.x, series.y, z_values, series.style, series.properties, series.line_spec)
            for series, z_values in zip(xy_series, z_columns)
        ]

    def _plot3_z_columns(self, z_data: _PlotData, series_count: int, point_count: int) -> list[tuple[float, ...]]:
        if z_data.is_vector:
            z_values = z_data.as_vector()
            if len(z_values) != point_count:
                raise ValueError("plot3 z vector length must match x and y data length")
            return [z_values for _index in range(series_count)]
        if z_data.row_count != point_count:
            raise ValueError("plot3 z row count must match x and y data length")
        if z_data.column_count != series_count:
            raise ValueError("plot3 z matrix columns must match expanded x and y series")
        return [z_data.column(column) for column in range(z_data.column_count)]

    def _errorbar_error_columns(
        self,
        error_data: _PlotData,
        series_count: int,
        point_count: int,
        name: str,
    ) -> list[tuple[float, ...]]:
        if error_data.is_vector:
            values = error_data.as_vector()
            if len(values) != point_count:
                raise ValueError(f"errorbar {name} error vector length must match data length")
            return [values for _index in range(series_count)]
        if error_data.row_count != point_count:
            raise ValueError(f"errorbar {name} error row count must match data length")
        if error_data.column_count != series_count:
            raise ValueError(f"errorbar {name} error columns must match expanded data series")
        return [error_data.column(column) for column in range(error_data.column_count)]

    def _normalize_scatter_size(self, value: Any, point_count: int) -> tuple[float, ...] | float:
        if isinstance(value, (str, bytes)):
            raise ValueError("scatter size must be numeric")
        try:
            vector = tuple(float(item) for item in value)
        except TypeError:
            size = float(value)
            if not isfinite(size) or size < 0.0:
                raise ValueError("scatter size must be a finite nonnegative value")
            return size
        except ValueError as exc:
            raise ValueError("scatter size must be numeric") from exc
        if len(vector) != point_count:
            raise ValueError("scatter size vector length must match data length")
        if any(not isfinite(item) or item < 0.0 for item in vector):
            raise ValueError("scatter size values must be finite and nonnegative")
        return vector

    def _normalize_scatter_color(self, value: Any, point_count: int) -> Any:
        if isinstance(value, str):
            return value
        if self._is_plot_row(value):
            rows = self._normalize_color_order(cast(Sequence[Sequence[float]], value))
            if len(rows) != point_count:
                raise ValueError("scatter color rows must match data length")
            return rows
        try:
            vector = tuple(float(item) for item in value)
        except TypeError:
            return value
        except ValueError as exc:
            raise ValueError("scatter color must be a color string, RGB triplet, or N-by-3 RGB sequence") from exc
        if len(vector) != 3 or any(not isfinite(item) or item < 0.0 or item > 1.0 for item in vector):
            raise ValueError("scatter color must be a color string, RGB triplet, or N-by-3 RGB sequence")
        return vector

    def _apply_plot_series_order(self, axes: Any, series: list[PlotSeries]) -> list[PlotSeries]:
        state = self._current_axes_ui_state(axes)
        color_order = state.color_order or self.DEFAULT_COLOR_ORDER
        line_style_order = state.line_style_order or self.DEFAULT_LINE_STYLE_ORDER
        next_index = state.next_series_index
        ordered: list[PlotSeries] = []
        for item in series:
            if item.style is not None and not item.line_spec:
                ordered.append(item)
                continue
            line_spec = item.line_spec
            applied_default = False
            if not self._series_has_property(item, "color") and color_order:
                color = color_order[next_index % len(color_order)]
                line_spec = (*line_spec, ("color", color))
                applied_default = True
            if not self._series_has_property(item, "linestyle") and line_style_order:
                style_index = (next_index // max(len(color_order), 1)) % len(line_style_order)
                line_spec = (*line_spec, ("linestyle", line_style_order[style_index]))
                applied_default = True
            if applied_default:
                next_index += 1
            ordered.append(
                PlotSeries(
                    item.x,
                    item.y,
                    item.style,
                    item.properties,
                    line_spec,
                )
            )
        state.color_order = color_order
        state.line_style_order = line_style_order
        state.next_series_index = next_index
        self._axes_ui_state[axes] = state
        if axes is self.active_axes:
            self.color_order = color_order
            self.line_style_order = line_style_order
            self.next_series_index = next_index
        return ordered

    def _series_has_property(self, series: PlotSeries, property_name: str) -> bool:
        return any(name == property_name for name, _value in (*series.line_spec, *series.properties))

    def _apply_plot3_series_order(self, axes: Any, series: list[Plot3Series]) -> list[Plot3Series]:
        proxy = [PlotSeries(item.x, item.y, item.style, item.properties, item.line_spec) for item in series]
        ordered = self._apply_plot_series_order(axes, proxy)
        return [
            Plot3Series(item.x, item.y, item.z, ordered_item.style, ordered_item.properties, ordered_item.line_spec)
            for item, ordered_item in zip(series, ordered)
        ]

    def _apply_errorbar_series_order(self, axes: Any, series: list[ErrorBarSeries]) -> list[ErrorBarSeries]:
        proxy = [PlotSeries(item.x, item.y, item.style, item.properties, item.line_spec) for item in series]
        ordered = self._apply_plot_series_order(axes, proxy)
        return [
            ErrorBarSeries(
                item.x,
                item.y,
                item.y_negative,
                item.y_positive,
                ordered_item.style,
                ordered_item.properties,
                ordered_item.line_spec,
            )
            for item, ordered_item in zip(series, ordered)
        ]

    def _apply_scatter_series_order(self, axes: Any, series: list[ScatterSeries]) -> list[ScatterSeries]:
        state = self._current_axes_ui_state(axes)
        color_order = state.color_order or self.DEFAULT_COLOR_ORDER
        next_index = state.next_series_index
        ordered: list[ScatterSeries] = []
        for item in series:
            line_spec = item.line_spec
            if item.color is not None:
                line_spec = (*line_spec, ("color", item.color))
            elif not self._series_has_property(PlotSeries(item.x, item.y, None, item.properties, line_spec), "color") and color_order:
                line_spec = (*line_spec, ("color", color_order[next_index % len(color_order)]))
                next_index += 1
            ordered.append(ScatterSeries(item.x, item.y, item.size, item.color, item.properties, line_spec))
        state.color_order = color_order
        state.next_series_index = next_index
        self._axes_ui_state[axes] = state
        if axes is self.active_axes:
            self.color_order = color_order
            self.next_series_index = next_index
        return ordered

    def _apply_stem_series_order(self, axes: Any, series: list[StemSeries]) -> list[StemSeries]:
        proxy = [PlotSeries(item.x, item.y, item.style, item.properties, item.line_spec) for item in series]
        ordered = self._apply_plot_series_order(axes, proxy)
        return [
            StemSeries(item.x, item.y, ordered_item.style, ordered_item.properties, ordered_item.line_spec)
            for item, ordered_item in zip(series, ordered)
        ]

    def _apply_bar_series_order(self, axes: Any, series: list[BarSeries]) -> list[BarSeries]:
        proxy = [PlotSeries(item.x, item.y, item.style, item.properties, item.line_spec) for item in series]
        ordered = self._apply_plot_series_order(axes, proxy)
        return [
            BarSeries(item.x, item.y, ordered_item.style, ordered_item.properties, ordered_item.line_spec)
            for item, ordered_item in zip(series, ordered)
        ]

    def _apply_area_series_order(self, axes: Any, series: list[AreaSeries]) -> list[AreaSeries]:
        proxy = [PlotSeries(item.x, item.y, item.style, item.properties, item.line_spec) for item in series]
        ordered = self._apply_plot_series_order(axes, proxy)
        return [
            AreaSeries(item.x, item.y, item.baseline, ordered_item.style, ordered_item.properties, ordered_item.line_spec)
            for item, ordered_item in zip(series, ordered)
        ]

    def _parse_line_spec(self, style: str | None) -> tuple[tuple[str, Any], ...]:
        if not style:
            return ()
        remaining = style.strip()
        if not remaining:
            return ()
        parsed: dict[str, Any] = {}
        while remaining:
            matched = False
            for token in self._LINE_SPEC_LINESTYLES:
                if remaining.startswith(token):
                    if "linestyle" in parsed:
                        return ()
                    parsed["linestyle"] = token
                    remaining = remaining[len(token) :]
                    matched = True
                    break
            if matched:
                continue
            for token in self._LINE_SPEC_MARKERS:
                if remaining.startswith(token):
                    if "marker" in parsed:
                        return ()
                    parsed["marker"] = self._LINE_SPEC_MARKER_ALIASES.get(token, token)
                    remaining = remaining[len(token) :]
                    matched = True
                    break
            if matched:
                continue
            color = remaining[0]
            if color in self._LINE_SPEC_COLORS:
                if "color" in parsed:
                    return ()
                parsed["color"] = color
                remaining = remaining[1:]
                continue
            return ()
        order = ("color", "linestyle", "marker")
        return tuple((key, parsed[key]) for key in order if key in parsed)

    def _set_tool_mode(self, mode: InteractionMode, value: bool | str | None) -> InteractionMode:
        if value is None:
            self.set_mode(mode)
        elif isinstance(value, str):
            normalized = value.strip().lower()
            if normalized == "on":
                self.set_mode(mode)
            elif normalized == "off":
                if self.mode == mode:
                    self.set_mode(InteractionMode.NONE)
            elif normalized == "toggle":
                self.toggle_mode(mode)
            else:
                raise ValueError(f"Unsupported interaction mode value: {value!r}")
        elif value:
            self.set_mode(mode)
        elif self.mode == mode:
            self.set_mode(InteractionMode.NONE)
        return self.mode

    def grid(self, value: bool | str | None = None, axes: Any | None = None) -> bool:
        """MATLAB-like grid control for the target axes."""

        axes = axes if axes is not None else self.require_active_axes()
        current = self.grid_is_enabled(axes)
        current_minor = self.minor_grid_is_enabled(axes)
        if value is None:
            visible = not current
        elif isinstance(value, str):
            normalized = value.strip().lower()
            if normalized == "on":
                visible = True
            elif normalized == "off":
                visible = False
                self.set_minor_grid_visible(axes, False)
            elif normalized == "toggle":
                visible = not current
            elif normalized == "minor":
                minor_visible = not current_minor
                self.set_minor_grid_visible(axes, minor_visible)
                self._save_axes_ui_state(axes)
                self.push_current_view(axes)
                return minor_visible
            else:
                raise ValueError(f"Unsupported grid value: {value!r}")
        else:
            visible = bool(value)
        force_off = isinstance(value, str) and value.strip().lower() == "off"
        if visible != current or force_off:
            self.set_grid_visible(axes, visible)
            self._save_axes_ui_state(axes)
            self.push_current_view(axes)
        return visible

    def xgrid(self, value: bool | str | None = None) -> bool:
        """MATLAB-like XGrid property helper."""

        return self._axis_grid_property("x", value, minor=False)

    def ygrid(self, value: bool | str | None = None) -> bool:
        """MATLAB-like YGrid property helper."""

        return self._axis_grid_property("y", value, minor=False)

    def zgrid(self, value: bool | str | None = None) -> bool | None:
        """MATLAB-like ZGrid property helper."""

        axes = self.require_active_axes()
        if not self.is_3d_axes(axes):
            return None
        return self._axis_grid_property("z", value, minor=False)

    def xminorgrid(self, value: bool | str | None = None) -> bool:
        """MATLAB-like XMinorGrid property helper."""

        return self._axis_grid_property("x", value, minor=True)

    def yminorgrid(self, value: bool | str | None = None) -> bool:
        """MATLAB-like YMinorGrid property helper."""

        return self._axis_grid_property("y", value, minor=True)

    def zminorgrid(self, value: bool | str | None = None) -> bool | None:
        """MATLAB-like ZMinorGrid property helper."""

        axes = self.require_active_axes()
        if not self.is_3d_axes(axes):
            return None
        return self._axis_grid_property("z", value, minor=True)

    def xminortick(self, value: bool | str | None = None) -> bool:
        """MATLAB-like XMinorTick property helper."""

        return self._axis_minor_tick_property("x", value)

    def yminortick(self, value: bool | str | None = None) -> bool:
        """MATLAB-like YMinorTick property helper."""

        return self._axis_minor_tick_property("y", value)

    def zminortick(self, value: bool | str | None = None) -> bool | None:
        """MATLAB-like ZMinorTick property helper."""

        axes = self.require_active_axes()
        if not self.is_3d_axes(axes):
            return None
        return self._axis_minor_tick_property("z", value)

    def _axis_grid_property(self, axis: Literal["x", "y", "z"], value: bool | str | None, *, minor: bool) -> bool:
        axes = self.require_active_axes()
        current = self.axis_grid_is_enabled(axes, axis, minor=minor)
        if value is None:
            return current
        visible = self._parse_grid_on_off(value, f"{axis}{'minor' if minor else ''}grid")
        if visible != current:
            self.set_axis_grid_visible(axes, axis, visible, minor=minor)
            self._save_axes_ui_state(axes)
            self.push_current_view(axes)
        return visible

    def _axis_minor_tick_property(self, axis: Literal["x", "y", "z"], value: bool | str | None) -> bool:
        axes = self.require_active_axes()
        current = self.axis_minor_tick_is_enabled(axes, axis)
        if value is None:
            return current
        visible = self._parse_grid_on_off(value, f"{axis}minortick")
        if visible != current:
            self.set_axis_minor_tick_visible(axes, axis, visible)
            self._save_axes_ui_state(axes)
            self.push_current_view(axes)
        return visible

    def _parse_grid_on_off(self, value: bool | str, name: str) -> bool:
        if isinstance(value, str):
            normalized = value.strip().lower()
            if normalized == "on":
                return True
            if normalized == "off":
                return False
            raise ValueError(f"Unsupported {name} value: {value!r}")
        return bool(value)

    def box(self, value: bool | str | None = None, axes: Any | None = None) -> bool:
        """MATLAB-like axes box control for the target axes."""

        axes = axes if axes is not None else self.require_active_axes()
        current = self.box_is_enabled(axes)
        if value is None:
            visible = not current
        elif isinstance(value, str):
            normalized = value.strip().lower()
            if normalized == "on":
                visible = True
            elif normalized == "off":
                visible = False
            elif normalized == "toggle":
                visible = not current
            else:
                raise ValueError(f"Unsupported box value: {value!r}")
        else:
            visible = bool(value)
        if visible != current:
            self.set_box_visible(axes, visible)
            self._save_axes_ui_state(axes)
            self.push_current_view(axes)
        return visible

    def legend(self, value: bool | str | None = None, axes: Any | None = None) -> bool:
        """MATLAB-like legend control for the target axes."""

        axes = axes if axes is not None else self.require_active_axes()
        current = self.legend_is_enabled(axes)
        if value is None:
            visible = not current
        elif isinstance(value, str):
            normalized = value.strip().lower()
            if normalized == "on":
                visible = True
            elif normalized == "off":
                visible = False
            elif normalized == "toggle":
                visible = not current
            else:
                raise ValueError(f"Unsupported legend value: {value!r}")
        else:
            visible = bool(value)
        if visible != current:
            actual = self.set_legend_visible(axes, visible)
            if actual != current:
                self._save_axes_ui_state(axes)
                self.push_current_view(axes)
            return actual
        return current

    def hold(self, value: bool | str | None = None) -> bool:
        """Get or set MATLAB-style hold state.

        Accepted string values are ``"on"``, ``"off"``, and ``"toggle"``.
        """

        if value is None:
            return self.hold_enabled
        if isinstance(value, str):
            normalized = value.strip().lower()
            if normalized == "on":
                value = True
            elif normalized == "off":
                value = False
            elif normalized == "toggle":
                value = not self.hold_enabled
            else:
                raise ValueError(f"Unsupported hold value: {value!r}")
        old_hold = self.hold_enabled
        self.hold_enabled = bool(value)
        self.next_plot = "add" if self.hold_enabled else "replace"
        self._save_axes_ui_state(self.active_axes)
        if self.hold_enabled != old_hold:
            self.on_hold_changed(self.hold_enabled)
        return self.hold_enabled

    def set_next_plot(self, value: NextPlotMode) -> None:
        if value not in self._VALID_NEXT_PLOT:
            raise ValueError(f"Unsupported next_plot value: {value!r}")
        old_hold = self.hold_enabled
        self.next_plot = value
        self.hold_enabled = value == "add"
        self._save_axes_ui_state(self.active_axes)
        if self.hold_enabled != old_hold:
            self.on_hold_changed(self.hold_enabled)

    def axis(
        self,
        value: Literal[
            "auto",
            "manual",
            "tight",
            "equal",
            "normal",
            "fill",
            "image",
            "square",
            "vis3d",
            "on",
            "off",
            "ij",
            "xy",
            "state",
        ]
        | Sequence[float]
        | None = None,
    ) -> tuple[float, ...] | LimitMode | None:
        if value is None:
            return self._axis_query()
        if not isinstance(value, str):
            self._axis_limits(value)
            return
        original_value = value
        value = value.strip().lower()
        if value == "state":
            return self._axis_state()
        if value == "auto":
            self.xlim_mode = "auto"
            self.ylim_mode = "auto"
            self.zlim_mode = "auto"
            self.autoscale_active_axes(tight=False)
            self.push_current_view()
            return
        if value == "manual":
            if (
                self.xlim_mode == "manual"
                and self.ylim_mode == "manual"
                and self.zlim_mode == "manual"
            ):
                return
            self.xlim_mode = "manual"
            self.ylim_mode = "manual"
            self.zlim_mode = "manual"
            self.push_current_view()
            return
        if value == "tight":
            self.xlim_mode = "auto"
            self.ylim_mode = "auto"
            self.zlim_mode = "auto"
            self.autoscale_active_axes(tight=True)
            self.push_current_view()
            return
        if value == "image":
            self.xlim_mode = "auto"
            self.ylim_mode = "auto"
            self.zlim_mode = "auto"
            self.axis_aspect = "equal"
            axes = self.require_active_axes()
            self.autoscale_axes(axes, tight=True)
            self.set_aspect(axes, "equal")
            self.push_current_view()
            return
        if value == "equal":
            if self.axis_aspect == "equal":
                return
            self.axis_aspect = "equal"
            self.set_aspect(self.require_active_axes(), "equal")
            self.push_current_view()
            return
        if value in {"normal", "fill"}:
            if self.axis_aspect == "auto" and self.box_aspect == "auto":
                return
            self.axis_aspect = "auto"
            self.box_aspect = "auto"
            axes = self.require_active_axes()
            self.set_aspect(axes, "auto")
            self.set_box_aspect(axes, "auto")
            self.push_current_view()
            return
        if value == "square":
            if self.box_aspect == "square":
                return
            self.box_aspect = "square"
            self.set_box_aspect(self.require_active_axes(), "square")
            self.push_current_view()
            return
        if value == "vis3d":
            if self.box_aspect == "vis3d":
                return
            self.box_aspect = "vis3d"
            self.set_box_aspect(self.require_active_axes(), "vis3d")
            self.push_current_view()
            return
        if value == "on":
            if self.axis_visible:
                return
            self.axis_visible = True
            self.set_axis_visible(self.require_active_axes(), True)
            self.push_current_view()
            return
        if value == "off":
            if not self.axis_visible:
                return
            self.axis_visible = False
            self.set_axis_visible(self.require_active_axes(), False)
            self.push_current_view()
            return
        if value == "ij":
            if self.y_direction == "reverse":
                return
            self._set_axis_direction("y", "reverse")
            return
        if value == "xy":
            if self.y_direction == "normal":
                return
            self._set_axis_direction("y", "normal")
            return
        raise ValueError(f"Unsupported axis value: {original_value!r}")

    def xdir(self, value: AxisDirection | str | None = None) -> AxisDirection | None:
        return self._axis_direction_property("x", value)

    def ydir(self, value: AxisDirection | str | None = None) -> AxisDirection | None:
        return self._axis_direction_property("y", value)

    def zdir(self, value: AxisDirection | str | None = None) -> AxisDirection | None:
        return self._axis_direction_property("z", value)

    def xscale(self, value: AxisScale | str | None = None) -> AxisScale | None:
        return self._axis_scale_property("x", value)

    def yscale(self, value: AxisScale | str | None = None) -> AxisScale | None:
        return self._axis_scale_property("y", value)

    def zscale(self, value: AxisScale | str | None = None) -> AxisScale | None:
        return self._axis_scale_property("z", value)

    def _axis_direction_property(self, axis: Literal["x", "y", "z"], value: AxisDirection | str | None) -> AxisDirection | None:
        if value is None:
            return getattr(self, f"{axis}_direction")
        direction = self._validate_axis_direction(value, f"{axis}dir")
        self._set_axis_direction(axis, direction)
        return None

    def _axis_scale_property(self, axis: Literal["x", "y", "z"], value: AxisScale | str | None) -> AxisScale | None:
        if value is None:
            return getattr(self, f"{axis}_scale")
        scale = self._validate_axis_scale(value, f"{axis}scale")
        attr = f"{axis}_scale"
        if getattr(self, attr) == scale:
            return None
        axes = self.require_active_axes()
        setattr(self, attr, scale)
        self.set_axis_scale(axes, axis, scale)
        self._save_axes_ui_state(axes)
        self.push_current_view(axes)
        return None

    def _set_axis_direction(self, axis: Literal["x", "y", "z"], direction: AxisDirection) -> None:
        attr = f"{axis}_direction"
        if getattr(self, attr) == direction:
            return
        axes = self.require_active_axes()
        setattr(self, attr, direction)
        if axis == "x":
            self.set_x_direction(axes, direction)
        elif axis == "y":
            self.set_y_direction(axes, direction)
        else:
            self.set_z_direction(axes, direction)
        self._save_axes_ui_state(axes)
        self.push_current_view(axes)

    def _validate_axis_direction(self, value: AxisDirection | str, name: str) -> AxisDirection:
        direction = str(value).strip().lower()
        if direction not in {"normal", "reverse"}:
            raise ValueError(f"Unsupported {name} value: {value!r}")
        return cast(AxisDirection, direction)

    def _validate_axis_scale(self, value: AxisScale | str, name: str) -> AxisScale:
        scale = str(value).strip().lower()
        if scale not in {"linear", "log"}:
            raise ValueError(f"Unsupported {name} value: {value!r}")
        return cast(AxisScale, scale)

    def _axis_query(self) -> tuple[float, ...]:
        axes = self.require_active_axes()
        limits = self.get_limits(axes)
        values: tuple[float, ...] = (*limits.xlim, *limits.ylim)
        if self.is_3d_axes(axes) and limits.zlim is not None:
            values = (*values, *limits.zlim)
        return values

    def _axis_state(self) -> LimitMode:
        if "manual" in {self.xlim_mode, self.ylim_mode, self.zlim_mode}:
            return "manual"
        return "auto"

    def _axis_limits(self, values: Sequence[float]) -> None:
        limits = self._parse_numeric_limits(values, "axis")
        if len(limits) not in {4, 6, 8}:
            raise ValueError("axis limit vector must contain 4, 6, or 8 values")
        axes = self.require_active_axes()
        current = self.get_limits(axes)
        zlim = current.zlim
        clim = current.clim
        self._validate_limit_range((limits[0], limits[1]), "xlim")
        self._validate_limit_range((limits[2], limits[3]), "ylim")
        if len(limits) in {6, 8}:
            if not self.is_3d_axes(axes):
                raise ValueError("6- or 8-value axis limit vector requires a 3D axes")
            zlim = (limits[4], limits[5])
            self._validate_limit_range(zlim, "zlim")
            self.zlim_mode = "manual"
        if len(limits) == 8:
            clim = (limits[6], limits[7])
            self._validate_limit_range(clim, "clim")
            self.clim_mode = "manual"
        self.set_limits(axes, AxesLimits((limits[0], limits[1]), (limits[2], limits[3]), zlim, clim))
        self.xlim_mode = "manual"
        self.ylim_mode = "manual"
        self.sync_linked_axes(axes, self.get_limits(axes))
        self.push_current_view()

    def set_xlim(self, left: float, right: float) -> None:
        left, right = self._parse_numeric_limits((left, right), "xlim")
        self._validate_limit_range((left, right), "xlim")
        axes = self.require_active_axes()
        current = self.get_limits(axes)
        if current.xlim == (left, right) and self.xlim_mode == "manual":
            return
        self.set_limits(axes, AxesLimits((left, right), current.ylim, current.zlim, current.clim))
        self.xlim_mode = "manual"
        self.sync_linked_axes(axes, self.get_limits(axes))
        self.push_current_view()

    def set_ylim(self, bottom: float, top: float) -> None:
        bottom, top = self._parse_numeric_limits((bottom, top), "ylim")
        self._validate_limit_range((bottom, top), "ylim")
        axes = self.require_active_axes()
        current = self.get_limits(axes)
        if current.ylim == (bottom, top) and self.ylim_mode == "manual":
            return
        self.set_limits(axes, AxesLimits(current.xlim, (bottom, top), current.zlim, current.clim))
        self.ylim_mode = "manual"
        self.sync_linked_axes(axes, self.get_limits(axes))
        self.push_current_view()

    def set_zlim(self, bottom: float, top: float) -> None:
        bottom, top = self._parse_numeric_limits((bottom, top), "zlim")
        self._validate_limit_range((bottom, top), "zlim")
        axes = self.require_active_axes()
        if not self.is_3d_axes(axes):
            return
        current = self.get_limits(axes)
        if current.zlim == (bottom, top) and self.zlim_mode == "manual":
            return
        self.set_limits(axes, AxesLimits(current.xlim, current.ylim, (bottom, top), current.clim))
        self.zlim_mode = "manual"
        self.sync_linked_axes(axes, self.get_limits(axes))
        self.push_current_view()

    def xlim(self, value: Literal["auto", "manual", "mode"] | Sequence[float] | None = None) -> tuple[float, float] | LimitMode | None:
        if value is None:
            return self.get_limits(self.require_active_axes()).xlim
        if isinstance(value, str):
            original_value = value
            value = value.strip().lower()
            if value == "mode":
                return self.xlim_mode
            if value == "auto":
                self.xlim_mode = "auto"
                self.autoscale_active_axes(tight=False)
                self.push_current_view()
                return None
            if value == "manual":
                if self.xlim_mode == "manual":
                    return None
                self.xlim_mode = "manual"
                self.push_current_view()
                return None
            raise ValueError(f"Unsupported xlim value: {original_value!r}")
        left, right = self._parse_two_value_limits(value, "xlim")
        self.set_xlim(left, right)
        return None

    def ylim(self, value: Literal["auto", "manual", "mode"] | Sequence[float] | None = None) -> tuple[float, float] | LimitMode | None:
        if value is None:
            return self.get_limits(self.require_active_axes()).ylim
        if isinstance(value, str):
            original_value = value
            value = value.strip().lower()
            if value == "mode":
                return self.ylim_mode
            if value == "auto":
                self.ylim_mode = "auto"
                self.autoscale_active_axes(tight=False)
                self.push_current_view()
                return None
            if value == "manual":
                if self.ylim_mode == "manual":
                    return None
                self.ylim_mode = "manual"
                self.push_current_view()
                return None
            raise ValueError(f"Unsupported ylim value: {original_value!r}")
        bottom, top = self._parse_two_value_limits(value, "ylim")
        self.set_ylim(bottom, top)
        return None

    def zlim(self, value: Literal["auto", "manual", "mode"] | Sequence[float] | None = None) -> tuple[float, float] | LimitMode | None:
        axes = self.require_active_axes()
        if not self.is_3d_axes(axes):
            return None
        if value is None:
            return self.get_limits(axes).zlim
        if isinstance(value, str):
            original_value = value
            value = value.strip().lower()
            if value == "mode":
                return self.zlim_mode
            if value == "auto":
                self.zlim_mode = "auto"
                self.autoscale_active_axes(tight=False)
                self.push_current_view()
                return None
            if value == "manual":
                if self.zlim_mode == "manual":
                    return None
                self.zlim_mode = "manual"
                self.push_current_view()
                return None
            raise ValueError(f"Unsupported zlim value: {original_value!r}")
        bottom, top = self._parse_two_value_limits(value, "zlim")
        self.set_zlim(bottom, top)
        return None

    def xticks(self, value: Literal["auto", "manual", "mode"] | Sequence[float] | None = None) -> tuple[float, ...] | LimitMode | None:
        return self._ticks_property("x", value)

    def yticks(self, value: Literal["auto", "manual", "mode"] | Sequence[float] | None = None) -> tuple[float, ...] | LimitMode | None:
        return self._ticks_property("y", value)

    def zticks(self, value: Literal["auto", "manual", "mode"] | Sequence[float] | None = None) -> tuple[float, ...] | LimitMode | None:
        axes = self.require_active_axes()
        if not self.is_3d_axes(axes):
            return None
        return self._ticks_property("z", value)

    def xticklabels(self, value: Literal["auto", "manual", "mode"] | Sequence[Any] | None = None) -> tuple[str, ...] | LimitMode | None:
        return self._ticklabels_property("x", value)

    def yticklabels(self, value: Literal["auto", "manual", "mode"] | Sequence[Any] | None = None) -> tuple[str, ...] | LimitMode | None:
        return self._ticklabels_property("y", value)

    def zticklabels(self, value: Literal["auto", "manual", "mode"] | Sequence[Any] | None = None) -> tuple[str, ...] | LimitMode | None:
        axes = self.require_active_axes()
        if not self.is_3d_axes(axes):
            return None
        return self._ticklabels_property("z", value)

    def xticklabelrotation(self, value: Literal["auto", "manual", "mode"] | float | int | None = None) -> float | LimitMode | None:
        return self._ticklabel_rotation_property("x", value)

    def yticklabelrotation(self, value: Literal["auto", "manual", "mode"] | float | int | None = None) -> float | LimitMode | None:
        return self._ticklabel_rotation_property("y", value)

    def zticklabelrotation(self, value: Literal["auto", "manual", "mode"] | float | int | None = None) -> float | LimitMode | None:
        axes = self.require_active_axes()
        if not self.is_3d_axes(axes):
            return None
        return self._ticklabel_rotation_property("z", value)

    def layer(self, value: AxisLayer | None = None) -> AxisLayer | None:
        """MATLAB-like axes Layer property helper."""

        if value is None:
            return self.axis_layer
        normalized = self._normalize_axis_layer(value)
        if self.axis_layer == normalized:
            return None
        axes = self.require_active_axes()
        self.axis_layer = normalized
        self.set_axis_layer(axes, normalized)
        self._save_axes_ui_state(axes)
        self.push_current_view()
        return None

    def tickdir(self, value: TickDirection | Literal["mode"] | None = None) -> TickDirection | LimitMode | None:
        """MATLAB-like TickDir property helper."""

        if value is None:
            return self.tick_direction
        if isinstance(value, str) and value.strip().lower() == "mode":
            return self.tick_direction_mode
        normalized = self._normalize_tick_direction(value)
        if self.tick_direction == normalized and self.tick_direction_mode == "manual":
            return None
        axes = self.require_active_axes()
        self.tick_direction = normalized
        self.tick_direction_mode = "manual"
        self.set_tick_direction(axes, normalized)
        self._save_axes_ui_state(axes)
        self.push_current_view()
        return None

    def tickdirmode(self, value: Literal["auto", "manual", "mode"] | None = None) -> LimitMode | None:
        """MATLAB-like TickDirMode property helper."""

        if value is None or value == "mode":
            return self.tick_direction_mode
        original_value = value
        value = value.strip().lower()
        if value not in {"auto", "manual"}:
            raise ValueError(f"Unsupported tickdirmode value: {original_value!r}")
        if self.tick_direction_mode == value:
            return None
        axes = self.require_active_axes()
        self.tick_direction_mode = cast(LimitMode, value)
        self._save_axes_ui_state(axes)
        self.push_current_view()
        return None

    def ticklength(self, value: Sequence[float] | None = None) -> tuple[float, float] | None:
        """MATLAB-like TickLength property helper."""

        if value is None:
            return self.tick_length
        tick_length = self._parse_tick_length(value)
        if self.tick_length == tick_length:
            return None
        axes = self.require_active_axes()
        self.tick_length = tick_length
        self.set_tick_length(axes, tick_length)
        self._save_axes_ui_state(axes)
        self.push_current_view(axes)
        return None

    def xaxislocation(self, value: XAxisLocation | None = None) -> XAxisLocation | None:
        """MATLAB-like XAxisLocation property helper."""

        if value is None:
            return self.x_axis_location
        normalized = self._normalize_x_axis_location(value)
        if self.x_axis_location == normalized:
            return None
        axes = self.require_active_axes()
        self.x_axis_location = normalized
        self.set_x_axis_location(axes, normalized)
        self._save_axes_ui_state(axes)
        self.push_current_view(axes)
        return None

    def yaxislocation(self, value: YAxisLocation | None = None) -> YAxisLocation | None:
        """MATLAB-like YAxisLocation property helper."""

        if value is None:
            return self.y_axis_location
        normalized = self._normalize_y_axis_location(value)
        if self.y_axis_location == normalized:
            return None
        axes = self.require_active_axes()
        self.y_axis_location = normalized
        self.set_y_axis_location(axes, normalized)
        self._save_axes_ui_state(axes)
        self.push_current_view(axes)
        return None

    def _ticks_property(
        self,
        axis: Literal["x", "y", "z"],
        value: Literal["auto", "manual", "mode"] | Sequence[float] | None,
    ) -> tuple[float, ...] | LimitMode | None:
        ticks_attr = f"{axis}tick"
        mode_attr = f"{axis}tick_mode"
        axes = self.require_active_axes()
        if value is None:
            ticks = self.get_ticks(axes, axis)
            setattr(self, ticks_attr, ticks)
            return ticks
        if isinstance(value, str):
            original_value = value
            value = value.strip().lower()
            if value == "mode":
                return getattr(self, mode_attr)
            if value in {"auto", "manual"}:
                if getattr(self, mode_attr) == value:
                    return None
                setattr(self, mode_attr, value)
                self._save_axes_ui_state(axes)
                self.push_current_view(axes)
                return None
            raise ValueError(f"Unsupported {axis}ticks value: {original_value!r}")
        ticks = self._parse_ticks(value, f"{axis}ticks")
        if getattr(self, ticks_attr) == ticks and getattr(self, mode_attr) == "manual":
            return None
        setattr(self, ticks_attr, ticks)
        setattr(self, mode_attr, "manual")
        self.set_ticks(axes, axis, ticks)
        self._save_axes_ui_state(axes)
        self.push_current_view(axes)
        return None

    def _ticklabels_property(
        self,
        axis: Literal["x", "y", "z"],
        value: Literal["auto", "manual", "mode"] | Sequence[Any] | None,
    ) -> tuple[str, ...] | LimitMode | None:
        labels_attr = f"{axis}ticklabel"
        mode_attr = f"{axis}ticklabel_mode"
        axes = self.require_active_axes()
        if value is None:
            labels = self.get_ticklabels(axes, axis)
            setattr(self, labels_attr, labels)
            return labels
        if isinstance(value, str):
            original_value = value
            value = value.strip().lower()
            if value == "mode":
                return getattr(self, mode_attr)
            if value in {"auto", "manual"}:
                if getattr(self, mode_attr) == value:
                    return None
                setattr(self, mode_attr, value)
                self._save_axes_ui_state(axes)
                self.push_current_view(axes)
                return None
            raise ValueError(f"Unsupported {axis}ticklabels value: {original_value!r}")
        labels = self._normalize_ticklabels(axis, tuple(str(item) for item in value))
        if getattr(self, labels_attr) == labels and getattr(self, mode_attr) == "manual":
            return None
        setattr(self, labels_attr, labels)
        setattr(self, mode_attr, "manual")
        self.set_ticklabels(axes, axis, labels)
        self._save_axes_ui_state(axes)
        self.push_current_view(axes)
        return None

    def _ticklabel_rotation_property(
        self,
        axis: Literal["x", "y", "z"],
        value: Literal["auto", "manual", "mode"] | float | int | None,
    ) -> float | LimitMode | None:
        rotation_attr = f"{axis}ticklabel_rotation"
        mode_attr = f"{axis}ticklabel_rotation_mode"
        axes = self.require_active_axes()
        if value is None:
            return float(getattr(self, rotation_attr))
        if isinstance(value, str):
            original_value = value
            value = value.strip().lower()
            if value == "mode":
                return getattr(self, mode_attr)
            if value == "auto":
                if getattr(self, mode_attr) == "auto" and getattr(self, rotation_attr) == 0.0:
                    return None
                setattr(self, mode_attr, "auto")
                setattr(self, rotation_attr, 0.0)
                self.set_ticklabel_rotation(axes, axis, 0.0)
                self._save_axes_ui_state(axes)
                self.push_current_view(axes)
                return None
            if value == "manual":
                if getattr(self, mode_attr) == "manual":
                    return None
                setattr(self, mode_attr, "manual")
                self._save_axes_ui_state(axes)
                self.push_current_view(axes)
                return None
            raise ValueError(f"Unsupported {axis}ticklabelrotation value: {original_value!r}")
        rotation = self._parse_ticklabel_rotation(value, f"{axis}ticklabelrotation")
        if getattr(self, rotation_attr) == rotation and getattr(self, mode_attr) == "manual":
            return None
        setattr(self, rotation_attr, rotation)
        setattr(self, mode_attr, "manual")
        self.set_ticklabel_rotation(axes, axis, rotation)
        self._save_axes_ui_state(axes)
        self.push_current_view(axes)
        return None

    def _normalize_ticklabels(self, axis: Literal["x", "y", "z"], labels: tuple[str, ...]) -> tuple[str, ...]:
        tick_count = len(getattr(self, f"{axis}tick"))
        if tick_count == 0 and self.active_axes is not None:
            tick_count = len(self.get_ticks(self.active_axes, axis))
        if tick_count <= len(labels):
            return labels
        return (*labels, *("" for _ in range(tick_count - len(labels))))

    def set_clim(self, bottom: float, top: float) -> None:
        bottom, top = self._parse_numeric_limits((bottom, top), "clim")
        self._validate_limit_range((bottom, top), "clim")
        axes = self.require_active_axes()
        current = self.get_limits(axes)
        if current.clim == (bottom, top) and self.clim_mode == "manual":
            return
        self.set_limits(axes, AxesLimits(current.xlim, current.ylim, current.zlim, (bottom, top)))
        self.clim_mode = "manual"
        self.sync_linked_axes(axes, self.get_limits(axes))
        self.push_current_view()

    def clim(self, value: Literal["auto", "manual", "mode"] | Sequence[float] | None = None) -> tuple[float, float] | LimitMode | None:
        if value is None:
            return self.get_limits(self.require_active_axes()).clim
        if isinstance(value, str):
            original_value = value
            value = value.strip().lower()
            if value == "mode":
                return self.clim_mode
            if value == "auto":
                self.clim_mode = "auto"
                axes = self.require_active_axes()
                self.autoscale_clim(axes)
                self.push_current_view(axes)
                return None
            if value == "manual":
                if self.clim_mode == "manual":
                    return None
                self.clim_mode = "manual"
                self.push_current_view()
                return None
            raise ValueError(f"Unsupported clim value: {original_value!r}")
        limits = self._parse_numeric_limits(value, "clim")
        if len(limits) != 2:
            raise ValueError("clim limit vector must contain 2 values")
        self.set_clim(limits[0], limits[1])
        return None

    def daspect(
        self,
        value: Literal["auto", "manual", "mode"] | Sequence[float] | None = None,
    ) -> tuple[float, float, float] | AspectRatioMode | None:
        if value is None:
            return self.data_aspect_ratio
        if isinstance(value, str):
            original_value = value
            value = value.strip().lower()
            if value == "mode":
                return self.data_aspect_ratio_mode
            if value in {"auto", "manual"}:
                if self.data_aspect_ratio_mode == value:
                    return None
                self.data_aspect_ratio_mode = value
                self._save_axes_ui_state(self.active_axes)
                self.push_current_view()
                return None
            raise ValueError(f"Unsupported daspect value: {original_value!r}")
        ratio = self._parse_aspect_ratio(value, "daspect")
        if self.data_aspect_ratio == ratio and self.data_aspect_ratio_mode == "manual":
            return None
        axes = self.require_active_axes()
        self.data_aspect_ratio = ratio
        self.data_aspect_ratio_mode = "manual"
        self.set_data_aspect_ratio(axes, ratio)
        self._save_axes_ui_state(axes)
        self.push_current_view(axes)
        return None

    def pbaspect(
        self,
        value: Literal["auto", "manual", "mode"] | Sequence[float] | None = None,
    ) -> tuple[float, float, float] | AspectRatioMode | None:
        if value is None:
            return self.plot_box_aspect_ratio
        if isinstance(value, str):
            original_value = value
            value = value.strip().lower()
            if value == "mode":
                return self.plot_box_aspect_ratio_mode
            if value in {"auto", "manual"}:
                if self.plot_box_aspect_ratio_mode == value:
                    return None
                self.plot_box_aspect_ratio_mode = value
                self._save_axes_ui_state(self.active_axes)
                self.push_current_view()
                return None
            raise ValueError(f"Unsupported pbaspect value: {original_value!r}")
        ratio = self._parse_aspect_ratio(value, "pbaspect")
        if self.plot_box_aspect_ratio == ratio and self.plot_box_aspect_ratio_mode == "manual":
            return None
        axes = self.require_active_axes()
        self.plot_box_aspect_ratio = ratio
        self.plot_box_aspect_ratio_mode = "manual"
        self.set_plot_box_aspect_ratio(axes, ratio)
        self._save_axes_ui_state(axes)
        self.push_current_view(axes)
        return None

    def _parse_two_value_limits(self, value: Sequence[float], name: str) -> tuple[float, float]:
        limits = self._parse_numeric_limits(value, name)
        if len(limits) != 2:
            raise ValueError(f"{name} limit vector must contain 2 values")
        return limits

    def _parse_camera_vector(self, value: Sequence[float], name: str) -> tuple[float, float, float]:
        vector = tuple(float(item) for item in value)
        if len(vector) != 3:
            raise ValueError(f"{name} vector must contain 3 values")
        if not all(isfinite(item) for item in vector):
            raise ValueError(f"{name} vector must be finite")
        return vector

    def _parse_aspect_ratio(self, value: Sequence[float], name: str) -> tuple[float, float, float]:
        ratio = tuple(float(item) for item in value)
        if len(ratio) != 3:
            raise ValueError(f"{name} ratio must contain 3 values")
        if not all(isfinite(item) and item > 0.0 for item in ratio):
            raise ValueError(f"{name} ratio values must be finite and positive")
        return ratio

    def _parse_ticks(self, value: Sequence[float], name: str) -> tuple[float, ...]:
        ticks = tuple(float(item) for item in value)
        if not all(isfinite(item) for item in ticks):
            raise ValueError(f"{name} values must be finite and increasing")
        if any(right <= left for left, right in zip(ticks, ticks[1:])):
            raise ValueError(f"{name} values must be finite and increasing")
        return ticks

    def _parse_tick_length(self, value: Sequence[float]) -> tuple[float, float]:
        tick_length = tuple(float(item) for item in value)
        if len(tick_length) != 2:
            raise ValueError("ticklength vector must contain 2 values")
        if not all(isfinite(item) for item in tick_length):
            raise ValueError("ticklength values must be finite")
        return cast(tuple[float, float], tick_length)

    def _parse_ticklabel_rotation(self, value: float | int, name: str) -> float:
        rotation = float(value)
        if not isfinite(rotation):
            raise ValueError(f"{name} value must be finite")
        return rotation

    def _normalize_axis_layer(self, value: Any) -> AxisLayer:
        if not isinstance(value, str):
            raise ValueError(f"Unsupported layer value: {value!r}")
        normalized = value.strip().lower()
        if normalized not in {"bottom", "top"}:
            raise ValueError(f"Unsupported layer value: {value!r}")
        return cast(AxisLayer, normalized)

    def _normalize_tick_direction(self, value: Any) -> TickDirection:
        if not isinstance(value, str):
            raise ValueError(f"Unsupported tickdir value: {value!r}")
        normalized = value.strip().lower()
        if normalized not in {"in", "out", "both", "none"}:
            raise ValueError(f"Unsupported tickdir value: {value!r}")
        return cast(TickDirection, normalized)

    def _normalize_x_axis_location(self, value: Any) -> XAxisLocation:
        if not isinstance(value, str):
            raise ValueError(f"Unsupported xaxislocation value: {value!r}")
        normalized = value.strip().lower()
        if normalized not in {"bottom", "top", "origin"}:
            raise ValueError(f"Unsupported xaxislocation value: {value!r}")
        return cast(XAxisLocation, normalized)

    def _normalize_y_axis_location(self, value: Any) -> YAxisLocation:
        if not isinstance(value, str):
            raise ValueError(f"Unsupported yaxislocation value: {value!r}")
        normalized = value.strip().lower()
        if normalized not in {"left", "right", "origin"}:
            raise ValueError(f"Unsupported yaxislocation value: {value!r}")
        return cast(YAxisLocation, normalized)

    def _translate_camera_vector(
        self,
        vector: tuple[float, float, float] | None,
        delta: tuple[float, float, float],
    ) -> tuple[float, float, float] | None:
        if vector is None:
            return None
        return (vector[0] + delta[0], vector[1] + delta[1], vector[2] + delta[2])

    def _camera_target_from_limits(self, limits: AxesLimits) -> tuple[float, float, float] | None:
        if limits.zlim is None:
            return None
        return (
            (limits.xlim[0] + limits.xlim[1]) / 2.0,
            (limits.ylim[0] + limits.ylim[1]) / 2.0,
            (limits.zlim[0] + limits.zlim[1]) / 2.0,
        )

    def _camera_position_for_view(
        self,
        target: tuple[float, float, float],
        limits: AxesLimits,
        camera: Camera3DState,
    ) -> tuple[float, float, float]:
        x_span = abs(limits.xlim[1] - limits.xlim[0])
        y_span = abs(limits.ylim[1] - limits.ylim[0])
        z_span = abs(limits.zlim[1] - limits.zlim[0]) if limits.zlim is not None else 0.0
        radius = max(x_span, y_span, z_span, 1.0) * 2.0
        azim = radians(camera.azim)
        elev = radians(camera.elev)
        cos_elev = cos(elev)
        return (
            target[0] + radius * cos_elev * cos(azim),
            target[1] + radius * cos_elev * sin(azim),
            target[2] + radius * sin(elev),
        )

    def _pan_3d_camera(self, drag: _DragState, dx: float, dy: float) -> None:
        if drag.start_camera is None:
            return
        delta = self._pan_3d_delta(dx, dy)
        position = self._translate_camera_vector(drag.start_camera.position, delta)
        target = self._translate_camera_vector(drag.start_camera.target, delta)
        camera = Camera3DState(
            azim=drag.start_camera.azim,
            elev=drag.start_camera.elev,
            roll=drag.start_camera.roll,
            view_angle=drag.start_camera.view_angle,
            position=position,
            target=target,
            up_vector=drag.start_camera.up_vector,
        )
        if camera == self.get_camera3d(drag.axes):
            if self.camera_position_mode == "manual" and self.camera_target_mode == "manual":
                return
        self.set_camera3d(drag.axes, camera)
        self.camera_position_mode = "manual"
        self.camera_target_mode = "manual"
        self._save_axes_ui_state(drag.axes)

    def _pan_3d_delta(self, dx: float, dy: float) -> tuple[float, float, float]:
        if self.pan_motion == "horizontal":
            dy = 0.0
        elif self.pan_motion == "vertical":
            dx = 0.0
        return (-dx, -dy, 0.0)

    def _zoom_3d_camera(self, axes: Any, scale: float) -> bool:
        camera = self.get_camera3d(axes)
        if camera.view_angle is None:
            return False
        self.camzoom(1.0 / scale)
        return True

    def _parse_numeric_limits(self, value: Sequence[float], name: str) -> tuple[float, ...]:
        limits = tuple(float(item) for item in value)
        if any(limit != limit for limit in limits):
            raise ValueError(f"{name} limits must not contain NaN")
        return limits

    def _validate_limit_range(self, limits: tuple[float, float], name: str) -> None:
        if limits[1] <= limits[0]:
            raise ValueError(f"{name} limits must be strictly increasing")

    @overload
    def view(self) -> tuple[float, float] | None:
        ...

    @overload
    def view(self, value: View3DPreset | Sequence[float] | float) -> bool:
        ...

    @overload
    def view(self, azim: float, elev: float) -> bool:
        ...

    def view(
        self,
        value: View3DPreset | Sequence[float] | float | None = None,
        elev: float | None = None,
    ) -> tuple[float, float] | bool | None:
        axes = self.require_active_axes()
        if not self.is_3d_axes(axes):
            return None if value is None and elev is None else False
        if value is None and elev is None:
            camera = self.get_camera3d(axes)
            return (camera.azim, camera.elev)
        current_camera = self.get_camera3d(axes)
        if isinstance(value, str):
            original_value = value
            value = value.strip().lower()
            if value not in self._VIEW_3D_PRESETS:
                raise ValueError(f"Unsupported view preset: {original_value!r}")
            camera = self._with_current_view_angle(self._VIEW_3D_PRESETS[value], current_camera)
        elif elev is None:
            if isinstance(value, Sequence):
                angles = tuple(float(item) for item in value)
                if len(angles) != 2:
                    raise ValueError("view angle vector must contain 2 values")
                camera = self._with_current_view_angle(Camera3DState(azim=angles[0], elev=angles[1]), current_camera)
            elif value in (2, 2.0):
                camera = self._with_current_view_angle(self._VIEW_3D_PRESETS["2d"], current_camera)
            elif value in (3, 3.0):
                camera = self._with_current_view_angle(self._VIEW_3D_PRESETS["3d"], current_camera)
            else:
                raise ValueError("view requires a preset, [azim, elev], or azim and elev")
        else:
            if isinstance(value, Sequence):
                raise ValueError("view angle vector cannot be combined with an elevation argument")
            camera = self._with_current_view_angle(Camera3DState(azim=float(value), elev=float(elev)), current_camera)
        self._validate_camera_finite(camera)
        if current_camera == camera and self.camera_mode == "manual":
            return True
        self.set_camera3d(axes, camera)
        self.camera_mode = "manual"
        self._save_axes_ui_state(axes)
        self.push_current_view(axes)
        return True

    def view_3d(self, preset: View3DPreset | float) -> bool:
        result = self.view(preset)
        return bool(result)

    def set_view_3d(self, azim: float, elev: float) -> bool:
        result = self.view(azim, elev)
        return bool(result)

    def get_view_3d(self) -> tuple[float, float] | None:
        result = self.view()
        return result if isinstance(result, tuple) else None

    def camva(self, value: Literal["auto", "manual", "mode"] | float | None = None) -> float | CameraViewAngleMode | None:
        """MATLAB-like camera view-angle control for 3D axes."""

        axes = self.require_active_axes()
        if not self.is_3d_axes(axes):
            return None
        if value is None:
            return self.get_camera3d(axes).view_angle
        if isinstance(value, str):
            original_value = value
            value = value.strip().lower()
            if value == "mode":
                return self.camera_view_angle_mode
            if value == "auto":
                if self.camera_view_angle_mode == "auto":
                    return None
                self.camera_view_angle_mode = "auto"
                self._save_axes_ui_state(axes)
                self.push_current_view(axes)
                return None
            if value == "manual":
                if self.camera_view_angle_mode == "manual":
                    return None
                self.camera_view_angle_mode = "manual"
                self._save_axes_ui_state(axes)
                self.push_current_view(axes)
                return None
            raise ValueError(f"Unsupported camva value: {original_value!r}")
        view_angle = float(value)
        if not isfinite(view_angle):
            raise ValueError("camera view angle must be finite")
        camera = self.get_camera3d(axes)
        if camera.view_angle == view_angle and self.camera_view_angle_mode == "manual":
            return None
        self.set_camera3d(
            axes,
            Camera3DState(
                camera.azim,
                camera.elev,
                camera.roll,
                view_angle,
                camera.position,
                camera.target,
                camera.up_vector,
            ),
        )
        self.camera_view_angle_mode = "manual"
        self._save_axes_ui_state(axes)
        self.push_current_view(axes)
        return None

    def camzoom(self, factor: float) -> None:
        axes = self.require_active_axes()
        if not self.is_3d_axes(axes):
            return None
        factor = float(factor)
        if not isfinite(factor) or factor <= 0.0:
            raise ValueError("camzoom factor must be finite and greater than 0")
        camera = self.get_camera3d(axes)
        if camera.view_angle is None:
            return None
        view_angle = degrees(2.0 * atan(tan(radians(camera.view_angle) / 2.0) / factor))
        if camera.view_angle == view_angle and self.camera_view_angle_mode == "manual":
            return None
        self.set_camera3d(
            axes,
            Camera3DState(
                camera.azim,
                camera.elev,
                camera.roll,
                view_angle,
                camera.position,
                camera.target,
                camera.up_vector,
            ),
        )
        self.camera_view_angle_mode = "manual"
        self._save_axes_ui_state(axes)
        self.push_current_view(axes)
        return None

    def camorbit(self, dazim: float, delev: float) -> None:
        axes = self.require_active_axes()
        if not self.is_3d_axes(axes):
            return None
        dazim = float(dazim)
        delev = float(delev)
        if not self._is_finite_pair(dazim, delev):
            raise ValueError("camorbit deltas must be finite")
        camera = self.get_camera3d(axes)
        min_elev, max_elev = self.elevation_limits
        next_camera = Camera3DState(
            azim=self._normalize_azimuth(camera.azim + dazim),
            elev=max(min_elev, min(max_elev, camera.elev + delev)),
            roll=camera.roll,
            view_angle=camera.view_angle,
            position=camera.position,
            target=camera.target,
            up_vector=camera.up_vector,
        )
        self._validate_camera_finite(next_camera)
        if (
            camera == next_camera
            and self.camera_mode == "manual"
            and self.camera_position_mode == "manual"
            and self.camera_up_vector_mode == "manual"
        ):
            return None
        self.set_camera3d(axes, next_camera)
        self.camera_mode = "manual"
        self.camera_position_mode = "manual"
        self.camera_up_vector_mode = "manual"
        self._save_axes_ui_state(axes)
        self.push_current_view(axes)
        return None

    def camroll(self, angle: float) -> None:
        axes = self.require_active_axes()
        if not self.is_3d_axes(axes):
            return None
        angle = float(angle)
        if not isfinite(angle):
            raise ValueError("camroll angle must be finite")
        camera = self.get_camera3d(axes)
        next_camera = Camera3DState(
            azim=camera.azim,
            elev=camera.elev,
            roll=self._normalize_azimuth(camera.roll + angle),
            view_angle=camera.view_angle,
            position=camera.position,
            target=camera.target,
            up_vector=camera.up_vector,
        )
        self._validate_camera_finite(next_camera)
        if camera == next_camera and self.camera_up_vector_mode == "manual":
            return None
        self.set_camera3d(axes, next_camera)
        self.camera_mode = "manual"
        self.camera_up_vector_mode = "manual"
        self._save_axes_ui_state(axes)
        self.push_current_view(axes)
        return None

    def camdolly(self, dx: float, dy: float, dz: float) -> None:
        axes = self.require_active_axes()
        if not self.is_3d_axes(axes):
            return None
        delta = self._parse_camera_vector((dx, dy, dz), "camdolly")
        camera = self.get_camera3d(axes)
        position = self._translate_camera_vector(camera.position, delta)
        target = self._translate_camera_vector(camera.target, delta)
        next_camera = Camera3DState(
            azim=camera.azim,
            elev=camera.elev,
            roll=camera.roll,
            view_angle=camera.view_angle,
            position=position,
            target=target,
            up_vector=camera.up_vector,
        )
        self._validate_camera_finite(next_camera)
        if (
            camera == next_camera
            and self.camera_position_mode == "manual"
            and self.camera_target_mode == "manual"
        ):
            return None
        self.set_camera3d(axes, next_camera)
        self.camera_position_mode = "manual"
        self.camera_target_mode = "manual"
        self._save_axes_ui_state(axes)
        self.push_current_view(axes)
        return None

    def campos(
        self,
        value: Literal["auto", "manual", "mode"] | Sequence[float] | None = None,
    ) -> tuple[float, float, float] | CameraVectorMode | None:
        return self._camera_vector_property("position", "camera_position_mode", "campos", value)

    def camtarget(
        self,
        value: Literal["auto", "manual", "mode"] | Sequence[float] | None = None,
    ) -> tuple[float, float, float] | CameraVectorMode | None:
        return self._camera_vector_property("target", "camera_target_mode", "camtarget", value)

    def camup(
        self,
        value: Literal["auto", "manual", "mode"] | Sequence[float] | None = None,
    ) -> tuple[float, float, float] | CameraVectorMode | None:
        return self._camera_vector_property("up_vector", "camera_up_vector_mode", "camup", value)

    def camproj(self, value: CameraProjection | str | None = None) -> CameraProjection | None:
        """MATLAB-like camera projection control for 3D axes."""

        axes = self.require_active_axes()
        if not self.is_3d_axes(axes):
            return None
        if value is None:
            projection = self.get_camera_projection(axes)
            self.camera_projection = projection
            return projection
        original_value = value
        projection = str(value).strip().lower()
        if projection not in {"orthographic", "perspective"}:
            raise ValueError(f"Unsupported camproj value: {original_value!r}")
        projection = cast(CameraProjection, projection)
        if self.get_camera_projection(axes) == projection and self.camera_projection == projection:
            return None
        self.set_camera_projection(axes, projection)
        self.camera_projection = projection
        self._save_axes_ui_state(axes)
        self.push_current_view(axes)
        return None

    def camlookat(self) -> None:
        """MATLAB-like camera look-at fit helper for 3D axes."""

        axes = self.require_active_axes()
        if not self.is_3d_axes(axes):
            return None
        limits = self.get_limits(axes)
        target_from_limits = self._camera_target_from_limits(limits)
        if target_from_limits is None:
            return None
        camera = self.get_camera3d(axes)
        target = camera.target if camera.target is not None else target_from_limits
        position = camera.position if camera.position is not None else self._camera_position_for_view(target, limits, camera)
        view_angle = camera.view_angle if camera.view_angle is not None else 10.0
        next_camera = Camera3DState(
            azim=camera.azim,
            elev=camera.elev,
            roll=camera.roll,
            view_angle=view_angle,
            position=position,
            target=target,
            up_vector=camera.up_vector,
        )
        self._validate_camera_finite(next_camera)
        if (
            camera == next_camera
            and self.camera_position_mode == "manual"
            and self.camera_target_mode == "manual"
            and self.camera_view_angle_mode == "manual"
        ):
            return None
        self.set_camera3d(axes, next_camera)
        self.camera_position_mode = "manual"
        self.camera_target_mode = "manual"
        self.camera_view_angle_mode = "manual"
        self._save_axes_ui_state(axes)
        self.push_current_view(axes)
        return None

    def _camera_vector_property(
        self,
        field: Literal["position", "target", "up_vector"],
        mode_attr: Literal["camera_position_mode", "camera_target_mode", "camera_up_vector_mode"],
        name: str,
        value: Literal["auto", "manual", "mode"] | Sequence[float] | None,
    ) -> tuple[float, float, float] | CameraVectorMode | None:
        axes = self.require_active_axes()
        if not self.is_3d_axes(axes):
            return None
        if value is None:
            return getattr(self.get_camera3d(axes), field)
        if isinstance(value, str):
            original_value = value
            value = value.strip().lower()
            if value == "mode":
                return getattr(self, mode_attr)
            if value in {"auto", "manual"}:
                if getattr(self, mode_attr) == value:
                    return None
                setattr(self, mode_attr, value)
                self._save_axes_ui_state(axes)
                self.push_current_view(axes)
                return None
            raise ValueError(f"Unsupported {name} value: {original_value!r}")
        vector = self._parse_camera_vector(value, name)
        camera = self.get_camera3d(axes)
        if getattr(camera, field) == vector and getattr(self, mode_attr) == "manual":
            return None
        kwargs = {
            "azim": camera.azim,
            "elev": camera.elev,
            "roll": camera.roll,
            "view_angle": camera.view_angle,
            "position": camera.position,
            "target": camera.target,
            "up_vector": camera.up_vector,
        }
        kwargs[field] = vector
        self.set_camera3d(axes, Camera3DState(**kwargs))
        setattr(self, mode_attr, "manual")
        self._save_axes_ui_state(axes)
        self.push_current_view(axes)
        return None

    def push_current_view(self, axes: Any | None = None) -> None:
        state = self.current_view_state(axes)
        if state is None:
            return

        if self.view_index >= 0 and self.view_stack[self.view_index] == state:
            return
        if state.axes is not self.active_axes:
            base_index = self._last_view_index_for_axes(state.axes)
            if base_index is not None:
                self.view_index = base_index
        del self.view_stack[self.view_index + 1 :]
        self.view_stack.append(state)
        self.view_index = len(self.view_stack) - 1
        self.on_view_history_changed()

    def clear_view_history(self, axes: Any | None = None) -> None:
        """Clear home/back/forward state for a fresh axes view lifecycle."""

        if axes is None:
            if not self.view_stack and self.view_index == -1:
                return
            self.view_stack.clear()
            self.view_index = -1
            self.on_view_history_changed()
            return

        old_stack = self.view_stack
        self.view_stack = [state for state in self.view_stack if state.axes is not axes]
        if len(self.view_stack) == len(old_stack):
            return
        if not self.view_stack:
            self.view_index = -1
        elif 0 <= self.view_index < len(old_stack) and old_stack[self.view_index].axes is axes:
            self.view_index = min(len(self.view_stack) - 1, self._last_view_index_for_active_axes() or 0)
        else:
            self.view_index = min(self.view_index, len(self.view_stack) - 1)
        self.on_view_history_changed()

    def current_view_state(self, axes: Any | None = None) -> ViewState | None:
        axes = axes if axes is not None else self.active_axes
        if axes is None:
            return None
        state = self._current_axes_ui_state(axes)
        camera = self._current_camera_snapshot(axes)
        if self.is_3d_axes(axes) and camera is None:
            return None
        return ViewState(
            axes=axes,
            limits=self.get_limits(axes),
            xlim_mode=state.xlim_mode,
            ylim_mode=state.ylim_mode,
            zlim_mode=state.zlim_mode,
            clim_mode=state.clim_mode,
            xtick=state.xtick,
            ytick=state.ytick,
            ztick=state.ztick,
            xtick_mode=state.xtick_mode,
            ytick_mode=state.ytick_mode,
            ztick_mode=state.ztick_mode,
            xticklabel=state.xticklabel,
            yticklabel=state.yticklabel,
            zticklabel=state.zticklabel,
            xticklabel_mode=state.xticklabel_mode,
            yticklabel_mode=state.yticklabel_mode,
            zticklabel_mode=state.zticklabel_mode,
            xticklabel_rotation=state.xticklabel_rotation,
            yticklabel_rotation=state.yticklabel_rotation,
            zticklabel_rotation=state.zticklabel_rotation,
            xticklabel_rotation_mode=state.xticklabel_rotation_mode,
            yticklabel_rotation_mode=state.yticklabel_rotation_mode,
            zticklabel_rotation_mode=state.zticklabel_rotation_mode,
            axes_title=state.axes_title,
            xlabel_text=state.xlabel_text,
            ylabel_text=state.ylabel_text,
            zlabel_text=state.zlabel_text,
            aspect=state.aspect,
            box_aspect=state.box_aspect,
            data_aspect_ratio=state.data_aspect_ratio,
            data_aspect_ratio_mode=state.data_aspect_ratio_mode,
            plot_box_aspect_ratio=state.plot_box_aspect_ratio,
            plot_box_aspect_ratio_mode=state.plot_box_aspect_ratio_mode,
            axis_visible=state.axis_visible,
            grid_visible=state.grid_visible,
            minor_grid_visible=state.minor_grid_visible,
            x_grid_visible=state.x_grid_visible,
            y_grid_visible=state.y_grid_visible,
            z_grid_visible=state.z_grid_visible,
            x_minor_grid_visible=state.x_minor_grid_visible,
            y_minor_grid_visible=state.y_minor_grid_visible,
            z_minor_grid_visible=state.z_minor_grid_visible,
            x_minor_tick_visible=state.x_minor_tick_visible,
            y_minor_tick_visible=state.y_minor_tick_visible,
            z_minor_tick_visible=state.z_minor_tick_visible,
            box_visible=state.box_visible,
            legend_visible=state.legend_visible,
            x_direction=state.x_direction,
            y_direction=state.y_direction,
            z_direction=state.z_direction,
            x_scale=state.x_scale,
            y_scale=state.y_scale,
            z_scale=state.z_scale,
            axis_layer=state.axis_layer,
            tick_direction=state.tick_direction,
            tick_direction_mode=state.tick_direction_mode,
            tick_length=state.tick_length,
            x_axis_location=state.x_axis_location,
            y_axis_location=state.y_axis_location,
            camera_mode=state.camera_mode,
            camera_view_angle_mode=state.camera_view_angle_mode,
            camera_position_mode=state.camera_position_mode,
            camera_target_mode=state.camera_target_mode,
            camera_up_vector_mode=state.camera_up_vector_mode,
            camera_projection=state.camera_projection,
            hold_enabled=state.hold_enabled,
            next_plot=state.next_plot,
            color_order=state.color_order,
            line_style_order=state.line_style_order,
            next_series_index=state.next_series_index,
            camera=camera,
        )

    def _current_axes_ui_state(self, axes: Any) -> AxesUIState:
        if axes is self.active_axes:
            self._save_axes_ui_state(axes)
        return self._axes_ui_state.get(axes, AxesUIState())

    def _save_axes_ui_state(self, axes: Any | None) -> None:
        if axes is None:
            return
        self._axes_ui_state[axes] = AxesUIState(
            xlim_mode=self.xlim_mode,
            ylim_mode=self.ylim_mode,
            zlim_mode=self.zlim_mode,
            clim_mode=self.clim_mode,
            xtick=self.xtick,
            ytick=self.ytick,
            ztick=self.ztick,
            xtick_mode=self.xtick_mode,
            ytick_mode=self.ytick_mode,
            ztick_mode=self.ztick_mode,
            xticklabel=self.xticklabel,
            yticklabel=self.yticklabel,
            zticklabel=self.zticklabel,
            xticklabel_mode=self.xticklabel_mode,
            yticklabel_mode=self.yticklabel_mode,
            zticklabel_mode=self.zticklabel_mode,
            xticklabel_rotation=self.xticklabel_rotation,
            yticklabel_rotation=self.yticklabel_rotation,
            zticklabel_rotation=self.zticklabel_rotation,
            xticklabel_rotation_mode=self.xticklabel_rotation_mode,
            yticklabel_rotation_mode=self.yticklabel_rotation_mode,
            zticklabel_rotation_mode=self.zticklabel_rotation_mode,
            axes_title=self.axes_title,
            xlabel_text=self.xlabel_text,
            ylabel_text=self.ylabel_text,
            zlabel_text=self.zlabel_text,
            aspect=self.axis_aspect,
            box_aspect=self.box_aspect,
            data_aspect_ratio=self.data_aspect_ratio,
            data_aspect_ratio_mode=self.data_aspect_ratio_mode,
            plot_box_aspect_ratio=self.plot_box_aspect_ratio,
            plot_box_aspect_ratio_mode=self.plot_box_aspect_ratio_mode,
            axis_visible=self.axis_visible,
            grid_visible=self.grid_is_enabled(axes),
            minor_grid_visible=self.minor_grid_is_enabled(axes),
            x_grid_visible=self.axis_grid_is_enabled(axes, "x", minor=False),
            y_grid_visible=self.axis_grid_is_enabled(axes, "y", minor=False),
            z_grid_visible=self.axis_grid_is_enabled(axes, "z", minor=False) if self.is_3d_axes(axes) else False,
            x_minor_grid_visible=self.axis_grid_is_enabled(axes, "x", minor=True),
            y_minor_grid_visible=self.axis_grid_is_enabled(axes, "y", minor=True),
            z_minor_grid_visible=self.axis_grid_is_enabled(axes, "z", minor=True) if self.is_3d_axes(axes) else False,
            x_minor_tick_visible=self.axis_minor_tick_is_enabled(axes, "x"),
            y_minor_tick_visible=self.axis_minor_tick_is_enabled(axes, "y"),
            z_minor_tick_visible=self.axis_minor_tick_is_enabled(axes, "z") if self.is_3d_axes(axes) else False,
            box_visible=self.box_is_enabled(axes),
            legend_visible=self.legend_is_enabled(axes),
            x_direction=self.x_direction,
            y_direction=self.y_direction,
            z_direction=self.z_direction,
            x_scale=self.x_scale,
            y_scale=self.y_scale,
            z_scale=self.z_scale,
            axis_layer=self.axis_layer,
            tick_direction=self.tick_direction,
            tick_direction_mode=self.tick_direction_mode,
            tick_length=self.tick_length,
            x_axis_location=self.x_axis_location,
            y_axis_location=self.y_axis_location,
            camera_mode=self.camera_mode,
            camera_view_angle_mode=self.camera_view_angle_mode,
            camera_position_mode=self.camera_position_mode,
            camera_target_mode=self.camera_target_mode,
            camera_up_vector_mode=self.camera_up_vector_mode,
            camera_projection=self.camera_projection,
            hold_enabled=self.hold_enabled,
            next_plot=self.next_plot,
            color_order=self.color_order,
            line_style_order=self.line_style_order,
            next_series_index=self.next_series_index,
        )

    def _load_axes_ui_state(self, axes: Any | None) -> None:
        state = self._axes_ui_state.get(axes) if axes is not None else None
        if state is None:
            state = AxesUIState()
            if axes is not None:
                self._axes_ui_state[axes] = state
        self.xlim_mode = state.xlim_mode
        self.ylim_mode = state.ylim_mode
        self.zlim_mode = state.zlim_mode
        self.clim_mode = state.clim_mode
        self.xtick = state.xtick
        self.ytick = state.ytick
        self.ztick = state.ztick
        self.xtick_mode = state.xtick_mode
        self.ytick_mode = state.ytick_mode
        self.ztick_mode = state.ztick_mode
        self.xticklabel = state.xticklabel
        self.yticklabel = state.yticklabel
        self.zticklabel = state.zticklabel
        self.xticklabel_mode = state.xticklabel_mode
        self.yticklabel_mode = state.yticklabel_mode
        self.zticklabel_mode = state.zticklabel_mode
        self.xticklabel_rotation = state.xticklabel_rotation
        self.yticklabel_rotation = state.yticklabel_rotation
        self.zticklabel_rotation = state.zticklabel_rotation
        self.xticklabel_rotation_mode = state.xticklabel_rotation_mode
        self.yticklabel_rotation_mode = state.yticklabel_rotation_mode
        self.zticklabel_rotation_mode = state.zticklabel_rotation_mode
        self.axes_title = state.axes_title
        self.xlabel_text = state.xlabel_text
        self.ylabel_text = state.ylabel_text
        self.zlabel_text = state.zlabel_text
        self.axis_aspect = state.aspect
        self.box_aspect = state.box_aspect
        self.data_aspect_ratio = state.data_aspect_ratio
        self.data_aspect_ratio_mode = state.data_aspect_ratio_mode
        self.plot_box_aspect_ratio = state.plot_box_aspect_ratio
        self.plot_box_aspect_ratio_mode = state.plot_box_aspect_ratio_mode
        self.axis_visible = state.axis_visible
        if axes is not None:
            self._apply_grid_state(axes, state)
            self.set_box_visible(axes, state.box_visible)
            self.set_legend_visible(axes, state.legend_visible)
            self.set_x_direction(axes, state.x_direction)
            self.set_y_direction(axes, state.y_direction)
            self.set_z_direction(axes, state.z_direction)
            self.set_axis_scale(axes, "x", state.x_scale)
            self.set_axis_scale(axes, "y", state.y_scale)
            self.set_axis_scale(axes, "z", state.z_scale)
            self.set_axis_layer(axes, state.axis_layer)
            self.set_tick_direction(axes, state.tick_direction)
            self.set_tick_length(axes, state.tick_length)
            self.set_x_axis_location(axes, state.x_axis_location)
            self.set_y_axis_location(axes, state.y_axis_location)
            if state.xtick_mode == "manual":
                self.set_ticks(axes, "x", state.xtick)
            if state.ytick_mode == "manual":
                self.set_ticks(axes, "y", state.ytick)
            if state.ztick_mode == "manual":
                self.set_ticks(axes, "z", state.ztick)
            self.set_ticklabel_rotation(axes, "x", state.xticklabel_rotation)
            self.set_ticklabel_rotation(axes, "y", state.yticklabel_rotation)
            if self.is_3d_axes(axes):
                self.set_ticklabel_rotation(axes, "z", state.zticklabel_rotation)
            if state.xticklabel_mode == "manual":
                self.set_ticklabels(axes, "x", state.xticklabel)
            if state.yticklabel_mode == "manual":
                self.set_ticklabels(axes, "y", state.yticklabel)
            if state.zticklabel_mode == "manual":
                self.set_ticklabels(axes, "z", state.zticklabel)
            self.set_axes_text(axes, "title", state.axes_title)
            self.set_axes_text(axes, "xlabel", state.xlabel_text)
            self.set_axes_text(axes, "ylabel", state.ylabel_text)
            self.set_axes_text(axes, "zlabel", state.zlabel_text)
        self.x_direction = state.x_direction
        self.y_direction = state.y_direction
        self.z_direction = state.z_direction
        self.x_scale = state.x_scale
        self.y_scale = state.y_scale
        self.z_scale = state.z_scale
        self.axis_layer = state.axis_layer
        self.tick_direction = state.tick_direction
        self.tick_direction_mode = state.tick_direction_mode
        self.tick_length = state.tick_length
        self.x_axis_location = state.x_axis_location
        self.y_axis_location = state.y_axis_location
        self.camera_mode = state.camera_mode
        self.camera_view_angle_mode = state.camera_view_angle_mode
        self.camera_position_mode = state.camera_position_mode
        self.camera_target_mode = state.camera_target_mode
        self.camera_up_vector_mode = state.camera_up_vector_mode
        self.camera_projection = state.camera_projection
        if axes is not None and self.is_3d_axes(axes):
            self.set_camera_projection(axes, state.camera_projection)
        self.hold_enabled = state.hold_enabled
        self.next_plot = state.next_plot
        self.color_order = state.color_order or self.DEFAULT_COLOR_ORDER
        self.line_style_order = state.line_style_order or self.DEFAULT_LINE_STYLE_ORDER
        self.next_series_index = state.next_series_index

    def home(self) -> bool:
        if not self.can_home():
            return False
        index = self._home_index()
        if index is None:
            return False
        self.view_index = index
        self._restore_view(self.view_stack[index])
        self.on_view_history_changed()
        return True

    def back(self) -> bool:
        if not self.can_back():
            return False
        index = self._previous_view_index()
        if index is None:
            return False
        self.view_index = index
        self._restore_view(self.view_stack[self.view_index])
        self.on_view_history_changed()
        return True

    def forward(self) -> bool:
        if not self.can_forward():
            return False
        index = self._next_view_index()
        if index is None:
            return False
        self.view_index = index
        self._restore_view(self.view_stack[self.view_index])
        self.on_view_history_changed()
        return True

    def can_home(self) -> bool:
        return self._home_index() is not None

    def can_back(self) -> bool:
        return self._previous_view_index() is not None

    def can_forward(self) -> bool:
        return self._next_view_index() is not None

    def _home_index(self) -> int | None:
        axes = self.active_axes
        if axes is None:
            return None
        for index, state in enumerate(self.view_stack):
            if state.axes is axes:
                return index
        return None

    def _previous_view_index(self) -> int | None:
        axes = self.active_axes
        if axes is None:
            return None
        start = self._active_history_cursor_index()
        for index in range(start - 1, -1, -1):
            if self.view_stack[index].axes is axes:
                return index
        return None

    def _next_view_index(self) -> int | None:
        axes = self.active_axes
        if axes is None:
            return None
        start = self._active_history_cursor_index()
        for index in range(start + 1, len(self.view_stack)):
            if self.view_stack[index].axes is axes:
                return index
        return None

    def _active_history_cursor_index(self) -> int:
        if 0 <= self.view_index < len(self.view_stack) and self.view_stack[self.view_index].axes is self.active_axes:
            return self.view_index
        index = self._last_view_index_for_active_axes()
        return len(self.view_stack) if index is None else index

    def _last_view_index_for_active_axes(self) -> int | None:
        return self._last_view_index_for_axes(self.active_axes)

    def _last_view_index_for_axes(self, axes: Any | None) -> int | None:
        if axes is None:
            return None
        for index in range(len(self.view_stack) - 1, -1, -1):
            if self.view_stack[index].axes is axes:
                return index
        return None

    def _select_latest_view_for_active_axes(self) -> None:
        index = self._last_view_index_for_active_axes()
        if index is None or index == self.view_index:
            return
        self.view_index = index
        self.on_view_history_changed()

    def linkaxes(self, axes: Iterable[Any] | Any, option: LinkAxesAxis | Literal["off"] | str = "xy") -> None:
        axes_set = self._axes_set_for_linking(axes)
        option = str(option).strip().lower()
        if option not in {"x", "y", "xy", "off"}:
            raise ValueError(f"Unsupported linkaxes option: {option!r}")
        if option == "off":
            self._unlink_axes_set(axes_set)
            return None
        axis = cast(LinkAxesAxis, option)
        self._link_axes_set(axes_set, axis)
        self._sync_linked_axes_to_union(axes_set, axis)
        return None

    def link_axes(self, axes: Iterable[Any], axis: LinkAxesAxis = "x") -> None:
        axes_set = self._axes_set_for_linking(axes)
        self._link_axes_set(axes_set, axis)

    def _axes_set_for_linking(self, axes: Iterable[Any] | Any) -> set[Any]:
        if isinstance(axes, (str, bytes)):
            raise ValueError("link_axes requires axes objects, not strings")
        try:
            axes_set = set(axes)
        except TypeError:
            axes_set = {axes}
        if len(axes_set) < 1:
            raise ValueError("link_axes requires at least one axes")
        return axes_set

    def _link_axes_set(self, axes_set: set[Any], axis: LinkAxesAxis) -> None:
        if axis not in {"x", "y", "xy"}:
            raise ValueError(f"Unsupported link_axes axis: {axis!r}")
        if len(axes_set) < 2:
            return
        self._linked = [
            (linked_axes, linked_axis)
            for linked_axes, linked_axis in self._linked
            if not (linked_axis == axis and linked_axes == axes_set)
        ]
        self._linked.append((axes_set, axis))

    def unlink_axes(self, axis: LinkAxesAxis | None = None) -> None:
        if axis is None:
            self._linked.clear()
            return
        self._linked = [(axes_set, linked_axis) for axes_set, linked_axis in self._linked if linked_axis != axis]

    def _unlink_axes_set(self, axes_set: set[Any]) -> None:
        self._linked = [(linked_axes, linked_axis) for linked_axes, linked_axis in self._linked if linked_axes != axes_set]

    def _sync_linked_axes_to_union(self, axes_set: set[Any], axis: LinkAxesAxis) -> None:
        if len(axes_set) < 2:
            return
        limits_by_axes = [(axes, self.get_limits(axes)) for axes in axes_set]
        xlim = self._union_limit_pair(limits.xlim for _, limits in limits_by_axes)
        ylim = self._union_limit_pair(limits.ylim for _, limits in limits_by_axes)
        for axes, limits in limits_by_axes:
            next_limits = AxesLimits(
                xlim if "x" in axis else limits.xlim,
                ylim if "y" in axis else limits.ylim,
                limits.zlim,
                limits.clim,
            )
            self.set_limits(axes, next_limits)
            self._mark_linked_axes_modes_manual(axes, axis)

    def _union_limit_pair(self, limits: Iterable[tuple[float, float]]) -> tuple[float, float]:
        pairs = list(limits)
        return (min(pair[0] for pair in pairs), max(pair[1] for pair in pairs))

    def on_mouse_press(self, event: PointerEvent) -> None:
        if event.axes is None:
            return
        self.set_active_axes(event.axes)
        button = event.normalized_button()
        if event.dblclick and button == MouseButton.LEFT:
            self.home()
            return
        if self.mode == InteractionMode.PAN:
            if button != MouseButton.LEFT:
                return
            if event.xdata is None or event.ydata is None or not self._is_finite_pair(event.xdata, event.ydata):
                return
            if self.button_down_filter(event):
                return
            self.action_pre_callback(self.mode, event)
            self._drag = _DragState(
                axes=event.axes,
                start_x=event.xdata,
                start_y=event.ydata,
                start_limits=self.get_limits(event.axes),
                modifiers=event.modifiers,
                start_view=self.current_view_state(event.axes),
                start_screen_x=event.x,
                start_screen_y=event.y,
                start_camera=self.get_camera3d(event.axes) if self.is_3d_axes(event.axes) else None,
            )
        elif self.mode == InteractionMode.ZOOM:
            if event.xdata is None or event.ydata is None or not self._is_finite_pair(event.xdata, event.ydata):
                return
            if button == MouseButton.RIGHT:
                if self.zoom_right_click_action == "inversezoom":
                    if self.button_down_filter(event):
                        return
                    self.action_pre_callback(self.mode, event)
                    self.on_point_zoom(event.axes, event.xdata, event.ydata, self.zoom_right_click_scale)
                    self.action_post_callback(self.mode, event)
                return
            if button != MouseButton.LEFT:
                return
            if self.button_down_filter(event):
                return
            self.action_pre_callback(self.mode, event)
            self._zoom_drag = _ZoomDragState(event.axes, event.xdata, event.ydata, event.x, event.y)
            self.begin_zoom_box(event.axes, event.xdata, event.ydata)
        elif self.mode == InteractionMode.ROTATE3D and self.is_3d_axes(event.axes):
            if button != MouseButton.LEFT:
                return
            start_x = event.x if event.x is not None else event.xdata
            start_y = event.y if event.y is not None else event.ydata
            if start_x is None or start_y is None or not self._is_finite_pair(start_x, start_y):
                return
            if self.button_down_filter(event):
                return
            self.action_pre_callback(self.mode, event)
            self._rotate_drag = _RotateDragState(
                event.axes,
                start_x,
                start_y,
                self.get_camera3d(event.axes),
                self.current_view_state(event.axes),
            )
        elif self.mode == InteractionMode.DATA_CURSOR:
            if button != MouseButton.LEFT:
                return
            if event.xdata is None or event.ydata is None or not self._is_finite_pair(event.xdata, event.ydata):
                return
            self.create_data_tip(event.axes, event.xdata, event.ydata)
        elif self.mode == InteractionMode.SELECT:
            if button != MouseButton.LEFT:
                return
            if event.xdata is None or event.ydata is None or not self._is_finite_pair(event.xdata, event.ydata):
                return
            self.select_nearest_artist(event.axes, event.xdata, event.ydata, event.modifiers)
        elif self.mode == InteractionMode.BRUSH:
            if button != MouseButton.LEFT:
                return
            if event.xdata is None or event.ydata is None or not self._is_finite_pair(event.xdata, event.ydata):
                return
            self._brush_drag = _BrushDragState(event.axes, event.xdata, event.ydata)
            self.begin_brush_box(event.axes, event.xdata, event.ydata)

    def on_mouse_move(self, event: PointerEvent) -> None:
        self.hover_axes = event.axes
        if (
            event.axes is not None
            and event.xdata is not None
            and event.ydata is not None
            and self._is_finite_pair(event.xdata, event.ydata)
        ):
            self.update_coordinate_readout(event.axes, event.xdata, event.ydata)
        if self._rotate_drag is not None and self.mode == InteractionMode.ROTATE3D:
            current_x = event.x
            current_y = event.y
            if current_x is None or current_y is None:
                if event.axes is not self._rotate_drag.axes:
                    return
                current_x = event.xdata
                current_y = event.ydata
            if current_x is None or current_y is None or not self._is_finite_pair(current_x, current_y):
                return
            dx = current_x - self._rotate_drag.start_x
            dy = current_y - self._rotate_drag.start_y
            if (dx * dx + dy * dy) ** 0.5 < self.rotate_drag_pixel_threshold:
                return
            camera = self._rotate_camera(self._rotate_drag.start_camera, dx, dy)
            if camera == self.get_camera3d(self._rotate_drag.axes):
                return
            axes = self._rotate_drag.axes
            self.set_camera3d(axes, camera)
            self.camera_mode = "manual"
            if self.rotate_style == "orbit":
                self.camera_position_mode = "manual"
                self.camera_up_vector_mode = "manual"
            self._save_axes_ui_state(axes)
            return
        if self._zoom_drag is not None and self.mode == InteractionMode.ZOOM:
            if event.xdata is None or event.ydata is None or not self._is_finite_pair(event.xdata, event.ydata):
                return
            self.update_zoom_box(
                self._zoom_drag.axes,
                self._zoom_drag.start_xdata,
                self._zoom_drag.start_ydata,
                event.xdata,
                event.ydata,
            )
            return
        if self._brush_drag is not None and self.mode == InteractionMode.BRUSH:
            if event.xdata is None or event.ydata is None or not self._is_finite_pair(event.xdata, event.ydata):
                return
            self.update_brush_box(
                self._brush_drag.axes,
                self._brush_drag.start_xdata,
                self._brush_drag.start_ydata,
                event.xdata,
                event.ydata,
            )
            return
        if self._drag is None or self.mode != InteractionMode.PAN:
            return
        if event.xdata is None or event.ydata is None or not self._is_finite_pair(event.xdata, event.ydata):
            return
        dx = event.xdata - self._drag.start_x
        dy = event.ydata - self._drag.start_y
        if "shift" in self._drag.modifiers:
            if self._pan_shift_constraint_is_horizontal(self._drag, event, dx, dy):
                dy = 0.0
            else:
                dx = 0.0
        if self.is_3d_axes(self._drag.axes) and self.pan_3d_mode == "camera":
            self._pan_3d_camera(self._drag, dx, dy)
            return
        limits = self._pan_limits(self._drag.start_limits, self._drag.start_x, self._drag.start_y, dx, dy)
        self._set_user_limits(self._drag.axes, self._apply_motion_to_limits(self._drag.start_limits, limits, self.pan_motion))

    def on_mouse_release(self, event: PointerEvent) -> None:
        post_modes = self._active_action_modes()
        if self._drag is not None and self._view_changed_since(self._drag.axes, self._drag.start_view):
            self.push_current_view(self._drag.axes)
        if self._zoom_drag is not None:
            zoom_drag = self._zoom_drag
            if (
                event.axes is zoom_drag.axes
                and event.xdata is not None
                and event.ydata is not None
                and self._is_finite_pair(event.xdata, event.ydata)
            ):
                if self._is_zoom_click(zoom_drag, event):
                    self.on_point_zoom(zoom_drag.axes, zoom_drag.start_xdata, zoom_drag.start_ydata, self._zoom_click_scale_for_direction())
                else:
                    self.on_box_zoom(
                        zoom_drag.axes,
                        (zoom_drag.start_xdata, zoom_drag.start_ydata),
                        (event.xdata, event.ydata),
                    )
            self.end_zoom_box()
        if self._rotate_drag is not None and self._view_changed_since(self._rotate_drag.axes, self._rotate_drag.start_view):
            self.push_current_view(self._rotate_drag.axes)
        if self._brush_drag is not None:
            brush_drag = self._brush_drag
            if (
                event.axes is brush_drag.axes
                and event.xdata is not None
                and event.ydata is not None
                and self._is_finite_pair(event.xdata, event.ydata)
            ):
                self.brush_box(
                    brush_drag.axes,
                    (brush_drag.start_xdata, brush_drag.start_ydata),
                    (event.xdata, event.ydata),
                    event.modifiers,
                )
            self.end_brush_box()
        self._drag = None
        self._zoom_drag = None
        self._brush_drag = None
        self._rotate_drag = None
        for post_mode in post_modes:
            self.action_post_callback(post_mode, event)

    def on_scroll(self, event: PointerEvent, base_scale: float = 1.2) -> None:
        if (
            event.axes is None
            or event.xdata is None
            or event.ydata is None
            or not self._is_finite_pair(event.xdata, event.ydata)
            or event.step == 0
            or not isfinite(float(event.step))
        ):
            return
        if not isfinite(float(base_scale)) or base_scale <= 1.0:
            raise ValueError("scroll zoom base_scale must be greater than 1")
        self.set_active_axes(event.axes)
        limits = self.get_limits(event.axes)
        step_scale = base_scale ** abs(event.step)
        scale = 1 / step_scale if event.step > 0 else step_scale
        if self.zoom_direction == "out":
            scale = 1 / scale
        if self.is_3d_axes(event.axes) and self.zoom_3d_mode == "camera" and self._zoom_3d_camera(event.axes, scale):
            return
        new_limits = self._zoom_limits(limits, event.xdata, event.ydata, scale)
        self._set_user_limits(event.axes, self._apply_motion_to_limits(limits, new_limits, self.zoom_motion))
        self.push_current_view(event.axes)

    def on_point_zoom(self, axes: Any, x: float, y: float, scale: float) -> None:
        self._validate_zoom_scale(scale)
        if not self._is_finite_pair(x, y):
            return
        if scale == 1.0:
            return
        self.set_active_axes(axes)
        if self.is_3d_axes(axes) and self.zoom_3d_mode == "camera" and self._zoom_3d_camera(axes, scale):
            return
        limits = self.get_limits(axes)
        self._set_user_limits(axes, self._apply_motion_to_limits(limits, self._zoom_limits(limits, x, y, scale), self.zoom_motion))
        self.push_current_view(axes)

    def on_box_zoom(self, axes: Any, start: tuple[float, float], end: tuple[float, float]) -> None:
        self.set_active_axes(axes)
        if not self._is_finite_pair(start[0], start[1]) or not self._is_finite_pair(end[0], end[1]):
            return
        current = self.get_limits(axes)
        if not self._is_valid_zoom_box(current, start, end, self.zoom_motion):
            return
        limits = AxesLimits((start[0], end[0]), (start[1], end[1]), current.zlim, current.clim).normalized()
        limits = self._apply_motion_to_limits(current, limits, self.zoom_motion)
        self._set_user_limits(axes, limits)
        self.push_current_view(axes)

    def prepare_for_plot(self, axes: Any | None = None) -> None:
        """Apply MATLAB-like NextPlot behavior before adding plot children."""

        axes = axes if axes is not None else self.require_active_axes()
        state = self._current_axes_ui_state(axes)
        if state.next_plot == "add":
            return
        if state.next_plot == "replacechildren":
            self.clear_children(axes, reset_properties=False)
            return
        self.clear_children(axes, reset_properties=True)
        self.clear_view_history(axes)
        self.reset_axes_properties(axes)
        self._axes_ui_state[axes] = AxesUIState(
            color_order=self.DEFAULT_COLOR_ORDER,
            line_style_order=self.DEFAULT_LINE_STYLE_ORDER,
        )
        if axes is self.active_axes:
            self._load_axes_ui_state(axes)

    def after_plot(self, axes: Any | None = None) -> None:
        axes = axes if axes is not None else self.require_active_axes()
        state = self._current_axes_ui_state(axes)
        if state.xlim_mode == "auto" or state.ylim_mode == "auto" or state.zlim_mode == "auto":
            self.autoscale_axes(axes, tight=False)
        self.push_current_view(axes)

    def require_active_axes(self) -> Any:
        if self.active_axes is None:
            raise RuntimeError("No active axes is available")
        return self.active_axes

    def _restore_view(self, state: ViewState) -> None:
        axes = self.require_active_axes()
        self.set_limits(axes, state.limits)
        self.xlim_mode = state.xlim_mode
        self.ylim_mode = state.ylim_mode
        self.zlim_mode = state.zlim_mode
        self.clim_mode = state.clim_mode
        self.xtick = state.xtick
        self.ytick = state.ytick
        self.ztick = state.ztick
        self.xtick_mode = state.xtick_mode
        self.ytick_mode = state.ytick_mode
        self.ztick_mode = state.ztick_mode
        self.xticklabel = state.xticklabel
        self.yticklabel = state.yticklabel
        self.zticklabel = state.zticklabel
        self.xticklabel_mode = state.xticklabel_mode
        self.yticklabel_mode = state.yticklabel_mode
        self.zticklabel_mode = state.zticklabel_mode
        self.xticklabel_rotation = state.xticklabel_rotation
        self.yticklabel_rotation = state.yticklabel_rotation
        self.zticklabel_rotation = state.zticklabel_rotation
        self.xticklabel_rotation_mode = state.xticklabel_rotation_mode
        self.yticklabel_rotation_mode = state.yticklabel_rotation_mode
        self.zticklabel_rotation_mode = state.zticklabel_rotation_mode
        self.axes_title = state.axes_title
        self.xlabel_text = state.xlabel_text
        self.ylabel_text = state.ylabel_text
        self.zlabel_text = state.zlabel_text
        self.axis_aspect = state.aspect
        self.box_aspect = state.box_aspect
        self.data_aspect_ratio = state.data_aspect_ratio
        self.data_aspect_ratio_mode = state.data_aspect_ratio_mode
        self.plot_box_aspect_ratio = state.plot_box_aspect_ratio
        self.plot_box_aspect_ratio_mode = state.plot_box_aspect_ratio_mode
        self.axis_visible = state.axis_visible
        self.x_direction = state.x_direction
        self.y_direction = state.y_direction
        self.z_direction = state.z_direction
        self.x_scale = state.x_scale
        self.y_scale = state.y_scale
        self.z_scale = state.z_scale
        self.axis_layer = state.axis_layer
        self.tick_direction = state.tick_direction
        self.tick_direction_mode = state.tick_direction_mode
        self.tick_length = state.tick_length
        self.x_axis_location = state.x_axis_location
        self.y_axis_location = state.y_axis_location
        self.camera_mode = state.camera_mode
        self.camera_view_angle_mode = state.camera_view_angle_mode
        self.camera_position_mode = state.camera_position_mode
        self.camera_target_mode = state.camera_target_mode
        self.camera_up_vector_mode = state.camera_up_vector_mode
        self.camera_projection = state.camera_projection
        self.hold_enabled = state.hold_enabled
        self.next_plot = state.next_plot
        self.color_order = state.color_order or self.DEFAULT_COLOR_ORDER
        self.line_style_order = state.line_style_order or self.DEFAULT_LINE_STYLE_ORDER
        self.next_series_index = state.next_series_index
        self.set_aspect(axes, state.aspect)
        self.set_box_aspect(axes, state.box_aspect)
        self.set_data_aspect_ratio(axes, state.data_aspect_ratio)
        self.set_plot_box_aspect_ratio(axes, state.plot_box_aspect_ratio)
        self.set_axis_visible(axes, state.axis_visible)
        self._apply_grid_state(axes, state)
        self.set_box_visible(axes, state.box_visible)
        self.set_legend_visible(axes, state.legend_visible)
        self.set_x_direction(axes, state.x_direction)
        self.set_y_direction(axes, state.y_direction)
        self.set_z_direction(axes, state.z_direction)
        self.set_axis_scale(axes, "x", state.x_scale)
        self.set_axis_scale(axes, "y", state.y_scale)
        self.set_axis_scale(axes, "z", state.z_scale)
        self.set_axis_layer(axes, state.axis_layer)
        self.set_tick_direction(axes, state.tick_direction)
        self.set_tick_length(axes, state.tick_length)
        self.set_x_axis_location(axes, state.x_axis_location)
        self.set_y_axis_location(axes, state.y_axis_location)
        if state.xtick_mode == "manual":
            self.set_ticks(axes, "x", state.xtick)
        if state.ytick_mode == "manual":
            self.set_ticks(axes, "y", state.ytick)
        if state.ztick_mode == "manual":
            self.set_ticks(axes, "z", state.ztick)
        self.set_ticklabel_rotation(axes, "x", state.xticklabel_rotation)
        self.set_ticklabel_rotation(axes, "y", state.yticklabel_rotation)
        if self.is_3d_axes(axes):
            self.set_ticklabel_rotation(axes, "z", state.zticklabel_rotation)
        if state.xticklabel_mode == "manual":
            self.set_ticklabels(axes, "x", state.xticklabel)
        if state.yticklabel_mode == "manual":
            self.set_ticklabels(axes, "y", state.yticklabel)
        if state.zticklabel_mode == "manual":
            self.set_ticklabels(axes, "z", state.zticklabel)
        self.set_axes_text(axes, "title", state.axes_title)
        self.set_axes_text(axes, "xlabel", state.xlabel_text)
        self.set_axes_text(axes, "ylabel", state.ylabel_text)
        self.set_axes_text(axes, "zlabel", state.zlabel_text)
        if self.is_3d_axes(axes):
            self.set_camera_projection(axes, state.camera_projection)
        if state.camera is not None and self.is_3d_axes(axes):
            self.set_camera3d(axes, state.camera)
        self.sync_linked_axes(axes, state.limits)
        self._save_axes_ui_state(axes)

    def _set_user_limits(self, axes: Any, limits: AxesLimits) -> None:
        current = self.get_limits(axes)
        self.set_limits(axes, limits)
        if limits.xlim != current.xlim:
            self.xlim_mode = "manual"
        if limits.ylim != current.ylim:
            self.ylim_mode = "manual"
        if limits.zlim is not None and limits.zlim != current.zlim:
            self.zlim_mode = "manual"
        if limits.clim is not None and limits.clim != current.clim:
            self.clim_mode = "manual"
        self.sync_linked_axes(axes, limits)
        self._save_axes_ui_state(axes)

    def _apply_grid_state(self, axes: Any, state: AxesUIState | ViewState) -> None:
        self.set_axis_grid_visible(axes, "x", state.x_grid_visible, minor=False)
        self.set_axis_grid_visible(axes, "y", state.y_grid_visible, minor=False)
        self.set_axis_grid_visible(axes, "x", state.x_minor_grid_visible, minor=True)
        self.set_axis_grid_visible(axes, "y", state.y_minor_grid_visible, minor=True)
        self.set_axis_minor_tick_visible(axes, "x", state.x_minor_tick_visible)
        self.set_axis_minor_tick_visible(axes, "y", state.y_minor_tick_visible)
        if self.is_3d_axes(axes):
            self.set_axis_grid_visible(axes, "z", state.z_grid_visible, minor=False)
            self.set_axis_grid_visible(axes, "z", state.z_minor_grid_visible, minor=True)
            self.set_axis_minor_tick_visible(axes, "z", state.z_minor_tick_visible)

    def _apply_motion_to_limits(self, current: AxesLimits, requested: AxesLimits, motion: ToolMotion) -> AxesLimits:
        if motion == "horizontal":
            return AxesLimits(requested.xlim, current.ylim, current.zlim, current.clim)
        if motion == "vertical":
            return AxesLimits(current.xlim, requested.ylim, current.zlim, current.clim)
        return requested

    def _zoom_click_scale_for_direction(self) -> float:
        return self.zoom_click_scale if self.zoom_direction == "in" else self.zoom_right_click_scale

    def _active_action_modes(self) -> tuple[InteractionMode, ...]:
        modes: list[InteractionMode] = []
        if self._drag is not None:
            modes.append(InteractionMode.PAN)
        if self._zoom_drag is not None:
            modes.append(InteractionMode.ZOOM)
        if self._rotate_drag is not None:
            modes.append(InteractionMode.ROTATE3D)
        return tuple(modes)

    def _active_action_post_callbacks(self) -> tuple[tuple[InteractionMode, PointerEvent], ...]:
        callbacks: list[tuple[InteractionMode, PointerEvent]] = []
        if self._drag is not None:
            callbacks.append(
                (
                    InteractionMode.PAN,
                    PointerEvent(
                        axes=self._drag.axes,
                        xdata=self._drag.start_x,
                        ydata=self._drag.start_y,
                        button=MouseButton.LEFT,
                        modifiers=self._drag.modifiers,
                    ),
                )
            )
        if self._zoom_drag is not None:
            callbacks.append(
                (
                    InteractionMode.ZOOM,
                    PointerEvent(
                        axes=self._zoom_drag.axes,
                        x=self._zoom_drag.start_x,
                        y=self._zoom_drag.start_y,
                        xdata=self._zoom_drag.start_xdata,
                        ydata=self._zoom_drag.start_ydata,
                        button=MouseButton.LEFT,
                    ),
                )
            )
        if self._rotate_drag is not None:
            callbacks.append(
                (
                    InteractionMode.ROTATE3D,
                    PointerEvent(
                        axes=self._rotate_drag.axes,
                        x=self._rotate_drag.start_x,
                        y=self._rotate_drag.start_y,
                        button=MouseButton.LEFT,
                    ),
                )
            )
        return tuple(callbacks)

    def _zoom_limits(
        self,
        limits: AxesLimits,
        center_x: float,
        center_y: float,
        scale: float,
    ) -> AxesLimits:
        self._validate_zoom_scale(scale)
        if not self._is_finite_pair(center_x, center_y):
            raise ValueError("zoom center must be finite")
        x0, x1 = limits.xlim
        y0, y1 = limits.ylim
        new_x0, new_x1 = self._zoom_axis_limits((x0, x1), center_x, scale, self.x_scale)
        new_y0, new_y1 = self._zoom_axis_limits((y0, y1), center_y, scale, self.y_scale)
        return AxesLimits((new_x0, new_x1), (new_y0, new_y1), limits.zlim, limits.clim)

    def _pan_limits(self, limits: AxesLimits, start_x: float, start_y: float, dx: float, dy: float) -> AxesLimits:
        xlim = self._pan_axis_limits(limits.xlim, start_x, dx, self.x_scale)
        ylim = self._pan_axis_limits(limits.ylim, start_y, dy, self.y_scale)
        return AxesLimits(xlim, ylim, limits.zlim, limits.clim)

    def _pan_shift_constraint_is_horizontal(self, drag: _DragState, event: PointerEvent, dx: float, dy: float) -> bool:
        if (
            drag.start_screen_x is not None
            and drag.start_screen_y is not None
            and event.x is not None
            and event.y is not None
            and self._is_finite_pair(drag.start_screen_x, drag.start_screen_y)
            and self._is_finite_pair(event.x, event.y)
        ):
            return abs(event.x - drag.start_screen_x) >= abs(event.y - drag.start_screen_y)
        return abs(dx) >= abs(dy)

    def _pan_axis_limits(self, limits: tuple[float, float], start: float, delta: float, scale: AxisScale) -> tuple[float, float]:
        low, high = limits
        if scale == "log" and self._can_use_log_axis(limits, start, start + delta):
            log_low, log_high, log_start, log_end = (self._log10(value) for value in (low, high, start, start + delta))
            log_delta = log_end - log_start
            return (10 ** (log_low - log_delta), 10 ** (log_high - log_delta))
        return (low - delta, high - delta)

    def _zoom_axis_limits(self, limits: tuple[float, float], center: float, scale: float, axis_scale: AxisScale) -> tuple[float, float]:
        low, high = limits
        if axis_scale == "log" and self._can_use_log_axis(limits, center):
            log_low, log_high, log_center = (self._log10(value) for value in (low, high, center))
            return (
                10 ** (log_center - (log_center - log_low) * scale),
                10 ** (log_center + (log_high - log_center) * scale),
            )
        return (center - (center - low) * scale, center + (high - center) * scale)

    def _can_use_log_axis(self, limits: tuple[float, float], *values: float) -> bool:
        return all(isfinite(float(value)) and value > 0.0 for value in (*limits, *values))

    def _log10(self, value: float) -> float:
        from math import log10

        return log10(value)

    def _validate_zoom_scale(self, scale: float) -> None:
        if not isfinite(float(scale)) or scale <= 0.0:
            raise ValueError("zoom scale must be finite and greater than 0")

    def _is_zoom_click(self, drag: _ZoomDragState, event: PointerEvent) -> bool:
        if drag.start_x is not None and drag.start_y is not None and event.x is not None and event.y is not None:
            dx = event.x - drag.start_x
            dy = event.y - drag.start_y
            return (dx * dx + dy * dy) ** 0.5 < self.zoom_drag_pixel_threshold
        if event.xdata is None or event.ydata is None:
            return False
        return event.xdata == drag.start_xdata and event.ydata == drag.start_ydata

    def _view_changed_since(self, axes: Any, start_view: ViewState | None) -> bool:
        current = self.current_view_state(axes)
        return current is not None and current != start_view

    def _is_valid_zoom_box(self, current: AxesLimits, start: tuple[float, float], end: tuple[float, float], motion: ToolMotion = "both") -> bool:
        x_applies = motion in {"both", "horizontal"}
        y_applies = motion in {"both", "vertical"}
        x_valid = True if not x_applies else self._is_valid_zoom_box_axis(current.xlim, start[0], end[0], self.x_scale)
        y_valid = True if not y_applies else self._is_valid_zoom_box_axis(current.ylim, start[1], end[1], self.y_scale)
        return x_valid and y_valid

    def _is_valid_zoom_box_axis(self, current: tuple[float, float], start: float, end: float, scale: AxisScale) -> bool:
        if scale == "log":
            if not self._can_use_log_axis(current, start, end):
                return False
            current_low, current_high, start_log, end_log = (self._log10(value) for value in (*current, start, end))
            current_span = abs(current_high - current_low)
            requested_span = abs(end_log - start_log)
        else:
            current_span = abs(current[1] - current[0])
            requested_span = abs(end - start)
        return requested_span > max(current_span * self.zoom_box_min_span_ratio, 0.0)

    def _rotate_camera(self, camera: Camera3DState, dx: float, dy: float) -> Camera3DState:
        self._validate_camera_finite(camera)
        if not self._is_finite_pair(dx, dy):
            raise ValueError("rotate deltas must be finite")
        if self.rotate_motion == "horizontal":
            dy = 0.0
        elif self.rotate_motion == "vertical":
            dx = 0.0
        min_elev, max_elev = self.elevation_limits
        elev = max(min_elev, min(max_elev, camera.elev - dy * self.rotate_elevation_sensitivity))
        azim = self._normalize_azimuth(camera.azim - dx * self.rotate_azimuth_sensitivity)
        return Camera3DState(
            azim=azim,
            elev=elev,
            roll=camera.roll,
            view_angle=camera.view_angle,
            position=camera.position,
            target=camera.target,
            up_vector=camera.up_vector,
        )

    def _normalize_azimuth(self, azim: float) -> float:
        return ((azim + 180.0) % 360.0) - 180.0

    def _normalized_camera(self, camera: Camera3DState) -> Camera3DState:
        return Camera3DState(
            azim=self._normalize_azimuth(camera.azim),
            elev=camera.elev,
            roll=camera.roll,
            view_angle=camera.view_angle,
            position=camera.position,
            target=camera.target,
            up_vector=camera.up_vector,
        )

    def _with_current_view_angle(self, camera: Camera3DState, current_camera: Camera3DState) -> Camera3DState:
        return Camera3DState(
            camera.azim,
            camera.elev,
            camera.roll,
            current_camera.view_angle,
            current_camera.position,
            current_camera.target,
            current_camera.up_vector,
        )

    def _current_camera_snapshot(self, axes: Any) -> Camera3DState | None:
        if not self.is_3d_axes(axes):
            return None
        camera = self.get_camera3d(axes)
        try:
            self._validate_camera_finite(camera)
        except ValueError:
            return None
        return self._normalized_camera(camera)

    def _validate_camera_finite(self, camera: Camera3DState) -> None:
        if not (isfinite(camera.azim) and isfinite(camera.elev) and isfinite(camera.roll)):
            raise ValueError("camera angles must be finite")
        if camera.view_angle is not None and not isfinite(camera.view_angle):
            raise ValueError("camera view angle must be finite")
        for name, vector in (
            ("camera position", camera.position),
            ("camera target", camera.target),
            ("camera up vector", camera.up_vector),
        ):
            if vector is not None and (len(vector) != 3 or not all(isfinite(float(item)) for item in vector)):
                raise ValueError(f"{name} must be a finite 3-element vector")

    def _is_finite_pair(self, x: float, y: float) -> bool:
        return isfinite(float(x)) and isfinite(float(y))

    @property
    def rotate_azimuth_sensitivity(self) -> float:
        return self._rotate_azimuth_sensitivity

    @property
    def pan_motion(self) -> ToolMotion:
        return self._pan_motion

    @pan_motion.setter
    def pan_motion(self, value: ToolMotion | str) -> None:
        self._pan_motion = self._validate_tool_motion(value, "pan motion")

    @property
    def pan_3d_mode(self) -> Pan3DMode:
        return self._pan_3d_mode

    @pan_3d_mode.setter
    def pan_3d_mode(self, value: Pan3DMode | str) -> None:
        normalized = value.strip().lower()
        if normalized not in {"camera", "limits"}:
            raise ValueError(f"Unsupported 3D pan mode: {value!r}")
        self._pan_3d_mode = normalized

    @property
    def zoom_motion(self) -> ToolMotion:
        return self._zoom_motion

    @zoom_motion.setter
    def zoom_motion(self, value: ToolMotion | str) -> None:
        self._zoom_motion = self._validate_tool_motion(value, "zoom motion")

    @property
    def rotate_motion(self) -> ToolMotion:
        return self._rotate_motion

    @rotate_motion.setter
    def rotate_motion(self, value: ToolMotion | str) -> None:
        self._rotate_motion = self._validate_tool_motion(value, "rotate motion")

    @property
    def zoom_3d_mode(self) -> Zoom3DMode:
        return self._zoom_3d_mode

    @zoom_3d_mode.setter
    def zoom_3d_mode(self, value: Zoom3DMode | str) -> None:
        normalized = value.strip().lower()
        if normalized not in {"camera", "limits"}:
            raise ValueError(f"Unsupported 3D zoom mode: {value!r}")
        self._zoom_3d_mode = normalized

    @property
    def zoom_direction(self) -> ZoomDirection:
        return self._zoom_direction

    @zoom_direction.setter
    def zoom_direction(self, value: ZoomDirection | str) -> None:
        normalized = value.strip().lower()
        if normalized not in {"in", "out"}:
            raise ValueError(f"Unsupported zoom direction: {value!r}")
        self._zoom_direction = normalized

    @property
    def zoom_right_click_action(self) -> ZoomRightClickAction:
        return self._zoom_right_click_action

    @zoom_right_click_action.setter
    def zoom_right_click_action(self, value: ZoomRightClickAction | str) -> None:
        normalized = value.strip().lower()
        if normalized not in {"postcontextmenu", "inversezoom"}:
            raise ValueError(f"Unsupported zoom right-click action: {value!r}")
        self._zoom_right_click_action = normalized

    @property
    def use_legacy_exploration_modes(self) -> Literal["off"]:
        return "off"

    @property
    def rotate_style(self) -> RotateStyle:
        return self._rotate_style

    @rotate_style.setter
    def rotate_style(self, value: RotateStyle | str) -> None:
        normalized = value.strip().lower()
        if normalized not in {"orbit", "box"}:
            raise ValueError(f"Unsupported rotate style: {value!r}")
        self._rotate_style = normalized

    @rotate_azimuth_sensitivity.setter
    def rotate_azimuth_sensitivity(self, value: float) -> None:
        self._rotate_azimuth_sensitivity = self._validate_nonnegative_float(value, "rotate azimuth sensitivity")

    @property
    def rotate_elevation_sensitivity(self) -> float:
        return self._rotate_elevation_sensitivity

    @rotate_elevation_sensitivity.setter
    def rotate_elevation_sensitivity(self, value: float) -> None:
        self._rotate_elevation_sensitivity = self._validate_nonnegative_float(value, "rotate elevation sensitivity")

    @property
    def rotate_drag_pixel_threshold(self) -> float:
        return self._rotate_drag_pixel_threshold

    @rotate_drag_pixel_threshold.setter
    def rotate_drag_pixel_threshold(self, value: float) -> None:
        self._rotate_drag_pixel_threshold = self._validate_nonnegative_float(value, "rotate drag pixel threshold")

    @property
    def elevation_limits(self) -> tuple[float, float]:
        return self._elevation_limits

    @elevation_limits.setter
    def elevation_limits(self, value: Sequence[float]) -> None:
        limits = tuple(float(item) for item in value)
        if len(limits) != 2:
            raise ValueError("elevation limits must contain 2 values")
        if not all(isfinite(limit) for limit in limits):
            raise ValueError("elevation limits must be finite")
        if limits[0] > limits[1]:
            raise ValueError("elevation limits must be in ascending order")
        self._elevation_limits = limits

    @property
    def rotate_sensitivity(self) -> float:
        """Compatibility scalar for callers that tune rotation as one value."""

        return self.rotate_azimuth_sensitivity

    @rotate_sensitivity.setter
    def rotate_sensitivity(self, value: float) -> None:
        sensitivity = self._validate_nonnegative_float(value, "rotate sensitivity")
        self.rotate_azimuth_sensitivity = sensitivity
        self.rotate_elevation_sensitivity = sensitivity

    def _validate_nonnegative_float(self, value: float, name: str) -> float:
        result = float(value)
        if not isfinite(result):
            raise ValueError(f"{name} must be finite")
        if result < 0.0:
            raise ValueError(f"{name} must be non-negative")
        return result

    def _validate_tool_motion(self, value: ToolMotion | str, name: str) -> ToolMotion:
        normalized = value.strip().lower()
        if normalized not in {"both", "horizontal", "vertical"}:
            raise ValueError(f"Unsupported {name}: {value!r}")
        return normalized

    def sync_linked_axes(self, source_axes: Any, source_limits: AxesLimits) -> None:
        for axes_set, axis in self._linked:
            if source_axes not in axes_set:
                continue
            for axes in axes_set:
                if axes is source_axes:
                    continue
                current = self.get_limits(axes)
                xlim = source_limits.xlim if "x" in axis else current.xlim
                ylim = source_limits.ylim if "y" in axis else current.ylim
                self.set_limits(axes, AxesLimits(xlim, ylim, current.zlim, current.clim))
                self._mark_linked_axes_modes_manual(axes, axis)

    def _mark_linked_axes_modes_manual(self, axes: Any, axis: Literal["x", "y", "xy"]) -> None:
        state = self._current_axes_ui_state(axes)
        if "x" in axis:
            state.xlim_mode = "manual"
        if "y" in axis:
            state.ylim_mode = "manual"
        self._axes_ui_state[axes] = state
        if axes is self.active_axes:
            self._load_axes_ui_state(axes)

    def on_active_axes_changed(self, axes: Any | None) -> None:
        """Hook for UI integrations."""

    def on_mode_changed(self, mode: InteractionMode) -> None:
        """Hook for UI integrations."""

    def on_hold_changed(self, enabled: bool) -> None:
        """Hook for UI integrations that expose hold state."""

    def on_view_history_changed(self) -> None:
        """Hook for UI integrations that update history toolbar state."""

    def button_down_filter(self, event: PointerEvent) -> bool:
        """Return True to block pan/zoom/rotate handling for this press."""

        return False

    def action_pre_callback(self, mode: InteractionMode, event: PointerEvent) -> None:
        """Hook called when a pan/zoom/rotate action starts."""

    def action_post_callback(self, mode: InteractionMode, event: PointerEvent) -> None:
        """Hook called when a pan/zoom/rotate action ends."""

    def update_coordinate_readout(self, axes: Any, x: float, y: float) -> None:
        """Hook for status bar or crosshair integrations."""

    def create_data_tip(self, axes: Any, x: float, y: float) -> None:
        """Hook for data cursor integrations."""

    def select_nearest_artist(
        self,
        axes: Any,
        x: float,
        y: float,
        modifiers: frozenset[str],
    ) -> None:
        """Hook for object selection integrations."""

    def brush_box(
        self,
        axes: Any,
        start: tuple[float, float],
        end: tuple[float, float],
        modifiers: frozenset[str],
    ) -> None:
        """Hook for MATLAB-like brush rectangle integrations."""

    def begin_zoom_box(self, axes: Any, x: float, y: float) -> None:
        """Hook for rubber-band zoom-box visualization."""

    def update_zoom_box(self, axes: Any, x0: float, y0: float, x1: float, y1: float) -> None:
        """Hook for rubber-band zoom-box visualization."""

    def end_zoom_box(self) -> None:
        """Hook for clearing rubber-band zoom-box visualization."""

    def begin_brush_box(self, axes: Any, x: float, y: float) -> None:
        """Hook for rubber-band brush-box visualization."""

    def update_brush_box(self, axes: Any, x0: float, y0: float, x1: float, y1: float) -> None:
        """Hook for rubber-band brush-box visualization."""

    def end_brush_box(self) -> None:
        """Hook for clearing rubber-band brush-box visualization."""

    def draw_plot_series(self, axes: Any, series: Sequence[PlotSeries]) -> list[Any]:
        """Draw normalized line series for the concrete backend."""

        raise NotImplementedError

    def draw_plot3_series(self, axes: Any, series: Sequence[Plot3Series]) -> list[Any]:
        """Draw normalized 3D line series for the concrete backend."""

        raise NotImplementedError

    def draw_errorbar_series(self, axes: Any, series: Sequence[ErrorBarSeries]) -> list[Any]:
        """Draw normalized error-bar series for the concrete backend."""

        raise NotImplementedError

    def draw_scatter_series(self, axes: Any, series: Sequence[ScatterSeries]) -> list[Any]:
        """Draw normalized scatter series for the concrete backend."""

        raise NotImplementedError

    def draw_stem_series(self, axes: Any, series: Sequence[StemSeries]) -> list[Any]:
        """Draw normalized stem series for the concrete backend."""

        raise NotImplementedError

    def draw_bar_series(self, axes: Any, series: Sequence[BarSeries]) -> list[Any]:
        """Draw normalized vertical bar series for the concrete backend."""

        raise NotImplementedError

    def draw_area_series(self, axes: Any, series: Sequence[AreaSeries]) -> list[Any]:
        """Draw normalized stacked area series for the concrete backend."""

        raise NotImplementedError

    def is_axes_handle(self, value: Any) -> bool:
        """Return whether ``value`` is a concrete backend axes object."""

        return False

    def clear_children(self, axes: Any, reset_properties: bool) -> None:
        """Clear plot children for the concrete backend."""

        raise NotImplementedError

    def reset_axes_properties(self, axes: Any) -> None:
        """Reset backend axes properties for MATLAB-like NextPlot='replace'."""

    def get_limits(self, axes: Any) -> AxesLimits:
        """Return current axes limits for the concrete backend."""

        raise NotImplementedError

    def set_limits(self, axes: Any, limits: AxesLimits) -> None:
        """Set current axes limits for the concrete backend."""

        raise NotImplementedError

    def autoscale_axes(self, axes: Any, tight: bool = False) -> None:
        """Autoscale one axes for the concrete backend."""

        raise NotImplementedError

    def autoscale_clim(self, axes: Any) -> None:
        """Autoscale color limits for the concrete backend."""

        raise NotImplementedError

    def autoscale_active_axes(self, tight: bool = False) -> None:
        self.autoscale_axes(self.require_active_axes(), tight=tight)

    def is_3d_axes(self, axes: Any) -> bool:
        """Return whether the concrete backend axes supports 3D camera control."""

        return False

    def get_camera3d(self, axes: Any) -> Camera3DState:
        """Return current 3D camera state for the concrete backend."""

        raise NotImplementedError

    def set_camera3d(self, axes: Any, camera: Camera3DState) -> None:
        """Set current 3D camera state for the concrete backend."""

        raise NotImplementedError

    def get_camera_projection(self, axes: Any) -> CameraProjection:
        """Return current 3D projection mode for the concrete backend."""

        return getattr(axes, "camera_projection", "orthographic")

    def set_camera_projection(self, axes: Any, projection: CameraProjection) -> None:
        """Set current 3D projection mode for the concrete backend."""

        setattr(axes, "camera_projection", projection)

    def set_aspect(self, axes: Any, aspect: AspectMode) -> None:
        """Set data aspect ratio for the concrete backend."""

        raise NotImplementedError

    def set_box_aspect(self, axes: Any, box_aspect: BoxAspectMode) -> None:
        """Set plot-box aspect ratio for the concrete backend."""

        raise NotImplementedError

    def set_data_aspect_ratio(self, axes: Any, ratio: tuple[float, float, float]) -> None:
        """Set explicit data aspect ratio for the concrete backend."""

        setattr(axes, "data_aspect_ratio", ratio)

    def set_plot_box_aspect_ratio(self, axes: Any, ratio: tuple[float, float, float]) -> None:
        """Set explicit plot-box aspect ratio for the concrete backend."""

        setattr(axes, "plot_box_aspect_ratio", ratio)

    def set_axis_visible(self, axes: Any, visible: bool) -> None:
        """Show or hide axes decorations for the concrete backend."""

        raise NotImplementedError

    def set_x_direction(self, axes: Any, direction: AxisDirection) -> None:
        """Set x-axis direction for the concrete backend."""

        setattr(axes, "x_direction", direction)

    def set_y_direction(self, axes: Any, direction: AxisDirection) -> None:
        """Set y-axis direction for the concrete backend."""

        raise NotImplementedError

    def set_z_direction(self, axes: Any, direction: AxisDirection) -> None:
        """Set z-axis direction for the concrete backend."""

        setattr(axes, "z_direction", direction)

    def set_axis_scale(self, axes: Any, axis: Literal["x", "y", "z"], scale: AxisScale) -> None:
        """Set axis scale for the concrete backend."""

        setattr(axes, f"{axis}_scale", scale)

    def set_axis_layer(self, axes: Any, layer: AxisLayer) -> None:
        """Set axes layer ordering for the concrete backend."""

        setattr(axes, "axis_layer", layer)

    def set_tick_direction(self, axes: Any, direction: TickDirection) -> None:
        """Set tick direction for the concrete backend."""

        setattr(axes, "tick_direction", direction)

    def set_tick_length(self, axes: Any, tick_length: tuple[float, float]) -> None:
        """Set tick length for the concrete backend."""

        setattr(axes, "tick_length", tick_length)

    def set_x_axis_location(self, axes: Any, location: XAxisLocation) -> None:
        """Set x-axis location for the concrete backend."""

        setattr(axes, "x_axis_location", location)

    def set_y_axis_location(self, axes: Any, location: YAxisLocation) -> None:
        """Set y-axis location for the concrete backend."""

        setattr(axes, "y_axis_location", location)

    def get_ticks(self, axes: Any, axis: Literal["x", "y", "z"]) -> tuple[float, ...]:
        """Return tick locations for the concrete backend."""

        return tuple(getattr(axes, f"{axis}tick", ()))

    def set_ticks(self, axes: Any, axis: Literal["x", "y", "z"], ticks: tuple[float, ...]) -> None:
        """Set tick locations for the concrete backend."""

        setattr(axes, f"{axis}tick", ticks)

    def get_ticklabels(self, axes: Any, axis: Literal["x", "y", "z"]) -> tuple[str, ...]:
        """Return tick labels for the concrete backend."""

        return tuple(str(item) for item in getattr(axes, f"{axis}ticklabel", ()))

    def set_ticklabels(self, axes: Any, axis: Literal["x", "y", "z"], labels: tuple[str, ...]) -> None:
        """Set tick labels for the concrete backend."""

        setattr(axes, f"{axis}ticklabel", labels)

    def set_ticklabel_rotation(self, axes: Any, axis: Literal["x", "y", "z"], rotation: float) -> None:
        """Set tick-label rotation for the concrete backend."""

        setattr(axes, f"{axis}ticklabel_rotation", rotation)

    def get_axes_text(self, axes: Any, kind: Literal["title", "xlabel", "ylabel", "zlabel"]) -> tuple[str, ...]:
        """Return title or axis-label text for the concrete backend."""

        return tuple(str(item) for item in getattr(axes, self._text_state_attr(kind), ()))

    def set_axes_text(self, axes: Any, kind: Literal["title", "xlabel", "ylabel", "zlabel"], text: tuple[str, ...]) -> None:
        """Set title or axis-label text for the concrete backend."""

        setattr(axes, self._text_state_attr(kind), text)

    def grid_is_enabled(self, axes: Any) -> bool:
        """Return whether grid lines are visible for the concrete backend."""

        axis_values = [self.axis_grid_is_enabled(axes, "x", minor=False), self.axis_grid_is_enabled(axes, "y", minor=False)]
        if self.is_3d_axes(axes):
            axis_values.append(self.axis_grid_is_enabled(axes, "z", minor=False))
        return all(axis_values)

    def set_grid_visible(self, axes: Any, visible: bool) -> None:
        """Set grid visibility for the concrete backend."""

        for axis in self._grid_axes_for(axes):
            self.set_axis_grid_visible(axes, axis, visible, minor=False)

    def minor_grid_is_enabled(self, axes: Any) -> bool:
        """Return whether minor grid lines are visible for the concrete backend."""

        axis_values = [self.axis_grid_is_enabled(axes, "x", minor=True), self.axis_grid_is_enabled(axes, "y", minor=True)]
        if self.is_3d_axes(axes):
            axis_values.append(self.axis_grid_is_enabled(axes, "z", minor=True))
        return all(axis_values)

    def set_minor_grid_visible(self, axes: Any, visible: bool) -> None:
        """Set minor grid visibility for the concrete backend."""

        for axis in self._grid_axes_for(axes):
            self.set_axis_grid_visible(axes, axis, visible, minor=True)

    def axis_grid_is_enabled(self, axes: Any, axis: Literal["x", "y", "z"], *, minor: bool = False) -> bool:
        """Return whether one axis grid is visible for the concrete backend."""

        attr = f"{axis}_{'minor_' if minor else ''}grid_visible"
        if hasattr(axes, attr):
            return bool(getattr(axes, attr))
        fallback = "minor_grid_visible" if minor else "grid_visible"
        return bool(getattr(axes, fallback, False))

    def set_axis_grid_visible(self, axes: Any, axis: Literal["x", "y", "z"], visible: bool, *, minor: bool = False) -> None:
        """Set one axis grid visibility for the concrete backend."""

        attr = f"{axis}_{'minor_' if minor else ''}grid_visible"
        setattr(axes, attr, visible)
        aggregate_attr = "minor_grid_visible" if minor else "grid_visible"
        axis_values = [bool(getattr(axes, f"{item}_{'minor_' if minor else ''}grid_visible", False)) for item in self._grid_axes_for(axes)]
        setattr(axes, aggregate_attr, all(axis_values))

    def axis_minor_tick_is_enabled(self, axes: Any, axis: Literal["x", "y", "z"]) -> bool:
        """Return whether one axis minor ticks are visible for the concrete backend."""

        return bool(getattr(axes, f"{axis}_minor_tick_visible", False))

    def set_axis_minor_tick_visible(self, axes: Any, axis: Literal["x", "y", "z"], visible: bool) -> None:
        """Set one axis minor tick visibility for the concrete backend."""

        setattr(axes, f"{axis}_minor_tick_visible", visible)

    def _grid_axes_for(self, axes: Any) -> tuple[Literal["x", "y", "z"], ...]:
        if self.is_3d_axes(axes):
            return ("x", "y", "z")
        return ("x", "y")

    def box_is_enabled(self, axes: Any) -> bool:
        """Return whether the axes box is visible for the concrete backend."""

        return False

    def set_box_visible(self, axes: Any, visible: bool) -> None:
        """Set axes box visibility for the concrete backend."""

        raise NotImplementedError

    def legend_is_enabled(self, axes: Any) -> bool:
        """Return whether a legend is visible for the concrete backend."""

        return False

    def set_legend_visible(self, axes: Any, visible: bool) -> bool:
        """Set legend visibility for the concrete backend."""

        return False
