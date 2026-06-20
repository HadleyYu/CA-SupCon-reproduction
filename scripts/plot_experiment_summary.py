#!/usr/bin/env python3
"""Create a paper-style summary figure for CA-SupCon reproduction runs."""

import argparse
import csv
import importlib.util
import os
from pathlib import Path

if "MPLCONFIGDIR" not in os.environ:
    mpl_config_dir = Path(__file__).resolve().parents[1] / ".mplconfig"
    mpl_config_dir.mkdir(exist_ok=True)
    os.environ["MPLCONFIGDIR"] = str(mpl_config_dir)

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


RATIOS = [
    ("all_equal_ratio_0.2", "0.20"),
    ("all_equal_ratio_0.1", "0.10"),
    ("all_equal_ratio_0.05", "0.05"),
    ("all_equal_ratio_0.02", "0.02"),
]

DATASETS = [
    {
        "key": "cwru",
        "label": "CWRU",
        "root": Path("output/cwru/Train1800_Val300_Test300/imbalanced"),
        "exp": Path("logs/supcon/ca_supcon/cnn1d-cwru"),
        "classes": 10,
    },
    {
        "key": "te",
        "label": "TE",
        "root": Path("output/te/train-2000_val-1000_test-1000_random-window/imbalanced"),
        "exp": Path("logs/supcon/ca_supcon/cnn1d-te"),
        "classes": 18,
    },
]


def load_parser():
    script_path = Path(__file__).resolve().parent / "plot_training_log.py"
    spec = importlib.util.spec_from_file_location("plot_training_log", script_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.parse_log


def latest_complete_run(log_dir, parse_log):
    logs = sorted(Path(log_dir).glob("*.log"), key=lambda path: path.stat().st_mtime)
    complete = []
    for log_path in logs:
        metrics = parse_log(log_path)
        if metrics["test_acc"] is not None:
            complete.append((log_path, metrics))
    if not complete:
        raise FileNotFoundError("No complete test run found in {}".format(log_dir))
    return complete[-1]


def collect_results(parse_log):
    rows = []
    per_class = {}
    for dataset in DATASETS:
        per_class[dataset["label"]] = []
        for ratio_dir, ratio_label in RATIOS:
            log_dir = dataset["root"] / ratio_dir / dataset["exp"]
            log_path, metrics = latest_complete_run(log_dir, parse_log)
            class_acc = metrics["per_class_acc"] or []
            mean_class_acc = sum(class_acc) / len(class_acc) if class_acc else None
            min_class_acc = min(class_acc) if class_acc else None
            weak_classes = []
            if class_acc:
                weak_classes = [idx for idx, _ in sorted(enumerate(class_acc), key=lambda item: item[1])[:3]]

            rows.append(
                {
                    "dataset": dataset["label"],
                    "ratio": ratio_label,
                    "ratio_dir": ratio_dir,
                    "epochs": len(metrics["epoch"]),
                    "test_acc": metrics["test_acc"],
                    "test_f1": metrics["test_f1"],
                    "test_mcc": metrics["test_mcc"],
                    "best_val_acc": metrics["best_val_acc"],
                    "best_epoch": metrics["best_epoch"],
                    "mean_class_acc": mean_class_acc,
                    "min_class_acc": min_class_acc,
                    "weak_classes": weak_classes,
                    "log_path": str(log_path),
                }
            )
            per_class[dataset["label"]].append(class_acc)
    return rows, per_class


def write_csv(rows, out_path):
    fields = [
        "dataset",
        "ratio",
        "epochs",
        "test_acc",
        "test_f1",
        "test_mcc",
        "best_val_acc",
        "best_epoch",
        "mean_class_acc",
        "min_class_acc",
        "weak_classes",
        "log_path",
    ]
    with Path(out_path).open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            csv_row = dict(row)
            csv_row["weak_classes"] = " ".join(str(item) for item in row["weak_classes"])
            writer.writerow({field: csv_row[field] for field in fields})


def rows_for_dataset(rows, dataset):
    return [row for row in rows if row["dataset"] == dataset]


def add_metric_bars(ax, rows, title):
    x = list(range(len(rows)))
    width = 0.24
    metrics = [
        ("test_acc", "Accuracy", "#2f6b9a"),
        ("test_f1", "Macro-F1", "#6f8f3a"),
        ("test_mcc", "MCC", "#b35c44"),
    ]
    for offset, (key, label, color) in zip([-width, 0, width], metrics):
        values = [row[key] for row in rows]
        bars = ax.bar([idx + offset for idx in x], values, width=width, label=label, color=color)
        for bar, value in zip(bars, values):
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                value + 0.012,
                "{:.3f}".format(value),
                ha="center",
                va="bottom",
                fontsize=8,
            )
    ax.set_title(title, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels([row["ratio"] for row in rows])
    ax.set_xlabel("Imbalance ratio")
    ax.set_ylabel("Score")
    ax.set_ylim(0.55, 1.0)
    ax.grid(axis="y", alpha=0.25, linewidth=0.8)
    ax.legend(loc="lower left", ncols=3, fontsize=9, frameon=False)


def add_table(ax, rows):
    ax.axis("off")
    headers = ["Dataset", "Ratio", "Acc", "F1", "MCC", "Best Val", "Best Ep.", "Mean Class", "Worst Class"]
    table_rows = []
    for row in rows:
        table_rows.append(
            [
                row["dataset"],
                row["ratio"],
                "{:.3f}".format(row["test_acc"]),
                "{:.3f}".format(row["test_f1"]),
                "{:.3f}".format(row["test_mcc"]),
                "{:.3f}".format(row["best_val_acc"]),
                str(row["best_epoch"]),
                "{:.3f}".format(row["mean_class_acc"]),
                "{:.3f}".format(row["min_class_acc"]),
            ]
        )
    table = ax.table(
        cellText=table_rows,
        colLabels=headers,
        loc="center",
        cellLoc="center",
        colLoc="center",
    )
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1, 1.35)
    for (row_idx, col_idx), cell in table.get_celld().items():
        cell.set_linewidth(0.5)
        cell.set_edgecolor("#d0d0d0")
        if row_idx == 0:
            cell.set_facecolor("#2f3a45")
            cell.set_text_props(color="white", weight="bold")
        elif row_idx % 2 == 0:
            cell.set_facecolor("#f3f5f2")
        else:
            cell.set_facecolor("white")
    ax.set_title("Numerical summary from best checkpoints", fontweight="bold", pad=12)


def add_heatmap(ax, matrix, title, class_count):
    image = ax.imshow(matrix, vmin=0, vmax=1, cmap="viridis", aspect="auto")
    ax.set_title(title, fontweight="bold")
    ax.set_yticks(range(len(RATIOS)))
    ax.set_yticklabels([label for _, label in RATIOS])
    ax.set_ylabel("Imbalance ratio")
    ax.set_xticks(range(class_count))
    ax.set_xticklabels([str(idx) for idx in range(class_count)], fontsize=8)
    ax.set_xlabel("Class index")
    for y_idx, values in enumerate(matrix):
        for x_idx, value in enumerate(values):
            text_color = "white" if value < 0.45 else "#111111"
            ax.text(x_idx, y_idx, "{:.2f}".format(value), ha="center", va="center", fontsize=7, color=text_color)
    return image


def make_figure(rows, per_class, out_png, out_pdf):
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.titlepad": 8,
            "figure.dpi": 150,
        }
    )
    fig = plt.figure(figsize=(17, 12))
    grid = fig.add_gridspec(3, 2, height_ratios=[1.05, 0.9, 1.25], hspace=0.42, wspace=0.18)

    cwru_rows = rows_for_dataset(rows, "CWRU")
    te_rows = rows_for_dataset(rows, "TE")
    add_metric_bars(fig.add_subplot(grid[0, 0]), cwru_rows, "CWRU test performance")
    add_metric_bars(fig.add_subplot(grid[0, 1]), te_rows, "TE test performance")
    add_table(fig.add_subplot(grid[1, :]), rows)

    ax_cwru = fig.add_subplot(grid[2, 0])
    ax_te = fig.add_subplot(grid[2, 1])
    image_left = add_heatmap(ax_cwru, per_class["CWRU"], "CWRU per-class test accuracy", 10)
    image_right = add_heatmap(ax_te, per_class["TE"], "TE per-class test accuracy", 18)

    cbar_left = fig.colorbar(image_left, ax=ax_cwru, fraction=0.025, pad=0.015)
    cbar_left.set_label("Accuracy")
    cbar_right = fig.colorbar(image_right, ax=ax_te, fraction=0.025, pad=0.015)
    cbar_right.set_label("Accuracy")

    fig.suptitle(
        "CA-SupCon Reproduction Results on Imbalanced Fault Diagnosis",
        fontsize=18,
        fontweight="bold",
        y=0.985,
    )
    fig.text(
        0.5,
        0.955,
        "Model: CA-SupCon + 1D CNN | Metrics are evaluated on the best validation checkpoint for each run.",
        ha="center",
        fontsize=10,
        color="#444444",
    )
    fig.savefig(out_png, dpi=300, bbox_inches="tight")
    fig.savefig(out_pdf, bbox_inches="tight")
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description="Plot an all-run CA-SupCon experiment summary.")
    parser.add_argument("--output_dir", default="output", help="Directory for summary artifacts.")
    parser.add_argument("--name", default="ca_supcon_experiment_summary", help="Base output file name.")
    args = parser.parse_args()

    parse_log = load_parser()
    rows, per_class = collect_results(parse_log)

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    csv_path = output_dir / "{}.csv".format(args.name)
    png_path = output_dir / "{}.png".format(args.name)
    pdf_path = output_dir / "{}.pdf".format(args.name)

    write_csv(rows, csv_path)
    make_figure(rows, per_class, png_path, pdf_path)

    print("Summary CSV:", csv_path)
    print("Summary PNG:", png_path)
    print("Summary PDF:", pdf_path)
    for row in rows:
        print(
            "{dataset} ratio={ratio} acc={test_acc:.5f} f1={test_f1:.5f} mcc={test_mcc:.5f}".format(
                **row
            )
        )


if __name__ == "__main__":
    main()
