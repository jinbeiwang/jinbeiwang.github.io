---
kind: chapter
order: 9
title: "优化：三个杠杆，别同时拉"
short: "优化"
summary: "prompt、权重、测试时算力是三个独立杠杆。课程的核心不是列出方法，而是给出「什么时候该动哪一个」的判断顺序——因为选错杠杆，投入会全部打水漂。"
part: "第三部 · 变好"
label: "第 9 章"
prereq: "第 5–6 章"
reading: "约 32 分钟"
date: 2026-10-24
ready: true
tags: [ai-agents, 教材式笔记]
lang: zh
---

<h2><span class="n">1</span>这一章要解决的问题</h2>

<p class="lede">同一个失败，可能是提示词没写清、可能是模型能力不够、也可能是它没想够久。三种病因对应三种药，而<b>药的成本差两个数量级</b>。顺序搞错，你会先花掉最贵的那笔钱。</p>

<h2><span class="n">2</span>三个杠杆</h2>

<table>
  <thead><tr><th style="width:130px;">杠杆</th><th style="width:230px;">手段</th><th>成本</th><th style="width:150px;">见效条件</th></tr></thead>
  <tbody>
    <tr><td><b>Prompt</b></td><td>手改、OPRO、TextGrad、MIPROv2、GEPA</td><td>低（钱与时间都是）</td><td>有评测集，任务可描述</td></tr>
    <tr><td><b>测试时算力</b></td><td>多采样、自我一致性、长思维链、best-of-n</td><td>中（每次推理都付）</td><td>错误是「不确定」而非「不会」</td></tr>
    <tr><td><b>权重</b></td><td>LoRA / QLoRA 微调、蒸馏、RLHF / DPO</td><td>高（数据 + 训练 + 维护）</td><td>任务固定、有大量样本、prompt 已到顶</td></tr>
  </tbody>
</table>

<h2><span class="n">3</span>判断顺序</h2>

<ol>
  <li><b>先确认这不是评测问题。</b>指标本身错了，优化只会让你更快地跑向错误方向（第 11 章）。</li>
  <li><b>再试提示词。</b>课程引用的结果很硬：GEPA 这类反射式提示词进化，在若干任务上能超过 RL 微调，且用的样本少一个数量级。</li>
  <li><b>再看算力。</b>如果失败集中在「有时对有时错」，加采样通常立刻见效；如果失败是系统性的（根本不会这类推理），加算力只是让它更自信地错。</li>
  <li><b>最后才动权重。</b>而且要在 prompt 已经稳定之后 —— 否则你无法判断微调带来的收益是否只是掩盖了提示词的问题。</li>
</ol>

<h2><span class="n">4</span>提示词优化：从手调到搜索</h2>

<table>
  <thead><tr><th style="width:130px;">方法</th><th style="width:250px;">怎么工作</th><th>适合</th></tr></thead>
  <tbody>
    <tr><td><b>OPRO</b></td><td>把「提示词」当优化变量，让模型根据历史表现提出新提示词</td><td>单步任务、指标明确</td></tr>
    <tr><td><b>TextGrad</b></td><td>用文本形式的「梯度」反向传播批评，逐段修改提示词</td><td>多段提示词、需要局部修改</td></tr>
    <tr><td><b>MIPROv2</b></td><td>同时优化指令与 few-shot 示例，贝叶斯式搜索</td><td>多阶段 pipeline（DSPy 生态）</td></tr>
    <tr><td><b>GEPA</b></td><td>反射式进化：看失败轨迹、写自然语言反思、生成新版本</td><td>有可读的失败原因（agent 任务尤其适用）</td></tr>
  </tbody>
</table>

<div class="box note"><span class="t">它们共同的隐含前提</span>
<p>都需要一个<b>能自动打分的指标</b>。这就是为什么「优化」和「评测」必须一起做：没有指标，提示词优化退化成 A/B 看感觉，而感觉在 20 个样本上不可靠。</p></div>

<h2><span class="n">5</span>微调：LoRA 与蒸馏的位置</h2>

<p>LoRA / QLoRA 冻结原权重、只训练低秩增量，所以便宜、可换、可并存多套。它在 agent 场景里的典型用途不是「教会模型新知识」，而是<b>固化一个稳定的输出格式或调用习惯</b> —— 比如永远按你的协议写工具调用，从而省掉提示词里的长说明。</p>

<p>蒸馏则是把一个大模型的行为压到小模型上：用大模型生成轨迹，让小模型学。课程把它放在「成本」这条线上：<b>如果 90% 的请求都是简单分类，用大模型跑是浪费；蒸馏一个小的专门做这件事，剩下的 10% 再交给大的。</b>这是模型路由的经济学基础。</p>

<h2><span class="n">6</span>测试时算力：什么时候加真的有用</h2>

<p>课程必读的 Snell et al. 给了一个比「多采样总更好」精确得多的结论：<b>测试时算力的收益取决于问题难度分布</b>。简单题上多采样是浪费（第一次就对了），极难题上多采样也没用（每次都错），收益集中在中段。</p>

<p>工程含义很直接：<b>先按难度分层统计你的失败率</b>，再决定要不要加算力。全部请求统一加 5 倍采样，通常是最差的选择 —— 成本涨 5 倍，通过率涨不到 5 个点。</p>

<div class="box finding"><span class="t">与 agent 的关系</span>
<p>agent 的「测试时算力」不只是采样次数，还包括<b>允许多少轮工具调用</b>。<code>max_turns</code> 从 5 提到 20，本质是同一个杠杆。所以 A2 的预算设计不是限制，是<b>把这个杠杆做成可调的旋钮</b> —— 而旋钮的每一档都要有对应的通过率与成本数字。</p></div>

<h2><span class="n">7</span>一个常见的错误组合</h2>

<p>同时改提示词、换模型、加采样，然后发现效果变好了，于是得出「三个都有效」。这是最浪费的一种实验设计：<b>你无法归因，也无法复用</b>。</p>

<p>正确做法是一次只动一个变量，并且固定评测集与随机种子（能固定的部分）。课程在作业里给了工具支持这一点：<code>CS329Z_EVAL_SLICE=5</code> 先在小切片上迭代，全量只在切片通过后跑一次 —— 因为每次全量都是一笔钱。</p>

<h2><span class="n">8</span>落到作业上</h2>

<p>课程作业不要求你训练任何东西。但 A7 的里程碑四要求一次<b>框架/结构层面的对照实验</b>（手写 vs DSPy 或 LangGraph），方法上与本节一致：同一评测集、只动一个变量、给出成本与质量两侧的数字。写不出数字的结论，不算结论。</p>

<h2><span class="n">9</span>延伸阅读</h2>

<table>
  <thead><tr><th style="width:70px;">类型</th><th style="width:250px;">材料</th><th>读它的理由</th></tr></thead>
  <tbody>
    <tr><td>必读</td><td>Snell et al. <i>Scaling LLM Test-Time Compute Optimally…</i>, ICLR 2025</td><td>「什么时候加算力有效」的定量回答；按难度分层是核心</td></tr>
    <tr><td>必读</td><td>Agrawal et al. <i>GEPA: Reflective Prompt Evolution Can Outperform RL</i>, 2026</td><td>为什么「读失败轨迹 + 写反思」比纯数值优化更省样本</td></tr>
    <tr><td>选读</td><td>Opsahl-Ong et al. <i>MIPRO</i>, 2024</td><td>指令与示例联合优化的具体算法；DSPy 的 optimizer 之一</td></tr>
  </tbody>
</table>
