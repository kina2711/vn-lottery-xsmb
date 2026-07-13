from __future__ import annotations

import pandas as pd


def _daily_number_counts(prizes: pd.DataFrame) -> pd.DataFrame:
    frame = prizes.copy()
    if frame.empty:
        return pd.DataFrame(columns=["draw_date", "number", "count"])
    frame["draw_date"] = pd.to_datetime(frame["draw_date"])
    frame["number"] = frame["last_two_digits"].astype(str).str.zfill(2)
    return frame.groupby(["draw_date", "number"]).size().reset_index(name="count")


def rolling_frequency(prizes: pd.DataFrame, window_days: int) -> pd.DataFrame:
    daily = _daily_number_counts(prizes)
    if daily.empty:
        return pd.DataFrame(columns=["draw_date", "number", "rolling_count"])
    dates = pd.date_range(daily["draw_date"].min(), daily["draw_date"].max(), freq="D")
    numbers = sorted(daily["number"].unique())
    grid = pd.MultiIndex.from_product([dates, numbers], names=["draw_date", "number"]).to_frame(index=False)
    merged = grid.merge(daily, on=["draw_date", "number"], how="left").fillna({"count": 0})
    merged["rolling_count"] = (
        merged.sort_values("draw_date")
        .groupby("number")["count"]
        .transform(lambda series: series.rolling(window_days, min_periods=1).sum())
    )
    return merged[["draw_date", "number", "rolling_count"]].assign(
        draw_date=lambda frame: frame["draw_date"].dt.date.astype(str)
    )


def moving_average(prizes: pd.DataFrame, window_days: int) -> pd.DataFrame:
    rolling = rolling_frequency(prizes, window_days)
    if rolling.empty:
        return pd.DataFrame(columns=["draw_date", "number", "moving_average"])
    rolling["moving_average"] = rolling["rolling_count"] / window_days
    return rolling[["draw_date", "number", "moving_average"]]


def days_since_last_seen(prizes: pd.DataFrame) -> pd.DataFrame:
    daily = _daily_number_counts(prizes)
    if daily.empty:
        return pd.DataFrame(columns=["number", "last_seen", "days_since"])
    latest = daily["draw_date"].max()
    last_seen = daily.groupby("number")["draw_date"].max().reset_index(name="last_seen")
    last_seen["days_since"] = (latest - last_seen["last_seen"]).dt.days
    last_seen["last_seen"] = last_seen["last_seen"].dt.date.astype(str)
    return last_seen.sort_values(["days_since", "number"], ascending=[False, True]).reset_index(drop=True)
