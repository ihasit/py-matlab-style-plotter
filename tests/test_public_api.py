import unittest
from pathlib import Path
import tomllib

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

    def test_version_matches_source_pyproject_in_development_tree(self):
        pyproject = Path(__file__).resolve().parents[1] / "pyproject.toml"
        data = tomllib.loads(pyproject.read_text(encoding="utf-8"))

        self.assertEqual(plotter_api.__version__, data["project"]["version"])

    def test_source_tree_version_ignores_other_project_pyproject(self):
        data = {
            "project": {
                "name": "other-project",
                "version": "9.9.9",
            }
        }

        self.assertIsNone(plotter_api._version_from_pyproject_data(data))


if __name__ == "__main__":
    unittest.main()
