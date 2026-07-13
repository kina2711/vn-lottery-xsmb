import pandas as pd

from vn_lottery_xsmb.analytics.metrics import heatmap_table, monthly_distribution
from vn_lottery_xsmb.analytics.windows import days_since_last_seen


def test_days_since_last_seen() -> None:
    prizes = pd.read_csv("tests/fixtures/prizes_sample.csv", dtype=str)

    result = days_since_last_seen(prizes)

    assert result.loc[result["number"] == "45", "days_since"].iloc[0] == 0
    assert result.loc[result["number"] == "56", "days_since"].iloc[0] == 2


def test_monthly_distribution_and_heatmap() -> None:
    prizes = pd.read_csv("tests/fixtures/prizes_sample.csv", dtype=str)

    monthly = monthly_distribution(prizes)
    heatmap = heatmap_table(prizes)

    assert "2026-07" in set(monthly["month"])
    assert "2026-07" in heatmap.columns
