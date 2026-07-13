from pathlib import Path

from vn_lottery_xsmb.visualization.charts import create_static_charts


def test_create_static_charts() -> None:
    outputs = create_static_charts(
        Path("tests/fixtures/metrics_sample"),
        Path(".test-output/charts"),
    )

    assert outputs["frequency"].exists()
    assert outputs["histogram"].exists()
