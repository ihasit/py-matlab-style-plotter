import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt

from py_matlab_style_plotter import MatplotlibAxesPlotter


def test_3d_zoom_box_uses_figure_overlay_patch():
    fig = plt.figure()
    ax = fig.add_subplot(111, projection="3d")
    plotter = MatplotlibAxesPlotter(ax)

    plotter.begin_zoom_box(ax, 0.0, 0.0)
    plotter.update_zoom_box(ax, 0.0, 0.0, 1.0, 1.0)

    assert plotter._zoom_box_artist not in ax.patches
    assert plotter._zoom_box_artist in fig.patches
    fig.canvas.draw()

    plotter.end_zoom_box()
    assert not fig.patches


def test_3d_brush_box_uses_figure_overlay_patch():
    fig = plt.figure()
    ax = fig.add_subplot(111, projection="3d")
    plotter = MatplotlibAxesPlotter(ax)

    plotter.begin_brush_box(ax, 0.0, 0.0)
    plotter.update_brush_box(ax, 0.0, 0.0, 1.0, 1.0)

    assert plotter._brush_box_artist not in ax.patches
    assert plotter._brush_box_artist in fig.patches
    fig.canvas.draw()

    plotter.end_brush_box()
    assert not fig.patches


def test_home_restores_3d_data_aspect_without_set_aspect_tuple_error():
    fig = plt.figure()
    ax = fig.add_subplot(111, projection="3d")
    plotter = MatplotlibAxesPlotter(ax)

    plotter.push_current_view(ax)
    plotter.daspect([1.0, 2.0, 3.0])

    assert plotter.home()
    fig.canvas.draw()
