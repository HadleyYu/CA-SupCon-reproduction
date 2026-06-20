# CA-SupCon 论文复现实验结果报告

生成日期：2026-06-20  
项目路径：`/Users/hadley/Desktop/UESTC/CA-SupCon`  
复现论文：A class-aware supervised contrastive learning framework for imbalanced fault diagnosis, Knowledge-Based Systems, 2022

---

## 1. 报告摘要

本报告总结当前项目对 CA-SupCon 论文的复现过程、实验设置、代码实现、最终结果，以及与原论文结果的对比。

当前复现已经完成：

```text
CWRU: 4 个不平衡比例 x 10 seeds x 50 epochs
TE:   4 个不平衡比例 x 10 seeds x 50 epochs
```

核心结论：

```text
1. CWRU 四个不平衡比例均超过论文 CA-SupCon 报告结果。
2. TE random-window 版本整体接近论文水平。
3. TE 的 0.20 和 0.02 超过论文，0.10 和 0.05 略低于论文。
4. TE 的类别 9、15，以及极端不平衡下的类别 3，是当前最明显的弱识别类别。
5. 当前新增代码主要服务于数据准备、设备适配、日志解析、结果汇总和图示输出，不改变 CA-SupCon 核心方法。
```

---

## 2. 复现目标

原论文研究的是不平衡故障诊断问题，即正常类样本充足，而多个故障类样本显著不足。

CA-SupCon 的核心方法包括：

```text
1. Cross Entropy 分类分支
2. Supervised Contrastive Learning 对比学习分支
3. Class-aware sampler 类别感知采样器
```

总损失为：

```text
L = lambda * LSupCon + LCE
```

论文最优设置中：

```text
lambda = 1
CWRU SupCon temperature = 0.1
TE SupCon temperature = 0.2
```

本项目复现目标是：

```text
在 CWRU 和 TE 两个数据集上，按照论文四个不平衡比例进行 10 次重复实验，统计 Acc、macro-F1、MCC 的 mean ± std，并与论文 CA-SupCon 结果对比。
```

---

## 3. 复现流程

### 3.1 项目准备

进入项目目录：

```bash
cd /Users/hadley/Desktop/UESTC/CA-SupCon
```

检查 Python 环境：

```bash
.venv/bin/python --version
```

当前项目使用：

```text
Python 3.14.3
PyTorch 2.12.1
macOS arm64
MacBook Pro M5 Pro 64GB
```

### 3.2 代码可运行性检查

运行编译检查：

```bash
.venv/bin/python -m compileall -q main lib scripts
```

该步骤用于确认：

```text
main/
lib/
scripts/
```

目录下代码没有基础语法错误。

### 3.3 CWRU 数据准备

CWRU 使用 48 kHz drive-end bearing fault data，3 hp 负载，10 类，窗口长度 400，步长 200。

数据准备脚本：

```bash
.venv/bin/python scripts/prepare_cwru.py
```

输出目录：

```text
output/cwru/Train1800_Val300_Test300/imbalanced/
```

生成四个不平衡比例：

```text
all_equal_ratio_0.2
all_equal_ratio_0.1
all_equal_ratio_0.05
all_equal_ratio_0.02
```

其中：

```text
0.2  对应 5:1
0.1  对应 10:1
0.05 对应 20:1
0.02 对应 50:1
```

### 3.4 TE 数据准备

TE 使用 Tennessee Eastman Process 数据，18 类，输入为 `52 x 200` 多变量时间窗。

当前正式版本使用 random-window 数据构造：

```bash
.venv/bin/python scripts/prepare_te.py \
  --raw_dir data_raw/te \
  --dataset_desc train-2000_val-1000_test-1000_random-window \
  --sample_strategy random_windows
```

输出目录：

```text
output/te/train-2000_val-1000_test-1000_random-window/imbalanced/
```

采用 random-window 的原因：

```text
旧 sequential 抽样容易只覆盖少量仿真段，导致 TE 部分类别严重偏低。
random-window 能覆盖更多仿真轨迹和故障演化阶段，结果更稳定。
```

### 3.5 严格训练

CWRU 严格训练命令：

```bash
.venv/bin/python scripts/run_seed_sweep.py \
  --dataset cwru \
  --device mps
```

TE 严格训练命令：

```bash
.venv/bin/python scripts/run_seed_sweep.py \
  --dataset te \
  --dataset_desc train-2000_val-1000_test-1000_random-window \
  --device mps
```

说明：

```text
每个数据集包含 4 个 ratio。
每个 ratio 跑 10 个 seed。
每个 seed 跑 50 epochs。
```

总计：

```text
2 datasets x 4 ratios x 10 seeds = 80 次正式训练
```

### 3.6 结果汇总

CWRU 汇总：

```bash
.venv/bin/python scripts/summarize_repeated_runs.py \
  --dataset cwru \
  --output_csv output/cwru_mean_std.csv
```

TE 汇总：

```bash
.venv/bin/python scripts/summarize_repeated_runs.py \
  --dataset te \
  --dataset_desc train-2000_val-1000_test-1000_random-window \
  --output_csv output/te_mean_std.csv
```

总图生成：

```bash
.venv/bin/python scripts/plot_experiment_summary.py \
  --output_dir output \
  --name ca_supcon_experiment_summary
```

正式结果文件：

```text
output/cwru_mean_std.csv
output/te_mean_std.csv
output/ca_supcon_vs_paper.csv
output/ca_supcon_experiment_summary.png
output/ca_supcon_vs_paper.png
```

---

## 4. 实验设置

### 4.1 CWRU 设置

| 项目 | 设置 |
|---|---|
| 数据集 | CWRU Bearing Data Center |
| 信号类型 | drive-end vibration |
| 采样频率 | 48 kHz |
| 负载 | 3 hp |
| 类别数 | 10 |
| 输入窗口 | `1 x 400` |
| window length | 400 |
| step | 200 |
| train normal | 1800 |
| val per class | 300 |
| test per class | 300 |
| epochs | 50 |
| batch size | 60 |
| optimizer | Adam |
| lr | 0.0003 |
| weight decay | 0.0003 |
| SupCon temperature | 0.1 |
| lambda | 1 |

### 4.2 TE 设置

| 项目 | 设置 |
|---|---|
| 数据集 | Tennessee Eastman Process |
| 类别数 | 18 |
| 输入窗口 | `52 x 200` |
| window length | 200 |
| step | 1 |
| train normal | 2000 |
| val per class | 1000 |
| test per class | 1000 |
| 数据构造 | random-window |
| epochs | 50 |
| batch size | 72 |
| optimizer | Adam |
| lr | 0.0003 |
| weight decay | 0.0003 |
| SupCon temperature | 0.2 |
| lambda | 1 |

---

## 5. 总结果图

下图展示当前项目各数据集、各不平衡比例的最新完整 run 结果，以及 per-class accuracy 热力图。

![CA-SupCon experiment summary](assets/ca_supcon_experiment_summary.png)

说明：

```text
该图适合快速查看单次完整 run 的 TestAcc、TestF1、TestMCC 和弱类别。
正式论文比较仍以 10 seed mean ± std 表格为准。
```

---

## 6. 与论文结果对比图

下图展示当前复现与论文 CA-SupCon 结果的 accuracy 对比。

![CA-SupCon reproduction vs paper](assets/ca_supcon_vs_paper.png)

读图方式：

```text
蓝色柱：当前复现 10-run mean accuracy。
黑色误差线：当前复现标准差。
橙色柱：论文 CA-SupCon accuracy。
柱子上方数字：当前复现 Acc - 论文 Acc。
正数表示超过论文，负数表示低于论文。
```

---

## 7. CWRU 结果

| Ratio | 当前 Acc | 论文 Acc | Acc 差值 | 当前 F1 | 论文 F1 | 当前 MCC | 论文 MCC |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 0.20 | 93.01±0.36 | 87.45 | +5.56 | 93.01±0.36 | 87.39 | 92.24±0.40 | 86.08 |
| 0.10 | 91.60±0.52 | 87.36 | +4.24 | 91.63±0.52 | 87.25 | 90.68±0.58 | 86.02 |
| 0.05 | 90.92±0.32 | 83.90 | +7.02 | 90.92±0.32 | 83.16 | 89.92±0.36 | 82.39 |
| 0.02 | 87.28±0.73 | 83.12 | +4.16 | 87.38±0.71 | 82.34 | 85.89±0.82 | 81.50 |

### 7.1 CWRU 结果解读

CWRU 四个比例全部超过论文。

观察点：

```text
1. Acc、F1、MCC 三个指标均超过论文。
2. 随着 ratio 从 0.20 降到 0.02，不平衡程度增加，指标整体下降。
3. 标准差较小，说明 10 seed 结果稳定。
4. CWRU 是当前复现最贴近论文设置的数据集。
```

CWRU 结论：

```text
CWRU 复现成功，且结果明显优于论文报告值。
这说明当前数据准备、采样器、训练流程、best checkpoint 保存、测试评估和 mean ± std 汇总整体可靠。
```

---

## 8. TE 结果

| Ratio | 当前 Acc | 论文 Acc | Acc 差值 | 当前 F1 | 论文 F1 | 当前 MCC | 论文 MCC |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 0.20 | 94.84±0.95 | 91.98 | +2.86 | 94.67±1.17 | 91.01 | 94.61±0.95 | 91.72 |
| 0.10 | 87.99±0.80 | 89.53 | -1.54 | 86.91±1.49 | 88.23 | 87.63±0.83 | 89.16 |
| 0.05 | 85.68±0.90 | 87.79 | -2.11 | 84.20±1.40 | 86.34 | 85.46±0.73 | 87.40 |
| 0.02 | 85.17±0.74 | 83.27 | +1.90 | 83.04±0.87 | 80.76 | 85.40±0.59 | 82.79 |

### 8.1 TE 结果解读

TE 结果比 CWRU 更复杂。

观察点：

```text
1. TE 0.20 超过论文。
2. TE 0.10 略低于论文。
3. TE 0.05 略低于论文，是当前最需要分析的比例。
4. TE 0.02 超过论文。
5. TE 的 F1 普遍低于 Acc，说明部分类别识别不均衡。
```

TE 结论：

```text
TE 整体已经接近论文水平，但仍存在明显弱类别。
不能只看总体 Acc，需要结合 macro-F1、MCC 和 per-class accuracy 判断。
```

---

## 9. 弱类别分析

根据最新完整 run 的 per-class accuracy：

| Dataset | Ratio | TestAcc | Weak classes | Min per-class Acc |
|---|---:|---:|---|---:|
| CWRU | 0.20 | 0.93100 | 8, 4, 6 | 0.833 |
| CWRU | 0.10 | 0.91100 | 4, 8, 2 | 0.777 |
| CWRU | 0.05 | 0.91300 | 4, 8, 6 | 0.700 |
| CWRU | 0.02 | 0.86733 | 8, 4, 6 | 0.720 |
| TE | 0.20 | 0.93656 | 15, 0, 9 | 0.336 |
| TE | 0.10 | 0.87444 | 9, 15, 0 | 0.088 |
| TE | 0.05 | 0.86011 | 9, 15, 3 | 0.002 |
| TE | 0.02 | 0.84544 | 9, 15, 3 | 0.002 |

关键现象：

```text
TE class 9 和 class 15 是持续弱类别。
TE class 3 在 0.05 和 0.02 下明显变弱。
CWRU 虽然也有弱类别，但最低 per-class accuracy 仍远高于 TE 的最差类别。
```

这说明：

```text
TE 的主要问题不是整体模型没有学会，而是部分类别的特征边界不稳定。
```

---

## 10. 与论文一致的地方

| 层面 | 一致内容 |
|---|---|
| 任务 | 不平衡故障诊断分类 |
| 数据集 | CWRU、TE |
| 不平衡比例 | 0.20、0.10、0.05、0.02 |
| 方法 | CE + SupCon + class-aware sampler |
| 损失 | `L = lambda * LSupCon + LCE` |
| lambda | 1 |
| CWRU temperature | 0.1 |
| TE temperature | 0.2 |
| epochs | 50 |
| optimizer | Adam |
| lr | 0.0003 |
| weight decay | 0.0003 |
| 评价指标 | Acc、macro-F1、MCC |
| 统计口径 | 10 runs / 10 seeds mean ± std |

---

## 11. 与论文不完全一致的地方

| 层面 | 不完全一致点 | 影响 |
|---|---|---|
| 窗口索引 | 论文未公开具体随机窗口索引 | 无法保证逐窗口完全一致 |
| TE 数据构造 | 当前正式版使用 random-window | 提升覆盖度和稳定性 |
| 运行环境 | 当前使用本机 MacBook Pro M5 Pro 64GB | 可能导致速度和随机性差异 |
| 工程代码 | 新增数据准备、汇总、画图、设备参数 | 不改变核心方法 |
| 图示 | 当前生成更多训练曲线和 per-class 图 | 方便分析，不影响算法 |

需要强调：

```text
这些差异不等于复现失败。
其中多数属于论文未公开细节或工程复现补齐。
核心方法、训练设置、指标和统计口径已经对齐论文。
```

---

## 12. 当前复现结论

正式结论：

```text
本项目完成了 CA-SupCon 在 CWRU 和 TE 两个数据集上的严格复现。
CWRU 四个不平衡比例均超过论文结果，说明当前复现流程在轴承振动故障诊断任务上稳定可靠。
TE random-window 版本整体接近论文，其中 0.20 和 0.02 超过论文，0.10 和 0.05 略低于论文。
TE 的类别 9、15 和极端不平衡下的类别 3 是主要弱识别类别，后续创新应重点围绕这些类别的特征可分性、采样策略和对比学习约束展开。
```

---

## 13. 后续建议

后续不建议继续盲目重复跑 baseline。

优先级应为：

```text
1. 固定当前 baseline。
2. 统计 TE class 3、9、15 在 10 seeds 下的 per-class mean ± std。
3. 做 TE 特征可视化，例如 t-SNE 或 UMAP。
4. 分析弱类别主要混淆到哪些类别。
5. 基于弱类别问题设计改进方法。
```

可选创新方向：

```text
1. prototype-based SupCon
2. hard negative mining
3. class-adaptive temperature
4. weak-class-aware sampler
5. fault-stage-aware window sampling
6. feature-space margin constraint
7. 不确定性估计 + 维护决策
```

推荐从 TE 0.05 和 TE 0.02 开始验证，因为这两个比例最能暴露弱类别问题。

---

## 14. 可引用文件清单

正式结果表：

```text
output/cwru_mean_std.csv
output/te_mean_std.csv
output/ca_supcon_vs_paper.csv
```

正式图：

```text
output/ca_supcon_experiment_summary.png
output/ca_supcon_vs_paper.png
```

详细说明文档：

```text
docs/04_reproduction_notes.md
docs/06_results_analysis.md
docs/07_final_reproduction_report.md
```

