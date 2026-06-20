import argparse
import logging
import os
import random
import sys
from datetime import datetime

import numpy as np
import torch


def create_parser():
    parser = argparse.ArgumentParser(description="CA-SupCon reproduction entrypoint")
    parser.add_argument("--dataset", choices=["cwru", "te"], required=True)
    parser.add_argument("--exp_name", default="supcon")
    parser.add_argument("--cfg_name", default="casupcon")
    parser.add_argument("--data_root", default=None, help="Override DATASET.DATA_ROOT")
    parser.add_argument("--dataset_desc", default=None, help="Override DATASET_DESC")
    parser.add_argument("--output_dir", default=None, help="Override OUTPUT_DIR")
    parser.add_argument("--imb_desc", default=None, help="Override IMB_DESC, e.g. all_equal_ratio_0.02")
    parser.add_argument("--device", default=None, help="Override TRAINING_OPT.DEVICE, e.g. auto, cpu, mps, or cuda:0")
    parser.add_argument("--epochs", type=int, default=None, help="Override TRAINING_OPT.NUM_EPOCHS")
    parser.add_argument("--batch_size", type=int, default=None, help="Override DATALOADER.BATCH_SIZE")
    parser.add_argument("--num_workers", type=int, default=None, help="Override DATALOADER.NUM_WORKERS")
    parser.add_argument("--seed", type=int, default=None, help="Override SEED")
    return parser.parse_args()


def apply_cli_overrides(config, args):
    if args.data_root is not None:
        config["DATASET"]["DATA_ROOT"] = args.data_root
    if args.dataset_desc is not None:
        config["DATASET_DESC"] = args.dataset_desc
    if args.output_dir is not None:
        config["OUTPUT_DIR"] = args.output_dir
    if args.imb_desc is not None:
        config["IMB_DESC"] = args.imb_desc
    if args.device is not None:
        config["TRAINING_OPT"]["DEVICE"] = args.device
        if args.device in ["cpu", "mps"]:
            config["TRAINING_OPT"]["CUDA_VISIBLE_DEVICES"] = ""
    if args.epochs is not None:
        config["TRAINING_OPT"]["NUM_EPOCHS"] = args.epochs
    if args.batch_size is not None:
        config["DATALOADER"]["BATCH_SIZE"] = args.batch_size
    if args.num_workers is not None:
        config["DATALOADER"]["NUM_WORKERS"] = args.num_workers
    if args.seed is not None:
        config["SEED"] = args.seed
    return config


def resolve_device(requested_device):
    has_mps = hasattr(torch.backends, "mps") and torch.backends.mps.is_available()

    if requested_device is None or requested_device == "auto":
        if torch.cuda.is_available():
            return torch.device("cuda:0")
        if has_mps:
            return torch.device("mps")
        return torch.device("cpu")

    if requested_device.startswith("cuda"):
        if torch.cuda.is_available():
            return torch.device(requested_device)
        if has_mps:
            return torch.device("mps")
        return torch.device("cpu")

    if requested_device == "mps":
        if has_mps:
            return torch.device("mps")
        return torch.device("cpu")

    return torch.device(requested_device)


def empty_device_cache(device):
    if device.type == "cuda":
        torch.cuda.empty_cache()
    elif device.type == "mps" and hasattr(torch.mps, "empty_cache"):
        torch.mps.empty_cache()


def create_logger(config):
    output_dir = config["OUTPUT_DIR"]
    dataset_desc = config["DATASET_DESC"]
    balance_desc = "imbalanced/{}".format(config["IMB_DESC"]) if config["IMBALANCED"] else "balanced"
    log_dir = os.path.join(
        output_dir,
        config["DATASET_NAME"],
        dataset_desc,
        balance_desc,
        "logs",
        config["TYPE"],
        config["RUN_DESC"],
        config["EXP_DESC"],
    )
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, "{}.log".format(datetime.now().strftime("%Y%m%d_%H%M%S")))

    logger = logging.getLogger("CA-SupCon")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    logger.log_file = log_file
    logger.info("===> Log file: {}".format(log_file))
    return logger


def seed_everything(logger, seed):
    random.seed(seed)
    os.environ["PYTHONHASHSEED"] = str(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False
    logger.info("===> Random seed fixed as {}".format(seed))


def total_acc_cal(preds, labels):
    preds = preds.detach().cpu()
    labels = labels.detach().cpu()
    correct_num = int((preds == labels).sum().item())
    total_num = int(labels.numel())
    accuracy = correct_num / total_num if total_num else 0.0
    return {"correct_num": correct_num, "total_num": total_num, "accuracy": accuracy}


def each_cls_acc_cal(preds, labels):
    preds = preds.detach().cpu().numpy()
    labels = labels.detach().cpu().numpy()
    classes = np.unique(labels)
    class_accs = []
    per_cls_correct = []
    per_cls_num = []
    for cls in classes:
        mask = labels == cls
        total = int(mask.sum())
        correct = int((preds[mask] == cls).sum())
        per_cls_num.append(total)
        per_cls_correct.append(correct)
        class_accs.append(correct / total if total else 0.0)
    return {
        "class_accs": class_accs,
        "per_cls_correct": per_cls_correct,
        "per_cls_num": per_cls_num,
    }


def classification_metrics(preds, labels, num_classes=None):
    preds = preds.detach().cpu().numpy().astype(int)
    labels = labels.detach().cpu().numpy().astype(int)
    if num_classes is None:
        num_classes = int(max(labels.max(), preds.max()) + 1) if labels.size else 0

    confusion = np.zeros((num_classes, num_classes), dtype=np.int64)
    for y_true, y_pred in zip(labels, preds):
        if 0 <= y_true < num_classes and 0 <= y_pred < num_classes:
            confusion[y_true, y_pred] += 1

    f1_scores = []
    for cls in range(num_classes):
        tp = confusion[cls, cls]
        fp = confusion[:, cls].sum() - tp
        fn = confusion[cls, :].sum() - tp
        denom = 2 * tp + fp + fn
        f1_scores.append((2 * tp / denom) if denom else 0.0)

    c = np.trace(confusion)
    s = confusion.sum()
    pk = confusion.sum(axis=0)
    tk = confusion.sum(axis=1)
    numerator = c * s - np.sum(pk * tk)
    denominator = np.sqrt((s ** 2 - np.sum(pk ** 2)) * (s ** 2 - np.sum(tk ** 2)))
    mcc = numerator / denominator if denominator else 0.0
    accuracy = c / s if s else 0.0
    return {"accuracy": accuracy, "macro_f1": float(np.mean(f1_scores)), "mcc": float(mcc)}


class Compose:
    def __init__(self, transforms):
        self.transforms = transforms

    def __call__(self, x):
        out = x.clone()
        for transform in self.transforms:
            out = transform(out)
        return out


class _RandomTransform:
    def __init__(self, params):
        self.p = float(params.get("p", 0.5))

    def should_apply(self):
        return random.random() < self.p


class Jitter(_RandomTransform):
    def __init__(self, params):
        super().__init__(params)
        self.sigma = float(params.get("sigma", 0.05))

    def __call__(self, x):
        if not self.should_apply():
            return x
        return x + torch.randn_like(x) * self.sigma


class Scaling(_RandomTransform):
    def __init__(self, params):
        super().__init__(params)
        self.sigma = float(params.get("sigma", 0.05))

    def __call__(self, x):
        if not self.should_apply():
            return x
        scale_shape = [x.shape[0]] + [1] * (x.dim() - 1)
        scale = torch.normal(mean=1.0, std=self.sigma, size=scale_shape, dtype=x.dtype)
        return x * scale.to(x.device)


class MakeNoise(_RandomTransform):
    def __init__(self, params):
        super().__init__(params)
        self.sigma = float(params.get("sigma", 0.1))

    def __call__(self, x):
        if not self.should_apply():
            return x
        keep_mask = (torch.rand_like(x) > self.sigma).to(dtype=x.dtype)
        return x * keep_mask


class Translation(_RandomTransform):
    def __call__(self, x):
        if not self.should_apply():
            return x
        length = x.shape[-1]
        if length <= 1:
            return x
        shift = random.randint(0, length - 1)
        return torch.roll(x, shifts=-shift, dims=-1)
