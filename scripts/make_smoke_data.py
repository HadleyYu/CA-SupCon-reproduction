#!/usr/bin/env python3
"""Create tiny synthetic datasets for code smoke tests.

These files are not paper data and must not be used for reporting results.
They only verify that dataloading, sampling, training, metrics, and checkpoint
writing work end to end.
"""

import argparse
from pathlib import Path

import numpy as np


def make_cwru(output_dir, seed):
    rng = np.random.default_rng(seed)
    root = Path(output_dir) / "cwru" / "Train1800_Val300_Test300" / "imbalanced" / "smoke" / "data"
    root.mkdir(parents=True, exist_ok=True)
    counts = {"train": [60] + [12] * 9, "val": [10] * 10, "test": [10] * 10}
    for split, per_class in counts.items():
        rows = []
        for label, count in enumerate(per_class):
            base = np.sin(np.linspace(0, np.pi * (label + 1), 400, dtype=np.float32))
            noise = rng.normal(0, 0.1, size=(count, 400)).astype(np.float32)
            x = base[None, :] + noise + label * 0.05
            y = np.full((count, 1), label, dtype=np.float32)
            rows.append(np.concatenate([x, y], axis=1))
        data = np.concatenate(rows, axis=0)
        rng.shuffle(data)
        np.savetxt(root / "{}_set.txt".format(split), data, fmt="%.8g")
    print("Wrote synthetic CWRU smoke data to {}".format(root))


def make_te(output_dir, seed):
    rng = np.random.default_rng(seed)
    root = Path(output_dir) / "te" / "train-2000_val-1000_test-1000" / "imbalanced" / "smoke" / "data"
    root.mkdir(parents=True, exist_ok=True)
    counts = {"train": [72] + [8] * 17, "val": [10] * 18, "test": [10] * 18}
    for split, per_class in counts.items():
        sequences = []
        labels = []
        t = np.linspace(0, 1, 200, dtype=np.float32)
        for label, count in enumerate(per_class):
            pattern = np.stack(
                [np.sin(2 * np.pi * (label + 1) * t / (dim + 1)) for dim in range(52)],
                axis=1,
            )
            noise = rng.normal(0, 0.1, size=(count, 200, 52)).astype(np.float32)
            x = pattern[None, :, :] + noise + label * 0.02
            sequences.append(x.astype(np.float32))
            labels.append(np.full((count,), label, dtype=np.int64))
        sequence = np.concatenate(sequences, axis=0)
        label = np.concatenate(labels, axis=0)
        order = rng.permutation(len(label))
        np.save(root / "{}_set.npy".format(split), {"sequence": sequence[order], "label": label[order]})
    print("Wrote synthetic TE smoke data to {}".format(root))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", choices=["cwru", "te", "both"], default="both")
    parser.add_argument("--output_dir", default="output")
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()

    if args.dataset in ["cwru", "both"]:
        make_cwru(args.output_dir, args.seed)
    if args.dataset in ["te", "both"]:
        make_te(args.output_dir, args.seed)


if __name__ == "__main__":
    main()
