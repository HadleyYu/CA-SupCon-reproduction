#!/usr/bin/env python3
"""Run CA-SupCon experiments over multiple random seeds."""

import argparse
import subprocess
import sys


DEFAULT_RATIOS = [
    "all_equal_ratio_0.2",
    "all_equal_ratio_0.1",
    "all_equal_ratio_0.05",
    "all_equal_ratio_0.02",
]


def main():
    parser = argparse.ArgumentParser(description="Run a dataset/ratio sweep over multiple seeds.")
    parser.add_argument("--dataset", choices=["cwru", "te"], required=True)
    parser.add_argument("--dataset_desc", default=None)
    parser.add_argument("--ratios", nargs="+", default=DEFAULT_RATIOS)
    parser.add_argument("--seeds", nargs="+", type=int, default=list(range(10)))
    parser.add_argument("--device", default="mps")
    parser.add_argument("--epochs", type=int, default=None)
    parser.add_argument("--batch_size", type=int, default=None)
    parser.add_argument("--num_workers", type=int, default=None)
    parser.add_argument("--dry_run", action="store_true")
    args = parser.parse_args()

    for ratio in args.ratios:
        for seed in args.seeds:
            cmd = [
                sys.executable,
                "main/main.py",
                "--dataset",
                args.dataset,
                "--exp_name",
                "supcon",
                "--cfg_name",
                "casupcon",
                "--imb_desc",
                ratio,
                "--seed",
                str(seed),
                "--device",
                args.device,
            ]
            if args.dataset_desc:
                cmd.extend(["--dataset_desc", args.dataset_desc])
            if args.epochs is not None:
                cmd.extend(["--epochs", str(args.epochs)])
            if args.batch_size is not None:
                cmd.extend(["--batch_size", str(args.batch_size)])
            if args.num_workers is not None:
                cmd.extend(["--num_workers", str(args.num_workers)])

            print("\n==>", " ".join(cmd), flush=True)
            if not args.dry_run:
                subprocess.run(cmd, check=True)


if __name__ == "__main__":
    main()
