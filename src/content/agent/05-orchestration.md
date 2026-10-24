---
kind: chapter
order: 5
title: "编排框架：DSPy 和 LangGraph 各自替你做了什么"
short: "编排框架"
summary: "框架不是加速器，是观点的封装。DSPy 认为「提示词应该被编译出来」，LangGraph 认为「agent 应该是一张显式状态图」。知道它们各自的观点，才知道什么时候不该用。"
part: "第二部 · 组件"
label: "第 5 章"
prereq: "第 3–4 章"
reading: "约 30 分钟"
date: 2026-10-24
ready: true
tags: [ai-agents, 教材式笔记]
lang: zh
---

<h2><span class="n">1</span>这一章要解决的问题</h2>

<p class="lede">课程第五讲现场演示了两个框架，然后要求学生<b>不用框架</b>做完整个作业。这个安排不矛盾：先看清框架替你决定了什么，你才有资格决定要不要用。</p>

<p>课程把工程实践归到三根支柱上：<b>data（数据）、system（系统）、evals（评测）</b>。框架的价值只在第三根柱子上体现 —— 如果它让你的系统更难评测，那它就是负资产，无论代码少了多少行。</p>

<h2><span class="n">2</span>DSPy：把提示词当成编译产物</h2>

<p>DSPy 的核心主张是：<b>不要手写提示词，声明输入输出，让优化器去搜提示词和示例。</b>三个概念：</p>

<table>
  <thead><tr><th style="width:110px;">概念</th><th style="width:250px;">是什么</th><th>对应手写版</th></tr></thead>
  <tbody>
    <tr><td><b>signature</b></td><td>声明「入参 → 出参」以及一句任务描述</td><td>你的 prompt 模板</td></tr>
    <tr><td><b>module</b></td><td>可组合的调用单元（Predict / ChainOfThought / ReAct）</td><td>你的 pipeline 函数</td></tr>
    <tr><td><b>optimizer</b></td><td>拿训练集和指标，搜出更好的指令与 few-shot 示例</td><td>你反复改提示词的手工过程</td></tr>
  </tbody>
</table>

<p>换来的东西很实在：第 9 章讲的 GEPA、MIPROv2 都是这条路线上的优化器，能把「凭感觉调提示词」变成「用一个指标搜」。</p>

<div class="box note"><span class="t">代价在哪</span>
<p>优化器需要一个<b>指标函数</b>和一份<b>带标签的数据</b>。没有这两样，DSPy 退化成一个写得比较绕的提示词模板。所以它的真实门槛不是学框架，是<b>你有没有评测集</b> —— 这也解释了为什么课程把评测放在第 13–14 讲，却在第 5 讲就提优化器：两者是一件事的两面。</p></div>

<h2><span class="n">3</span>LangGraph：把 agent 画成状态图</h2>

<p>LangGraph 的主张相反：<b>agent 是一张图，节点是步骤，边是跳转，状态是显式对象。</b></p>

<pre><code>state  → 一个 TypedDict，声明所有会被读写的东西
node   →  一个函数：state -> 局部更新
edge   →  固定跳转，或由函数决定的条件下一个节点
checkpoint → 每一步的状态快照，可回放、可中断、可恢复</code></pre>

<p>它解决的是手写循环最难处理的三件事：<b>循环里有分支</b>、<b>长任务要能中断恢复</b>、<b>跑完要能回放</b>。第三点尤其重要 —— 一个 while 循环出问题，你只有一行行日志；一张图出问题，你能看到状态在第几个节点被改坏。</p>

<h2><span class="n">4</span>两者的分界</h2>

<table>
  <thead><tr><th style="width:130px;"></th><th style="width:250px;">DSPy</th><th>LangGraph</th></tr></thead>
  <tbody>
    <tr><td>核心隐喻</td><td>程序（可编译、可优化）</td><td>状态机（可回放、可中断）</td></tr>
    <tr><td>它优化的是</td><td>提示词与示例</td><td>控制流与状态</td></tr>
    <tr><td>你必须先有</td><td>指标 + 标注数据</td><td>清楚的状态定义</td></tr>
    <tr><td>不适合</td><td>一次性脚本、无评测集</td><td>单轮问答、无分支的流水线</td></tr>
    <tr><td>隐藏了什么</td><td>最终发出的提示词长什么样</td><td>边与边之间的隐式耦合</td></tr>
  </tbody>
</table>

<h2><span class="n">5</span>另一条路：把循环写短</h2>

<p>课程还列了三个开源 harness，它们的共同点是<b>用极少的代码把循环写清楚</b>：mini-SWE-agent、OpenHands、Pi。其中 mini-SWE-agent 常被引用为一个示范：整个 agent 循环不到百行，没有图、没有编译器，只有「拼消息 → 调模型 → 执行命令 → 追加结果」。</p>

<p>这不是返祖。它的论点是：<b>当评测足够好时，复杂 scaffold 的边际收益会消失</b>；而一个你能一行行读完的循环，出问题时你能改。课程在第 6 章用 Pi 做案例研究，第 9 章讲优化时还会回到这个判断。</p>

<div class="box finding"><span class="t">持久化编排为什么出现在这一讲</span>
<p>课程提到了 Temporal 一类的持久化编排与可观测性工具。原因很实际：一个跑 40 分钟的编码 agent，如果进程在第 38 分钟挂掉，你要么从头再来（贵），要么能从第 37 步的状态恢复（这才是工程）。<b>「能恢复」是长任务 agent 和演示脚本的分水岭。</b></p></div>

<h2><span class="n">6</span>怎么选</h2>

<ol>
  <li><b>先手写一遍。</b>不是为了苦行，是为了知道每个抽象背后的失败长什么样。课程强制这一步。</li>
  <li><b>看你的瓶颈在哪。</b>瓶颈是提示词质量、且有评测集 → DSPy 路线；瓶颈是控制流复杂、需要中断恢复 → LangGraph 路线。</li>
  <li><b>用同一套评测比较。</b>代码行数少 60% 不是收益；在同一个评测集上通过率不变、成本下降、或者失败可定位，才是收益。</li>
</ol>

<h2><span class="n">7</span>落到作业上</h2>

<ul>
  <li><b>A1–A6 全部手写。</b>这不是保守，是课程明确禁止使用 agent/LLM 框架库，并且不允许加依赖。</li>
  <li><b>A7 的里程碑四</b>要求你选 DSPy 或 LangGraph 重写一个组件，并用同一评测集对照：代码量、可读性、状态透明度、可测试性、调试难度、依赖成本。这一项没有标准答案，但必须给出结论 —— 而结论必须由数字支撑。</li>
</ul>

<h2><span class="n">8</span>延伸阅读</h2>

<table>
  <thead><tr><th style="width:70px;">类型</th><th style="width:250px;">材料</th><th>读它的理由</th></tr></thead>
  <tbody>
    <tr><td>必读</td><td>Khattab et al. <i>DSPy: Compiling Declarative Language Model Calls into Self-Improving Pipelines</i>, ICLR 2024</td><td>「编译」这个隐喻到底指什么；optimizer 搜的是哪两个空间</td></tr>
    <tr><td>跟练</td><td><a href="https://github.com/cs329z/lecture5-frameworks">cs329z/lecture5-frameworks</a></td><td>课程现场 notebook：DSPy 与 LangGraph 各一段，可直接跑</td></tr>
    <tr><td>选读</td><td>Anthropic. <i>Building Effective Agents</i></td><td>它把「框架」放在最后一节，并建议先用直接 API —— 与课程的立场一致</td></tr>
  </tbody>
</table>
