import csv
import sqlite3
import tempfile
import unittest
from pathlib import Path

from src.db import count_rows
from src.marketing_os import competitive_analysis, consumer_insight, content_opportunity, effect_analysis, read_csv, run_os


class MarketingOSTests(unittest.TestCase):
    def setUp(self):
        self.root = Path(__file__).parents[1]
        self.raw = self.root / "data" / "raw"

    def test_modules_produce_traceable_outputs(self):
        feedback = read_csv(self.raw / "consumer_feedback.csv")
        insight = consumer_insight(feedback)
        self.assertEqual(insight["sample_size"], 20)
        self.assertTrue(insight["topic_metrics"][0]["evidence_ids"])
        competition = competitive_analysis(read_csv(self.raw / "competitor_snapshot.csv"))
        opportunity = content_opportunity(read_csv(self.raw / "content_coverage.csv"), insight)
        effect = effect_analysis(read_csv(self.raw / "ab_test_anonymous.csv"), read_csv(self.raw / "questionnaire_anonymous.csv"))
        self.assertEqual(len(competition["ranked_competitors"]), 4)
        self.assertEqual(len(opportunity["ranked_opportunities"]), 4)
        self.assertGreater(effect["conversion_uplift_B_vs_A_pct"], 0)

    def test_full_run_and_sqlite_rows(self):
        with tempfile.TemporaryDirectory() as temp:
            temp_root = Path(temp)
            for source in ["brand_profile.json", "consumer_feedback.csv", "competitor_snapshot.csv", "content_coverage.csv", "ab_test_anonymous.csv", "questionnaire_anonymous.csv"]:
                target = temp_root / "data" / "raw" / source
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes((self.raw / source).read_bytes())
            result = run_os(temp_root)
            self.assertEqual(result["version"], "v1.0")
            self.assertTrue((temp_root / "reports" / "analysis_report.md").exists())
            self.assertEqual(count_rows(temp_root / "data" / "marketing_os.db", "consumer_feedback"), 20)
            self.assertEqual(count_rows(temp_root / "data" / "marketing_os.db", "experiment_result"), 24)

    def test_ab_sample_has_two_balanced_variants(self):
        rows = read_csv(self.raw / "ab_test_anonymous.csv")
        counts = {variant: sum(row["variant"] == variant for row in rows) for variant in {"A", "B"}}
        self.assertEqual(counts, {"A": 12, "B": 12})


if __name__ == "__main__":
    unittest.main()
