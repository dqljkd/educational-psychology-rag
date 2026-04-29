# 评估标准

## 评估目标
确保该 RAG 系统在“能检索到、能答对、能引用、能稳定运行”四个方面达到可上线或可验收标准。

## 一、离线评估维度

### 1. 检索质量
- Recall@K
  正确证据是否出现在前 K 个召回片段中
- Precision@K
  前 K 个片段中有多少是真正相关证据
- MRR
  第一个正确证据出现的位置质量
- NDCG@K
  结果排序质量

### 2. 生成质量
- Answer Correctness
  答案是否正确回答了问题
- Faithfulness
  答案是否严格受上下文约束
- Completeness
  关键点是否覆盖完整
- Citation Accuracy
  引用是否对应真实证据

### 3. 系统质量
- P95 Latency
  95 分位响应时延
- Failure Rate
  错误率
- Empty Retrieval Rate
  无结果返回比例
- Unsupported Claim Rate
  无证据断言比例

## 二、人工评审 Rubric

每题按 1-5 分打分：

### A. 检索相关性
- 5 分：核心证据完全召回，且排序靠前
- 4 分：主要证据召回到，但排序略有偏差
- 3 分：只召回部分证据
- 2 分：证据弱相关
- 1 分：未召回有效证据

### B. 答案正确性
- 5 分：答案准确且完整
- 4 分：答案基本正确，有少量遗漏
- 3 分：答案部分正确
- 2 分：答案明显不完整或存在错误
- 1 分：答案错误

### C. 忠实度
- 5 分：所有结论都能在证据中找到依据
- 4 分：几乎都可追溯，只有轻微扩写
- 3 分：有部分推断但尚可接受
- 2 分：存在明显超出证据的内容
- 1 分：存在严重幻觉

### D. 引用准确率
- 5 分：引用编号与内容完全对应
- 4 分：基本对应，有轻微偏差
- 3 分：部分对应
- 2 分：引用较混乱
- 1 分：引用失效或错误

## 三、建议验收阈值

### PoC 阶段
- Recall@5 >= 0.70
- Faithfulness 人工平均分 >= 4.0
- Citation Accuracy 人工平均分 >= 4.0
- P95 Latency <= 8s

### 试运行阶段
- Recall@5 >= 0.80
- Answer Correctness 人工平均分 >= 4.2
- Unsupported Claim Rate <= 5%
- P95 Latency <= 6s

### 上线前
- Recall@5 >= 0.85
- Faithfulness >= 4.5
- Citation Accuracy >= 4.5
- Failure Rate <= 1%

## 四、评测集构建建议
- 每个问题必须有标准答案
- 每个问题必须标注 gold evidence 文档和片段
- 题型要覆盖：
  - 事实问答
  - 流程问答
  - 比较问答
  - 边界问答
  - 无答案问答

## 五、推荐评测字段

建议使用 `data/eval/golden_set_template.csv`：
- `question`
- `reference_answer`
- `gold_sources`
- `gold_notes`
- `difficulty`
- `category`

## 六、上线前检查清单
- 检索结果是否稳定
- 答案是否附带引用
- 无答案场景是否能诚实拒答
- 文档更新后索引是否可重建
- API Key 和敏感信息是否隔离
- 上传恶意文件是否有拦截策略
