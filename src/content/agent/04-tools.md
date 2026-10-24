---
kind: chapter
order: 4
title: "工具：从函数调用到 MCP"
short: "工具"
summary: "模型不会算数、不知道现在几点、不能改文件。工具补的是这三类缺口，而接口标准化的历史（REST → function calling → MCP）讲的是同一件事：把「怎么用」从提示词里搬到协议里。"
part: "第二部 · 组件"
label: "第 4 章"
prereq: "第 2–3 章"
reading: "约 30 分钟"
date: 2026-10-24
ready: true
tags: [ai-agents, 教材式笔记]
lang: zh
---

<h2><span class="n">1</span>这一章要解决的问题</h2>

<p class="lede">工具不是「给模型多几个 API」。工具是 agent 唯一能改变世界的手，所以工具的设计同时决定了三件事：<b>它能不能做对、它会不会做过头、出事之后能不能查。</b></p>

<h2><span class="n">2</span>三类缺口</h2>

<table>
  <thead><tr><th style="width:120px;">缺口</th><th style="width:200px;">例子</th><th>不补会怎样</th></tr></thead>
  <tbody>
    <tr><td>算不准</td><td>「8 月发了多少封邮件」</td><td>它给一个听起来合理的数字，且无法核对</td></tr>
    <tr><td>不知道现在</td><td>汇率、库存、今天的日程</td><td>用训练数据里的旧值回答</td></tr>
    <tr><td>改不了</td><td>写文件、发邮件、建工单</td><td>只能建议，不能完成</td></tr>
  </tbody>
</table>

<p>课程把第三类单独拎出来，因为它是<b>唯一有副作用的一类</b>。前两类错了可以重试，第三类错了不可撤销。整个 Part 2 的审批、deny 规则、沙箱，都是为了这一类存在的。</p>

<h2><span class="n">3</span>接口的三次搬家</h2>

<p>课程把工具使用的历史写成一条标准化的线，值得记住的是每次搬家<b>省掉了什么</b>：</p>

<table>
  <thead><tr><th style="width:150px;">阶段</th><th style="width:210px;">代表工作</th><th>省掉了什么</th></tr></thead>
  <tbody>
    <tr><td>学习调用</td><td>Toolformer</td><td>证明了模型可以自学「何时该调 API」</td></tr>
    <tr><td>规模化</td><td>Gorilla、ToolLLM</td><td>从几个 API 到上千个：检索候选工具、纠正参数幻觉</td></tr>
    <tr><td>协议化</td><td>REST → function calling → MCP</td><td>不再把「怎么调」写在提示词里，改由运行时提供 schema</td></tr>
  </tbody>
</table>

<p>MCP（Model Context Protocol）是第三次搬家的当前形态：<b>工具的发现、schema、调用、权限从应用里抽出来，变成一个可插拔的服务。</b>它的意义不在于多了一个协议，而在于工具终于可以像依赖一样被安装、被替换、被审计。</p>

<div class="box finding"><span class="t">但课程偏偏不给你 function calling</span>
<p>作业提供的模型原语只有 <code>lm(messages) -&gt; str</code>，没有 tool calling、没有 JSON mode。这不是复古，是教学顺序：<b>你必须在没有任何协议支持的情况下实现一次工具调用，才会知道协议替你做了什么。</b>做完 A2 的 <code>run_parse_response</code>，你再看 MCP 的 schema，就会明白它省掉的是「截断、嵌套、多调用、参数类型」这四类边界处理。</p></div>

<h2><span class="n">4</span>工具设计：描述就是文档</h2>

<p>模型的全部信息来自 tool 的 <code>name</code>、<code>description</code> 和 <code>parameters</code>。课程把这句话重复了两次，因为它是 Part 2 里最容易被糊弄过去的地方：<b>描述写得含糊，模型就会错用，而你会以为是模型不行。</b></p>

<p>一个可操作的写法是「三段式」：做什么、边界在哪、返回什么形状。</p>

<pre><code>run_terminal:
  "Run one shell command in a workspace that holds the email archive and
   documents. Arguments must be plain shell: no here-documents, no command
   substitution, no redirection. Write multi-line Python as python3 -c '...'.
   Returns the exit code, stdout and stderr. Large output is truncated in
   the middle."</code></pre>

<p>第二句就是边界。课程里有一句很实用的观察：<b>被测模型在没被告知的情况下会写 here-document</b>，而被沙箱拒绝。加了那一句，这类失败基本消失 —— 这是「提示词即接口文档」的直接证据。</p>

<h2><span class="n">5</span>五个设计决策</h2>

<table>
  <thead><tr><th style="width:130px;">决策</th><th style="width:230px;">问题</th><th>参考实现的选择</th></tr></thead>
  <tbody>
    <tr><td><b>粒度</b></td><td>一个「查邮件」还是「搜 / 读 / 摘要」三个？</td><td>拆开：搜索返回指针，读返回窗口。粒度粗会让模型只能猜</td></tr>
    <tr><td><b>返回值</b></td><td>整篇文档还是片段？</td><td>片段 + doc_id + 总行数，让它自己决定读不读</td></tr>
    <tr><td><b>错误</b></td><td>抛异常还是返回错误文本？</td><td>返回 <code>tool_error</code> 结果，内容含异常消息；循环继续</td></tr>
    <tr><td><b>幂等</b></td><td>同一个调用重复执行安全吗？</td><td>读操作天然幂等；写操作交给审批层</td></tr>
    <tr><td><b>可观测</b></td><td>调用留痕吗？</td><td>transcript 里记 name、args、status、content —— 这是事后归因的唯一依据</td></tr>
  </tbody>
</table>

<h2><span class="n">6</span>怎么测工具使用</h2>

<p>课程列了三个基准，各自的切面不同：</p>

<ul>
  <li><b>BFCL</b>（Berkeley Function Calling Leaderboard）：给定工具与请求，能不能选出正确的工具并给出正确参数。这是 A2 的 live 测试形态（20 个请求，至少 18 个正确）。</li>
  <li><b>ToolBench</b>：工具数量大、真实 API 多，考的是「在几千个工具里找到对的那个」。</li>
  <li><b>τ-bench</b>：把工具调用放进<b>多轮对话</b>里，还有一个模拟用户在配合或捣乱。这是 A6 的评测形态。</li>
</ul>

<p>三者的递进关系是：单轮选对 → 大规模选对 → 多轮里仍然对。多数系统在前两关及格，在第三关崩掉，因为多轮引入了「用户改主意」和「上一步的结果要保留」。</p>

<h2><span class="n">7</span>落到作业上</h2>

<ul>
  <li><b>A2 · tool_registry</b>：把「校验」和「执行」分成两步。这不是洁癖 —— 审批必须在执行前发生，而<b>一个参数都不合法的调用不该拿去问用户</b>。</li>
  <li><b>A2 · tool_protocol</b>：自己实现 tool calling 的文本层。三个函数：渲染工具、解析回复、格式化调用（第三个是给测试用的，这样测试不依赖你选的格式）。</li>
  <li><b>A3</b>：把 Part 1 的检索改造成「给模型用的接口」，并给终端加上观测策略 —— 一次命令可能打印 218,000 个字符。</li>
</ul>

<h2><span class="n">8</span>延伸阅读</h2>

<table>
  <thead><tr><th style="width:70px;">类型</th><th style="width:250px;">材料</th><th>读它的理由</th></tr></thead>
  <tbody>
    <tr><td>必读</td><td><a href="https://modelcontextprotocol.io/specification/2025-06-18">Model Context Protocol Specification</a>, 2025-06-18</td><td>看它如何定义 tools / resources / prompts 三类原语，以及权限模型</td></tr>
    <tr><td>选读</td><td>Yao et al. <i>τ-bench</i>, 2024</td><td>为什么工具调用必须放在对话里测；A6 的方法论来源</td></tr>
    <tr><td>选读</td><td>Patil et al. <i>Gorilla</i>, 2023</td><td>参数幻觉的两种形态（编造参数名、编造取值）与检索式纠错</td></tr>
  </tbody>
</table>
