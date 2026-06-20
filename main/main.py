import _init_paths
from utils import seed_everything, create_parser, create_logger, apply_cli_overrides
from dataprep import *
from dataloader import load_data
from core import *

import yaml
import os
import numpy as np
from pathlib import Path


def plot_current_run(logger):
    import importlib.util

    log_file = Path(logger.log_file)
    plot_script = Path(__file__).resolve().parents[1] / "scripts" / "plot_training_log.py"
    spec = importlib.util.spec_from_file_location("plot_training_log", plot_script)
    plot_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(plot_module)

    out_dir = log_file.parent / "figures"
    out_dir.mkdir(parents=True, exist_ok=True)

    metrics = plot_module.parse_log(log_file)
    summary_path = out_dir / "{}_summary.png".format(log_file.stem)
    per_class_path = out_dir / "{}_per_class.png".format(log_file.stem)
    detailed_path = out_dir / "{}_detailed_report.png".format(log_file.stem)

    plot_module.plot_summary(metrics, summary_path, "CA-SupCon metrics from {}".format(log_file.name))
    plotted_per_class = plot_module.plot_per_class(
        metrics,
        per_class_path,
        "Per-class accuracy from {}".format(log_file.name),
    )
    plot_module.plot_detailed_report(
        metrics,
        detailed_path,
        "CA-SupCon detailed report from {}".format(log_file.name),
    )

    logger.info("===> Summary figure is saved at {}".format(summary_path))
    if plotted_per_class:
        logger.info("===> Per-class figure is saved at {}".format(plotted_per_class))
    logger.info("===> Detailed report is saved at {}".format(detailed_path))


def main():
    args = create_parser()  # argument from command line
    
    cfg_name = "{}.yaml".format(args.cfg_name)
    cfg_path = os.path.join("configs", args.dataset, args.exp_name, cfg_name)

    # load configuration file
    with open(cfg_path) as f:
        config = yaml.load(f, Loader = yaml.FullLoader)
    config = apply_cli_overrides(config, args)

    logger = create_logger(config)  # create logger

    seed_everything(logger, config["SEED"])  # fix random seed

    splits = config["DATASET"]["SPLITS"]        

    os.environ['CUDA_VISIBLE_DEVICES'] = config["TRAINING_OPT"]["CUDA_VISIBLE_DEVICES"]
    logger.info("===> CUDA_VISIBLE_DEVICES: {}".format(config["TRAINING_OPT"]["CUDA_VISIBLE_DEVICES"]))

    dataloader_dict = {split: load_data(config, logger, phase = split) for split in splits}

    model = Model_SupCon(config, dataloader_dict, logger)
    if (config["MODE"] in ["train_supcon", "train_linear", "fine_tune"]):
        model.train()
    elif (config["MODE"] == "test"):
        model.eval_ce("test", True)

    for handler in logger.handlers:
        handler.flush()
    plot_current_run(logger)
        
    print("\ndone!")


if __name__ == '__main__':
    main()
