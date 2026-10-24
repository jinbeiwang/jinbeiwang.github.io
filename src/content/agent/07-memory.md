---
kind: chapter
order: 7
title: "记忆：记住什么，比怎么存更重要"
short: "记忆"
summary: "四类记忆、四种架构模式，以及课程没有明说但工程上绕不开的问题：记忆的元数据、删除权，和「不该记的东西」。"
part: "第二部 · 组件"
label: "第 7 章"
prereq: "第 6 章"
reading: "约 28 分钟"
date: 2026-10-24
ready: true
tags: [ai-agents, 教材式笔记]
lang: zh
---

<h2><span class="n">1</span>这一章要解决的问题</h2>

<p class="lede">会话一结束，上下文就没了。记忆补的是这个缺口，但「记住更多」几乎总是错的 —— 真正的设计问题是<b>记住什么、记多久、谁能删</b>。</p>

<h2><span class="n">2</span>四类记忆</h2>

<table>
  <thead><tr><th style="width:130px;">类型</th><th style="width:230px;">内容</th><th>例子</th></tr></thead>
  <tbody>
    <tr><td><b>Working</b></td><td>当前任务的工作集</td><td>这一轮读过哪几封邮件</td></tr>
    <tr><td><b>Episodic</b></td><td>发生过什么（时间序）</td><td>「上周你让我别动生产库」</td></tr>
    <tr><td><b>Semantic</b></td><td>关于世界/用户的事实</td><td>「我在固件团队；说『规格』指固件规格」</td></tr>
    <tr><td><b>Procedural</b></td><td>怎么做一件事</td><td>「清理日志要先确认没有审计需要」</td></tr>
  </tbody>
</table>

<p>混用这四类是常见错误。把 procedural 存成 semantic 的句子，模型会把它当事实复述；把 episodic 当成 semantic，模型会把一次偶发偏好当成永久设定。<b>存的时候打对标签，比存得多重要。</b></p>

<h2><span class="n">3</span>四种架构模式</h2>

<table>
  <thead><tr><th style="width:170px;">模式</th><th style="width:230px;">做法</th><th>适合</th></tr></thead>
  <tbody>
    <tr><td><b>Skill library</b></td><td>把成功的操作序列存成可复用技能，下次直接调用</td><td>重复性高的任务（Voyager 路线）</td></tr>
    <tr><td><b>分层（MemGPT）</b></td><td>把上下文当内存、把外部存储当磁盘，模型自己「换页」</td><td>对话极长、无法预先判断什么重要</td></tr>
    <tr><td><b>Reflective consolidation</b></td><td>定期让模型回顾历史，抽取并合并成更少、更准的条目</td><td>事实会随时间修正（改口、更正）</td></tr>
    <tr><td><b>Maintenance</b></td><td>过期、去重、冲突消解、按访问频次降权</td><td>任何长期运行的记忆；不做就会腐烂</td></tr>
  </tbody>
</table>

<p>MemGPT 的关键动作不是「外存」，而是<b>模型自己决定换入换出</b>：它把「我要查长期记忆」变成一个工具调用。课程作业采用的正是这个形状 —— <code>remember(fact)</code> 与 <code>recall(query)</code> 两个工具，文件系统当存储。</p>

<h2><span class="n">4</span>一个必须自己回答的问题：新会话加载什么</h2>

<p>课程把这个点明确标为「你的设计决策」，并给了两个真实系统的对照：</p>

<ul>
  <li><b>Claude Code / Codex CLI / Gemini CLI</b>：会话开始时把整个指令文件读进提示词。简单、可靠，但会占掉上下文预算。</li>
  <li><b>Letta</b>：只在提示词里放一个<b>有大小上限的记忆块</b>，其余留在库里由模型用工具搜。省预算，但模型可能不知道「有东西可搜」。</li>
</ul>

<p>两种都合格。<b>不合格的是没想过这个问题</b>：如果你的记忆只有 <code>recall</code> 而没有「提示词里的一点点提示」，模型在第二场会话里根本不会想到去调它 —— 这是这类系统最典型的静默失败。</p>

<div class="box finding"><span class="t">参考实现的选择</span>
<p>折中：提示词里放<b>最近 5 条用户明说的事实</b>，加一行「还有 N 条更早的在库里，用 recall 搜」。这一行很关键 —— 它不占多少 token，但告诉模型「库存在」。<code>MemoryStore.prompt_block()</code> 就是这么写的，代码不到 10 行。</p></div>

<h2><span class="n">5</span>课程没讲、但工程上绕不开的三件事</h2>

<p>这三条来自一份非官方自学计划（Week 10），我在参考实现里全部落地了，因为缺了它们，记忆系统不能上线：</p>

<table>
  <thead><tr><th style="width:150px;">问题</th><th style="width:230px;">做法</th><th>缺了会怎样</th></tr></thead>
  <tbody>
    <tr><td><b>来源与置信度</b></td><td>每条记 <code>source</code>（user/tool/inferred）与 <code>confidence</code></td><td>模型的推测被当成事实永久保存</td></tr>
    <tr><td><b>敏感级别</b></td><td>标 <code>sensitive</code> 的条目不进提示词，只能显式 recall</td><td>工号、地址自动出现在每次请求里</td></tr>
    <tr><td><b>可查可删</b></td><td>每条有 <code>id</code>，用户能列出、能删</td><td>用户无法纠正它「记住」的错事</td></tr>
  </tbody>
</table>

<p>课程的设计备忘里有一个问题问得很准：「跑完评测后，你的记忆库里都有什么？它们值得被记住吗？漏了什么本该记住的？」—— 这三个附加字段，就是让你能回答这个问题的前提。</p>

<h2><span class="n">6</span>评测：怎么知道记忆有用</h2>

<p>课程的测法是<b>成对会话</b>：第一场用户说一个事实（「我在固件团队，说『规格』指固件规格」），第二场问一个只有靠这个事实才能答对的问题。两场只共享 <code>memory_dir</code>，不共享任何上下文。三对里至少两对答对。</p>

<p>这个设计的好处是把「记忆」和「上下文」彻底分开了：如果第二场答对，唯一的解释是它真的从磁盘读回来了。<b>而如果两场共享同一个 session，你测的其实是上下文长度，不是记忆。</b></p>

<div class="box note"><span class="t">一个反直觉的结论</span>
<p>课程明确说：<b>「把整个库加载进提示词」是合格策略，给满分。</b>因为它诚实、可预测、容易测。加分项不在复杂度，而在说清你的选择与代价。这条判断贯穿整门课 —— 第 1 章说「没有为复杂度给分」，这里又说了一遍。</p></div>

<h2><span class="n">7</span>开放问题</h2>

<ul>
  <li><b>遗忘</b>：该忘的没忘（过时的偏好）、不该忘的忘了（用户强调过的约束）。目前没有通用解法。</li>
  <li><b>隐私</b>：记忆库是一个长期累积的个人档案，它的访问控制通常比主数据库弱得多。</li>
  <li><b>过度个性化</b>：记住太多偏好，会让 agent 只会按老路走，用户想换个方式时反而被「贴心」拖住。</li>
</ul>

<h2><span class="n">8</span>落到作业上</h2>

<p><b>A4 · memory</b>：实现 <code>remember</code> / <code>recall</code> 两个工具，存储在同一目录下的文件里；同目录的新会话能看到，不同目录的看不到；空库 recall 返回非空消息。参考实现另加了三个元数据字段与 <code>forget()</code>，对应上面第 5 节。</p>

<h2><span class="n">9</span>延伸阅读</h2>

<table>
  <thead><tr><th style="width:70px;">类型</th><th style="width:250px;">材料</th><th>读它的理由</th></tr></thead>
  <tbody>
    <tr><td>必读</td><td>Packer et al. <i>MemGPT: Towards LLMs as Operating Systems</i>, 2023</td><td>「模型自己换页」这个想法的原始形状与它的失败模式</td></tr>
    <tr><td>选读</td><td>Chhikara et al. <i>Mem0</i>, 2025</td><td>生产级记忆的抽取/合并流水线，以及它的成本结构</td></tr>
    <tr><td>选读</td><td>Park et al. <i>Generative Agents</i>, UIST 2023</td><td>记忆流的打分与反思机制；「reflective consolidation」的出处</td></tr>
  </tbody>
</table>
