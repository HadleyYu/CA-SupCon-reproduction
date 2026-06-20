#!/usr/bin/env python3
"""Prepare CWRU data for the CA-SupCon reproduction.

The paper uses CWRU drive-end vibration signals collected at 48 kHz under
3 hp load. This script downloads the corresponding raw .mat files and writes
the text files consumed by ``CWRUDatasetShuffle``.
"""

import argparse
import os
import shutil
import subprocess
import time
import urllib.request
from pathlib import Path

import numpy as np
from scipy.io import loadmat


DATASET_DESC = "Train1800_Val300_Test300"
RATIO_COUNTS = {
    "all_equal_ratio_0.2": 360,   # IB rate 5:1
    "all_equal_ratio_0.1": 180,   # IB rate 10:1
    "all_equal_ratio_0.05": 90,   # IB rate 20:1
    "all_equal_ratio_0.02": 36,   # IB rate 50:1
}
NORMAL_TRAIN = 1800
VAL_PER_CLASS = 300
TEST_PER_CLASS = 300
WINDOW = 400
STEP = 200


CLASS_FILES = [
    ("Normal", 0, "https://engineering.case.edu/sites/default/files/100.mat"),
    ("IR007", 1, "https://engineering.case.edu/sites/default/files/112.mat"),
    ("IR014", 2, "https://engineering.case.edu/sites/default/files/177.mat"),
    ("IR021", 3, "https://engineering.case.edu/sites/default/files/217.mat"),
    ("B007", 4, "https://engineering.case.edu/sites/default/files/125.mat"),
    ("B014", 5, "https://engineering.case.edu/sites/default/files/192.mat"),
    ("B021", 6, "https://engineering.case.edu/sites/default/files/229.mat"),
    ("OR007@6", 7, "https://engineering.case.edu/sites/default/files/138.mat"),
    ("OR014@6", 8, "https://engineering.case.edu/sites/default/files/204.mat"),
    ("OR021@6", 9, "https://engineering.case.edu/sites/default/files/241.mat"),
]


def download(url, dest, retries=20):
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists() and dest.stat().st_size > 0:
        return
    tmp = dest.with_suffix(dest.suffix + ".part")
    if shutil.which("curl"):
        # The CWRU server sometimes closes large downloads early. Keep the
        # partial file and ask curl to resume until the transfer completes.
        for attempt in range(1, retries + 1):
            result = subprocess.run(
                [
                    "curl",
                    "-L",
                    "--fail",
                    "--continue-at",
                    "-",
                    "--retry",
                    "3",
                    "--retry-all-errors",
                    "--retry-delay",
                    "2",
                    "-A",
                    "Mozilla/5.0",
                    "-o",
                    str(tmp),
                    url,
                ],
                check=False,
            )
            if result.returncode == 0 and tmp.exists() and tmp.stat().st_size > 0:
                tmp.replace(dest)
                return
            if attempt == retries:
                raise RuntimeError("Failed to download {} after {} attempts".format(url, retries))
            time.sleep(2)
    for attempt in range(1, retries + 1):
        try:
            request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(request, timeout=120) as response:
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


def extract_de_signal(mat_path):
    mat = loadmat(mat_path)
    candidates = [key for key in mat if key.endswith("_DE_time")]
    if not candidates:
        candidates = [key for key in mat if "DE_time" in key]
    if not candidates:
        raise ValueError("No drive-end signal key found in {}".format(mat_path))
    signal = np.asarray(mat[candidates[0]]).reshape(-1).astype(np.float32)
    return signal


def make_windows(signal, window=WINDOW, step=STEP):
    starts = range(0, len(signal) - window + 1, step)
    windows = np.stack([signal[start:start + window] for start in starts], axis=0)
    return windows


def split_class_windows(windows, label, train_count, rng):
    required = train_count + VAL_PER_CLASS + TEST_PER_CLASS
    if len(windows) < required:
        raise ValueError(
            "Class {} has {} windows but {} are required".format(label, len(windows), required)
        )
    order = rng.permutation(len(windows))[:required]
    selected = windows[order]
    train = selected[:train_count]
    val = selected[train_count:train_count + VAL_PER_CLASS]
    test = selected[train_count + VAL_PER_CLASS:]
    return {
        "train": append_label(train, label),
        "val": append_label(val, label),
        "test": append_label(test, label),
    }


def append_label(x, label):
    y = np.full((x.shape[0], 1), label, dtype=np.float32)
    return np.concatenate([x.astype(np.float32), y], axis=1)


def write_split(data_by_split, out_dir):
    out_dir.mkdir(parents=True, exist_ok=True)
    for split, arrays in data_by_split.items():
        data = np.concatenate(arrays, axis=0)
        np.savetxt(out_dir / "{}_set.txt".format(split), data, fmt="%.10g")
        labels, counts = np.unique(data[:, -1].astype(int), return_counts=True)
        print("{}: shape={}, counts={}".format(split, data.shape, dict(zip(labels, counts))))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output_dir", default="output")
    parser.add_argument("--raw_dir", default="data_raw/cwru")
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--ratios", nargs="+", default=list(RATIO_COUNTS.keys()))
    args = parser.parse_args()

    raw_dir = Path(args.raw_dir)
    output_root = Path(args.output_dir) / "cwru" / DATASET_DESC / "imbalanced"
    rng = np.random.default_rng(args.seed)

    windows_by_label = {}
    for name, label, url in CLASS_FILES:
        mat_path = raw_dir / "{}_{}.mat".format(label, name.replace("@", "at"))
        print("Preparing class {} ({})".format(label, name))
        download(url, mat_path)
        windows_by_label[label] = make_windows(extract_de_signal(mat_path))
        print("  windows={}".format(windows_by_label[label].shape))

    for ratio in args.ratios:
        if ratio not in RATIO_COUNTS:
            raise ValueError("Unknown ratio {}. Choose from {}".format(ratio, sorted(RATIO_COUNTS)))
        data_by_split = {"train": [], "val": [], "test": []}
        for label, windows in windows_by_label.items():
            train_count = NORMAL_TRAIN if label == 0 else RATIO_COUNTS[ratio]
            split_data = split_class_windows(windows, label, train_count, rng)
            for split in data_by_split:
                data_by_split[split].append(split_data[split])
        out_dir = output_root / ratio / "data"
        print("\nWriting {}".format(out_dir))
        write_split(data_by_split, out_dir)


if __name__ == "__main__":
    main()
