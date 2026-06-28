import unittest

import py_matlab_style_plotter as plotter_api


class PublicApiTest(unittest.TestCase):
    def test_stable_star_import_surface_excludes_internal_state_classes(self):
        self.assertIn("MatplotlibAxesPlotter", plotter_api.__all__)
        self.assertIn("MatplotlibContextMenuEventBridge", plotter_api.__all__)
        self.assertIn("__version__", plotter_api.__all__)

        self.assertNotIn("PlotSeries", plotter_api.__all__)
        self.assertNotIn("DataTip", plotter_api.__all__)
        self.assertNotIn("SelectedLineState", plotter_api.__all__)

    def test_advanced_state_classes_remain_directly_importable(self):
        self.assertTrue(hasattr(plotter_api, "PlotSeries"))
        self.assertTrue(hasattr(plotter_api, "DataTip"))

    def test_version_is_exposed(self):
        self.assertIsInstance(plotter_api.__version__, str)
        self.assertTrue(plotter_api.__version__)


if __name__ == "__main__":
    unittest.main()
