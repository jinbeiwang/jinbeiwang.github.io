---
kind: chapter
order: 2
title: "面向构建者的 LLM：哪些旋钮真的在你手里"
short: "面向构建者的 LLM"
summary: "解码、上下文、后训练、结构化输出、context engineering——课程第二讲不是讲模型原理，是讲构建者能控制什么、不能控制什么，以及误判边界的代价。"
part: "第一部 · 底座"
label: "第 2 章"
prereq: "第 1 章"
reading: "约 30 分钟"
date: 2026-10-24
ready: true
tags: [ai-agents, 教材式笔记]
lang: zh
---

<h2><span class="n">1</span>这一章要解决的问题</h2>

<p class="lede">几乎每一个 agent 的 bug，追溯到最后都是一句「我以为模型会……」。这一章把「会」与「不会」的边界画清楚：<b>五个旋钮里，你能拧的通常只有两个。</b></p>

<table>
  <thead><tr><th style="width:150px;">旋钮</th><th style="width:110px;">你能控制吗</th><th>说明</th></tr></thead>
  <tbody>
    <tr><td>解码策略</td><td>部分</td><td>温度、top-p 是 API 参数；<b>但课程提供的模型不接受 temperature</b>，所以同一提示两次结果可以不同</td></tr>
    <tr><td>上下文长度</td><td>是</td><td>你能决定塞多少，不能决定它注意到多少</td></tr>
    <tr><td>后训练</td><td>否</td><td>你只能用现成权重；能做的是 prompt 优化、微调、蒸馏（第 9 章）</td></tr>
    <tr><td>结构化输出</td><td>是</td><td>受约束解码需要模型支持；不支持时，你自己写解析器</td></tr>
    <tr><td>上下文工程</td><td>是</td><td>把什么放进窗口、以什么顺序、什么时候拿走 —— 构建者最大的杠杆</td></tr>
  </tbody>
</table>

<h2><span class="n">2</span>解码：为什么「同样的输入」不等于「同样的输出」</h2>

<p>贪心解码每次都取概率最高的 token，看起来最可复现，实际不是：浮点累加顺序、批处理分组、推理框架的算子选择都会让两个「相同」的请求走出不同的路径。加温度只会让它更不稳定。</p>

<p>课程把这个事实写进了作业说明：<b>模型不接受温度设置，所以同一提示两次运行结果可能不同；但相同调用的重放是免费的，因为缓存。</b></p>

<div class="box finding"><span class="t">这条说明改变了测试怎么写</span>
<p>如果你的测试断言「模型输出等于某个字符串」，它一定会间歇性失败。正确的做法是把断言放在<b>结构</b>上：解析出来的工具名对不对、参数类型对不对、预算有没有守住、失败时状态是不是 <code>malformed</code>。课程把这套测试叫 deterministic tests，它们不调模型；效果类断言另放在 <code>-m live</code> 里，用阈值而不是等号。</p></div>

<h2><span class="n">3</span>上下文：长度是容量，不是注意力</h2>

<p>第二讲讲 transformer attention（含 linear 与 hybrid 变体）与上下文长度，落点却是一个工程事实：<b>窗口变大不等于模型会用满它。</b>放在中间位置的信息被利用的概率显著低于开头和结尾，这是长上下文系统反复踩到的坑。</p>

<p>对 agent 的直接后果有三条，后面每一章都会用到：</p>

<ol>
  <li><b>检索优于堆砌。</b>把 20 封邮件全文塞进去，不如检索出 4 封、每封给出准确片段。A1 的 <code>run_email_qa</code> 之所以限制 <code>k</code> 和跳数，就是这条的工程化。</li>
  <li><b>顺序是设计变量。</b>系统提示在前、当前用户消息在后、工具结果紧跟其调用 —— 这些位置不是排版偏好，是注意力预算的分配。</li>
  <li><b>上下文会溢出，而且很快。</b>一次终端命令能打印 218,000 个字符；把它原样放进窗口，下一次调用就超预算。这就是 A3 的观测策略与 A4 的压缩必须存在的原因。</li>
</ol>

<h2><span class="n">4</span>截断：最常见的运行时异常</h2>

<p>课程定义了两种调用异常：<code>BudgetExceeded</code>（花超了）与 <code>OutputTruncated</code>（写满了）。后者更隐蔽，因为<b>推理模型把隐藏的推理 token 也算进同一个 max_tokens 上限</b> —— 你以为它在写答案，其实它已经把额度用在了思考上，返回的文本可能是空的。</p>

<pre><code>class OutputTruncated(RuntimeError):
    """The model hit max_tokens. ``.text`` is what it managed to write."""
    def __init__(self, text: str = ""):
        self.text = text</code></pre>

<p>参考实现的处理方式值得照抄：截断不抛给用户，而是<b>当作一次格式错误</b> —— 把「你的回复被截断了，请写短一点」发回给模型，连续三次才终止整个 send。理由是截断几乎总是可恢复的：模型不是不会，是话太多。</p>

<div class="box note"><span class="t">为什么不用「把 max_tokens 调大」解决</span>
<p>因为上限是双向的。调大到不会截断，就等于放弃了对单次调用成本的控制；一个循环跑了 20 轮、每轮都写满，账单是线性增长的。正确做法是<b>让上限小、让重试便宜</b>：截断 → 提示写短 → 重来，最坏情况多花一次小调用。</p></div>

<h2><span class="n">5</span>结构化输出：受约束解码 vs 自己写解析器</h2>

<p>两条路，课程选了后者，而且说得很直白：</p>

<p><b>受约束解码</b>（constrained decoding）在采样时就把不合语法的 token 屏蔽掉，所以输出必然符合 schema。代价是它需要模型/推理框架支持，而且约束越复杂，采样越慢、越容易把模型逼进它不想说的句子。</p>

<p><b>自己写协议</b>：让模型输出一段文本，你用代码把结构抠出来。课程只给你一个原语 —— <code>lm(messages) -> str</code>，没有 tool calling、没有 JSON mode —— 于是你必须自己规定格式、自己解析、自己处理解析失败。A2 的 <code>run_parse_response</code> 就是这件事。</p>

<table>
  <thead><tr><th style="width:150px;"></th><th style="width:250px;">受约束解码</th><th>自己写协议</th></tr></thead>
  <tbody>
    <tr><td>合法性</td><td>保证</td><td>不保证，要处理解析失败</td></tr>
    <tr><td>坏输入的行为</td><td>报错，或给出一个勉强合法的输出</td><td>你能决定：报错、重问、还是降级</td></tr>
    <tr><td>可移植性</td><td>绑定模型/框架</td><td>换模型不改代码</td></tr>
    <tr><td>学到什么</td><td>调参数</td><td>知道协议的成本在哪：截断、嵌套、多调用</td></tr>
  </tbody>
</table>

<h2><span class="n">6</span>context engineering：第 6 章的前置</h2>

<p>课程把 context engineering 放在这一讲收尾，并在第 6 章展开成四种手段：事件日志、压缩（compaction）、观测掩蔽（observation masking）、上下文隔离。这里只留一个判断标准，后面反复用：</p>

<div class="box takeaway"><span class="t">判断标准</span>
<p>问一句：<b>这条信息如果不进上下文，agent 还能不能重新拿到？</b>能（比如终端输出已经落盘、邮件还能再检索一次），就可以放心丢；不能（比如用户刚说的一句约束），就必须保留，而且要保留到它能被用到为止。A4 的压缩策略就是按这条线设计的。</p></div>

<h2><span class="n">7</span>落到作业上</h2>

<ul>
  <li><b>A0</b>：把 <code>lm(messages) -&gt; str</code> 这一个原语封好，加上缓存、账本、预算、两种异常。这一层做对，后面所有测试才可能确定。</li>
  <li><b>A2</b>：<code>run_render_tools</code> 是「怎么告诉模型有哪些工具」，<code>run_parse_response</code> 是「怎么把它写的抠出来」。两者合起来就是「自己实现 tool calling」。</li>
  <li><b>A4</b>：<code>context_budget</code> 是这一章「容量不是注意力」的硬约束版本 —— 它不管你注没注意到，只保证你不超。</li>
</ul>

<h2><span class="n">8</span>延伸阅读</h2>

<table>
  <thead><tr><th style="width:70px;">类型</th><th style="width:250px;">材料</th><th>读它的理由</th></tr></thead>
  <tbody>
    <tr><td>必读</td><td>Schluntz &amp; Zhang. <i>Building Effective Agents</i>, Anthropic, 2024</td><td>workflow 与 agent 的工程分界，五种模式的原始表述</td></tr>
    <tr><td>选读</td><td>Rajasekaran et al. <i>Effective Context Engineering for AI Agents</i>, Anthropic, 2025</td><td>第 6 章四种上下文手段的前身</td></tr>
  </tbody>
</table>
