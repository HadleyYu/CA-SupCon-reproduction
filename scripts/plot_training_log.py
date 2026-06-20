#!/usr/bin/env python3
"""Plot CA-SupCon training metrics from a log file."""

import argparse
import ast
import os
import re
from pathlib import Path

if "MPLCONFIGDIR" not in os.environ:
    mpl_config_dir = Path(__file__).resolve().parents[1] / ".mplconfig"
    mpl_config_dir.mkdir(exist_ok=True)
    os.environ["MPLCONFIGDIR"] = str(mpl_config_dir)

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


def latest_log(log_dir):
    logs = sorted(Path(log_dir).glob("*.log"), key=lambda p: p.stat().st_mtime)
    if not logs:
        raise FileNotFoundError("No .log files found in {}".format(log_dir))
    return logs[-1]


def parse_log(path):
    metrics = {
        "epoch": [],
        "train_loss": [],
        "train_sup_loss": [],
        "train_ce_loss": [],
        "train_acc": [],
        "val_loss": [],
        "val_acc": [],
        "val_f1": [],
        "val_mcc": [],
        "test_loss": None,
        "test_num": None,
        "acc_test_num": None,
        "test_acc": None,
        "test_f1": None,
        "test_mcc": None,
        "best_val_acc": None,
        "best_epoch": None,
        "per_class_acc": None,
        "per_class_correct": None,
        "per_class_total": None,
    }
    current_epoch = 0
    epoch_re = re.compile(r"Epoch: \[(\d+)/(\d+)\]")
    train_re = re.compile(
        r"TrainLoss: ([0-9.]+)\s+TrainSupLoss: ([0-9.]+)\s+TrainCeLoss: ([0-9.]+).*TrainAcc: ([0-9.]+)"
    )
    val_re = re.compile(r"ValLoss: ([0-9.]+).*ValAcc: ([0-9.]+)\s+ValF1: ([0-9.]+)\s+ValMCC: ([0-9.]+)")
    test_re = re.compile(
        r"TestLoss: ([0-9.]+)\s+TestNum: (\d+)\s+AccTestNum: (\d+)\s+TestAcc: ([0-9.]+)\s+TestF1: ([0-9.]+)\s+TestMCC: ([0-9.]+)"
    )
    best_re = re.compile(r"Best validation accuracy is ([0-9.]+) at epoch (\d+)")
    per_cls_re = re.compile(r"Per class accuracy: (\[.*\])")
    per_cls_correct_re = re.compile(r"Per class acc_Nums: (\[.*\])")
    per_cls_total_re = re.compile(r"Per class totalNum: (\[.*\])")

    for line in Path(path).read_text(errors="ignore").splitlines():
        epoch_match = epoch_re.search(line)
        if epoch_match:
            current_epoch = int(epoch_match.group(1))
            continue
        train_match = train_re.search(line)
        if train_match:
            metrics["epoch"].append(current_epoch or len(metrics["epoch"]) + 1)
            metrics["train_loss"].append(float(train_match.group(1)))
            metrics["train_sup_loss"].append(float(train_match.group(2)))
            metrics["train_ce_loss"].append(float(train_match.group(3)))
            metrics["train_acc"].append(float(train_match.group(4)))
            continue
        val_match = val_re.search(line)
        if val_match and len(metrics["val_acc"]) < len(metrics["epoch"]):
            metrics["val_loss"].append(float(val_match.group(1)))
            metrics["val_acc"].append(float(val_match.group(2)))
            metrics["val_f1"].append(float(val_match.group(3)))
            metrics["val_mcc"].append(float(val_match.group(4)))
            continue
        test_match = test_re.search(line)
        if test_match:
            metrics["test_loss"] = float(test_match.group(1))
            metrics["test_num"] = int(test_match.group(2))
            metrics["acc_test_num"] = int(test_match.group(3))
            metrics["test_acc"] = float(test_match.group(4))
            metrics["test_f1"] = float(test_match.group(5))
            metrics["test_mcc"] = float(test_match.group(6))
            continue
        best_match = best_re.search(line)
        if best_match:
            metrics["best_val_acc"] = float(best_match.group(1))
            metrics["best_epoch"] = int(best_match.group(2))
            continue
        per_cls_match = per_cls_re.search(line)
        if per_cls_match:
            metrics["per_class_acc"] = ast.literal_eval(per_cls_match.group(1))
            continue
        per_cls_correct_match = per_cls_correct_re.search(line)
        if per_cls_correct_match:
            metrics["per_class_correct"] = ast.literal_eval(per_cls_correct_match.group(1))
            continue
        per_cls_total_match = per_cls_total_re.search(line)
        if per_cls_total_match:
            metrics["per_class_total"] = ast.literal_eval(per_cls_total_match.group(1))
    return metrics


def plot_summary(metrics, out_path, title):
    fig, axes = plt.subplots(2, 2, figsize=(13, 9))
    fig.suptitle(title)
    epochs = metrics["epoch"]

    axes[0, 0].plot(epochs, metrics["train_loss"], marker="o", label="Train total")
    axes[0, 0].plot(epochs, metrics["train_sup_loss"], marker="o", label="Train SupCon")
    axes[0, 0].plot(epochs, metrics["train_ce_loss"], marker="o", label="Train CE")
    axes[0, 0].set_title("Loss")
    axes[0, 0].set_xlabel("Epoch")
    axes[0, 0].legend()
    axes[0, 0].grid(alpha=0.3)

    axes[0, 1].plot(epochs, metrics["train_acc"], marker="o", label="Train Acc")
    axes[0, 1].plot(epochs[: len(metrics["val_acc"])], metrics["val_acc"], marker="o", label="Val Acc")
    axes[0, 1].set_title("Accuracy")
    axes[0, 1].set_xlabel("Epoch")
    axes[0, 1].set_ylim(0, 1.05)
    axes[0, 1].legend()
    axes[0, 1].grid(alpha=0.3)

    axes[1, 0].plot(epochs[: len(metrics["val_f1"])], metrics["val_f1"], marker="o", label="Val macro-F1")
    axes[1, 0].plot(epochs[: len(metrics["val_mcc"])], metrics["val_mcc"], marker="o", label="Val MCC")
    axes[1, 0].set_title("Validation F1 / MCC")
    axes[1, 0].set_xlabel("Epoch")
    axes[1, 0].set_ylim(0, 1.05)
    axes[1, 0].legend()
    axes[1, 0].grid(alpha=0.3)

    test_values = [metrics["test_acc"], metrics["test_f1"], metrics["test_mcc"]]
    if all(value is not None for value in test_values):
        axes[1, 1].bar(["Test Acc", "Test F1", "Test MCC"], test_values, color=["#3973b7", "#5a9f62", "#b77939"])
        for idx, value in enumerate(test_values):
            axes[1, 1].text(idx, value + 0.02, "{:.3f}".format(value), ha="center")
    axes[1, 1].set_title("Final Test Metrics")
    axes[1, 1].set_ylim(0, 1.05)
    axes[1, 1].grid(axis="y", alpha=0.3)

    fig.tight_layout()
    fig.savefig(out_path, dpi=180)
    plt.close(fig)


def plot_per_class(metrics, out_path, title):
    per_class = metrics["per_class_acc"]
    if per_class is None:
        return None
    labels = ["class {}".format(i) for i in range(len(per_class))]
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.bar(labels, per_class, color="#3973b7")
    ax.set_ylim(0, 1.05)
    ax.set_ylabel("Accuracy")
    ax.set_title(title)
    ax.grid(axis="y", alpha=0.3)
    for idx, value in enumerate(per_class):
        ax.text(idx, value + 0.02, "{:.2f}".format(value), ha="center", fontsize=8)
    fig.tight_layout()
    fig.savefig(out_path, dpi=180)
    plt.close(fig)
    return out_path


def plot_detailed_report(metrics, out_path, title):
    epochs = metrics["epoch"]
    fig = plt.figure(figsize=(16, 12), constrained_layout=True)
    grid = fig.add_gridspec(3, 3, height_ratios=[0.8, 1.25, 1.25])

    ax_summary = fig.add_subplot(grid[0, :])
    ax_summary.axis("off")
    per_class = metrics["per_class_acc"] or []
    if per_class:
        weakest = sorted(enumerate(per_class), key=lambda item: item[1])[:3]
        strongest = sorted(enumerate(per_class), key=lambda item: item[1], reverse=True)[:3]
        weakest_text = ", ".join(["class {}={:.1f}%".format(idx, value * 100) for idx, value in weakest])
        strongest_text = ", ".join(["class {}={:.1f}%".format(idx, value * 100) for idx, value in strongest])
        mean_class_acc = sum(per_class) / len(per_class)
    else:
        weakest_text = "N/A"
        strongest_text = "N/A"
        mean_class_acc = None
    if metrics["best_epoch"] and metrics["val_acc"] and metrics["best_epoch"] <= len(metrics["val_acc"]):
        best_epoch = metrics["best_epoch"]
        best_val_acc = metrics["val_acc"][best_epoch - 1]
    elif metrics["val_acc"]:
        best_val_acc = max(metrics["val_acc"])
        best_epoch = epochs[metrics["val_acc"].index(best_val_acc)]
    else:
        best_val_acc = metrics["best_val_acc"] or 0
        best_epoch = metrics["best_epoch"] or 0

    summary_lines = [
        title,
        "Epochs: {} | Best Val Acc: {:.2f}% at epoch {} | Final Test: Acc {:.2f}%, Macro-F1 {:.2f}%, MCC {:.2f}%".format(
            len(epochs),
            best_val_acc * 100,
            best_epoch,
            (metrics["test_acc"] or 0) * 100,
            (metrics["test_f1"] or 0) * 100,
            (metrics["test_mcc"] or 0) * 100,
        ),
        "Test samples: {}/{} correct | Test loss: {:.5f} | Mean per-class Acc: {}".format(
            metrics["acc_test_num"] if metrics["acc_test_num"] is not None else "N/A",
            metrics["test_num"] if metrics["test_num"] is not None else "N/A",
            metrics["test_loss"] if metrics["test_loss"] is not None else 0,
            "{:.2f}%".format(mean_class_acc * 100) if mean_class_acc is not None else "N/A",
        ),
        "Strong classes: {} | Weak classes: {}".format(strongest_text, weakest_text),
    ]
    ax_summary.text(
        0.01,
        0.94,
        "\n".join(summary_lines),
        va="top",
        ha="left",
        fontsize=12,
        linespacing=1.55,
        bbox={"boxstyle": "round,pad=0.6", "facecolor": "#f7f7f4", "edgecolor": "#d8d8d0"},
    )

    ax_loss = fig.add_subplot(grid[1, 0])
    ax_loss.plot(epochs, metrics["train_loss"], color="#386cb0", label="Train total loss")
    ax_loss.plot(epochs, metrics["train_sup_loss"], color="#7b3294", label="Train SupCon loss")
    if metrics["val_loss"]:
        ax_loss.plot(epochs[: len(metrics["val_loss"])], metrics["val_loss"], color="#bf812d", label="Val CE loss")
    ax_loss.set_title("Loss trend")
    ax_loss.set_xlabel("Epoch")
    ax_loss.set_ylabel("Loss")
    ax_loss.grid(alpha=0.3)
    ax_loss.legend(fontsize=8)

    ax_ce = fig.add_subplot(grid[1, 1])
    ax_ce.plot(epochs, metrics["train_ce_loss"], color="#018571", label="Train CE loss")
    ax_ce.set_title("Classifier loss detail")
    ax_ce.set_xlabel("Epoch")
    ax_ce.set_ylabel("CE loss")
    ax_ce.grid(alpha=0.3)
    ax_ce.legend(fontsize=8)

    ax_acc = fig.add_subplot(grid[1, 2])
    ax_acc.plot(epochs, metrics["train_acc"], color="#5e3c99", label="Train Acc")
    ax_acc.plot(epochs[: len(metrics["val_acc"])], metrics["val_acc"], color="#e66101", label="Val Acc")
    ax_acc.plot(epochs[: len(metrics["val_f1"])], metrics["val_f1"], color="#1b9e77", label="Val Macro-F1")
    ax_acc.plot(epochs[: len(metrics["val_mcc"])], metrics["val_mcc"], color="#7570b3", label="Val MCC")
    if metrics["best_epoch"] is not None:
        ax_acc.axvline(metrics["best_epoch"], color="#555555", linestyle="--", linewidth=1)
        ax_acc.text(metrics["best_epoch"], 0.05, "best epoch", rotation=90, va="bottom", ha="right", fontsize=8)
    ax_acc.set_title("Accuracy / F1 / MCC")
    ax_acc.set_xlabel("Epoch")
    ax_acc.set_ylim(0, 1.05)
    ax_acc.grid(alpha=0.3)
    ax_acc.legend(fontsize=8)

    ax_test = fig.add_subplot(grid[2, 0])
    test_labels = ["Acc", "Macro-F1", "MCC"]
    test_values = [metrics["test_acc"], metrics["test_f1"], metrics["test_mcc"]]
    colors = ["#386cb0", "#1b9e77", "#7570b3"]
    if all(value is not None for value in test_values):
        bars = ax_test.bar(test_labels, test_values, color=colors)
        for bar, value in zip(bars, test_values):
            ax_test.text(bar.get_x() + bar.get_width() / 2, value + 0.02, "{:.2f}%".format(value * 100), ha="center")
    ax_test.set_title("Final test metrics")
    ax_test.set_ylim(0, 1.05)
    ax_test.grid(axis="y", alpha=0.3)

    ax_class = fig.add_subplot(grid[2, 1])
    if per_class:
        class_labels = ["C{}".format(i) for i in range(len(per_class))]
        class_colors = [
            "#b2182b" if value < 0.7 else "#ef8a62" if value < 0.85 else "#67a9cf" if value < 0.9 else "#2166ac"
            for value in per_class
        ]
        bars = ax_class.bar(class_labels, per_class, color=class_colors)
        for idx, (bar, value) in enumerate(zip(bars, per_class)):
            ax_class.text(bar.get_x() + bar.get_width() / 2, value + 0.015, "{:.1f}".format(value * 100), ha="center", fontsize=8)
    ax_class.set_title("Per-class accuracy")
    ax_class.set_ylim(0, 1.05)
    ax_class.set_ylabel("Accuracy")
    ax_class.grid(axis="y", alpha=0.3)

    ax_counts = fig.add_subplot(grid[2, 2])
    correct = metrics["per_class_correct"]
    total = metrics["per_class_total"]
    if correct and total:
        class_labels = ["C{}".format(i) for i in range(len(correct))]
        wrong = [max(t - c, 0) for c, t in zip(correct, total)]
        ax_counts.bar(class_labels, correct, color="#4daf4a", label="Correct")
        ax_counts.bar(class_labels, wrong, bottom=correct, color="#d95f02", label="Wrong")
        for idx, (c, t) in enumerate(zip(correct, total)):
            ax_counts.text(idx, t + max(total) * 0.015, "{}/{}".format(c, t), ha="center", fontsize=7, rotation=45)
        ax_counts.set_ylim(0, max(total) * 1.15)
    ax_counts.set_title("Per-class correct / total")
    ax_counts.set_ylabel("Samples")
    ax_counts.grid(axis="y", alpha=0.3)
    ax_counts.legend(fontsize=8)

    fig.savefig(out_path, dpi=180)
    plt.close(fig)
    return out_path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--log_file", default=None)
    parser.add_argument("--log_dir", default=None)
    parser.add_argument("--out_dir", default=None)
    args = parser.parse_args()

    if args.log_file is None and args.log_dir is None:
        raise ValueError("Provide --log_file or --log_dir")
    log_file = Path(args.log_file) if args.log_file else latest_log(args.log_dir)
    out_dir = Path(args.out_dir) if args.out_dir else log_file.parent / "figures"
    out_dir.mkdir(parents=True, exist_ok=True)

    metrics = parse_log(log_file)
    summary_path = out_dir / "{}_summary.png".format(log_file.stem)
    per_class_path = out_dir / "{}_per_class.png".format(log_file.stem)
    detailed_path = out_dir / "{}_detailed_report.png".format(log_file.stem)
    plot_summary(metrics, summary_path, "CA-SupCon metrics from {}".format(log_file.name))
    plotted_per_class = plot_per_class(metrics, per_class_path, "Per-class accuracy from {}".format(log_file.name))
    plot_detailed_report(metrics, detailed_path, "CA-SupCon detailed report from {}".format(log_file.name))

    print("Log file: {}".format(log_file))
    print("Summary figure: {}".format(summary_path))
    if plotted_per_class:
        print("Per-class figure: {}".format(plotted_per_class))
    print("Detailed report: {}".format(detailed_path))
    if metrics["test_acc"] is not None:
        print("TestAcc={:.5f}, TestF1={:.5f}, TestMCC={:.5f}".format(metrics["test_acc"], metrics["test_f1"], metrics["test_mcc"]))


if __name__ == "__main__":
    main()
