---
kind: chapter
order: 1
title: "什么是 agentic 系统：一条抽象递进链"
short: "什么是 agentic 系统"
summary: "模型、workflow、复合系统、agent 是四个不同的东西。分不清它们，后面所有的设计决策都会做错——包括「这题到底要不要用 agent」。"
part: "第一部 · 底座"
label: "第 1 章"
prereq: "会写 Python，用过任意一个 LLM API"
reading: "约 25 分钟"
date: 2026-10-24
ready: true
tags: [ai-agents, 教材式笔记]
lang: zh
---

<h2><span class="n">1</span>这一章要解决的问题</h2>

<p class="lede">在写下第一行 agent 代码之前，你需要一个判断：<b>这个任务需要 agent，还是只需要一个写死的流程？</b>课程第一讲把这个问题拆成了一条抽象递进链，而链上每一层都引入新的失效模式。</p>

<p>CS 329Z 的开篇论点来自 Berkeley BAIR 那篇广为引用的文章：AI 产品的能力越来越多地来自<b>多个组件的组合</b>，而不是一次模型调用。这个判断有一个常被忽略的后半句 —— 组合在带来质量、成本、控制三个杠杆的同时，也让调试和评测变难。后面十一章讲的一切，本质都是在为这个「变难」付账。</p>

<h2><span class="n">2</span>四个词，别混着用</h2>

<table>
  <thead><tr><th style="width:120px;">东西</th><th style="width:230px;">定义</th><th>谁决定下一步</th></tr></thead>
  <tbody>
    <tr><td><b>模型</b></td><td>一个输入到输出的函数</td><td>没有人：调用一次，返回一次</td></tr>
    <tr><td><b>workflow</b></td><td>控制流写死在代码里的多步程序</td><td>你的 <code>for</code> 和 <code>if</code></td></tr>
    <tr><td><b>复合系统</b></td><td>多个组件（模型、检索器、工具、验证器）协作完成任务</td><td>你的代码，但组件之间有反馈</td></tr>
    <tr><td><b>agent</b></td><td>在循环中根据当前状态选择下一步动作</td><td><b>模型</b>，在你能接受的边界内</td></tr>
  </tbody>
</table>

<p>关键区分不在「调了几次模型」，而在<b>控制权在谁手里</b>。一个 RAG 流水线可能调三次模型，但它是 workflow：检索→拼上下文→生成，路径是你写的。反过来，一个 agent 可能只调两次模型，但它自己决定第二次要查什么。</p>

<div class="box finding"><span class="t">一个反直觉的判据</span>
<p>「用了 agent 框架」不等于「是 agent」。LangGraph 里的固定图是 workflow；而一个 <code>while</code> 循环里让模型选工具，是 agent —— 哪怕它只有 40 行。<b>判断依据是控制流由谁决定，不是代码用了什么库。</b>这也是课程禁止使用 agent 框架的原因：先自己写一遍，你才知道框架替你决定了什么。</p></div>

<h2><span class="n">3</span>agent 的最小定义</h2>

<p>课程没有给一个正式定义，但工程上需要能落笔的描述。这里借用一个更实用的六要素写法（来自一份非官方自学计划，见文末），它比「感知—决策—行动」那套更接近你真正要写的东西：</p>

<pre><code>Agent = 目标 + 环境 + 状态 + 动作 + 策略 + 停止条件</code></pre>

<table>
  <thead><tr><th style="width:96px;">要素</th><th style="width:230px;">在代码里对应什么</th><th>做错了会怎样</th></tr></thead>
  <tbody>
    <tr><td><b>目标</b></td><td>用户的那句话</td><td>目标模糊，agent 会用很多步去猜你想干什么</td></tr>
    <tr><td><b>环境</b></td><td>它能读的文件、能查的库、能跑的命令</td><td>环境不可观察，它会编造观察结果</td></tr>
    <tr><td><b>状态</b></td><td>transcript：一条只追加的事件日志</td><td>状态被压缩得看不见，它就会重复劳动</td></tr>
    <tr><td><b>动作</b></td><td>工具集与参数 schema</td><td>动作粒度太粗，它只能猜；太细，它走不完</td></tr>
    <tr><td><b>策略</b></td><td>系统提示 + 工具描述 + 循环里的判断</td><td>策略写在代码里，它就没有余地</td></tr>
    <tr><td><b>停止条件</b></td><td>轮数、token、上下文、重复动作</td><td>缺一个，就有一类任务会跑到天荒地老</td></tr>
  </tbody>
</table>

<p>对照一下课程作业里那个 <code>AgentConfig</code>，你会发现它几乎就是这张表的工程版：<code>max_turns</code>、<code>token_budget</code>、<code>context_budget</code>、<code>deny_rules</code>、<code>mode</code>。<b>六个要素里，有四个最后都变成了配置项</b> —— 这是个有用的信号：如果你的 agent 设计说不出这几个数，它还没设计完。</p>

<h2><span class="n">4</span>五个问题，判断要不要 agent</h2>

<p class="lede">先设计最简单的基线，再设计 workflow，最后才设计 agent。顺序反过来，你会永远不知道 agent 到底贡献了什么。</p>

<ol>
  <li><b>执行路径能不能提前完整写出来？</b>能，就写 workflow。这条否掉了一半的「agent 项目」。</li>
  <li><b>需不需要根据中间结果改变下一步？</b>不需要，那就是流水线。</li>
  <li><b>需不需要和环境反复交互？</b>只读一次数据不算交互，要「读了才知道下一步读什么」才算。</li>
  <li><b>错误的动作能不能被检测和恢复？</b>不能检测，agent 的自主性就是纯风险。</li>
  <li><b>额外的成本和延迟值不值？</b>这个问题必须用数字回答，不能用感觉。</li>
</ol>

<div class="box note"><span class="t">第五问为什么必须有数字</span>
<p>课程作业里有一个刻意的设计：<code>email_qa</code> 只允许 3 次检索，而 <code>run_priority</code> 只允许 1 次模型调用。这不是为了省钱的道德姿态，而是<b>把「值不值」变成可测的</b>：同一批问题，1 次检索的准确率、3 次检索的准确率、不限次数的准确率，三条曲线摆在一起，你才知道多出来的自主性买到了什么。</p></div>

<h2><span class="n">5</span>抽象每上一层，失效模式换一批</h2>

<table>
  <thead><tr><th style="width:110px;">层次</th><th style="width:240px;">典型失效</th><th>什么时候才发现</th></tr></thead>
  <tbody>
    <tr><td>单次调用</td><td>格式不合预期、答非所问</td><td>解析回复时</td></tr>
    <tr><td>workflow</td><td>某一步的上游错了，下游全错，但每步都「成功」</td><td>端到端评测时</td></tr>
    <tr><td>复合系统</td><td>组件各自达标，组合起来不达标；改一处，另一处退化</td><td>做对照实验时</td></tr>
    <tr><td>agent</td><td>循环不停、反复调同一个工具、把工具输出当指令执行</td><td>跑真实用户请求时</td></tr>
  </tbody>
</table>

<p>最后一行值得多说一句。agent 独有的风险不是「答错」，而是<b>「做了不该做的事」</b>。答错可以重试，做错有副作用。这就是为什么这门课把作业的一半分值放在循环边界、审批、deny 规则和沙箱上 —— 而这些在纯文本生成系统里根本不存在。</p>

<h2><span class="n">6</span>落到作业上</h2>

<p>这一章的知识点不落在某个函数上，它落在两个决定上：</p>

<ul>
  <li><b>A1 的第一个决定</b>：<code>run_priority</code> 是一次调用，<code>run_daily_digest</code> 是多次调用但控制流在你手里 —— 这两个都是 workflow。到了 <code>run_email_qa</code>，控制权第一次交给模型（它决定再查什么），但检索次数仍在你的代码里。这条线就是「workflow 到哪里结束」的实物标本。</li>
  <li><b>A2 的核心</b>：<code>run_agent_session</code> 把控制权整体交给模型，于是你必须同时交出四道边界：轮数、token、上下文、格式错误次数。少了任何一道，第六要素就缺一块。</li>
</ul>

<div class="box takeaway"><span class="t">读完这一章，你应该能回答</span>
<p>拿你手头任何一个「想做成 agent」的想法，回答三个问题：它的路径能不能写死？它的错误能不能被自动检测？它的停止条件是哪几个数？三个都答得出来，再开工。答不出来，先写 workflow。</p></div>

<h2><span class="n">7</span>延伸阅读</h2>

<table>
  <thead><tr><th style="width:70px;">类型</th><th style="width:250px;">材料</th><th>读它的理由</th></tr></thead>
  <tbody>
    <tr><td>必读</td><td>Zaharia et al. <i>The Shift from Models to Compound AI Systems</i>, BAIR Blog, 2024</td><td>「复合系统」这个提法的出处；重点看它列出的三个杠杆和代价</td></tr>
    <tr><td>选读</td><td>Ng. <i>Agentic Design Patterns Part 1</i>, The Batch, 2024</td><td>Reflection / Tool use / Planning / Multi-agent 四种模式的入门版，第 6 章会展开</td></tr>
    <tr><td>选读</td><td>Si et al. <i>Towards Execution-Grounded Automated AI Research</i>, arXiv 2026</td><td>看一个开放式目标如何被改写成「有环境、有动作、有客观反馈」的循环</td></tr>
    <tr><td>非官方</td><td><a href="https://github.com/DuGuanhuan/cs329z-self-study">cs329z-self-study</a> 的 Week 1</td><td>本页六要素写法与「五个判断问题」的来源；它的三版本对照实验被吸收进了 A7</td></tr>
  </tbody>
</table>

<footer>
  <p><strong>与讲义的关系</strong> 本页的抽象递进与四个术语的区分依据 CS 329Z 第一讲（L01）与其必读材料；六要素写法与五个判断问题来自非官方自学计划，已在文中标注，不是课程观点。</p>
</footer>
