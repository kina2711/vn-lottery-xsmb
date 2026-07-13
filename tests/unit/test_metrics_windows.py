import pandas as pd

from vn_lottery_xsmb.analytics.windows import moving_average, rolling_frequency


def test_rolling_frequency_uses_prior_dates_only() -> None:
    prizes = pd.read_csv("tests/fixtures/prizes_sample.csv", dtype=str)

    result = rolling_frequency(prizes, window_days=2)
    number_45 = result.loc[(result["draw_date"] == "2026-07-12") & (result["number"] == "45")]

    assert int(number_45.iloc[0]["rolling_count"]) == 2


def test_moving_average_divides_by_window() -> None:
    prizes = pd.read_csv("tests/fixtures/prizes_sample.csv", dtype=str)

    result = moving_average(prizes, window_days=2)
    number_45 = result.loc[(result["draw_date"] == "2026-07-12") & (result["number"] == "45")]

    assert float(number_45.iloc[0]["moving_average"]) == 1.0
