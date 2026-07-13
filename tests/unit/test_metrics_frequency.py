import pandas as pd

from vn_lottery_xsmb.analytics.metrics import frequency, histogram


def test_frequency_counts_last_two_digits() -> None:
    prizes = pd.read_csv("tests/fixtures/prizes_sample.csv", dtype=str)

    result = frequency(prizes)

    assert result.iloc[0].to_dict() == {"number": "45", "count": 3}


def test_histogram_groups_frequency_counts() -> None:
    prizes = pd.read_csv("tests/fixtures/prizes_sample.csv", dtype=str)

    result = histogram(prizes)

    assert set(result.columns) == {"count", "number_total"}
