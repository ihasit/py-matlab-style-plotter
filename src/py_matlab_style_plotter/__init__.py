"""MATLAB-like plotter primitives."""

from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
import tomllib


def _source_tree_version() -> str | None:
    pyproject = Path(__file__).resolve().parents[2] / "pyproject.toml"
    if not pyproject.exists():
        return None
    try:
        data = tomllib.loads(pyproject.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError):
        return None
    return _version_from_pyproject_data(data)


def _version_from_pyproject_data(data: dict) -> str | None:
    project = data.get("project")
    if not isinstance(project, dict):
        return None
    if project.get("name") != "py-matlab-style-plotter":
        return None
    value = project.get("version")
    return str(value) if value else None


try:
    __version__ = _source_tree_version() or version("py-matlab-style-plotter")
except PackageNotFoundError:
    __version__ = "0+unknown"

from .interaction import (
    AreaSeries,
    AxisDirection,
    AxisScale,
    AspectRatioMode,
    AspectMode,
    AxesLimits,
    BoxAspectMode,
    AxisLayer,
    BarSeries,
    Camera3DState,
    CameraMode,
    CameraProjection,
    CameraVectorMode,
    CameraViewAngleMode,
    ConstantLineSeries,
    ContourSeries,
    ErrorBarSeries,
    FillSeries,
    HistogramSeries,
    ImageSeries,
    InteractionMode,
    LinkAxesAxis,
    MatlabLikeAxesBase,
    MouseButton,
    NextPlotMode,
    Pan3DMode,
    PColorSeries,
    QuiverSeries,
    Plot3Series,
    PlotSeries,
    PointerEvent,
    RotateStyle,
    AnnotationSeries,
    RoseSeries,
    HeatmapSeries,
    ParetoSeries,
    PieSeries,
    PolarHistogramSeries,
    PolarSeries,
    SpySeries,
    Scatter3Series,
    ScatterSeries,
    SurfaceSeries,
    Stem3Series,
    StemSeries,
    TextSeries,
    TickDirection,
    ToolMotion,
    ToolState,
    View3DPreset,
    ViewState,
    XAxisLocation,
    YAxisLocation,
    ZoomDirection,
    Zoom3DMode,
    ZoomRightClickAction,
)
from .matplotlib_adapter import (
    ActiveAxesStyle,
    BrushedPointsState,
    CoordinateReadout,
    DataTip,
    MatplotlibAxesPlotter,
    SelectedDataTipState,
    SelectedLineState,
    SpineStyle,
)
from .matplotlib_bridge import MatplotlibEventBridge
from .matplotlib_context_menu import (
    MatplotlibContextMenu,
    MatplotlibContextMenuActions,
    MatplotlibContextMenuEventBridge,
)

__all__ = [
    "__version__",
    "InteractionMode",
    "MouseButton",
    "PointerEvent",
    "ToolState",
    "ToolMotion",
    "RotateStyle",
    "View3DPreset",
    "ZoomDirection",
    "Zoom3DMode",
    "ZoomRightClickAction",
    "MatplotlibAxesPlotter",
    "MatplotlibEventBridge",
    "MatplotlibContextMenu",
    "MatplotlibContextMenuActions",
    "MatplotlibContextMenuEventBridge",
]
