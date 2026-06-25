# pyMatlabStylePlotter

MATLAB-like plotting and axes interaction helpers for Python UI applications.

The first iteration focuses on axes UI behavior rather than drawing syntax:

- active axes tracking
- active axes queries with `current_axes()`, MATLAB-style `gca()`, and `is_active_axes(axes)`
- per-axes UI state for limit modes, aspect, box aspect, axis visibility, and y direction when switching active axes
- exclusive interaction modes: `none`, `pan`, `zoom`, `data_cursor`, `select`, `brush`
- MATLAB-style tool mode helpers: `pan`, `zoom`, `rotate3d`, `datacursormode`, `selectmode`, and `brush` accept `on`, `off`, `toggle`, or booleans
- MATLAB-style `grid on/off/toggle/minor` helper for axes major/minor grid visibility
- MATLAB-style `box on/off/toggle` helper for axes frame visibility
- MATLAB-style `legend on/off/toggle` helper for axes legends
- MATLAB-style `colorbar on/off/toggle` helper for axes colorbars
- mode state queries with `active_mode()` and `is_mode_active(mode)` for toolbar highlighting
- MATLAB-like exploration tool state snapshots with `tool_state(mode)`, `pan_state()`, `zoom_state()`, and `rotate3d_state()` exposing `Enable`-style on/off state plus tool properties
- MATLAB-style per-axes `hold on/off`
- MATLAB-style hold-state queries with `ishold()` or `ishold(axes)`
- MATLAB-style `NextPlot` lifecycle and public `newplot(...)` helper: `replace` clears axes, resets axes UI/backend properties, and starts a fresh view history, while `add` preserves existing plots and view history
- MATLAB-style `cla` / `cla reset` helpers for clearing axes children with optional axes property and view-history reset
- MATLAB-style base `plot(...)` command template with `plot(y)`, `plot(x, y)`, `plot(ax, ...)`, matrix columns, repeated `x, y, LineSpec` groups, MATLAB Name/Value properties, Python keyword properties, and backend-neutral `NextPlot` / `hold` / autoscale lifecycle handling
- MATLAB-style `line(...)` primitive helper for adding 2D/3D line objects without `NextPlot` clearing or default series-order assignment
- MATLAB-style `plot3(...)` command template with repeated `x, y, z, LineSpec` groups and the same backend-neutral series-order and `NextPlot` lifecycle handling as `plot(...)`
- MATLAB-style `stairs(...)` command template that expands stairstep x/y points while reusing `plot(...)` parsing, styling, series-order, and lifecycle behavior
- MATLAB-style vertical `errorbar(...)` command template for `y/e`, `x/y/e`, and `x/y/negative/positive` forms with shared styling and lifecycle behavior
- MATLAB-style `scatter(...)` command template for `x/y`, optional marker size, optional color, matrix-column expansion, and shared styling/lifecycle behavior
- MATLAB-style `stem(...)` command template for discrete sequence plots with shared `plot(...)` parsing, LineSpec, series-order, and lifecycle behavior
- MATLAB-style `bar(...)` command template for vertical bar plots with shared `plot(...)` parsing, LineSpec, series-order, and lifecycle behavior
- MATLAB-style `area(...)` command template for stacked area plots with shared `plot(...)` parsing, LineSpec, series-order, and lifecycle behavior
- MATLAB-style `fill(...)` command template for filled polygons with explicit color groups, default `ColorOrder`, and shared lifecycle behavior
- MATLAB-style `histogram(...)` command template for data histograms with optional bin count or explicit bin edges and shared lifecycle behavior
- MATLAB-style `xline(...)` and `yline(...)` constant reference-line helpers with LineSpec, labels, positional axes, and primitive-style lifecycle behavior
- MATLAB-style `text(...)` annotation helper for 2D/3D axes text with positional axes, Name/Value properties, and primitive-style lifecycle behavior
- MATLAB-style `imagesc(...)` command template for scaled image CData with optional x/y endpoints, color-limit autoscaling, and shared plot lifecycle behavior
- MATLAB-style `colormap(...)` helper for querying or setting per-axes named colormaps or N-by-3 RGB colormap matrices
- MATLAB-style `contour(...)` command template for contour plots with Z matrix, optional X/Y coordinates, optional level count or level vector, and shared plot lifecycle behavior
- MATLAB-style `subtitle(...)` helper
- MATLAB-style `sgtitle(...)` helper
- MATLAB-style `yyaxis("left"|"right")` helper for dual y-axis plots with per-axes left/right side tracking for subplot group titles, stored per-axes in view history for secondary axes descriptions, stored per-axes in view history
- MATLAB-style `subplot(m, n, p)` and `subplot(mnp)` helpers for creating and selecting axes in a figure grid layout, with cached reuse of existing subplot axes
- MATLAB-style `contourf(...)` command template for filled contour plots sharing `contour(...)` arg normalization and lifecycle behavior
- MATLAB-style `contour3(...)` command template for 3D contour projections sharing `contour(...)` arg normalization and rendering
- MATLAB-style `surf(...)` and `mesh(...)` command templates for 3D surface and wireframe plots with Z matrix, optional X/Y coordinates, optional color data, and shared plot lifecycle behavior
- MATLAB-style `waterfall(...)` command template for waterfall plots sharing `surf(...)` arg normalization and mesh rendering
- MATLAB-style `ribbon(...)` command template for ribbon plots sharing `surf(...)` arg normalization and mesh rendering
- MATLAB-style `quiver(...)` command template for vector field plots with U/V components, optional X/Y positions, and shared plot lifecycle behavior
- MATLAB-style `pcolor(...)` command template for pseudocolor checkerboard plots with CData, optional X/Y coordinates, and shared plot lifecycle behavior
- MATLAB-style `spy(...)` command template for visualizing matrix sparsity patterns with shared plot lifecycle behavior
- MATLAB-style `annotation(type, ...)` helpers for figure-level annotations including `line`, `arrow`, `textarrow`, `textbox`, `ellipse`, and `rectangle`
- MATLAB-like `delete(handle)` helper for removing graphics handles, cleaning up active-axes state, subplot cache, and view history
- MATLAB-like `copyobj(handle, parent)` helper for copying graphics handles to a target axes
- MATLAB-like `set(handle, name, value)` and `get(handle, name)` helpers for querying and setting properties on graphics handles
- MATLAB-like `findobj(handle, name, value)` helper for recursively searching graphics handles by property
- MATLAB-like `drawnow()` helper for flushing pending graphics updates
- MATLAB-style `semilogx(...)`, `semilogy(...)`, and `loglog(...)` wrappers that reuse the base `plot(...)` lifecycle and set x/y axis scales
- MATLAB-style default `ColorOrder`, `LineStyleOrder`, and per-axes `NextSeriesIndex` handling for plotted lines, with `replace` resetting the cycle and `hold on` continuing it
- MATLAB-style `colororder(...)`, `linestyleorder(...)`, and `nextseriesindex(...)` helpers for querying and setting per-axes series-order state
- Matplotlib `replace` / `replacechildren` plot lifecycles clear stale data tips, selections, coordinate readouts, and temporary zoom/brush boxes for the target axes
- hold state notifications with `on_hold_changed(enabled)`
- explicit `auto` / `manual` x/y limit modes
- MATLAB-style `axis auto/manual/tight/equal/fill/image/normal/square/vis3d/on/off/ij/xy` view controls; `axis auto/manual/tight/image` update coordinate limit modes without changing color limit mode
- MATLAB-style axis direction helpers with `xdir`, `ydir`, and `zdir` for `normal`/`reverse` directions, with `axis ij/xy` updating only y direction
- MATLAB-style axis scale helpers with `xscale`, `yscale`, and `zscale` for `linear`/`log` scale state
- MATLAB-style axes appearance helpers with `layer`, `tickdir`, `tickdirmode`, `ticklength`, `xaxislocation`, and `yaxislocation`
- MATLAB-style per-axis grid helpers with `xgrid`, `ygrid`, `zgrid`, `xminorgrid`, `yminorgrid`, and `zminorgrid`
- MATLAB-style per-axis minor tick helpers with `xminortick`, `yminortick`, and `zminortick`
- MATLAB-style tick helpers with `xticks`, `yticks`, and `zticks` supporting current tick queries, increasing finite tick vectors, empty ticks, `auto`, `manual`, and `mode`
- MATLAB-style tick label helpers with `xticklabels`, `yticklabels`, `zticklabels`, and tick-label rotation helpers, including empty labels, automatic padding, `auto`, `manual`, and `mode`
- MATLAB-style text helpers with `title`, `xlabel`, `ylabel`, and `zlabel` storing single-line or multi-line text in view history
- MATLAB-style explicit aspect ratio helpers with `daspect()` / `daspect([x, y, z])` and `pbaspect()` / `pbaspect([x, y, z])`, including `auto`, `manual`, and `mode`
- MATLAB-style `xlim`, `ylim`, and `zlim` commands with `[min, max]`, `auto`, `manual`, `mode`, or no-argument current-limit queries
- MATLAB-style `axis()` current-limit queries, `axis("state")` coordinate-limit auto/manual queries, numeric limit vectors via `axis([xmin, xmax, ymin, ymax])`, 3D `axis([xmin, xmax, ymin, ymax, zmin, zmax])`, and color limits with `axis([xmin, xmax, ymin, ymax, zmin, zmax, cmin, cmax])`
- direct color limit control with `set_clim(cmin, cmax)`, MATLAB-style `clim([cmin, cmax])`, `clim auto`, `clim manual`, `clim mode`, or no-argument current-limit queries, plus `caxis(...)` as the traditional MATLAB-compatible alias
- active-axes-scoped view history for home/back/forward, including 3D camera and z limits, with `can_home`/`can_back`/`can_forward` UI state queries and `on_view_history_changed` notifications
- MATLAB-style `linkaxes(axes, "x"|"y"|"xy"|"off")` linked-limit control, defaulting to `xy` and using MATLAB-like initial union limits before subsequent pan/zoom synchronization
- read-only view snapshots with `current_view_state()`
- 3D camera snapshots normalize equivalent azimuth angles for stable view-history comparisons
- MATLAB-style 3D camera views with `view()`, `view(2)`, `view(3)`, `view("2d")`, `view("3d")`, `view([azim, elev])`, and `view(azim, elev)`
- per-axes 3D camera mode tracking so `view(...)` and rotate3d mark camera state as manual without forcing data limits to manual
- MATLAB-style 3D camera view-angle state with `camva()`, `camva(value)`, `camva("auto")`, `camva("manual")`, and `camva("mode")`
- MATLAB-style 3D camera zoom helper with `camzoom(factor)` updating camera view angle
- MATLAB-style 3D orbit helper with `camorbit(dazim, delev)` for finite azimuth/elevation deltas
- MATLAB-style 3D roll helper with `camroll(angle)` for finite camera roll deltas
- MATLAB-style 3D dolly helper with `camdolly(dx, dy, dz)` for finite camera position/target translation
- MATLAB-style 3D camera projection helper with `camproj()`, `camproj("orthographic")`, and `camproj("perspective")`
- MATLAB-style 3D camera look-at helper with `camlookat()` marking position, target, and view-angle modes manual
- MATLAB-style 3D camera vector state with `campos`, `camtarget`, and `camup` query/set/mode helpers for finite 3-element vectors
- wheel zoom, zoom-tool click in/out, drag-box zoom, and drag-pan state transitions
- left-button double-click on an axes restores that axes to its home view and does not start a pan/zoom/rotate drag
- MATLAB-like pan/zoom tool state with `pan_motion` and `zoom_motion` set to `both`, `horizontal`, or `vertical`, `pan_3d_mode` and `zoom_3d_mode` set to `camera` or `limits`, `zoom_direction` set to `in` or `out`, and `zoom_right_click_action` set to `postcontextmenu` or `inversezoom`
- MATLAB-like rotate3d tool state with `rotate_motion` set to `both`, `horizontal`, or `vertical`, plus `rotate_style` set to `orbit` by default, matching MATLAB's `RotateStyle`
- MATLAB-like `UseLegacyExplorationModes` reporting in tool snapshots; MATLAB R2023b reports this as `off` for pan, zoom, and rotate3d
- MATLAB-like exploration tool hooks with `button_down_filter(event)`, `action_pre_callback(mode, event)`, and `action_post_callback(mode, event)` for pan, zoom, and rotate3d integrations
- MATLAB-like `rotate3d` mode with low, pixel-based rotation sensitivity
- a small optional adapter for Matplotlib axes

The core classes are pure Python so the behavior can be tested without a GUI backend.

The backend-neutral `MatlabLikeAxesBase.plot(...)` method normalizes common
MATLAB line-plot calling forms into `PlotSeries` records, including
positional axes handles with `plot(ax, ...)`, `plot(Y)` matrix-column
expansion, `plot(x, Y)` vector-to-matrix expansion, and `plot(X, Y)` paired
matrix columns. MATLAB-style Name/Value pairs at the end of the argument list
are accepted for common line properties such as `LineWidth`, `LineStyle`,
`Marker`, `Color`, `MarkerSize`, and `DisplayName`; names are normalized to
backend-friendly property keys, with `DisplayName` mapped to `label` for
Matplotlib. MATLAB LineSpec strings such as `r--o`, `k:`, and `x` are parsed
into backend-neutral `color`, `linestyle`, and `marker` properties, while
unrecognized style strings are preserved for backends that can handle them.
Series without explicit `Color` or `LineStyle` use MATLAB-like default
`ColorOrder` and `LineStyleOrder` values from a per-axes `NextSeriesIndex`;
`NextPlot="replace"` resets the cycle, while `hold on` continues it. The
method runs `newplot(...)` / `prepare_for_plot(...)`, delegates actual artist creation to
`draw_plot_series(...)`, then calls `after_plot(...)`. Backends can implement
one hook and inherit MATLAB-like `hold`/`NextPlot` behavior consistently.
Use `colororder(...)`, `linestyleorder(...)`, and `nextseriesindex(...)` to
query or set the per-axes series-order state explicitly; setting color or line
style order resets `NextSeriesIndex` to MATLAB-like cycle-start behavior.
`semilogx(...)`, `semilogy(...)`, and `loglog(...)` share the same parsing,
series-order, `NextPlot`, and view-history behavior as `plot(...)`, then apply
the corresponding x/y logarithmic axis scale.
`plot3(...)` normalizes repeated `x, y, z, LineSpec` groups into `Plot3Series`
records, including matrix-column expansion and the same LineSpec,
Name/Value, ColorOrder, LineStyleOrder, hold, and `NextPlot` behavior as
2D `plot(...)`.
`stairs(...)` normalizes the same x/y data forms as `plot(...)`, expands each
series into stairstep points, then draws through the same backend line hook.
`errorbar(...)` normalizes vertical symmetric and asymmetric error-bar forms,
including matrix-column expansion, then delegates to a backend errorbar hook
while preserving LineSpec, Name/Value, series-order, hold, and `NextPlot`
behavior.
`scatter(...)` normalizes `scatter(x, y)`, `scatter(x, y, size)`, and
`scatter(x, y, size, color)` forms into backend-neutral `ScatterSeries`
records. Marker size may be scalar or one value per point; color may be a
color string, RGB triplet, or one RGB row per point. The helper supports
positional axes handles, MATLAB-style Name/Value properties, matrix-column
expansion, default `ColorOrder` / `NextSeriesIndex` assignment, hold, and
`NextPlot` lifecycle behavior before delegating to `draw_scatter_series(...)`.
`stem(...)` normalizes the same `y`, `x/y`, LineSpec, matrix-column, and
Name/Value forms as `plot(...)` into backend-neutral `StemSeries` records,
then applies default series-order, hold, and `NextPlot` behavior before
delegating to `draw_stem_series(...)`.
`bar(...)` normalizes the same `y`, `x/y`, LineSpec, matrix-column, and
Name/Value forms as `plot(...)` into backend-neutral `BarSeries` records for
vertical bars, then applies default series-order, hold, and `NextPlot`
behavior before delegating to `draw_bar_series(...)`.
`area(...)` normalizes the same `y`, `x/y`, LineSpec, matrix-column, and
Name/Value forms as `plot(...)` into backend-neutral `AreaSeries` records.
Matrix columns are converted to stacked top/baseline pairs before default
series-order, hold, and `NextPlot` behavior are applied, then delegated to
`draw_area_series(...)`.
`fill(...)` normalizes repeated `x, y, color` polygon groups into
backend-neutral `FillSeries` records. Colors may be strings, RGB triplets, or
N-by-3 RGB sequences; polygons without explicit color use `ColorOrder` and
`NextSeriesIndex`. The helper also supports positional axes handles,
Name/Value properties, hold, and `NextPlot` lifecycle behavior before
delegating to `draw_fill_series(...)`.
`histogram(...)` normalizes data plus an optional positive bin count or
strictly increasing bin-edge vector into backend-neutral `HistogramSeries`
records. Histograms without explicit color use `ColorOrder` and
`NextSeriesIndex`; positional axes handles, Name/Value properties, hold, and
`NextPlot` lifecycle behavior are preserved before delegating to
`draw_histogram_series(...)`.
`xline(...)` and `yline(...)` normalize scalar or vector positions, optional
LineSpec strings, labels, Name/Value properties, and positional axes handles
into backend-neutral `ConstantLineSeries` records. Like `line(...)`, they add
reference-line primitives without `NextPlot` clearing or default series-order
assignment before delegating to `draw_constant_line_series(...)`.
`text(...)` normalizes `text(x, y, str)` and `text(x, y, z, str)` forms into
backend-neutral `TextSeries` records. It supports multi-line text sequences,
Name/Value properties, and positional axes handles, and like `line(...)` adds
annotations without `NextPlot` clearing or default series-order assignment
before delegating to `draw_text_series(...)`.
`imagesc(...)` normalizes `imagesc(C)` and `imagesc(x, y, C)` forms into
backend-neutral `ImageSeries` records. It accepts numeric matrix CData,
optional two-endpoint x/y axes, Name/Value properties, `NextPlot` lifecycle
behavior, and autoscaled color limits when `clim` mode is `auto`, before
delegating to `draw_image_series(...)`.
`colormap(...)` queries or sets the active axes colormap state. String names
are normalized to lowercase, and numeric maps use MATLAB-like N-by-3 RGB rows
with values in `[0, 1]`. The Matplotlib adapter applies the selected colormap
to existing images and collections on the target axes.
`contour(...)` normalizes `contour(Z)`, `contour(Z, n)`, `contour(X, Y, Z)`, and `contour(X, Y, Z, v)` forms into backend-neutral `ContourSeries` records. It accepts numeric matrix ZData, optional X/Y coordinate vectors, an optional scalar level count or explicit level vector, Name/Value properties, `NextPlot` lifecycle behavior, and autoscaled color limits when `clim` mode is `auto`, before delegating to `draw_contour_series(...)`.
`contourf(...)` shares the same calling-form normalization as `contour(...)` but delegates to `draw_contourf_series(...)` for filled contour rendering.
`surf(...)` normalizes `surf(Z)`, `surf(X, Y, Z)`, and `surf(X, Y, Z, C)` forms into backend-neutral `SurfaceSeries` records. It accepts numeric matrix ZData, optional X/Y coordinate vectors, optional color data, Name/Value properties, `NextPlot` lifecycle behavior, and autoscaled color limits when `clim` mode is `auto`, before delegating to `draw_surf_series(...)`.
`mesh(...)` shares the same calling-form normalization as `surf(...)` but delegates to `draw_mesh_series(...)` for wireframe rendering.
`quiver(...)` normalizes `quiver(U, V)` and `quiver(X, Y, U, V)` forms into backend-neutral `QuiverSeries` records. It accepts numeric velocity components, optional position vectors, Name/Value properties, and `NextPlot` lifecycle behavior before delegating to `draw_quiver_series(...)`.
`pcolor(...)` normalizes `pcolor(C)` and `pcolor(X, Y, C)` forms into backend-neutral `PColorSeries` records. It accepts numeric matrix CData, optional X/Y coordinate vectors, Name/Value properties, `NextPlot` lifecycle behavior, and autoscaled color limits when `clim` mode is `auto`, before delegating to `draw_pcolor_series(...)`.
`subplot(m, n, p)` creates or selects an axes in an m-by-n grid at position p, matching MATLAB's subplot layout. Shorthand `subplot(mnp)` with a three-digit integer is also accepted. Previously created subplot axes are cached and reused. The helper delegates actual axes creation to the `create_subplot_axes(rows, columns, position)` backend hook, and the Matplotlib adapter calls `figure.add_subplot(...)`.
`spy(...)` normalizes `spy(S)` forms into backend-neutral `SpySeries` records containing row/column indices of nonzero elements and the matrix dimensions. It accepts numeric matrix data, Name/Value properties, and `NextPlot` lifecycle behavior before delegating to `draw_spy_series(...)`.
`line(...)` adds explicit 2D or 3D line primitives directly to the target axes:
it accepts MATLAB Name/Value properties and positional axes handles, but unlike
`plot(...)` it does not apply `NextPlot` clearing or default series-order
styling.

## Matplotlib Demo

Install Matplotlib, then run:

```bash
PYTHONPATH=src python examples/matplotlib_2d_3d_demo.py
```

The demo wires a Matplotlib canvas to the interaction state machine:

- mouse wheel zooms the axes under the pointer using the wheel step magnitude; zero-step wheel events are ignored
- left-button double-click restores the axes home view without starting the active exploration tool
- zoom mode supports MATLAB-like left-click zoom-in, left-drag box zoom, default right-click context-menu handoff, optional right-click inverse zoom, and ignores degenerate or invalid log-axis drag boxes
- pan mode drags 2D axes by changing limits; shift-pan constrains to the dominant screen-space drag direction, falling back to data-space deltas when pixel coordinates are unavailable; on 3D axes it defaults to camera dolly behavior, with `pan_3d_mode="limits"` available for legacy x/y-limit panning
- `pan_motion` can constrain pan to horizontal or vertical motion, matching MATLAB's pan tool `Motion` setting
- rotate3d mode uses left-button drag on 3D axes with low MATLAB-like sensitivity, keeps pixel-based rotation active when the pointer leaves the start axes, ignores tiny pointer jitter before rotation starts, and leaves right/middle-button gestures to other UI integrations
- data cursor mode clicks a line point within pick tolerance and fixes a data tip, including Z values for 3D lines, without duplicating an existing tip on the same line point
- select mode clicks a line within pick tolerance, highlights it idempotently, clears selection on empty clicks, and supports Shift/Ctrl multi-select
- brush mode left-drags a rectangle to highlight lines with data points inside the box, with Shift/Ctrl additive brushing
- Matplotlib event bridging tracks held Shift/Ctrl/Cmd modifiers across press, move, and release events for constrained pan and additive select/brush
- switching to a MATLAB-like interaction mode deactivates Matplotlib's native toolbar pan/zoom mode so only one interaction stack handles the drag
- mode shortcuts: `n` none; `p`, `z`, `r`, `d`, `s`, and `B` toggle pan, zoom, rotate3d, data cursor, select, and brush
- shifted shortcut keys are normalized across Matplotlib backends, so `B` and backend strings like `shift+b` both activate brush mode
- `h` restores home, left/right arrows move through view history
- `a` runs `axis auto`, `M` runs `axis manual`, `t` runs `axis tight`, `e` runs `axis equal`, `f` runs `axis fill`, `i` runs `axis image`, `m` runs `axis normal`, `q` runs `axis square`, `w` runs `axis vis3d`, `O` runs `axis off`, `U` runs `axis on`, `j` runs `axis ij`, `k` runs `axis xy`
- `2` applies MATLAB-like `view(2)`, `3` applies MATLAB-like `view(3)` on 3D axes; UI integrations can call `bridge.apply_view("xy"|"xz"|"yz")` for orthographic view buttons
- `o` toggles MATLAB-style `hold on/off`
- escape returns to `none` mode and clears selection/readout plus any bridge-tracked modifier state
- delete/backspace deletes selected lines, or clears data tips when no line is selected
- `v` toggles selected line visibility
- `g` toggles the active axes grid; integrations can also call `grid("on"|"off"|"toggle"|"minor")`
- `l` toggles the active axes legend; integrations can also call `legend("on"|"off"|"toggle")`
- `x`/`y`/`b` toggle linked x, y, or both-axis limits across axes in the same figure
- linked axes updates also mark the corresponding linked limit modes as manual
- pointer movement updates a coordinate readout for the active hover axes, including nearby line Z values on 3D axes when available within tolerance
- clicking an axes makes it active and highlights its spines

The 3D rotation path uses pointer pixel deltas when available because Matplotlib
3D data coordinates can be unstable during drag. The default gains are
deliberately conservative (`0.18` degrees/pixel for azimuth and `0.12`
degrees/pixel for elevation), with a `3.0` pixel startup threshold to avoid
accidental camera changes from click jitter. Drag rotation stores azimuth in a
signed MATLAB-like range instead of wrapping to `0..360`. Integrations can tune
`rotate_drag_pixel_threshold`, `rotate_azimuth_sensitivity`, and
`rotate_elevation_sensitivity` separately, or set the compatibility scalar
`rotate_sensitivity` to update both gains. `rotate_motion` can constrain
rotate3d drags to horizontal azimuth-only or vertical elevation-only motion.
Once a rotate3d drag starts, later pixel-coordinate motion is applied even if
the pointer leaves the start axes, matching toolbar-style pointer capture.

The `view(...)` helpers preserve the current camera view angle, matching
MATLAB's behavior that changing azimuth/elevation does not force
`CameraViewAngleMode` to manual. Use `camva(value)` to set a finite manual
view angle, `camva("auto"|"manual")` to change the mode, and `camva("mode")`
to query it. The Matplotlib adapter maps this to the 3D axes `dist` attribute
when available. `camzoom(factor)` applies MATLAB's perspective view-angle
scaling for finite positive factors, where values greater than 1 zoom in and
values between 0 and 1 zoom out.

`daspect([x, y, z])` and `pbaspect([x, y, z])` set positive finite
3-element data and plot-box aspect ratios and switch their modes to manual.
`"auto"`, `"manual"`, and `"mode"` mirror MATLAB's mode controls, and the
ratios participate in the same view history as limits and camera state.

`xdir("normal"|"reverse")`, `ydir(...)`, and `zdir(...)` expose MATLAB-style
axis direction state. The `axis("ij")` and `axis("xy")` helpers remain
MATLAB-compatible by changing only y direction, while x and z direction state
is preserved and restored through view history.

`xscale("linear"|"log")`, `yscale(...)`, and `zscale(...)` expose MATLAB-style
axis scale state and restore it through view history. 2D pan and zoom gestures
use logarithmic-space limit math for positive log axes, so dragging and wheel
zooming preserve multiplicative visual spacing; nonpositive limits or centers
fall back to linear math. Drag-box zoom rejects nonpositive box edges on log
axes that are affected by the current `zoom_motion`, and its degenerate-box
threshold is measured in logarithmic span for log axes.

`grid("minor")` toggles minor grid visibility independently from the major
grid, and `grid("off")` clears both major and minor grid state, matching
MATLAB's grid command behavior. `xgrid(...)`, `ygrid(...)`, `zgrid(...)`,
`xminorgrid(...)`, `yminorgrid(...)`, and `zminorgrid(...)` expose MATLAB's
per-axis grid properties, so global grid commands can be followed by
axis-specific overrides. `xminortick(...)`, `yminortick(...)`, and
`zminortick(...)` expose the independent MATLAB minor tick visibility
properties. Major and minor per-axis grid visibility plus minor tick visibility
are restored through view history.

`colorbar("on"|"off"|"toggle")` mirrors MATLAB's colorbar visibility helper for
the target axes. Backends decide whether a mappable image or collection is
available; the Matplotlib adapter attaches the colorbar to the latest image or
collection and removes the tracked colorbar on `off`.

`xticks(...)`, `yticks(...)`, and `zticks(...)` mirror MATLAB's tick location
helpers. No argument queries current tick locations, a finite increasing vector
sets manual ticks, an empty vector hides ticks, and `"auto"`, `"manual"`, or
`"mode"` control/query tick mode. Manual tick locations participate in view
history restore.

`xticklabels(...)`, `yticklabels(...)`, and `zticklabels(...)` mirror MATLAB's
tick label helpers. Label sequences set manual labels, shorter sequences are
padded with empty strings to the current tick count, and empty sequences hide
tick labels. `"auto"`, `"manual"`, and `"mode"` control/query tick-label mode,
and manual labels are restored with view history. `xticklabelrotation(...)`,
`yticklabelrotation(...)`, and `zticklabelrotation(...)` mirror MATLAB's
finite-angle tick label rotation properties, including `auto`, `manual`, and
`mode`; `auto` resets the stored rotation to `0.0` like MATLAB.

`layer("bottom"|"top")`, `tickdir("in"|"out"|"both"|"none")`,
`tickdirmode("auto"|"manual"|"mode")`, `ticklength([major, minor])`,
`xaxislocation("bottom"|"top"|"origin")`, and
`yaxislocation("left"|"right"|"origin")` mirror MATLAB axes Layer, TickDir,
TickDirMode, TickLength, XAxisLocation, and YAxisLocation UI state. The
Matplotlib adapter maps Layer to `set_axisbelow`, TickDir and TickLength to
`tick_params(...)`, and axis locations to tick/label positions plus spine
placement where available; these properties are scoped per axes and restored
through view history.

`title(...)`, `xlabel(...)`, `ylabel(...)`, and `zlabel(...)` set and query
axes text content. Strings are stored as one line, sequences are stored as
multi-line text, scalar values are converted to strings, and the text state is
restored through view history.

`camorbit(dazim, delev)` applies finite azimuth/elevation deltas, clamps
elevation to the configured `elevation_limits`, and marks camera position and
up-vector modes manual like MATLAB orbit operations. The current implementation
updates the backend-neutral azimuth/elevation camera state; full geometric
recomputation of camera position and up-vector can be layered in by backends
that expose a complete camera model.

`camroll(angle)` applies a finite camera roll delta and marks camera
up-vector mode manual, including the MATLAB-compatible `camroll(0)` case. The
base class stores this as backend-neutral roll state; backends with full camera
geometry can also update the concrete up-vector.

`camproj()` queries the current 3D projection mode, and
`camproj("orthographic"|"perspective")` switches between MATLAB-style
orthographic and perspective projection. Projection state participates in the
same view history as limits and camera angles, so home/back/forward restore it
with the rest of the 3D view.

`camlookat()` mirrors MATLAB's 3D camera-fit mode semantics by marking camera
position, target, and view-angle modes manual while leaving up-vector mode
unchanged. The backend-neutral base preserves existing camera vectors when
available, or derives a stable target and position from current 3D limits when
they are missing; backends with full scene bounds can replace this with exact
MATLAB-style camera fitting.

`camdolly(dx, dy, dz)` moves camera position and target together when those
vectors are available and marks both modes manual, matching MATLAB's mode
semantics. In the backend-neutral base this is a direct vector translation;
backends with a full MATLAB-style camera basis can replace this with exact
camera-coordinate dolly math.

The camera vector helpers mirror MATLAB's `campos`, `camtarget`, and `camup`
shape: no argument queries the current 3-element vector, a finite 3-element
sequence sets it and marks the corresponding mode manual, and
`"auto"`, `"manual"`, or `"mode"` control/query the mode. Backends that do not
expose concrete camera position, target, or up-vector values can return `None`
while still preserving the mode state in the base class.

`linkaxes(axes, option)` links x, y, or both limits for a list of axes, with
`option` set to `"x"`, `"y"`, `"xy"`, or `"off"`. Like MATLAB, the default is
`"xy"` and the initial linked view uses the union of existing linked limits;
later pan, zoom, and explicit limit commands synchronize the linked axes.

The pan and zoom tool state mirrors MATLAB's figure tool objects: pan and zoom
default to `Motion="both"`, while zoom defaults to `Direction="in"`. Setting
`pan_motion` or `zoom_motion` to `horizontal` or `vertical` constrains the
affected limit axis, and setting `zoom_direction` to `out` makes left-click and
wheel zoom gestures expand limits instead of shrinking them. Zoom also defaults
to `RightClickAction="PostContextMenu"` like MATLAB; set
`zoom_right_click_action` to `inversezoom` to preserve right-click zoom-out
behavior in integrations that want that shortcut.

For 3D axes, `pan_3d_mode` defaults to `camera`, so pan gestures translate
camera position and target through the same camera-state path as `camdolly`.
Set it to `limits` to preserve the older behavior of panning x/y limits on 3D
axes.

`zoom_3d_mode` also defaults to `camera`, so wheel zoom and zoom-tool point
clicks use `camzoom` when the backend exposes a camera view angle. Set it to
`limits` to force x/y-limit zooming on 3D axes.

Pan, zoom, and rotate3d also expose MATLAB-style action lifecycle hooks.
Override `button_down_filter(event)` to prevent an exploration tool from taking
over a press, and override `action_pre_callback(mode, event)` /
`action_post_callback(mode, event)` to mirror MATLAB tool pre/post callbacks
around completed or cancelled interactions.

Toolbar integrations can query `pan_state()`, `zoom_state()`, and
`rotate3d_state()` instead of reconstructing state from individual properties.
The snapshots expose MATLAB-like `enable` values (`on`/`off`) and include
tool-specific properties such as pan/zoom/rotate motion, zoom direction, and
zoom right-click behavior. `rotate3d_state()` also reports `rotate_style`,
which defaults to MATLAB's `orbit`. The snapshots include
`use_legacy_exploration_modes`, currently reported as `off` to match MATLAB
R2023b's pan, zoom, and rotate3d tool objects.
