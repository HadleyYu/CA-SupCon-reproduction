# 工业故障诊断与预测性维护综述：研究脉络、产业现状与可能创新点

生成日期：2026-06-20  
适用背景：控制科学与工程、工业过程监控、智能故障诊断、预测性维护、设备健康管理 PHM

---

## 本文件怎么用来找方向

前四份文档解决“会不会跑、懂不懂代码”的问题。这一份解决“跑完以后研究什么”的问题。

阅读顺序建议：

```text
先看第 1-4 节：建立故障诊断、PHM、产业和技术路线的全局认识
再看第 5 节：理解强化学习适合放在哪里
再看第 6-8 节：知道当前热点、数据集和指标
重点看第 9-10 节：筛选你可以做的创新点
最后看第 13 节：制定短期、中期计划
```

看完以后，你应该能把一个想法讲成研究问题：

```text
不是：“我想换个模型试试。”
而是：“在不平衡故障诊断中，少数类特征边界不稳定。我要通过某种 sampler/loss/prototype/domain adaptation 机制改善少数类可分性，并用 CWRU/TE 的四个不平衡率和 mean ± std 验证。”
```

## 当前 baseline 对创新选题的意义

现在 CA-SupCon baseline 已经不是“还没跑完”的状态，而是一个可以拿来做后续研究对照的正式 baseline：

| Dataset | Ratio | 当前 Acc mean±std | 论文 Acc | 差值 | 选题含义 |
|---|---:|---:|---:|---:|---|
| CWRU | 0.20 | 93.01±0.36 | 87.45 | +5.56 | 已经很强，不适合作为主要突破口 |
| CWRU | 0.10 | 91.60±0.52 | 87.36 | +4.24 | 已经很强，适合做稳定性验证 |
| CWRU | 0.05 | 90.92±0.32 | 83.90 | +7.02 | 已经很强，适合做消融对照 |
| CWRU | 0.02 | 87.28±0.73 | 83.12 | +4.16 | 极端不平衡仍有空间，但已超过论文 |
| TE | 0.20 | 94.84±0.95 | 91.98 | +2.86 | 表现强，说明 random-window 有效 |
| TE | 0.10 | 87.99±0.80 | 89.53 | -1.54 | 值得重点分析弱类别 |
| TE | 0.05 | 85.68±0.90 | 87.79 | -2.11 | 最适合找创新点 |
| TE | 0.02 | 85.17±0.74 | 83.27 | +1.90 | 极端不平衡下已经有效 |

论文对比图：

![CA-SupCon reproduction vs paper](assets/ca_supcon_vs_paper.png)

这张表给出的研究判断是：

```text
不要把主要创新押在“让 CWRU 再涨一点”上。
CWRU 已经偏容易，继续涨分可能更像调参。

更值得做的是 TE：
尤其是 0.10 和 0.05 下的弱类别、类间混淆、窗口覆盖和少数类特征边界。
```

后续如果写论文或开题，可以把 CWRU 当成标准验证集，把 TE 当成主要问题场景：

```text
CWRU:
证明方法在典型轴承振动故障上有效。

TE:
证明方法在多变量工业过程、动态耦合和复杂类别混淆下仍然有效。
```

## 0. 一句话判断

当前工业故障诊断已经从传统的“信号处理 + 专家规则”快速转向“数据驱动 + 深度学习 + 工业 AI 平台”。如果只看算法形式，它确实很像机器学习；但如果看问题来源、应用场景和最终闭环，它仍然属于控制科学与工程、工业过程监控、设备健康管理和智能运维的重要交叉方向。

对于你现在复现的 CA-SupCon 这类论文，更准确的定位是：

> 面向工业控制系统和复杂装备的故障诊断问题，研究小样本、不平衡、跨工况条件下的数据驱动智能诊断方法。

这不是传统控制理论论文，但可以放在控制学科中的“故障检测与诊断 FDD”“过程监控”“工业智能运维”“数据驱动控制系统安全”方向里。

---

## 1. 基本概念：故障诊断、预测性维护、PHM 的关系

### 1.1 故障诊断 FDD

Fault Detection and Diagnosis, FDD，通常包括：

- 故障检测：系统是否异常。
- 故障隔离：异常来自哪个部件、传感器、执行器或过程单元。
- 故障分类：属于哪一种已知故障类型。
- 故障解释：为什么判断为该故障。
- 故障定位：故障发生在系统的哪个结构位置。

你现在复现的 CA-SupCon 主要做的是：

> 已知故障类别下的监督式故障分类。

也就是说，它重点解决“这段信号/这段过程数据属于哪一类故障”。

### 1.2 预测性维护 PdM

Predictive Maintenance, PdM，目标是提前预测设备或系统何时可能出问题，从而安排维护。IBM 将预测性维护描述为利用运行数据和实时状态监测来预测资产何时可能失效；IBM 也强调 AI 工具通常会从 IoT 传感器采集振动、温度、声学等数据，通过模型识别正常状态和异常偏离。[IBM Predictive Maintenance](https://www.ibm.com/think/topics/predictive-maintenance), [IBM AI in Predictive Maintenance](https://www.ibm.com/think/insights/ai-in-predictive-maintenance)

故障诊断和预测性维护的关系可以理解为：

```text
故障检测/诊断 -> 当前是否异常、是什么故障
RUL 预测       -> 还能用多久
维护决策       -> 什么时候修、修哪里、怎么安排资源
```

### 1.3 PHM

Prognostics and Health Management, PHM，范围更大：

- 状态监测
- 故障检测
- 故障诊断
- 健康状态评估
- 剩余寿命预测 RUL
- 维护决策
- 资产管理

所以你的方向如果往工程化、产业化走，最好不要只说“分类准确率”，而应逐步上升到：

> 面向 PHM 的可靠、可解释、可迁移、可部署的智能故障诊断。

---

## 2. 为什么它和控制科学与工程有关

故障诊断本来就是控制系统安全运行的重要组成部分。传统控制里有一条经典路线叫 model-based FDD：

- 基于状态空间模型
- 基于观测器
- 基于残差生成
- 基于参数估计
- 基于卡尔曼滤波
- 基于鲁棒控制和未知输入观测器

但实际工业系统越来越复杂，精确建模很难，于是数据驱动方法逐渐成为主流。2025 年一篇工业故障诊断综述指出，工业故障诊断已经从规则推理和经典信号处理，发展到现代数据驱动方法。[Research Progress on Data-Driven Industrial Fault Diagnosis Methods](https://pmc.ncbi.nlm.nih.gov/articles/PMC12074220/)

因此，控制学科和机器学习在这个方向上的分工大致是：

```text
控制科学：定义工业对象、系统运行机制、安全约束、报警和维护闭环
机器学习：提供异常检测、特征学习、分类、迁移、预测和决策工具
```

如果研究只停留在公开数据集分类准确率，控制味道会比较弱；如果加入工况变化、实时性、误报警成本、维护决策、机理知识、闭环控制影响，控制学科属性就会明显增强。

---

## 3. 产业与市场现状

### 3.1 市场总体趋势

各家市场报告数字不同，但结论一致：预测性维护和工业 AI 处于快速增长阶段。

公开报告中的口径示例：

- MarketsandMarkets 预计预测性维护市场从 2026 年 138.9 亿美元增长到 2031 年 237.9 亿美元，CAGR 11.4%。[MarketsandMarkets PdM Market](https://www.marketsandmarkets.com/Market-Reports/operational-predictive-maintenance-market-8656856.html)
- Grand View Research 估计全球预测性维护市场 2025 年为 142 亿美元，2026 年 175 亿美元，到 2033 年达到 981 亿美元，CAGR 27.9%。[Grand View Research](https://www.grandviewresearch.com/industry-analysis/predictive-maintenance-market)
- The Business Research Company 估计预测性维护市场从 2025 年 118.2 亿美元增长到 2026 年 152.9 亿美元，CAGR 29.4%。[TBRC Predictive Maintenance Market](https://www.thebusinessresearchcompany.com/report/predictive-maintenance-global-market-report)
- MarketsandMarkets 对 AI-driven predictive maintenance 的报告估计，AI 驱动预测性维护市场 2025 年 17.7 亿美元，到 2032 年 192.7 亿美元，CAGR 39.5%。[MarketsandMarkets AI-driven PdM](https://www.marketsandmarkets.com/Market-Reports/ai-driven-predictive-maintenance-market-56600288.html)

这些数字不能逐字当成严谨财务事实，因为不同报告对“预测性维护”“AI 驱动预测性维护”“工业预测维护”的定义不同。但可以得出一个可靠判断：

> 工业故障诊断/预测性维护已经不是单纯学术问题，而是 IIoT、工业 AI、资产管理和智能制造中的高价值赛道。

### 3.2 产业为什么需要它

企业愿意买单的原因不是“模型准确率高”，而是：

- 减少非计划停机。
- 减少过度维护。
- 降低备件库存和维护人力成本。
- 提高设备利用率 OEE。
- 提前发现安全风险。
- 支撑工厂数字化和资产绩效管理 APM。

AWS 对预测性维护的解释里强调 IoT 设备接入、事件监测、触发动作等架构。[AWS What is Predictive Maintenance](https://aws.amazon.com/what-is/predictive-maintenance/)  
Microsoft Azure 的参考架构强调多变量时间序列、流式数据、模型生命周期管理和实时检测。[Azure Multivariate Anomaly Detector Architecture](https://learn.microsoft.com/en-us/azure/ai-services/anomaly-detector/concepts/multivariate-architecture)

这说明产业界更关心完整系统：

```text
传感器 -> 数据采集 -> 边缘/云端存储 -> 异常检测 -> 故障诊断 -> 工单/报警 -> 维护决策
```

而不是只关心一个离线分类模型。

### 3.3 典型企业与产品形态

当前业界产品通常不是单独卖一个“故障诊断算法”，而是以平台或解决方案形式出现。

#### IBM Maximo

IBM Maximo 是资产管理和 APM 平台，强调 AI-powered condition insights、资产可靠性、减少停机和优化运营。[IBM Maximo APM](https://www.ibm.com/products/maximo/asset-performance-management)

#### Siemens Senseye / Insights Hub

Siemens Senseye Predictive Maintenance 面向制造业，帮助企业从反应式维护转向可扩展的基于状态的维护，覆盖汽车、过程工业、离散制造等场景。[Siemens Senseye](https://www.siemens.com/en-us/products/industrial-digitalization-services/senseye-predictive-maintenance/)  
Siemens Insights Hub 强调从设备和过程数据中获得 actionable insights，并支持 AI-driven continuous improvement。[Siemens Insights Hub](https://www.siemens.com/en-us/products/insights-hub/)

#### AWS / Azure

AWS 和 Azure 更像基础设施和解决方案模板提供者：

- 设备接入
- IoT 数据流
- 数据湖
- 云端训练
- 边缘部署
- 异常检测服务
- MLOps

例如 Azure 有预测性维护开源模板，AWS 文档强调使用 IoT 和 ML 预测设备故障并在边缘部署模型。[Azure AI PredictiveMaintenance GitHub](https://github.com/Azure/AI-PredictiveMaintenance), [AWS IoT Predictive Maintenance](https://aws.amazon.com/blogs/iot/using-aws-iot-for-predictive-maintenance/)

### 3.4 产业落地的真实难点

相比学术论文，工业现场更难的地方是：

- 故障样本极少，甚至没有标签。
- 不同设备、不同工况、不同厂线分布差异很大。
- 传感器位置不理想，信号质量差。
- 数据缺失、漂移、噪声、同步问题严重。
- 故障定义不统一，维修记录文本不规范。
- 误报成本和漏报成本不对称。
- 模型需要解释，否则工程师不信。
- 需要和工单系统、MES、SCADA、DCS、EAM 集成。
- 需要持续更新，不能只训练一次。

这也是为什么很多论文在 CWRU、TE、NASA C-MAPSS 上准确率很高，但工业落地仍然难。

---

## 4. 技术路线演化

### 4.1 第一阶段：专家规则和阈值

最早的工业监测多依赖：

- 温度阈值
- 振动 RMS 阈值
- 压力/流量报警限
- 频谱中特定频率峰值
- 专家经验规则

优点：

- 可解释
- 容易部署
- 工程人员容易接受

缺点：

- 对复杂故障不敏感
- 阈值需要人工调
- 对多变量耦合和早期微弱故障能力弱

### 4.2 第二阶段：信号处理 + 传统机器学习

典型流程：

```text
原始信号 -> 手工特征 -> 特征选择 -> 分类器
```

常用特征：

- 时域：均值、方差、RMS、峰峰值、峭度、偏度
- 频域：FFT、包络谱、特征频率
- 时频域：STFT、小波包、EMD、HHT

常用模型：

- PCA / KPCA
- PLS
- SVM
- KNN
- Random Forest
- XGBoost
- GMM
- HMM

优点：

- 数据量要求较低
- 可解释性相对较好
- 在小规模工业场景仍然有价值

缺点：

- 特征依赖专家经验
- 迁移能力弱
- 对复杂非线性和多源数据不够强

### 4.3 第三阶段：深度学习故障诊断

2015 年之后，深度学习成为智能故障诊断主线之一。相关综述指出，深度学习方法可以自动特征学习，缓解传统方法依赖人工特征的问题。[Machine learning and deep learning based methods toward industry 4.0 predictive maintenance in induction motors](https://www.jiem.org/index.php/jiem/article/view/3597)

常见模型：

- 1D-CNN：振动信号、声学信号。
- 2D-CNN：时频图、谱图、GAF、MTF。
- RNN/LSTM/GRU：过程时间序列。
- TCN：长序列、实时预测。
- Transformer：多变量长序列、跨变量依赖。
- Autoencoder/VAE：无监督异常检测。
- GNN：设备拓扑、传感器图、过程变量关系。

优势：

- 自动特征提取。
- 能处理复杂非线性。
- 多源数据融合能力强。

主要问题：

- 标签依赖强。
- 黑箱性强。
- 对跨工况、跨设备泛化不足。
- 训练集和真实生产分布不一致。

### 4.4 第四阶段：小样本、不平衡、迁移和自监督

这是你当前 CA-SupCon 最相关的阶段。

工业现场最常见的情况不是“每类都有大量标注样本”，而是：

```text
正常数据很多
故障数据很少
严重故障几乎没有
新故障没有标签
不同设备分布不同
```

因此近年来热点包括：

- 类不平衡学习
- 小样本学习
- 元学习
- 迁移学习
- 域适应
- 开集识别
- 自监督学习
- 对比学习
- 数据增强
- 生成式样本合成

Nature Scientific Reports 2024 的综述也指出，很多智能故障诊断方法默认数据完整、平衡且充足，但这与真实工程场景不一致。[Deep learning based approaches for intelligent industrial machinery fault diagnosis and prognosis](https://www.nature.com/articles/s41598-024-79151-2)

你的 CA-SupCon 本质上就在解决：

> 类不平衡条件下，用监督对比学习增强特征表征，使少数类更容易分开。

### 4.5 第五阶段：知识和数据双驱动

纯数据驱动的问题是：

- 容易学到伪相关。
- 对未见工况不稳。
- 工程解释不足。
- 无法体现机理约束。

因此新趋势是 Knowledge + Data Dual-Driven Diagnosis：

- 把故障机理注入模型。
- 把专家规则转为约束。
- 使用知识图谱组织设备、故障、症状、维修动作。
- 使用物理约束损失函数。
- 使用数字孪生生成或校验数据。

2024/2025 的知识和数据双驱动综述强调，单纯数据驱动和单纯知识驱动都有局限，结合领域知识和深度模型是工业故障诊断的重要方向。[Knowledge and Data Dual-Driven Fault Diagnosis in Industrial Scenarios: A Survey](https://www.researchgate.net/publication/379905870_Knowledge_and_Data_Dual-Driven_Fault_Diagnosis_in_Industrial_Scenarios_A_Survey)

### 4.6 第六阶段：大模型、多模态和智能维护助手

2025 以后开始出现 LLM/多模态大模型与故障诊断结合的工作：

- 读取传感器趋势图。
- 结合维修手册、工单文本、报警日志。
- 生成故障解释。
- 给出排查步骤。
- 作为工程师 copilot。
- 与 MCP/工具调用结合，读取数据库、曲线、模型输出。

2025 年已有关于 LLM 在故障诊断和预测性维护中应用的专刊征稿，说明该方向正在成为新热点。[ASCE-ASME Special Collection on LLMs for Fault Diagnosis and Predictive Maintenance](https://asce-asme-journal-of-risk-and-uncertainty.org/posts/post-2025-08-01_si075a/)

也有研究讨论用 LLM 做机械故障预后分析。[Large language models for prognostic analysis in mechanical fault diagnosis](https://pmc.ncbi.nlm.nih.gov/articles/PMC12637991/)

但目前 LLM 在该领域更适合做：

- 解释和报告生成
- 工单知识检索
- 故障树推理
- 维护建议
- 多源信息融合

不太适合直接替代传感器信号分类模型。

---

## 5. 强化学习在故障诊断和维护中的位置

你的判断“强化学习肯定用了”是对的，但要区分两个层面：

```text
故障诊断本身：RL 不是主流第一选择
维护决策/调度：RL 非常自然，越来越常见
```

### 5.1 RL 不太适合作为普通分类器

如果任务只是：

```text
输入一段振动信号 -> 输出故障类别
```

那么 CNN、Transformer、对比学习、域适应通常比 RL 更直接。

因为分类问题有明确标签，不需要智能体和环境交互。

### 5.2 RL 适合维护决策

RL 最适合处理：

- 什么时候维护？
- 是继续运行、降载运行、检查，还是停机维修？
- 备件如何调度？
- 多设备如何安排维修顺序？
- 如何在生产收益、维修成本、停机损失和安全风险之间权衡？

这类问题天然是序贯决策问题：

```text
状态：设备健康状态、传感器数据、RUL、生产负荷、备件状态
动作：不修/检查/小修/大修/停机/调整工况
奖励：收益 - 维修成本 - 停机损失 - 故障惩罚 - 安全风险
```

2026 年一篇关于 RL 在维护决策中的综述明确指出，RL 被用于维护优化和决策支持。[Reinforcement learning in maintenance decision-making and optimization](https://link.springer.com/article/10.1007/s13198-026-03313-w)

2025 年也有研究把设备健康状态预测建模为 MDP，并比较 PPO、A2C、DDPG、SAC 等算法。[Health state prediction with reinforcement learning for predictive maintenance](https://pmc.ncbi.nlm.nih.gov/articles/PMC12833388/)

### 5.3 RL 也可用于诊断系统内部优化

一些更细的用法包括：

- 传感器选择：选择最有信息量的传感器。
- 特征选择：动态选择信号通道或频段。
- 阈值调整：根据运行阶段调整报警阈值。
- 主动诊断：选择下一步测试动作。
- 自适应滤波：自动选择滤波参数。
- 边缘资源调度：决定何时上传、何时本地推理。

2025 年 IIT Madras 的报道中提到，研究人员用 RL 结合多传感器融合和自适应滤波，在传感器位置不理想的情况下进行实时齿轮箱故障检测。[Times of India: IIT Madras RL gearbox fault detection](https://timesofindia.indiatimes.com/city/chennai/iit-madras-develops-ai-framework-for-real-time-gearbox-fault-detection/articleshow/123607199.cms)

### 5.4 RL 方向的风险

RL 很有吸引力，但做论文时要小心：

- 需要定义环境，真实工业环境很难交互试错。
- 奖励函数容易主观。
- 安全探索是难点。
- 离线数据下容易出现分布外动作。
- 很难和纯分类方法公平比较。

所以如果你想做 RL，不建议做“用 RL 做分类”这种硬凑方向。更好的方向是：

> 诊断模型输出健康状态/RUL，RL 根据诊断结果做维护决策。

这就更像控制科学与工程里的闭环决策问题。

---

## 6. 当前研究热点梳理

### 6.1 不平衡故障诊断

痛点：

- 正常类和轻微故障类样本多。
- 严重故障样本少。
- 少数类容易被多数类淹没。

常见方法：

- 重采样
- 类别权重
- Focal Loss
- LDAM
- Logit Adjustment
- Class-aware sampler
- 监督对比学习
- 原型学习
- 生成式增强

可能创新点：

- 类别不平衡 + 工况不平衡同时建模。
- 长尾类别的类间边界自适应 margin。
- 对比学习中正负样本权重随类别频次动态调整。
- 少数类原型不确定性建模。

### 6.2 小样本和新故障识别

痛点：

- 新故障没有足够样本。
- 工厂很难故意制造故障收集数据。

常见方法：

- Few-shot learning
- Prototypical Network
- Matching Network
- MAML
- Self-supervised pretraining
- Prompt learning

可能创新点：

- 基于对比学习的故障原型库。
- 结合维修文本的 few-shot 故障识别。
- 开集故障诊断：已知类分类 + 未知类拒识。
- 少数样本下的置信度校准。

### 6.3 跨工况和跨设备迁移

痛点：

- 实验台数据和真实设备不同。
- 负载、转速、材料、环境变化都会导致分布漂移。

常见方法：

- Domain adaptation
- Domain generalization
- Adversarial learning
- MMD / CORAL
- Contrastive domain alignment
- Test-time adaptation

可能创新点：

- 不平衡条件下的域适应。
- 类别条件对齐，避免不同故障被错误对齐。
- 源域多、目标域无标签时的自监督域泛化。
- 面向连续工况漂移的在线自适应诊断。

### 6.4 多源多模态融合

数据来源：

- 振动
- 声音
- 电流
- 温度
- 压力
- 图像
- 工艺变量
- 报警日志
- 维修工单

常见模型：

- 多分支 CNN
- Attention fusion
- Transformer fusion
- GNN
- Multimodal contrastive learning

可能创新点：

- 传感器缺失情况下的鲁棒融合。
- 异步采样多源数据对齐。
- 文本工单 + 时序信号联合诊断。
- 多模态故障解释生成。

### 6.5 可解释故障诊断

工业现场很重视解释。单纯说“模型预测 class 7”不够，工程师更想知道：

- 哪个传感器异常？
- 哪个频段贡献大？
- 哪个时间段触发判断？
- 与已知故障机理是否一致？

常见方法：

- Grad-CAM
- Saliency map
- SHAP
- LIME
- Attention visualization
- Rule extraction
- Counterfactual explanation

可能创新点：

- 面向故障机理的一致性解释。
- 解释结果与维修文本对齐。
- 可解释性作为训练约束。
- 解释可靠性评估指标。

### 6.6 边缘部署和实时诊断

产业需求：

- 延迟低。
- 不依赖云。
- 数据隐私。
- 带宽受限。
- 设备算力有限。

常见方法：

- 模型剪枝
- 量化
- 蒸馏
- TinyML
- Edge AI
- 流式推理

Arm/Siemens 关于 Edge AI 预测性维护的报道强调实时边缘 AI 对工厂可靠性的价值。[Arm: Siemens Edge AI Predictive Maintenance](https://newsroom.arm.com/blog/siemens-arm-edge-ai-driven-predictive-maintenance)

可能创新点：

- 面向边缘设备的轻量化对比学习诊断模型。
- 云边协同：边缘异常筛查，云端精诊断。
- 低功耗传感器下的自适应采样。
- 不确定性驱动的数据上传策略。

### 6.7 联邦学习和隐私保护

企业之间不愿共享原始数据，但多个工厂联合训练有价值。

可能方向：

- 联邦故障诊断。
- 联邦域适应。
- 个性化联邦学习。
- 隐私保护下的小样本故障识别。
- 跨工厂模型聚合与异常工厂检测。

### 6.8 数字孪生和仿真增强

如果真实故障样本少，可以用仿真系统补充：

- 机理模型生成故障数据。
- 数字孪生模拟极端工况。
- 仿真数据预训练，真实数据微调。

可能创新点：

- 仿真到真实的域适应。
- 数字孪生 + 对比学习。
- 物理一致性约束的数据增强。

### 6.9 大模型和维护知识助手

LLM 更适合做“诊断辅助系统”而不是直接替代时序模型。

可行方向：

- 读取模型诊断结果，生成维护报告。
- 结合报警日志和维修手册做 RAG。
- 构建故障知识图谱。
- 让 LLM 调用信号分析工具。
- 工程师交互式诊断助手。

可能创新点：

- 时序模型 + LLM 的多阶段故障诊断解释框架。
- 诊断模型输出结构化证据，LLM 生成可审核报告。
- 基于维修工单的少样本类别语义增强。

---

## 7. 数据集现状

### 7.1 CWRU

特点：

- 轴承振动故障。
- 经典数据集。
- 类别较少。
- 信号较干净。

优点：

- 入门方便。
- 论文多，便于对比。

缺点：

- 被用烂了。
- 工况相对简单。
- 过高准确率意义有限。

### 7.2 TE

特点：

- Tennessee-Eastman 化工过程。
- 多变量过程数据。
- 更接近控制/过程工业。
- 类别更多。

优点：

- 和控制科学关系更强。
- 适合过程监控、异常检测、多变量诊断。

缺点：

- 数据大。
- 训练慢。
- 模型解释更难。

### 7.3 NASA C-MAPSS

主要用于航空发动机 RUL 预测。

适合：

- 剩余寿命预测。
- 退化建模。
- 维护决策。

### 7.4 PHM Challenge 数据

常用于轴承、刀具、齿轮箱等 PHM 任务。

适合：

- RUL
- 故障检测
- 健康指数构建

### 7.5 公开数据集的共同问题

- 和真实工业场景仍有差距。
- 标签干净但现实标签很脏。
- 多数数据集工况有限。
- 很多论文拆分方式不严谨，存在数据泄漏风险。

如果你想做更有价值的创新，应该尽量避免只在 CWRU 单数据集上刷精度。

---

## 8. 方法评价指标

### 8.1 分类指标

- Accuracy
- Precision
- Recall
- Macro-F1
- MCC
- Confusion Matrix
- Per-class Accuracy

在不平衡诊断里，Accuracy 往往不够，应该重点看：

```text
Macro-F1
MCC
少数类 Recall
每类准确率
混淆矩阵
```

### 8.2 异常检测指标

- AUROC
- AUPRC
- FPR@TPR
- Detection Delay
- False Alarm Rate

### 8.3 RUL 指标

- RMSE
- MAE
- NASA scoring function
- Prognostic horizon

### 8.4 工业指标

真正产业落地还要看：

- 停机减少比例
- 误报警次数
- 漏报次数
- 维修成本降低
- 备件库存降低
- 模型推理延迟
- 人工审核时间
- 工程师接受度

这也是学术创新和产业价值之间的差距。

---

## 9. 你可以考虑的创新点

下面按“难度/适合硕士或阶段性论文”的角度排序。

### 方向 A：不平衡监督对比学习的改进

适合你当前 CA-SupCon 复现基础。

核心问题：

> CA-SupCon 已经用了 class-aware supervised contrastive learning，但还可以进一步处理少数类边界、类内紧致性和类间分离。

可能做法：

- 类别频次自适应温度系数。
- 少数类更大的 margin。
- 类原型引导的 SupCon。
- 难负样本挖掘。
- 类别不确定性加权。
- 对比损失 + logit adjustment。

可实验数据：

- CWRU 四组不平衡率。
- TE 四组不平衡率。

优点：

- 和你当前代码最接近。
- 容易做消融实验。
- 可形成较完整论文。

风险：

- 容易变成小修小补。
- 必须做扎实消融和可视化。

### 方向 B：不平衡 + 跨工况域适应

比单纯不平衡更有价值。

核心问题：

> 实际工业中不仅类别不平衡，而且训练工况和测试工况不同。

可能做法：

- 类别条件域对齐。
- 少数类原型对齐。
- 源域监督对比 + 目标域自监督对比。
- 域不变特征 + 类别可分特征解耦。

优点：

- 工程意义强。
- 比刷 CWRU 单工况更有创新性。

风险：

- 需要构造跨工况实验。
- 实验设计复杂。

### 方向 C：未知故障/开集故障诊断

核心问题：

> 模型不能把所有未知故障都硬分到已知类。

可能做法：

- 已知类分类 + 未知类拒识。
- 基于原型距离的 open-set recognition。
- Energy score / confidence calibration。
- 对比学习增强类边界。

优点：

- 非常贴近工业现场。
- 可解释性较好。

风险：

- 评价指标和实验设计要认真。

### 方向 D：TE 过程监控中的多变量图结构诊断

核心问题：

> TE 是 52 个过程变量，不是普通一维振动信号；变量之间存在过程耦合关系。

可能做法：

- 用 GNN 建模变量关系。
- 根据相关性/工艺知识构图。
- Transformer + Graph Attention。
- 故障影响传播路径解释。

优点：

- 控制学科味道更强。
- TE 数据很适合。

风险：

- 代码实现难度高于 CNN。
- 图结构设计要合理。

### 方向 E：诊断 + 强化学习维护决策

核心问题：

> 诊断结果只是中间变量，最终要决定什么时候维护。

可能做法：

```text
诊断模型输出健康状态/故障概率/RUL
RL 智能体根据状态决定维护动作
奖励函数考虑维修成本、停机损失、故障风险
```

可能算法：

- DQN
- PPO
- SAC
- QR-DQN
- Offline RL

优点：

- 和控制、决策、运维闭环关系强。
- 容易讲成“从诊断到决策”。

风险：

- 环境模拟难。
- 如果没有真实维护成本数据，奖励函数可能显得假。

建议：

> 不要一上来就把 RL 用在分类上，而是把 RL 用在维护决策层。

### 方向 F：可解释故障诊断报告生成

核心问题：

> 工程师不只要类别，还要解释和建议。

可能做法：

- CNN/Transformer 给出故障类别和关键传感器。
- SHAP/attention 给出贡献变量。
- LLM 根据结构化结果生成诊断报告。
- 报告引用维修知识库。

优点：

- 新颖，展示效果好。
- 可以和你现在生成结果图的需求结合。

风险：

- LLM 不能胡说，需要可审核证据。
- 论文评价较难。

### 方向 G：边缘轻量化故障诊断

核心问题：

> 工业现场很多诊断要跑在边缘设备上。

可能做法：

- 轻量 CNN。
- 模型剪枝。
- 量化。
- 知识蒸馏。
- 早退机制 early-exit。

优点：

- 工程落地强。
- 指标不只是准确率，还包括延迟、参数量、FLOPs。

风险：

- 需要边缘设备或至少模拟部署指标。

---

## 10. 最推荐你的三条路线

结合你现在已经复现 CA-SupCon，最现实的创新路线是：

### 推荐 1：类不平衡监督对比学习改进

题目雏形：

> 面向长尾工业故障诊断的类别自适应监督对比学习方法

创新点：

- 类别频次自适应温度。
- 少数类原型增强。
- 难负样本加权。
- 不同不平衡率下稳定提升 Macro-F1/MCC。

实验：

- CWRU：0.2, 0.1, 0.05, 0.02
- TE：0.2, 0.1, 0.05, 0.02
- 指标：Acc, Macro-F1, MCC, per-class Acc, t-SNE

优点：

- 最容易在当前代码上继续。

### 推荐 2：TE 多变量过程的图对比诊断

题目雏形：

> 面向多变量工业过程的图结构对比学习故障诊断方法

创新点：

- 变量关系图建模。
- 图神经网络提取过程变量耦合。
- 对比学习增强故障类表征。
- 可解释变量贡献。

实验：

- TE 主数据集。
- 可补充 CWRU 作为机械数据对照。

优点：

- 更贴近控制科学与工程。

### 推荐 3：诊断模型 + 强化学习维护决策

题目雏形：

> 融合智能故障诊断与强化学习的工业设备预测性维护决策方法

框架：

```text
传感器数据 -> 故障诊断/健康状态评估 -> RL 维护决策 -> 成本/风险优化
```

创新点：

- 诊断概率作为 RL 状态。
- 不确定性进入奖励函数。
- 维护成本、停机损失、误报漏报共同优化。

优点：

- 和控制/决策关系最强。

风险：

- 需要设计合理仿真环境。

---

## 11. 论文写作时的定位建议

如果你继续沿着 CA-SupCon 做，建议不要这样写：

> 本文提出一种机器学习分类模型。

更好的写法是：

> 面向工业控制系统中故障样本稀缺、类别分布不均和运行工况复杂等问题，本文研究数据驱动的智能故障诊断方法，以提高工业系统状态监测的可靠性和少数类故障识别能力。

如果做 TE，控制味道可以更强：

> 针对 Tennessee-Eastman 化工过程多变量耦合、故障类型复杂和故障样本不平衡的问题，构建面向过程监控的智能故障诊断模型。

如果加入 RL：

> 在故障诊断结果基础上，进一步构建维护决策模型，实现从故障识别到维护动作优化的闭环。

---

## 12. 当前领域的主要空白

从研究和产业结合角度看，比较有价值的空白包括：

1. 公开数据集高精度很多，真实跨设备泛化仍然不足。
2. 少数类故障识别仍然不稳定，特别是极端不平衡下的召回率。
3. 大多数方法只分类，不解释，不给维护建议。
4. 诊断模型和维护决策脱节。
5. 工况漂移和在线学习研究不足。
6. 多源数据融合还没有统一范式。
7. 工业知识和深度模型结合不够自然。
8. LLM 进入该领域后，如何保证诊断可信、可审核、可追溯仍是问题。

---

## 13. 给你的下一步建议

### 13.1 短期

当前 CA-SupCon 的 CWRU 和 TE 四组不平衡率已经跑完，严格结果已经整理成：

```text
output/cwru_mean_std.csv
output/te_mean_std.csv
output/ca_supcon_vs_paper.csv
```

下一步短期任务不是继续重复跑 baseline，而是基于这些结果做诊断分析：

```text
1. 找出 TE 0.10 和 0.05 为什么略低于论文。
2. 统计每个比例下最弱类别，特别关注 TE 的类别 3、9、15。
3. 做 per-class accuracy 表，而不只看总体 Acc。
4. 画特征空间可视化，例如 t-SNE/UMAP，观察少数类是否被压缩或混淆。
5. 准备一个 baseline 结果段落，作为后续创新方法的对照。
```

当前 baseline 结论可以这样概括：

```text
CWRU 四个不平衡比例全部超过论文。
TE 0.20 和 0.02 超过论文，0.10 和 0.05 略低于论文但已经接近。
TE 仍然保留明显的弱类别现象，因此更适合继续做创新实验。
```

### 13.2 中期

在 CA-SupCon 上改一个明确模块：

- loss
- sampler
- prototype
- augmentation
- domain adaptation

不要同时改太多，否则难以证明贡献。

### 13.3 如果想做 RL

不要直接替换分类模型。建议两阶段：

```text
第一阶段：诊断模型输出故障概率/健康状态
第二阶段：RL 根据状态做维护决策
```

这样更符合强化学习的优势，也更容易和控制科学与工程挂钩。

---

## 14. 参考资料

### 市场与产业

- MarketsandMarkets, Predictive Maintenance Market 2026-2031: <https://www.marketsandmarkets.com/Market-Reports/operational-predictive-maintenance-market-8656856.html>
- MarketsandMarkets, AI-driven Predictive Maintenance Market 2025-2032: <https://www.marketsandmarkets.com/Market-Reports/ai-driven-predictive-maintenance-market-56600288.html>
- Grand View Research, Predictive Maintenance Market Size & Share Report: <https://www.grandviewresearch.com/industry-analysis/predictive-maintenance-market>
- The Business Research Company, Predictive Maintenance Global Market Report: <https://www.thebusinessresearchcompany.com/report/predictive-maintenance-global-market-report>
- IBM, What is predictive maintenance: <https://www.ibm.com/think/topics/predictive-maintenance>
- IBM, AI in predictive maintenance: <https://www.ibm.com/think/insights/ai-in-predictive-maintenance>
- IBM Maximo APM: <https://www.ibm.com/products/maximo/asset-performance-management>
- Siemens Senseye Predictive Maintenance: <https://www.siemens.com/en-us/products/industrial-digitalization-services/senseye-predictive-maintenance/>
- Siemens Insights Hub: <https://www.siemens.com/en-us/products/insights-hub/>
- AWS, What is Predictive Maintenance: <https://aws.amazon.com/what-is/predictive-maintenance/>
- Microsoft Azure, Multivariate Anomaly Detector predictive maintenance architecture: <https://learn.microsoft.com/en-us/azure/ai-services/anomaly-detector/concepts/multivariate-architecture>

### 学术综述与趋势

- Research Progress on Data-Driven Industrial Fault Diagnosis Methods: <https://pmc.ncbi.nlm.nih.gov/articles/PMC12074220/>
- Deep learning based approaches for intelligent industrial machinery fault diagnosis and prognosis: <https://www.nature.com/articles/s41598-024-79151-2>
- Fault Detection and Diagnosis in Industry 4.0: A Review on Machine-Learning Solutions: <https://www.mdpi.com/1424-8220/25/1/60>
- A survey of data-driven fault-diagnosis methods for large-scale industrial production processes: <https://cje.ustb.edu.cn/en/article/doi/10.13374/j.issn2095-9389.2024.05.24.002?viewType=HTML>
- Machine learning and deep learning based methods toward industry 4.0 predictive maintenance in induction motors: <https://www.jiem.org/index.php/jiem/article/view/3597>
- Knowledge and Data Dual-Driven Fault Diagnosis in Industrial Scenarios: <https://www.researchgate.net/publication/379905870_Knowledge_and_Data_Dual-Driven_Fault_Diagnosis_in_Industrial_Scenarios_A_Survey>

### 强化学习、LLM 与新方向

- Health state prediction with reinforcement learning for predictive maintenance: <https://pmc.ncbi.nlm.nih.gov/articles/PMC12833388/>
- Optimized predictive maintenance for streaming data in industrial IoT networks using deep reinforcement learning and ensemble techniques: <https://www.nature.com/articles/s41598-025-10268-8>
- Predictive maintenance optimization via RUL prediction and distributional reinforcement learning: <https://link.springer.com/article/10.1007/s40747-025-02127-w>
- Reinforcement learning in maintenance decision-making and optimization: <https://link.springer.com/article/10.1007/s13198-026-03313-w>
- IIT Madras real-time gearbox fault detection using RL: <https://timesofindia.indiatimes.com/city/chennai/iit-madras-develops-ai-framework-for-real-time-gearbox-fault-detection/articleshow/123607199.cms>
- Large language models for prognostic analysis in mechanical fault diagnosis: <https://pmc.ncbi.nlm.nih.gov/articles/PMC12637991/>
- ASCE-ASME Special Collection on LLMs for Fault Diagnosis and Predictive Maintenance: <https://asce-asme-journal-of-risk-and-uncertainty.org/posts/post-2025-08-01_si075a/>

## 15. 创新点筛选工作表

以后你想到一个创新点，不要马上写代码。先用这张表筛一遍。

### 15.1 研究问题是否清楚

填写：

```text
我要解决的问题：
它出现在 CWRU、TE，还是更一般的工业故障诊断？
它和类别不平衡、小样本、跨工况、未知故障、实时部署、维护决策中的哪一个有关？
现有 CA-SupCon 为什么还不够？
```

如果说不清“现有方法哪里不够”，这个创新点通常还不成熟。

### 15.2 改的是哪一层

选一个主层，不要一次改太多：

| 层次 | 可改内容 | 风险 |
|---|---|---|
| 数据层 | 切窗、增强、采样、归一化 | 容易被质疑数据不公平 |
| sampler 层 | class-aware、hard class、动态采样 | 要证明不是简单重复过采样 |
| loss 层 | SupCon 改进、margin、prototype、focal | 要解释公式动机 |
| 模型层 | CNN、TCN、Transformer、GNN | 容易变成普通换模型 |
| 迁移层 | 跨工况、跨设备、domain adaptation | 实验设计更复杂 |
| 决策层 | 诊断 + RL 维护决策 | 需要环境、成本和状态定义 |
| 工程层 | 轻量化、实时、边缘部署 | 需要速度和资源指标 |

### 15.3 最小可验证实验

先设计最小实验：

```text
Baseline:
改进方法:
数据集:
不平衡比例:
seed 数:
主要指标:
预期改善:
失败时怎么解释:
```

对于当前这个 CA-SupCon 项目，baseline 已经完整跑完，不需要再从 CWRU 小实验开始。当前推荐最小创新路线是：

```text
TE 0.05 或 TE 0.02
-> 重点分析 class 3、9、15
-> 先做 1 个 ratio x 3 seeds 快速验证
-> 如果有效，再扩展 TE 四个 ratio
-> 再用 CWRU 做泛化和对照
-> 最后补到 10 seeds
```

如果以后换一篇新论文或新数据集，才建议从更小的路线起步：

```text
一个数据集
一个 ratio
三个 seeds
确认有效后再扩大
```

### 15.4 论文贡献怎么写

一个合格贡献通常要能写成：

```text
1. 针对什么问题提出了什么方法。
2. 这个方法为什么适合故障诊断。
3. 相比 CA-SupCon 或其他 baseline 改善在哪里。
4. 在哪些数据集、哪些不平衡设置上验证。
5. 是否通过消融证明每个模块有用。
```

不要写成：

```text
我把模型 A 换成模型 B，Acc 高了一点。
```

更好的表述：

```text
针对少数类故障特征分布稀疏、类间边界不稳定的问题，
提出某种 class-aware prototype contrastive learning 方法，
通过类别原型约束增强少数类聚类稳定性，
并在 CWRU 和 TE 多个不平衡率上验证 Acc、Macro-F1、MCC 与 per-class accuracy 的提升。
```

### 15.5 选题优先级建议

对你当前阶段，优先级可以这样排：

```text
第一优先级：在 CA-SupCon 上做 loss / sampler / prototype 小改进
第二优先级：TE 多变量过程的图结构或变量关系建模
第三优先级：跨工况 / 跨设备泛化
第四优先级：诊断模型输出 + RL 维护决策
第五优先级：大模型维护报告助手
```

原因是：

```text
第一类最容易在当前代码上落地，也最容易形成可控消融。
第二类更贴近 TE 和控制过程监控，有研究空间。
第三类学术价值高，但实验设计更难。
第四类很有控制味道，但需要额外定义维护环境和成本函数。
第五类新颖，但要避免变成展示型应用。
```

最终筛选标准：

```text
能不能解释清楚问题？
能不能在当前代码上实现？
能不能公平比较？
能不能做消融？
能不能让少数类或跨工况指标变好？
能不能和控制/工业过程场景联系起来？
```
