---
kind: index
title: "Agent 工程：从复合系统到可评测的智能体"
short: "Agent 工程"
summary: "以 Stanford CS 329Z 为主线，把 18 讲的理论压成 12 章，把课程作业的 17 个 problem 重排成 7 个可交付的作业。每一章讲清一个决策点，每一个作业给出可直接运行的实现与可验证的完成标准。"
date: 2026-10-24
tags: [Agent, LLM, 检索, 评测, 教材式笔记]
lang: zh
steps:
  - part: "理论线 · 12 章"
    items:
      - title: "01 什么是 agentic 系统"
        href: "/agent/01-what-is-an-agentic-system.html"
        note: "复合系统、workflow 与 agent 的分界"
        state: done
      - title: "02 面向构建者的 LLM"
        href: "/agent/02-llm-for-builders.html"
        note: "解码、上下文、受约束输出"
        state: done
      - title: "03 检索"
        href: "/agent/03-retrieval.html"
        note: "chunking、BM25、hybrid、agentic RAG"
        state: done
      - title: "04 工具"
        href: "/agent/04-tools.html"
        note: "function calling 到 MCP"
        state: done
      - title: "05 编排框架"
        href: "/agent/05-orchestration.html"
        note: "DSPy 与 LangGraph 各自替你做了什么"
        state: done
      - title: "06 设计模式与 scaffold"
        href: "/agent/06-patterns-and-scaffolds.html"
        note: "ReAct、Reflexion、CodeAct、上下文管理"
        state: done
      - title: "07 记忆"
        href: "/agent/07-memory.html"
        note: "四类记忆与四种架构"
        state: done
      - title: "08 多智能体"
        href: "/agent/08-multi-agent.html"
        note: "何时该用，为何失败"
        state: done
      - title: "09 优化"
        href: "/agent/09-optimization.html"
        note: "prompt / 权重 / 测试时算力"
        state: done
      - title: "10 数据"
        href: "/agent/10-data.html"
        note: "traces、合成数据、数据飞轮"
        state: done
      - title: "11 评测"
        href: "/agent/11-evaluation.html"
        note: "4-tuple、grader、pass@k 与 pass^k"
        state: done
      - title: "12 安全与前沿"
        href: "/agent/12-safety-and-frontier.html"
        note: "权限、沙箱、间接注入；编码与主动式 agent"
        state: done
  - part: "作业线 · A0 前置 + 7 个作业"
    items:
      - title: "A0 环境与 LM 层"
        href: "/agent/a0-environment.html"
        note: "先让「模型」可控、可复现、可记账"
        state: done
      - title: "A1 流水线与检索底座"
        href: "/agent/a1-pipelines-and-retrieval.html"
        note: "P1–P4 · 23 分"
        state: done
      - title: "A2 工具与主循环"
        href: "/agent/a2-tools-and-loop.html"
        note: "P5–P8 · 17 分"
        state: done
      - title: "A3 检索与终端"
        href: "/agent/a3-retrieval-and-terminal.html"
        note: "P9–P10 · 11 分"
        state: done
      - title: "A4 压缩与记忆"
        href: "/agent/a4-compaction-and-memory.html"
        note: "P11–P12 · 16 分"
        state: done
      - title: "A5 交互与安全"
        href: "/agent/a5-interaction-and-safety.html"
        note: "P13–P14 · 11 分"
        state: done
      - title: "A6 评测与备忘"
        href: "/agent/a6-evaluation.html"
        note: "P15–P17 · 40 分"
        state: done
      - title: "A7 结课项目：从零到一个 agent"
        href: "/agent/a7-capstone.html"
        note: "自选领域 · 三版本对照 · 50 个评测任务"
        state: done
---

<h2><span class="n">1</span>这个系列是什么</h2>

<p class="lede">一句话：把「怎么造一个 agent」拆成 12 个决策点和 7 段可交付的代码，每一个决策点都说清取舍，每一段代码都能跑、能验证。</p>

<p>Stanford 的 CS 329Z《Engineering AI Agents》2026 年秋季开课，18 讲，从「什么是 agentic 系统」一路讲到安全与前沿。它和多数 LLM 课程不同的地方在于：<b>它不教你怎么调 API，它教你为什么这个系统会以这种方式失败。</b>课程的主线是一条抽象递进链 —— 单次调用 → 固定流水线 → 复合系统 → 自主 agent —— 而每一层抽象都带来新的失效模式。</p>

<p>这套笔记做两件事。第一，把那 18 讲压成 12 章，去掉课堂语境，保留判断依据。第二，把课程作业 <code>assignment1-harness</code> 的 17 个 problem 重新分成 7 个作业：<b>因为课程的题号是按「知识点」排的，而学习的顺序应该按「依赖」排。</b></p>

<div class="box finding"><span class="t">一个必须先说明的发现</span>
<p>课程大纲里给出的 GitHub 组织地址 <code>github.com/cs329zss</code> 目前<b>并不存在</b>（匿名访问与组织 API 都返回 404）。课程真正在用的组织是 <code>github.com/cs329z</code>，下面三件都在里面：<code>assignment1-harness</code>（HW1 起始仓库，含 26 页 handout）、<code>cs329z.github.io</code>（主页源码）、<code>lecture5-frameworks</code>（第 5 讲 DSPy / LangGraph 跟练 notebook）。</p>
<p>所以本系列的作业规格不是从课表推测的，而是逐条对齐 handout 里的 problem 编号、adapter 签名与通过阈值。课程仍在更新（HW2 尚未公开发布），涉及未来的部分在正文里明确标为 TBA。</p></div>

<h2><span class="n">2</span>两条线怎么交叉</h2>

<p class="lede">理论章按「组件 → 变好 → 边界」排，作业线按依赖串行。每章末尾会指出它的知识点落在哪个函数上。</p>

<p>不要把两条线当成「先读完全部理论再做题」。这套材料的读法是<b>锯齿形</b>：读第 1、2 章建立坐标系，然后做 A0 和 A1（此时会反复回查第 3 章），再做 A2（回查第 4、6 章），以此类推。理论章的作用是你卡住时的查阅点，不是通关前置。</p>

<table>
  <thead><tr><th style="width:56px;">讲次</th><th style="width:200px;">主题</th><th style="width:150px;">对应章</th><th>它解决的问题</th></tr></thead>
  <tbody>
    <tr><td class="num">L01</td><td>引言：什么是 agentic 系统</td><td>第 1 章</td><td>workflow 与 agent 的界线画在哪</td></tr>
    <tr><td class="num">L02</td><td>面向构建者的 LLM</td><td>第 2 章</td><td>哪些旋钮真的在你手里</td></tr>
    <tr><td class="num">L03</td><td>RAG</td><td>第 3 章</td><td>检索错在哪一步，怎么归因</td></tr>
    <tr><td class="num">L04</td><td>工具使用与函数调用</td><td>第 4 章</td><td>接口标准化省掉了哪一层工作</td></tr>
    <tr><td class="num">L05</td><td>框架与编排</td><td>第 5 章</td><td>框架替你做了什么，代价是什么</td></tr>
    <tr><td class="num">L06</td><td>设计模式与 scaffold</td><td>第 6 章</td><td>五种模式各自适配什么问题</td></tr>
    <tr><td class="num">L07</td><td>记忆架构</td><td>第 7 章</td><td>记住什么，忘掉什么</td></tr>
    <tr><td class="num">L08</td><td>多智能体系统</td><td>第 8 章</td><td>什么时候单 agent 反而更强</td></tr>
    <tr><td class="num">L09</td><td>优化</td><td>第 9 章</td><td>该动 prompt、动权重，还是加算力</td></tr>
    <tr><td class="num">L10</td><td>嘉宾：Terminal-Bench</td><td>第 11 章</td><td>真实任务的基准怎么设计</td></tr>
    <tr><td class="num">L11–12</td><td>Agentic 系统的数据 / 数据质量</td><td>第 10 章</td><td>训练与评测的数据从哪来</td></tr>
    <tr><td class="num">L13–14</td><td>评估基础 / LLM-as-Judge</td><td>第 11 章</td><td>怎么知道它变好了</td></tr>
    <tr><td class="num">L15</td><td>安全与护栏</td><td>第 12 章</td><td>权限该给到多细</td></tr>
    <tr><td class="num">L16–18</td><td>编码 agent / 主动式 / 开放问题</td><td>第 12 章</td><td>这一类系统的边界在哪</td></tr>
  </tbody>
</table>

<h2><span class="n">3</span>作业清单</h2>

<p class="lede">A0 是前置，A1–A7 七个作业覆盖官方 17 个 problem、118 分。分值不是重点，<b>「覆盖」那一列才是</b> —— 它告诉你这个作业在整条链上承担什么。</p>

<table>
  <thead><tr><th style="width:52px;">作业</th><th style="width:186px;">主题</th><th style="width:96px;">覆盖</th><th>你交付什么</th></tr></thead>
  <tbody>
    <tr><td class="num">A0</td><td><b>环境与 LM 层</b></td><td>前置 · 0 分</td><td>一个只有「消息进、字符串出」的模型接口，外加缓存、账本、预算和可脚本化的假模型</td></tr>
    <tr><td class="num">A1</td><td><b>流水线与检索底座</b></td><td>P1–P4 · 23 分</td><td>单次分类、多调用摘要、从零 BM25 倒排索引、多跳 RAG 问答</td></tr>
    <tr><td class="num">A2</td><td><b>工具与主循环</b></td><td>P5–P8 · 17 分</td><td>工具注册表、文本工具调用协议、agent 主循环、完整工具集</td></tr>
    <tr><td class="num">A3</td><td><b>检索与终端</b></td><td>P9–P10 · 11 分</td><td>面向 agent 的检索接口（指针 + 短证据）、带观测策略的终端工具</td></tr>
    <tr><td class="num">A4</td><td><b>压缩与记忆</b></td><td>P11–P12 · 16 分</td><td>守住上下文预算的压缩策略、跨会话持久记忆</td></tr>
    <tr><td class="num">A5</td><td><b>交互与安全</b></td><td>P13–P14 · 11 分</td><td>审批/拒绝/steering/反问，deny 规则与间接注入防御</td></tr>
    <tr><td class="num">A6</td><td><b>评测与备忘</b></td><td>P15–P17 · 40 分</td><td>模拟用户评测、一页实测记录、两页设计备忘</td></tr>
    <tr><td class="num">A7</td><td><b>结课项目</b></td><td>自选 · 不设官方分</td><td>换一个你自己的领域，从问题定义走到可演示：三个版本对照、50 个评测任务的评测集、20 例红队、一份 Demo</td></tr>
  </tbody>
</table>

<div class="box note"><span class="t">A7 为什么必须换领域</span>
<p>A1 到 A6 用的都是课程给的语料（Cardinal Energy 文档 + 邮件档案），规格是别人写好的 —— 你只需要实现。<b>而真实工作里最难的从来不是实现，是决定做什么。</b>A7 从这个位置开始：自选用户与任务，自己论证这题为什么需要 agent，自己造评测集，自己划定权限边界。它没有官方分值，因为它评的不是「对错」，是「这件事值不值得做、你说不说得清」。</p></div>

<div class="box note"><span class="t">为什么不是 17 个作业</span>
<p>官方题号是按知识点排的：P3 是 BM25，P4 是多跳问答，两者都以「检索」为地基。如果按题号逐个做，你会在 P4 卡住时才发现 P3 的索引结构选错了。<b>合并按依赖</b>之后，A1 内部先做 P3 再做 P4，你会在同一份代码里看到这个决定的后果 —— 这正是 handout 里 design memo 想让你说清的事。</p></div>

<div class="box note"><span class="t">与仿写仓库的关系</span>
<p>设计作业时参考了 <a href="https://github.com/DuGuanhuan/cs329z-self-study">DuGuanhuan/cs329z-self-study</a>（一个非官方的 12 周自学计划）。它的价值在<b>练习设计</b>而不在代码：真正落地的只有 week-01，两个作业各是一页 README，没有代码也没有阈值。所以这里借的是它的方法论，不是它的规格。</p>
<p>被吸收的六条，都在正文里标了出处：<b>三版本对照</b>（单次调用 → 固定 workflow → 自主 agent，逼你先证明这题需要 agent）、<b>Agent 六要素</b>（目标·环境·状态·动作·策略·停止条件）、<b>重复动作检测</b>（官方停止条件只有轮数/令牌/上下文，没有这一条）、<b>四层评测</b>（组件 / 轨迹 / 结果 / 系统）、<b>记忆元数据</b>（来源·置信度·敏感级别·过期，且用户可查可删）、<b>红队 20 例 / 7 类</b>。</p></div>

<h2><span class="n">4</span>验证边界</h2>

<p class="lede">这套材料的可信度分三层，读的时候请对号入座。我不想让你把「我实测过」和「课程原文这么写」混为一谈。</p>

<table>
  <thead><tr><th style="width:118px;">层次</th><th style="width:180px;">内容</th><th>凭什么可信</th></tr></thead>
  <tbody>
    <tr><td><b>一手</b></td><td>课表、讲次、必读文献、problem 编号与分值、阈值与接口签名</td><td>直接取自课程官网、26 页 handout、仓库源码与 <code>tests/</code>；引用时给出原始出处</td></tr>
    <tr><td><b>我的实测</b></td><td>参考实现的接口、确定性测试结果、性能数字、踩过的坑</td><td>配套 <code>agentlab</code> 参考实现可下载可运行，本页的数字来自实际执行</td></tr>
    <tr><td><b>我的判断</b></td><td>章节切分、作业分组、决策清单里的取舍建议</td><td>标明是判断，不是课程观点；与讲义冲突时以讲义为准</td></tr>
  </tbody>
</table>

<div class="box takeaway"><span class="t">一处必须诚实的地方</span>
<p>作业里的<b>效果类</b>阈值（例如「60 封邮件分类一致率 ≥85%」）需要真实模型才能产生数字。参考实现提供两类测试：确定性测试（不调模型，验证机制与契约）和标记为 <code>live</code> 的效果测试（需要你自己的 API key）。本系列给出的实测数字只覆盖前者；后者我会写清命令与判定方式，但不会伪造分数。</p></div>

<h3>参考实现在哪</h3>

<p>配套的 <code>agentlab</code> 就在本站仓库里：<a href="https://github.com/jinbeiwang/jinbeiwang.github.io/tree/main/agentlab">github.com/jinbeiwang/jinbeiwang.github.io/tree/main/agentlab</a>。零运行时依赖，Python 3.11+，约 3200 行实现加约 1100 行测试（87 个用例）：</p>

<pre><code>git clone https://github.com/jinbeiwang/jinbeiwang.github.io
cd jinbeiwang.github.io/agentlab
python -m pytest                 # 87 passed，不需要 API key
python -m agentlab bench         # 用内置的假模型跑一遍，看它输在哪</code></pre>

<p><b>它不是标准答案。</b>它是"一份可以被反驳的实现"—— 每一处判断都在网页正文里写了理由，包括几处我认为可以更好的地方（<code>remember</code> 的来源标记、Windows 上没有沙箱、BM25 不做词干化）。你按照作业页重写一遍，然后和它对照，比读它更有用。</p>
