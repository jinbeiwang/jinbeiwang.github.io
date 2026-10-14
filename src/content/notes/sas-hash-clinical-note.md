---
title: "SAS Hash 对象的系统化用法：定义、键值查找、数据装载与输出"
summary: "全文已迁回 sas-pattern-notes 仓库——一篇笔记只在一处维护。本页保留原地址，读它就是读那一篇。"
date: 2026-09-19
category: SAS patterns
tags: [SAS, Hash, 临床编程, SDTM/ADaM]
lang: zh
---

<div class="meta-row">
    <span><b>迁出</b> &nbsp;2026-10-14 —— 正文移入 <code>sas-pattern-notes</code> 仓库</span>
    <span><b>本页保留</b> &nbsp;原地址，使已发布的链接继续可用</span>
</div>

<div class="box takeaway">
  <span class="t">去哪里读</span>
  <p>全文在
  <a href="https://jinbeiwang.github.io/sas-pattern-notes/sas-hash-clinical-note.html">jinbeiwang.github.io/sas-pattern-notes/sas-hash-clinical-note.html</a>
  &mdash; 同一篇文字，中文，五段代码、七张表、两张图与十三处出处标记都在。</p>
</div>

<h2><span class="n">1</span>为什么只留一个指路页</h2>
<p class="lede">同一条规矩，这个站已经用过一次，只是方向相反。</p>

<p>《Chained kit replacement》当初从子站退休进来，是因为一篇笔记同时在两个仓库维护，改一处漏一处。
这次反过来：hash 这篇的正文退回子站，本页只留地址。两次动作是同一条规矩&mdash;&mdash;<strong>一篇笔记只在一处维护</strong>，
而被留下的那一处，就是拿到后续修改的地方。</p>

<p>迁移时顺手把子站那份补齐了。它写在 2026-09-19 凌晨，还是第一代单色相版式：没有第二色相，也没有
<code>em.ev</code> 的出处标记；而这一份当晚重排时已经改过。所以做法是把这份较新的正文重新过一遍
<code>sas-pattern-note</code> 当前的骨架，落回子站，再退休本页的正文。<strong>读者看到的文字一个字没变</strong>
&mdash;&mdash; 变的只是那十三处出处标记从此有了样式。</p>

<h2><span class="n">2</span>全文还取得回来吗</h2>
<p class="lede">能，而且随时可以核。</p>

<p>本页的正文删于 2026-10-14，全文留在版本历史里，按提交号取回即可：</p>

<pre><code>git show <span class="mk">bf025f3</span>:src/content/notes/sas-hash-clinical-note.md</code></pre>

<p>迁移前后做过逐字核对：新旧两版从页头到页脚的<b>可见文字完全相同</b>（各 12,530 字），因此"文字没变"这句话
是可验证的，不是印象 <em class="ev">[实践]</em>。</p>

<footer>
  <p><strong>这一页是指路页</strong> 正文不在本仓库；本页既没有代码也没有数据，因此没有任何可复核的运行结果。</p>
  <p><strong>去标识化</strong> 原笔记的说明照旧适用，见子站那份全文的页头与页脚。</p>
</footer>
