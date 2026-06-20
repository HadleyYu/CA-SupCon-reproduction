# CA-SupCon 零基础入门手册

这份文档假设你是第一次做论文代码复现。它不会默认你懂深度学习、故障诊断、指标、终端命令或 Python 项目结构。

你可以把这份文档当成一条路线：

```text
先知道论文在解决什么问题
-> 再知道数据长什么样
-> 再知道模型怎么学
-> 再知道指标怎么看
-> 最后照着命令一步一步跑
```

本文所在工程目录是：

```text
/Users/hadley/Desktop/UESTC/CA-SupCon
```

原始论文 PDF 在上一层目录：

```text
/Users/hadley/Desktop/UESTC/2022KBS-A class-aware supervised contrastive learning framework for imbalanced fault diagnosis(1).pdf
```

## 阅读路线和掌握目标

这 8 份编号文档是一套完整学习路径，不是彼此独立的碎片。

推荐顺序：

```text
00_git_and_results_quick_start.md
-> 01_beginner_guide.md
-> 02_training_workflow_full_guide.md
-> 03_training_theory_to_code_deep_dive.md
-> 04_reproduction_notes.md
-> 05_fault_diagnosis_review_market_and_innovation.md
-> 06_results_analysis.md
-> 07_final_reproduction_report.md
```

每份文档解决的问题：

| 文件 | 主要用途 | 看完应该会什么 |
|---|---|---|
| `00_git_and_results_quick_start.md` | Git 和结果入口 | 知道怎么提交 docs、怎么看总图、怎么看论文对比 |
| `01_beginner_guide.md` | 零基础入门 | 知道故障诊断、分类、指标、训练日志的基本概念 |
| `02_training_workflow_full_guide.md` | 实验操作手册 | 知道怎么准备数据、跑训练、汇总结果、画总图 |
| `03_training_theory_to_code_deep_dive.md` | 理论到代码 | 知道 SupCon、sampler、Dataset、模型和 loss 在代码里怎么实现 |
| `04_reproduction_notes.md` | 论文复现记录 | 知道当前工程和论文设置如何对应，哪些结果能算正式复现 |
| `05_fault_diagnosis_review_market_and_innovation.md` | 综述与创新点 | 知道这个方向的产业背景、研究热点和后续选题方向 |
| `06_results_analysis.md` | 实验结果分析 | 知道当前结果说明什么，CWRU/TE 哪里强，TE 弱类别在哪里 |
| `07_final_reproduction_report.md` | 最终结果报告 | 能直接看到复现过程、实验设置、结果表、论文对比和最终结论 |

读完这套文档后，至少要能自己回答：

```text
1. CWRU 和 TE 分别是什么数据，输入形状有什么区别？
2. 为什么不平衡故障诊断不能只看 Acc？
3. CA-SupCon 为什么要同时用 CE loss 和 SupCon loss？
4. class-aware sampler 为什么对少数类有帮助？
5. 单次训练结果和论文 mean ± std 有什么区别？
6. 训练日志、checkpoint、单次图、总图分别在哪里？
7. 如果换一个新故障诊断数据集，应该从哪些代码文件开始改？
8. 如果要做创新，应该改数据、采样、loss、模型、迁移还是决策层？
```

## 读完整套文档后的达标标准

这套文档不是只为了“会敲命令”，而是为了让你对故障诊断形成一个从理论到实验、从代码到选题的完整框架。

读完后，至少应该达到下面四个层次。

第一层：能讲清故障诊断是什么。

```text
你应该能解释：
故障检测、故障分类、故障诊断、PHM、预测性维护之间是什么关系。
CWRU 为什么代表旋转机械轴承故障。
TE 为什么代表多变量工业过程故障。
为什么故障诊断和控制科学与工程有关，而不只是普通机器学习分类。
```

第二层：能完整跑通一次论文复现。

```text
你应该能解释：
原始数据放哪里。
prepare_cwru.py 和 prepare_te.py 做了什么。
main/main.py 如何启动训练。
run_seed_sweep.py 为什么要跑多个 seed。
summarize_repeated_runs.py 为什么才是论文表格口径。
plot_experiment_summary.py 和 ca_supcon_vs_paper.png 分别看什么。
```

第三层：能看懂指标和日志。

```text
你应该能解释：
TrainLoss、TrainSupLoss、TrainCeLoss 分别是什么。
ValAcc 和 TestAcc 为什么不能混。
macro-F1 为什么比 Acc 更关注少数类。
MCC 为什么适合不平衡分类。
per-class accuracy 为什么能暴露 TE class 9、15、3 的问题。
mean ± std 为什么比单次结果更严谨。
```

第四层：能提出有依据的创新点。

```text
你不应该只说“换个模型试试”。
你应该能说：
当前 CWRU 已经全部超过论文，不适合作为主要突破口。
TE 0.10 和 0.05 略低于论文，且 class 9、15、3 是弱类别。
后续创新应围绕弱类别、特征边界、窗口采样、对比学习约束、prototype 或 hard negative mining 展开。
```

如果能做到这四层，就基本具备了写一份故障诊断方向综述、复现实验报告和初步开题思路的能力。

## 当前版本的最终结果口径

这套文档已经按当前项目的正式复现结果更新。以后看结果时，先记住这个顺序：

```text
第一优先级：output/cwru_mean_std.csv 和 output/te_mean_std.csv
第二优先级：output/ca_supcon_vs_paper.csv / .png / .pdf
第三优先级：output/ca_supcon_experiment_summary.png / .pdf
第四优先级：每次单独训练的 log 和 figures
```

原因很简单：

```text
mean_std.csv 是论文口径：多 seed 的均值和标准差。
ca_supcon_vs_paper 是论文对比图：看当前复现比论文高还是低。
ca_supcon_experiment_summary 是总说明图：看最新完整 run 的曲线、指标和 per-class heatmap。
单次 log 只能用来排查训练过程，不能单独代表论文复现水平。
```

当前严格复现结论：

```text
CWRU:
四个不平衡比例全部超过论文。

TE:
random-window 数据版本已经解决旧 sequential 版本严重偏低的问题。
0.20 和 0.02 超过论文。
0.10 和 0.05 略低于论文，但已经接近论文水平。
```

### 结果图怎么看

总说明图：

![CA-SupCon experiment summary](assets/ca_supcon_experiment_summary.png)

论文对比图：

![CA-SupCon reproduction vs paper](assets/ca_supcon_vs_paper.png)

论文对比图的读法：

```text
蓝色柱 = 当前复现的 10 次均值。
黑色误差线 = 当前复现的标准差。
橙色柱 = 论文 CA-SupCon 结果。
柱子上方数字 = 当前复现 Acc - 论文 Acc。
正数表示超过论文，负数表示低于论文。
```

## 不跳步骤的完整学习路线

如果你想从完全不熟，到能自己复现实验、看懂代码、再找创新点，按下面顺序走。不要一开始就跳到改模型，也不要一开始就全量跑 80 次训练。

### 第 0 步：先知道自己在做什么

目标：

```text
知道这不是普通跑代码，而是在复现一篇不平衡故障诊断论文。
```

你要弄清：

```text
故障诊断是什么
CWRU 是轴承振动故障
TE 是工业过程故障
类别不平衡为什么重要
CA-SupCon 的核心是 CE + SupCon + class-aware sampler
```

对应阅读：

```text
01_beginner_guide.md 的 0-15 节
```

### 第 1 步：补齐基础指标

目标：

```text
看到日志里的 Acc、F1、MCC、per-class accuracy 不懵。
```

你要弄清：

```text
Acc 看整体对不对
macro-F1 平等看每个类别
MCC 对不平衡更严格
per-class accuracy 看每个故障类是否学会
mean ± std 是论文严谨统计口径
```

对应阅读：

```text
01_beginner_guide.md 的 19-30 节
```

### 第 2 步：认识项目目录

目标：

```text
知道每个文件夹大概干什么。
```

必须知道：

```text
main/       训练入口
configs/    实验配置
lib/        核心代码
scripts/    数据准备、批量训练、汇总、画图
output/     数据、日志、模型、结果图
docs/       文档
```

对应阅读：

```text
01_beginner_guide.md 的 31 节
02_training_workflow_full_guide.md 的 17 节
```

### 第 3 步：跑通最小链路

目标：

```text
先证明环境、代码、训练入口都能跑通。
```

做法：

```text
先跑 smoke test 或 1 epoch
确认不报错
确认能产生 log
确认能输出 TestAcc/TestF1/TestMCC
确认能保存图
```

对应阅读：

```text
01_beginner_guide.md 的 32-37 节
02_training_workflow_full_guide.md 的 14 节
```

### 第 4 步：准备真实数据

目标：

```text
生成符合论文设置的 CWRU 和 TE train/val/test。
```

必须确认：

```text
CWRU: Train1800_Val300_Test300
TE: train-2000_val-1000_test-1000_random-window
四个比例: 0.2, 0.1, 0.05, 0.02
数据文件在 output/ 对应目录下
```

对应阅读：

```text
02_training_workflow_full_guide.md 的 3-4 节
04_reproduction_notes.md 的二、八节
```

### 第 5 步：单次训练

目标：

```text
先跑一个 dataset、一个 ratio、一个 seed、50 epochs。
```

必须确认：

```text
Training Complete
Best checkpoint is saved
Performance on test set
TestAcc/TestF1/TestMCC
Per class accuracy
Summary figure / Per-class figure / Detailed report
```

对应阅读：

```text
02_training_workflow_full_guide.md 的 6-10 节
```

### 第 6 步：理解训练过程

目标：

```text
知道为什么它会一轮一轮跑，为什么有 300/300，为什么 best epoch 不一定是最后一轮。
```

必须理解：

```text
epoch 是完整训练轮次
300/300 是当前 epoch 的 batch 数
TrainNum 可能来自 class-aware sampler 采样后的训练步数
每轮后跑 val
最终 test 使用 best validation checkpoint
```

对应阅读：

```text
01_beginner_guide.md 的 16-18、45、57-74 节
03_training_theory_to_code_deep_dive.md 的 7、16、18 节
```

### 第 7 步：多 seed 和严格复现

目标：

```text
从单次结果升级到论文级 mean ± std。
```

严格标准：

```text
2 datasets
4 ratios
10 seeds
50 epochs
共 80 次训练
```

不能混入：

```text
1 epoch 调试结果
smoke data
Ctrl+C 中断日志
没输出 TestAcc 的日志
旧 sequential TE 数据
```

对应阅读：

```text
02_training_workflow_full_guide.md 的 12-13、24 节
04_reproduction_notes.md 的八节
```

### 第 8 步：汇总和画图

目标：

```text
把很多日志变成论文能用的表和图。
```

顺序：

```text
先 summarize_repeated_runs.py
再 plot_experiment_summary.py
再看 ca_supcon_experiment_summary
再看 ca_supcon_vs_paper
```

对应阅读：

```text
02_training_workflow_full_guide.md 的 10-13、20、24 节
```

### 第 9 步：和论文比

目标：

```text
知道自己的结果是否接近论文，为什么高或低。
```

必须看：

```text
Acc/F1/MCC mean ± std
四个不平衡比例趋势
per-class accuracy
最弱类别
标准差是否过大
数据处理是否和论文一致
```

对应阅读：

```text
02_training_workflow_full_guide.md 的 15、21-22 节
04_reproduction_notes.md 全文
```

### 第 10 步：开始想创新点

目标：

```text
不是盲目换模型，而是基于问题提出可验证改进。
```

顺序：

```text
先找问题：少数类差、跨工况差、TE 多变量关系没用好、泛化不稳
再选层次：数据 / sampler / loss / model / domain adaptation / decision
再做最小实验：一个 ratio x 3 seeds
再扩展完整实验
最后写消融和分析
```

对应阅读：

```text
03_training_theory_to_code_deep_dive.md 的 13、19、21 节
05_fault_diagnosis_review_market_and_innovation.md 的 9、10、15 节
```

### 最终掌握标准

当你能做到下面这些，就说明这套文档真正读明白了：

```text
1. 能用自己的话讲清 CA-SupCon 为什么适合不平衡故障诊断。
2. 能独立跑 CWRU 或 TE 的一个单次训练。
3. 能判断日志里训练是否正常。
4. 能找到 output 里的 log、checkpoint、figure。
5. 能跑多 seed 并汇总 mean ± std。
6. 能解释自己的结果和论文差在哪里。
7. 能说出一个创新点改哪一层、为什么改、怎么验证。
8. 能设计最小实验和最终严格实验。
```

## 0. 先记住几个最重要的结论

这篇论文要做的是：

> 用深度学习识别机器是否故障，以及是哪一种故障。

它难在：

> 正常数据很多，故障数据很少，而且所有故障类都少。

普通模型容易学成：

> 大部分都猜正常，导致故障识别不好。

CA-SupCon 的核心想法是：

> 让同一类样本在特征空间靠近，让不同类样本远离；同时训练时让每个 batch 尽量类别均衡。

论文最重要的评估指标是：

- `Acc`：整体预测对了多少
- `macro-F1`：每个类别都平等看待后的综合效果
- `MCC`：更严格的整体分类相关性指标

## 1. 什么是论文复现

论文复现不是简单运行一个 Python 文件。

严谨的复现至少要检查这些东西：

1. 数据来源是不是论文说的数据。
2. 数据处理方式是不是论文说的方式。
3. 训练集、验证集、测试集样本数是不是论文表格里的数量。
4. 模型结构是不是论文里的结构。
5. loss、sampler、学习率、batch size、epoch 数是不是一致。
6. 评价指标是不是论文报告的指标。
7. 是否重复多次实验并报告均值和标准差。

本工程的目标是把这些步骤都放到当前文件夹里，尽量做到你能从原始数据开始走到训练结果。

## 2. 故障诊断到底是什么

机器运行时会产生传感器信号，比如振动、电流、温度、压力。

以轴承为例：

- 正常轴承转动时，振动信号比较稳定。
- 内圈坏了，振动会出现某种异常模式。
- 外圈坏了，振动会出现另一种异常模式。
- 滚动体坏了，又会出现另一种异常模式。

故障诊断就是让模型看一段信号，然后判断：

```text
这是正常，还是某一种故障？
```

这类任务通常叫 **分类任务**。

## 3. 什么是分类任务

分类任务就是从几个固定类别里选一个。

例如 CWRU 数据集有 10 类：

```text
0: normal 正常
1: IR007 内圈故障，故障直径 0.007 inch
2: IR014 内圈故障，故障直径 0.014 inch
3: IR021 内圈故障，故障直径 0.021 inch
4: B007 滚动体故障，故障直径 0.007 inch
5: B014 滚动体故障，故障直径 0.014 inch
6: B021 滚动体故障，故障直径 0.021 inch
7: OR007 外圈故障，故障直径 0.007 inch
8: OR014 外圈故障，故障直径 0.014 inch
9: OR021 外圈故障，故障直径 0.021 inch
```

模型输入一段信号，输出一个类别编号。

例如：

```text
输入：一段长度为 400 的振动信号
输出：2
含义：模型认为这是 IR014
```

## 4. 什么是样本和标签

机器学习里最常见的两个词是：

- sample：样本
- label：标签

一个样本就是一条输入数据。

一个标签就是这个样本的正确答案。

在 CWRU 中：

```text
样本 = 一段振动信号
标签 = 这段振动信号对应的故障类别
```

例如：

```text
样本: [0.12, 0.10, -0.03, ..., 0.08]
标签: 0
```

意思是：

> 这段信号属于正常类别。

再例如：

```text
样本: [0.45, -0.20, 0.33, ..., -0.18]
标签: 6
```

意思是：

> 这段信号属于 B021 故障。

## 5. 为什么原始长信号要切成窗口

原始 CWRU `.mat` 文件里通常是一条很长的振动信号。

模型不能直接把一整条超长信号当一个样本，因为：

1. 不同文件长度可能不一样。
2. 神经网络通常需要固定长度输入。
3. 一条长信号可以切出很多训练样本。

所以论文使用滑动窗口。

CWRU 设置是：

```text
窗口长度 = 400
步长 = 200
```

这是什么意思？

假设原始信号是：

```text
x[0], x[1], x[2], ..., x[999]
```

第一个窗口取：

```text
x[0] 到 x[399]
```

第二个窗口从 200 开始：

```text
x[200] 到 x[599]
```

第三个窗口从 400 开始：

```text
x[400] 到 x[799]
```

这样每个窗口都是一个样本。

步长 200 小于窗口长度 400，所以相邻窗口有一部分重叠。这样可以得到更多训练样本。

## 6. 什么是训练集、验证集、测试集

一个严谨实验通常把数据分成三份：

### 训练集 train

模型真正拿来学习的数据。

模型会反复看训练集，更新自己的参数。

### 验证集 val

训练过程中用来选择最好模型的数据。

模型不会直接用验证集更新参数，但会用它判断：

> 当前这一轮训练出来的模型好不好？

### 测试集 test

最后报告结果的数据。

测试集应该尽量只在最终评价时使用，避免模型“偷看答案”。

## 7. 什么是类别不平衡

如果每个类别样本数量差不多，叫类别平衡。

例如：

| 类别 | 样本数 |
|---|---:|
| 正常 | 1000 |
| 故障 1 | 1000 |
| 故障 2 | 1000 |

如果某些类别样本很多，某些类别样本很少，叫类别不平衡。

例如：

| 类别 | 样本数 |
|---|---:|
| 正常 | 1800 |
| 故障 1 | 36 |
| 故障 2 | 36 |
| 故障 3 | 36 |

现实中，正常数据容易采集，故障数据难采集，所以故障诊断经常不平衡。

## 8. 这篇论文的不平衡场景是什么

论文研究的是：

> 只有正常类很多，所有故障类都很少。

论文叫它：

```text
all-fault imbalance scenario
```

也就是“全故障类不平衡场景”。

用 CWRU 的 50:1 设置举例：

| 类别 | 训练样本数 |
|---|---:|
| 正常 | 1800 |
| 每个故障类 | 36 |

这里 `50:1` 的意思是：

```text
正常类样本数 / 每个故障类样本数 = 1800 / 36 = 50
```

所以叫 IB rate = 50:1。

IB 是 imbalance 的缩写。

## 9. 为什么不平衡会让模型变差

神经网络训练时会看大量样本。

如果正常样本特别多，模型会更频繁地看到正常类。

结果可能变成：

> 只要不确定，就猜正常。

这样整体准确率可能还不错，但故障类识别很差。

故障诊断里这很危险，因为漏掉故障的代价很高。

## 10. CA-SupCon 的直觉

CA-SupCon 不只是训练一个普通分类器。

它想让模型学到一个更好的特征空间。

什么叫特征空间？

你可以想象模型把每个样本变成一个点：

```text
原始振动信号 -> 神经网络 -> 一个 100 维向量
```

这个 100 维向量就是特征。

如果特征学得好：

- 正常样本会聚在一起
- 同一种故障会聚在一起
- 不同故障之间距离会比较远

如果特征学得不好：

- 正常和故障混在一起
- 故障 1 和故障 2 混在一起
- 分类器就很难判断

## 11. SupCon 是什么

SupCon 全称是：

```text
Supervised Contrastive Learning
```

中文可以叫：

```text
监督式对比学习
```

拆开看：

- Supervised：有标签监督
- Contrastive：通过“对比”来学习
- Learning：学习

它做的事情是：

```text
同一类样本 -> 拉近
不同类样本 -> 推远
```

举例：

```text
样本 A 标签是 2
样本 B 标签是 2
样本 C 标签是 7
```

SupCon 希望：

```text
A 和 B 更近
A 和 C 更远
B 和 C 更远
```

这样模型学出的特征更容易分类。

## 12. 数据增强是什么

数据增强就是对原始样本做一点不会改变类别的小扰动。

例如一段轴承振动信号，加一点点噪声，它还是同一种故障。

论文使用四种增强：

### Jitter

加高斯噪声。

直觉：

> 真实传感器本来就会有一点噪声，模型不能太脆弱。

### Scaling

把信号幅值稍微放大或缩小。

直觉：

> 同一种故障在不同采集条件下幅值可能略有变化。

### MakeNoise

随机把一部分点遮掉。

直觉：

> 让模型不要依赖某几个固定采样点。

### Translation

把信号左右平移。

直觉：

> 故障冲击可能出现在窗口里稍微不同的位置。

## 13. Class-aware sampler 是什么

普通采样是：

> 每个样本都有差不多概率被抽进 batch。

问题是正常样本太多时，一个 batch 里很可能大部分都是正常类。

Class-aware sampler 是：

> 先选类别，再从这个类别里选样本。

这样每个 batch 里各个类别更均衡。

CWRU 中：

```text
类别数 = 10
batch size = 60
NUM_SAMPLER_CLS = 6
```

大致效果是：

```text
每个类别约 6 个样本
10 个类别 -> 60 个样本
```

这样 SupCon 在一个 batch 里能看到多个故障类，才有机会把故障类之间也推远。

## 14. Cross-Entropy 是什么

Cross-Entropy 是分类任务最常用的损失函数。

它衡量：

> 模型给正确类别的概率够不够高？

例如真实标签是 `2`。

模型输出：

```text
类别 0: 0.01
类别 1: 0.05
类别 2: 0.90
类别 3: 0.04
```

正确类别概率是 0.90，loss 会比较小。

如果模型输出：

```text
类别 0: 0.80
类别 1: 0.10
类别 2: 0.02
类别 3: 0.08
```

正确类别概率只有 0.02，loss 会很大。

训练就是让 loss 变小。

## 15. 总损失是什么

CA-SupCon 同时使用两个 loss：

```text
LCE      = 交叉熵分类损失
LSupCon  = 监督对比学习损失
```

总损失是：

```text
L = LCE + lambda * LSupCon
```

论文里：

```text
lambda = 1
```

所以可以理解成：

```text
总损失 = 分类错误惩罚 + 特征空间不清楚惩罚
```

## 16. 什么是 epoch

epoch 是训练轮数。

一个 epoch 的意思是：

> 模型把训练集大致看完一遍。

论文设置：

```text
epochs = 50
```

也就是训练 50 轮。

如果你只是检查代码能不能跑，可以先用：

```text
epochs = 1
```

这叫 smoke test，不是正式论文结果。

## 17. 什么是 batch size

训练时不是一次只看一个样本，也不是一次看完整训练集，而是一小批一小批看。

这一小批叫 batch。

batch size 就是每一批有多少样本。

CWRU 中：

```text
batch size = 60
```

TE 中：

```text
batch size = 72
```

## 18. 什么是 learning rate

learning rate 是学习率。

它控制模型参数每次更新的步子大小。

太大：

> 可能训练不稳定。

太小：

> 可能学得很慢。

论文设置：

```text
learning rate = 0.0003
```

## 19. 什么是混淆矩阵

指标都来自混淆矩阵，所以先讲它。

假设只有 3 类：

```text
A = 正常
B = 故障 1
C = 故障 2
```

模型在测试集上的结果整理成：

| 真实类别 \ 预测类别 | 预测 A | 预测 B | 预测 C |
|---|---:|---:|---:|
| 真实 A | 50 | 3 | 2 |
| 真实 B | 5 | 30 | 15 |
| 真实 C | 1 | 4 | 45 |

读表方法：

- 行表示真实类别。
- 列表示模型预测类别。
- `真实 A, 预测 A = 50`，说明 50 个 A 被预测对。
- `真实 B, 预测 C = 15`，说明 15 个真实 B 被错判成 C。

对角线是正确预测：

```text
50, 30, 45
```

非对角线是错误预测。

## 20. Acc 是什么

Acc 是 Accuracy，准确率。

它问的是：

> 所有样本中，有多少比例被预测对？

公式：

```text
Acc = 正确预测数 / 总样本数
```

用上面的混淆矩阵：

```text
正确预测数 = 50 + 30 + 45 = 125
总样本数 = 50+3+2+5+30+15+1+4+45 = 155
Acc = 125 / 155 = 0.8065 = 80.65%
```

注意：

```text
0.8065 = 80.65%
```

程序日志里通常输出小数，比如：

```text
TestAcc: 0.80650
```

论文表格通常写百分数，比如：

```text
80.65
```

它们表达的是同一个值。

## 21. 为什么不能只看 Acc

假设测试集有 1000 个样本：

| 类别 | 数量 |
|---|---:|
| 正常 | 950 |
| 故障 | 50 |

如果模型永远预测正常：

```text
正常 950 个全对
故障 50 个全错
Acc = 950 / 1000 = 95%
```

Acc 很高，但模型完全不能发现故障。

这在故障诊断里不可接受。

所以还要看 F1、MCC、每类准确率。

## 22. TP、FP、FN、TN 是什么

讲 Precision 和 Recall 前，要先讲四个缩写。

以“类别 B”为例，把问题变成：

```text
这个样本是不是 B？
```

### TP

True Positive，真正例。

```text
真实是 B，模型也预测 B
```

### FP

False Positive，假正例。

```text
真实不是 B，模型却预测 B
```

### FN

False Negative，假负例。

```text
真实是 B，模型却没预测 B
```

### TN

True Negative，真负例。

```text
真实不是 B，模型也没预测 B
```

多分类里，计算某个类别的 Precision/Recall 时，会把这个类别当成“正类”，其他所有类别当成“负类”。

## 23. Precision 精确率是什么

Precision 问的是：

> 模型预测成某一类的样本里，有多少是真的这一类？

公式：

```text
Precision = TP / (TP + FP)
```

仍用前面的混淆矩阵，计算类别 B。

预测为 B 的样本有：

```text
真实 A 预测 B: 3
真实 B 预测 B: 30
真实 C 预测 B: 4
```

其中真正是 B 的只有 30。

所以：

```text
TP_B = 30
FP_B = 3 + 4 = 7
Precision_B = 30 / (30 + 7) = 0.8108 = 81.08%
```

直觉：

> 模型只要说“这是 B”，它说得准不准？

Precision 低说明误报多。

## 24. Recall 召回率是什么

Recall 问的是：

> 所有真实属于某一类的样本里，模型找回了多少？

公式：

```text
Recall = TP / (TP + FN)
```

还是类别 B。

真实为 B 的样本有：

```text
真实 B 预测 A: 5
真实 B 预测 B: 30
真实 B 预测 C: 15
```

其中被正确找出来的是 30。

所以：

```text
TP_B = 30
FN_B = 5 + 15 = 20
Recall_B = 30 / (30 + 20) = 0.60 = 60%
```

直觉：

> 真正的 B，模型漏掉了多少？

故障诊断里 Recall 很重要，因为漏报故障可能造成严重后果。

## 25. Precision 和 Recall 的区别

Precision 看误报。

Recall 看漏报。

举例：

模型很保守，只有特别确定才报故障：

```text
误报少 -> Precision 高
漏报多 -> Recall 低
```

模型很敏感，一点异常就报故障：

```text
漏报少 -> Recall 高
误报多 -> Precision 低
```

一个好模型应该尽量两者都高。

## 26. F1-score 是什么

F1 是 Precision 和 Recall 的综合指标。

公式：

```text
F1 = 2 * Precision * Recall / (Precision + Recall)
```

它的特点是：

> Precision 或 Recall 任何一个很低，F1 都会被拉低。

例如：

```text
Precision = 0.90
Recall = 0.10
F1 = 2 * 0.90 * 0.10 / (0.90 + 0.10)
F1 = 0.18
```

虽然 Precision 很高，但 Recall 太低，所以 F1 仍然很差。

这就是为什么 F1 适合故障诊断。

## 27. macro-F1 是什么

多分类任务里，每个类别都可以算一个 F1。

例如：

| 类别 | F1 |
|---|---:|
| normal | 0.95 |
| fault 1 | 0.70 |
| fault 2 | 0.60 |
| fault 3 | 0.50 |

macro-F1 就是普通平均：

```text
macro-F1 = (0.95 + 0.70 + 0.60 + 0.50) / 4
macro-F1 = 0.6875
```

重点：

> macro-F1 不管每个类别样本数多少，每个类别权重一样。

这对不平衡数据很重要。

因为正常类样本很多，如果只看整体 Acc，正常类会占很大影响；macro-F1 会强迫你关注每个故障类。

## 28. MCC 是什么

MCC 全称：

```text
Matthews Correlation Coefficient
```

中文：

```text
马修斯相关系数
```

它的取值范围：

```text
1    完美预测
0    接近随机猜
-1   完全反着预测
```

你可以先这样理解：

> MCC 是一个更严格的整体分类质量指标，尤其适合不平衡数据。

它会考虑整个混淆矩阵，而不是只看正确总数。

所以如果一个模型只会猜多数类，Acc 可能看起来还行，但 MCC 通常会不好。

论文使用 MCC，是为了避免被不平衡数据骗到。

## 29. 每类准确率是什么

日志里还会输出：

```text
Per class accuracy
```

它表示每个类别单独的准确率。

例如：

```text
[0.98, 0.75, 0.60, 0.20]
```

意思是：

```text
类别 0 准确率 98%
类别 1 准确率 75%
类别 2 准确率 60%
类别 3 准确率 20%
```

这非常有用。

如果整体 Acc 不低，但某几个故障类准确率特别低，就说明模型仍然偏。

## 30. 均值和标准差是什么

论文表格里经常写：

```text
87.45 ± 0.52
```

这表示 10 次重复实验：

```text
平均值 = 87.45
标准差 = 0.52
```

为什么要跑 10 次？

因为神经网络训练有随机性：

- 初始参数随机
- 数据顺序随机
- 数据增强随机
- GPU 计算可能有轻微差异

只跑一次可能刚好好运或坏运。

跑 10 次再取平均，更严谨。

标准差越小，说明结果越稳定。

## 31. 当前工程目录里有什么

进入工程目录后：

```bash
cd /Users/hadley/Desktop/UESTC/CA-SupCon
```

主要文件如下：

```text
README.md
```

快速说明。

```text
docs/01_beginner_guide.md
```

你正在看的这份零基础说明。

```text
docs/04_reproduction_notes.md
```

更偏论文复现细节的说明。

```text
configs/cwru/supcon/casupcon.yaml
```

CWRU 实验配置。

```text
configs/te/supcon/casupcon.yaml
```

TE 实验配置。

```text
main/main.py
```

训练入口。

```text
lib/backbone/
```

神经网络模型结构。

```text
lib/loss/
```

损失函数，包括 Cross-Entropy 和 SupCon。

```text
lib/sampler/
```

类别感知采样器。

```text
scripts/prepare_cwru.py
```

下载并处理 CWRU 数据。

```text
scripts/prepare_te.py
```

处理 TE 数据。

```text
scripts/make_smoke_data.py
```

生成很小的假数据，只用来检查代码是否能跑通。

## 32. 什么是假数据 smoke test

smoke test 是软件工程里的说法。

意思是：

> 先用很小的假数据跑一遍，确认代码链路没有断。

它能检查：

- Python 环境是否可用
- 数据读取是否可用
- 模型是否能前向传播
- loss 是否能计算
- 反向传播是否能更新参数
- 日志是否能输出指标
- checkpoint 是否能保存

但它不能证明论文结果。

所以一定记住：

```text
smoke data 不是论文数据
smoke test 不是论文复现结果
```

## 33. 从零开始运行：第一步，打开终端

你需要在终端里输入命令。

如果你用的是 macOS：

1. 打开 Launchpad。
2. 搜索 Terminal 或 终端。
3. 打开它。

打开后，你会看到一个可以输入命令的窗口。

## 34. 第二步，进入工程目录

在终端输入：

```bash
cd /Users/hadley/Desktop/UESTC/CA-SupCon
```

按回车。

这条命令的意思是：

> 切换到 CA-SupCon 工程目录。

输入下面命令检查是否进对了：

```bash
pwd
```

如果输出是：

```text
/Users/hadley/Desktop/UESTC/CA-SupCon
```

说明位置正确。

## 35. 第三步，创建 Python 虚拟环境

虚拟环境可以理解成：

> 给这个项目单独建一个 Python 工具箱。

输入：

```bash
python3 -m venv .venv
```

这会在当前目录创建 `.venv` 文件夹。

然后激活它：

```bash
source .venv/bin/activate
```

如果激活成功，你的终端前面可能出现：

```text
(.venv)
```

这表示你现在正在使用这个项目自己的 Python 环境。

## 36. 第四步，安装依赖

输入：

```bash
pip install -r requirements.txt
```

这条命令会安装项目需要的包，比如：

- numpy
- scipy
- PyYAML
- torch
- tqdm
- pyreadr

如果中途网络失败，可以重新运行同一条命令。

## 37. 第五步，先跑 smoke test

先生成假数据：

```bash
python scripts/make_smoke_data.py --dataset cwru
```

如果成功，会看到类似：

```text
Wrote synthetic CWRU smoke data to output/cwru/Train1800_Val300_Test300/imbalanced/smoke/data
```

然后跑 1 个 epoch：

```bash
python main/main.py --dataset cwru --exp_name supcon --cfg_name casupcon --imb_desc smoke --epochs 1 --device cpu
```

这条命令很长，我们拆开看：

```text
python main/main.py
```

运行训练入口。

```text
--dataset cwru
```

使用 CWRU 配置。

```text
--exp_name supcon
```

实验类型是 supcon。

```text
--cfg_name casupcon
```

使用 `casupcon.yaml` 配置。

```text
--imb_desc smoke
```

读取 smoke test 数据。

```text
--epochs 1
```

只训练 1 轮。

```text
--device cpu
```

不用 GPU，用 CPU 跑。

看到最后有：

```text
done!
```

说明流程跑通。

## 38. 第六步，准备真实 CWRU 数据

正式复现要用真实 CWRU 数据。

运行：

```bash
python scripts/prepare_cwru.py
```

脚本会做三件事：

1. 下载 CWRU 原始 `.mat` 文件。
2. 用滑动窗口切成样本。
3. 按论文样本数生成 train、val、test 文件。

真实数据会放在：

```text
data_raw/cwru/
```

处理后的训练数据会放在：

```text
output/cwru/Train1800_Val300_Test300/imbalanced/
```

## 39. CWRU 需要哪些原始文件

论文 CWRU 复现需要 10 个 `.mat` 文件：

| 类别 | 原始文件 |
|---|---|
| normal | `100.mat` |
| IR007 | `112.mat` |
| IR014 | `177.mat` |
| IR021 | `217.mat` |
| B007 | `125.mat` |
| B014 | `192.mat` |
| B021 | `229.mat` |
| OR007 | `138.mat` |
| OR014 | `204.mat` |
| OR021 | `241.mat` |

脚本下载后会保存成更清楚的名字：

```text
0_Normal.mat
1_IR007.mat
2_IR014.mat
3_IR021.mat
4_B007.mat
5_B014.mat
6_B021.mat
7_OR007at6.mat
8_OR014at6.mat
9_OR021at6.mat
```

## 40. 如果 CWRU 下载中断怎么办

CWRU 官网有时会中途断开连接。

这不是你操作错，也不是代码一定错。

本工程的下载脚本已经支持断点续传。

如果中断，重新运行：

```bash
python scripts/prepare_cwru.py
```

它会接着未完成的 `.part` 文件继续下载。

如果某个文件一直失败，可以手动下载对应 `.mat` 文件，然后放到：

```text
data_raw/cwru/
```

放好后重新运行脚本。

## 41. 第七步，确认数据数量是否对

`prepare_cwru.py` 成功后，会打印每个 split 的类别数量。

例如 50:1 应该类似：

```text
train counts:
0: 1800
1: 36
2: 36
...
9: 36
```

验证集应该是：

```text
每个类别 300
```

测试集也应该是：

```text
每个类别 300
```

如果数量对，说明数据构造和论文 Table 1 对齐。

## 42. 第八步，正式训练 CWRU

CWRU 有四种不平衡率。

### IB rate = 5:1

```bash
python main/main.py --dataset cwru --exp_name supcon --cfg_name casupcon --imb_desc all_equal_ratio_0.2
```

### IB rate = 10:1

```bash
python main/main.py --dataset cwru --exp_name supcon --cfg_name casupcon --imb_desc all_equal_ratio_0.1
```

### IB rate = 20:1

```bash
python main/main.py --dataset cwru --exp_name supcon --cfg_name casupcon --imb_desc all_equal_ratio_0.05
```

### IB rate = 50:1

```bash
python main/main.py --dataset cwru --exp_name supcon --cfg_name casupcon --imb_desc all_equal_ratio_0.02
```

如果没有 GPU，可以加：

```text
--device cpu
```

但正式训练用 CPU 会慢。

## 43. 日志在哪里

日志会保存在 `output/` 下面。

例如 CWRU smoke test 的日志路径类似：

```text
output/cwru/Train1800_Val300_Test300/imbalanced/smoke/logs/supcon/ca_supcon/cnn1d-cwru/
```

正式 CWRU 50:1 的日志路径类似：

```text
output/cwru/Train1800_Val300_Test300/imbalanced/all_equal_ratio_0.02/logs/supcon/ca_supcon/cnn1d-cwru/
```

## 44. 模型保存在哪里

模型 checkpoint 会保存在：

```text
output/cwru/Train1800_Val300_Test300/imbalanced/<imb_desc>/models/supcon/ca_supcon/cnn1d-cwru/
```

文件名类似：

```text
supcon_train_supcon.pth
```

`.pth` 是 PyTorch 模型文件。

## 45. 跑完后看哪些日志

训练日志里你会看到：

```text
TrainLoss
TrainSupLoss
TrainCeLoss
TrainAcc
ValAcc
ValF1
ValMCC
TestAcc
TestF1
TestMCC
Per class accuracy
```

逐个解释：

```text
TrainLoss
```

训练集上的总损失。

```text
TrainSupLoss
```

SupCon 对比学习损失。

```text
TrainCeLoss
```

交叉熵分类损失。

```text
TrainAcc
```

训练集准确率。

```text
ValAcc, ValF1, ValMCC
```

验证集指标，用来选择最好模型。

```text
TestAcc, TestF1, TestMCC
```

测试集指标，用来和论文表格对比。

```text
Per class accuracy
```

每个类别单独准确率。

## 45.1 控制台实时看什么

训练时终端里会实时出现进度条，例如：

```text
45%|████▌     | 136/300 [00:21<00:25, 6.31it/s]
```

它表示：

```text
当前 epoch 已经跑到 136/300 个 batch
速度大约 6.31 个 batch/s
```

每个 epoch 结束后，会打印本轮指标：

```text
TrainLoss
TrainSupLoss
TrainCeLoss
TrainAcc
ValAcc
ValF1
ValMCC
```

训练全部结束后，会打印测试集指标：

```text
TestAcc
TestF1
TestMCC
Per class accuracy
```

如果你想在另一个 VS Code 终端实时盯日志，可以运行：

```bash
tail -f output/cwru/Train1800_Val300_Test300/imbalanced/all_equal_ratio_0.02/logs/supcon/ca_supcon/cnn1d-cwru/*.log
```

`tail -f` 的意思是：

> 文件有新内容，就实时显示出来。

## 45.2 训练结果怎么画图

训练结束后，可以把日志画成图片。

例如画 CWRU 50:1 最新日志：

```bash
python scripts/plot_training_log.py --log_dir output/cwru/Train1800_Val300_Test300/imbalanced/all_equal_ratio_0.02/logs/supcon/ca_supcon/cnn1d-cwru
```

它会生成两张图：

```text
*_summary.png
*_per_class.png
```

第一张图包含：

- loss 曲线
- Train Acc / Val Acc 曲线
- Val F1 / Val MCC 曲线
- 最终 TestAcc / TestF1 / TestMCC 柱状图

第二张图是：

- 每个类别的准确率柱状图

图片会保存在日志目录下面的：

```text
figures/
```

你可以在 VS Code 左侧文件栏里直接点开 PNG 看。

## 46. 怎么判断结果是否合理

你要分三层判断。

### 第一层：代码是否跑通

看到：

```text
done!
```

并且有 checkpoint 文件，说明跑通。

### 第二层：数据是否正确

看 `prepare_cwru.py` 打印的类别数量。

如果 CWRU 50:1 中训练集是：

```text
normal 1800
每个故障类 36
```

验证集和测试集每类 300，那么数据数量合理。

### 第三层：指标是否接近论文

论文 CWRU 50:1 的 CA-SupCon 结果大约是：

```text
Acc 83.12
F1  82.34
MCC 81.50
```

注意论文表格用百分数。

程序日志如果输出：

```text
TestAcc: 0.8312
TestF1: 0.8234
TestMCC: 0.8150
```

换成百分数就是：

```text
83.12
82.34
81.50
```

## 47. 为什么你的结果可能和论文不完全一样

原因包括：

1. 论文没有公开每个窗口的具体划分索引。
2. PyTorch 版本可能不同。
3. CUDA/GPU 计算有随机性。
4. 数据下载源虽然是同一数据集，但文件处理细节可能有差异。
5. 论文报告的是 10 次均值，不是单次结果。

所以严谨说法应该是：

> 单次结果应该趋势接近；要复现论文表格，需要 10 个 seed 重复实验并计算均值和标准差。

## 48. 怎样跑 10 次

可以手动改 seed 跑。

例如 CWRU 50:1：

```bash
python main/main.py --dataset cwru --exp_name supcon --cfg_name casupcon --imb_desc all_equal_ratio_0.02 --seed 0
python main/main.py --dataset cwru --exp_name supcon --cfg_name casupcon --imb_desc all_equal_ratio_0.02 --seed 1
python main/main.py --dataset cwru --exp_name supcon --cfg_name casupcon --imb_desc all_equal_ratio_0.02 --seed 2
```

一直到：

```bash
python main/main.py --dataset cwru --exp_name supcon --cfg_name casupcon --imb_desc all_equal_ratio_0.02 --seed 9
```

然后从每次日志中记录：

```text
TestAcc
TestF1
TestMCC
```

再计算平均值和标准差。

## 49. TE 数据怎么理解

TE 是 Tennessee-Eastman 过程数据。

它不是轴承振动，而是一个化工过程仿真数据。

它有很多变量：

```text
41 个测量变量 + 12 个操作变量 = 53 个变量
```

论文和代码里实际输入是：

```text
52 x 200
```

可以简单理解为：

> 每个样本是 52 个变量连续 200 个时间点。

TE 的处理比 CWRU 更复杂，而且原始文件很大。

如果你刚入门，建议先把 CWRU 完整跑通，再做 TE。

## 50. 常见错误：No such file

如果看到：

```text
No such file or directory
```

通常说明数据还没准备好，或者路径不对。

检查：

1. 你是否在 `/Users/hadley/Desktop/UESTC/CA-SupCon` 目录。
2. 是否运行过 `python scripts/prepare_cwru.py`。
3. `--imb_desc` 是否和数据文件夹名字一致。

例如你运行：

```bash
--imb_desc all_equal_ratio_0.02
```

那么数据应该在：

```text
output/cwru/Train1800_Val300_Test300/imbalanced/all_equal_ratio_0.02/data/
```

## 51. 常见错误：No module named torch

如果看到：

```text
No module named torch
```

说明 PyTorch 没装在当前环境。

先确认虚拟环境已激活：

```bash
source .venv/bin/activate
```

再安装依赖：

```bash
pip install -r requirements.txt
```

## 52. 常见错误：下载中断

如果看到：

```text
curl: (18) transfer closed
```

意思是服务器提前断开连接。

解决方法：

```bash
python scripts/prepare_cwru.py
```

重新运行即可。脚本会继续下载 `.part` 文件。

## 53. 常见错误：训练很慢

如果你用：

```text
--device cpu
```

训练会慢。

这是正常的。

正式复现实验最好使用 GPU。

smoke test 用 CPU 就可以。

## 54. 这次工程相对官方代码补了什么

官方 GitHub 仓库只给了核心训练代码，不完整。

本工程补了：

1. `requirements.txt`：依赖清单。
2. `lib/utils.py`：日志、随机种子、指标、数据增强。
3. `lib/dataprep/__init__.py`：兼容官方入口缺失模块。
4. `scripts/prepare_cwru.py`：CWRU 下载和预处理。
5. `scripts/prepare_te.py`：TE 预处理。
6. `scripts/make_smoke_data.py`：小规模假数据测试。
7. 指标输出：Acc、macro-F1、MCC。
8. 修复 checkpoint 保存时引用不存在 `PROJECTION_HEAD` 的 bug。
9. 这份零基础文档和复现说明文档。

## 55. 最后给你一条最小路线

如果你现在只想知道“我该按什么顺序做”，按下面走：

```bash
cd /Users/hadley/Desktop/UESTC/CA-SupCon
```

```bash
source .venv/bin/activate
```

如果 `.venv` 不存在：

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

先检查代码：

```bash
python scripts/make_smoke_data.py --dataset cwru
python main/main.py --dataset cwru --exp_name supcon --cfg_name casupcon --imb_desc smoke --epochs 1 --device cpu
```

准备真实 CWRU：

```bash
python scripts/prepare_cwru.py
```

跑 CWRU 50:1：

```bash
python main/main.py --dataset cwru --exp_name supcon --cfg_name casupcon --imb_desc all_equal_ratio_0.02
```

看最后的：

```text
TestAcc
TestF1
TestMCC
Per class accuracy
```

这就是你和论文表格对比的核心结果。

## 56. 当前已经做到哪一步

当前工程已经完成：

1. CWRU 10 个真实 `.mat` 文件已经下载到 `data_raw/cwru/`。
2. CWRU 4 组不平衡率数据已经生成到 `output/cwru/Train1800_Val300_Test300/imbalanced/`。
3. TE random-window 4 组不平衡率数据已经生成到 `output/te/train-2000_val-1000_test-1000_random-window/imbalanced/`。
4. fake smoke data 已经跑通过。
5. CWRU 和 TE 都已经完成严格论文口径复现：四个不平衡比例、每个比例 10 个 seed、每个 seed 50 epochs。
6. CWRU 和 TE 的 mean ± std 汇总 CSV、总结果图、论文对比图都已经输出到 `output/`。

最终正式结果文件：

```text
output/cwru_mean_std.csv
output/te_mean_std.csv
output/ca_supcon_experiment_summary.png
output/ca_supcon_experiment_summary.pdf
output/ca_supcon_vs_paper.png
output/ca_supcon_vs_paper.pdf
output/ca_supcon_vs_paper.csv
```

最终 CWRU 结果：

```text
Ratio  Acc          Macro-F1     MCC
0.20   93.01±0.36   93.01±0.36   92.24±0.40
0.10   91.60±0.52   91.63±0.52   90.68±0.58
0.05   90.92±0.32   90.92±0.32   89.92±0.36
0.02   87.28±0.73   87.38±0.71   85.89±0.82
```

最终 TE random-window 结果：

```text
Ratio  Acc          Macro-F1     MCC
0.20   94.84±0.95   94.67±1.17   94.61±0.95
0.10   87.99±0.80   86.91±1.49   87.63±0.83
0.05   85.68±0.90   84.20±1.40   85.46±0.73
0.02   85.17±0.74   83.04±0.87   85.40±0.59
```

和论文 Acc 对比：

```text
CWRU 0.20: +5.56
CWRU 0.10: +4.24
CWRU 0.05: +7.02
CWRU 0.02: +4.16
TE   0.20: +2.86
TE   0.10: -1.54
TE   0.05: -2.11
TE   0.02: +1.90
```

结论：

> CWRU 四个不平衡比例全部超过论文。TE 的 0.20 和 0.02 超过论文，0.10 和 0.05 略低于论文，但已经接近论文水平；旧 TE sequential 抽样导致的严重偏低问题已经通过 random-window 数据构造解决。

## 57. 代码阅读路线：从一条命令开始

你运行训练时输入的是：

```bash
python main/main.py --dataset cwru --exp_name supcon --cfg_name casupcon --imb_desc all_equal_ratio_0.02
```

这条命令可以拆成两部分：

```text
python main/main.py
```

意思是：

> 用 Python 执行 `main/main.py` 这个文件。

后面的：

```text
--dataset cwru --exp_name supcon --cfg_name casupcon --imb_desc all_equal_ratio_0.02
```

是传给程序的参数。

程序运行路线是：

```text
main/main.py
-> lib/utils.py 解析命令行参数
-> configs/cwru/supcon/casupcon.yaml 读取实验配置
-> lib/dataloader/load_data.py 构造 train/val/test DataLoader
-> lib/dataset/cwru_dataset_shuffle.py 读取 CWRU txt 数据
-> lib/sampler/class_aware_sampler.py 训练集类别均衡采样
-> lib/core/run_supcon.py 创建模型、优化器、loss
-> lib/backbone/cnn1d_cwru.py 提取特征
-> lib/backbone/dot_product_classifier.py 分类
-> lib/loss/SupCon.py 计算监督对比损失
-> lib/loss/CrossEntropy.py 计算分类损失
-> lib/core/run_supcon.py 训练、验证、测试、保存模型
```

这就是整套代码的主线。

## 58. `main/main.py` 逐行解释

文件位置：

```text
main/main.py
```

这个文件是训练入口。你运行命令时，Python 最先执行它。

### 第 1 行

```python
import _init_paths
```

作用：

> 把 `lib/` 加入 Python 搜索路径。

为什么需要？

因为后面要写：

```python
from utils import ...
from dataloader import ...
from core import ...
```

这些模块都在 `lib/` 下面。如果不先改路径，Python 可能找不到它们。

### 第 2 行

```python
from utils import seed_everything, create_parser, create_logger, apply_cli_overrides
```

作用：

从 `lib/utils.py` 里导入 4 个函数：

- `create_parser`：读取命令行参数
- `apply_cli_overrides`：用命令行参数覆盖 yaml 配置
- `create_logger`：创建日志
- `seed_everything`：固定随机种子

### 第 3 行

```python
from dataprep import *
```

这是官方代码保留的导入。

本工程里 `dataprep` 是一个兼容空模块，因为公开仓库里原本引用它但没有提供内容。

它现在的作用是：

> 保证官方入口不报 `No module named dataprep`。

### 第 4 行

```python
from dataloader import load_data
```

导入数据加载函数。

后面会用它分别创建：

```text
train dataloader
val dataloader
test dataloader
```

### 第 5 行

```python
from core import *
```

导入核心训练类。

实际用到的是：

```python
Model_SupCon
```

### 第 7-9 行

```python
import yaml
import os
import numpy as np
```

导入第三方或标准库：

- `yaml`：读取 `.yaml` 配置文件
- `os`：拼路径、设置环境变量
- `numpy`：数值计算库

这里 `numpy` 在当前文件里没有直接用到，是官方代码遗留导入，不影响运行。

### 第 12 行

```python
def main():
```

定义主函数。

真正的训练流程都写在这个函数里。

### 第 13 行

```python
args = create_parser()
```

读取你在命令行输入的参数。

例如你输入：

```bash
--dataset cwru
```

那么程序内部：

```python
args.dataset == "cwru"
```

如果你输入：

```bash
--imb_desc all_equal_ratio_0.02
```

那么程序内部：

```python
args.imb_desc == "all_equal_ratio_0.02"
```

### 第 15 行

```python
cfg_name = "{}.yaml".format(args.cfg_name)
```

把配置名变成 yaml 文件名。

你输入：

```bash
--cfg_name casupcon
```

程序就变成：

```text
casupcon.yaml
```

### 第 16 行

```python
cfg_path = os.path.join("configs", args.dataset, args.exp_name, cfg_name)
```

拼出配置文件路径。

如果：

```text
dataset = cwru
exp_name = supcon
cfg_name = casupcon.yaml
```

那么路径就是：

```text
configs/cwru/supcon/casupcon.yaml
```

### 第 19-20 行

```python
with open(cfg_path) as f:
    config = yaml.load(f, Loader = yaml.FullLoader)
```

打开 yaml 配置文件并读成 Python 字典。

读完后，`config` 大概长这样：

```python
config["DATASET_NAME"] == "cwru"
config["DATALOADER"]["BATCH_SIZE"] == 60
config["TRAINING_OPT"]["NUM_EPOCHS"] == 50
```

### 第 21 行

```python
config = apply_cli_overrides(config, args)
```

用命令行参数覆盖 yaml。

例如 yaml 里默认：

```yaml
IMB_DESC: "all_equal_ratio_0.2"
```

但你命令行输入：

```bash
--imb_desc all_equal_ratio_0.02
```

这一行会把配置改成：

```python
config["IMB_DESC"] == "all_equal_ratio_0.02"
```

所以命令行优先级更高。

### 第 23 行

```python
logger = create_logger(config)
```

创建日志系统。

之后所有：

```python
logger.info(...)
```

都会同时输出到：

1. 控制台
2. `.log` 文件

### 第 25 行

```python
seed_everything(logger, config["SEED"])
```

固定随机种子。

作用：

> 尽量让每次运行结果可复现。

它会固定：

- Python random
- NumPy random
- PyTorch random
- CUDA random

### 第 27 行

```python
splits = config["DATASET"]["SPLITS"]
```

读取数据划分。

yaml 里是：

```yaml
SPLITS: ["train", "val", "test"]
```

所以：

```python
splits == ["train", "val", "test"]
```

### 第 29-30 行

```python
os.environ['CUDA_VISIBLE_DEVICES'] = config["TRAINING_OPT"]["CUDA_VISIBLE_DEVICES"]
logger.info(...)
```

设置 GPU 可见编号，并写进日志。

如果你用 CPU：

```bash
--device cpu
```

本工程会把 `CUDA_VISIBLE_DEVICES` 设为空。

### 第 32 行

```python
dataloader_dict = {split: load_data(config, logger, phase = split) for split in splits}
```

这是非常关键的一行。

它等价于：

```python
dataloader_dict = {}
dataloader_dict["train"] = load_data(config, logger, phase="train")
dataloader_dict["val"] = load_data(config, logger, phase="val")
dataloader_dict["test"] = load_data(config, logger, phase="test")
```

最后得到：

```python
dataloader_dict["train"]
dataloader_dict["val"]
dataloader_dict["test"]
```

训练时用 train。

每轮结束用 val。

最后报告用 test。

### 第 34 行

```python
model = Model_SupCon(config, dataloader_dict, logger)
```

创建 CA-SupCon 模型对象。

这一步会进入：

```text
lib/core/run_supcon.py
```

里面会创建：

- backbone
- classifier
- optimizer
- CE loss
- SupCon loss

### 第 35-38 行

```python
if (config["MODE"] in ["train_supcon", "train_linear", "fine_tune"]):
    model.train()
elif (config["MODE"] == "test"):
    model.eval_ce("test", True)
```

根据配置决定做什么。

当前 yaml 里：

```yaml
MODE: "train_supcon"
```

所以会执行：

```python
model.train()
```

也就是正式训练。

### 第 40 行

```python
print("\ndone!")
```

所有流程结束后打印：

```text
done!
```

你看到它，说明程序正常走完。

### 第 43-44 行

```python
if __name__ == '__main__':
    main()
```

意思是：

> 如果这个文件是被直接运行的，就调用 `main()`。

你运行：

```bash
python main/main.py ...
```

所以它会进入 `main()`。

## 59. 配置文件 `casupcon.yaml` 怎么读

文件位置：

```text
configs/cwru/supcon/casupcon.yaml
```

你可以把 yaml 理解成：

> 实验参数说明书。

里面写了数据、模型、训练、loss 的所有设置。

### 数据集部分

```yaml
DATASET_NAME: "cwru"
DATASET_DESC: "Train1800_Val300_Test300"
IMBALANCED: True
IMB_DESC: "all_equal_ratio_0.2"
```

解释：

- `DATASET_NAME`：数据集叫 cwru
- `DATASET_DESC`：数据规模描述
- `IMBALANCED`：使用不平衡数据
- `IMB_DESC`：默认不平衡率

注意：

你命令行传了：

```bash
--imb_desc all_equal_ratio_0.02
```

所以实际运行时会覆盖 yaml 默认值。

### 数据增强部分

```yaml
TRANSFORM_TYPE: [["Jitter", "Scaling", "MakeNoise", "Translation"]]
K: 2
```

意思是：

> 训练时对每个样本做 Jitter、Scaling、MakeNoise、Translation 组合增强，并生成 2 个增强视图。

SupCon 需要两个视图，所以 `K=2`。

### DataLoader 部分

```yaml
BATCH_SIZE: 60
SAMPLER_CLASS: "ClassAwareSampler"
NUM_SAMPLER_CLS: 6
```

意思是：

- 每个 batch 有 60 个样本
- 训练集使用 class-aware sampler
- 每次从同一类别连续取 6 个样本

CWRU 有 10 类，所以大致形成：

```text
10 类 * 每类 6 个 = 60 个样本
```

### 网络部分

```yaml
MODEL_CREATE_FUNC: "create_cnn1d_cwru"
PARAMS: {seq_len: 400, num_blocks: 2, planes: [10, 10, 10], kernel_size: 10, pool_size: 2, linear_plane: 100}
```

意思是：

使用 `create_cnn1d_cwru` 创建 backbone。

输入信号长度是 400。

输出特征维度是 100。

### 分类器部分

```yaml
PARAMS: {linear_plane: 100, num_classes: 10}
```

意思是：

分类器输入 100 维特征，输出 10 个类别。

### loss 部分

```yaml
temperature: 0.1
base_temperature: 0.1
```

这是 SupCon loss 的温度系数。

温度系数会影响不同样本相似度的放大程度。

论文 CWRU 里使用 `0.1`。

### 训练部分

```yaml
NUM_EPOCHS: 50
NUM_CLASSES: 10
```

意思是：

训练 50 轮，类别数 10。

## 60. `load_data.py` 逐行解释

文件位置：

```text
lib/dataloader/load_data.py
```

它的任务是：

> 根据配置创建 PyTorch DataLoader。

DataLoader 可以理解成：

> 每次训练时帮你一批一批拿数据的工具。

### 第 1-6 行

```python
from torch.utils import data
from dataset import *
from sampler import ClassAwareSampler
from torch.utils.data import DataLoader
import os
```

导入需要的工具：

- `dataset`：数据集类，比如 `CWRUDatasetShuffle`
- `ClassAwareSampler`：类别感知采样器
- `DataLoader`：PyTorch 批量取数据工具
- `os`：拼路径

### 第 8 行

```python
def load_data(cfg, logger, phase):
```

定义函数。

参数：

- `cfg`：配置字典
- `logger`：日志
- `phase`：当前是 `"train"`、`"val"` 还是 `"test"`

### 第 10-17 行

这几行决定数据目录。

如果 yaml 里手动写了 `DATA_ROOT`，就用它。

否则自动拼路径：

```text
output/cwru/Train1800_Val300_Test300/imbalanced/all_equal_ratio_0.02/data
```

这就是你真实 CWRU 50:1 数据所在的位置。

### 第 19-22 行

```python
if "cwru" in cfg["DATASET_NAME"]:
    data_txt = "{}_set.txt".format(phase)
elif "te" in cfg["DATASET_NAME"]:
    data_txt = "{}_set.npy".format(phase)
```

如果是 CWRU：

```text
train -> train_set.txt
val   -> val_set.txt
test  -> test_set.txt
```

如果是 TE：

```text
train -> train_set.npy
```

CWRU 用 txt，TE 用 npy。

### 第 24-26 行

```python
transforms = cfg["DATASET"]["TRANSFORMS"]
dataset = eval(cfg["DATASET"]["DATASET_CLASS"])(...)
```

读取增强配置。

然后创建数据集对象。

CWRU 配置里：

```yaml
DATASET_CLASS: "CWRUDatasetShuffle"
```

所以实际执行的是：

```python
dataset = CWRUDatasetShuffle(data_root, data_txt, transforms, logger, phase)
```

### 第 29-34 行

读取 DataLoader 参数：

- sampler 类
- 每类取几个样本
- batch size
- 是否 shuffle
- 是否丢掉最后不足一个 batch 的数据
- worker 数量

### 第 36-41 行

如果当前是训练集，并且配置了 sampler：

```python
sampler = ClassAwareSampler(...)
return DataLoader(..., sampler=sampler)
```

也就是说：

> 训练集不用普通随机采样，而用 class-aware sampler。

### 第 43-47 行

如果是训练集但没有自定义 sampler，就用普通 DataLoader。

当前 CA-SupCon 不走这里，因为配置里有 `ClassAwareSampler`。

### 第 49-52 行

如果是验证集或测试集：

```python
shuffle=False
drop_last=False
```

为什么？

验证和测试要稳定，不能随机打乱，也不能丢样本。

## 61. `CWRUDatasetShuffle` 逐行解释

文件位置：

```text
lib/dataset/cwru_dataset_shuffle.py
```

这个类负责：

> 读取 CWRU 的 `train_set.txt`、`val_set.txt`、`test_set.txt`，并在训练时返回增强样本。

### 第 1-6 行

导入：

- PyTorch
- Dataset 基类
- os
- numpy
- utils 里的增强函数

### 第 9 行

```python
class CWRUDatasetShuffle(Dataset):
```

定义一个 PyTorch 数据集类。

只要继承 `Dataset`，就必须提供：

```python
__getitem__
__len__
```

### 第 10-17 行

```python
self.data_path = os.path.join(data_root, data_txt)
self.data = np.loadtxt(self.data_path)
self.sequence = torch.from_numpy(self.data[:,:-1])
self.label = torch.from_numpy(self.data[:,-1]).long()
```

解释：

`train_set.txt` 每一行是：

```text
400 个信号值 + 1 个标签
```

所以：

```python
self.data[:,:-1]
```

取前 400 列，作为信号。

```python
self.data[:,-1]
```

取最后 1 列，作为标签。

### 第 20-23 行

```python
if len(self.sequence.shape) < 3:
    self.sequence = self.sequence.unsqueeze(2)
if self.sequence.shape.index(min(self.sequence.shape)) != 1:
    self.sequence = self.sequence.permute(0, 2, 1)
```

神经网络 Conv1d 需要输入形状：

```text
[样本数, 通道数, 序列长度]
```

CWRU 最终要变成：

```text
[N, 1, 400]
```

其中：

- `N`：样本数
- `1`：一个振动通道
- `400`：窗口长度

这几行就是调整维度。

### 第 25-35 行

如果是训练集，并且启用增强：

```python
self.transforms_list = []
```

开始构建增强流水线。

配置里写的是：

```text
Jitter -> Scaling -> MakeNoise -> Translation
```

代码会把这些名字变成真正的增强对象。

`self.K = 2` 表示每个样本生成 2 个增强版本。

### 第 37-42 行

写日志。

你在控制台看到的：

```text
the shape of sequence data: torch.Size([2124, 1, 400])
```

就是这里打印的。

### 第 45 行

```python
def __getitem__(self, index):
```

当 DataLoader 需要第 `index` 个样本时，会调用这个函数。

### 第 46-51 行

训练阶段：

```python
data_transformed_list = []
for transform in self.transforms_list:
    for _ in range(self.K):
        data_transformed = transform(self.sequence[index])
        data_transformed_list.append(data_transformed)
```

意思是：

> 对当前样本做 2 次随机增强，得到两个增强视图。

SupCon loss 会用这两个视图。

### 第 52-54 行

验证或测试阶段：

```python
data_transformed_list.append(self.sequence[index])
```

不做增强，直接返回原始样本。

为什么？

验证和测试要评估真实输入，不应该随机扰动。

### 第 56 行

```python
return self.sequence[index], self.label[index], data_transformed_list
```

每次返回三个东西：

```text
原始样本
标签
两个增强样本
```

训练循环中对应：

```python
data, target, data_transformed_list
```

### 第 59-60 行

```python
def __len__(self):
    return self.label.shape[0]
```

告诉 DataLoader 数据集总共有多少个样本。

## 62. `ClassAwareSampler` 逐行解释

文件位置：

```text
lib/sampler/class_aware_sampler.py
```

它的任务是：

> 让训练 batch 内类别更均衡。

### 第 1-3 行

导入：

- `random`：打乱类别或样本
- `numpy`：统计类别
- `Sampler`：PyTorch 采样器基类

### 第 5-26 行：`RandomCycleIter`

这个类是一个循环迭代器。

比如数据是：

```python
[0, 1, 2]
```

它会不断返回：

```text
0, 1, 2, 然后打乱，再继续
```

这样采样不会停。

第 18-26 行是核心：

```python
self.i += 1
if self.i == self.length:
    self.i = 0
    random.shuffle(self.data_list)
return self.data_list[self.i]
```

意思是：

> 到末尾后重新从头开始，并随机打乱顺序。

### 第 29-44 行：`class_aware_sample_generator`

这是真正生成样本 index 的函数。

关键变量：

- `cls_iter`：类别迭代器
- `data_iter_list`：每个类别自己的样本 index 迭代器
- `n`：总共要生成多少 index
- `num_samples_cls`：每次同一类连续取几个样本

对 CWRU：

```text
num_samples_cls = 6
```

所以它会：

```text
选一个类别 -> 从这个类别取 6 个样本
再选下一个类别 -> 取 6 个样本
...
```

### 第 47 行

```python
class ClassAwareSampler(Sampler):
```

定义 PyTorch 采样器。

### 第 52-63 行

初始化采样器。

第 53 行：

```python
num_classes = len(np.unique(dataset.label))
```

统计类别数。

CWRU 是 10。

第 55 行：

```python
self.class_iter = RandomCycleIter(range(num_classes))
```

创建类别循环器。

第 57-59 行：

```python
cls_data_list = [list() for _ in range(num_classes)]
for i, label in enumerate(dataset.label):
    cls_data_list[int(label)].append(i)
```

把每个样本 index 放进对应类别。

例如：

```text
类别 0: [0, 4, 8, ...]
类别 1: [1, 7, 20, ...]
```

第 61 行：

```python
self.data_iter_list = [RandomCycleIter(x) for x in cls_data_list]
```

每个类别都有自己的循环采样器。

第 62 行：

```python
self.num_samples = max([len(x) for x in cls_data_list]) * len(cls_data_list)
```

让一个 epoch 的采样长度等于：

```text
最大类别样本数 * 类别数
```

在 CWRU 50:1 中：

```text
最大类别样本数 = normal 的 1800
类别数 = 10
num_samples = 18000
```

这就是你日志里看到：

```text
TrainNum: 18000
```

的原因。

注意：

原始训练集实际只有：

```text
1800 + 9 * 36 = 2124
```

但 sampler 会循环重复少数类，让一个 epoch 里每类都有更多机会出现。

### 第 66-68 行

```python
def __iter__(self):
    return class_aware_sample_generator(...)
```

DataLoader 每次需要采样顺序时，会调用它。

### 第 71-72 行

```python
def __len__(self):
    return self.num_samples
```

告诉 DataLoader 一个 epoch 里有多少采样结果。

## 63. CWRU backbone 逐行解释

文件位置：

```text
lib/backbone/cnn1d_cwru.py
```

这个文件定义 1D-ResNet。

它负责：

> 把 `[batch, 1, 400]` 的振动信号变成 `[batch, 100]` 的特征向量。

### 第 1-7 行

这是文件说明和引用。

说明它实现的是用于故障诊断的 ResNet 结构。

### 第 9-11 行

导入 PyTorch：

- `torch`
- `torch.nn`
- `torch.nn.functional`

其中：

```python
nn.Module
```

是所有神经网络模块的基类。

### 第 14-40 行：`BasicBlock`

这是 ResNet 的基本块。

输入：

```text
x
```

经过：

```text
Conv1d -> BatchNorm -> ReLU -> Conv1d -> BatchNorm
```

然后加上 shortcut：

```text
out = 主分支输出 + shortcut(x)
```

再 ReLU。

这就是 ResNet 的残差连接。

残差连接的作用：

> 让网络更容易训练，避免层数加深后信息丢失。

### 第 18-21 行

```python
self.conv1 = nn.Conv1d(...)
self.bn1 = nn.BatchNorm1d(...)
self.conv2 = nn.Conv1d(...)
self.bn2 = nn.BatchNorm1d(...)
```

定义主分支的两层 1D 卷积。

1D 卷积适合时间序列信号，比如振动信号。

### 第 23-26 行

```python
self.shortcut = nn.Sequential(...)
```

定义 shortcut 分支。

因为输入通道数和输出通道数可能不同，所以用 `1x1` 卷积对齐维度。

### 第 29-40 行

这是 BasicBlock 的前向传播。

前向传播就是：

> 输入数据真正流过网络的过程。

关键顺序：

```text
保存原长度
卷积
BN
ReLU
裁剪回原长度
卷积
BN
裁剪回原长度
加 shortcut
ReLU
返回
```

为什么有裁剪？

因为卷积 padding 后长度有时会多 1，裁剪保证长度和输入一致，方便残差相加。

### 第 43-76 行：`ResNetCWRU`

这是完整 CWRU backbone。

第 50-52 行：

```python
self.conv1 = nn.Conv1d(1, 10, ...)
self.bn1 = nn.BatchNorm1d(10)
self.layer = self._make_layer(...)
```

第一层把 1 通道信号变成 10 通道特征。

然后进入残差层。

第 54 行：

```python
self.linear = nn.Linear(..., linear_plane)
```

最后把展开后的特征变成 100 维。

### 第 57-66 行：`_make_layer`

创建多个 BasicBlock。

配置里：

```text
num_blocks = 2
pool_size = 2
```

所以结构大概是：

```text
BasicBlock
MaxPool1d
BasicBlock
```

MaxPool 会把序列长度从 400 压到 200。

### 第 69-76 行：`forward`

模型真正运行时走这里。

输入：

```text
[batch, 1, 400]
```

经过第一层卷积：

```text
[batch, 10, 400]
```

经过残差层和池化：

```text
[batch, 10, 200]
```

展开：

```text
[batch, 2000]
```

全连接：

```text
[batch, 100]
```

这 100 维就是后面 SupCon 和分类器共同使用的特征。

### 第 81-93 行

```python
def create_cnn1d_cwru(...)
```

这是工厂函数。

训练代码不会直接写：

```python
ResNetCWRU(...)
```

而是从 yaml 读到函数名：

```text
create_cnn1d_cwru
```

再调用这个函数创建模型。

## 64. 分类器 `dot_product_classifier.py` 逐行解释

文件位置：

```text
lib/backbone/dot_product_classifier.py
```

这个分类器很简单。

### 第 1 行

```python
import torch.nn as nn
```

导入神经网络模块。

### 第 3 行

```python
class DotProduct_Classifier(nn.Module):
```

定义分类器类。

### 第 5-7 行

```python
def __init__(self, linear_plane, num_classes):
    super(...)
    self.fc = nn.Linear(linear_plane, num_classes)
```

创建一个全连接层。

CWRU 中：

```text
linear_plane = 100
num_classes = 10
```

所以：

```text
输入 100 维特征
输出 10 个类别 logit
```

logit 是还没经过 softmax 的分类分数。

### 第 9-11 行

```python
def forward(self, x):
    x = self.fc(x)
    return x
```

输入 100 维特征，输出 10 类分数。

例如：

```text
[batch, 100] -> [batch, 10]
```

### 第 14-20 行

和 backbone 一样，这是工厂函数。

yaml 里写：

```text
create_dot_product_classifier
```

训练代码根据这个名字创建分类器。

## 65. `run_supcon.py` 训练核心逐行解释

文件位置：

```text
lib/core/run_supcon.py
```

这是最重要的文件。

它负责：

1. 创建模型
2. 创建优化器
3. 创建 loss
4. 训练每个 epoch
5. 验证模型
6. 保存最好 checkpoint
7. 测试模型

### 第 1-11 行

导入依赖。

```python
import torch
import torch.optim as optim
import torch.nn.functional as F
```

分别用于：

- 张量计算
- 优化器 Adam
- softmax、normalize 等函数

```python
from tqdm import tqdm
```

用于显示进度条。

```python
from utils import total_acc_cal, each_cls_acc_cal, classification_metrics
```

导入指标函数。

```python
from backbone import *
from loss import create_ce_loss, create_supcon_loss
```

导入模型和 loss 创建函数。

### 第 13 行

```python
class Model_SupCon(object):
```

定义训练管理类。

它不是单纯的神经网络，而是一个“训练器”。

### 第 14-43 行：初始化

```python
def __init__(self, cfg, dataloader_dict, logger):
```

传入：

- 配置
- train/val/test dataloader
- 日志

第 23 行：

```python
self.device = torch.device(...)
```

决定用 GPU 还是 CPU。

如果你传：

```bash
--device cpu
```

就用 CPU。

第 28-30 行：

```python
self._init_models()
self._init_optimizers()
self._init_criterions()
```

依次创建：

1. 网络模型
2. 优化器
3. 损失函数

第 43 行：

```python
self.lamda = self.cfg["LAMDA"]
```

读取总损失里的 `lambda`。

论文中是 1。

### 第 46-61 行：创建模型

```python
self.networks_defs = self.cfg["NETWORKS"]
self.networks = {}
```

准备一个字典保存模型。

配置里有两个网络：

```text
FEAT_MODEL
CLASSIFIER
```

第 52-54 行：

```python
for key, val in self.networks_defs.items():
    model_args = val["PARAMS"]
    self.networks[key] = eval(val["MODEL_CREATE_FUNC"])(...)
```

意思是：

> 遍历 yaml 里的网络配置，根据函数名创建网络。

对于 CWRU：

```text
FEAT_MODEL -> create_cnn1d_cwru
CLASSIFIER -> create_dot_product_classifier
```

创建完以后放进：

```python
self.networks["FEAT_MODEL"]
self.networks["CLASSIFIER"]
```

### 第 94-103 行：创建优化器

这部分创建 Adam 优化器。

它会把 backbone 和 classifier 的参数都放进优化器。

配置里：

```text
lr = 0.0003
weight_decay = 0.0003
```

所以训练时两个网络都会被更新。

### 第 120-130 行：创建 loss

配置里有：

```text
CE_LOSS
CL_LOSS
```

所以这里会创建：

```python
self.criterions["CE_LOSS"]
self.criterions["CL_LOSS"]
```

其中：

- `CE_LOSS`：交叉熵
- `CL_LOSS`：SupCon

### 第 133-152 行：模型保存路径

这部分拼出 checkpoint 路径。

CWRU 50:1 会保存到：

```text
output/cwru/Train1800_Val300_Test300/imbalanced/all_equal_ratio_0.02/models/supcon/ca_supcon/cnn1d-cwru/supcon_train_supcon.pth
```

### 第 155-168 行：保存模型

```python
torch.save(model_states, model_file_path)
```

保存：

- 当前 epoch
- 最好 epoch
- 最好模型参数
- 最好验证集准确率

### 第 188 行：进入训练

```python
def train(self):
```

这是训练主函数。

### 第 190-195 行

初始化：

- `best_model_weights`：最好模型权重
- `best_acc`：最好验证准确率
- `best_epoch`：最好 epoch 编号
- `end_epoch`：总 epoch 数

### 第 201 行

```python
for epoch in range(1, end_epoch + 1):
```

从第 1 轮训练到第 50 轮。

你日志里的：

```text
Epoch: [29/50]
```

就是这里来的。

### 第 204-205 行

```python
for model in self.networks.values():
    model.train()
```

把所有网络切换到训练模式。

训练模式会影响 BatchNorm、Dropout 等层。

### 第 208-212 行

创建列表和空张量，用来记录本轮：

- total loss
- supcon loss
- ce loss
- 预测标签
- 真实标签

### 第 214 行

```python
for step, (data, target, data_transformed_list) in enumerate(tqdm(self.dataloader_dict["train"])):
```

这是每个 epoch 里的 batch 循环。

每次 DataLoader 返回：

```text
data: 原始样本
target: 标签
data_transformed_list: 两个增强样本
```

`tqdm` 就是你看到的进度条。

### 第 220 行

```python
data, target = data.float().to(self.device), target.long().to(self.device)
```

把数据转成正确类型，并放到 CPU/GPU。

信号要是 float。

标签要是 long，因为交叉熵需要整数类别标签。

### 第 223-224 行

```python
data_transformed1, data_transformed2 = ...
```

取出两个增强视图。

SupCon 要用它们来做对比学习。

### 第 226 行

```python
self.model_optimizer.zero_grad()
```

清空上一批留下的梯度。

训练神经网络每个 batch 都要先清梯度。

### 第 228-233 行

```python
feature1 = self.networks["FEAT_MODEL"](data_transformed1)
feature2 = self.networks["FEAT_MODEL"](data_transformed2)
feature1 = F.normalize(feature1, dim=1)
feature2 = F.normalize(feature2, dim=1)
```

两个增强样本分别进入 backbone。

得到两个 100 维特征。

然后做 L2 normalize。

normalize 后，特征长度变成 1。

这样点积可以当作余弦相似度。

### 第 235-236 行

```python
feature = self.networks["FEAT_MODEL"](data)
logit = self.networks["CLASSIFIER"](feature)
```

原始样本进入 backbone 和 classifier。

得到 10 个类别分数。

这条分支用于交叉熵分类。

### 第 238-240 行

```python
projection_feature = torch.cat([feature1.unsqueeze(1), feature2.unsqueeze(1)], dim=1)
sup_loss = self.criterions["CL_LOSS"](projection_feature, target)
```

把两个增强特征拼成 SupCon 需要的形状：

```text
[batch, 2, 100]
```

然后计算监督对比损失。

### 第 242 行

```python
ce_loss = self.criterions["CE_LOSS"](logit, target)
```

计算交叉熵分类损失。

### 第 244-247 行

```python
output = F.softmax(logit, 1)
_, preds = output.max(dim=1)
```

把 logit 转成概率。

取概率最大的类别作为预测结果。

然后把预测和真实标签保存起来，用于算训练准确率。

### 第 249-252 行

```python
total_loss = ce_loss + self.lamda * sup_loss
```

这是 CA-SupCon 的总损失。

当前：

```text
lambda = 1
```

所以：

```text
total_loss = ce_loss + sup_loss
```

### 第 254-256 行

把每个 batch 的 loss 数值保存到列表。

epoch 结束后会求平均。

### 第 258-259 行

```python
total_loss.backward()
self.model_optimizer.step()
```

这是神经网络真正学习的地方。

`backward()`：

> 计算每个参数应该怎么改。

`step()`：

> 用 Adam 优化器更新参数。

### 第 264-266 行

一个 epoch 结束后，计算并打印训练集准确率和 loss。

你日志里的：

```text
TrainLoss
TrainSupLoss
TrainCeLoss
TrainAcc
```

来自这里。

### 第 268 行

```python
total_eval_rsl = self.eval_ce(phase="val", display=False)
```

每个 epoch 结束后，在验证集上评估。

### 第 269-273 行

```python
if val accuracy > best_acc:
    保存当前模型为最好模型
```

这就是为什么你日志显示：

```text
Best validation accuracy is 0.874 at epoch 29
```

最后测试用的是第 29 轮的最好模型，不一定是第 50 轮。

### 第 275-284 行

训练完成后：

1. 打印训练完成
2. 保存最好 checkpoint
3. 恢复最好模型权重
4. 在 val 上再评估一次
5. 在 test 上最终评估

### 第 287-336 行：验证和测试

`eval_ce` 用于验证和测试。

第 292-293 行：

```python
model.eval()
```

切换到评估模式。

第 302 行：

```python
with torch.set_grad_enabled(False):
```

评估时不计算梯度，省内存、省时间。

第 303-304 行：

```python
feature = FEAT_MODEL(data)
logit = CLASSIFIER(feature)
```

验证/测试只用原始样本，不用增强。

第 314-319 行：

计算：

- Acc
- macro-F1
- MCC

第 321-323 行：

如果是验证集，打印：

```text
ValAcc
ValF1
ValMCC
```

第 325-334 行：

如果是测试集，打印：

```text
TestAcc
TestF1
TestMCC
Per class accuracy
```

## 66. SupCon loss 逐行解释

文件位置：

```text
lib/loss/SupCon.py
```

这个文件实现监督式对比损失。

### 第 1-3 行

导入 PyTorch。

`nn.Module` 用于定义 loss 类。

### 第 6 行

```python
class SupConLoss(nn.Module):
```

定义 SupCon loss。

### 第 7-14 行

初始化参数：

- `temperature`：温度系数
- `contrast_mode`：使用哪个视图做 anchor
- `base_temperature`：缩放用
- `similarity_function`：余弦相似度函数

当前 CWRU：

```text
temperature = 0.1
contrast_mode = all
base_temperature = 0.1
```

### 第 16 行

```python
def forward(self, features, labels=None, mask=None):
```

真正计算 loss 的函数。

输入：

```text
features shape = [batch, n_views, feature_dim]
```

当前是：

```text
[60, 2, 100]
```

### 第 17-21 行

检查 features 维度。

如果维度不够 3，会报错。

如果维度超过 3，会压平成：

```text
[batch, n_views, feature_dim]
```

### 第 23-34 行

根据标签创建 mask。

mask 是一个矩阵。

如果两个样本标签相同：

```text
mask[i, j] = 1
```

如果标签不同：

```text
mask[i, j] = 0
```

这个 mask 告诉 SupCon：

> 哪些样本是正样本，哪些不是。

### 第 36-37 行

```python
contrast_count = features.shape[1]
contrast_feature = torch.cat(torch.unbind(features, dim=1), dim=0)
```

把两个视图拼起来。

原来：

```text
[60, 2, 100]
```

变成：

```text
[120, 100]
```

### 第 39-46 行

如果 `contrast_mode == "all"`：

```python
anchor_feature = contrast_feature
anchor_count = contrast_count
```

意思是：

> 两个视图都当 anchor。

当前配置就是 `all`。

### 第 49-51 行

```python
anchor_dot_contrast = torch.matmul(anchor_feature, contrast_feature.T) / temperature
```

计算每个 anchor 和所有 contrast feature 的相似度。

因为前面做了 normalize，所以点积近似余弦相似度。

除以 temperature 是为了控制分布尖锐程度。

### 第 53-54 行

```python
logits = anchor_dot_contrast - logits_max.detach()
```

做数值稳定处理。

深度学习里指数运算容易溢出，减去最大值可以避免数值太大。

### 第 57-65 行

扩展 mask，并去掉“自己和自己对比”。

一个样本不能把自己当自己的正样本。

### 第 68-69 行

```python
exp_logits = torch.exp(logits) * logits_mask
log_prob = logits - torch.log(exp_logits.sum(1, keepdim=True))
```

这一步相当于计算 softmax 后的 log probability。

可以理解成：

> 在所有候选样本里，正样本相似度占多大优势。

### 第 72 行

```python
mean_log_prob_pos = (mask * log_prob).sum(1) / mask.sum(1)
```

只取正样本位置，求平均 log probability。

正样本越相似，这个值越好。

### 第 75-76 行

```python
loss = - (...) * mean_log_prob_pos
loss = loss.view(anchor_count, batch_size).mean()
```

把目标变成最小化 loss。

最终返回一个标量。

这个标量就是训练日志里的：

```text
TrainSupLoss
```

### 第 81-84 行

工厂函数。

训练代码通过它创建 SupCon loss。

## 67. `utils.py` 关键代码解释

文件位置：

```text
lib/utils.py
```

这是本复现工程补齐的工具文件。

### 第 12-23 行：命令行参数

```python
def create_parser():
```

定义你可以在命令行传哪些参数。

比如：

```bash
--dataset cwru
--imb_desc all_equal_ratio_0.02
--epochs 1
--device cpu
```

这里定义了，程序才能识别。

### 第 26-41 行：命令行覆盖 yaml

```python
def apply_cli_overrides(config, args):
```

如果你传了：

```bash
--epochs 1
```

它会把：

```python
config["TRAINING_OPT"]["NUM_EPOCHS"]
```

改成 1。

这就是为什么 smoke test 可以只跑 1 个 epoch。

### 第 44-74 行：日志

```python
def create_logger(config):
```

创建日志目录和日志文件。

它会同时输出到：

1. 控制台
2. `.log` 文件

### 第 77-87 行：固定随机种子

```python
def seed_everything(logger, seed):
```

固定随机性。

它不是保证 100% 完全一样，但能大幅提高可复现性。

### 第 90-96 行：总准确率

```python
def total_acc_cal(preds, labels):
```

计算：

```text
预测正确数 / 总样本数
```

### 第 99-117 行：每类准确率

```python
def each_cls_acc_cal(preds, labels):
```

逐类计算准确率。

你日志里的：

```text
Per class accuracy
```

来自这里。

### 第 120-147 行：Acc、macro-F1、MCC

```python
def classification_metrics(preds, labels, num_classes=None):
```

先创建混淆矩阵：

```python
confusion[y_true, y_pred] += 1
```

然后对每个类别计算 F1。

最后按论文公式计算 MCC。

### 第 150-158 行：Compose

```python
class Compose:
```

把多个增强操作串起来。

例如：

```text
Jitter -> Scaling -> MakeNoise -> Translation
```

一个样本会依次经过这些增强。

### 第 161-166 行：随机增强基类

```python
class _RandomTransform:
```

每个增强都有概率 `p`。

默认：

```text
p = 0.5
```

也就是 50% 概率执行，50% 概率跳过。

### 第 169-177 行：Jitter

加高斯噪声。

代码：

```python
return x + torch.randn_like(x) * self.sigma
```

意思是：

> 原信号 + 随机噪声。

### 第 180-190 行：Scaling

随机缩放幅值。

代码生成一个接近 1 的缩放系数，然后：

```python
return x * scale
```

### 第 193-202 行：MakeNoise

随机遮掉一部分点。

代码：

```python
keep_mask = (torch.rand_like(x) > self.sigma)
return x * keep_mask
```

mask 为 0 的位置会被置零。

### 第 205-213 行：Translation

随机平移序列。

代码：

```python
torch.roll(x, shifts=-shift, dims=-1)
```

意思是把时间序列循环移动。

## 68. 训练时一个 batch 的数据形状

以 CWRU 为例。

batch size 是 60。

原始输入：

```text
data.shape = [60, 1, 400]
```

标签：

```text
target.shape = [60]
```

第一个增强视图：

```text
data_transformed1.shape = [60, 1, 400]
```

第二个增强视图：

```text
data_transformed2.shape = [60, 1, 400]
```

经过 backbone：

```text
feature1.shape = [60, 100]
feature2.shape = [60, 100]
feature.shape  = [60, 100]
```

给 SupCon 的特征：

```text
projection_feature.shape = [60, 2, 100]
```

分类器输出：

```text
logit.shape = [60, 10]
```

预测类别：

```text
preds.shape = [60]
```

## 69. 一次完整训练的代码时间线

你可以按下面时间线理解每次训练。

### 程序启动

```text
main/main.py
```

读取命令行参数。

### 读取配置

```text
configs/cwru/supcon/casupcon.yaml
```

决定数据路径、模型、loss、epoch。

### 构造数据

```text
load_data("train")
load_data("val")
load_data("test")
```

读取 `train_set.txt`、`val_set.txt`、`test_set.txt`。

### 创建模型

```text
create_cnn1d_cwru
create_dot_product_classifier
```

得到 backbone 和 classifier。

### 创建 loss

```text
CrossEntropyLoss
SupConLoss
```

### 每个 epoch

```text
取 batch
做增强
backbone 提特征
算 SupCon loss
算 CE loss
总 loss
反向传播
更新参数
验证集评估
如果验证集更好就保存权重
```

### 训练结束

```text
加载最好权重
在测试集评估
打印 TestAcc/TestF1/TestMCC
保存 checkpoint
```

## 70. 你这次 50 epoch 结果在代码里是怎么产生的

你的日志里：

```text
Best validation accuracy is 0.874 at epoch 29
```

来自 `run_supcon.py` 的逻辑：

```text
每个 epoch 都 eval val
如果 ValAcc 超过历史最好
就把当前模型权重复制到 best_model_weights
```

训练到第 50 轮后，代码执行：

```python
self.reset_model(best_model_weights)
self.eval_ce(phase="test", display=False)
```

所以最终测试的是第 29 轮最好模型。

你的最终：

```text
TestAcc = 0.86500
TestF1  = 0.86610
TestMCC = 0.85136
```

来自 `eval_ce` 里：

```python
classification_metrics(eval_total_preds, eval_total_labels)
```

然后写入日志。

## 71. 如果你要改代码，最常改哪里

刚入门不要随便改核心训练逻辑。

如果只是实验，常改这些地方：

### 改 epoch

命令行加：

```bash
--epochs 1
```

或者改 yaml：

```yaml
NUM_EPOCHS: 50
```

### 改不平衡率

命令行改：

```bash
--imb_desc all_equal_ratio_0.02
```

### 改随机种子

命令行加：

```bash
--seed 1
```

### 改 CPU/GPU

CPU：

```bash
--device cpu
```

GPU：

```bash
--device cuda:0
```

### 改 batch size

改 yaml：

```yaml
BATCH_SIZE: 60
```

但不建议一开始改，因为 sampler 参数也和 batch size 有关系。

## 72. 哪些地方不要乱改

如果目标是复现论文，先不要改：

- backbone 结构
- SupCon loss 公式
- class-aware sampler
- 数据窗口长度
- validation/test 样本数
- temperature
- lambda

因为这些一改，就不是严格复现原论文设置了。

## 73. 新增可视化脚本怎么理解

文件位置：

```text
scripts/plot_training_log.py
```

作用：

> 从 `.log` 文件里提取指标，然后画图。

它做的事情：

1. 找到最新 log。
2. 用正则表达式提取 TrainLoss、ValAcc、ValF1、ValMCC、TestAcc、TestF1、TestMCC。
3. 用 matplotlib 画图。
4. 保存成 PNG。

运行：

```bash
python scripts/plot_training_log.py --log_dir output/cwru/Train1800_Val300_Test300/imbalanced/all_equal_ratio_0.02/logs/supcon/ca_supcon/cnn1d-cwru
```

输出：

```text
figures/xxx_summary.png
figures/xxx_per_class.png
```

`summary.png` 看整体训练过程。

`per_class.png` 看每个类别效果。

## 74. 最后再用一句话串起来

这套代码做的事就是：

```text
读取 CWRU 原始切窗数据
-> 用 class-aware sampler 让训练 batch 类别均衡
-> 对每个训练样本做两次增强
-> backbone 把信号变成 100 维特征
-> SupCon 让同类特征靠近、异类特征远离
-> classifier 用交叉熵学习分类
-> 每轮用验证集选最好模型
-> 最后用测试集输出 Acc、macro-F1、MCC 和每类准确率
```

如果你能把上面这条线讲清楚，就已经真正理解这份复现代码的主干了。

## 75. 零基础学习验收清单

看完这份入门手册后，不要求你马上能写新模型，但至少应该能做到下面这些事。

### 75.1 概念层面

你应该能解释：

```text
故障诊断是什么
分类任务是什么
样本和标签是什么
为什么长信号要切成窗口
训练集、验证集、测试集分别干什么
类别不平衡为什么会伤害模型
Acc、macro-F1、MCC、per-class accuracy 各自看什么
均值和标准差为什么比单次结果更可靠
```

### 75.2 项目层面

你应该能说清楚：

```text
main/main.py 是训练入口
configs/ 里放实验配置
lib/dataset/ 里读数据
lib/backbone/ 里放模型
lib/loss/ 里放损失函数
lib/sampler/ 里放 class-aware sampler
scripts/ 里放数据准备、批量训练、汇总和画图脚本
output/ 里放数据、日志、模型和图片
```

### 75.3 操作层面

你应该能独立完成：

```text
进入项目目录
激活或使用 .venv
跑一个 1 epoch smoke test
跑一个 CWRU 单次训练
找到最新 log
看懂 Epoch [x/50]
看懂 300/300 表示 batch 数
找到 TestAcc/TestF1/TestMCC
找到 per-class accuracy
知道什么时候可以开始多 seed
```

### 75.4 如果还不熟，下一步看什么

如果你卡在“怎么跑完整实验”，看：

```text
02_training_workflow_full_guide.md
```

如果你卡在“代码为什么这么写”，看：

```text
03_training_theory_to_code_deep_dive.md
```

如果你卡在“这个结果能不能算论文复现”，看：

```text
04_reproduction_notes.md
```

如果你卡在“以后怎么找创新点”，看：

```text
05_fault_diagnosis_review_market_and_innovation.md
```
