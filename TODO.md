# TODO

This file tracks low-risk follow-up work that was previously kept in
`todo.md.save`.

## Context Menu

- Promote the Qt native context menu path to a first-class integration option,
  for example through a `context_menu_backend="qt"` setting or a small factory.
- Keep the current Matplotlib-drawn menu for single-canvas use cases, but make
  the Qt path the recommended option for dense multi-plot Qt applications.
- Continue aligning Qt-rendered icons with the existing Matplotlib menu icon
  model so applications do not need to maintain their own icon mapping.
- Preserve automatic close behavior across canvases when a Qt menu opens.

## Axes Lifecycle

- Add an explicit cleanup API for removed axes or disposed plotter instances.
- Ensure axes-specific state can be cleared from active axes state, view
  history, linked axes groups, selected artists, data tips, and brush state.
- Revisit strong references from `self.axes`, `ViewState.axes`, `view_stack`,
  and linked axes sets when embedding in applications that frequently rebuild
  plot widgets.
