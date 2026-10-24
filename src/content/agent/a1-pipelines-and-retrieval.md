---
kind: assignment
track: practice
order: 2
title: "A1 流水线与检索底座"
short: "A1 · 流水线与检索"
summary: "四个 pipeline，从「一次调用」走到「模型决定何时停」。BM25 从零实现，多跳问答的预算留在自己手里 —— 这是固定流水线的终点，也是 agent 的起点。"
part: "第一部 · 打底"
label: "A1"
prereq: "A0；第 3 章"
reading: "约 70 分钟"
problems: "P1–P4 · 23 分"
deliverable: "pipelines.py / bm25.py"
date: 2026-10-24
ready: true
tags: [ai-agents, 作业, 检索, 参考实现]
lang: zh
---

<h2><span class="n">1</span>这个作业要解决什么</h2>

<p class="lede">四个 problem 是一条<b>抽象阶梯</b>，不是四道独立的题。它们共用同一份语料、同一个 <code>LMCallable</code>，唯一的变量是「控制流在谁手里」：全在我们手里 → 一半在模型手里 → 全在模型手里（但预算还在我们手里）。</p>

<table>
  <thead><tr><th style="width:56px;">题</th><th style="width:170px;">名字</th><th style="width:150px;">控制流</th><th>它在教什么</th></tr></thead>
  <tbody>
    <tr><td class="num">P1</td><td><code>run_priority</code></td><td>一次调用，一次解析</td><td>输出契约：模型返回散文，代码必须能承受它</td></tr>
    <tr><td class="num">P2</td><td><code>run_daily_digest</code></td><td>多次调用，我们的循环</td><td>并发、去重、过滤，全部由代码决定</td></tr>
    <tr><td class="num">P3</td><td><code>bm25</code></td><td>零次调用</td><td>检索是可以完全不算模型的能力</td></tr>
    <tr><td class="num">P4</td><td><code>run_email_qa</code></td><td>模型决定查什么、何时停</td><td>第一个"agent 形状"的东西，也是流水线的天花板</td></tr>
  </tbody>
</table>

<p>P4 的位置值得多说一句。它已经有 agent 的三个特征：模型选择动作（下一次查什么）、观察结果、判断够了没有。它<b>不是</b> agent 的原因只有一个 —— <b>工具的集合是写死的两个：search 和 answer</b>。它不能读文件、不能跑命令、不能问用户。把「可选动作」从一个闭集变成一套注册表，就是 A2 要做的全部事情。</p>

<div class="box finding"><span class="t">语料是刻意造的，四个性质不能改</span>
<p>参考实现自带的语料（6 份公司文档 + 25 封 2001 年邮件）不是随便凑的。它同时具备四个性质，每个都对应一条测试：<b>① 被取代的旧政策</b>（2025 年餐补 $45 → 2026 年 $60，检索会同时命中两份）；<b>② 只出现一次的 needle</b>（Thistledown / Larchfield / Basin，用来测稀有词查询的延迟）；<b>③ 真实的两跳链</b>（问题里的词和第二封邮件的词不重叠，必须靠第一跳学到新词）；<b>④ 面向 AI 的植入指令</b>（一封邮件正文里写着要 agent 去执行的命令，用于 A5）。</p>
<p><b>如果你自己造语料，这四条至少要保留前三条。</b>只有性质 ③ 能证明"多跳"不是"多查一次同样的词"。</p></div>

<h2><span class="n">2</span>接口签名</h2>

<table>
  <thead><tr><th style="width:300px;">签名</th><th>返回值与约束</th></tr></thead>
  <tbody>
    <tr><td><code>run_priority(email: Email, lm: LMCallable) -> dict</code></td><td><code>{"category": "urgent"|"normal"|"ignore"|"unknown", "reason": str}</code>，<code>reason</code> 永不为空串</td></tr>
    <tr><td><code>run_daily_digest(emails, lm, *, max_words=300) -> str</code></td><td>纯文本摘要；空输入返回固定句而不是空串</td></tr>
    <tr><td><code>bm25.build(docs: list[str]) -> Index</code></td><td><code>Index(postings, lengths, idf)</code>，doc id 就是列表下标</td></tr>
    <tr><td><code>bm25.scores(index, query) -> dict[int, float]</code></td><td>只含与查询共享至少一个词的文档</td></tr>
    <tr><td><code>bm25.search(index, query, k=10) -> list[tuple[int, float]]</code></td><td>按分降序，同分按 doc_id 升序</td></tr>
    <tr><td><code>build_email_index(emails) -> Index</code></td><td>索引 <code>email_text(e)</code>（subject + from + to + body）</td></tr>
    <tr><td><code>make_search(emails, index) -> Callable[[str, int], list[Email]]</code></td><td>返回<b>副本</b>，调用方改不到原语料</td></tr>
    <tr><td><code>run_email_qa(question, search, lm, *, k=4) -> dict</code></td><td><code>{"answer": str|None, "support": list[str], "searches": int}</code>，<code>searches ≤ 3</code></td></tr>
  </tbody>
</table>

<p>三个常量是契约的一部分，改了要同步改测试：<code>CATEGORIES = ("urgent","normal","ignore")</code>、<code>HOP_BUDGET = 3</code>、BM25 的 <code>K1=1.5 / B=0.75</code>。</p>

<h2><span class="n">3</span>模块划分</h2>

<table>
  <thead><tr><th style="width:150px;">文件</th><th style="width:56px;">行数</th><th>责任</th></tr></thead>
  <tbody>
    <tr><td><code>bm25.py</code></td><td class="num">103</td><td>索引结构、打分、排序。不认识邮件，只认识字符串列表</td></tr>
    <tr><td><code>pipelines.py</code></td><td class="num">359</td><td>四个 pipeline + 文档检索 + 两个常量。不认识 Session，不认识工具协议</td></tr>
    <tr><td><code>corpus.py</code></td><td class="num">341</td><td>语料、gold 标签、<code>email_text</code> / <code>doc_lines</code> 两个视图函数</td></tr>
  </tbody>
</table>

<p>划界的原则：<b><code>bm25.py</code> 不知道"邮件"存在</b>。它接受 <code>list[str]</code>，因此 A3 的文档检索可以复用它而不需要改一行。反过来，如果 <code>bm25.build</code> 的参数是 <code>list[Email]</code>，A3 就会出现第二个 BM25 实现 —— 那是这类项目里最常见的腐化方式。</p>

<p><code>corpus.py</code> 里的 <code>email_text()</code> 和 <code>doc_lines()</code> 值得单独提：它们是<b>同一个对象的两副面孔</b>。<code>email_text</code> 把一封邮件压成适合索引的一行；<code>doc_lines</code> 把一份文档切成"一行一段"，因为文档内容一行就是一整段，用行号做窗口才有意义。这两个函数改变输出，检索结果就整体漂移，所以它们必须只有一处定义。</p>

<h2><span class="n">4</span>关键逻辑逐段解读</h2>

<h3>4.1 P1：输出契约与 <code>unknown</code></h3>

<p>提示词要求模型输出两行。但模型可能输出三种东西：格式正确的两行、一段散文、和一段自称"urgent"但没有 <code>CATEGORY:</code> 前缀的话。<b>第三种最危险，因为它看起来是对的。</b></p>

<pre><code>category = "unknown"
m = re.search(r"CATEGORY\s*:\s*([A-Za-z]+)", reply)
if m:
    word = m.group(1).lower()
    if word in CATEGORIES:
        category = word</code></pre>

<p>两个细节：<b>① 默认值是 <code>unknown</code>，不是 <code>normal</code></b>；<b>② 解析出的词必须在白名单里</b>。第一点决定了一件重要的事 —— 格式不合规时，这条样本<b>不计入正确率的分母之外</b>，而是单独计数。<code>bench</code> 里会打印 <code>unknown</code> 的个数，如果这个数字不是 0，说明提示词或模型有问题，<b>而不是"分类器准确率 80%"</b>。第二点挡住 <code>CATEGORY: Urgent!</code> 被 <code>[A-Za-z]+</code> 抓到 <code>Urgent</code> 之后被当成合法值（因为 <code>lower()</code> 之后它确实合法）—— 但更常见的坑是 <code>CATEGORY: P1</code> 这种模型自创的等级被静默丢弃。</p>

<p><code>reason</code> 的兜底也要写：<code>"The model gave no reason."</code>。返回空串会让下游的摘要 prompt 里出现 <code>- [urgent]  | </code> 这种空槽，模型会开始猜。</p>

<h3>4.2 P2：三件事必须由代码保证</h3>

<p>摘要的三个约束里，只有第一个（字数）能靠提示词，另外两个必须靠代码：</p>

<pre><code>if label == "ignore":
    continue                      # 过滤在最终调用之前，不在提示词里
thread = email.get("thread_id") or email["id"]
if thread in seen_threads:
    continue                      # 每个 thread 一条，保留最先出现的那封
seen_threads.add(thread)</code></pre>

<p><b>为什么"忽略"必须提前过滤：</b>如果你把 7 封广告也塞进 prompt 并说"不要提及它们"，模型会花注意力去判断哪些是广告，而且有相当概率漏掉一封。过滤掉之后再调用，是零成本的确定性。<b>这条原则可以推广成一句话：能由代码保证的事情，不要交给提示词。</b></p>

<p><b>为什么每个 thread 只留一条：</b>一封请求邮件加三封回复，四条里说的是一件事。全塞进去会让摘要在同一件事上重复三遍，而且字数预算被同一件事吃掉四倍。保留最先出现的那封（请求本身而非回复）是因为回复通常只说"好的"。</p>

<p>并发用 <code>ThreadPoolExecutor(max_workers=min(8, len(emails)))</code>：上限 8 是因为真实 API 的 QPS 通常在这个量级就够用，再高只会拿到 429。<b>注意这个函数是 A0 里 <code>FnLM</code> 存在的理由</b> —— 用 <code>ScriptedLM</code> 测它必然间歇性失败。</p>

<h3>4.3 P3：BM25 的两个非显然点</h3>

<p>公式本身在 handout 里给了，实现只值 30 行。真正会写错的是两处。</p>

<p><b>第一处：IDF 里的 <code>+1</code>。</b></p>

<pre><code>IDF(t) = ln((N - n_t + 0.5) / (n_t + 0.5) + 1)</code></pre>

<p>原始的 Robertson 公式没有最后那个 <code>+1</code>。当某个词出现在超过一半文档里，<code>N - n_t + 0.5</code> 会小于 <code>n_t + 0.5</code>，log 取到负数，于是<b>这个词会让命中文档的分数下降</b>。Lucene 加了 <code>+1</code>，把下界抬到 0。这不是精度问题，是符号问题：负权重会让"命中了反而排名更后"，而你在调试时只会看到"排序很奇怪"。</p>

<p>手算一遍，这个公式才真正落地。三篇文档 <code>["a b", "a a b", "c"]</code>，查询 <code>a</code>：</p>

<pre><code>N = 3,  avgdl = (2 + 3 + 1) / 3 = 2
n_t = 2   →   IDF = ln((3-2+0.5)/(2+0.5) + 1) = ln(1.6) ≈ 0.4700

d0 "a b"    tf=1, dl=2
  denom = 1 + 1.5 × (1 - 0.75 + 0.75 × 2/2) = 2.500
  score = 0.4700 × 1 × 2.5 / 2.500 = 0.4700

d1 "a a b"  tf=2, dl=3
  denom = 2 + 1.5 × (0.25 + 0.75 × 3/2) = 4.0625
  score = 0.4700 × 2 × 2.5 / 4.0625 = 0.5785</code></pre>

<p>d1 词频是 d0 的两倍，分数只高 23% —— 这就是 TF 饱和：<b><code>k1</code> 控制"再多出现一次能加多少分"</b>。把 <code>k1</code> 调到 0.5，d1 的领先会变大；调到 5，两者会几乎相等。测试断言 <code>math.isclose(got[0], idf * 2.5 / 2.5)</code>，所以实现里任何一个括号位置错了都会被抓住。</p>

<p><b>第二处：查询只碰查询词的 posting。</b></p>

<pre><code>for term in set(tokenize(query)):        # distinct：重复的词只算一次
    row = index.postings.get(term)
    if not row:
        continue
    for doc_id, tf in row.items():       # 只遍历命中的文档
        ...</code></pre>

<p><code>set()</code> 让 <code>"alpha alpha alpha"</code> 与 <code>"alpha"</code> 同分 —— 否则用户可以靠重复关键词刷分。<code>for doc_id in row.items()</code> 是整个倒排索引的意义所在：一个只在 3 篇文档里出现的词，查询成本是 3 次除法，与语料规模无关。实测 20 万篇文档、罕见词命中 3 篇：<b>0.69 ms</b>。这个数字只有在实现不遍历全库时才可能出现 —— 任何写成 <code>for doc in docs: score(doc)</code> 的版本会慢三到四个数量级。</p>

<p>排序的 tie-break 是 <code>(-score, doc_id)</code>。看起来是细节，实际上决定了测试可重复性：两篇同分文档每次返回的顺序必须一样，否则"哪条证据被引用"会随机变化。</p>

<h3>4.4 P4：预算必须留在代码里</h3>

<pre><code>HOP_BUDGET = 3

for _hop in range(HOP_BUDGET):
    hits = search(query, k)
    ...
    if m:                      # ANSWER: ...
        answer = candidate
        break
    if not m:                  # 连 SEARCH: 都没有
        break
    if next_query in queries:  # 原地打转
        break
    query = next_query</code></pre>

<p>三个 break 分别对应三种终止：<b>给出答案</b>、<b>格式崩了</b>、<b>重复同一个查询</b>。第四个隐含终止是 <code>range(HOP_BUDGET)</code> —— <b>模型说"再查一次"而预算已尽时，循环直接结束，答案为空</b>。</p>

<p>这里有个容易漏的判断：<code>if next_query in queries: break</code>。没有它，一个反复问同一个问题的模型会烧光三轮预算然后返回 <code>answer=None</code>，而你会以为是"检索没找到"。有了它，<code>return {"answer": None, ...}</code> 的语义就清楚了：<b>不是找不到，是它没在往前走</b>。这个区分直接对应 A2 里新增的 <code>stuck</code> 停止原因。</p>

<p><b>为什么 budget 不能靠模型自己停：</b>这是全章最贵的一句话。模型没有任何关于"我已经查了几次"的可靠内部状态；提示词里写"最多查三次"，实际遵循率取决于模型和当天的运气。而三次没查到就返回"找不到"，是一个产品决策，不是一个语言决策 —— <b>产品决策必须由代码执行。</b></p>

<h3>4.5 支撑证据：为什么不能直接拿答案去匹配</h3>

<pre><code>def _support(answer, searched, question) -> list[str]:
    q = set(tokenize(question))
    a = set(tokenize(answer)) - q - {"the","a","an","is","was","of"}
    probe = a or set(tokenize(answer))     # 答案是个裸名字时退回全部词
    scored = [(len(probe & set(tokenize(email_text(e)))), eid) ...]
    return [eid for _n, eid in scored[:2]]</code></pre>

<p>一个短答案 <code>"240k"</code> 与写出它的那封邮件共享的词只有 <code>240k</code> 一个，而问题里的 <code>Thistledown</code>、<code>budget</code> 在<b>很多</b>封邮件里都有。如果把问题和答案一起拿去匹配，<b>命中最多的会是那些喊着"budget"的无关邮件</b>。</p>

<p>所以要减掉问题词。减完之后如果什么都不剩（答案是个专有名词，比如 <code>"Priya Raman"</code>），退回用答案自身的全部词 —— 此时 <code>priya</code> 和 <code>raman</code> 都是高区分度的稀有词，匹配是可靠的。</p>

<p>只返回前 2 个 id，而且只在<b>本次检索到的</b>邮件里选（<code>searched</code> 字典），不是全库。这两条限制让 <code>support</code> 的含义明确：<b>"这次回答依据的是这两封"</b>，而<b>不是</b>"全库里最相关的两封"。前者可以被审计，后者不能。</p>

<h2><span class="n">5</span>实现步骤</h2>

<ol>
  <li><b>先写 <code>corpus.py</code> 的两个视图函数</b>，再写数据。<code>email_text(e)</code> 决定索引看到什么，<code>doc_lines(doc)</code> 决定窗口边界。这两处一旦定下来，后面的数字才可比。</li>
  <li><b>bm25.py 按 4.3 的顺序写</b>：<code>build</code> 单次遍历累积 postings，再单独一遍算 idf，然后 <code>scores</code> 只遍历查询词，最后 <code>search</code> 排序。<b>先让手算那个用例通过</b>，再跑 25 封邮件的测试。</li>
  <li><b>P1</b>。提示词把 rubric 原文放进去，输出要求写成两行。<b>先跑一遍看模型实际输出什么</b>，再写正则 —— 不要凭想象写解析器。</li>
  <li><b>P2</b>。先写单线程版本，把过滤和去重测通；再换线程池。<b>换并发的那一步不要同时改逻辑</b>，否则失败时归因不了。</li>
  <li><b>P3 的接线</b>：<code>build_email_index</code> + <code>make_search</code>。注意 <code>make_search</code> 返回 <code>dict(email)</code> 副本。</li>
  <li><b>P4</b>。按 4.4 写循环和三个 break，最后加 <code>_support</code>。</li>
  <li><b>接上 CLI</b>。四个子命令各十行，作用不是"方便"，而是让 memo 里的问题（"跑几个你自己的查询，排序错在哪"）有一条命令可跑。</li>
  <li><b>跑 bench</b>。它会打印每个问题的实际答案，而不只是对错。<b>先看错的那三条为什么错</b>，再决定要不要改代码。</li>
</ol>

<h2><span class="n">6</span>验证标准</h2>

<h3>机制类（必须全绿，离线）</h3>

<table>
  <thead><tr><th style="width:52px;">#</th><th style="width:290px;">判定</th><th>通过标准</th></tr></thead>
  <tbody>
    <tr><td class="num">V1</td><td>BM25 手算一致</td><td><code>ln(1.6)</code> 与 <code>ln(1.6)×5/4.0625</code> 在 <code>rel_tol=1e-12</code> 下相等</td></tr>
    <tr><td class="num">V2</td><td>词频单调</td><td>同长度文档里 tf=2 的分数 &gt; tf=1</td></tr>
    <tr><td class="num">V3</td><td>无共享词返回空</td><td><code>search(index,"epsilon") == []</code></td></tr>
    <tr><td class="num">V4</td><td>重复查询词只算一次</td><td><code>"alpha alpha alpha"</code> 与 <code>"alpha"</code> 分数完全相同</td></tr>
    <tr><td class="num">V5</td><td>同分按 doc_id 升序</td><td>两篇 <code>"same"</code> 返回 <code>[0,1]</code></td></tr>
    <tr><td class="num">V6</td><td>k 大于候选数不报错</td><td>返回 1 条而不是抛异常</td></tr>
    <tr><td class="num">V7</td><td>索引构建 &lt; 1 s（25 封）</td><td>实测 0.38 ms</td></tr>
    <tr><td class="num">V8</td><td>稀有词查询 &lt; 2 ms（5000 篇语料，词只命中 1 篇）</td><td>实测约 0.002 ms；另测 20 万篇命中 3 篇为 0.69 ms</td></tr>
    <tr><td class="num">V9</td><td>无标签回复不被猜成 <code>normal</code></td><td><code>"This one looks fairly important, I think."</code> → <code>unknown</code>，且 <code>reason</code> 非空</td></tr>
    <tr><td class="num">V10</td><td>摘要字数在界内</td><td><code>len(text.split()) ≤ 300</code></td></tr>
    <tr><td class="num">V11</td><td>忽略项不进摘要、紧急项必须点名</td><td>2001-06-06 这一天：<code>"Larchfield" in text</code> 且 <code>"conference pass" not in text</code></td></tr>
    <tr><td class="num">V12</td><td>每个 thread 只交一条</td><td>2001-06-04：最终 prompt 含原邮件 subject，<b>不含</b> <code>"Re: …"</code> 那条回复</td></tr>
    <tr><td class="num">V13</td><td>检索次数有硬上界</td><td>模型连给 8 个 query，<code>searches == 3</code> 且 <code>answer is None</code></td></tr>
    <tr><td class="num">V14</td><td>查不到就说查不到</td><td><code>ANSWER: NONE</code> → <code>answer is None</code>，<code>support == []</code></td></tr>
    <tr><td class="num">V15</td><td>支撑只在本次检索结果里</td><td><code>set(support) ⊆</code> 检索返回过的 email id</td></tr>
    <tr><td class="num">V16</td><td>空输入不调模型</td><td><code>run_daily_digest([])</code> 返回非空串，模型函数若被调用则抛异常</td></tr>
  </tbody>
</table>

<h3>效果类（需要真实模型，单独标记）</h3>

<div class="box note"><span class="t">这一节的数字不要拿我的来判分</span>
<p>参考实现自带的是 <b>25 封邮件</b>的子集，而官方 fixture 的规模是 60 封。用 mock 模型跑 <code>bench</code> 得到的是 <b>priority 20/25、QA 3/6</b> —— 这个分数是 <code>mock.py</code> 的性质（它是个规则匹配器，被<b>故意</b>写得比黄金标签差），<b>不是任何语言模型的能力</b>。你接上真实模型后应该显著高于它；如果你的结果接近 3/6，说明管线接错了，不是模型不行。</p></div>

<pre><code>$ python -m agentlab bench
priority (25 emails, gold labels from the corpus)
  agree 20/25 = 80%   unknown 0

email QA (6 questions, exact substring match on accepted answers)
  ERR [1hop] What is the Thistledown budget?        → Finance came back this morning
  ok  [1hop] How many open findings did the Larchfield audit report?  → 3 open, responses due Friday
  ok  [1hop] Who signed off on the Thistledown budget?  → Priya Raman signed off …
  ERR [2hop] Which team does the person who chairs the weekly Basin review work in?  …
  ERR [2hop] What release shipped for the firmware that Ravi Menon's team owns?  …
  ok  [1hop] When are written responses to the Larchfield findings due?  → … Friday
  correct 3/6

calls 63 (cached 32)  spend $0.0000</code></pre>

<p>看这三条错例，能读出三件不同的事，这正是"看输出而不是看分数"的价值：</p>

<table>
  <thead><tr><th style="width:220px;">错例</th><th style="width:120px;">失败类型</th><th>它说明什么</th></tr></thead>
  <tbody>
    <tr><td>Thistledown budget → "Finance came back this morning"</td><td>答案摘取</td><td>找到了正确邮件，但截的是第一句而不是含 240k 的那句。<b><code>ANSWER:</code> 要求"短答案"，模型给了上下文。</b></td></tr>
    <tr><td>Basin review → 引用了含 "Dana Whitfield chairs" 的邮件</td><td>两跳未完成</td><td>第一跳找到了"谁主持"，但没把 <code>Dana Whitfield</code> 当作下一跳的查询词。<b>这就是 <code>hops=2</code> 的意义。</b></td></tr>
    <tr><td>Ravi Menon 的固件 → 引用了招聘相关邮件</td><td>检索错</td><td>问题里的 <code>team</code>、<code>owns</code> 是高频词，第一跳没命中 <code>em-0014</code>，后续全偏。<b>这类错误改 prompt 没用，要改检索。</b></td></tr>
  </tbody>
</table>

<div class="box takeaway"><span class="t">A1 的完成判据</span>
<p><b>① 16 条机制测试全绿；② 能不看代码说清 <code>HOP_BUDGET</code> 为什么在代码里而不在提示词里；③ 能对着三条错例分别指出它属于"检索错""提取错"还是"没完成第二跳"。</b>第三点是 A6 design memo 的第四问，现在就该能答。</p></div>

<div class="box note"><span class="t">一条本实现没有测试的分支</span>
<p><code>run_email_qa</code> 里有一个 <code>if next_query in queries: break</code>（模型原地打转）。参考实现写了它但<b>没有为它写测试</b>。补这条测试只需要注入一个永久返回同一结果的 <code>always()</code> 搜索函数，让脚本连给两次相同 query，断言 <code>searches == 2</code>。<b>把它补上，然后想一个问题：这条分支和 A2 的 <code>stuck</code> 是不是同一件事的两种实现？</b></p></div>

<h2><span class="n">7</span>常见坑</h2>

<table>
  <thead><tr><th style="width:250px;">现象</th><th style="width:230px;">原因</th><th>改法</th></tr></thead>
  <tbody>
    <tr><td>手算用例差一点点</td><td>用了 <code>k1</code> 而不是 <code>k1+1</code> 做分子，或把 <code>b</code> 与 <code>1-b</code> 写反</td><td>对着 4.3 的算式逐项替换，别凭记忆写</td></tr>
    <tr><td>常见词让排序变差</td><td>IDF 少了 <code>+1</code>，出现负权重</td><td>见 4.3 第一处</td></tr>
    <tr><td>查询随语料规模变慢</td><td>在 <code>scores</code> 里遍历了所有文档</td><td>只遍历 <code>postings[term]</code></td></tr>
    <tr><td><code>unknown</code> 比例很高</td><td>提示词只要了两行，但模型爱先写一段分析</td><td>在提示词里明确"只输出两行，不要前言"；同时保留 <code>unknown</code> 计数，别用它冒充 <code>normal</code></td></tr>
    <tr><td>并发测试随机失败</td><td>用 <code>ScriptedLM</code> 测 <code>_classify_all</code></td><td>换 <code>FnLM</code>，从 prompt 里读 subject</td></tr>
    <tr><td>摘要里出现广告</td><td>在 prompt 里说"不要提"，而不是在代码里 filter</td><td>过滤前置</td></tr>
    <tr><td>答案对但 <code>support</code> 是错的</td><td>拿问题 + 答案一起去匹配</td><td>减掉问题词，见 4.5</td></tr>
    <tr><td><code>make_search</code> 改坏了语料</td><td>返回了原 dict 引用</td><td>返回 <code>dict(e)</code></td></tr>
  </tbody>
</table>

<h2><span class="n">8</span>自评备忘题</h2>

<ol>
  <li><b><code>HOP_BUDGET</code> 从 3 改成 5，哪一类问题的通过率会上升，哪一类会下降？</b>（提示：多跳链最长是 2 跳；多出来的两跳在做什么？）</li>
  <li><b>P4 已经有"模型选动作"，为什么它不是 agent？</b>如果只允许你加一个工具让它变成 agent，你加哪个，为什么那个比另外两个更重要？</li>
  <li><b>BM25 在"meal limit"上查不到结果，但文档里明明写着 <code>Meals</code> 和 <code>reimbursement</code>。</b>这是分词问题、词干问题，还是同义词问题？三种改法各自的代价是什么？</li>
  <li><b>如果两封邮件说同一件事但日期不同、金额不同，你的 <code>run_email_qa</code> 会引用哪一封？</b>它怎么知道哪封更新？如果它不知道，这属于检索问题还是提示词问题？</li>
  <li><b>你的 digest 在 25 封邮件上花了多少次模型调用？</b>如果有 200 封呢？这个增长是线性的、对数的，还是常数的？你愿意为它付多少？</li>
</ol>

<div class="box note"><span class="t">下一作业的接口依赖</span>
<p>A2 会把 A1 的四个 pipeline 直接包成工具（<code>email_qa</code>、<code>daily_digest</code>、<code>search_emails</code>），并把 <code>bm25.search</code> 换成 A3 的"指针 + 短证据"接口。<b>所以 A1 的函数签名不要顺手改</b> —— 改了之后 A2 的工具描述、A6 的检查、memo 的第四问都会跟着失效。</p></div>
