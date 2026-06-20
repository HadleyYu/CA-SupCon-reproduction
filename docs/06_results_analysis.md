# CA-SupCon 实验结果分析

本文档只做一件事：分析当前复现结果。

它不重复讲训练命令，也不重复讲 Git。重点回答：

```text
1. 当前结果是否完成严格复现。
2. CWRU 和 TE 分别表现如何。
3. 和论文相比哪里一致、哪里不一致。
4. 哪些类别是主要问题。
5. 后续创新应该从哪里切入。
```

---

## 1. 正式结果来源

当前正式统计文件是：

```text
output/cwru_mean_std.csv
output/te_mean_std.csv
output/ca_supcon_vs_paper.csv
```

当前正式图示是：

```text
output/ca_supcon_experiment_summary.png
output/ca_supcon_vs_paper.png
```

文档内备份图：

![CA-SupCon experiment summary](assets/ca_supcon_experiment_summary.png)

![CA-SupCon reproduction vs paper](assets/ca_supcon_vs_paper.png)

说明：

```text
mean_std.csv:
正式论文口径，10 seed 的 mean ± std。

ca_supcon_vs_paper.csv:
当前复现和论文 CA-SupCon 表格结果的直接对比。

ca_supcon_experiment_summary.csv:
每个比例最新完整 run 的总览，适合看 per-class 弱类别，但不是 mean ± std 本身。
```

---

## 2. 实验是否完整

当前严格实验已经完整：

| Dataset | Ratios | Seeds | Epochs | 是否完成 |
|---|---:|---:|---:|---|
| CWRU | 4 | 10 | 50 | 完成 |
| TE | 4 | 10 | 50 | 完成 |

总训练规模：

```text
2 datasets x 4 ratios x 10 seeds x 50 epochs
= 80 次正式训练
```

因此，当前已经不是“单次训练看趋势”，而是可以进入论文复现比较的正式结果。

---

## 3. 总体结论

一句话结论：

```text
CWRU 复现结果全面超过论文。
TE random-window 复现结果整体接近论文，其中 0.20 和 0.02 超过论文，0.10 和 0.05 略低于论文。
```

更严谨地说：

```text
当前方法、训练轮数、核心超参、评价指标和 10 seed 统计口径与论文一致。
CWRU 数据构造高度贴近论文设置，因此结果稳定且全部超过论文。
TE 的任务定义和统计口径与论文一致，但论文未公开具体窗口索引；当前使用 random-window 构造正式数据集，修复了旧 sequential 抽样覆盖不足的问题。
```

---

## 4. CWRU 结果分析

| Ratio | 当前 Acc | 论文 Acc | Acc 差值 | 当前 F1 | 论文 F1 | 当前 MCC | 论文 MCC |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 0.20 | 93.01±0.36 | 87.45 | +5.56 | 93.01±0.36 | 87.39 | 92.24±0.40 | 86.08 |
| 0.10 | 91.60±0.52 | 87.36 | +4.24 | 91.63±0.52 | 87.25 | 90.68±0.58 | 86.02 |
| 0.05 | 90.92±0.32 | 83.90 | +7.02 | 90.92±0.32 | 83.16 | 89.92±0.36 | 82.39 |
| 0.02 | 87.28±0.73 | 83.12 | +4.16 | 87.38±0.71 | 82.34 | 85.89±0.82 | 81.50 |

### 4.1 CWRU 趋势

CWRU 的整体趋势符合预期：

```text
不平衡越严重，Acc/F1/MCC 整体下降。
0.20 最容易，0.02 最难。
所有 ratio 都超过论文。
标准差较小，说明结果稳定。
```

### 4.2 CWRU 说明了什么

CWRU 说明当前复现链路是可靠的：

```text
数据准备没有明显错误。
class-aware sampler 生效。
CE + SupCon 联合训练能稳定工作。
best checkpoint、测试评估、mean ± std 汇总流程闭合。
```

因此，CWRU 可以作为当前项目的“复现成功证据”。

但从创新角度看，CWRU 不适合作为主要突破口：

```text
因为当前 baseline 已经明显超过论文。
继续在 CWRU 上涨 1-2 个点，可能更像调参，而不是有说服力的新方法。
```

---

## 5. TE 结果分析

| Ratio | 当前 Acc | 论文 Acc | Acc 差值 | 当前 F1 | 论文 F1 | 当前 MCC | 论文 MCC |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 0.20 | 94.84±0.95 | 91.98 | +2.86 | 94.67±1.17 | 91.01 | 94.61±0.95 | 91.72 |
| 0.10 | 87.99±0.80 | 89.53 | -1.54 | 86.91±1.49 | 88.23 | 87.63±0.83 | 89.16 |
| 0.05 | 85.68±0.90 | 87.79 | -2.11 | 84.20±1.40 | 86.34 | 85.46±0.73 | 87.40 |
| 0.02 | 85.17±0.74 | 83.27 | +1.90 | 83.04±0.87 | 80.76 | 85.40±0.59 | 82.79 |

### 5.1 TE 趋势

TE 的趋势比 CWRU 更复杂：

```text
0.20 明显超过论文。
0.10 略低于论文。
0.05 略低于论文，是当前最需要分析的比例。
0.02 重新超过论文。
```

这说明 TE 不是简单的“样本越少越差”。

可能原因：

```text
TE 是多变量工业过程数据。
不同 fault 的动态演化和变量耦合不同。
某些类别即使样本不少，也可能和其他类别高度相似。
窗口抽样方式会影响模型看到的动态阶段。
```

### 5.2 TE 的真正问题不是整体 Acc

TE 的整体 Acc 看起来已经接近论文，但 per-class 结果暴露了关键问题。

最新完整 run 的弱类别如下：

| Ratio | TestAcc | Weak classes | 最低 per-class Acc |
|---:|---:|---|---:|
| 0.20 | 0.93656 | 15, 0, 9 | 0.336 |
| 0.10 | 0.87444 | 9, 15, 0 | 0.088 |
| 0.05 | 0.86011 | 9, 15, 3 | 0.002 |
| 0.02 | 0.84544 | 9, 15, 3 | 0.002 |

最重要的发现：

```text
TE class 9 和 class 15 是持续弱类别。
TE class 3 在 0.05 和 0.02 下也明显变弱。
```

这说明后续分析不能只看整体 Acc。

如果只看 Acc，TE 0.02 有 85.17%，似乎还不错。
但 per-class 显示 class 9 和 class 15 几乎没有识别出来。

这就是不平衡故障诊断里最关键的问题：

```text
整体性能不错，不等于少数类故障可靠。
```

---

## 6. 和论文一致的地方

一致项：

```text
1. 数据集一致：CWRU 和 TE。
2. 任务一致：不平衡故障分类。
3. 不平衡比例一致：0.20、0.10、0.05、0.02。
4. 方法主线一致：CE loss + SupCon loss + class-aware sampler。
5. lambda 一致：1。
6. CWRU temperature 一致：0.1。
7. TE temperature 一致：0.2。
8. 训练轮数一致：50 epochs。
9. 统计口径一致：10 runs / 10 seeds mean ± std。
10. 指标一致：Acc、macro-F1、MCC。
```

---

## 7. 和论文不完全一致的地方

不完全一致项：

```text
1. 论文没有公开具体随机窗口索引。
2. 当前 CWRU 和 TE 的窗口抽取无法做到逐窗口与论文完全相同。
3. 当前 TE 正式版使用 random-window，而不是旧 sequential 抽样。
4. 当前训练环境是 MacBook Pro M5 Pro 64GB，本机 Python/PyTorch 环境与论文作者环境不同。
5. 当前代码增加了设备选择、数据准备、汇总和画图脚本，这些是工程增强，不是方法改变。
```

这些差异的性质不同：

```text
窗口索引差异：
属于论文未公开细节导致的不可避免差异。

TE random-window：
属于数据构造修正，目的是提升覆盖度和稳定性。

Mac 本机环境：
属于运行环境差异，不改变算法定义。

新增脚本：
属于复现工程补齐，不改变 CA-SupCon 核心方法。
```

---

## 8. 当前复现能怎么写

可以这样写：

```text
本项目基于 CA-SupCon 官方方法路线，完成了 CWRU 和 TE 两个数据集在四种不平衡比例下的严格复现。实验采用 50 epochs 训练，并对每个比例重复 10 个 seed，报告 Acc、macro-F1 和 MCC 的 mean ± std。CWRU 四个比例均超过论文报告结果，说明当前数据构造、采样策略、训练流程和评估脚本已经形成稳定闭环。TE 使用 random-window 数据构造后整体接近论文水平，其中 0.20 和 0.02 超过论文，0.10 和 0.05 略低于论文。进一步 per-class 分析显示，TE 的类别 9、15 以及极端不平衡下的类别 3 是主要弱识别类别。
```

如果写得更审慎：

```text
由于原论文未公开具体随机窗口索引，当前复现无法保证与论文逐窗口完全一致。因此，本文将比较重点放在方法设置、统计口径、整体趋势、mean ± std 和弱类别行为上，而不是追求每个数值与论文完全相同。
```

---

## 9. 后续创新点从哪里来

当前最有价值的创新方向不是继续跑 baseline，而是围绕 TE 的弱类别做问题驱动改进。

### 9.1 类别 9、15、3 的弱识别

问题：

```text
class 9 和 class 15 在多个比例下持续很差。
class 3 在 0.05 和 0.02 下明显变差。
```

可能创新方向：

```text
1. class-aware loss re-weighting
2. prototype-based SupCon
3. hard positive / hard negative mining
4. fault-stage-aware window sampling
5. per-class adaptive temperature
6. feature-space margin constraint
```

### 9.2 TE 的动态阶段问题

TE 故障不是静态图像，而是随时间演化的过程。

后续可以分析：

```text
同一个 fault 的早期、中期、后期窗口是否可分。
当前 random-window 是否把困难阶段采够。
weak class 是否集中在某些仿真 run 或某些时间段。
```

可能创新方向：

```text
stage-aware sampler
temporal contrastive learning
sequence encoder
time-frequency / variable-attention fusion
```

### 9.3 从分类到维护决策

当前 CA-SupCon 只做分类。

如果要和控制科学与工程、预测性维护结合，可以往后接：

```text
故障概率
-> 置信度/不确定性
-> 风险评估
-> 维护决策
```

强化学习更适合放在这个阶段，而不是直接替换分类器。

---

## 10. 下一步应该做什么

建议顺序：

```text
1. 固定当前 baseline，不再反复重跑。
2. 单独统计 TE class 3、9、15 在 10 seeds 下的 per-class mean ± std。
3. 画 TE feature embedding，可用 t-SNE 或 UMAP。
4. 看弱类别到底和哪些类别混淆。
5. 基于弱类别问题设计一个小改动，例如 prototype SupCon 或 hard-negative SupCon。
6. 只在 TE 0.05 和 0.02 先做快速验证。
7. 如果有效，再扩展到四个 ratio 和 CWRU。
```

当前最优先的分析任务：

```text
TE weak class analysis:
class 3
class 9
class 15
```

原因：

```text
整体 Acc 已经说明 baseline 成立。
真正能形成创新点的是少数弱故障类为什么识别不好，以及如何改善它们。
```

