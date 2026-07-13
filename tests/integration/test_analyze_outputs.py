from pathlib import Path

import pandas as pd

from vn_lottery_xsmb.analytics.metrics import write_metric_outputs


def test_write_metric_outputs() -> None:
    prizes = pd.read_csv("tests/fixtures/prizes_sample.csv", dtype=str)
    output_dir = Path(".test-output/reports")

    outputs = write_metric_outputs(prizes, output_dir, window=2)

    assert set(outputs) == {
        "frequency",
        "histogram",
        "monthly_distribution",
        "heatmap",
        "rolling_frequency",
        "moving_average",
        "days_since_last_seen",
    }
    assert all(path.exists() for path in outputs.values())
