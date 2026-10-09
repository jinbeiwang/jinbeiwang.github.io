---
title: "Claude Code 实战：统计编程师的可复现工作流"
summary: "把 Claude Code 当成一个要写进 SOP 的生产工具，而不是聊天框：用分层记忆固化命名规则与宏库路径，用 @ 引用和 /context 把每条结论钉回源数据与版本，用子 agent 做独立 QC 与文档抽取，用 Hooks 把纪律从「嘱咐」变成「拦截」。每一项能力都配可复制的命令，语境全部落在 SAS 程序与临床试验文档上。"
date: 2026-10-09
category: Languages and practice
tags: [Claude Code, AI 工具, SAS, 临床编程, 可复现]
lang: zh
---

<div class="meta-row">
    <span><b>读者</b> &nbsp;用 SAS 做临床统计编程、想把 AI 助手接进日常交付物的人</span>
    <span><b>目标</b> &nbsp;每个能力知道「解决什么问题、命令怎么写、什么算做对了」</span>
</div>

<div class="box note" style="margin-top:26px;">
  <span class="t">范围与界定</span>
  <p class="small">这篇写的是<b>工程用法</b>：怎么让 AI 产出的代码与文档可追溯、可复现、可被第二个人复核。它不涉及任何统计方法的对错 —— 模型选择、估计口径、缺失值处理该由统计师决定，这篇一个字都不碰。文中的命令以 Claude Code 官方文档与内置命令表为口径；标注 <em class="ev">[doc]</em> 的来自官方文档，标注 <em class="ev">[实践]</em> 的是工程判断，需要你在自己环境里验证一次。</p>
  <p class="small">程序片段沿用去标识化惯例：研究编号、库名、程序头一律替换为占位符；示例数据均为构造，不含任何受试者信息。</p>
</div>


<!-- ============================================================ -->
<h2><span class="n">1</span>先把心态摆正：它是一支笔，不是一位统计师</h2>
<p class="lede">三条前置认知，决定了后面所有用法是不是用对了地方。</p>

<h3>1.1 你能验收的，只有它写得「像不像你们的程序」</h3>
<p>AI 最擅长的是<strong>有大量先例的机械劳动</strong>：按规格书生成一个 mapping、把一段 TFL 说明扩写成程序注释、把审阅意见归类成表格、把一个 300 行的老宏拆成带单测的新宏。这些任务的验收标准你手里都有。它最不擅长的，是替你判断一个统计口径 —— 那本来也不该它来判断。</p>

<div class="box takeaway"><span class="t">边界一句话</span><p>凡是「验收标准能写成一段 SAS 日志或一张比对表」的活，交给它；凡是「验收标准取决于统计师一句话」的活，让它起草、你来定稿。</p></div>

<h3>1.2 同一个词在两边意思不同</h3>
<p>「记忆」在两套语境里都指跨会话保存，但落点完全不同，一开始就分开，后面不会乱：终端里跑的那份，指的是文件系统上若干层 <code>CLAUDE.md</code>；WorkBuddy 这类桌面助手，另有自己的云侧档案与工作区 <code>memory/</code> 目录。本文只讲前者。同理，下文出现的 <code>@</code> 引用只指「提示词里 <code>@</code> 一个文件路径」，不指任何站的 @ 提及。</p>

<h3>1.3 版本会漂，先记一条查证习惯</h3>
<p>这个工具的发版节奏很快，命令名和字段名一年里会变。任何一条记不准的用法，先跑 <code>/help</code> 看当前会话里真实存在的命令清单，再决定信不信笔记。本文标注 <em class="ev">[doc]</em> 的部分以官方文档为准，落笔时会核一遍。</p>


<!-- ============================================================ -->
<h2><span class="n">2</span>溯源与可复现：让每条结论都有来路</h2>
<p class="lede">这一节解决一个问题：三个月后，你怎么证明「这段程序是按 SAP 第 6.2 节这个口径写的、用的是这个版本的数据集」。</p>

<h3>2.1 三层结构：约束在 CLAUDE.md，证据在仓库，动作在 git</h3>
<p>把「可追溯」拆成三件各自独立的事，就不会把它们混成一团：</p>
<table>
  <thead><tr><th style="width:150px;">层</th><th style="width:200px;">放什么</th><th>为什么是这一层</th></tr></thead>
  <tbody>
    <tr><td><b>约束</b></td><td><code>CLAUDE.md</code></td><td>命名规则、库路径、CDISC 版本这类「每次都要遵守」的常量。写一次，往后每次会话自动加载。</td></tr>
    <tr><td><b>证据</b></td><td>规格书、SAP 章节、define.xml、日志</td><td>论据本体。用 <code>@</code> 临时引用，不进记忆 —— 它们会改版，钉进 CLAUDE.md 就是埋一颗过期的雷。</td></tr>
    <tr><td><b>动作</b></td><td>git commit</td><td>真正不可篡改的那一层。程序与笔记都进仓库，每次生成都留一条消息。</td></tr>
  </tbody>
</table>

<div class="box finding"><span class="t">最常见的踩法 —— 把规格书塞进 CLAUDE.md</span><p>规格书是<em>证据</em>，不是<em>约束</em>。它会随版本改：SDTM IG 从 3.2 到 3.4，变量长度、受控术语都动过。一旦把「本变量的长度是 200」这类具体值写进常驻记忆，模型会一直照着旧值干活，而日志里不会有一句报错。让 <code>CLAUDE.md</code> 只说「变量长度以 <code>@spec/define.xml</code> 为准，不要写死」，需要时当次引用具体文件。</p></div>

<h3>2.2 用 <code>@</code> 把源文件钉进这一轮对话</h3>
<p>在提示词里写 <code>@路径</code>，Claude Code 会把这个文件完整读进当前上下文（<code>@</code> 后打路径会自动补全）。要让它从 SAP 抽取变量清单，就把 SAP 当次引用进去，而不是让它凭记忆猜：</p>

<pre><code><span class="cm"># 从 SAP 的一节里抽 TFL 的变量清单，逐条注明出自哪句</span>
读 @docs/sap_v3.1.docx 的「Table 14.1.2」一节，抽出这张表要展示的变量清单，
每条后面附上 SAP 里对应的原句（英文原文照抄，不要改写），
输出成三列：变量名 / 来源数据集（ADSL 或 ADAE） / SAP 原句。

<span class="cm"># 读规格书 + define.xml，交叉核对同一个变量</span>
分别看 @spec/sdtm_spec.xlsx 和 @spec/define.xml 里 AE 域的 AESTDTC，
两边对不上就把差异列成表格，不要替我选一个「正确的」。

<span class="cm"># 手上有两份数据，直接让程序说明差异出自哪一步</span>
@programs/adsl.sas 与 @logs/adsl.log 一起看：找出这条 NOTE 是哪个 DATA step 触发的，
指到具体行号，并解释它是不是预期行为。</code></pre>

<div class="box note"><span class="t">一句话换一个确定性</span><p class="small">规则很简单：凡是你要写进文档、发给统计师或进审阅意见的结论，它引用的每个文件这一轮都必须在上下文里。<code>@</code> 比「我看过那个文件」可靠得多，因为前者会在 <code>/context</code> 里留下可核对的痕迹。</p></div>

<h3>2.3 用 <code>/context</code> 定期核对「它到底看到了什么」</h3>
<p><code>/context</code> 可视化当前上下文窗口中加载了什么、各占多少 token。<em class="ev">[doc]</em> 这是溯源最容易漏的一环：你以为模型读了规格书，其实那一段早被压缩掉了，而它仍会自信地给出结论。<em class="ev">[实践]</em> 一个工作习惯是 —— 在让它产出任何要进文档的东西之前，先 <code>/context</code> 看一眼关键证据文件还在不在窗口里；不在就补 <code>@</code> 重新引用。</p>

<pre><code><span class="cm"># 长会话里，先看窗口被什么占满了，再决定压不压缩</span>
/context

<span class="cm"># 需要腾空间时，带上焦点压缩，别让它把证据也压掉</span>
/compact 保留 SAP 那一节和 define.xml 的变量定义，其余可以摘要</code></pre>

<h3>2.4 每个程序一块 git 记录，写清「依据哪一版」</h3>
<p>真正可追溯的那一层是 git，而它只对<strong>你写进 commit 消息的内容</strong>负责。让 AI 代笔时，要求它把依据版本写进消息正文：</p>

<pre><code><span class="cm"># 让它按模板生成提交信息，正文里带依据版本与数据快照</span>
把这次改动做成一次 commit，消息按这个模板写：
  <span class="mk">adsl: derive TRTSDT from EX domain per SAP v3.1 §4.3</span>
  <span class="mk">Source: ADSL spec v2.4, define.xml checksum 9f2c</span>
  <span class="mk">Data snapshot: SDTM 2026-09-15</span>

<span class="cm"># 需要对照「谁在什么时候动了哪一行」时，直接问它</span>
git log -p -3 -- programs/adsl.sas &gt; /tmp/hist.txt

<span class="cm"># 生成一份可直接贴进 QC 记录的改动摘要</span>
把 git diff 的要点整理成「改了什么 / 为什么 / 影响哪些输出」三栏表</code></pre>

<div class="box takeaway"><span class="t">本节结论</span><p>约束进记忆、证据进引用、动作进 git —— 三层各司其职。查证一个结论的来路时，顺序也照这个走：先看 <code>CLAUDE.md</code> 里定的规则，再看当次 <code>@</code> 引用过的文件在 <code>/context</code> 里是否还在，最后落到 <code>git log</code> 上的那一行。</p></div>


<!-- ============================================================ -->
<h2><span class="n">3</span>记忆管理：分层、固化、以及别把它喂脏</h2>
<p class="lede">记忆的默认行为是「越具体越靠后、越靠后越优先」，弄清楚加载顺序，才不会出现两个文件互相打架。</p>

<h3>3.1 四个层级，按作用域从宽到窄</h3>
<table>
  <thead><tr><th style="width:190px;">层级</th><th>位置</th><th style="width:120px;">谁看得到</th></tr></thead>
  <tbody>
    <tr><td><b>企业策略</b></td><td>组织级统一部署（Windows 通常落在 <code>C:\ProgramData\ClaudeCode\CLAUDE.md</code>，由 IT 管理）<em class="ev">[doc]</em></td><td>全组织</td></tr>
    <tr><td><b>用户记忆</b></td><td><code>~/.claude/CLAUDE.md</code></td><td>你自己，所有项目</td></tr>
    <tr><td><b>项目记忆</b></td><td><code>./CLAUDE.md</code> 或 <code>./.claude/CLAUDE.md</code></td><td>整个项目组，随 git 分发</td></tr>
    <tr><td><b>目录记忆</b></td><td>子目录下的 <code>CLAUDE.md</code>，读到该目录文件时才加载</td><td>项目组</td></tr>
  </tbody>
</table>
<p>加载顺序是「先宽后窄」：企业 → 用户 → 项目，越靠后越具体、优先级越高。<em class="ev">[doc]</em> 查找方式是递归的 —— 从当前工作目录往上级走，一路上的 <code>CLAUDE.md</code> 都会被收进来；而子目录里的那份，只有当你真的读到那个子目录的文件时才加载。</p>

<div class="box note"><span class="t">重点：目录记忆不是自动全量加载的</span><p class="small">这一点在临床试验文档库里特别好用。项目根目录放总规则，<code>programs/</code>、<code>specs/</code>、<code>qc/</code> 各自的 <code>CLAUDE.md</code> 写各自的口径 —— 它们在真正用到时才会占用上下文，不会在每次会话开头就一起压进来。</p></div>

<h3>3.2 值得固化的，只有这四类</h3>
<p>写进记忆的每一条都是成本：它会占上下文、会被模型当真理。值得固化的只有「每一次都要遵守、且基本不变」的那几条。<em class="ev">[实践]</em></p>
<table>
  <thead><tr><th style="width:190px;">固化什么</th><th>例子（示意，请替换成你自己的）</th></tr></thead>
  <tbody>
    <tr><td><b>命名与编程规范</b></td><td>数据集名全大写；衍生变量必须带 <code>ABLFL</code> 标记的那套写法；宏名以 <code>%m_</code> 开头；每个程序头部必须有的注释块字段。</td></tr>
    <tr><td><b>宏库与库路径</b></td><td><code>%inc "/projects/&lt;study&gt;/macros/common.sas";</code> 这一句放哪；常用库的 libname 名与指向。</td></tr>
    <tr><td><b>CDISC 与版本口径</b></td><td>本项目用 SDTM IG 哪个版本、ADaM IG 哪个版本、CT 以哪一版为准 —— <em>只写版本号与「以 define.xml 为准」，不写具体变量定义</em>。</td></tr>
    <tr><td><b>不可逾越的红线</b></td><td>提交服务器的源码必须全 ASCII；不许自动改 <code>qc/</code> 下任何文件；受试者信息不许出现。</td></tr>
  </tbody>
</table>

<h3>3.3 两个写入口：<code>/init</code> 起手，<code>#</code> 随手补</h3>
<p>第一次进一个新仓库，让它自己扫一遍生成底稿；日常工作里发现它反复犯同一个错，就地固化。</p>

<pre><code><span class="cm"># 1. 起手：扫仓库生成 CLAUDE.md 底稿，然后你手工删掉猜错的部分</span>
/init

<span class="cm"># 2. 打开记忆文件编辑（会在系统编辑器里打开，适合成段整理）</span>
/memory

<span class="cm"># 3. 随手固化：以 # 开头的一句话会被问存到哪一层</span>
<span class="mk"># 所有衍生数据集必须先按 USUBJID 排序，再参与 merge</span>

<span class="cm"># 4. 让目录记忆分层：先建目录，再逐个子树补规则</span>
mkdir -p .claude &amp;&amp; touch .claude/CLAUDE.md</code></pre>

<h3>3.4 避免记忆污染的三条硬规矩</h3>
<div class="box finding"><span class="t">规矩一 —— 不写会过期的事实</span><p>具体数值、具体行号、具体某次日志的结论，都不进记忆。写「口径以规格书为准」，把规格书当次引用。判断标准：这条信息六个月后还成立吗？不成立就出去。</p></div>
<div class="box finding"><span class="t">规矩二 —— 不写互相矛盾的两条</span><p>两层记忆给出不同答案时，模型会挑一条遵循，而它未必挑对，日志里也不会有提示。定期 <code>/memory</code> 通读一遍，看到打架的就删掉旧的。</p></div>
<div class="box finding"><span class="t">规矩三 —— 个人偏好放用户层，别混进项目层</span><p>「我习惯用 <code>proc print</code> 看数据集」是你的习惯，不是团队规范。这类内容进 <code>~/.claude/CLAUDE.md</code>，随 git 分发出去会污染同事的环境。</p></div>

<div class="box takeaway"><span class="t">本节结论</span><p>记忆只固化「每次都遵守、且基本不变」的约束。四类候选 —— 命名规范、宏库路径、CDISC 版本、红线；除此之外一律当次引用，不进常驻记忆。</p></div>


<!-- ============================================================ -->
<h2><span class="n">4</span>子 agent：把 QC 交给一个没看过你草稿的人</h2>
<p class="lede">子 agent 的价值不在「更快」，而在「独立」—— 它有自己的上下文窗口和工具边界，看不到主会话里的推理过程，因此不会被你的思路带偏。</p>

<h3>4.1 为什么 QC 必须用一个独立的上下文</h3>
<p>同一个上下文里让模型「再检查一遍自己刚写的东西」，效果很有限，因为它复用的是同一批假设。<em class="ev">[实践]</em> 子 agent 是一次全新的读取：你把两份产物丢给它，它只做比对，不背主会话的包袱。这正是独立 QC 想要的关系 —— 复核者不参与创作。</p>

<h3>4.2 定义一个只读的比对 agent</h3>
<p>子 agent 是 <code>.claude/agents/</code> 下的一个 Markdown 文件，YAML 头写身份与权限，正文就是它的系统提示。<em class="ev">[doc]</em> 只读类复核 agent 只给 <code>Read, Grep, Glob</code>，不给写权限 —— 分工就写死在能力边界里：</p>

<pre><code><span class="cm">--- .claude/agents/qc-compare.md ---</span>
<span class="kw">---</span>
<span class="kw">name:</span> qc-compare
<span class="kw">description:</span> 独立比对两份 SAS 产物或一套程序的逻辑不一致。用于 QC 复核、双人编程比对。只读，不修改任何文件。
<span class="kw">tools:</span> Read, Grep, Glob
<span class="kw">model:</span> sonnet
<span class="kw">---</span>
你是独立 QC。你拿到的两份产物中，至少有一份不是你写的，
因此不要假设任何一方是对的、也不要说「看起来没问题」。

逐条比对两份产物，按三类给出结论：
  1. 硬差异 —— 同一观测在不同产物里取值不同，给出 USUBJID / 变量 / 两边取值
  2. 结构差异 —— 行数、列数、类型、长度不一致
  3. 覆盖差异 —— 一边有、另一边没有的记录

输出一张表：类别 / 定位（受试者 + 变量）/ 生产方取值 / QC 方取值 / 判定
判定只用三个词：一致 / 存疑 / 不一致。
最后一行给总数。不要解释可能的原因，那是统计师的事。</code></pre>

<h3>4.3 定义文档抽取 agent，只做「只进不出」的搬运</h3>
<p>文档抽取类任务要求零改写 —— 从 SAP、审阅意见里搬出结构化条目，一个词都不许润色。给它配上专用提示，明确「原文照抄」：</p>

<pre><code><span class="cm">--- .claude/agents/comment-triager.md ---</span>
<span class="kw">---</span>
<span class="kw">name:</span> comment-triager
<span class="kw">description:</span> 把审阅意见或会议记录整理成结构化条目，逐条保留原文与出处。不解读、不改写。
<span class="kw">tools:</span> Read, Grep, Glob
<span class="kw">---</span>
输入是一份审阅意见或会议记录。把它拆成条目，每条一行，四列：
  序号 / 类型（统计 / 编程 / 文档 / 其他） / 原文（照抄，含说话人） / 出处（文件 + 页码或小节）

规则：原文列必须逐字照抄，不许改标点、不许缩写、不许翻译。
类型判断不确定时填「其他」，并在末尾单列一行为「需人工确认」。
不要给处理建议，不要合并重复条目 —— 合并会丢掉「有两个人提了同一件事」这个信息。</code></pre>

<h3>4.4 怎么调用、怎么拆、怎么汇总</h3>
<p>子 agent 由主会话用任务工具派发，也可以直接点名；关键是给它一个<strong>能独立完成、只倒数条结论</strong>的任务边界：</p>

<pre><code><span class="cm"># 直接指名调用（在提示词里点名该 agent）</span>
用 qc-compare 比一下 @programs/adsl.sas 产出的 ADSL 和 @qc/adsl_qc.sas 产出的 QC 版本，
只看 TRTSDT / TRTEDT / SAFFL 三个变量。

<span class="cm"># 分治：三个域各自派一个，互不干扰</span>
并行派三个 qc-compare：分别比对 AE、CM、EX 三个域的生产版与 QC 版。
每个只回一张差异表，最后我来汇总。

<span class="cm"># 汇总时要求合并成一张总表，而不是三段散文</span>
把刚才三个 agent 的结论合并成一张表，加一列「域」，
按「不一致 → 存疑 → 一致」排序，只保留前两类。</code></pre>

<div class="box note"><span class="t">管理命令与两个已知限制</span><p class="small"><code>/agents</code> 用于列出、创建、管理子 agent。<em class="ev">[doc]</em> 两个限制值得先知道：子 agent <b>不能再开子 agent</b>；每次调用都是全新上下文，不会继承主会话聊到一半的共识 —— 所以派活时要在提示词里把前提说全，别指望它「记得刚才」。<em class="ev">[doc]</em></p></div>

<div class="box takeaway"><span class="t">本节结论</span><p>子 agent 的用法分两种：一是<em>独立复核</em>（读、只回差异表），二是<em>机械抽取</em>（读、只回结构化条目）。两种都靠「只读工具 + 只回结论」的边界来保证整洁；把它当平行抄写员，别当决策者。</p></div>


<!-- ============================================================ -->
<h2><span class="n">5</span>一张能力映射表：每个功能配哪个 SAS 场景</h2>
<p class="lede">功能名先对齐到具体场景，再看后面几节各自怎么用。这张表是全篇的索引。</p>

<table>
  <thead>
    <tr><th style="width:150px;">能力</th><th>解决什么（SAS 语境）</th><th style="width:150px;">命令入口</th></tr>
  </thead>
  <tbody>
    <tr><td><b>Skills</b></td><td>把可复用的作业流程固化：TFL 宏生成、SDTM 域映射、审阅意见归类</td><td><code>/技能名</code></td></tr>
    <tr><td><b>Hooks</b></td><td>把纪律变成拦截：提交前查 ASCII、编辑后跑 lint、改完程序跑 <code>proc compare</code></td><td><code>settings.json</code></td></tr>
    <tr><td><b>Slash Commands</b></td><td>一键动作：生成骨架、跑比对、出改动摘要</td><td><code>/命令名</code></td></tr>
    <tr><td><b>Plan Mode</b></td><td>动一个 300 行的老宏之前，先让它只读地给方案</td><td><code>Shift+Tab</code> / <code>/plan</code></td></tr>
    <tr><td><b>MCP</b></td><td>接上外部系统：Jira 取审阅意见、数据库读 SDTM、SAS 提交作业</td><td><code>/mcp</code></td></tr>
    <tr><td><b>检查点回滚</b></td><td>重构跑偏了，一键回到改之前的状态</td><td><code>Esc Esc</code> / <code>/rewind</code></td></tr>
    <tr><td><b>扩展思考</b></td><td>宏重构、跨程序影响面、复杂比对时，给它更多推理预算</td><td><code>/effort</code> / <code>ultrathink</code></td></tr>
    <tr><td><b>子 agent</b></td><td>独立 QC 比对、文档抽取（见第 4 节）</td><td><code>.claude/agents/</code></td></tr>
  </tbody>
</table>

<h3>5.1 Skills：可复用的作业流程</h3>
<p>一个 skill 就是 <code>.claude/skills/&lt;名字&gt;/SKILL.md</code>，YAML 头写名字与「什么时候该用它」，正文写步骤，还可以带脚本和参考文件。<em class="ev">[doc]</em> 它的省 token 之处在于渐进式披露：平时只加载一行描述，真被用到时才读全文。<em class="ev">[doc]</em> 适合固化的 SAS 作业，是那种「步骤固定、但每次数据不同」的流程。</p>

<pre><code><span class="cm"># 把一个 TFL 宏生成流程做成 skill：.claude/skills/tfl-macro/SKILL.md</span>
<span class="kw">---</span>
<span class="kw">name:</span> tfl-macro
<span class="kw">description:</span> 按 TFL 说明表生成表格宏骨架。当用户要求「生成 / 新建一个 TFL 宏」「按 shell 出表格程序」时使用。
<span class="kw">allowed-tools:</span> Read, Write, Grep
<span class="kw">---</span>
输入：TFL 说明表里的一个表号；输出：一个 <code>%m_tl_&lt;表号&gt;</code> 宏骨架。
步骤：
  1. 从说明表读出这张表的总体、分组、要展示的统计量
  2. 骨架里预置程序头注释块、宏参数、空的数据步占位
  3. 统计量名称全部对齐说明表的写法，不要自创缩写
  4. 结尾的 <code>%mend</code> 后附一行「待填」清单，列出还需要人工确认的口径

<span class="cm"># 用起来就是一句话（技能名即命令）</span>
/tfl-macro Table 14.1.2</code></pre>

<h3>5.2 Hooks：把纪律从「嘱咐」变成「拦截」</h3>
<p>写在 <code>CLAUDE.md</code> 里的「提交前检查 ASCII」，是建议，模型可能照做也可能忘；写在 Hooks 里的，是客户端强制执行。<em class="ev">[doc]</em> Hooks 配在 <code>settings.json</code> 的 <code>hooks</code> 块里，按生命周期事件触发（<code>PreToolUse</code> / <code>PostToolUse</code> / <code>Stop</code> 等），命令钩子以退出码表态：<code>0</code> 放行，<code>2</code> 拦截并把你 stderr 的内容回给模型。<em class="ev">[doc]</em></p>

<pre><code><span class="cm">/* .claude/settings.json —— 编辑 SAS 文件后自动查非 ASCII 字符 */</span>
{
  "hooks": {
    "PostToolUse": [
      { "matcher": "Edit|Write",
        "hooks": [ { "type": "command",
                     "command": "bash .claude/hooks/ascii-check.sh" } ] }
    ]
  }
}</code></pre>

<pre><code><span class="cm"># .claude/hooks/ascii-check.sh —— 提交服务器源码必须全 ASCII</span>
#!/usr/bin/env bash
file=$(jq -r '.tool_input.file_path // empty')
case "$file" in *.sas|*.SAS) ;; *) exit 0 ;; esac
<span class="kw">if</span> LC_ALL=C grep -nP <span class="mk">'[^\x00-\x7F]'</span> "$file"; then
  echo "非 ASCII 字符出现在 $file —— 提交服务器的源码必须全 ASCII" &gt;&amp;2
  <span class="kw">exit</span> 2            <span class="cm"># 退出码 2：拦截这次编辑</span>
<span class="kw">fi</span>
<span class="kw">exit</span> 0</code></pre>

<div class="box finding"><span class="t">Hook 的三条务实提醒</span><p>一，默认超时 60 秒，别在钩子里跑整批 <code>proc compare</code>，只跑单个域或快速校验。<em class="ev">[doc]</em> 二，钩子写得不好会「静默失败」—— 退出码非 0 且非 2 时不会拦截，只是不阻塞地过掉，所以写完要故意制造一次错误来验证它真的拦得住。<em class="ev">[实践]</em> 三，把「反复被嘱咐同一件事」当作写钩子的信号：凡是你在提示词里说了三遍以上的纪律，就该固化成钩子。</p></div>

<h3>5.3 Slash Commands：把反复敲的提示词收成一个词</h3>
<p>自定义命令与 skill 是同一套系统：<code>.claude/commands/foo.md</code> 与 <code>.claude/skills/foo/SKILL.md</code> 都会生成 <code>/foo</code>。<em class="ev">[doc]</em> 只带提示词、不需要脚本时，命令这种轻量形式更顺手：</p>

<pre><code><span class="cm">--- .claude/commands/cmp.md ---</span>
比对 @programs/$1.sas 与 @qc/$1_qc.sas 的逻辑差异，只看这三类：
数据集重建步骤、衍生变量的 if/else 条件、去重与排序键。
输出一张表：差异点 / 生产版写法 / QC 版写法 / 是否会影响最终输出（是/否/不确定）。
不要修改任何文件。

<span class="cm"># 用起来：把域当参数传进去</span>
/cmp adae
/cmp adlb</code></pre>

<h3>5.4 Plan Mode：动老宏之前先只读地给方案</h3>
<p>Plan Mode 是只读的：它会探索、解释、提方案，但不改文件、不执行命令。<em class="ev">[doc]</em> 用 <code>Shift+Tab</code> 循环切换，或 <code>/plan</code> 直接进入。<em class="ev">[doc]</em> 面对一个 300 行的老宏，先让它把方案摊开，你审一遍再放行 —— 比让它改完再看 diff 便宜得多。</p>

<pre><code><span class="cm"># 进入只读计划模式，附上任务描述</span>
/plan 把 @macros/m_dervar.sas 拆成三个单一职责的宏，保持所有调用点不变

<span class="cm"># 方案要问清楚「影响面」，再决定动不到手</span>
只读分析：这个宏被哪些程序 include 过？改它的接口会波及哪些输出？
列出文件与行号，不要给改法。</code></pre>

<h3>5.5 MCP：接上你已经在用的系统</h3>
<p>MCP 是把外部系统作为工具接进来的开放协议。<em class="ev">[doc]</em> 对临床编程，最有价值的三个接法是：从工单系统取审阅意见、从数据库直接读 SDTM/ADaM、把程序提交给 SAS 会话执行。配置写在项目根的 <code>.mcp.json</code>（随仓库分发）或用户级配置里。<em class="ev">[doc]</em></p>

<pre><code><span class="cm"># 查看、认证、管理当前会话可用的 MCP 服务器</span>
/mcp

<span class="cm"># 接上一个「读数据库取 SDTM」的服务，写进项目级 .mcp.json</span>
claude mcp add sdtm-db --scope project -- npx -y <span class="mk">"@vendor/sdtm-mcp"</span>

<span class="cm"># 接上工单系统，直接按编号取审阅意见进上下文</span>
从 Jira 取 STUDY-1234 的所有评论，用 comment-triager 规则整理成条目表</code></pre>

<div class="box note"><span class="t">接入前的红线</span><p class="small">MCP 让模型能对你接进来的系统<em>动手</em>，不只是读。两件事先做：一，凡是会写回生产库、会改工单状态的服务器，先只给读权限跑一遍；二，项目级 <code>.mcp.json</code> 会随仓库分发，别人的机器上也会生效，所以它的内容必须过一遍团队评审 —— 别人的一次 clone 不该等于一次未经审视的连接。</p></div>

<h3>5.6 检查点回滚：改坏了就退回去</h3>
<p>Claude Code 在每次改动前自动打检查点，按两次 <code>Esc</code> 或 <code>/rewind</code> 打开回滚菜单，可以分别退回<em>代码</em>或<em>对话</em>。<em class="ev">[doc]</em> 这让「大胆重构」变得可承受：试错了就回滚，而不是一行行手工撤回。习惯上，把回滚点当成一次微型 git —— 探索性的改动之前先确认检查点存在，改完满意了再落一次真实 commit。</p>

<pre><code><span class="cm"># 打开回滚菜单（也可连按两次 Esc）</span>
/rewind

<span class="cm"># 查看当前工作区改了什么，决定是保留还是回滚</span>
/diff</code></pre>

<h3>5.7 扩展思考：把推理预算花在刀刃上</h3>
<p>扩展思考在默认开启，模型按任务复杂度自适应地分配推理预算。<em class="ev">[doc]</em> 需要更深推理时，用 <code>/effort</code> 调档（<code>low</code> / <code>medium</code> / <code>high</code> / <code>xhigh</code> / <code>max</code>），或在提示词里写 <code>ultrathink</code> 让这一轮想得更深。<em class="ev">[doc]</em> 值不值得调高，看任务形态：字段改名、生成骨架这类，低档就好；跨程序依赖分析、复杂比对、老宏重构，才值得拉高。</p>

<pre><code><span class="cm"># 常规任务：低档，快且省</span>
/effort low

<span class="cm"># 复杂分析：拉高档位</span>
/effort high

<span class="cm"># 或者只在当前这一轮加深推理</span>
ultrathink 把这三个宏的调用关系画出来，说明改动其中一个会怎样影响
最终交付的那几张 TFL，逐条给出证据。</code></pre>


<!-- ============================================================ -->
<h2><span class="n">6</span>六个可复制的场景</h2>
<p class="lede">每个都是「一句话提示 + 期望产出」，可以直接改路径就用。</p>

<h3>6.1 从 SAP 抽取变量清单</h3>
<pre><code>读 @docs/sap_v3.1.docx 里 Table 14.1.2 的定义，抽出这张表的行标识变量与列分组变量，
输出三列：变量名 / 来源数据集 / SAP 原句（英文照抄）。
凡是 SAP 没写清楚的，最后一列留空并单独列一张「待确认」清单。</code></pre>

<h3>6.2 批量生成 TFL 宏骨架</h3>
<pre><code>@spec/tfl_list.xlsx 里有 20 张表的说明。为其中「安全性分析」那 8 张，
各生成一个 <code>%m_tl_&lt;表号&gt;</code> 宏骨架，统一程序头注释块，
统计量名称严格照说明表的写法。骨架里不要填任何统计逻辑，只留占位与「待填」清单。</code></pre>

<h3>6.3 <code>proc compare</code> 差异解读</h3>
<pre><code>@logs/adsl_cmp.log 是一次 proc compare 的输出。把差异整理成一张表：
受试者 / 变量 / 生产方取值 / QC 方取值 / 差异类型（数值 / 长度 / 缺失 / 类型）。
按差异类型分组计数，最后告诉我一共几处、涉及几个受试者。
不要猜差异原因，那是我的事。</code></pre>
<div class="box note"><span class="t">为什么要求它「不要猜原因」</span><p class="small">差异归因属于口径判断，必须由你完成。让它只做整理，反而更快 —— 你拿到一张干净的对照表，三两下就能定位到是哪个 DATA step 的哪一行。</p></div>

<h3>6.4 旧宏重构（先生成单测，再改实现）</h3>
<pre><code>/plan 把 @macros/m_dervar.sas 重构为单一职责的宏。

第一步只做一件事：为它现有行为写一份回归用例 —— 三段构造输入与期望输出，
覆盖正常路径、缺失值、重复键三种情况。

用例通过后，再动实现，且不改任何调用点的接口。</code></pre>

<h3>6.5 规格书与 define.xml 的一致性核对</h3>
<pre><code>交叉核对 @spec/adam_spec.xlsx 与 @spec/define.xml 中 ADAE 的全部变量：
类型、长度、受控术语、codelist。只列出两边对不上的，
输出：变量 / 属性 / 规格书值 / define.xml 值。
不要替我判定哪个是对的。</code></pre>

<h3>6.6 审阅意见整理与回复草稿</h3>
<pre><code>用 comment-triager 把 @docs/review_comments.docx 整理成条目表。

整理完后，另起一张表：对每条「编程」类意见，草拟一句回复要点，
但不要替我承诺任何交付时间或口径。回复要点留给我确认后再发出。</code></pre>


<!-- ============================================================ -->
<h2><span class="n">7</span>六条没被问到、但工程上最省事的原则</h2>
<p class="lede">这些不在功能清单里，但它们决定你用得顺不顺。</p>

<h3>7.1 提示词里三件必写的事</h3>
<p>派活时补全这三样，返工率会明显下降：<strong>依据哪个文件、产出什么格式、验收标准是什么</strong>。缺第一样，它会凭记忆编；缺第二样，它会给你一段散文；缺第三样，你只能自己推敲它做对没有。</p>

<h3>7.2 用 git 兜底，而不是指望它永远不出错</h3>
<p>在一条干净的基线上让它动手，它每轮改动都会落成可回滚的检查点，你自己再定期 commit。这样「出错」不再是损失，只是一次 <code>/rewind</code> 的成本 —— 你才敢真正把重复劳动外包出去。</p>

<h3>7.3 上下文到一半就压，别等它变钝</h3>
<p>上下文越满，产出越钝。实践中到约五成就主动 <code>/compact</code>，而不是等自动压缩触发 —— 那时候往往已经过了它状态最好的窗口。<em class="ev">[实践]</em> 压缩时带上焦点，明确要保住哪几段证据。</p>

<h3>7.4 平行的活分成平行会话</h3>
<p>三个域、三份文档、三条互不相干的活儿，开三个会话（或 <code>git worktree</code>）比挤在一个会话里更快，而且互不污染上下文。开新会话前先 <code>/clear</code>，让项目记忆留着、对话历史清掉。</p>

<h3>7.5 让它读你的日志，而不是只读你的代码</h3>
<p>SAS 的很多问题只有日志看得见 —— <code>NOTE: Missing values were generated</code> 是谁触发的、哪个 length 截断了字符，代码里看不出来。把日志一并引用进来，它给出的解释才落在真实执行上，而不是落在你写下的意图上。</p>

<h3>7.6 去标识化从「引用之前」开始</h3>
<p>这一条是红线，不是技巧。受试者信息、真实研究编号、真实库路径，都不该进入任何一次外部模型的上下文。养成习惯：一个专门用于协作的目录，里面的规格书摘录、程序片段、日志都先去过标识化；引用来自这个目录，而不是直接从原始项目里拖。</p>

<div class="box takeaway"><span class="t">全篇收口</span><p>把约束交给记忆、把证据交给引用、把历史交给 git；把复核交给独立上下文的子 agent、把纪律交给钩子、把复杂推理交给思考档位。这几件事各就各位之后，AI 助手就从「一个聊得不错的工具」变成了「一个能写进 SOP 的环节」—— 它做的事你都能验收，它给的结论你都查得到来路。</p></div>

<footer>
  <p><strong>验证说明</strong> 功能描述与命令以 Claude Code 官方文档与内置命令表为口径（文中标 <em class="ev">[doc]</em> 处）；标 <em class="ev">[实践]</em> 的是工程判断，需在你自己的环境中验证一次。文中未给出任何统计方法的建议，程序片段均为示意骨架。</p>
  <p><strong>去标识化</strong> 研究编号、库名、程序头与路径均已替换为占位符；示例数据为构造，不含任何受试者信息。</p>
  <p><strong>时效提醒</strong> 该工具发版较快，命令名与字段可能随版本变动。落笔时会核对一遍；使用前建议以当前会话的 <code>/help</code> 与官方文档为准。</p>
</footer>
