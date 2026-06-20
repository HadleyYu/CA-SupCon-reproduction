# Git、文档和结果图快速入口

这份文档解决四个最实际的问题：

```text
1. Git 到底怎么用。
2. 如何把当前项目或后续新项目推送到 GitHub。
3. 当前 docs 应该按什么顺序看。
4. 你的复现结果和论文结果哪里一致、哪里不一致。
```

---

## 1. Git 是干什么的

Git 可以理解成代码和文档的“版本记录器”。

它解决的问题是：

```text
我改了哪些文件？
这些改动能不能保存成一个版本？
以后能不能回看当时改了什么？
能不能只提交 docs，不提交乱七八糟的临时文件？
```

你现在最常用的 Git 命令只需要这几个：

```bash
git status --short
git diff
git add 文件或文件夹
git commit -m "一句话说明这次改了什么"
git log --oneline -5
```

---

## 2. 先看当前仓库状态

当前项目已经上传到你的 GitHub 私有仓库：

```text
https://github.com/HadleyYu/CA-SupCon-reproduction
```

当前远程仓库分工是：

```text
origin:
你的 GitHub 仓库，用来 push 自己的复现项目。

upstream:
论文作者官方仓库，只用来参考和拉取官方更新。
当前 upstream 的 push 已禁用，避免误推到作者仓库。
```

在项目目录下执行：

```bash
cd /Users/hadley/Desktop/UESTC/CA-SupCon
git status --short
```

输出里常见符号含义：

```text
 M 文件名     这个文件被修改过，Git 以前认识它
?? 文件名     这是新文件或新文件夹，Git 还没开始跟踪
A  文件名     已经 git add，准备进入下一次 commit
```

当前正常状态应该是：

```text
git status --short 没有输出。
```

这表示：

```text
本地文件和 GitHub 上的 main 分支一致。
没有未提交改动。
```

如果看到 `docs/故障诊断综述.md`，不用紧张。它是本地早期扩展阅读文件，已经从 GitHub 当前版本移除，并写入 `.gitignore`，不会再被上传。

---

## 3. 提交 docs 的标准流程

如果你只想提交文档，不想提交代码改动，执行：

```bash
cd /Users/hadley/Desktop/UESTC/CA-SupCon
git status --short
git add docs/
git status --short
git commit -m "Update CA-SupCon reproduction docs"
git push origin main
```

提交后检查：

```bash
git log --oneline -5
```

你应该能看到最新一条 commit。

注意：不要一上来就执行：

```bash
git add .
```

因为它会把当前目录下所有未跟踪文件都加进去，包括你可能暂时不想提交的临时文件。

---

## 4. 如果你想提交代码和脚本

如果你以后改了训练代码、数据脚本或结果脚本，建议和文档分开提交，便于以后回看。

第一类：文档提交。

```bash
git add docs/
git commit -m "Update reproduction docs"
git push origin main
```

第二类：训练代码和脚本提交。

```bash
git add main/ lib/ scripts/ requirements.txt
git commit -m "Update reproduction utilities"
git push origin main
```

提交前一定看：

```bash
git status --short
git diff --stat
```

`git diff --stat` 会告诉你每个文件大概改了多少行。

---

## 4.1 推送到 GitHub 和拉取更新

### 场景一：当前仓库里新增文件或文件夹

如果你后续在当前 `CA-SupCon` 文件夹下新建了其他文件夹，比如 `new_algorithm/`、`notes/`、`paper_review/`，并且想上传到当前 GitHub 仓库，标准流程是：

```bash
cd /Users/hadley/Desktop/UESTC/CA-SupCon
git status --short
git add 新文件夹名/
git status --short
git commit -m "Add new reproduction materials"
git push origin main
```

如果只想提交某几个文件，不要用 `git add .`，可以明确写文件名：

```bash
git add docs/00_git_and_results_quick_start.md scripts/某个脚本.py
git commit -m "Update GitHub workflow notes"
git push origin main
```

如果你确认当前目录下所有改动都要提交，再使用：

```bash
git add .
git commit -m "Update project files"
git push origin main
```

推送前建议检查远程仓库地址：

```bash
git remote -v
git branch -vv
```

当前这个仓库的 `origin` 应该指向你自己的 GitHub 仓库：

```text
https://github.com/HadleyYu/CA-SupCon-reproduction.git
```

### 场景二：拉取 GitHub 上的最新内容

如果你在另一台电脑、GitHub 网页端，或者之后自己在远端改过内容，本地想同步最新版本，执行：

```bash
cd /Users/hadley/Desktop/UESTC/CA-SupCon
git status --short
git pull origin main
```

拉取前先看 `git status --short`，如果本地有未提交改动，建议先提交再拉取：

```bash
git status --short
git add 要保存的文件或文件夹
git commit -m "Save local changes before pulling"
git pull origin main
```

### 场景三：复现其他论文或写其他算法，建立新的 GitHub 仓库

如果你在 `UESTC` 目录下新建另一个项目，例如：

```bash
cd /Users/hadley/Desktop/UESTC
mkdir New-Paper-Reproduction
cd New-Paper-Reproduction
```

第一次把它变成 Git 仓库：

```bash
git init
git status --short
git add README.md main/ docs/ scripts/
git commit -m "Initial reproduction project"
```

然后先去 GitHub 网页上新建一个空仓库，不要勾选自动创建 `README`、`.gitignore` 或 `LICENSE`，避免和本地首次提交冲突。假设新仓库地址是：

```text
https://github.com/HadleyYu/New-Paper-Reproduction.git
```

本地绑定远程仓库并首次推送：

```bash
git remote add origin https://github.com/HadleyYu/New-Paper-Reproduction.git
git branch -M main
git push -u origin main
```

以后这个新仓库的日常提交和推送就是：

```bash
git status --short
git add 要提交的文件或文件夹
git commit -m "Describe this change"
git push
```

以后拉取远端最新内容就是：

```bash
git pull
```

### 场景四：从 GitHub 克隆别人的仓库再复现

如果你要复现别人已经公开的论文代码，通常先克隆：

```bash
cd /Users/hadley/Desktop/UESTC
git clone 对方仓库地址
cd 仓库文件夹名
```

如果你只是阅读和运行，不需要推送到对方仓库。你可以先看远程地址：

```bash
git remote -v
```

如果你想把自己的复现改动上传到自己的 GitHub，建议在 GitHub 上 fork 对方仓库，或者新建自己的复现仓库，然后把 `origin` 改成自己的仓库地址。

常用做法是保留对方仓库为 `upstream`，自己的仓库为 `origin`：

```bash
git remote rename origin upstream
git remote add origin https://github.com/HadleyYu/你的复现仓库.git
git push -u origin main
```

以后同步对方原仓库更新：

```bash
git pull upstream main
```

以后推送你自己的改动：

```bash
git push origin main
```

---

## 5. 不要随便用的命令

这些命令有用，但初期不要随便敲：

```bash
git reset --hard
git clean -fd
git checkout -- 文件名
git restore 文件名
```

原因：

```text
它们可能丢掉你还没提交的改动。
```

如果只是想看历史，不会破坏文件，可以用：

```bash
git log --oneline --decorate -10
git show --stat
```

---

## 6. docs 阅读顺序

建议顺序：

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

各文件作用：

| 文件 | 作用 |
|---|---|
| `00_git_and_results_quick_start.md` | Git、结果图、论文对比的快速入口 |
| `01_beginner_guide.md` | 零基础概念：故障诊断、指标、训练日志 |
| `02_training_workflow_full_guide.md` | 实操流程：准备数据、训练、汇总、画图 |
| `03_training_theory_to_code_deep_dive.md` | 理论到代码：Dataset、Sampler、Loss、模型 |
| `04_reproduction_notes.md` | 复现审计：哪些设置对齐论文，哪些结果算正式 |
| `05_fault_diagnosis_review_market_and_innovation.md` | 综述和创新点：下一步研究怎么找 |
| `06_results_analysis.md` | 结果分析：CWRU/TE、论文对比、弱类别、后续创新切入点 |
| `07_final_reproduction_report.md` | 最终报告：复现过程、实验设置、结果、论文对比和结论 |

如果目录里看到 `故障诊断综述.md`，把它当作早期扩展阅读即可。当前主线以编号后的 `00-07` 文件为准。

该文件当前是本地保留文件：

```text
GitHub 当前版本不包含它。
.gitignore 已忽略它。
它不会影响当前主线文档。
```

---

## 7. 总结果图

这张图用于快速展示当前项目每个数据集、每个不平衡比例的最新完整训练结果。

![CA-SupCon experiment summary](assets/ca_supcon_experiment_summary.png)

读图顺序：

```text
先看每个 ratio 的最终 TestAcc/TestF1/TestMCC。
再看训练和验证曲线是否稳定。
最后看 per-class accuracy，找最弱类别。
```

---

## 8. 和论文结果对比图

这张图是最适合放进阶段汇报或复现说明里的图。

![CA-SupCon reproduction vs paper](assets/ca_supcon_vs_paper.png)

读图方式：

```text
蓝色柱：当前复现的 10-run mean accuracy。
黑色误差线：当前复现的标准差。
橙色柱：论文 CA-SupCon accuracy。
柱子上方数字：当前复现 Acc - 论文 Acc。
正数：当前复现高于论文。
负数：当前复现低于论文。
```

---

## 9. 哪里和论文一致

一致点：

```text
1. 使用 CWRU 和 TE 两个数据集。
2. 使用四个不平衡比例：0.20、0.10、0.05、0.02。
3. 使用 CA-SupCon 主流程：CE loss + SupCon loss + class-aware sampler。
4. 使用 50 epochs 训练。
5. 使用 10 seed mean ± std 作为正式统计口径。
6. 使用 Acc、macro-F1、MCC 评估。
7. CWRU 趋势稳定，四个比例全部达到并超过论文水平。
8. TE random-window 后整体接近论文水平。
```

---

## 10. 哪里和论文不完全一致

不完全一致点：

```text
1. 论文没有公开当年的随机窗口索引，所以无法保证每个样本窗口与论文完全相同。
2. 当前 TE 使用 random-window 数据构造，目的是覆盖更多仿真轨迹，避免旧 sequential 抽样偏低。
3. 当前运行环境是本机 MacBook Pro M5 Pro 64GB，不是论文作者当年的训练环境。
4. TE 的 0.10 和 0.05 当前 Acc 略低于论文。
5. 当前总说明图 ca_supcon_experiment_summary 展示的是最新完整 run，不等同于 mean ± std 表格。
```

这些不一致不代表复现失败。严格说，当前复现更合理的表述是：

```text
在官方方法和论文统计口径基础上，本工程完成了 CWRU/TE 四个不平衡比例的 10 seed 复现。
CWRU 全部超过论文；TE 的 0.20 和 0.02 超过论文，0.10 和 0.05 略低但接近论文。
由于论文未公开固定窗口索引，TE 的精确数值不能保证逐点相同，但趋势和量级已经对齐。
```

---

## 10.1 方法、代码、条件和环境差异

如果你写复现说明，不要只写“结果高于或低于论文”。更严谨的是分层说明。

### 方法层

```text
一致：
CE loss + SupCon loss + class-aware sampler。
lambda = 1。
CWRU temperature = 0.1。
TE temperature = 0.2。
50 epochs。
10 次重复统计 mean ± std。

不改变方法：
当前新增脚本只是让训练、汇总、画图、本机设备选择更方便，没有把 CA-SupCon 换成另一个算法。
```

### 数据层

```text
CWRU：
数据来源、类别数、48 kHz drive-end、3 hp、window=400、step=200、val/test 每类 300，都按论文复现。
主要限制是论文没有公开具体随机窗口索引，所以无法保证每个窗口逐点相同。

TE：
类别数、52 x 200 输入、window=200、step=1、z-score、val/test 每类 1000，与论文任务口径一致。
当前正式版本使用 random-window，因为旧 sequential 抽样覆盖不足，会让部分 TE 类别异常偏低。
```

### 代码层

```text
保留：
cnn1d_cwru.py
cnn1d_te.py
dot_product_classifier.py
SupCon.py
class_aware_sampler.py
CE + SupCon 训练主流程

新增或增强：
prepare_cwru.py
prepare_te.py
run_seed_sweep.py
summarize_repeated_runs.py
plot_training_log.py
plot_experiment_summary.py
--device / --seed / --dataset_desc 等命令行参数
```

### 环境层

```text
论文没有给出完整硬件、Python、PyTorch、驱动版本。
当前本机环境是 MacBook Pro M5 Pro 64GB，Python 3.14.3，PyTorch 2.12.1，macOS arm64。
硬件环境不一致是正常的，所以不能拿单次结果硬比，必须看 10 seed mean ± std。
```

---

## 11. 最终结果表

| Dataset | Ratio | 当前 Acc mean±std | 论文 Acc | 差值 | 判断 |
|---|---:|---:|---:|---:|---|
| CWRU | 0.20 | 93.01±0.36 | 87.45 | +5.56 | 高于论文 |
| CWRU | 0.10 | 91.60±0.52 | 87.36 | +4.24 | 高于论文 |
| CWRU | 0.05 | 90.92±0.32 | 83.90 | +7.02 | 高于论文 |
| CWRU | 0.02 | 87.28±0.73 | 83.12 | +4.16 | 高于论文 |
| TE | 0.20 | 94.84±0.95 | 91.98 | +2.86 | 高于论文 |
| TE | 0.10 | 87.99±0.80 | 89.53 | -1.54 | 略低于论文 |
| TE | 0.05 | 85.68±0.90 | 87.79 | -2.11 | 略低于论文 |
| TE | 0.02 | 85.17±0.74 | 83.27 | +1.90 | 高于论文 |

正式数值来源：

```text
output/cwru_mean_std.csv
output/te_mean_std.csv
output/ca_supcon_vs_paper.csv
```
