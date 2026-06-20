# CA-SupCon 论文复现工程

本目录复现论文 **A class-aware supervised contrastive learning framework for imbalanced fault diagnosis**, Knowledge-Based Systems 252 (2022) 109437。

官方论文代码仓库只包含核心训练代码，缺少 `utils`、`dataprep`、依赖清单和数据预处理脚本；本复现工程在保留核心网络、SupCon 损失、class-aware sampler 与 YAML 超参的基础上，补齐了可运行所需的工程文件。

## 1. 环境

建议使用 Python 3.9-3.11：

```bash
cd /Users/hadley/Desktop/UESTC/CA-SupCon
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

如果没有 GPU，可用 `--device cpu` 跑通流程；论文结果使用 RTX 2080 GPU、Python 3.7、PyTorch 1.10。

只检查代码是否能跑通时，可以生成很小的 synthetic smoke data。注意它不是论文数据，不能用于报告论文结果：

```bash
python scripts/make_smoke_data.py --dataset cwru
python main/main.py --dataset cwru --exp_name supcon --cfg_name casupcon --imb_desc smoke --epochs 1 --device cpu
```

## 2. 生成数据

### CWRU

自动下载论文指定的 Case Western Reserve University 48 kHz、3 hp、drive-end 原始 `.mat` 文件，并生成 4 个不平衡率的数据集：

```bash
python scripts/prepare_cwru.py
```

输出位置：

```text
output/cwru/Train1800_Val300_Test300/imbalanced/all_equal_ratio_0.2/data
output/cwru/Train1800_Val300_Test300/imbalanced/all_equal_ratio_0.1/data
output/cwru/Train1800_Val300_Test300/imbalanced/all_equal_ratio_0.05/data
output/cwru/Train1800_Val300_Test300/imbalanced/all_equal_ratio_0.02/data
```

对应论文中的 IB rate 分别是 5:1、10:1、20:1、50:1。

### TE

TE 数据来自 Harvard Dataverse DOI `10.7910/DVN/6C3JR1`。可自动下载，但 faulty 文件较大：

```bash
python scripts/prepare_te.py --download
```

也可以手动下载以下文件到 `data_raw/te/` 后再运行：

```text
TEP_FaultFree_Training.RData
TEP_Faulty_Training.RData
TEP_FaultFree_Testing.RData
TEP_Faulty_Testing.RData
```

```bash
python scripts/prepare_te.py
```

## 3. 训练

CWRU 复现：

```bash
python main/main.py --dataset cwru --exp_name supcon --cfg_name casupcon --imb_desc all_equal_ratio_0.2
python main/main.py --dataset cwru --exp_name supcon --cfg_name casupcon --imb_desc all_equal_ratio_0.1
python main/main.py --dataset cwru --exp_name supcon --cfg_name casupcon --imb_desc all_equal_ratio_0.05
python main/main.py --dataset cwru --exp_name supcon --cfg_name casupcon --imb_desc all_equal_ratio_0.02
```

TE 复现：

```bash
python main/main.py --dataset te --exp_name supcon --cfg_name casupcon --imb_desc all_equal_ratio_0.2
python main/main.py --dataset te --exp_name supcon --cfg_name casupcon --imb_desc all_equal_ratio_0.1
python main/main.py --dataset te --exp_name supcon --cfg_name casupcon --imb_desc all_equal_ratio_0.05
python main/main.py --dataset te --exp_name supcon --cfg_name casupcon --imb_desc all_equal_ratio_0.02
```

输出模型和日志在 `output/` 下。论文报告的是每种设置重复 10 次的均值和标准差；严格对齐时应改 seed 跑 10 次并汇总测试集 Acc、F1、MCC。

## 4. 详细说明

小白入门说明，包括故障诊断、混淆矩阵、Acc、Precision、Recall、macro-F1、MCC：

```text
docs/01_beginner_guide.md
```

完整论文说明、代码结构、数据构造和严谨性备注见：

```text
docs/04_reproduction_notes.md
```
