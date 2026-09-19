---
title: "笔记部件样板：每个元素长什么样"
summary: "把一篇笔记能用到的部件全部摆在同一页上 —— 页头出自 frontmatter、导语、三种框、表格与判定标签、代码块、插图、页脚收口 —— 每个都标出它在页面的位置和归属的色相。写新笔记时对着这一页抄即可。"
date: 2026-09-20
category: Site notes
tags: [笔记规范, 排版, Astro]
lang: zh
---

<div class="meta-row">
    <span><b>来源</b> &nbsp;本站构建时实际渲染出的部件，与 <code>templates/new-note.md</code> 逐项对应</span>
    <span><b>状态</b> &nbsp;已由站点构建实际渲染</span>
</div>


<h2><span class="n">1</span>页头不是写出来的</h2>

<p class="lede">页头上没有一个字来自正文 —— 分类行、标题、摘要、日期、标签，全部由文件顶部的 frontmatter 生成。正文从 meta-row 开始。</p>

这是最容易踩空的一处：照着别的笔记写，很自然会想在正文顶部再敲一遍标题。**不要敲** —— 你会得到页面上两个标题。在笔记文件里，h1 这个概念不存在。

几行 frontmatter 各自负责页面上的一块：

| 字段 | 页面上出现在哪 | 必填 |
|---|---|---|
| `title` | 页头最大的那行 | <span class="pill ok">必填</span> |
| `summary` | 标题下方那段摘要 | <span class="pill ok">必填</span> |
| `date` | 页头日期，兼首页排序 | <span class="pill ok">必填</span> |
| `category` | 页头第一行，兼首页分组 | <span class="pill cav">可省</span> |
| `tags` | 页头标签，自动生成标签页 | <span class="pill cav">可省</span> |
| `lang` | 不显示，只给检索与阅读器 | <span class="pill cav">可省</span> |
| `draft` | 不显示；为 true 时整篇不进页面 | <span class="pill cav">可省</span> |

可省的四项都有默认值：`category` 落到 `Site notes`，`tags` 为空，`lang` 为 `zh`，`draft` 为 `false` —— 不写也能构建，但写清楚读者才知道自己看到的是不是作者的本意。

<div class="box note"><span class="t">范围</span><p>这里讲的是<b>外观</b>，不是原理。frontmatter 在构建期怎么被读取、集合与路由怎么走，写在另一篇 <a href="/notes/site-workflow.html">这个站怎么组织</a> 里。</p></div>


<h2><span class="n">2</span>正文里的六个部件</h2>

<p class="lede">除段落本身外，正文只有六种部件。每一种都不需要写样式 —— 写下对应的标签或类名，颜色与间距就定了。</p>

<h3>2.1 段落、出处标记与引用</h3>

段落直接写。要给一句话标出处，就在句末放一个标记：官方文档用 <em class="ev">[doc]</em>，会议论文用 <em class="ev">[lit]</em>，属于工程判断、没有公开依据的用 <em class="ev">[实践]</em>。三个就够了 —— 再多，读者就得额外记住一套编码。

标记是祖母绿的，因为「这句话有依据」属于**证据**，不属于**结构**。这条分工贯穿全站：靛蓝管你会点走的东西（分类、链接、章节序号、代码块竖线），祖母绿管你该相信的东西（出处、结论、表格、图号）。

引用别人或强调一句话时用引用块，它的左边线是祖母绿：

> 版式住在 layout 和两张样式表里，永远不在笔记文件里。

<h3>2.2 三种框，三种语气</h3>

框只有三种，选错等于说错话。靛蓝的 `box note` 是**范围** —— 划定讨论边界、声明去标识化，属于 housekeeping，不是内容（上面那节末尾就有一个）。琥珀色的 `box finding` 是**缺陷** —— 你踩到了什么、什么条件下会踩到：

<div class="box finding"><span class="t">别直接改模板</span><p><code>templates/new-note.md</code> 是所有新笔记的共同来源，改它等于改以后每一篇。要在某一篇里临时调样式也不行 —— 那会让这一页和其余各页分叉。样式只改 <code>src/styles/note.css</code> 一处。</p></div>

收口的是祖母绿的 `box takeaway`，一节最多一个：

<div class="box takeaway"><span class="t">本章结论</span><p>选框就是选语气：<b>靛蓝 = 先划范围，琥珀 = 有坑，祖母绿 = 结论</b>。三种都不是装饰，用错会直接误导读者。</p></div>

<h3>2.3 表格与判定标签</h3>

表格的顶线、表头底线、末行线都是祖母绿 —— 因为表格承载的是**数据**，它是证据。表头的淡祖母绿底同理。判定列用 pill：<span class="pill ok">通过</span> / <span class="pill cav">视情况</span> / <span class="pill bad">不要用</span>，语义与全站一致：祖母绿可以、琥珀有条件、红不行。

给第一列留足宽度。Markdown 表格不会自动分配列宽，内容一长就会断词折行 —— 上面那张表如果第一列写成完整路径，会折成两行，第二行只剩一个词。

<h3>2.4 代码块</h3>

SAS 和 shell 都不在语法高亮器的语言表里，所以**不要用三个反引号的围栏** —— 那样只会得到一片单色。手写 <code>&lt;pre&gt;&lt;code&gt;</code>，用三个类上色：<code>cm</code> 注释（灰）、<code>kw</code> 关键字（靛蓝）、<code>mk</code> 字面量（琥珀）。代码块的左侧竖线是靛蓝的，因为它是结构，不是内容。

<pre><code><span class="cm"># 1. 生成骨架，日期自动填今天</span>
npm run <span class="kw">new</span> my-note-slug

<span class="cm"># 2. 本地看效果，边改边刷</span>
npm run <span class="kw">dev</span>

<span class="cm"># 3. 发布</span>
git add -A &amp;&amp; git commit -m <span class="mk">"Add a note"</span> &amp;&amp; git push</code></pre>

<h3>2.5 插图</h3>

插图是手写的内联 SVG，必须给 <code>viewBox</code> 与 <code>role</code> / <code>aria-label</code>；内部的 <code>fill</code> 与 <code>stroke</code> **每一个都要显式写** —— 样式表不负责 SVG 内部。配色继续分工：画结构用靛蓝，画证据与结论用祖母绿。

<figure>
  <svg viewBox="0 0 680 344" role="img" aria-label="页面部件地图：左列是一次页面自上而下的形状，右列标出部件名。靛蓝的部件是结构与导航，祖母绿的是证据与结论。">
    <rect x="20" y="12" width="280" height="320" fill="#ffffff" stroke="#d8dde3"/>
    <rect x="40" y="30" width="64" height="7" fill="#1b4f8a"/>
    <rect x="40" y="48" width="200" height="9" fill="#17181a"/>
    <rect x="40" y="66" width="236" height="5" fill="#c9ced4"/>
    <rect x="40" y="77" width="196" height="5" fill="#c9ced4"/>
    <rect x="40" y="94" width="48" height="12" rx="6" fill="#eaf3ef" stroke="#0f7b5f"/>
    <rect x="94" y="94" width="52" height="12" rx="6" fill="#eaf3ef" stroke="#0f7b5f"/>
    <rect x="40" y="116" width="120" height="2" fill="#1b4f8a"/>
    <rect x="160" y="116" width="116" height="2" fill="#0f7b5f"/>
    <rect x="40" y="130" width="34" height="10" rx="2" fill="#eaf3ef" stroke="#0f7b5f"/>
    <rect x="80" y="133" width="150" height="5" fill="#c9ced4"/>
    <rect x="40" y="158" width="12" height="12" fill="#1b4f8a"/>
    <rect x="58" y="161" width="150" height="7" fill="#17181a"/>
    <rect x="40" y="180" width="240" height="1" fill="#e3e7eb"/>
    <rect x="40" y="192" width="240" height="5" fill="#c9ced4"/>
    <rect x="40" y="203" width="212" height="5" fill="#c9ced4"/>
    <rect x="40" y="220" width="240" height="30" fill="#f0f7f4" stroke="#dbe9e3"/>
    <rect x="40" y="220" width="3" height="30" fill="#0f7b5f"/>
    <rect x="52" y="228" width="112" height="5" fill="#9cc0b2"/>
    <rect x="52" y="238" width="168" height="5" fill="#c9ced4"/>
    <rect x="40" y="266" width="240" height="2" fill="#0f7b5f"/>
    <rect x="40" y="268" width="240" height="12" fill="#eaf3ef"/>
    <rect x="40" y="280" width="240" height="1" fill="#cfd6dc"/>
    <rect x="52" y="290" width="140" height="4" fill="#c9ced4"/>
    <rect x="40" y="310" width="240" height="2" fill="#0f7b5f"/>
    <rect x="40" y="324" width="240" height="2" fill="#0f7b5f"/>
    <path d="M302 33 H326" stroke="#d8dde3" stroke-width="1" fill="none"/>
    <path d="M302 53 H326" stroke="#d8dde3" stroke-width="1" fill="none"/>
    <path d="M302 79 H326" stroke="#d8dde3" stroke-width="1" fill="none"/>
    <path d="M302 100 H326" stroke="#d8dde3" stroke-width="1" fill="none"/>
    <path d="M302 117 H326" stroke="#d8dde3" stroke-width="1" fill="none"/>
    <path d="M302 135 H326" stroke="#d8dde3" stroke-width="1" fill="none"/>
    <path d="M302 164 H326" stroke="#d8dde3" stroke-width="1" fill="none"/>
    <path d="M302 235 H326" stroke="#d8dde3" stroke-width="1" fill="none"/>
    <path d="M302 276 H326" stroke="#d8dde3" stroke-width="1" fill="none"/>
    <path d="M302 325 H326" stroke="#d8dde3" stroke-width="1" fill="none"/>
    <text x="332" y="37" font-size="11" fill="#1b4f8a">category — 分类行</text>
    <text x="332" y="57" font-size="11" fill="#17181a">title — 页头大标题</text>
    <text x="332" y="83" font-size="11" fill="#6b7280">summary — 摘要</text>
    <text x="332" y="104" font-size="11" fill="#0f7b5f">tags / date — 元数据标签</text>
    <text x="332" y="121" font-size="11" fill="#6b7280">页头分隔线：左靛蓝 右祖母绿</text>
    <text x="332" y="139" font-size="11" fill="#0f7b5f">meta-row — 出处与状态</text>
    <text x="332" y="168" font-size="11" fill="#1b4f8a">h2 与靛蓝序号</text>
    <text x="332" y="199" font-size="11" fill="#6b7280">lede 导语与正文段落</text>
    <text x="332" y="239" font-size="11" fill="#0f7b5f">box — 三种语气</text>
    <text x="332" y="280" font-size="11" fill="#0f7b5f">表格 — 三条祖母绿线</text>
    <text x="332" y="329" font-size="11" fill="#0f7b5f">footer — 收口线</text>
  </svg>
  <figcaption><b>图 1 |</b> 一篇笔记的部件地图。左列是页面自上而下的形状，右列是部件名。靛蓝的部件是结构与导航，祖母绿的是证据与结论 —— 两者唯一的交汇处是页头那条分隔线。</figcaption>
</figure>

<h3>2.6 目录与页脚</h3>

左侧抽屉不用维护 —— 页面打开时从正文的 h2 与 h3 现场生成，标题改了就跟着改。页脚则要自己写，它上方那条 2px 祖母绿收口线会自动出现。

<footer>
  <p><strong>验证说明</strong> 本文列出的每个部件都在站点构建产物中实际渲染过。页头字段与 <code>src/content.config.ts</code> 的 schema 一致，配色与间距取自 <code>src/styles/note.css</code>。</p>
  <p><strong>对照来源</strong> 部件清单与 <code>templates/new-note.md</code> 同步维护 —— 模板是风格的唯一来源，要加部件就改模板，不要改单篇笔记。</p>
</footer>
