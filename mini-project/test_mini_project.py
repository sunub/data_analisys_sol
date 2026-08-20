import json
import unittest
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parent
NOTEBOOK_PATH = PROJECT_DIR / "mini-project.ipynb"


def load_analysis_namespace():
    notebook = json.loads(NOTEBOOK_PATH.read_text(encoding="utf-8"))
    core_cells = [
        "".join(cell["source"])
        for cell in notebook["cells"]
        if cell["cell_type"] == "code"
        and "analysis-core" in cell.get("metadata", {}).get("tags", [])
    ]
    if not core_cells:
        raise AssertionError("실행 가능한 analysis-core 셀이 없습니다.")

    namespace = {}
    exec("\n\n".join(core_cells), namespace)
    return namespace


class PopulationAnalysisTest(unittest.TestCase):
    def test_gu_summary_uses_actual_population_as_ratio_denominator(self):
        analysis = load_analysis_namespace()
        population = analysis["load_population_data"](PROJECT_DIR)
        summary = analysis["build_gu_summary"](population).set_index("구")

        expected = {
            "남동구": (480_147, 58_973, 12.2822802183),
            "미추홀구": (417_578, 48_481, 11.6100465063),
            "연수구": (409_437, 71_191, 17.3875345902),
        }
        for gu, (total, children, ratio) in expected.items():
            with self.subTest(gu=gu):
                self.assertEqual(summary.loc[gu, "2025년_전체"], total)
                self.assertEqual(summary.loc[gu, "2025년_아동전체"], children)
                self.assertAlmostEqual(summary.loc[gu, "아동비율"], ratio, places=8)

    def test_top5_keeps_full_dong_names_and_returns_five_per_gu(self):
        analysis = load_analysis_namespace()
        population = analysis["load_population_data"](PROJECT_DIR)
        top5 = analysis["build_top5"](population)

        self.assertEqual(top5.groupby("구").size().to_dict(), {
            "남동구": 5,
            "미추홀구": 5,
            "연수구": 5,
        })
        michuhol_names = set(top5.loc[top5["구"] == "미추홀구", "동"])
        self.assertIn("도화2.3동", michuhol_names)
        self.assertNotIn("3동", michuhol_names)
        yeonsu = top5.loc[top5["구"] == "연수구", "동"].tolist()
        self.assertEqual(yeonsu, ["송도4동", "송도5동", "송도3동", "송도2동", "송도1동"])


if __name__ == "__main__":
    unittest.main()
