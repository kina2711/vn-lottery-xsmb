from __future__ import annotations

from pathlib import Path

import pandas as pd


def _prepared_prizes(prizes: pd.DataFrame) -> pd.DataFrame:
    frame = prizes.copy()
    if frame.empty:
        return frame
    frame["draw_date"] = pd.to_datetime(frame["draw_date"])
    frame["month"] = frame["draw_date"].dt.to_period("M").astype(str)
    frame["last_two_digits"] = frame["last_two_digits"].astype(str).str.zfill(2)
    return frame


def frequency(prizes: pd.DataFrame) -> pd.DataFrame:
    frame = _prepared_prizes(prizes)
    if frame.empty:
        return pd.DataFrame(columns=["number", "count"])
    return (
        frame.groupby("last_two_digits")
        .size()
        .reset_index(name="count")
        .rename(columns={"last_two_digits": "number"})
        .sort_values(["count", "number"], ascending=[False, True])
        .reset_index(drop=True)
    )


def histogram(prizes: pd.DataFrame) -> pd.DataFrame:
    freq = frequency(prizes)
    if freq.empty:
        return pd.DataFrame(columns=["count", "number_total"])
    return freq.groupby("count").size().reset_index(name="number_total").sort_values("count")


def monthly_distribution(prizes: pd.DataFrame) -> pd.DataFrame:
    frame = _prepared_prizes(prizes)
    if frame.empty:
        return pd.DataFrame(columns=["month", "number", "count"])
    return (
        frame.groupby(["month", "last_two_digits"])
        .size()
        .reset_index(name="count")
        .rename(columns={"last_two_digits": "number"})
        .sort_values(["month", "number"])
        .reset_index(drop=True)
    )


def heatmap_table(prizes: pd.DataFrame) -> pd.DataFrame:
    monthly = monthly_distribution(prizes)
    if monthly.empty:
        return pd.DataFrame()
    return monthly.pivot_table(
        index="number",
        columns="month",
        values="count",
        aggfunc="sum",
        fill_value=0,
    ).reset_index()


def write_metric_outputs(prizes: pd.DataFrame, output_dir: Path, window: int = 30) -> dict[str, Path]:
    from vn_lottery_xsmb.analytics.windows import (
        days_since_last_seen,
        moving_average,
        rolling_frequency,
    )

    output_dir.mkdir(parents=True, exist_ok=True)
    outputs = {
        "frequency": output_dir / "frequency.csv",
        "histogram": output_dir / "histogram.csv",
        "monthly_distribution": output_dir / "monthly_distribution.csv",
        "heatmap": output_dir / "heatmap.csv",
        "rolling_frequency": output_dir / "rolling_frequency.csv",
        "moving_average": output_dir / "moving_average.csv",
        "days_since_last_seen": output_dir / "days_since_last_seen.csv",
    }
    frequency(prizes).to_csv(outputs["frequency"], index=False)
    histogram(prizes).to_csv(outputs["histogram"], index=False)
    monthly_distribution(prizes).to_csv(outputs["monthly_distribution"], index=False)
    heatmap_table(prizes).to_csv(outputs["heatmap"], index=False)
    rolling_frequency(prizes, window).to_csv(outputs["rolling_frequency"], index=False)
    moving_average(prizes, window).to_csv(outputs["moving_average"], index=False)
    days_since_last_seen(prizes).to_csv(outputs["days_since_last_seen"], index=False)
    return outputs
