---
kind: chapter
order: 6
title: "设计模式与 scaffold：ReAct 只是起点"
short: "设计模式与 scaffold"
summary: "五种可组合的 workflow 模式、四种推理—行动模式（ReAct / Reflexion / CodeAct / ReWOO），以及真正决定长会话成败的四类上下文管理手段。"
part: "第二部 · 组件"
label: "第 6 章"
prereq: "第 4–5 章"
reading: "约 35 分钟"
date: 2026-10-24
ready: true
tags: [ai-agents, 教材式笔记]
lang: zh
---

<h2><span class="n">1</span>这一章要解决的问题</h2>

<p class="lede">「用 ReAct」不是一个设计。ReAct 只规定了「想一步、做一步」，没规定你想几步、什么算做完、观察太长怎么办。<b>那些没规定的部分，才是 agent 真正的设计。</b></p>

<h2><span class="n">2</span>五种 workflow 模式</h2>

<p>先看不用 agent 就能解决的部分。课程列了五种可组合的 workflow 模式（表述与 Anthropic 的 <i>Building Effective Agents</i> 一致）：</p>

<table>
  <thead><tr><th style="width:130px;">模式</th><th style="width:240px;">形状</th><th>适合</th></tr></thead>
  <tbody>
    <tr><td><b>Prompt chaining</b></td><td>A → B → C，每步输出是下一步输入</td><td>可分解、每步可校验的写作/翻译/抽取</td></tr>
    <tr><td><b>Routing</b></td><td>先分类，再分派到不同分支</td><td>请求类型差异大，处理方式完全不同</td></tr>
    <tr><td><b>Parallelization</b></td><td>同一步并行多份，或分工后汇总</td><td>独立子任务；需要投票/多视角</td></tr>
    <tr><td><b>Orchestrator–workers</b></td><td>一个调度者拆任务，多个执行者做</td><td>子任务数量事先不知道</td></tr>
    <tr><td><b>Evaluator–optimizer</b></td><td>生成 → 评审 → 修改，循环到达标</td><td>有明确质量标准、可自动判断</td></tr>
  </tbody>
</table>

<p>判断顺序是：<b>能用这五种拼出来，就不要写 agent。</b>它们的路径是你定的，所以每一步都能测、能重跑、能定位。agent 只在「路径本身要由结果决定」时才划算。</p>

<h2><span class="n">3</span>四种推理—行动模式</h2>

<table>
  <thead><tr><th style="width:110px;">模式</th><th style="width:200px;">循环里有什么</th><th>解决的问题</th><th style="width:150px;">代价</th></tr></thead>
  <tbody>
    <tr><td><b>ReAct</b></td><td>思考 → 动作 → 观察，重复</td><td>让推理与外部证据交替</td><td>步数不受控；观察会撑爆上下文</td></tr>
    <tr><td><b>Reflexion</b></td><td>做完 → 自我批评 → 带着批评重做</td><td>同一任务内的迭代改进</td><td>自我评价不可靠；成本翻倍</td></tr>
    <tr><td><b>CodeAct</b></td><td>动作是「写一段代码」，不是「调一个函数」</td><td>动作空间太大、组合太复杂</td><td>需要沙箱；错误信息更难读</td></tr>
    <tr><td><b>ReWOO</b></td><td>先整体规划，再一次性执行，最后汇总</td><td>减少串行调用、可并行</td><td>计划错则全错，且无法中途调整</td></tr>
  </tbody>
</table>

<p>四者的关系不是替代，是<b>在「灵活」与「可控」之间取不同点</b>：ReAct 最灵活最不可控，ReWOO 最可控最不灵活，Reflexion 加的是「同一任务内的多次机会」，CodeAct 换的是动作的表达方式。</p>

<div class="box finding"><span class="t">作业只要求 ReAct，但测的是另三样</span>
<p><code>run_agent_session</code> 的循环就是 ReAct 的最小实现：一次模型调用 → 最多一个工具 → 结果回填。<b>但它的测试全在 ReAct 没规定的部分</b>：轮数上限、token 上限、上下文上限、连续三次格式错误就停。这说明「模式」提供的是骨架，「边界」才是工程质量。</p></div>

<h2><span class="n">4</span>上下文管理：长会话的真正难点</h2>

<p>课程把上下文管理单列，并给了四种手段。这是本章最该带走的部分，因为它是唯一在 20 轮之后仍然决定成败的东西。</p>

<table>
  <thead><tr><th style="width:150px;">手段</th><th style="width:250px;">做法</th><th>丢掉了什么</th></tr></thead>
  <tbody>
    <tr><td><b>Event logs</b></td><td>把完整历史落成只追加的日志；模型只看其中一部分</td><td>什么都不丢，但日志本身不进上下文</td></tr>
    <tr><td><b>Compaction</b></td><td>把早期对话压成一段摘要，替换原文</td><td>细节：原文里的具体数字、路径、措辞</td></tr>
    <tr><td><b>Observation masking</b></td><td>旧工具结果替换成「已省略」占位，保留调用记录</td><td>内容，但保留了「我查过什么」</td></tr>
    <tr><td><b>Context isolation</b></td><td>子任务在独立上下文里跑，只把结论带回主循环</td><td>过程；也因此丢了可追溯性</td></tr>
  </tbody>
</table>

<p>关键区分是<b>「日志」与「模型的上下文」是两样东西</b>。课程把这一点写进了类型定义：transcript 是 append-only 的事件日志，压缩只改变发给模型的消息，<b>永远不从 transcript 里删事件</b>。理由是评测和事后归因都读 transcript —— 如果它也缩水，你就没法回答「它当时为什么那么做」。</p>

<pre><code># 只追加，不修改
transcript = [
  {"type": "user",        "content": "..."},
  {"type": "assistant",   "content": "..."},   # 模型原话
  {"type": "tool_call",   "name": "...", "args": {...}},
  {"type": "tool_result", "name": "...", "status": "ok", "content": "..."},
]</code></pre>

<h2><span class="n">5</span>观测策略：三种主流做法</h2>

<p>当一次工具调用返回 218,000 个字符，怎么办？课程列了三种真实系统里的做法，它们代表三种取舍：</p>

<table>
  <thead><tr><th style="width:150px;">做法</th><th style="width:230px;">代表</th><th>代价</th></tr></thead>
  <tbody>
    <tr><td>原样透传</td><td>mini-SWE-agent</td><td>一条命令就可能撑爆上下文</td></tr>
    <tr><td>截断（留头留尾）</td><td>Codex CLI</td><td>中间的信息永久丢失</td></tr>
    <tr><td>截断 + 落盘 + 告知路径</td><td>OpenHands / Gemini CLI / Claude Code</td><td>多一轮读文件；但信息可追回</td></tr>
  </tbody>
</table>

<div class="box takeaway"><span class="t">选哪个，取决于一句话</span>
<p><b>「被丢掉的东西，模型能不能重新拿到？」</b>能，就截断（第三种的落盘是「能」的保证）；不能，就得想别的办法。<b>参考实现选的是第二种（留头留尾）</b>，因为它的沙箱禁止重定向、没有落盘路径；这个限制在 A3 的备忘里要写清楚 —— 它是有意的取舍，不是疏忽。</p></div>

<h2><span class="n">6</span>scaffold 是设计决策，不是实现细节</h2>

<p>课程第 9 讲（编码 agent）会用一整讲讲「scaffold 即设计」：同一个模型，换个 scaffold，SWE-bench 上的分数可以差十几个点。第 6 章用 Pi 做案例，第 4 章讲 mini-SWE-agent 的极简循环 —— 两者结论一致：</p>

<p><b>模型能力是给定的，scaffold 是你唯一能改的变量。</b>而 scaffold 具体指四件事：工具怎么描述、观察怎么呈现、上下文怎么管理、循环怎么终止。这四件事，正好对应本章的四节。</p>

<h2><span class="n">7</span>落到作业上</h2>

<ul>
  <li><b>A2 · agent_loop</b>：ReAct 的最小实现，加上四道边界（轮数、token、上下文、格式错误）。</li>
  <li><b>A3 · terminal</b>：观测策略。测试会给一条打印 600,000 字符的命令，然后要求下一次调用的上下文仍在预算内。</li>
  <li><b>A4 · compaction</b>：四种手段里选一种或组合。参考实现是「先 masking，再 compaction」，因为前者免费。</li>
</ul>

<h2><span class="n">8</span>延伸阅读</h2>

<table>
  <thead><tr><th style="width:70px;">类型</th><th style="width:250px;">材料</th><th>读它的理由</th></tr></thead>
  <tbody>
    <tr><td>必读</td><td>Yao et al. <i>ReAct: Synergizing Reasoning and Acting in Language Models</i>, ICLR 2023</td><td>原始设定里，「思考」是输出的一部分，不是隐藏的；这决定了你能否审计</td></tr>
    <tr><td>选读</td><td>Shinn et al. <i>Reflexion</i>, 2023</td><td>自我批评什么时候真的有效，什么时候只是把错误说得更自信</td></tr>
    <tr><td>选读</td><td>Xu et al. <i>ReWOO</i>, 2023</td><td>规划与执行分离后，token 消耗为什么能降下来</td></tr>
  </tbody>
</table>
