#!/usr/bin/env python3
"""Prepare Tennessee-Eastman data for the CA-SupCon reproduction.

Expected raw files are the Harvard Dataverse RData files from
doi:10.7910/DVN/6C3JR1. The script can download them, but the two faulty files
are large; passing an existing ``--raw_dir`` is often faster.
"""

import argparse
import shutil
import subprocess
import time
import urllib.request
from pathlib import Path

import numpy as np
import pandas as pd
import pyreadr


DATASET_DESC = "train-2000_val-1000_test-1000"
RANDOM_WINDOW_DATASET_DESC = "train-2000_val-1000_test-1000_random-window"
RATIO_COUNTS = {
    "all_equal_ratio_0.2": 400,
    "all_equal_ratio_0.1": 200,
    "all_equal_ratio_0.05": 100,
    "all_equal_ratio_0.02": 40,
}
NORMAL_TRAIN = 2000
VAL_PER_CLASS = 1000
TEST_PER_CLASS = 1000
WINDOW = 200
STEP = 1
FAULTS = list(range(1, 18))
DATAVERSE_FILES = {
    "TEP_FaultFree_Training.RData": 3031241,
    "TEP_Faulty_Training.RData": 3031242,
    "TEP_FaultFree_Testing.RData": 3031240,
    "TEP_Faulty_Testing.RData": 3031243,
}


def download_dataverse(file_id, dest, retries=3):
    if dest.exists() and dest.stat().st_size > 0:
        return
    dest.parent.mkdir(parents=True, exist_ok=True)
    url = "https://dataverse.harvard.edu/api/access/datafile/{}".format(file_id)
    tmp = dest.with_suffix(dest.suffix + ".part")
    if shutil.which("curl"):
        subprocess.run(
            [
                "curl",
                "-L",
                "--fail",
                "--retry",
                str(retries),
                "--retry-all-errors",
                "--retry-delay",
                "2",
                "-A",
                "Mozilla/5.0",
                "-o",
                str(tmp),
                url,
            ],
            check=True,
        )
        if tmp.stat().st_size == 0:
            tmp.unlink()
            raise IOError("Downloaded empty file")
        tmp.replace(dest)
        return
    for attempt in range(1, retries + 1):
        try:
            request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(request, timeout=300) as response:
                tmp.write_bytes(response.read())
            if tmp.stat().st_size == 0:
                raise IOError("Downloaded empty file")
            tmp.replace(dest)
            return
        except Exception:
            if tmp.exists():
                tmp.unlink()
            if attempt == retries:
                raise
            time.sleep(2 * attempt)


def load_rdata(path):
    result = pyreadr.read_r(str(path))
    if len(result) != 1:
        raise ValueError("Expected one object in {}".format(path))
    return next(iter(result.values()))


def feature_columns(df):
    excluded = {"faultNumber", "simulationRun", "sample"}
    return [col for col in df.columns if col not in excluded]


def collect_windows_sequential(df, fault, count, rng, train_like):
    cols = feature_columns(df)
    subset = df[df["faultNumber"] == fault]
    runs = np.array(sorted(subset["simulationRun"].unique()))
    rng.shuffle(runs)
    windows = []
    transient = 20 if train_like else 160
    for run in runs:
        run_df = subset[subset["simulationRun"] == run].sort_values("sample")
        values = run_df[cols].to_numpy(dtype=np.float32)
        if fault != 0:
            values = values[transient:]
        for start in range(0, len(values) - WINDOW + 1, STEP):
            windows.append(values[start:start + WINDOW])
            if len(windows) >= count:
                return np.stack(windows, axis=0)
    raise ValueError("Fault {} produced {} windows, need {}".format(fault, len(windows), count))


def collect_windows_random(df, fault, count, rng, train_like):
    cols = feature_columns(df)
    subset = df[df["faultNumber"] == fault]
    transient = 20 if train_like else 160
    candidates = []
    run_cache = {}

    for run, run_df in subset.groupby("simulationRun", sort=True):
        run_df = run_df.sort_values("sample")
        values = run_df[cols].to_numpy(dtype=np.float32)
        if fault != 0:
            values = values[transient:]
        max_start = len(values) - WINDOW
        if max_start < 0:
            continue
        run_cache[run] = values
        candidates.extend((run, start) for start in range(0, max_start + 1, STEP))

    if len(candidates) < count:
        raise ValueError("Fault {} produced {} windows, need {}".format(fault, len(candidates), count))

    selected = rng.choice(len(candidates), size=count, replace=False)
    windows = []
    for idx in selected:
        run, start = candidates[int(idx)]
        values = run_cache[run]
        windows.append(values[start:start + WINDOW])
    return np.stack(windows, axis=0)


def collect_windows(df, fault, count, rng, train_like, sample_strategy):
    if sample_strategy == "sequential_runs":
        return collect_windows_sequential(df, fault, count, rng, train_like)
    if sample_strategy == "random_windows":
        return collect_windows_random(df, fault, count, rng, train_like)
    raise ValueError("Unknown sample strategy {}".format(sample_strategy))


def append_labels(sequence, label):
    labels = np.full((sequence.shape[0],), label, dtype=np.int64)
    return sequence, labels


def zscore_from_train(split_dict):
    train = split_dict["train"]["sequence"]
    mean = train.reshape(-1, train.shape[-1]).mean(axis=0)
    std = train.reshape(-1, train.shape[-1]).std(axis=0)
    std[std == 0] = 1.0
    for split in split_dict.values():
        split["sequence"] = ((split["sequence"] - mean) / std).astype(np.float32)


def write_split(split_dict, out_dir):
    out_dir.mkdir(parents=True, exist_ok=True)
    zscore_from_train(split_dict)
    for split, data in split_dict.items():
        np.save(out_dir / "{}_set.npy".format(split), data)
        labels, counts = np.unique(data["label"], return_counts=True)
        print("{}: sequence={}, counts={}".format(split, data["sequence"].shape, dict(zip(labels, counts))))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output_dir", default="output")
    parser.add_argument("--raw_dir", default="data_raw/te")
    parser.add_argument("--dataset_desc", default=RANDOM_WINDOW_DATASET_DESC)
    parser.add_argument("--sample_strategy", choices=["random_windows", "sequential_runs"], default="random_windows")
    parser.add_argument("--download", action="store_true")
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--ratios", nargs="+", default=list(RATIO_COUNTS.keys()))
    args = parser.parse_args()

    raw_dir = Path(args.raw_dir)
    if args.download:
        for filename, file_id in DATAVERSE_FILES.items():
            print("Downloading {}".format(filename))
            download_dataverse(file_id, raw_dir / filename)

    required = [raw_dir / filename for filename in DATAVERSE_FILES]
    missing = [str(path) for path in required if not path.exists()]
    if missing:
        raise FileNotFoundError("Missing TE RData files: {}".format(missing))

    print("Loading RData files")
    ff_train = load_rdata(raw_dir / "TEP_FaultFree_Training.RData")
    f_train = load_rdata(raw_dir / "TEP_Faulty_Training.RData")
    ff_test = load_rdata(raw_dir / "TEP_FaultFree_Testing.RData")
    f_test = load_rdata(raw_dir / "TEP_Faulty_Testing.RData")
    train_source = pd.concat([ff_train, f_train], ignore_index=True)
    test_source = pd.concat([ff_test, f_test], ignore_index=True)

    output_root = Path(args.output_dir) / "te" / args.dataset_desc / "imbalanced"
    rng = np.random.default_rng(args.seed)
    classes = [0] + FAULTS

    for ratio in args.ratios:
        if ratio not in RATIO_COUNTS:
            raise ValueError("Unknown ratio {}. Choose from {}".format(ratio, sorted(RATIO_COUNTS)))
        split_parts = {split: {"sequence": [], "label": []} for split in ["train", "val", "test"]}
        for label in classes:
            train_count = NORMAL_TRAIN if label == 0 else RATIO_COUNTS[ratio]
            train_val_count = train_count + VAL_PER_CLASS
            train_val = collect_windows(
                train_source,
                label,
                train_val_count,
                rng,
                train_like=True,
                sample_strategy=args.sample_strategy,
            )
            test = collect_windows(
                test_source,
                label,
                TEST_PER_CLASS,
                rng,
                train_like=False,
                sample_strategy=args.sample_strategy,
            )

            train_seq, train_lab = append_labels(train_val[:train_count], label)
            val_seq, val_lab = append_labels(train_val[train_count:], label)
            test_seq, test_lab = append_labels(test, label)
            for split, seq, lab in [
                ("train", train_seq, train_lab),
                ("val", val_seq, val_lab),
                ("test", test_seq, test_lab),
            ]:
                split_parts[split]["sequence"].append(seq)
                split_parts[split]["label"].append(lab)

        split_dict = {}
        for split, parts in split_parts.items():
            sequence = np.concatenate(parts["sequence"], axis=0).astype(np.float32)
            label = np.concatenate(parts["label"], axis=0).astype(np.int64)
            order = rng.permutation(len(label))
            split_dict[split] = {"sequence": sequence[order], "label": label[order]}
        out_dir = output_root / ratio / "data"
        print("\nWriting {}".format(out_dir))
        write_split(split_dict, out_dir)


if __name__ == "__main__":
    main()
