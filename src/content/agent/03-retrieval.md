---
kind: chapter
order: 3
title: "检索：RAG 的四个决策点"
short: "检索"
summary: "RAG 不是「向量库 + 大模型」。它有四个独立决策点，每个决策点有各自的失效模式；把它们混在一起谈，你就永远不知道错在哪一层。"
part: "第二部 · 组件"
label: "第 3 章"
prereq: "第 1–2 章"
reading: "约 35 分钟"
date: 2026-10-24
ready: true
tags: [ai-agents, 教材式笔记]
lang: zh
---

<h2><span class="n">1</span>这一章要解决的问题</h2>

<p class="lede">当一个 RAG 系统答错，可能是<b>没找到</b>、<b>找到了但排在后面</b>、<b>找到了但被截断</b>、<b>找到了但模型没照着说</b>、或者<b>答案本来就要两跳</b>。这五种原因对应五个不同的修法，而它们经常被笼统地叫作「检索效果不好」。</p>

<h2><span class="n">2</span>为什么要检索</h2>

<p>模型的知识是参数化的：训练截止之后就没了，而且它对细节的记忆是不可靠的 —— 它会把两个公司的政策混成一句听起来很顺的话。检索把知识改成非参数化的：<b>答案从你给的文档里来，出处可以被检查。</b></p>

<p>课程第三讲把它拆成四个决策点，这四个点是独立的，可以分别优化、分别测：</p>

<table>
  <thead><tr><th style="width:130px;">决策点</th><th style="width:250px;">选项</th><th>主要失效</th></tr></thead>
  <tbody>
    <tr><td><b>索引</b></td><td>固定切块 / 语义切块 / contextual retrieval / RAPTOR 层次摘要 / HNSW 近似近邻</td><td>切断了句子，或把答案切到了两块之间</td></tr>
    <tr><td><b>检索器</b></td><td>BM25 / DPR 双塔 / hybrid / rerank</td><td>词不匹配（同义、缩写）；或语义相似但事实无关</td></tr>
    <tr><td><b>重排</b></td><td>cross-encoder / ColBERT 的 late interaction</td><td>候选里有对的，但没进前 k</td></tr>
    <tr><td><b>循环</b></td><td>一次性检索 / Self-RAG / Search-R1</td><td>问题需要两跳，一次检索永远够不到</td></tr>
  </tbody>
</table>

<h2><span class="n">3</span>索引：切块是最容易被低估的一步</h2>

<p>切块（chunking）决定了「一条可检索单元」的边界。切得太碎，单块缺少判断所需的上下文；切得太大，一块里混了三个主题，检索命中却答不准。</p>

<p>课程提到的 contextual retrieval 值得单独说：它给每个块<b>补上一句由模型生成的上下文说明</b>（「这段出自 2026 年费用政策的住宿条款」），再嵌入。这一句解决的是切块丢失上下文的问题，代价是索引时要为每块调一次模型 —— 一次性成本，查询时免费。</p>

<div class="box finding"><span class="t">作业里为什么先不切块</span>
<p>参考实现对六份短文档直接用整篇索引，理由写在 <code>build_doc_index</code> 的 docstring 里：<b>短文档切块只带来边界问题，不带来收益。</b>手册量级（几千词）开始，切块才有意义。这是一个「按数据规模决定架构」的例子 —— 凡是没写清数据规模的 RAG 方案，都不值得信。</p></div>

<h2><span class="n">4</span>BM25：为什么从它开始</h2>

<p>课程要求从零实现 BM25，而不是先教向量检索。原因很实际：BM25 没有可调的超参魔法，它的每一分都来自可解释的三个量 —— 词有多稀有、在文档里出现几次、文档有多长。</p>

<pre><code>score(q,d) = Σ IDF(t) · f(t,d)(k1+1) / (f(t,d) + k1(1 − b + b·|d|/avgdl))

IDF(t) = ln( (N − n_t + 0.5) / (n_t + 0.5) + 1 )</code></pre>

<p>三个细节决定你的分数能不能和别人对上：</p>

<ol>
  <li><b>IDF 里的 <code>+1</code></b>。这是 Lucene 的写法，不是原论文的。没有它，出现在超过一半文档里的词会得到负权重，反而把相关文档往下压。</li>
  <li><b>查询词去重</b>。同一个词在查询里出现三次，只算一次 —— 否则用户在查询里强调一个词，排序会被他自己的重复放大。</li>
  <li><b>分词器必须一致</b>。课程指定了 tokenizer（小写、按非字母数字切），你自己的实现如果加了词干化，分数就对不上任何手算结果。</li>
</ol>

<h2><span class="n">5</span>五种失败，五种修法</h2>

<table>
  <thead><tr><th style="width:150px;">症状</th><th style="width:220px;">先测什么</th><th>可能的修法</th></tr></thead>
  <tbody>
    <tr><td>完全找不到</td><td>recall@k（k 放大到 50）</td><td>换分词/加同义词/换嵌入模型；先确认文档里真有这句</td></tr>
    <tr><td>找到了但排第 12</td><td>recall@10 与 recall@50 的差</td><td>加 rerank；调整 b（长度惩罚）</td></tr>
    <tr><td>上下文里被截断</td><td>数每次放进窗口的 token</td><td>改成「指针 + 片段」，让模型自己来读</td></tr>
    <tr><td>模型不照着说</td><td>人工看 5 个案例：是没看到还是没采信</td><td>改提示（要求引用 id）；把证据放在最后</td></tr>
    <tr><td>两跳够不到</td><td>把问题按跳数分层统计</td><td>让模型决定下一次查什么（agentic RAG）</td></tr>
  </tbody>
</table>

<p>最后一行是这一章通向 agent 的接口。<code>run_email_qa</code> 就是最小版的 agentic RAG：模型读完检索结果，要么回答，要么给出下一个查询。课程加了一条硬约束 ——<b>最多 3 次检索</b> —— 因为一个由模型决定何时停止的循环，通常不会停。</p>

<h2><span class="n">6</span>评测：先测检索，再测答案</h2>

<p>把「答对了没有」当成唯一指标，你无法定位问题。课程把评测拆成两层：</p>

<ul>
  <li><b>检索层</b>：<code>recall@k</code> —— 相关文档有没有进前 k。<code>run_bm25_search</code> 的验收标准就是 17 个查询平均 recall@10 ≥ 90%，外加性能门槛（建索引 15 秒、平均每查询 20 ms、稀有词 2 ms）。</li>
  <li><b>答案层</b>：答案里是否包含被接受的说法，<b>且</b> support 里至少有一封 gold 邮件。第二个条件比第一个重要 —— 它挡住「蒙对了」。</li>
</ul>

<div class="box note"><span class="t">为什么 support 必须来自本次检索</span>
<p>因为「支持证据」是给用户核对的，不是给模型自我表扬的。如果模型可以引用一封它没检索到的邮件，这个字段就退化成了一个装饰。参考实现的 <code>_support</code> 只在本次 <code>search</code> 返回的集合里选，代码里就一行 <code>searched[e["id"]] = e</code> —— 但这个约束决定了整个字段有没有意义。</p></div>

<h2><span class="n">7</span>落到作业上</h2>

<ul>
  <li><b>A1 · BM25</b>：倒排索引、单次建索引、查询只读命中词的 posting。<code>2 ms/稀有词</code> 这条门槛专门用来否决「查询时遍历全库」的实现。</li>
  <li><b>A1 · email_qa</b>：3 跳预算 + support 必须来自检索结果。</li>
  <li><b>A3 · search_docs / read_doc</b>：把「检索」改成 agent 的接口 —— 返回指针和短证据（≤150 token），让模型自己决定读哪一段（≤1500 token 窗口）。这是从「检索给代码用」到「检索给模型用」的转变。</li>
</ul>

<h2><span class="n">8</span>延伸阅读</h2>

<table>
  <thead><tr><th style="width:70px;">类型</th><th style="width:250px;">材料</th><th>读它的理由</th></tr></thead>
  <tbody>
    <tr><td>必读</td><td>Lewis et al. <i>Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks</i>, NeurIPS 2020</td><td>RAG 的原始设定：检索器与生成器联合训练，而不是「先查再问」</td></tr>
    <tr><td>选读</td><td>Khattab &amp; Zaharia. <i>ColBERT</i>, SIGIR 2020</td><td>late interaction 为什么能在效果和延迟之间取中间点</td></tr>
    <tr><td>工具</td><td>Robertson &amp; Zaragoza. <i>The Probabilistic Relevance Framework: BM25 and Beyond</i>, 2009</td><td>公式推导与 k1、b 的实际含义；调参前先读这个</td></tr>
  </tbody>
</table>
