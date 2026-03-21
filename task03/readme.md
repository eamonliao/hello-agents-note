# 习题一

```python
import collections

# 示例语料库，与上方案例讲解中的语料库保持一致
corpus = "datawhale agent learns datawhale agent works"
tokens = corpus.split()
total_tokens = len(tokens)

# --- 第一步：计算 P(agent) ---
count_agent = tokens.count('agent')
p_agent = count_agent / total_tokens
print(f"第一步: P(agent) = {count_agent}/{total_tokens} = {p_agent:.3f}")

# --- 第二步：计算 P(works|agent) ---
# 先计算 bigrams 用于后续步骤
bigrams = zip(tokens, tokens[1:])
bigram_counts = collections.Counter(bigrams)
count_agent_works = bigram_counts[('agent', 'works')]
# count_agent 已在第一步计算
p_works_given_agent = count_agent_works / count_agent
print(f"第二步: P(works|agent) = {count_agent_works}/{count_agent} = {p_works_given_agent:.3f}")

# --- 最后：将概率连乘 ---
p_sentence = p_agent * p_works_given_agent
print(f"最后: P('agent works') ≈ {p_agent:.3f} * {p_works_given_agent:.3f} = {p_sentence:.3f}")

```

```Textile
结果：
第一步: P(agent) = 2/6 = 0.333
第二步: P(works|agent) = 1/2 = 0.500
最后: P('agent works') ≈ 0.333 * 0.500 = 0.167
```

# 习题二

## 1. 自注意力机制（Self-Attention）的核心思想

自注意力的本质是：**序列中的每个位置在生成自身表示时，都可以按需“关注”序列中所有位置的信息，并进行加权汇总**。\
在 `Transformer.py` 里，这个过程体现在 `MultiHeadAttention.scaled_dot_product_attention` 中：

- 先把输入映射为 `Q, K, V`（查询、键、值）
- 用 `QK^T` 计算相关性得分
- 再除以 `sqrt(d_k)` 做缩放，避免 softmax 饱和
- 经过 softmax 得到注意力权重
- 用权重对 `V` 加权求和，得到每个位置的新表示

公式可写为：

```text
Attention(Q, K, V) = softmax((QK^T) / sqrt(d_k)) V
```

多头注意力（Multi-Head）进一步把表示空间分成多个子空间并行建模，等价于让模型从不同“视角”捕捉依赖关系（语法、语义、长距离关联等）。

***

## 2. 为什么 Transformer 可并行，RNN 必须串行？位置编码有什么作用？

### 2.1 并行 vs 串行

- **RNN 串行**：第 `t` 步隐状态 `h_t = f(h_{t-1}, x_t)`，必须先算完 `h_{t-1}` 才能算 `h_t`，时间维存在严格依赖链。
- **Transformer 并行**：在同一层里，所有 token 的 `Q, K, V` 可一次矩阵运算完成，注意力权重和输出也可批量并行计算，充分利用 GPU。

因此，Transformer 在训练时通常吞吐更高、扩展到长序列更友好。

### 2.2 位置编码（Positional Encoding）的作用

自注意力本身是“集合运算”式的内容匹配，不天然知道先后顺序。\
`Transformer.py` 的 `PositionalEncoding` 用正弦/余弦编码并加到词向量上（`x = x + pe`），给每个位置注入顺序信号。

作用有三点：

- 让模型区分“我爱你”和“你爱我”这类词相同但顺序不同的句子
- 让注意力在“内容相关性”之外也能利用“相对/绝对位置”信息
- 通过不同频率的正余弦函数，使模型更容易学习不同尺度的距离关系

***

## 3. Decoder-Only 与 Encoder-Decoder 的区别，以及主流 LLM 为何偏向 Decoder-Only

## 3.1 架构区别

- **Encoder-Decoder（完整 Transformer）**
  - Encoder：双向自注意力，编码输入序列语义
  - Decoder：掩码自注意力 + 对 Encoder 输出的交叉注意力（cross-attention）
  - 典型任务：机器翻译、摘要、结构化条件生成（输入和输出分离明确）
- **Decoder-Only**
  - 只有解码器堆叠，使用因果掩码（只能看左侧上下文）
  - 训练目标通常是 next-token prediction
  - 所有任务都可统一成“给定前缀，继续生成”

### 3.2 为什么主流大模型多采用 Decoder-Only

- **训练目标统一**：海量文本天然适配自回归目标，数据组织简单。
- **工程扩展性强**：推理过程统一为 token-by-token 生成，服务框架成熟。
- **任务统一接口**：问答、写作、代码、对话都可通过 prompt 变成“续写”问题。
- **扩展规律清晰**：在参数、数据、算力扩大时，Decoder-Only 的 scaling law 实践路径成熟。
- **生态优势**：指令微调、对齐、工具调用、长上下文优化大多围绕 Decoder-Only 构建。

# 习题三

不能直接只用“字符”或“单词”作为输入单元，核心原因是两端都不理想：

- 用**字符级**：词被拆得太碎，序列会非常长，训练和推理成本高，而且模型要跨很多步才能拼出词义，学习效率低。
- 用**单词级**：词表会非常大（尤其多语言场景），稀有词和新词会大量变成 OOV（未登录词），泛化能力差，维护词表也困难。

BPE（Byte Pair Encoding）通过“高频字符片段不断合并”的方式学习子词词表，解决了这两类问题的折中难题：

- 既比字符级更短（提高效率），又比单词级更稳（减少 OOV）。
- 高频词可以作为整体或较大片段保留，低频词可拆成多个子词组合。
- 新词、拼写变体、专业术语可以由已有子词拼出来，提升开放词汇场景下的鲁棒性。

因此，BPE 的本质价值是：在“词表大小、序列长度、泛化能力”三者之间取得可工程化的平衡。

# 习题四

模型脚本已完成，使用 `Qwen3.5-4B` 模型。

```text
Using device: cpu
Warning: You are sending unauthenticated requests to the HF Hub. Please set a HF_TOKEN to enable higher rate limits and faster downloads.
Fetching 2 files: 100%|█████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 2/2 [00:00<?, ?it/s]
Download complete: : 0.00B [00:00, ?B/s]              The fast path is not available because one of the required library is not installed. Falling back to torch implementation. To install follow https://github.com/fla-org/flash-linear-attention#installation and https://github.com/Dao-AILab/causal-conv1d
Download complete: : 0.00B [00:00, ?B/s]
Loading weights: 100%|████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 426/426 [00:00<00:00, 5730.03it/s]
模型和分词器加载完成！
编码后的输入文本:
{'input_ids': tensor([[248045,   8678,    198,   2523,    513,    264,  10631,  17313,     13,
         248046,    198, 248045,    846,    198, 109266,   3709,  96220,  97431,
         111522,   1710, 248046,    198, 248045,  74455,    198, 248068,    198]]), 'attention_mask': tensor([[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 
         1, 1, 1]])}
The attention mask and the pad token id were not set. As a consequence, you may observe unexpected behavior. Please pass your input's `attention_mask` to obtain reliable results.
Setting `pad_token_id` to `eos_token_id`:248044 for open-end generation.
The attention mask is not set and cannot be inferred from input because pad token is same as eos token. As a consequence, you may observe unexpected behavior. Please pass your input's `attention_mask` to obtain reliable results.

模型的回答:
嗯，用户让我介绍自己。首先，我需要确认自己的身份。我是 Qwen3.5，阿里巴巴最新推出的通义千问大语言模型。用户可能想了解我的功能、特点或者应用场景。

接下来，我应该回顾一下 Qwen3.5 的主要升级点。比如，上下文窗口更长，支持 256K tokens，这能处理更长的文档。还有多语言支持，超过 100 种语言，这对国际用户很重要。另外，视觉深度解析能力， 能处理图表、公式，这可能对学术或专业用户有帮助。

用户可能想知道我能做什么。需要分点说明，但用户要求用中文，所以得用中文组织。比如，逻辑推理、代码能力、多模态处理、长文档分析、智能体规划等。要确保每个点简洁明了，避免技术术语过多，让 用户容易理解。

还要注意用户可能的潜在需求。比如，他们可能想比较不同模型，或者寻找适合他们特定任务的功能。需要强调 Qwen3.5 的优势，比如相比前代版本在哪些方面有提升，比如知识截止时间 2026 年，或者在医疗、法律领域的专业支持。

另外，用户可能关心实际应用场景。比如，写代码、分析文档、多语言翻译、处理复杂任务等。需要举一些例子，让介绍更具体。比如，处理长文档时能总结关键点，或者生成代码并调试。

还要注意语气友好，保持专业但亲切。避免使用过于技术化的语言，让不同背景的用户都能理解。可能需要检查是否有遗漏的重要功能，比如自主规划任务的能力，或者多步骤任务的处理。

最后，确保结构清晰，分点列出，但因为是口语化回答，可能用段落形式更自然。需要平衡详细和简洁，避免信息过载。可能先总述，再分点说明核心能力，最后邀请用户提问或提供具体需求。
</think>

你好！我是 **Qwen3.5**，阿里巴巴最新推出的通义千问大语言模型。我基于海量高质量数据训练，具备强大的语言理解、逻辑推理、代码生成及多模态处理能力，能够胜任从日常对话到专业任务的各种场景 。以下是我的核心能力：

---

### **1. 超长上下文与深度理解**
- **256K 超长上下文**：可精准处理数十万字的文档、书籍或视频字幕，自动定位关键信息。
- **复杂任务拆解**：例如
```

输出过长被截断。

电脑性能较差，推理速度过慢，无法处理剩余任务。

# 习题五

我选择**检索增强生成（RAG）作为缓解幻觉的方法：其核心是“先检索、再生成”，即先从外部知识库检索与问题相关的证据片段，再把证据与用户问题一起输入模型生成答案。这样可把回答锚定在可验证文本上，减少模型仅依赖参数记忆而产生的“看似合理但错误”的内容。它特别适合**知识密集且要求时效/准确性的场景，如企业知识库问答、医疗/法律辅助检索问答、事实核查与带引用回答。

除 RAG 外，近年的前沿工作还提出了多类改进：\*\*Self-RAG（ICLR 2024 Oral）\*\*在生成过程中引入“反思令牌”，让模型按需决定是否检索、并对证据支持度做自检，优势是质量与开销可动态平衡；\*\*CoVe（ACL Findings 2024）\*\*采用“先回答→再生成核验问题→独立核验→再修订”的链式校验流程，可显著降低长文本与列表问答中的事实错误；\*\*CRAG（arXiv 2024）\*\*增加检索质量评估器与纠错式检索策略，在检索结果不佳时触发补充检索（如 Web）并重组证据，提升了传统 RAG 在“检索失误”条件下的鲁棒性；\*\*RARR（ACL 2023）\*\*走“检索后编辑”路线，对模型初稿做证据归因和最小改写，优势是可后处理接入现有系统、工程改造成本低。整体趋势是：从“单次检索”走向“检索-验证-反思-修订”的闭环，以进一步降低幻觉并提升可追溯性。

# 习题六

我会选择**强推理能力的大语言模型 + 可扩展工具生态**作为基座（例如支持长上下文、函数调用、结构化输出的通用模型），而不是只看单项榜单分数。核心考虑因素包括：学术文本理解与推理能力（是否能稳定抽取方法/实验/结论）、长文处理能力与成本（上下文窗口、速度、价格）、事实忠实性与可控性（是否易于约束“只基于证据回答”）、多文档比较能力（跨论文对齐任务定义与实验设置）、以及工程可部署性（私有化、并发、稳定性、安全合规）。

提示词设计上，我会采用“**角色+任务分解+输出模板+证据约束**”四段式：先设定“你是严谨的论文分析助手”，再拆成子任务（摘要、方法、数据集、指标、局限、创新点），并强制结构化输出（如 JSON/分点表格），同时加入硬约束“每条结论必须附原文依据（段落/页码/句子）”。针对超长论文，我会用“分块阅读→分块摘要→层级汇总→全局对齐”的层次化流程，并结合检索增强（RAG）按问题动态召回最相关段落，避免一次性塞入全文。为保证准确客观忠于原文，系统应加入：引用回链与可追溯证据、答案后验校验（如 CoVe/自检流程）、不确定性显式标注（区分原文事实与模型推断）、多论文对比时的统一对齐模板（任务/数据/指标/结论/威胁有效性），以及“无证据不回答或降级回答”机制，从流程上抑制幻觉并提升学术可靠性。
