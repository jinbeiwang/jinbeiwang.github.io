---
kind: chapter
order: 8
title: "多智能体：先证明单 agent 不够"
short: "多智能体"
summary: "多智能体不是「更高级的 agent」。它是一种用通信成本换并行度与专业化分工的交易，而课程专门讲了一节「它们为什么失败」。"
part: "第二部 · 组件"
label: "第 8 章"
prereq: "第 6–7 章"
reading: "约 26 分钟"
date: 2026-10-24
ready: true
tags: [ai-agents, 教材式笔记]
lang: zh
---

<h2><span class="n">1</span>这一章要解决的问题</h2>

<p class="lede">课程在第 8 讲的开头就问了一句不太客气的话：<b>什么时候不该用多智能体？</b>答案是「大多数时候」。这一章讲清那条分界线画在哪。</p>

<h2><span class="n">2</span>单 agent 为什么常常更强</h2>

<p>多智能体引入的每一层通信，都是一次信息损耗：A 把任务描述给 B，B 的理解不等于 A 的意图；B 的结果回到 A，A 要重新判断它是否可信。而单 agent 的优势是<b>它只有一份上下文</b> —— 没有翻译、没有交接、没有「我以为你知道」。</p>

<p>课程把一篇标题很直白的文章列为选读：<i>Don't Sleep on Single-agent Systems</i>。它的论点是：很多被归因为「需要多智能体」的问题，实际是<b>单 agent 的工具不够好或上下文没管好</b>。</p>

<div class="box finding"><span class="t">一个判断顺序</span>
<p>遇到「一个 agent 做不完」时，按这个顺序排查：工具粒度是否太粗？上下文是否被无关内容占满？系统提示是否没写清职责？<b>这三条都排除之后</b>，才轮到「拆成多个 agent」。反过来做，你会得到一个通信开销大于分工收益的系统。</p></div>

<h2><span class="n">3</span>三种编排模式</h2>

<table>
  <thead><tr><th style="width:130px;">模式</th><th style="width:230px;">控制流</th><th>适合</th><th style="width:130px;">典型失效</th></tr></thead>
  <tbody>
    <tr><td><b>Orchestrator</b></td><td>一个调度者拆任务、分派、汇总</td><td>子任务可预先切分</td><td>调度者成为瓶颈与单点</td></tr>
    <tr><td><b>Swarm</b></td><td>agent 之间互相 handoff，没有中心</td><td>任务边界模糊、需要接力</td><td>来回踢皮球，无人负责</td></tr>
    <tr><td><b>Hybrid</b></td><td>分层：上层调度，下层自主</td><td>规模大、需要局部自治</td><td>层间语义漂移</td></tr>
  </tbody>
</table>

<h2><span class="n">4</span>通信的三种基础设施</h2>

<p>课程把「怎么通信」和「怎么协调」分开讲，这个区分很实用：前者是消息怎么走，后者是状态怎么一致。</p>

<table>
  <thead><tr><th style="width:150px;">机制</th><th style="width:250px;">作用</th><th>坑</th></tr></thead>
  <tbody>
    <tr><td><b>Handoff</b></td><td>把控制权连同上下文一并交给另一个 agent</td><td>上下文丢了关键约束，接手的 agent 不知道</td></tr>
    <tr><td><b>Message board</b></td><td>共享一块可读写的区域，异步协作</td><td>写入无主、重复劳动、状态过期</td></tr>
    <tr><td><b>A2A 协议</b></td><td>标准化的 agent 间调用（能力发现、任务、结果）</td><td>协议解决传输，不解决「谁该负责」</td></tr>
  </tbody>
</table>

<p>协调基础设施更底层，也更决定成败：<b>task ledger</b>（谁认领了什么、做到哪）、<b>shared memory</b>（共享事实的一致性）、<b>worktree isolation</b>（多个 agent 改代码时不互相踩）。最后一条在编码 agent 里是刚需 —— 两个 agent 同时改同一个文件，冲突不是「可能发生」，是「必然发生」。</p>

<h2><span class="n">5</span>它们为什么失败</h2>

<p>课程指定了一篇系统性的失败分析（Cemri et al., 2025），把多智能体系统的失败归到几类根因。归纳起来是三句话：</p>

<ol>
  <li><b>任务描述在传递中失真。</b>上游的约束没被下游继承，于是下游做得「对」，但不对题。</li>
  <li><b>协调本身消耗了预算。</b>互相确认、等待、重试占掉的 token 与轮数，超过了并行省下的。</li>
  <li><b>验证缺位。</b>没有独立的校验者时，一个 agent 的错误会被另一个 agent 当作前提继续推导 —— 错误被放大而不是被发现。</li>
</ol>

<p>第三点解释了为什么 orchestrator–workers 常配一个 reviewer：不是为了更好，是为了<b>有一个不共享前提的视角</b>。但 reviewer 也会被同样的前提误导，除非它有自己的工具去查证。</p>

<h2><span class="n">6</span>什么时候值得</h2>

<p>三种情况值得认真考虑多智能体：</p>

<ul>
  <li><b>可并行且互不依赖</b>：比如同时审 20 个文件。并行收益是线性的，通信成本接近零。</li>
  <li><b>需要不同的工具权限</b>：一个只能读、一个能写，物理隔离比提示词约束可靠。</li>
  <li><b>需要独立验证</b>：生成者与验证者用不同的上下文，避免「自己检查自己」。</li>
</ul>

<p>反过来说，<b>「任务太复杂所以拆开」不成立</b>。复杂任务的子任务之间通常有依赖，拆开之后依赖变成通信，而通信是最容易丢信息的地方。</p>

<h2><span class="n">7</span>落到作业上</h2>

<p>课程作业没有把多智能体作为必做项 —— 这是一个信号。它的位置在 <b>A7 结课项目的可选扩展</b>：如果你的任务确实有可并行、可隔离的部分，做一个「Planner + 2 Worker + Reviewer」的对照实验，<b>并且必须在质量或延迟上有可测量收益，否则回退到单 agent。</b>这条「否则回退」是自学计划 Week 10 的验收标准，参考实现把它写进了 A7 的验收表。</p>

<h2><span class="n">8</span>延伸阅读</h2>

<table>
  <thead><tr><th style="width:70px;">类型</th><th style="width:250px;">材料</th><th>读它的理由</th></tr></thead>
  <tbody>
    <tr><td>必读</td><td>Wu et al. <i>AutoGen</i>, COLM 2024</td><td>「对话即编排」的原始设定；看它如何用消息传递表达控制流</td></tr>
    <tr><td>必读</td><td>Cemri et al. <i>Why Do Multi-Agent LLM Systems Fail?</i>, 2025</td><td>失败分类学；做多智能体之前先读这篇，能省很多时间</td></tr>
    <tr><td>选读</td><td>Neubig. <i>Don't Sleep on Single-agent Systems</i>, 2024</td><td>反面论证，写得克制</td></tr>
  </tbody>
</table>
