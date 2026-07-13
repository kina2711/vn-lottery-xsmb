from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd


def create_frequency_chart(frequency_csv: Path, output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    frame = pd.read_csv(frequency_csv)
    top = frame.head(20)
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(top["number"].astype(str), top["count"])
    ax.set_title("Top number frequency")
    ax.set_xlabel("Number")
    ax.set_ylabel("Count")
    fig.tight_layout()
    fig.savefig(output_path)
    plt.close(fig)
    return output_path


def create_histogram_chart(histogram_csv: Path, output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    frame = pd.read_csv(histogram_csv)
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(frame["count"].astype(str), frame["number_total"])
    ax.set_title("Frequency histogram")
    ax.set_xlabel("Frequency count")
    ax.set_ylabel("Number total")
    fig.tight_layout()
    fig.savefig(output_path)
    plt.close(fig)
    return output_path


def create_static_charts(metrics_dir: Path, assets_dir: Path) -> dict[str, Path]:
    return {
        "frequency": create_frequency_chart(metrics_dir / "frequency.csv", assets_dir / "frequency.png"),
        "histogram": create_histogram_chart(metrics_dir / "histogram.csv", assets_dir / "histogram.png"),
    }
