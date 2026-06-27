from py_matlab_style_plotter import MatplotlibAxesPlotter, MatplotlibEventBridge


def main() -> None:
    import matplotlib.pyplot as plt

    fig = plt.figure()
    ax = fig.add_subplot(111, projection="3d")

    plotter = MatplotlibAxesPlotter(ax)
    bridge = MatplotlibEventBridge(plotter)
    bridge.connect()

    plotter.plot3([1, 2, 3], [1, 4, 9], [1, 8, 27])
    plotter.rotate3d("on")

    plt.show()


if __name__ == "__main__":
    main()
