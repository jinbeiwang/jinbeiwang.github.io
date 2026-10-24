---
kind: chapter
order: 11
title: "评测：pass@k 与 pass^k 是两个问题"
short: "评测"
summary: "4-tuple 框架、三种 grader、judge 的已知偏差，以及一个最容易被忽略的指标——pass^k：同一个任务跑 k 次，每次都成功了吗。"
part: "第三部 · 变好"
label: "第 11 章"
prereq: "第 10 章"
reading: "约 35 分钟"
date: 2026-10-24
ready: true
tags: [ai-agents, 教材式笔记]
lang: zh
---

<h2><span class="n">1</span>这一章要解决的问题</h2>

<p class="lede">「通过率 85%」这句话在 agent 上几乎没有信息量。它没说是哪个任务集、跑了多少次、谁来判、判什么。<b>评测的难点不是算分，是把任务说清楚到可以算分。</b></p>

<h2><span class="n">2</span>4-tuple：把一个任务说清楚</h2>

<p>课程给的框架是四个字段，缺一个，这个任务就不可复现：</p>

<table>
  <thead><tr><th style="width:150px;">字段</th><th style="width:250px;">要写清什么</th><th>写不清会怎样</th></tr></thead>
  <tbody>
    <tr><td><b>Request</b></td><td>用户到底说了什么（原话）</td><td>你测的是自己想象的任务</td></tr>
    <tr><td><b>Environment</b></td><td>初始状态：有哪些文件、哪些服务、哪些数据</td><td>同一任务两次运行结果不同，且无法复现</td></tr>
    <tr><td><b>Stopping criteria</b></td><td>什么算做完：轮数、token、显式成功信号</td><td>agent 跑不完，你就测不了</td></tr>
    <tr><td><b>Scorer</b></td><td>谁来判、判什么、阈值多少</td><td>分数不可比，也无从解释</td></tr>
  </tbody>
</table>

<p>课程把 stopping criteria 单列，是因为 agent 评测里最常见的坑就在这：<b>任务没有「做完」的定义，评测就变成了「跑到预算耗尽」，而你测的是预算。</b></p>

<h2><span class="n">3</span>三种 grader</h2>

<table>
  <thead><tr><th style="width:130px;">grader</th><th style="width:230px;">强弱</th><th>典型用法</th></tr></thead>
  <tbody>
    <tr><td><b>代码判定</b></td><td>强：确定、便宜、可复现；弱：只能判可形式化的东西</td><td>「回复里有没有那个数」「那个命令有没有被执行」</td></tr>
    <tr><td><b>人工判定</b></td><td>强：能判质量；弱：贵、慢、不一致</td><td>抽样校准、构造黄金集</td></tr>
    <tr><td><b>LLM judge</b></td><td>强：能判开放式质量；弱：有系统偏差</td><td>对话质量、是否编造、rubric 逐条判定</td></tr>
  </tbody>
</table>

<div class="box finding"><span class="t">课程作业的双层设计值得照抄</span>
<p>一场对话只有在<b>三件事同时成立</b>时才算成功：agent 没抛异常、所有程序化检查通过、judge 判定通过。前两层是代码，最后一层是模型。<b>代码层挡住「事实错误」，judge 层挡住「答对了但过程不可接受」</b>（比如靠猜、靠把用户的话复述一遍）。</p>
<p>更关键的是：<b>被模拟用户说「我的目标达成了」不算证据</b> —— 用户无法核实事实。这一条挡掉了最常见的一种假阳性。</p></div>

<h2><span class="n">4</span>judge 的已知偏差</h2>

<ul>
  <li><b>位置偏差</b>：成对比较时偏向第一个（或第二个）出现的答案。</li>
  <li><b>长度偏差</b>：更长、更结构化的答案得分更高，即使内容相同。</li>
  <li><b>自我偏好</b>：judge 偏爱与自己风格相近的输出。</li>
  <li><b>格式偏好</b>：带小标题和列表的答案被认为更「有条理」。</li>
</ul>

<p>对策不是换一个「更好的 judge」，而是<b>设计上抵消</b>：成对比较时随机交换顺序、把 rubric 拆成可独立判定的条目、要求 judge 指出证据所在（课程让 judge 看到工具调用的前 300 字符，以及「结果中还有哪段包含你引用的数字」）、定期用人工抽样校准。</p>

<h2><span class="n">5</span>pass@k 与 pass^k：这一章最重要的一节</h2>

<table>
  <thead><tr><th style="width:120px;">指标</th><th style="width:230px;">定义</th><th>回答的问题</th></tr></thead>
  <tbody>
    <tr><td><b>pass@k</b></td><td>跑 k 次，<b>至少一次</b>成功</td><td>「这题它会不会做」</td></tr>
    <tr><td><b>pass^k</b></td><td>跑 k 次，<b>每次都</b>成功</td><td>「这题它能不能稳定做对」</td></tr>
  </tbody>
</table>

<p>两个数会差得很远。一个 pass@5 = 90% 的系统，如果每次独立成功率是 0.9，那 pass^5 ≈ 0.59；如果失败是相关的（同一个错误反复出现），pass^5 会更低。</p>

<p>对 agent 来说，<b>pass^k 才是用户感受到的指标</b>：没人会把同一个请求提交五次取最好的一次。课程在作业里明确提醒「分数在两次运行之间会上下浮动约一场对话」，就是在说这件事 —— 你要留出余量，因为用户不会重试。</p>

<div class="box note"><span class="t">一个实际后果</span>
<p>如果你的 20 场评测里 16 场通过（刚好满分线），那么换一批同分布的 20 场，你很可能掉到 15 场。<b>这不是评测噪声，这是你真实的 pass^k 水平。</b>课程的做法是在另一批 20 个 persona 上复测，用同一套阈值 —— 这一步比分数本身更能说明系统的稳定性。</p></div>

<h2><span class="n">6</span>基准设计与 harness</h2>

<p>课程把「怎么建一个好基准」当成独立议题，列了可操作的性质：任务真实（有真实的环境与真实的失败模式）、脚手架真实（用真实的工具与预算，而不是为基准特调的提示词）、判分可复现、难度有梯度、失败原因可归类。</p>

<p>最后一条最容易被忽略，也最有用：<b>一个只会告诉你「错」的基准，无法指导改进。</b>课程第 10 讲的嘉宾来自 Terminal-Bench，其设计就是把「真实终端任务」做成可判分的集合 —— 任务本身就是一条命令序列，判分看最终状态，而不是看模型说了什么。</p>

<h2><span class="n">7</span>落到作业上</h2>

<ul>
  <li><b>A6 · sim_eval</b>：20 场模拟用户对话，7 类任务，双层判分。16 场及格，每少一场扣 1 分。评分表在 <code>evaluate.py</code>。</li>
  <li><b>A6 · field_notes</b>：用你自己的 agent 做 5 个真实请求（文档、邮件、终端、需确认、应拒绝），每条都要<b>核对答案对不对</b>。这一项考的是你会不会验证，不是会不会用。</li>
  <li><b>A6 · design_memo</b>：10 个设计决策各一段。它其实是「把你的 4-tuple 写出来」—— 每个决策都要能指向代码或保存的对话。</li>
</ul>

<h2><span class="n">8</span>延伸阅读</h2>

<table>
  <thead><tr><th style="width:70px;">类型</th><th style="width:250px;">材料</th><th>读它的理由</th></tr></thead>
  <tbody>
    <tr><td>必读</td><td>Zhu et al. <i>Establishing Best Practices for Building Rigorous Agentic Benchmarks</i>, 2025</td><td>4-tuple 的来源；它列出的「不合格基准」清单可以直接当自检表</td></tr>
    <tr><td>必读</td><td>Grace et al. <i>Demystifying Evals for AI Agents</i>, Anthropic, 2026</td><td>8 步路线图；工程视角，不是论文视角</td></tr>
    <tr><td>必读</td><td>Zheng et al. <i>Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena</i>, NeurIPS 2023</td><td>三类偏差的实证与缓解手段</td></tr>
    <tr><td>选读</td><td>Polo et al. <i>tinyBenchmarks</i>, ICML 2024</td><td>「小而准」的评测集能省多少；与第 10 章呼应</td></tr>
  </tbody>
</table>
