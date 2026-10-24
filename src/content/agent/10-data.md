---
kind: chapter
order: 10
title: "数据：agent 需要的不是语料，是轨迹"
short: "数据"
summary: "传统机器学习要标注，agent 要的是 traces——它做了什么、看到什么、为什么停。这一章讲 trace 的三种用法（优化/评测/训练）、数据飞轮怎么转，以及「小而准」为什么比「大而糙」更值钱。"
part: "第三部 · 变好"
label: "第 10 章"
prereq: "第 9 章"
reading: "约 28 分钟"
date: 2026-10-24
ready: true
tags: [ai-agents, 教材式笔记]
lang: zh
---

<h2><span class="n">1</span>这一章要解决的问题</h2>

<p class="lede">一个 agent 每天产生成千上万条轨迹，其中大部分是垃圾。这一章讲怎么把其中少数几条变成可用的东西 —— 以及为什么<b>「挑得准」比「收得多」重要一个数量级</b>。</p>

<h2><span class="n">2</span>三种数据，三种用途</h2>

<table>
  <thead><tr><th style="width:130px;">类型</th><th style="width:230px;">内容</th><th>用在哪</th></tr></thead>
  <tbody>
    <tr><td><b>Traces</b></td><td>完整的动作序列：每步的工具、参数、结果、状态</td><td>归因（为什么失败）、蒸馏（教小模型）、回归（同一问题重放）</td></tr>
    <tr><td><b>Demonstrations</b></td><td>「正确做法」的示范轨迹</td><td>few-shot、微调、作为评测的参考解</td></tr>
    <tr><td><b>Feedback</b></td><td>用户评价、judge 判定、人工标注</td><td>打分、筛选、构造偏好对（DPO）</td></tr>
  </tbody>
</table>

<p>三者里最被低估的是 trace。它同时是<b>调试记录、训练素材和测试用例</b>：一条失败轨迹修好之后，就该变成一条回归测试。课程作业的 <code>transcript</code> 之所以设计成 append-only 的事件日志，正是为了让这三件事都成立。</p>

<h2><span class="n">3</span>数据飞轮</h2>

<pre><code>线上流量 → traces → 失败归因 → 新评测用例 / 新示范
   ↑                                    ↓
   └──────── 优化（prompt / 权重）──────┘</code></pre>

<p>飞轮的关键不是「收集」，而是<b>归因那一步有产出</b>。如果一批 trace 看完只能说「效果不好」，飞轮就不转。有产出的归因长这样：</p>

<ul>
  <li>「23 个失败里，11 个是检索没召回，7 个是召回但答案被上下文截断，5 个是模型编造。」</li>
  <li>→ 于是你得到三个不同的任务，而不是一个笼统的「提升效果」。</li>
</ul>

<h2><span class="n">4</span>合成数据：什么时候安全</h2>

<p>课程把合成数据放在这一讲，但给了一个很重要的限定条件：<b>合成数据必须可被验证</b>。</p>

<table>
  <thead><tr><th style="width:150px;">场景</th><th style="width:230px;">能不能合成</th><th>为什么</th></tr></thead>
  <tbody>
    <tr><td>有执行反馈的任务</td><td>能，且效果好</td><td>代码跑不跑通、SQL 查不查得出，可自动验证（SWE-smith 路线）</td></tr>
    <tr><td>格式/风格转换</td><td>能</td><td>输出对不对一眼可判</td></tr>
    <tr><td>开放式事实问答</td><td>危险</td><td>没有验证器时，合成数据把幻觉固化成训练目标</td></tr>
  </tbody>
</table>

<div class="box note"><span class="t">一个可操作的判据</span>
<p>问：<b>这条合成样本，我能不能用一个程序判断它对不对？</b>能，合成是净收益；不能，你只是在用模型的猜测训练模型。</p></div>

<h2><span class="n">5</span>小而准 vs 大而糙</h2>

<p>课程列了两篇结论一致的必读/选读：LIMA 说「一千条精心挑选的样本足以对齐」，而 <i>Who Validates the Validators?</i> 说「让模型当评审，必须先验证评审本身」。</p>

<p>合起来是一句话：<b>数据的价值在质量密度，不在条数。</b>对 agent 尤其如此 —— 一条包含完整失败归因的轨迹，信息量大于一百条「成功了但不知道为什么」的轨迹。</p>

<h2><span class="n">6</span>从 agent 轨迹造数据集</h2>

<p>课程给了一条具体路径（第 7 讲）：从轨迹里挖样本。可操作的步骤是：</p>

<ol>
  <li><b>按结果分组</b>：成功 / 失败 / 安全拒绝。三类都要留，第三类最容易被丢掉。</li>
  <li><b>在失败组里按根因打标</b>：检索、工具选择、参数、上下文、终止、权限。</li>
  <li><b>每条样本保留最小可复现集</b>：任务 + 初始状态 + 判定方式。不要存整段对话 —— 它太大，且大部分无关。</li>
  <li><b>划分四份</b>：development / validation / test / adversarial。前三份防止你过拟合评测集，第四份防止你把「安全」当成「效果」的副产品。</li>
</ol>

<h2><span class="n">7</span>落到作业上</h2>

<p><b>A6</b> 的评测集就是这套方法的产物：20 个 persona 按类别覆盖 7 种任务，其中 2 个是对抗性的；评分用「程序化检查 + judge」双层，前者判事实，后者判对话质量。<b>A7</b> 要求 50 条以上可重复评测任务，并且必须包含成功、失败与安全拒绝三类案例。</p>

<div class="box takeaway"><span class="t">一个反直觉的验收</span>
<p>A7 的验收表里有一条：<b>「失败案例按根因分类」</b>。它比「通过率」更能说明你懂不懂自己的系统 —— 通过率可以靠调参碰上去，根因分类不能。</p></div>

<h2><span class="n">8</span>延伸阅读</h2>

<table>
  <thead><tr><th style="width:70px;">类型</th><th style="width:250px;">材料</th><th>读它的理由</th></tr></thead>
  <tbody>
    <tr><td>必读</td><td>Shankar. <i>Data Flywheels for LLM Applications</i>, 2024</td><td>飞轮的四个环节，以及为什么「归因」是瓶颈</td></tr>
    <tr><td>必读</td><td>Yang et al. <i>SWE-smith: Scaling Data for Software Engineering Agents</i>, 2025</td><td>有执行反馈时，合成数据怎么规模化</td></tr>
    <tr><td>必读</td><td>Shankar et al. <i>Who Validates the Validators?</i>, UIST 2024</td><td>LLM 评审与人类偏好不一致的实证；做 judge 之前必读</td></tr>
    <tr><td>选读</td><td>Zhou et al. <i>LIMA: Less Is More for Alignment</i>, 2023</td><td>「一千条足够」的原始实验与它的适用边界</td></tr>
  </tbody>
</table>
