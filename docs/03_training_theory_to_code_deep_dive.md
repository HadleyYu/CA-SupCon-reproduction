# CA-SupCon 从理论原理到代码实现深度讲解

这份文档是 `02_training_workflow_full_guide.md` 的深挖版。原 guide 更像实验手册，这一份专门回答：

```text
这个方法为什么这么设计？
每一步训练到底在优化什么？
代码里的 Dataset / Sampler / Model / Loss / Log 分别对应论文里的哪一部分？
以后自己做故障诊断研究时，拿到新数据应该怎么落地？
```

默认工程路径：

```bash
/Users/hadley/Desktop/UESTC/CA-SupCon
```

核心论文：

```text
A class-aware supervised contrastive learning framework for imbalanced fault diagnosis
Knowledge-Based Systems, 2022
```

## 本文件的学习目标

这份文档用来把“论文方法”和“当前代码”对起来。看完以后，你应该能做到：

```text
1. 看到训练命令，知道会进入哪些代码文件。
2. 看到 Dataset 返回值，知道 data、target、data_transformed_list 分别是什么。
3. 看到 [batch, 2, 100]，知道这是 SupCon 的两个增强视图。
4. 看到 ClassAwareSampler，知道它为什么会让一个 epoch 的 TrainNum 大于原始训练集大小。
5. 看到 total_loss = ce_loss + lambda * sup_loss，知道 CE 和 SupCon 各自优化什么。
6. 看到 TestAcc/TestF1/TestMCC，知道它们由哪些函数算出来。
7. 想改模型、loss、sampler、augmentation 时，知道应该改哪个文件。
```

推荐边读边打开这些源文件：

```text
main/main.py
lib/dataloader/load_data.py
lib/dataset/cwru_dataset_shuffle.py
lib/dataset/te_dataset_shuffle.py
lib/sampler/class_aware_sampler.py
lib/backbone/cnn1d_cwru.py
lib/backbone/cnn1d_te.py
lib/backbone/dot_product_classifier.py
lib/loss/SupCon.py
lib/core/run_supcon.py
lib/utils.py
```

## 当前版本要带着哪些结果读代码

读这份文档时，不要只把它当成代码注释。要把代码和最终结果联系起来：

```text
CWRU 四个比例全部超过论文：
说明当前 CWRU 的 Dataset、ClassAwareSampler、SupCon loss、best checkpoint 和指标统计链路是闭合的。

TE random-window 后整体接近论文：
说明 TE 的主要瓶颈不是代码跑不通，而是多变量过程数据的窗口覆盖、类别相似性和弱类别泛化。

TE 0.10 / 0.05 略低：
说明后续创新更应该盯住弱类别、类间边界和 feature space，而不是盲目堆更大的模型。
```

因此，后面看 sampler、loss、augmentation、backbone 时，要一直问：

```text
这个模块是在改善整体 Acc，还是在改善少数类？
这个模块会不会只让训练集更好，但验证/测试不稳？
它对 CWRU 和 TE 的作用是否一致？
它能不能解释 TE 弱类别为什么混淆？
```

先看论文对比图，再看代码会更清楚：

![CA-SupCon reproduction vs paper](assets/ca_supcon_vs_paper.png)

---

## 1. 先建立总图：故障诊断实验到底在做什么

故障诊断本质上是一个分类问题：

```text
输入信号 x
-> 模型提取特征 z
-> 分类器输出每个故障类别的概率
-> 预测类别 y_hat
-> 和真实类别 y 比较
```

在这个项目里，输入有两种：

```text
CWRU:
一段轴承振动信号
shape 约为 [batch, 1, 400]

TE:
一段多变量工业过程时间窗
shape 约为 [batch, 52, 200]
```

输出是故障类别：

```text
CWRU: 10 类
TE:   18 类
```

普通深度分类的路线是：

```text
信号窗口
-> 1D CNN / ResNet
-> 特征向量 feature
-> 线性分类器
-> cross entropy
```

CA-SupCon 在这个基础上加了一个东西：

```text
监督对比学习 SupCon
```

所以当前代码的训练路线是：

```text
原始样本 data
增强样本 view1
增强样本 view2

view1 -> 特征 feature1 -> normalize
view2 -> 特征 feature2 -> normalize
data  -> 特征 feature  -> classifier -> CE loss

[feature1, feature2] + label -> SupCon loss

total_loss = CE loss + lambda * SupCon loss
```

对应代码在：

```text
lib/core/run_supcon.py
```

核心片段：

```python
feature1 = FEAT_MODEL(data_transformed1)
feature2 = FEAT_MODEL(data_transformed2)

feature1 = F.normalize(feature1, dim=1)
feature2 = F.normalize(feature2, dim=1)

feature = FEAT_MODEL(data)
logit = CLASSIFIER(feature)

projection_feature = torch.cat(
    [feature1.unsqueeze(1), feature2.unsqueeze(1)],
    dim=1
)

sup_loss = CL_LOSS(projection_feature, target)
ce_loss = CE_LOSS(logit, target)
total_loss = ce_loss + lamda * sup_loss
```

一句话理解：

```text
CE loss 管“分得对不对”。
SupCon loss 管“特征空间长得好不好”。
Class-aware sampler 管“每个 batch 里类别不要被多数类淹没”。
```

---

## 2. 为什么普通分类不够：不平衡故障诊断的核心矛盾

工业故障诊断经常是不平衡的。

现实里正常数据很多，故障数据少；严重故障数据更少；某些故障模式甚至很难采集。

所以训练集可能长这样：

```text
normal: 1800
fault_1: 36
fault_2: 36
fault_3: 36
...
```

如果只用普通 CE loss，模型很容易出现：

```text
总体准确率看起来不错
但是少数类故障识别很差
```

比如某个模型在 10 类任务里把多数类学得很好，但少数类经常混淆。总 Acc 可能还有 80% 以上，但实际工程里这很危险，因为少数故障类往往才是最需要识别的。

所以论文不只看 Acc，还看：

```text
Acc: 总体准确率
F1: 更关注每类 precision / recall 的平衡
MCC: 多分类相关系数，对类别不平衡更敏感
Per-class accuracy: 每个类别分别看
```

当前代码在 `lib/utils.py` 里实现了这些指标：

```python
classification_metrics(...)
each_cls_acc_cal(...)
total_acc_cal(...)
```

训练日志里你看到的：

```text
TestAcc
TestF1
TestMCC
Per class accuracy
```

就是从这些函数算出来的。

---

## 3. 监督对比学习 SupCon：直觉、公式、代码

### 3.1 直觉

普通 CE loss 只要求分类器最后分对。

但它不强制要求特征空间一定很漂亮。例如两个同类样本在特征空间里可能离得很远，只要最后分类头还能分对，CE 就不一定强烈惩罚。

SupCon 的目标是：

```text
同一类样本的特征靠近
不同类样本的特征远离
```

你可以把模型学出来的特征空间想成一个坐标系：

```text
正常类聚在一个区域
内圈故障聚在一个区域
外圈故障聚在一个区域
...
```

这样少数类即使样本少，也更容易形成清晰边界。

### 3.2 为什么要两份增强视图

对比学习需要“同一个语义对象的不同视图”。

在图像里可能是同一张图的裁剪、颜色扰动。在故障信号里就是：

```text
原始振动/过程信号
-> jitter 加噪
-> scaling 幅值缩放
-> make noise 随机置零
-> translation 时间平移
```

当前代码对每个训练样本生成两份增强：

```text
data_transformed1
data_transformed2
```

对应 `Dataset.__getitem__`：

```python
return self.sequence[index], self.label[index], data_transformed_list
```

其中 `data_transformed_list` 里面有两份 view。

配置在：

```text
configs/cwru/supcon/casupcon.yaml
configs/te/supcon/casupcon.yaml
```

CWRU 配置示例：

```yaml
TRANSFORMS:
  USE_TRANSFORMS: True
  TRANSFORM_TYPE: [["Jitter", "Scaling", "MakeNoise", "Translation"]]
  PARAM_DICT:
    - Jitter: {sigma: 0.05, p: 0.5}
      Scaling: {sigma: 0.05, p: 0.5}
      MakeNoise: {sigma: 0.1, p: 0.5}
      Translation: {p: 0.5}
  K: 2
```

这里的 `K: 2` 就是每个样本生成两个增强视图。

增强函数在：

```text
lib/utils.py
```

包括：

```python
Jitter
Scaling
MakeNoise
Translation
Compose
```

### 3.3 SupCon loss 的输入 shape

当前 SupCon loss 要求输入：

```text
features: [batch_size, n_views, feature_dim]
labels:   [batch_size]
```

训练时：

```python
feature1.shape = [batch, 100]
feature2.shape = [batch, 100]
```

然后：

```python
feature1.unsqueeze(1) -> [batch, 1, 100]
feature2.unsqueeze(1) -> [batch, 1, 100]

cat 后:
projection_feature -> [batch, 2, 100]
```

这正好符合 `SupConLoss.forward()` 的要求。

### 3.4 SupCon loss 内部做了什么

代码在：

```text
lib/loss/SupCon.py
```

核心步骤：

1. 根据 label 构造正样本 mask。

```python
labels = labels.contiguous().view(-1, 1)
mask = torch.eq(labels, labels.T).float()
```

如果 batch 里有 60 个样本，`mask` 是：

```text
[60, 60]
```

其中：

```text
mask[i, j] = 1 表示第 i 个样本和第 j 个样本同类
mask[i, j] = 0 表示不同类
```

2. 把两份 view 拼起来。

```python
contrast_feature = torch.cat(torch.unbind(features, dim=1), dim=0)
```

如果：

```text
features = [60, 2, 100]
```

那么：

```text
contrast_feature = [120, 100]
```

3. 计算所有特征之间的相似度。

```python
anchor_dot_contrast = torch.matmul(anchor_feature, contrast_feature.T) / temperature
```

因为训练前已经做了：

```python
F.normalize(feature1, dim=1)
F.normalize(feature2, dim=1)
```

所以点积基本就是余弦相似度。

4. 去掉自己和自己的对比。

```python
logits_mask = torch.scatter(...)
mask = mask * logits_mask
```

对比学习不能把“自己和自己”当成正样本，否则会投机。

5. 对正样本的 log probability 求平均，得到 loss。

```python
mean_log_prob_pos = (mask * log_prob).sum(1) / mask.sum(1)
loss = - (temperature / base_temperature) * mean_log_prob_pos
```

直觉上：

```text
同类越相似，SupCon loss 越低。
异类越不相似，SupCon loss 越低。
```

### 3.5 temperature 是什么

`temperature` 控制相似度分布的尖锐程度。

小 temperature：

```text
更强调难样本
相似度差异被放大
训练可能更敏感
```

大 temperature：

```text
分布更平滑
训练更温和
可能区分力度弱一些
```

当前配置：

```text
CWRU temperature = 0.1
TE temperature   = 0.2
```

代码位置：

```yaml
CRITERIONS:
  CL_LOSS:
    LOSS_CREATE_FUNC: "create_supcon_loss"
    PARAM_DICT:
      temperature: 0.1
      contrast_mode: "all"
      base_temperature: 0.1
```

---

## 4. Class-aware sampler：为什么它是这篇论文的关键之一

### 4.1 普通 shuffle 的问题

假设训练集极度不平衡：

```text
normal: 1800
fault_each: 36
```

如果普通随机抽 batch，batch 里大概率正常类很多，少数类很少，甚至没有。

这会影响两件事：

```text
CE loss: 梯度主要来自多数类
SupCon loss: 少数类正样本对不足
```

对 SupCon 来说尤其严重。

因为 SupCon 需要同类样本形成 positive pairs。如果一个 batch 里某个少数类只有 1 个样本，那它虽然有两份增强视图，但和其他同类样本的正对比不够丰富。

### 4.2 ClassAwareSampler 在做什么

代码在：

```text
lib/sampler/class_aware_sampler.py
```

它先把所有样本按类别分桶：

```python
cls_data_list = [list() for _ in range(num_classes)]
for i, label in enumerate(dataset.label):
    cls_data_list[int(label)].append(i)
```

然后用两个循环器：

```text
class_iter:       循环抽类别
data_iter_list:   每个类别内部循环抽样本
```

这样训练时不是从全体样本里盲抽，而是：

```text
先选类别
再从该类别里选样本
```

配置里：

```yaml
DATALOADER:
  SAMPLER:
    SAMPLER_CLASS: "ClassAwareSampler"
    NUM_SAMPLER_CLS: 6
```

`NUM_SAMPLER_CLS: 6` 的意思是：每次选中一个类别后，连续从这个类别里取若干样本。这样 batch 里类别分布比普通 shuffle 更均衡。

### 4.3 为什么它对不平衡任务有效

它改变的是训练过程中的“被看见频率”。

原始数据分布：

```text
normal 多
fault 少
```

训练 batch 分布经过 class-aware sampler 后：

```text
各类被更均衡地采到
```

这不等于修改测试集，也不等于作弊。测试集仍然正常评估。

它只是让模型训练时更认真地学习少数类。

---

## 5. 数据层代码：从文件到 batch

### 5.1 数据准备脚本

CWRU：

```text
scripts/prepare_cwru.py
```

输出：

```text
output/cwru/Train1800_Val300_Test300/imbalanced/all_equal_ratio_0.2/data/train_set.txt
output/cwru/Train1800_Val300_Test300/imbalanced/all_equal_ratio_0.2/data/val_set.txt
output/cwru/Train1800_Val300_Test300/imbalanced/all_equal_ratio_0.2/data/test_set.txt
```

TE：

```text
scripts/prepare_te.py
```

推荐输出：

```text
output/te/train-2000_val-1000_test-1000_random-window/imbalanced/all_equal_ratio_0.2/data/train_set.npy
output/te/train-2000_val-1000_test-1000_random-window/imbalanced/all_equal_ratio_0.2/data/val_set.npy
output/te/train-2000_val-1000_test-1000_random-window/imbalanced/all_equal_ratio_0.2/data/test_set.npy
```

这里要特别注意：

```text
DATASET_DESC 决定数据集目录名。
IMB_DESC 决定不平衡比例目录名。
```

所以你看到：

```text
all_equal_ratio_0.02
```

不是“总结果被放错地方”，而是这次实验的某一个不平衡比例。

### 5.2 Dataset 类

CWRU Dataset：

```text
lib/dataset/cwru_dataset_shuffle.py
```

读取：

```python
self.data = np.loadtxt(self.data_path)
self.sequence = torch.from_numpy(self.data[:, :-1])
self.label = torch.from_numpy(self.data[:, -1]).long()
```

说明：

```text
txt 每一行 = 信号点 + 最后一列 label
```

然后保证 channel 在第二维：

```python
if len(self.sequence.shape) < 3:
    self.sequence = self.sequence.unsqueeze(2)
if self.sequence.shape.index(min(self.sequence.shape)) != 1:
    self.sequence = self.sequence.permute(0, 2, 1)
```

最后模型看到的 CWRU 大致是：

```text
[N, 1, 400]
```

TE Dataset：

```text
lib/dataset/te_dataset_shuffle.py
```

读取：

```python
self.data = np.load(self.data_path, allow_pickle=True)
self.sequence = torch.from_numpy(self.data.item().get("sequence"))
self.label = torch.from_numpy(self.data.item().get("label")).long()
self.sequence = self.sequence.permute(0, 2, 1)
```

原始 TE 窗口通常是：

```text
[N, 200, 52]
```

permute 后变成：

```text
[N, 52, 200]
```

因为 Conv1d 要求：

```text
[batch, channels, length]
```

### 5.3 DataLoader

代码：

```text
lib/dataloader/load_data.py
```

它负责：

```text
根据 cfg 找数据目录
根据 dataset name 决定读 txt 还是 npy
创建 Dataset
创建 DataLoader
如果是 train 且配置了 ClassAwareSampler，就启用 sampler
```

关键逻辑：

```python
if phase == "train" and sampler_class is not None:
    sampler = eval(sampler_class)(dataset=dataset, num_samples_cls=num_samples_cls)
    return DataLoader(..., shuffle=False, sampler=sampler, ...)
```

注意：

```text
用了 sampler 后，shuffle 必须 False。
因为采样顺序由 sampler 控制。
```

---

## 6. 模型结构：1D ResNet + Dot Product Classifier

### 6.1 为什么用 1D CNN

故障诊断信号是时间序列。

CWRU 是一维振动信号：

```text
amplitude over time
```

TE 是多变量过程信号：

```text
52 variables over time
```

Conv1d 擅长从局部时间窗口里提模式：

```text
冲击
周期性波形
局部突变
变量间动态变化
```

### 6.2 CWRU backbone

代码：

```text
lib/backbone/cnn1d_cwru.py
```

入口：

```python
create_cnn1d_cwru(...)
```

模型：

```python
ResNetCWRU
```

输入：

```text
[batch, 1, 400]
```

核心：

```python
self.conv1 = nn.Conv1d(1, planes[0], kernel_size=kernel_size, padding=kernel_size//2)
self.layer = self._make_layer(block, num_blocks, pool_size)
self.linear = nn.Linear(..., linear_plane)
```

输出：

```text
[batch, 100]
```

其中 `100` 来自配置：

```yaml
linear_plane: 100
```

### 6.3 TE backbone

代码：

```text
lib/backbone/cnn1d_te.py
```

入口：

```python
create_cnn1d_te(...)
```

和 CWRU 最大区别：

```python
self.conv1 = nn.Conv1d(52, planes[0], ...)
```

因为 TE 有 52 个变量通道。

输入：

```text
[batch, 52, 200]
```

输出：

```text
[batch, 100]
```

### 6.4 BasicBlock 残差块

代码：

```text
lib/backbone/cnn1d_cwru.py
```

核心：

```python
out = F.relu(self.bn1(self.conv1(x)))
out = self.bn2(self.conv2(out))
out += self.shortcut(x)
out = F.relu(out)
```

残差连接的作用：

```text
让网络更容易训练
减少深层网络退化
保留原始信息通道
```

### 6.5 分类器

代码：

```text
lib/backbone/dot_product_classifier.py
```

它把：

```text
feature [batch, 100]
```

映射成：

```text
logit [batch, num_classes]
```

然后 CE loss 根据 logit 和真实 label 计算分类损失。

---

## 7. 训练循环：一轮 epoch 内到底发生了什么

入口命令：

```bash
.venv/bin/python main/main.py \
  --dataset cwru \
  --exp_name supcon \
  --cfg_name casupcon \
  --imb_desc all_equal_ratio_0.2 \
  --seed 0 \
  --device mps
```

主入口：

```text
main/main.py
```

训练类：

```text
lib/core/run_supcon.py
Model_SupCon
```

### 7.1 初始化阶段

`Model_SupCon.__init__()` 做这些事：

```text
读取 cfg
确定 device
初始化模型 FEAT_MODEL / CLASSIFIER
初始化 optimizer
初始化 loss
检查 sampler / epoch_steps
读取 lambda
```

对应函数：

```python
self._init_models()
self._init_optimizers()
self._init_criterions()
```

### 7.2 每个 batch 的训练过程

从 DataLoader 取出：

```python
data, target, data_transformed_list
```

含义：

```text
data: 原始信号
target: 标签
data_transformed_list[0]: 增强视图 1
data_transformed_list[1]: 增强视图 2
```

放到设备：

```python
data = data.float().to(self.device)
target = target.long().to(self.device)
data_transformed1 = data_transformed_list[0].float().to(self.device)
data_transformed2 = data_transformed_list[1].float().to(self.device)
```

前向传播：

```python
feature1 = FEAT_MODEL(data_transformed1)
feature2 = FEAT_MODEL(data_transformed2)
feature = FEAT_MODEL(data)
logit = CLASSIFIER(feature)
```

损失：

```python
sup_loss = CL_LOSS(projection_feature, target)
ce_loss = CE_LOSS(logit, target)
total_loss = ce_loss + lamda * sup_loss
```

反向传播：

```python
total_loss.backward()
optimizer.step()
```

### 7.3 一个 epoch 结束后

代码会统计训练集表现：

```text
TrainLoss
TrainSupLoss
TrainCeLoss
TrainAcc
```

然后跑验证集：

```python
total_eval_rsl = self.eval_ce(phase="val", display=False)
```

如果验证集 Acc 更高，就记录当前模型为 best：

```python
if total_eval_rsl["accuracy"] > best_acc:
    best_epoch = epoch
    best_acc = total_eval_rsl["accuracy"]
    best_model_weights = copy.deepcopy(...)
```

注意：

```text
训练 50 epoch 后，最终 test 用的不是最后一轮模型，
而是验证集最佳 epoch 的模型。
```

这就是日志里的：

```text
Best validation accuracy is ... at epoch ...
Best checkpoint is saved at ...
```

### 7.4 为什么用 val 选 best，而不是 test

标准机器学习流程：

```text
train set: 用来训练参数
val set: 用来选模型和调超参
test set: 最后只评估一次
```

如果用 test 来选 best，会把测试集信息泄漏进训练流程，论文复现就不严格。

当前代码是合理的：

```text
每轮看 val
训练完用 best val checkpoint 跑 test
```

---

## 8. 日志、模型、图都存在哪里

输出路径由这些字段拼出来：

```yaml
OUTPUT_DIR
DATASET_NAME
DATASET_DESC
IMBALANCED / balanced
IMB_DESC
TYPE
RUN_DESC
EXP_DESC
```

以 CWRU 0.02 为例：

```text
output/
  cwru/
    Train1800_Val300_Test300/
      imbalanced/
        all_equal_ratio_0.02/
          data/
          logs/
          models/
```

所以：

```text
all_equal_ratio_0.02
```

表示这一次训练用的是故障类样本比例 0.02，也就是 50:1 不平衡设置。

单次训练日志：

```text
output/.../logs/supcon/ca_supcon/cnn1d-cwru/20260618_171620.log
```

单次 best checkpoint：

```text
output/.../models/supcon/ca_supcon/cnn1d-cwru/supcon_train_supcon.pth
```

单次训练图：

```text
output/.../logs/supcon/ca_supcon/cnn1d-cwru/figures/
```

总结果图：

```text
output/ca_supcon_experiment_summary.png
output/ca_supcon_vs_paper.png
```

---

## 9. 单次训练、多 seed、严格复现分别是什么

### 9.1 单次训练

单次训练就是：

```text
某个 dataset
某个 ratio
某个 seed
跑 50 epochs
得到一个 TestAcc / TestF1 / TestMCC
```

命令例子：

```bash
.venv/bin/python main/main.py \
  --dataset cwru \
  --exp_name supcon \
  --cfg_name casupcon \
  --imb_desc all_equal_ratio_0.2 \
  --seed 0 \
  --device mps
```

适合：

```text
调试代码
确认数据没问题
快速看一个结果
```

### 9.2 多 seed sweep

论文通常不是报单次结果，而是多次随机实验的均值和标准差。

因为深度学习训练受这些因素影响：

```text
随机初始化
数据采样顺序
数据增强随机性
class-aware sampler 顺序
```

所以严格复现要跑：

```text
10 seeds
```

当前脚本：

```text
scripts/run_seed_sweep.py
```

默认会跑：

```text
4 个 ratio x 10 个 seed = 40 次训练
```

CWRU 严格命令：

```bash
cd /Users/hadley/Desktop/UESTC/CA-SupCon
.venv/bin/python scripts/run_seed_sweep.py --dataset cwru --device mps
```

TE 严格命令：

```bash
cd /Users/hadley/Desktop/UESTC/CA-SupCon
.venv/bin/python scripts/run_seed_sweep.py \
  --dataset te \
  --dataset_desc train-2000_val-1000_test-1000_random-window \
  --device mps
```

如果只想跑某个比例的 3 个 seed：

```bash
.venv/bin/python scripts/run_seed_sweep.py \
  --dataset te \
  --dataset_desc train-2000_val-1000_test-1000_random-window \
  --ratios all_equal_ratio_0.2 \
  --seeds 0 1 2 \
  --device mps
```

### 9.3 结果汇总

跑完后，用：

```text
scripts/summarize_repeated_runs.py
```

它会解析 logs，抽取每次实验最后的：

```text
TestAcc
TestF1
TestMCC
Per-class accuracy
```

然后按 ratio / seed 汇总 mean 和 std。

CWRU：

```bash
.venv/bin/python scripts/summarize_repeated_runs.py \
  --dataset cwru \
  --output_csv output/cwru_mean_std.csv
```

TE：

```bash
.venv/bin/python scripts/summarize_repeated_runs.py \
  --dataset te \
  --dataset_desc train-2000_val-1000_test-1000_random-window \
  --output_csv output/te_mean_std.csv
```

### 9.4 画总图

脚本：

```text
scripts/plot_experiment_summary.py
```

输出：

```text
output/ca_supcon_experiment_summary.png
output/ca_supcon_experiment_summary.pdf
output/ca_supcon_vs_paper.png
output/ca_supcon_vs_paper.pdf
```

这些才是你要放论文里的总结果图。

---

## 10. CWRU 和 TE 为什么训练结果差异大

### 10.1 CWRU 更容易

CWRU 的输入是轴承振动，故障模式往往在局部波形、频率、冲击模式上比较明显。

当前严格复现里，CWRU 四个不平衡比例全部超过论文 CA-SupCon 表格结果：

```text
Ratio  Acc          Paper Acc  差值
0.20   93.01±0.36   87.45      +5.56
0.10   91.60±0.52   87.36      +4.24
0.05   90.92±0.32   83.90      +7.02
0.02   87.28±0.73   83.12      +4.16
```

这说明当前代码的 CWRU 数据构造、采样、训练、验证集选择 best checkpoint、测试集评估和 mean ± std 汇总已经形成了完整闭环。

### 10.2 TE 更难

TE 是多变量过程数据，难点是：

```text
52 个变量互相耦合
故障随时间演化
不同故障之间可能动态相似
数据切窗方式会极大影响泛化
```

旧 TE sequential 数据构造曾经导致结果明显偏低，主要问题是：

```text
旧 sequential window 容易只取到少量仿真段
导致训练 / 测试覆盖不充分
部分类别泛化很差
```

后来改成：

```text
random-window
```

让训练、验证、测试从更多仿真轨迹中随机取窗口，严格 10 seed 结果变成：

```text
Ratio  Acc          Paper Acc  差值
0.20   94.84±0.95   91.98      +2.86
0.10   87.99±0.80   89.53      -1.54
0.05   85.68±0.90   87.79      -2.11
0.02   85.17±0.74   83.27      +1.90
```

因此 TE 的结论要更细：

```text
0.20 和 0.02 已超过论文。
0.10 和 0.05 略低于论文，但差距已经收敛到 1.5-2.1 个 Acc 点。
旧 TE 严重偏低问题已经解决。
TE 仍然比 CWRU 更适合拿来做后续创新，因为它保留了多变量耦合、部分类别弱识别和工况动态复杂性。
```

TE 推荐数据目录：

```text
output/te/train-2000_val-1000_test-1000_random-window/
```

以后凡是 TE 严格复现，都应该显式带上：

```bash
--dataset_desc train-2000_val-1000_test-1000_random-window
```

---

## 11. 配置文件怎么看

以 CWRU：

```text
configs/cwru/supcon/casupcon.yaml
```

重要字段：

```yaml
DATASET_NAME: "cwru"
DATASET_DESC: "Train1800_Val300_Test300"
IMBALANCED: True
IMB_DESC: "all_equal_ratio_0.2"
```

含义：

```text
DATASET_NAME: 用哪个数据集
DATASET_DESC: 数据划分规模
IMBALANCED: 是否不平衡实验
IMB_DESC: 当前不平衡比例
```

模型字段：

```yaml
NETWORKS:
  FEAT_MODEL:
    MODEL_CREATE_FUNC: "create_cnn1d_cwru"
    PARAMS:
      seq_len: 400
      num_blocks: 2
      planes: [10, 10, 10]
      kernel_size: 10
      pool_size: 2
      linear_plane: 100

  CLASSIFIER:
    MODEL_CREATE_FUNC: "create_dot_product_classifier"
    PARAMS:
      linear_plane: 100
      num_classes: 10
```

含义：

```text
FEAT_MODEL: 特征提取器
CLASSIFIER: 分类头
linear_plane: 特征维度
num_classes: 类别数
```

训练字段：

```yaml
SEED: 0
LAMDA: 1
TRAINING_OPT:
  DEVICE: "cuda:0"
  NUM_EPOCHS: 50
```

命令行参数会覆盖 YAML：

```bash
--seed 3
--device mps
--epochs 50
--imb_desc all_equal_ratio_0.02
```

所以你不用手改 YAML 就能跑不同实验。

---

## 12. 代码调用链：从命令到结果

完整调用链：

```text
你在终端输入命令
-> main/main.py
-> utils.create_parser()
-> 读取 configs/{dataset}/supcon/casupcon.yaml
-> utils.apply_cli_overrides()
-> utils.seed_everything()
-> dataloader.load_data() 构造 train/val/test
-> Model_SupCon(cfg, dataloader_dict, logger)
-> model.train()
-> 每个 epoch 训练
-> 每个 epoch 验证
-> 保存 best checkpoint
-> best checkpoint 跑 test
-> main.py 调 plot_current_run(logger)
-> 生成单次图
```

批量 sweep 调用链：

```text
scripts/run_seed_sweep.py
-> 循环 ratio
-> 循环 seed
-> 每次 subprocess.run(main/main.py ...)
```

结果汇总调用链：

```text
scripts/summarize_repeated_runs.py
-> 扫描 output 下的 log
-> 解析 TestAcc/TestF1/TestMCC
-> 按 ratio/seed 汇总
-> 输出 csv
```

---

## 13. 以后做一个新故障诊断课题，该怎么迁移

假设你以后拿到一个新数据集，比如电机、电池、齿轮箱、泵、化工过程。

标准路线：

### 13.1 第一步：明确任务

先问：

```text
输入是什么？
单变量还是多变量？
采样频率多少？
每个样本窗口多长？
类别有几类？
类别是否不平衡？
训练 / 验证 / 测试怎么划分才不泄漏？
```

尤其注意：

```text
同一条长时间序列切出来的相邻窗口高度相似。
如果 train/test 混着切，很容易数据泄漏。
```

### 13.2 第二步：做数据准备脚本

仿照：

```text
scripts/prepare_cwru.py
scripts/prepare_te.py
```

目标是输出标准格式。

如果是单变量：

```text
train_set.txt / val_set.txt / test_set.txt
每行: signal values + label
```

如果是多变量：

```text
train_set.npy / val_set.npy / test_set.npy
dict:
  sequence: [N, length, channels]
  label: [N]
```

然后 Dataset 里 permute 成：

```text
[N, channels, length]
```

### 13.3 第三步：写 Dataset

可以照着：

```text
lib/dataset/cwru_dataset_shuffle.py
lib/dataset/te_dataset_shuffle.py
```

必须返回：

```python
return sequence, label, data_transformed_list
```

因为训练循环期待这个结构。

### 13.4 第四步：写 backbone 或复用 backbone

如果是时间序列，可以先复用 1D CNN。

只需要改：

```text
输入通道数
seq_len
num_classes
```

例如多变量 30 通道、窗口 512：

```python
nn.Conv1d(30, planes[0], ...)
seq_len = 512
```

### 13.5 第五步：写 config

新建：

```text
configs/your_dataset/supcon/casupcon.yaml
```

确保这些字段对：

```yaml
DATASET_NAME
DATASET_DESC
IMB_DESC
DATASET.DATASET_CLASS
NETWORKS.FEAT_MODEL.MODEL_CREATE_FUNC
NETWORKS.CLASSIFIER.PARAMS.num_classes
TRAINING_OPT.NUM_CLASSES
```

### 13.6 第六步：先 smoke test

不要一上来跑 40 次。

先跑：

```bash
.venv/bin/python main/main.py \
  --dataset your_dataset \
  --exp_name supcon \
  --cfg_name casupcon \
  --imb_desc all_equal_ratio_0.2 \
  --epochs 1 \
  --device mps
```

看：

```text
数据 shape 对不对
loss 是否正常下降
有没有 NaN
能不能生成 log 和图
test 是否能跑通
```

### 13.7 第七步：正式训练

单次：

```bash
.venv/bin/python main/main.py ...
```

多 seed：

```bash
.venv/bin/python scripts/run_seed_sweep.py ...
```

汇总：

```bash
.venv/bin/python scripts/summarize_repeated_runs.py ...
```

画图：

```bash
.venv/bin/python scripts/plot_experiment_summary.py ...
```

---

## 14. 论文复现时哪些东西不能乱改

如果目标是“尽量严格复现论文”，这些不要随便改：

```text
训练 / 验证 / 测试样本数量
不平衡比例
类别定义
epoch 数
seed 次数
评价指标
数据泄漏规则
是否用 best val checkpoint
```

可以为了调试临时改：

```text
epochs = 1
seeds = 0 1 2
只跑一个 ratio
```

但论文表格不能用这些调试结果。

真正严格表格应该是：

```text
2 datasets x 4 ratios x 10 seeds x 50 epochs
```

也就是：

```text
80 次训练
4000 个 epoch
```

---

## 15. 你这台 MacBook Pro M5 Pro 64GB 怎么跑更合理

当前建议：

```text
device: mps
num_workers: 0
一次只跑一个训练进程
插电
保持散热
长任务用 caffeinate
```

命令：

```bash
caffeinate -dimsu .venv/bin/python scripts/run_seed_sweep.py --dataset cwru --device mps
```

为什么一次只跑一个训练进程：

```text
MPS/GPU 资源共享时，多进程不一定更快
反而可能抢显存、抢带宽、导致系统调度变慢
```

对这类 1D CNN 故障诊断任务：

```text
M5 Pro 64GB 足够做研究。
M5 Max 会更快，但不是必须。
```

真正的瓶颈往往不是内存，而是：

```text
严格复现实验次数多
TE 数据窗口大
多 seed 重复训练耗时
```

---

## 16. 看日志时应该怎么判断训练是否正常

正常日志会有：

```text
TrainLoss
TrainSupLoss
TrainCeLoss
TrainAcc
ValLoss
ValAcc
ValF1
ValMCC
Best validation accuracy
TestAcc
TestF1
TestMCC
Per class accuracy
```

你重点看：

### 16.1 TrainLoss 是否离谱

如果 loss 是 NaN：

```text
学习率太大
数据里有异常值
增强过强
MPS 某些算子异常
```

当前一般不会出现。

### 16.2 ValAcc 和 TestAcc 是否接近

如果：

```text
ValAcc 很高
TestAcc 很低
```

可能：

```text
数据划分不一致
测试集更难
数据泄漏或分布偏移
过拟合
```

### 16.3 Per-class accuracy 是否有 0

如果某些类 accuracy 是 0：

```text
这个类别完全没学会
```

优先检查：

```text
训练集中该类样本是否存在
数据预处理是否覆盖该类
label 是否错位
该类 test 是否和 train 分布完全不同
```

之前 TE 旧数据方式就出现过部分类别特别差，后来 random-window 改善明显。

---

## 17. 这套代码和论文方法的一一对应

| 论文概念 | 当前代码位置 | 作用 |
|---|---|---|
| Fault diagnosis dataset | `scripts/prepare_cwru.py`, `scripts/prepare_te.py` | 原始数据切窗并划分 |
| Imbalanced setting | `IMB_DESC` | 控制 0.2 / 0.1 / 0.05 / 0.02 |
| Data augmentation | `lib/utils.py` | 生成 SupCon 两个 view |
| Class-aware sampler | `lib/sampler/class_aware_sampler.py` | 平衡 batch 内类别出现 |
| Feature encoder | `lib/backbone/cnn1d_cwru.py`, `cnn1d_te.py` | 提取 100 维特征 |
| Classifier | `lib/backbone/dot_product_classifier.py` | 输出类别 logit |
| SupCon loss | `lib/loss/SupCon.py` | 拉近同类，推远异类 |
| CE loss | `lib/loss/CrossEntropy.py` | 分类监督 |
| Joint training | `lib/core/run_supcon.py` | `CE + lambda * SupCon` |
| Best checkpoint | `run_supcon.py::save_model` | 保存最佳验证集模型 |
| Metrics | `lib/utils.py` | Acc / F1 / MCC / per-class |
| Repeated runs | `scripts/run_seed_sweep.py` | 多 ratio 多 seed |
| Mean ± std | `scripts/summarize_repeated_runs.py` | 按论文格式汇总 |
| Summary figure | `scripts/plot_experiment_summary.py` | 论文级总图 |

---

## 18. 最容易混淆的几个点

### 18.1 train_supcon 不是只训练 SupCon

虽然模式叫：

```text
train_supcon
```

但实际训练是：

```text
CE + SupCon
```

不是只做对比学习。

### 18.2 SupCon 用增强视图，CE 用原始 data

当前代码里：

```text
SupCon: data_transformed1 / data_transformed2
CE: 原始 data
```

日志里也写了：

```text
no use aug for classifier
```

意思是分类 CE 没有用增强后的样本。

### 18.3 单次结果不能等于论文严格结果

论文表格通常是：

```text
mean ± std
```

单次结果只能说明这一次训练表现好坏。

严格复现需要：

```text
每个 ratio 跑 10 个 seed
```

### 18.4 `all_equal_ratio_0.02` 是实验条件，不是错误目录

它表示：

```text
所有故障类训练样本数量 = normal 类的一定比例
0.02 对应 50:1 imbalance
```

### 18.5 summarize 不是训练

```text
run_seed_sweep.py: 负责训练
summarize_repeated_runs.py: 负责读日志和统计
plot_experiment_summary.py: 负责画总图
```

标准科研流程本来就是：

```text
训练
-> 汇总
-> 作图
```

可以写脚本把它们串起来，但逻辑上最好分开，方便中断后继续、排查和复核。

---

## 19. 你以后可以怎么创新

如果你要在这篇论文基础上找创新点，不要只想“换一个模型”。可以从这些层面想：

### 19.1 数据层创新

```text
更合理的切窗策略
跨工况泛化划分
小样本故障增强
物理约束的数据增强
异常工况的开放集识别
```

### 19.2 采样层创新

```text
动态 class-aware sampler
根据类别难度自适应采样
根据 per-class accuracy 调整采样权重
少数类 hard positive 挖掘
```

### 19.3 损失函数创新

```text
class-balanced CE
focal loss + SupCon
prototype contrastive loss
margin-based SupCon
fault severity-aware contrastive loss
```

### 19.4 模型层创新

```text
1D CNN + attention
Transformer for multivariate process data
TCN
CNN + graph neural network
frequency-time dual branch
```

### 19.5 工程/控制结合创新

```text
把控制系统状态变量引入诊断
结合过程机理约束
用故障诊断结果指导控制策略切换
诊断-预测-控制一体化
强化学习用于故障后的控制恢复
```

你之前担心“这是不是纯机器学习，和控制关系不大”，这个判断有一半是对的：

```text
当前这篇 CA-SupCon 的代码实现主要是机器学习分类。
但 TE 数据、工业过程监控、故障后的决策和容错控制，天然属于控制科学与工程的应用场景。
```

真正把它做得更像控制方向，可以往：

```text
诊断 + 过程机理
诊断 + 容错控制
诊断 + 强化学习决策
诊断 + 在线监测
```

这些方向靠。

---

## 20. 最后用一句话把整个系统串起来

这套 CA-SupCon 代码做的事情是：

```text
先把故障信号切成标准窗口，
再用 class-aware sampler 让少数故障类在训练中被充分看见，
然后用两份数据增强视图做监督对比学习，让同类故障特征聚集、异类故障特征分开，
同时用 CE loss 保证分类器能直接输出故障类别，
最后用验证集选择最佳模型，在测试集上报告 Acc/F1/MCC/per-class accuracy，
再通过多 seed 汇总 mean ± std，形成论文级实验结果。
```

你以后做任何一个新故障诊断课题，都可以按这个骨架走：

```text
数据定义
-> 切窗划分
-> Dataset
-> Sampler
-> Backbone
-> Loss
-> 训练
-> 验证
-> 测试
-> 多 seed
-> mean ± std
-> 总图
-> 和论文/基线对比
```

## 21. 代码掌握验收题

如果你想确认自己不是“看过了但没看懂”，可以用下面这些问题自测。

### 21.1 数据和 shape

你应该能回答：

```text
CWRU 的输入为什么是 [batch, 1, 400]？
TE 的输入为什么是 [batch, 52, 200]？
为什么 TE Dataset 里要 permute(0, 2, 1)？
Dataset.__getitem__ 为什么返回三个东西？
data_transformed_list 为什么至少有两个元素？
```

### 21.2 sampler

你应该能解释：

```text
ClassAwareSampler 为什么会重复采少数类？
为什么用了 sampler 后 DataLoader shuffle=False？
为什么日志里的 TrainNum 可能比原始训练样本数大？
为什么 SupCon 特别需要 batch 里有多个类别和同类样本？
```

### 21.3 loss

你应该能写出：

```text
total_loss = CE loss + lambda * SupCon loss
```

并说明：

```text
CE loss 负责让分类器预测正确类别。
SupCon loss 负责让特征空间同类聚集、异类分离。
lambda 控制 SupCon 在总损失中的权重。
temperature 控制对比学习相似度分布的尖锐程度。
```

### 21.4 训练循环

你应该能按顺序讲出：

```text
取 batch
放到 device
两份增强视图过 FEAT_MODEL
原始 data 过 FEAT_MODEL 和 CLASSIFIER
计算 SupCon loss
计算 CE loss
相加成 total_loss
backward
optimizer.step
每个 epoch 后跑 val
保存 best validation checkpoint
最后用 best checkpoint 跑 test
```

### 21.5 修改代码时的入口

以后想改不同模块，对应入口是：

| 想改什么 | 优先看哪里 |
|---|---|
| 数据读取 | `lib/dataset/` |
| 数据划分 | `scripts/prepare_cwru.py`, `scripts/prepare_te.py` |
| batch 采样策略 | `lib/sampler/class_aware_sampler.py` |
| 数据增强 | `lib/utils.py` |
| CNN backbone | `lib/backbone/` |
| SupCon 公式 | `lib/loss/SupCon.py` |
| 训练流程 | `lib/core/run_supcon.py` |
| 命令行参数 | `lib/utils.py::create_parser` |
| 多 seed 批量训练 | `scripts/run_seed_sweep.py` |
| mean ± std 汇总 | `scripts/summarize_repeated_runs.py` |

如果这些问题你都能答出来，就说明你已经不只是会运行代码，而是开始具备改代码做研究的能力了。
