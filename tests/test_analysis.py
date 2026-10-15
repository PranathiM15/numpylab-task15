import unittest

from app import analyze_values


class AnalyzeValuesTests(unittest.TestCase):
    def test_basic_statistics(self):
        result = analyze_values([1, 2, 3, 4, 5])
        self.assertEqual(result["count"], 5)
        self.assertEqual(result["mean"], 3.0)
        self.assertEqual(result["median"], 3.0)
        self.assertEqual(result["min"], 1.0)
        self.assertEqual(result["max"], 5.0)
        self.assertEqual(result["range"], 4.0)

    def test_population_standard_deviation(self):
        result = analyze_values([2, 4, 4, 4, 5, 5, 7, 9])
        self.assertEqual(result["std_dev"], 2.0)
        self.assertEqual(result["std_dev_type"], "population")

    def test_low_outlier_is_flagged(self):
        result = analyze_values([68, 72, 76, 79, 83, 85, 88, 91, 94, 97, 12])
        self.assertTrue(any(item["value"] == 12.0 and item["outlier_kind"] == "low" for item in result["outliers"]))

    def test_requires_three_observations(self):
        with self.assertRaisesRegex(ValueError, "at least 3"):
            analyze_values([2, 3])

    def test_rejects_non_finite_values(self):
        with self.assertRaisesRegex(ValueError, "finite"):
            analyze_values([1, float("nan"), 3])

    def test_rejects_too_many_observations(self):
        with self.assertRaisesRegex(ValueError, "no more than 500"):
            analyze_values(list(range(501)))


if __name__ == "__main__":
    unittest.main()
