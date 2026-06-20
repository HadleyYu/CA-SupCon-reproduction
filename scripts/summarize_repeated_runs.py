#!/usr/bin/env python3
"""Summarize repeated CA-SupCon runs as mean ± standard deviation."""

import argparse
import csv
import importlib.util
from pathlib import Path

import numpy as np


DEFAULT_RATIOS = [
    "all_equal_ratio_0.2",
    "all_equal_ratio_0.1",
    "all_equal_ratio_0.05",
    "all_equal_ratio_0.02",
]

DATASET_DEFAULTS = {
    "cwru": ("Train1800_Val300_Test300", "cnn1d-cwru"),
    "te": ("train-2000_val-1000_test-1000", "cnn1d-te"),
}


def load_parser():
    script_path = Path(__file__).resolve().parent / "plot_training_log.py"
    spec = importlib.util.spec_from_file_location("plot_training_log", script_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.parse_log


def complete_runs(log_dir, parse_log, min_epochs):
    rows = []
    for log_path in sorted(Path(log_dir).glob("*.log"), key=lambda path: path.stat().st_mtime):
        metrics = parse_log(log_path)
        if metrics["test_acc"] is None:
            continue
        if len(metrics["epoch"]) < min_epochs:
            continue
        rows.append(
            {
                "log": str(log_path),
                "epochs": len(metrics["epoch"]),
                "acc": metrics["test_acc"] * 100,
                "f1": metrics["test_f1"] * 100,
                "mcc": metrics["test_mcc"] * 100,
                "best_val_acc": (metrics["best_val_acc"] or np.nan) * 100,
                "best_epoch": metrics["best_epoch"],
            }
        )
    return rows


def fmt(values):
    values = np.array(values, dtype=float)
    return "{:.2f}±{:.2f}".format(values.mean(), values.std(ddof=1) if len(values) > 1 else 0.0)


def main():
    parser = argparse.ArgumentParser(description="Summarize repeated CA-SupCon logs.")
    parser.add_argument("--dataset", choices=["cwru", "te"], required=True)
    parser.add_argument("--dataset_desc", default=None)
    parser.add_argument("--ratios", nargs="+", default=DEFAULT_RATIOS)
    parser.add_argument("--last_n", type=int, default=10, help="Use the latest N complete logs for each ratio.")
    parser.add_argument("--min_epochs", type=int, default=50)
    parser.add_argument("--output_csv", default=None)
    args = parser.parse_args()

    dataset_desc, exp_desc = DATASET_DEFAULTS[args.dataset]
    if args.dataset_desc is not None:
        dataset_desc = args.dataset_desc

    parse_log = load_parser()
    summary = []
    for ratio in args.ratios:
        log_dir = (
            Path("output")
            / args.dataset
            / dataset_desc
            / "imbalanced"
            / ratio
            / "logs"
            / "supcon"
            / "ca_supcon"
            / exp_desc
        )
        runs = complete_runs(log_dir, parse_log, args.min_epochs)
        selected = runs[-args.last_n :] if args.last_n else runs
        if not selected:
            print("{}: no complete runs in {}".format(ratio, log_dir))
            continue
        row = {
            "dataset": args.dataset,
            "dataset_desc": dataset_desc,
            "ratio": ratio.replace("all_equal_ratio_", ""),
            "runs": len(selected),
            "acc_mean": np.mean([run["acc"] for run in selected]),
            "acc_std": np.std([run["acc"] for run in selected], ddof=1) if len(selected) > 1 else 0.0,
            "f1_mean": np.mean([run["f1"] for run in selected]),
            "f1_std": np.std([run["f1"] for run in selected], ddof=1) if len(selected) > 1 else 0.0,
            "mcc_mean": np.mean([run["mcc"] for run in selected]),
            "mcc_std": np.std([run["mcc"] for run in selected], ddof=1) if len(selected) > 1 else 0.0,
            "acc": fmt([run["acc"] for run in selected]),
            "f1": fmt([run["f1"] for run in selected]),
            "mcc": fmt([run["mcc"] for run in selected]),
        }
        summary.append(row)
        print(
            "{dataset} {ratio} n={runs} | Acc {acc} | F1 {f1} | MCC {mcc}".format(
                **row
            )
        )

    if args.output_csv:
        out_path = Path(args.output_csv)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        fields = [
            "dataset",
            "dataset_desc",
            "ratio",
            "runs",
            "acc_mean",
            "acc_std",
            "f1_mean",
            "f1_std",
            "mcc_mean",
            "mcc_std",
            "acc",
            "f1",
            "mcc",
        ]
        with out_path.open("w", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields)
            writer.writeheader()
            writer.writerows(summary)
        print("CSV:", out_path)


if __name__ == "__main__":
    main()
