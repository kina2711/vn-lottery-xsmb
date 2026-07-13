from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.express as px
from plotly.io import to_html


def _read_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path) if path.exists() else pd.DataFrame()


def build_dashboard(metrics_dir: Path, output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    frequency = _read_csv(metrics_dir / "frequency.csv")
    monthly = _read_csv(metrics_dir / "monthly_distribution.csv")
    rolling = _read_csv(metrics_dir / "rolling_frequency.csv")
    heatmap = _read_csv(metrics_dir / "heatmap.csv")
    histogram = _read_csv(metrics_dir / "histogram.csv")
    moving = _read_csv(metrics_dir / "moving_average.csv")
    recency = _read_csv(metrics_dir / "days_since_last_seen.csv")
    figures = []
    if not frequency.empty:
        figures.append(px.bar(frequency.head(30), x="number", y="count", title="Tần suất"))
    if not monthly.empty:
        figures.append(px.bar(monthly, x="number", y="count", color="month", title="Phân bố theo tháng"))
    if not rolling.empty:
        figures.append(px.line(rolling, x="draw_date", y="rolling_count", color="number", title="Tần suất cuốn chiếu"))
    if not heatmap.empty:
        figures.append(px.imshow(heatmap.set_index("number"), aspect="auto", title="Bản đồ nhiệt"))
    if not histogram.empty:
        figures.append(px.bar(histogram, x="count", y="number_total", title="Biểu đồ phân phối"))
    if not moving.empty:
        figures.append(px.line(moving, x="draw_date", y="moving_average", color="number", title="Trung bình động"))
    if not recency.empty:
        figures.append(px.bar(recency, x="number", y="days_since", title="Số ngày chưa xuất hiện"))
    body = "\n".join(to_html(figure, full_html=False, include_plotlyjs="cdn") for figure in figures)
    output_path.write_text(
        f"""<!doctype html>
<html lang="vi">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>XSMB Dashboard</title></head>
<body><main><h1>XSMB Dashboard</h1>{body or "<p>Chưa có dữ liệu.</p>"}</main></body>
</html>
""",
        encoding="utf-8",
    )
    return output_path


def _markdown_table(frame: pd.DataFrame) -> str:
    if frame.empty:
        return ""
    columns = [str(column) for column in frame.columns]
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join("---" for _ in columns) + " |",
    ]
    for _, row in frame.iterrows():
        lines.append("| " + " | ".join(str(row[column]) for column in frame.columns) + " |")
    return "\n".join(lines)


def build_markdown_report(metrics_dir: Path, output_path: Path, title: str = "Báo cáo XSMB") -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    frequency = _read_csv(metrics_dir / "frequency.csv")
    recency = _read_csv(metrics_dir / "days_since_last_seen.csv")
    lines = [f"# {title}", "", "## Top tần suất", ""]
    lines.append("Chưa có dữ liệu tần suất." if frequency.empty else _markdown_table(frequency.head(10)))
    lines.extend(["", "## Gan số", ""])
    lines.append("Chưa có dữ liệu gan số." if recency.empty else _markdown_table(recency.head(10)))
    lines.extend(["", "## Liên kết", "", "- [Dashboard](index.html)", "- Biểu đồ tĩnh nằm trong `assets/`."])
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return output_path
