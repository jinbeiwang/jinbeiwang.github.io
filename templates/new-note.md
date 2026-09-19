---
title: 笔记标题写在这里
summary: 一句话摘要，显示在首页条目下方。写清这篇解决什么问题、读完能拿走什么。
date: __DATE__
category: SAS patterns
tags: [SAS, 临床编程]
lang: zh
---

<!-- ===========================================================================
     这是笔记模板。不要直接改这个文件 —— 用 `npm run new <slug>` 复制一份到
     src/content/notes/ 再改。下面每段都标了它是什么，删掉注释即可。

     记住三条规矩：
       1. 不写标题行、不写副标题、不写 CSS。页头（分类行 / 标题 / 摘要 / 日期 /
          标签）由 frontmatter 自动生成，版式全由 note.css 决定。
       2. 二级标题就是章节。序号要靛蓝色就写 <span class="n">1</span>，不写也行。
       3. 目录不用维护 —— 页面打开时从 h2/h3 生成。
     =========================================================================== -->


<!-- 出处与状态条（可选）。每个 <span> 是一组「标签 + 值」，标签是祖母绿。 -->
<div class="meta-row">
    <span><b>来源</b> &nbsp;写依据：官方文档 / 会议论文 / 实测；注明有没有真实数据</span>
    <span><b>状态</b> &nbsp;静态分析 / 已执行 / 部分验证</span>
</div>


<h2><span class="n">1</span>这一节要解决的问题</h2>

<!-- 紧跟 h2 的导语。自动带一条软分隔线，用来一句话说清这节的意图。 -->
<p class="lede">先说清要解决什么，再说数据结构；这两件事清楚了，后面的语法只是翻译工作。</p>

正文从这里开始。引进一个说法时把出处标在句末：引用官方文档用 <em class="ev">[doc]</em>，引用会议论文用 <em class="ev">[lit]</em>，属于工程判断、你也没跑过就用 <em class="ev">[实践]</em>。三个就够了，不要再发明新的。

<!-- 说明框（靛蓝）：范围划定、约定、去标识化声明这类 housekeeping 放这里。 -->
<div class="box note"><span class="t">范围</span><p>本文代码取自去标识化后的项目，研究编号、库名与程序头均已替换为占位符。</p></div>

<h3>一个三级标题</h3>

三级标题不需要装饰 —— 层级由字号与留白区分；哪一节在哪里，交给左侧目录抽屉。

- 列表的项目符号是祖母绿圆点，不需要手工加
- 需要读者带走的结论，放进结论框，不要用加粗硬顶

<!-- 表格：表头上方 2px、下方 1px、末行 2px 都是祖母绿，表头带淡祖母绿底。
     「判定」列用 pill：ok 祖母绿 / cav 琥珀 / bad 红。 -->
| 数据形态 | 结论 | 判定 |
|---|---|---|
| 主表远小于查找表 | 一次读进内存最划算 | <span class="pill ok">推荐</span> |
| 两边都很大且已排序 | merge 更省内存 | <span class="pill cav">视情况</span> |
| 需要保留输入顺序 | hash 不保证输出顺序 | <span class="pill bad">不要用</span> |

<!-- 风险框（琥珀）：写症状 + 触发条件，标题里带上症状。 -->
<div class="box finding"><span class="t">风险 1 —— 重复键被静默丢弃</span><p>写清什么情况下会踩到，以及它是报错还是悄悄出错。</p></div>

<!-- 结论框（祖母绿）：每节收口的那一句，一节最多一个。 -->
<div class="box takeaway"><span class="t">本章结论</span><p>一句话说清读者应该记住什么。</p></div>


<h2><span class="n">2</span>代码与实现</h2>

<!-- 代码块。SAS 不在 Shiki 支持的语言里，所以不要用 ``` 围栏 —— 它只会变成
     一片单色。用 <pre><code> 手写，并用三个类上色：
       .cm 注释（灰）  .kw 关键字（深蓝）  .mk 字面量/选项值（琥珀）
     代码里的 < > & 必须写成 &lt; &gt; &amp;。 -->
<pre><code><span class="cm">/* (1) 一步到位：主表每行各自去钉 */</span>
<span class="kw">data</span> want;
  <span class="kw">if</span> _n_ = 1 <span class="kw">then do</span>;
    <span class="kw">declare hash</span> h(<span class="mk">dataset</span>:<span class="mk">'work.lookup'</span>);
    h.<span class="kw">definekey</span>(<span class="mk">'subjid'</span>);
    h.<span class="kw">definedata</span>(<span class="mk">'arm'</span>);
    h.<span class="kw">definedone</span>();
  <span class="kw">end</span>;
  rc = h.<span class="kw">find</span>();
<span class="kw">run</span>;</code></pre>

<!-- 插图：内联 SVG，必须给 viewBox 与 role/aria-label，每个图形的 fill / stroke
     都要显式写（样式表不管 SVG 内部）。配色继续分工：表现结构用靛蓝 #1b4f8a，
     表现实测结果用祖母绿 #0f7b5f。 -->
<figure>
  <svg viewBox="0 0 680 120" role="img" aria-label="把查找表读进内存，主表逐行查找">
    <rect x="10" y="20" width="180" height="60" fill="#eef3f8" stroke="#1b4f8a" stroke-width="1.5" rx="3"/>
    <text x="100" y="55" font-size="13" fill="#1b4f8a" text-anchor="middle">lookup 表</text>
    <path d="M200 50 H300" stroke="#1b4f8a" stroke-width="1.5" fill="none" marker-end="url(#a)"/>
    <rect x="310" y="20" width="180" height="60" fill="#f0f7f4" stroke="#0f7b5f" stroke-width="1.5" rx="3"/>
    <text x="400" y="55" font-size="13" fill="#0f7b5f" text-anchor="middle">hash 对象</text>
    <defs><marker id="a" markerWidth="8" markerHeight="8" refX="6" refY="4" orient="auto">
      <path d="M0 0 L8 4 L0 8 z" fill="#1b4f8a"/></marker></defs>
  </svg>
  <figcaption><b>图 1 |</b> 图号「图 1 |」是祖母绿，正文说明用次级灰。每张图都要有说明。</figcaption>
</figure>


<h2><span class="n">3</span>复用清单</h2>

留在最后一节：搬进别的程序之前要改什么、要检查什么。

<!-- 笔记自己的结尾。上面这条 2px 祖母绿线自动出现。 -->
<footer>
  <p><strong>验证说明</strong> 这篇是怎么核对的：跑过什么、没跑什么，依据哪份文档的哪一节。</p>
  <p><strong>去标识化</strong> 研究编号、库名、程序头均已移除或替换为占位符。</p>
</footer>
