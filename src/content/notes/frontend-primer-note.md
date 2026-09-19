---
title: "前端入门：从浏览器渲染到可交付页面"
summary: "把前端拆成「结构 — 表现 — 行为 — 运行环境 — 数据通路 — 工程交付」六层，逐层给出核心概念、术语、 最小示例与验收标准，并配知识结构图与流程图。写作语境按读者现有的 R / Python / SAS 心智模型来搭桥， 终点是能独立做出一个可用的页面并放到网上。"
date: 2026-09-19
category: Languages and practice
tags: [前端, JavaScript, HTML, 学习路径]
lang: zh
---

<div class="meta-row">
    <span><b>读者</b> &nbsp;零基础起步，现有主力语言为 R / Python / SAS</span>
    <span><b>目标</b> &nbsp;能独立完成一个响应式页面并部署</span>
    <span><b>版本基准</b> &nbsp;MDN 与 WHATWG / ECMAScript 现行文档；Node v22.22.2 实测（2026-09）</span>
  </div>


<div class="box note" style="margin-top:26px;">
  <span class="t">阅读约定与证据边界</span>
  <div class="small">
  <p><b>三类断言，分开标注。</b>凡写「<b>规范</b>」，指的是现行标准或官方文档已经规定、可查附录 B 原文的行为；
  凡写「<b>实测</b>」，指的是本机 Node v22.22.2 上跑出来的结果，原始输出见 §5.10；凡写「<b>惯例</b>」，
  指的是工程界的取舍而非事实，可以被合理反对。三者混在一起读，最容易把「大家都这么写」当成「必须这么写」。</p>
  <p><b>这篇笔记不覆盖什么。</b>只到「能独立做出页面」为止的地平线：框架只给判断标准，不给 API 细节；
  不涉及构建工具的插件体系、微前端、SSR 等服务端渲染话题；代码是最小可运行片段，不是完整项目骨架。</p>
  <p><b>没有在本机复现的部分。</b>CSS 布局、浏览器渲染与网络行为均按规范文档陈述，未在本机浏览器中逐步复现；
  本文所有「实测」结论仅来自 Node 的 JavaScript 引擎，不包含任何 DOM 或渲染结论。</p>
  </div>
</div>

<!-- ============================================================ -->
<h2><span class="n">1</span>前端是什么：三个职责层，一个运行环境</h2>
<p class="lede">先把「前端」这个词拆干净，否则后面每一层都会含糊。</p>

<p>前端不是一个技术，而是<b>三种职责在同一份交付物里的分工</b>：HTML 说明有什么内容，
CSS 说明这些内容长什么样、怎么排，JavaScript 说明用户动了之后发生什么。三者由浏览器统一解释执行。
判断一段代码属于前端还是后端，标准只有一条 —— <b>它在哪里执行</b>。在用户的浏览器里执行的，就是前端。</p>

<h3>1.1 三个层各自回答什么问题</h3>

<table>
  <thead><tr><th style="width:104px;">层</th><th style="width:168px;">回答的问题</th><th>用你已有的工具打比方</th></tr></thead>
  <tbody>
    <tr><td><b>HTML</b></td><td>有哪些内容，各是什么</td><td>类似数据集的结构定义：哪一列是标识、哪一列是测量值、哪一列是分组标签。声明事实，不做计算。</td></tr>
    <tr><td><b>CSS</b></td><td>长什么样，怎么排</td><td>类似绘图参数与主题：字体、颜色、坐标轴、面板间距。只影响呈现，不影响内容本身。</td></tr>
    <tr><td><b>JavaScript</b></td><td>发生什么动作</td><td>类似 DATA step 或脚本逻辑：判断、循环、变换数据、响应输入。它也是三层里唯一能做运算的。</td></tr>
  </tbody>
</table>

<div class="box">
  <span class="t">这是一个可以检验的理解</span>
  <p>如果去掉 JavaScript，页面依然能显示，只是不能交互 —— 这正说明 HTML 与 CSS 的职责是<b>呈现</b>而不是<b>行为</b>。
  反过来，一份只有 JavaScript 而内容由它临时拼出来的页面，在脚本报错时会变成白屏。这就是为什么后面反复强调：
  <b>内容优先用 HTML 写出来，JavaScript 只做增强</b>。</p>
</div>

<h3>1.2 代码在哪里运行：浏览器与服务器</h3>

<figure>
<svg viewBox="0 0 680 214" role="img" aria-label="浏览器的三层职责与服务器侧的分工示意图">
  <g font-family="-apple-system,BlinkMacSystemFont,'Segoe UI','PingFang SC','Microsoft YaHei',Helvetica,Arial,sans-serif">
    <rect x="16" y="24" width="396" height="158" rx="6" fill="#ffffff" stroke="#c9d2dc"/>
    <text x="34" y="46" font-size="12.5" font-weight="700" fill="#17181a">浏览器（用户的设备）</text>
    <rect x="34" y="58" width="360" height="34" rx="4" fill="#f7f8f9" stroke="#dfe5ea"/>
    <rect x="34" y="58" width="3" height="34" fill="#1b4f8a"/>
    <text x="50" y="79" font-size="11.5" font-weight="700" fill="#17181a">HTML</text>
    <text x="102" y="79" font-size="11" fill="#5b6570">结构 —— 有哪些内容，各是什么</text>
    <rect x="34" y="100" width="360" height="34" rx="4" fill="#f7f8f9" stroke="#dfe5ea"/>
    <rect x="34" y="100" width="3" height="34" fill="#1b4f8a"/>
    <text x="50" y="121" font-size="11.5" font-weight="700" fill="#17181a">CSS</text>
    <text x="102" y="121" font-size="11" fill="#5b6570">表现 —— 长什么样，怎么排列</text>
    <rect x="34" y="142" width="360" height="34" rx="4" fill="#f7f8f9" stroke="#dfe5ea"/>
    <rect x="34" y="142" width="3" height="34" fill="#1b4f8a"/>
    <text x="50" y="163" font-size="11.5" font-weight="700" fill="#17181a">JavaScript</text>
    <text x="120" y="163" font-size="11" fill="#5b6570">行为 —— 用户动了以后发生什么</text>
    <line x1="412" y1="103" x2="442" y2="103" stroke="#1b4f8a" stroke-width="1.4"/>
    <polygon points="450,103 442,99.5 442,106.5" fill="#1b4f8a"/>
    <text x="414" y="86" font-size="10" fill="#1b4f8a">请求</text>
    <text x="414" y="128" font-size="10" fill="#8b949e">响应</text>
    <rect x="454" y="24" width="210" height="158" rx="6" fill="#eef3f8" stroke="#1b4f8a"/>
    <text x="472" y="46" font-size="12.5" font-weight="700" fill="#1b4f8a">服务器</text>
    <text x="472" y="72" font-size="11" fill="#17181a">API 接口</text>
    <text x="472" y="94" font-size="11" fill="#17181a">数据库 / 文件</text>
    <text x="472" y="116" font-size="11" fill="#17181a">权限与业务规则</text>
    <text x="472" y="148" font-size="10.5" fill="#5b6570">这里的代码用什么语言写，</text>
    <text x="472" y="164" font-size="10.5" fill="#5b6570">前端原则上不关心。</text>
    <text x="16" y="204" font-size="10.5" fill="#8b949e">前端 = 在浏览器里执行的那部分；后端 = 在服务器上执行的那部分。边界由「谁执行」决定，不由文件后缀决定。</text>
  </g>
</svg>
<figcaption><b>图 1 |</b> 三层职责都发生在浏览器一侧，服务器只负责给数据和规则。理解这一点的实际价值在于：
当页面「没反应」时，第一步永远是判断问题出在浏览器侧还是服务器侧 —— 打开开发者工具的网络面板，看请求有没有发出去。</figcaption>
</figure>

<h3>1.3 从 R / Python / SAS 迁移过来，心智模型要改哪几处</h3>

<p>语言语法是可以现查的，真正会持续误导你的是<b>执行模型</b>。下表左列是你在 R / Python / SAS 里已经形成的直觉，
右列是前端世界里对应的事实。这张表是整个入门阶段最值得反复回看的一页。</p>

<table>
  <thead><tr><th style="width:132px;">维度</th><th style="width:250px;">R / Python / SAS 的直觉</th><th>JavaScript / 前端的实际情况</th></tr></thead>
  <tbody>
    <tr>
      <td><b>生命周期</b></td>
      <td>脚本从头跑到尾，跑完进程退出</td>
      <td><span class="pill cav">差异最大</span> 页面在标签页里长期驻留。代码写完只是「注册」了行为，真正执行取决于用户点没点、网络通没通。</td>
    </tr>
    <tr>
      <td><b>控制流</b></td>
      <td>顺序执行，你用循环决定下一步</td>
      <td>事件驱动：注册回调函数，交给浏览器在合适时机调用。<code>for</code> 循环仍然存在，但主结构是「有人触发 → 我的函数被调用」。</td>
    </tr>
    <tr>
      <td><b>数值类型</b></td>
      <td>R 区分 integer / double，SAS 区分数值与字符</td>
      <td>只有一种数值类型 <code>number</code>（IEEE-754 双精度）；没有整型，因此 <code>1/3</code> 与精度问题需要主动处理（见 §5.3）。</td>
    </tr>
    <tr>
      <td><b>类型宽松度</b></td>
      <td>把字符当数值用通常直接报错</td>
      <td><code>'3' * 2</code> 得到 <code>6</code>，<code>'1' + 1</code> 得到 <code>'11'</code>。同一套运算符有时转数字、有时拼字符串，是初学者 bug 的头号来源。<span class="pill cav">实测</span></td>
    </tr>
    <tr>
      <td><b>相等判断</b></td>
      <td><code>==</code> 基本就是值相等</td>
      <td><code>==</code> 会先做类型转换，<code>===</code> 才要求类型和值都相同。工程惯例是<b>只用 <code>===</code></b>，见 §5.2。</td>
    </tr>
    <tr>
      <td><b>缺失值</b></td>
      <td><code>NA</code> / <code>NaN</code> / SAS 的 <code>.</code>，语义明确</td>
      <td>有 <code>undefined</code> 与 <code>null</code> 两个，且 <code>undefined == null</code> 为真。好消息是 <code>NaN !== NaN</code> 与 R 一致。<span class="pill ok">直觉可迁移</span></td>
    </tr>
    <tr>
      <td><b>向量化</b></td>
      <td>R 的向量、pandas 的列运算、SAS 隐式逐行</td>
      <td><b>没有向量化</b>。数组运算要么手写 <code>map</code> / <code>filter</code> / <code>reduce</code>，要么靠库。这是从数据语言转过来最需要补的一块，见 §5.6。</td>
    </tr>
    <tr>
      <td><b>集合类型</b></td>
      <td><code>data.frame</code> / DataFrame / 数据集</td>
      <td>没有表格类型。数据是一维数组（array）加键值对象（object）拼出来的，表格要靠库或自己约定结构。</td>
    </tr>
    <tr>
      <td><b>依赖管理</b></td>
      <td><code>install.packages()</code> / <code>pip</code> / SAS autocall 宏</td>
      <td>用 npm 装包，但<b>依赖不会自动到达浏览器</b> —— 需要一步「打包」把依赖合进交付文件。这是工程化存在的根本原因（§8）。</td>
    </tr>
    <tr>
      <td><b>错误可见性</b></td>
      <td>报错即停，日志里能看到</td>
      <td>错误可能只让某一个交互失效，页面其余部分照常工作。静默失败是常态，所以必须主动打开控制台看报错。</td>
    </tr>
  </tbody>
</table>

<h3>1.4 最小可运行页面</h3>

<p>环境只有一个要求：一个能保存文件的编辑器，加一个现代浏览器。下面这个文件保存为 <code>index.html</code>，
双击就能在浏览器里打开 —— 不需要安装任何东西，这本身就是前端入门最大的优势。</p>

<pre><code><span class="cm">&lt;!-- (1) 文档类型与语言：告诉浏览器用标准模式解析 --&gt;</span>
<span class="kw">&lt;!DOCTYPE html&gt;</span>
<span class="kw">&lt;html</span> lang=<span class="mk">"zh-CN"</span><span class="kw">&gt;</span>
<span class="kw">&lt;head&gt;</span>
  <span class="cm">&lt;!-- (2) 这两行是所有页面都必须有的：字符集与视口 --&gt;</span>
  <span class="kw">&lt;meta</span> charset=<span class="mk">"UTF-8"</span><span class="kw">&gt;</span>
  <span class="kw">&lt;meta</span> name=<span class="mk">"viewport"</span> content=<span class="mk">"width=device-width, initial-scale=1"</span><span class="kw">&gt;</span>
  <span class="kw">&lt;title&gt;</span>队列基线特征<span class="kw">&lt;/title&gt;</span>
<span class="kw">&lt;/head&gt;</span>
<span class="kw">&lt;body&gt;</span>
  <span class="cm">&lt;!-- (3) 内容用语义标签写出来，而不是一堆 div --&gt;</span>
  <span class="kw">&lt;h1&gt;</span>队列基线特征<span class="kw">&lt;/h1&gt;</span>
  <span class="kw">&lt;p&gt;</span>共入组 <span class="kw">&lt;strong&gt;</span>128<span class="kw">&lt;/strong&gt;</span> 例。详见下表。<span class="kw">&lt;/p&gt;</span>
  <span class="kw">&lt;table&gt;</span>
    <span class="kw">&lt;thead&gt;&lt;tr&gt;&lt;th&gt;</span>变量<span class="kw">&lt;/th&gt;&lt;th&gt;</span>均值（标准差）<span class="kw">&lt;/th&gt;&lt;/tr&gt;&lt;/thead&gt;</span>
    <span class="kw">&lt;tbody&gt;</span>
      <span class="kw">&lt;tr&gt;&lt;td&gt;</span>年龄<span class="kw">&lt;/td&gt;&lt;td&gt;</span>57.3 (11.4)<span class="kw">&lt;/td&gt;&lt;/tr&gt;</span>
      <span class="kw">&lt;tr&gt;&lt;td&gt;</span>体质指数<span class="kw">&lt;/td&gt;&lt;td&gt;</span>24.8 (3.1)<span class="kw">&lt;/td&gt;&lt;/tr&gt;</span>
    <span class="kw">&lt;/tbody&gt;</span>
  <span class="kw">&lt;/table&gt;</span>
<span class="kw">&lt;/body&gt;</span>
<span class="kw">&lt;/html&gt;</span></code></pre>

<p>注意最后那段：<code>&lt;table&gt;</code> 不是为了好看才写的，它是<b>语义</b>。浏览器、屏幕阅读器、搜索引擎都靠它理解
「这一行是数据，那一格是表头」。如果你用一堆 <code>div</code> 加边框视觉上拼出一张表，人看着一样，机器看着就是一堆散装文字。</p>

<!-- ============================================================ -->
<h2><span class="n">2</span>知识体系总览</h2>
<p class="lede">先看地图，再走路线。六条主干之间是有依赖顺序的，跳着学会反复返工。</p>

<figure>
<svg viewBox="0 0 680 400" role="img" aria-label="前端知识体系总览思维导图：中心为前端，六条主干分别指向 HTML、CSS、JavaScript、运行环境、数据通路、工程与交付">
  <g font-family="-apple-system,BlinkMacSystemFont,'Segoe UI','PingFang SC','Microsoft YaHei',Helvetica,Arial,sans-serif">
    <polyline points="290,199 265,199 265,52 248,52" fill="none" stroke="#c9d2dc" stroke-width="1.2"/>
    <line x1="290" y1="199" x2="248" y2="199" stroke="#c9d2dc" stroke-width="1.2"/>
    <polyline points="290,199 265,199 265,348 248,348" fill="none" stroke="#c9d2dc" stroke-width="1.2"/>
    <polyline points="390,199 415,199 415,52 432,52" fill="none" stroke="#c9d2dc" stroke-width="1.2"/>
    <line x1="390" y1="199" x2="432" y2="199" stroke="#c9d2dc" stroke-width="1.2"/>
    <polyline points="390,199 415,199 415,348 432,348" fill="none" stroke="#c9d2dc" stroke-width="1.2"/>
    <rect x="16" y="22" width="232" height="60" rx="5" fill="#ffffff" stroke="#c9d2dc"/>
    <text x="32" y="44" font-size="12" font-weight="700" fill="#17181a">HTML · 结构</text>
    <text x="32" y="63" font-size="10.5" fill="#5b6570">文档骨架 / 语义 / 表单</text>
    <rect x="16" y="170" width="232" height="60" rx="5" fill="#ffffff" stroke="#c9d2dc"/>
    <text x="32" y="192" font-size="12" font-weight="700" fill="#17181a">CSS · 表现</text>
    <text x="32" y="211" font-size="10.5" fill="#5b6570">盒模型 / 层叠 / Flex / Grid</text>
    <rect x="16" y="318" width="232" height="60" rx="5" fill="#ffffff" stroke="#c9d2dc"/>
    <text x="32" y="340" font-size="12" font-weight="700" fill="#17181a">JavaScript · 行为</text>
    <text x="32" y="359" font-size="10.5" fill="#5b6570">类型 / 闭包 / 数组 / 异步 / DOM</text>
    <rect x="432" y="22" width="232" height="60" rx="5" fill="#ffffff" stroke="#c9d2dc"/>
    <text x="448" y="44" font-size="12" font-weight="700" fill="#17181a">运行环境 · 浏览器</text>
    <text x="448" y="63" font-size="10.5" fill="#5b6570">渲染路径 / 重排重绘 / DevTools</text>
    <rect x="432" y="170" width="232" height="60" rx="5" fill="#ffffff" stroke="#c9d2dc"/>
    <text x="448" y="192" font-size="12" font-weight="700" fill="#17181a">数据通路 · 网络</text>
    <text x="448" y="211" font-size="10.5" fill="#5b6570">HTTP / fetch / JSON / CORS</text>
    <rect x="432" y="318" width="232" height="60" rx="5" fill="#ffffff" stroke="#c9d2dc"/>
    <text x="448" y="340" font-size="12" font-weight="700" fill="#17181a">工程与交付</text>
    <text x="448" y="359" font-size="10.5" fill="#5b6570">npm / 构建 / 部署 / 框架</text>
    <rect x="290" y="176" width="100" height="46" rx="6" fill="#1b4f8a" stroke="#1b4f8a"/>
    <text x="340" y="204" text-anchor="middle" font-size="14" font-weight="700" fill="#ffffff">前端</text>
    <text x="16" y="394" font-size="10.5" fill="#8b949e">六条主干中，左边三条是可以立刻动手的；右上两条决定你为什么「本地能跑、线上报错」；右下一条决定交付形态。</text>
  </g>
</svg>
<figcaption><b>图 2 |</b> 知识体系总览。中心是交付物本身，六条主干是你会反复回访的六个方向。用途不是背下来，
而是当你卡住时能定位「我卡在哪一支上」—— 多数新手问题都能归到图里某一格。</figcaption>
</figure>

<h3>2.1 六条主干的分工</h3>

<table>
  <thead><tr><th style="width:120px;">主干</th><th>解决什么</th><th style="width:150px;">入门阶段要投入多少</th></tr></thead>
  <tbody>
    <tr><td><b>HTML · 结构</b></td><td>把内容正确、完整地表达出来，让机器也能读懂</td><td><span class="pill ok">重点</span> 一两天可掌握常用部分</td></tr>
    <tr><td><b>CSS · 表现</b></td><td>布局与外观，决定页面能不能用、好不好看</td><td><span class="pill ok">重点</span> 前两周最花时间的一支</td></tr>
    <tr><td><b>JavaScript · 行为</b></td><td>交互与数据处理，唯一能做运算的一层</td><td><span class="pill ok">重点</span> 长期投入，占学习时间的一半</td></tr>
    <tr><td><b>运行环境 · 浏览器</b></td><td>解释「为什么代码这么写才会快、才会对」</td><td><span class="pill cav">按需</span> 先会看控制台与网络面板即可</td></tr>
    <tr><td><b>数据通路 · 网络</b></td><td>把数据从服务器取到页面上，以及为什么会被拦</td><td><span class="pill ok">重点</span> 会写一个 fetch 就够起步</td></tr>
    <tr><td><b>工程与交付</b></td><td>依赖、构建、部署 —— 从「我的电脑上」到「网上可用」</td><td><span class="pill cav">按需</span> 做出第一个页面之后再碰</td></tr>
  </tbody>
</table>

<div class="box finding">
  <span class="t">最常见的路线错误：先学框架</span>
  <p>直接上 React 或 Vue，能拼出界面，但一遇到样式不对、接口报错、打包失败就完全无从下手，因为底下三层是空的。
  合理的顺序是<b>先把 HTML 与 CSS 用到能默写出一个页面骨架，再补 JavaScript</b>，框架放到最后 —— 它只是把
  「用 DOM 操作界面」这件事换了一种更省心的写法，前提是你知道原来的写法是什么样。</p>
</div>

<!-- ============================================================ -->
<h2><span class="n">3</span>HTML：结构与语义</h2>
<p class="lede">一层被严重低估的语言。它不难，但写错会让后面两层无处着力。</p>

<p>HTML（HyperText Markup Language）不是编程语言 —— 它没有变量、没有循环、没有判断，只有<b>嵌套的标签</b>。
一个标签声明一段内容「是什么」，浏览器把它解析成一棵<b>盒子树</b>，CSS 与 JavaScript 都在这棵树上工作。
所以 HTML 的质量决定了后两层的工作难度：结构扁平、语义清晰，CSS 选择器就短，JavaScript 的遍历就简单。</p>

<h3>3.1 元素、属性、嵌套</h3>

<table>
  <thead><tr><th style="width:150px;">概念</th><th>含义</th><th style="width:210px;">写法</th></tr></thead>
  <tbody>
    <tr><td><b>元素</b></td><td>一对开始标签与结束标签，加上它们包裹的内容</td><td><code>&lt;p&gt;文字&lt;/p&gt;</code></td></tr>
    <tr><td><b>空元素</b></td><td>没有内容、不需要结束标签的元素</td><td><code>&lt;img src="..." alt="..."&gt;</code></td></tr>
    <tr><td><b>属性</b></td><td>给元素的附加说明，写在开始标签里</td><td><code>&lt;a href="/report"&gt;</code></td></tr>
    <tr><td><b>嵌套</b></td><td>元素可以包含元素，形成树形结构；嵌套必须完整闭合</td><td>树形，越深越难维护</td></tr>
    <tr><td><b>布尔属性</b></td><td>写了就是真，不写就是假，不写值</td><td><code>&lt;input required&gt;</code></td></tr>
  </tbody>
</table>

<p>浏览器对错误的 HTML 极其宽容：少一个闭合标签不会报错，它会猜。这个宽容是双刃剑 ——
页面看起来正常，但 DOM 树可能和你想的不是一回事。养成习惯：随手用开发者工具的「元素」面板看一眼真实结构。</p>

<h3>3.2 语义化：为什么不能全用 div</h3>

<p><code>&lt;div&gt;</code> 是「一个没有含义的容器」。用它可以拼出任何视觉效果，这也是它被滥用的原因。
问题是<b>含义是给机器用的</b>：屏幕阅读器靠它决定怎么朗读，搜索引擎靠它决定哪段是正文，
键盘用户靠它判断能不能跳到主内容区。下表左列能替代的是右侧的 <code>div</code> 写法。</p>

<table>
  <thead><tr><th style="width:150px;">语义标签</th><th style="width:190px;">含义</th><th>替代掉的无含义写法</th></tr></thead>
  <tbody>
    <tr><td><code>&lt;header&gt;</code></td><td>页面或区块的头部</td><td><code>&lt;div class="header"&gt;</code></td></tr>
    <tr><td><code>&lt;nav&gt;</code></td><td>导航链接的集合</td><td><code>&lt;div class="nav"&gt;</code></td></tr>
    <tr><td><code>&lt;main&gt;</code></td><td>本页唯一的主体内容（一页只应有一个）</td><td><code>&lt;div id="content"&gt;</code></td></tr>
    <tr><td><code>&lt;section&gt;</code></td><td>有主题的一节，通常带标题</td><td><code>&lt;div class="sec"&gt;</code></td></tr>
    <tr><td><code>&lt;h1&gt;</code>…<code>&lt;h6&gt;</code></td><td>标题层级，表达从属关系而非字号</td><td><code>&lt;div class="big-bold"&gt;</code></td></tr>
    <tr><td><code>&lt;table&gt;</code> / <code>&lt;th&gt;</code> / <code>&lt;caption&gt;</code></td><td>表格数据、表头单元格、表标题</td><td>用边框拼出来的假表格</td></tr>
    <tr><td><code>&lt;button&gt;</code></td><td>可点击的动作</td><td><code>&lt;div onclick="..."&gt;</code></td></tr>
    <tr><td><code>&lt;label&gt;</code></td><td>表单控件的文字标签</td><td>控件旁边的普通文字</td></tr>
  </tbody>
</table>

<div class="box finding">
  <span class="t">用 div 假装按钮，会坏在三个地方</span>
  <p>把 <code>&lt;div onclick="..."&gt;</code> 当按钮用，视觉上没问题，但：键盘 <kbd>Tab</kbd> 键跳不过去；
  屏幕阅读器不会告诉用户「这是可点击的」；表单里按 <kbd>Enter</kbd> 不会提交。换成 <code>&lt;button&gt;</code>
  这三个问题同时消失，而且不需要写一行额外代码。这就是「语义」的实际收益 —— <b>它是免费的功能，不是洁癖</b>。</p>
</div>

<h3>3.3 表单：把用户的输入送回服务器</h3>

<p>表单是前端唯一一类「原生就能提交数据」的元素。<code>&lt;input&gt;</code> 的 <code>type</code> 属性不只是外观差异，
它决定了浏览器给你什么键盘、做什么校验、提交什么格式。</p>

<table>
  <thead><tr><th style="width:130px;"><code>type</code></th><th>浏览器额外做的事</th></tr></thead>
  <tbody>
    <tr><td><code>text</code></td><td>普通文本；<code>value</code> 永远是字符串，需要自己转数字</td></tr>
    <tr><td><code>number</code></td><td>数字键盘、<code>min</code> / <code>max</code> / <code>step</code> 约束、<code>valueAsNumber</code></td></tr>
    <tr><td><code>date</code></td><td>日期选择器，<code>value</code> 格式固定为 <code>YYYY-MM-DD</code></td></tr>
    <tr><td><code>checkbox</code> / <code>radio</code></td><td>布尔或单选；<code>name</code> 相同的 radio 互斥</td></tr>
    <tr><td><code>file</code></td><td>文件选择器，配合 <code>accept</code> 限制类型，得到 <code>File</code> 对象</td></tr>
  </tbody>
</table>

<p>一个统计场景的表单骨架 —— 用于筛选队列：</p>

<pre><code><span class="kw">&lt;form</span> id=<span class="mk">"filter"</span><span class="kw">&gt;</span>
  <span class="cm">&lt;!-- label 用 for 指向 id，点文字也能聚焦控件；for 与 id 必须严格对应 --&gt;</span>
  <span class="kw">&lt;label</span> for=<span class="mk">"sex"</span><span class="kw">&gt;</span>性别<span class="kw">&lt;/label&gt;</span>
  <span class="kw">&lt;select</span> id=<span class="mk">"sex"</span> name=<span class="mk">"sex"</span><span class="kw">&gt;</span>
    <span class="kw">&lt;option</span> value=<span class="mk">""</span><span class="kw">&gt;</span>全部<span class="kw">&lt;/option&gt;</span>
    <span class="kw">&lt;option</span> value=<span class="mk">"F"</span><span class="kw">&gt;</span>女<span class="kw">&lt;/option&gt;</span>
    <span class="kw">&lt;option</span> value=<span class="mk">"M"</span><span class="kw">&gt;</span>男<span class="kw">&lt;/option&gt;</span>
  <span class="kw">&lt;/select&gt;</span>
  <span class="kw">&lt;label</span> for=<span class="mk">"ageMin"</span><span class="kw">&gt;</span>最小年龄<span class="kw">&lt;/label&gt;</span>
  <span class="kw">&lt;input</span> id=<span class="mk">"ageMin"</span> name=<span class="mk">"ageMin"</span> type=<span class="mk">"number"</span> min=<span class="mk">"18"</span> max=<span class="mk">"100"</span><span class="kw">&gt;</span>
  <span class="cm">&lt;!-- type="submit" 的按钮会触发表单提交这种「原生行为」 --&gt;</span>
  <span class="kw">&lt;button</span> type=<span class="mk">"submit"</span><span class="kw">&gt;</span>应用筛选<span class="kw">&lt;/button&gt;</span>
<span class="kw">&lt;/form&gt;</span></code></pre>

<p>注意 <code>&lt;button&gt;</code> 必须显式写 <code>type</code>。不写时它在表单内的默认值是 <code>submit</code>，
于是「重置」按钮会意外提交整个表单 —— 这是真实项目里反复出现的 bug。</p>

<h3>3.4 无障碍：最小可用集</h3>

<p>无障碍（accessibility，常缩写为 a11y）听起来专业，入门阶段其实只有四条要记。
做对这四条，就能覆盖绝大多数常见问题。</p>

<ol>
  <li><b>图片写 <code>alt</code>。</b>内容图写描述，纯装饰图写 <code>alt=""</code>（空字符串表示「跳过」）。缺失 <code>alt</code> 会让屏幕阅读器读出文件名。</li>
  <li><b>表单控件配 <code>&lt;label&gt;</code>。</b>用 <code>for</code> 与 <code>id</code> 绑定，而不是把文字放在旁边。</li>
  <li><b>该用原生元素就用原生元素。</b>按钮用 <code>&lt;button&gt;</code>，链接用 <code>&lt;a&gt;</code>，别用 <code>div</code> 加事件模拟。</li>
  <li><b>标题层级不跳级。</b>从 <code>h1</code> 到 <code>h3</code> 不能跳过 <code>h2</code>，它表达的是文档大纲，不是字号。</li>
</ol>

<div class="box">
  <span class="t">一条经验判断</span>
  <p>如果你需要给一个元素手工添加 <code>role</code>、<code>tabindex</code> 和键盘事件三样东西才能让它像按钮，
  那说明原生按钮本来就能满足需求。ARIA 属性是补丁，正确用法是「优先用原生元素，只在原生表达不了时才用 ARIA」。</p>
</div>

<!-- ============================================================ -->
<h2><span class="n">4</span>CSS：盒模型、层叠与布局</h2>
<p class="lede">样式表被低估的地方不在于「怎么让它好看」，而在于「为什么我写的这条规则没生效」。</p>

<p>CSS（Cascading Style Sheets，层叠样式表）的全部难点集中在两个字上：<b>层叠</b>。
页面里每个元素最终的样子，是所有匹配到它的规则按优先级与声明顺序「竞争」出来的结果。
所以学 CSS 的顺序应该是：先懂盒模型（一个元素占多大地方），再懂层叠（哪条规则赢），最后才是布局（怎么摆放）。</p>

<h3>4.1 盒模型</h3>

<figure>
<svg viewBox="0 0 680 250" role="img" aria-label="CSS 盒模型示意图：content、padding、border、margin 由内到外四层">
  <g font-family="-apple-system,BlinkMacSystemFont,'Segoe UI','PingFang SC','Microsoft YaHei',Helvetica,Arial,sans-serif">
    <rect x="70" y="26" width="540" height="174" rx="4" fill="#f7f8f9" stroke="#c9d2dc" stroke-dasharray="5 4"/>
    <rect x="104" y="44" width="472" height="138" rx="3" fill="#ffffff" stroke="#17181a" stroke-width="1.6"/>
    <rect x="126" y="62" width="428" height="102" rx="3" fill="#eef3f8" stroke="#1b4f8a"/>
    <rect x="200" y="84" width="280" height="58" rx="3" fill="#ffffff" stroke="#c9d2dc"/>
    <text x="76" y="40" font-size="10.5" fill="#8b949e">margin 外边距</text>
    <text x="110" y="58" font-size="10.5" fill="#17181a">border 边框</text>
    <text x="132" y="78" font-size="10.5" fill="#1b4f8a">padding 内边距</text>
    <text x="340" y="118" text-anchor="middle" font-size="12" font-weight="700" fill="#17181a">content 内容区</text>
    <text x="340" y="136" text-anchor="middle" font-size="10" fill="#8b949e">width / height 默认只指这一层</text>
    <text x="70" y="216" font-size="10.5" fill="#8b949e">默认 <tspan font-weight="700">box-sizing: content-box</tspan>：width 只指 content 那一层。</text>
    <text x="70" y="232" font-size="10.5" fill="#8b949e">所以 200px 的盒子加上 padding 与 border 会明显更宽。统一改 <tspan font-weight="700">border-box</tspan> 可避免。</text>
  </g>
</svg>
<figcaption><b>图 3 |</b> 从内到外四层。新手最常踩的坑是「设了 <code>width: 100%</code> 却还是横向溢出」——
因为还有 padding 与 border 被加在外面。<b>惯例</b>是在样式表开头统一设置 <code>*{box-sizing:border-box}</code>，让宽高包含边框与内边距。</figcaption>
</figure>

<table>
  <thead><tr><th style="width:210px;">属性</th><th>作用与常见取值</th></tr></thead>
  <tbody>
    <tr><td><code>display</code></td><td>决定这个盒子在布局中的身份，最重要的一条。取值 <code>block</code> / <code>inline</code> / <code>inline-block</code> / <code>flex</code> / <code>grid</code> / <code>none</code>。</td></tr>
    <tr><td><code>margin</code> / <code>padding</code></td><td>上下左右间距；<code>padding</code> 有背景色，<code>margin</code> 永远透明。</td></tr>
    <tr><td><code>border</code></td><td>边框，写作 <code>border: 1px solid #ccc</code>。</td></tr>
    <tr><td><code>overflow</code></td><td>内容超出盒子时怎么办，<code>auto</code> 是最常用的（需要才出滚动条）。</td></tr>
    <tr><td><code>position</code></td><td>脱离正常流的方式。<code>relative</code> 相对自身偏移、<code>absolute</code> 相对最近的定位祖先、<code>fixed</code> 相对视口、<code>sticky</code> 滚动到阈值后粘住。</td></tr>
  </tbody>
</table>

<h3>4.2 层叠与优先级：为什么我的样式没生效</h3>

<p>当多条规则作用于同一个属性时，浏览器按下面的顺序决出胜者 —— 这是<b>规范</b>规定的判定顺序，不是经验法则：</p>

<ol>
  <li><b>来源与重要性。</b>带 <code>!important</code> 的声明优先于普通声明；作者样式优先于浏览器默认样式。</li>
  <li><b>选择器特异性（specificity）。</b>把选择器拆成三类计数，按「内联 &gt; id &gt; class / 属性 / 伪类 &gt; 元素 / 伪元素」从高到低比较。</li>
  <li><b>出现顺序。</b>以上全部相同时，写在后面的赢。</li>
</ol>

<table>
  <thead><tr><th style="width:250px;">选择器</th><th style="width:110px;">特异性</th><th>说明</th></tr></thead>
  <tbody>
    <tr><td><code>tbody td</code></td><td class="num">0,0,2</td><td>两个元素选择器，各计 1</td></tr>
    <tr><td><code>table.data td</code></td><td class="num">0,1,2</td><td>一个 class 计 1，元素各计 1</td></tr>
    <tr><td><code>#report td</code></td><td class="num">1,0,1</td><td>一个 id 直接压过上面两条</td></tr>
    <tr><td><code>style="color:red"</code></td><td class="num">内联</td><td>写在标签上的内联样式，高于任何选择器</td></tr>
    <tr><td><code>color: red !important</code></td><td class="num">最高</td><td>压过内联，因此也最难被覆盖</td></tr>
  </tbody>
</table>

<div class="box finding">
  <span class="t">排查「样式不生效」的三步动作</span>
  <p>不要反复改代码猜。打开开发者工具，选中该元素，在右侧的样式面板里从上往下看：
  <b>(1)</b> 你写的那条规则在不在列表里？不在说明选择器没匹配上（多半是类名拼错或层级写错）；
  <b>(2)</b> 在列表里但被划了删除线？说明被更高优先级的规则覆盖了，直接看压在上面的是谁；
  <b>(3)</b> 规则生效了但看不到变化？说明属性写错了或者值非法（例如给 <code>width</code> 写了 <code>auto</code> 之外的字符串）。
  这三步能定位九成以上的样式问题，比反复读代码快得多。</p>
</div>

<h3>4.3 布局：三种机制，一条判断路径</h3>

<figure>
<svg viewBox="0 0 680 252" role="img" aria-label="布局机制选择流程图：先判断是一维排列还是二维对齐，再决定用正常流、Flex 还是 Grid">
  <g font-family="-apple-system,BlinkMacSystemFont,'Segoe UI','PingFang SC','Microsoft YaHei',Helvetica,Arial,sans-serif">
    <rect x="250" y="12" width="180" height="40" rx="5" fill="#ffffff" stroke="#c9d2dc"/>
    <text x="340" y="37" text-anchor="middle" font-size="12" font-weight="700" fill="#17181a">要摆放一组元素</text>
    <line x1="340" y1="52" x2="340" y2="70" stroke="#1b4f8a" stroke-width="1.4"/>
    <polygon points="340,78 336.5,70 343.5,70" fill="#1b4f8a"/>
    <rect x="190" y="78" width="300" height="50" rx="5" fill="#eef3f8" stroke="#1b4f8a"/>
    <text x="340" y="100" text-anchor="middle" font-size="12" font-weight="700" fill="#1b4f8a">一维排列，还是二维对齐？</text>
    <text x="340" y="118" text-anchor="middle" font-size="10.5" fill="#5b6570">这个问题直接决定用哪种机制</text>
    <line x1="254" y1="128" x2="152" y2="164" stroke="#c9d2dc" stroke-width="1.3"/>
    <polygon points="146,168 152,161 155,166" fill="#c9d2dc"/>
    <line x1="340" y1="128" x2="340" y2="164" stroke="#1b4f8a" stroke-width="1.3"/>
    <polygon points="340,170 336.5,162 343.5,162" fill="#1b4f8a"/>
    <line x1="426" y1="128" x2="528" y2="164" stroke="#1b4f8a" stroke-width="1.3"/>
    <polygon points="534,168 525,166 528,161" fill="#1b4f8a"/>
    <rect x="20" y="170" width="200" height="56" rx="5" fill="#ffffff" stroke="#c9d2dc"/>
    <text x="120" y="192" text-anchor="middle" font-size="11.5" font-weight="700" fill="#17181a">正常流（默认）</text>
    <text x="120" y="210" text-anchor="middle" font-size="10.5" fill="#5b6570">块级上下排、行内左右排</text>
    <rect x="240" y="170" width="200" height="56" rx="5" fill="#eef3f8" stroke="#1b4f8a"/>
    <text x="340" y="192" text-anchor="middle" font-size="11.5" font-weight="700" fill="#1b4f8a">Flex 弹性盒</text>
    <text x="340" y="210" text-anchor="middle" font-size="10.5" fill="#17181a">一行或一列，自动分配余量</text>
    <rect x="460" y="170" width="200" height="56" rx="5" fill="#eef3f8" stroke="#1b4f8a"/>
    <text x="560" y="192" text-anchor="middle" font-size="11.5" font-weight="700" fill="#1b4f8a">Grid 网格</text>
    <text x="560" y="210" text-anchor="middle" font-size="10.5" fill="#17181a">行与列同时定义，精确对齐</text>
    <text x="16" y="246" font-size="10.5" fill="#8b949e">判断顺序：能用正常流就用正常流 → 一维用 Flex → 行列都要对齐才用 Grid。不要一上来就 Grid。</text>
  </g>
</svg>
<figcaption><b>图 4 |</b> 布局机制的判断路径。这条路径的价值在于避免「用 Grid 硬做一行三个按钮」这类绕远路的写法。
另外注意：<code>display</code> 是布局机制的总开关，<code>flex</code> 与 <code>grid</code> 写的是<b>父容器</b>，
子元素负责被排布，这是新手最容易搞反的一处。</figcaption>
</figure>

<table>
  <thead><tr><th style="width:130px;">机制</th><th style="width:120px;">适合</th><th>代价与注意</th></tr></thead>
  <tbody>
    <tr><td>正常流</td><td><span class="pill ok">默认首选</span></td><td>零成本、自然响应。适合文章、表单这类线性内容。</td></tr>
    <tr><td><code>float</code></td><td><span class="pill bad">避免</span></td><td>当年用于多列布局，需要清浮动且易塌陷。今天只在「文字环绕图片」这一个场景仍合适。</td></tr>
    <tr><td><code>position: absolute</code></td><td><span class="pill cav">克制使用</span></td><td>脱离正常流，父元素不会为它撑高。适合角标、悬浮层，不适合做整体布局。</td></tr>
    <tr><td>Flex</td><td><span class="pill ok">推荐</span></td><td>一维布局的标准答案。工具栏、卡片行、垂直居中都用它。</td></tr>
    <tr><td>Grid</td><td><span class="pill ok">推荐</span></td><td>二维布局的标准答案。整体页面骨架、整齐的指标卡片矩阵用它最省心。</td></tr>
  </tbody>
</table>

<p>一个够用很久的写法组合 —— 页面骨架用 Grid，内部局部用 Flex：</p>

<pre><code><span class="cm">/* 父容器：整体骨架，两栏（主内容 + 侧栏） */</span>
<span class="kw">.layout</span> {
  <span class="cm">/* fr 表示「剩余空间按份数分」，比写百分比更好用 */</span>
  display: grid;
  grid-template-columns: <span class="mk">1fr</span> <span class="mk">320px</span>;
  gap: 24px;
}
<span class="cm">/* 父容器：一行指标卡片，空间不够时自动换行 */</span>
<span class="kw">.cards</span> {
  display: flex;
  flex-wrap: wrap;        <span class="cm">/* 不写这行就不会换行，只会在原地挤扁 */</span>
  gap: 16px;
  align-items: center;    <span class="cm">/* 交叉轴对齐：这里指垂直居中 */</span>
}
<span class="kw">.cards &gt; *</span> {
  flex: 1 1 200px;        <span class="cm">/* 可伸可缩，基准 200px —— 自适应卡片的标准写法 */</span>
}
<span class="cm">/* 小屏时骨架改成一栏 */</span>
@media (max-width: 720px) {
  <span class="kw">.layout</span> { grid-template-columns: <span class="mk">1fr</span>; }
}</code></pre>

<h3>4.4 单位与响应式</h3>

<table>
  <thead><tr><th style="width:120px;">单位</th><th style="width:220px;">含义</th><th>什么时候用</th></tr></thead>
  <tbody>
    <tr><td><code>px</code></td><td>CSS 像素，与设备物理像素无关</td><td>边框、细线、需要精确 1px 的地方</td></tr>
    <tr><td><code>rem</code></td><td>相对<b>根元素</b>字号；浏览器默认 1rem = 16px</td><td>字号、间距的首选 —— 用户改了浏览器字号能整体缩放</td></tr>
    <tr><td><code>em</code></td><td>相对<b>自身或父元素</b>字号</td><td>组件内部相关的间距；会层层累积，容易失控，新手期少用</td></tr>
    <tr><td><code>%</code></td><td>相对父元素的同维度尺寸</td><td>宽度自适应；注意高度百分比需要父元素有确定高度</td></tr>
    <tr><td><code>vw</code> / <code>vh</code></td><td>视口宽 / 高的 1%</td><td>全屏区块；<code>vh</code> 在移动端浏览器地址栏收发时会跳变，谨慎使用</td></tr>
    <tr><td><code>fr</code></td><td>Grid 专用，剩余空间的一份</td><td>Grid 里分配列宽</td></tr>
  </tbody>
</table>

<p>响应式（responsive）的目标是<b>同一份 HTML 适配不同宽度</b>，做法是移动优先 + 媒体查询：</p>

<pre><code><span class="cm">/* (1) 先写窄屏样式作为默认值 —— 移动优先 */</span>
<span class="kw">.cards</span> { display: flex; flex-direction: column; }
<span class="cm">/* (2) 宽度够了再逐级增强，而不是先写桌面端再往回打补丁 */</span>
@media (min-width: 720px) {
  <span class="kw">.cards</span> { flex-direction: row; }
}
@media (min-width: 1100px) {
  <span class="kw">.layout</span> { grid-template-columns: <span class="mk">240px</span> <span class="mk">1fr</span> <span class="mk">280px</span>; }
}</code></pre>

<h3>4.5 三个高频坑</h3>

<table>
  <thead><tr><th style="width:190px;">症状</th><th>原因与解法</th></tr></thead>
  <tbody>
    <tr><td>子元素设了 <code>margin-top</code>，父元素跟着往下跑</td><td>外边距折叠（margin collapsing）—— 相邻的上下外边距会合并。解法：给父元素加 <code>padding-top</code> 或 <code>overflow: hidden</code>，或者直接用 Flex 让子元素不再相邻折叠。</td></tr>
    <tr><td><code>z-index</code> 写到 9999 还是压不住</td><td><code>z-index</code> 只在<b>同一层叠上下文</b>内比较。父元素若有 <code>transform</code>、<code>opacity</code> 小于 1、<code>position</code> 加 <code>z-index</code>，就会另起一个上下文，里面再大的值也越不出父级。</td></tr>
    <tr><td>内容莫名溢出容器，右侧出现横向滚动条</td><td>固定宽度（如 <code>width: 400px</code>）加上 padding 与 border 超出父宽。解法：改用 <code>max-width</code> 与 <code>box-sizing: border-box</code>。</td></tr>
  </tbody>
</table>

<!-- ============================================================ -->
<h2><span class="n">5</span>JavaScript：语言核心</h2>
<p class="lede">这一节是耗时最长的一支。以下所有「实测」均在 Node v22.22.2 上运行得到，原始输出见 §5.10。</p>

<p>JavaScript（常缩写为 JS）是前端唯一能运算的语言，也是三者里唯一需要真正花时间学的。
好消息是：你不需要学完它。下面这些概念覆盖了做页面时九成以上的场景，剩下的边用边查。
本节所有实测都只反映 JS 引擎行为，不涉及任何浏览器或 DOM 结论。</p>

<h3>5.1 值与类型</h3>

<p>JS 有 7 种原始类型（primitive）加 1 种引用类型（object）。做数据的人最容易踩的是前两行：</p>

<pre><code>typeof 42          <span class="cm">// 'number'  —— 没有整型，42 与 42.0 是同一个东西</span>
typeof '42'        <span class="cm">// 'string'  —— 引号决定一切</span>
typeof true        <span class="cm">// 'boolean'</span>
typeof undefined   <span class="cm">// 'undefined'</span>
typeof null        <span class="cm">// 'object'  —— 实测，这是语言早期的遗留问题，不是笔误</span>
typeof []          <span class="cm">// 'object'  —— 数组也是 object，typeof 分不出来</span>
Array.isArray([])  <span class="cm">// true      —— 判断数组只能用它</span>
typeof document    <span class="cm">// 浏览器里是 'object'；Node 里是 'undefined'（实测）</span></code></pre>

<div class="box">
  <span class="t">一条能省很多时间的习惯</span>
  <p>拿不准一个值是数字还是字符串时，不要猜，直接 <code>console.log(typeof v, v)</code>。
  从表里读出来的 <code>value</code> 永远是<b>字符串</b>，这是最经典的坑：<code>'57.3' &gt; '100'</code> 为真（按字符串逐位比较），
  而 <code>57.3 &gt; 100</code> 为假。看到结果反直觉时，第一反应应该是检查类型。</p>
</div>

<h3>5.2 相等：只用 === 就够了</h3>

<p><code>==</code> 会在比较前先做类型转换，<code>===</code> 不做。转换规则复杂且反直觉，所以工程上的<b>惯例是全部使用 <code>===</code></b>。
下表是实测结果：</p>

<table>
  <thead><tr><th style="width:250px;">表达式</th><th style="width:90px;">结果</th><th>为什么值得记住</th></tr></thead>
  <tbody>
    <tr><td><code>'' == 0</code></td><td><span class="pill bad">true</span></td><td>空字符串被转成 0。用它判断「有没有填写」会误判。</td></tr>
    <tr><td><code>'' === 0</code></td><td><span class="pill ok">false</span></td><td>换成严格相等就符合直觉了。</td></tr>
    <tr><td><code>[] == false</code></td><td><span class="pill bad">true</span></td><td>空数组既被当成空字符串又被当成假值。这就是为什么数组判空要用 <code>arr.length === 0</code>。</td></tr>
    <tr><td><code>null == undefined</code></td><td><span class="pill cav">true</span></td><td>唯一一个宽松相等有用的场合：<code>v == null</code> 同时覆盖两者。</td></tr>
    <tr><td><code>null === undefined</code></td><td><span class="pill ok">false</span></td><td>严格相等下它们是两个不同的值。</td></tr>
    <tr><td><code>NaN === NaN</code></td><td><span class="pill cav">false</span></td><td>与 R 一致，判断缺失/非法数值要用 <code>Number.isNaN(v)</code>。</td></tr>
    <tr><td><code>[]</code> 作为条件</td><td><span class="pill bad">真</span></td><td>空数组是真值。同理 <code>Boolean('0')</code> 为 <code>true</code>，因为非空字符串都是真。<b>实测</b></td></tr>
    <tr><td><code>Boolean('')</code></td><td><span class="pill ok">false</span></td><td>假值只有固定的几个：<code>false</code>、<code>0</code>、<code>''</code>、<code>null</code>、<code>undefined</code>、<code>NaN</code>。</td></tr>
  </tbody>
</table>

<h3>5.3 数字与精度</h3>

<pre><code>0.1 + 0.2               <span class="cm">// 0.30000000000000004   —— 实测</span>
0.1 + 0.2 === 0.3       <span class="cm">// false                 —— 实测</span>
<span class="cm">// 结论：浮点数不要直接用 === 比较，用容差</span>
Math.abs(a - b) &lt; 1e-9  <span class="cm">// 这才是「约等于」的正确写法</span>
Number('12abc')         <span class="cm">// NaN   —— 转换失败会给出 NaN，而不是报错</span>
Number('')              <span class="cm">// 0     —— 注意：空字符串转出来是 0，不是 NaN</span>
parseInt('12abc')       <span class="cm">// 12    —— 它更宽容，会解析到不能解析为止</span></code></pre>

<p class="small">补充一个记录细节：§5.10 里 <code>Number('12abc')</code> 显示为 <code>null</code>，
是因为输出用了 <code>JSON.stringify</code>，而 <code>NaN</code> 在 JSON 里没有表示法，会被编码成 <code>null</code>。
这本身也是个值得记住的事实 —— 把含 NaN 的数据发成 JSON，对方收到的是 <code>null</code>。</p>

<div class="box finding">
  <span class="t">给数据人的一句提醒</span>
  <p>统计量在 JS 里没有「整数」概念，也不区分缺失与零。把 <code>NaN</code> 通过网络传成 JSON 会静默变成 <code>null</code>，
  再读回来时你必须自己决定它代表「缺失」还是「真的没有」。这个决定最好在接口约定里写清楚，而不是在代码里猜。</p>
</div>

<h3>5.4 作用域、声明与闭包</h3>

<pre><code>console.log(typeof hoistedVar);  <span class="cm">// 'undefined'          —— 实测：var 声明被提升，值是 undefined</span>
var hoistedVar = 1;
console.log(typeof tdzLet);      <span class="cm">// 抛 ReferenceError    —— 实测：let 有暂时性死区</span>
let tdzLet = 1;
<span class="cm">// 闭包：函数记住了它定义时所在的作用域</span>
const makeCounter = () =&gt; {
  let n = 0;                     <span class="cm">// 这个变量不会随函数返回而消失</span>
  return () =&gt; ++n;              <span class="cm">// 内部函数「捕获」了 n</span>
};
const next = makeCounter();
next(); next();                  <span class="cm">// 2</span></code></pre>

<table>
  <thead><tr><th style="width:96px;">声明</th><th style="width:150px;">作用域</th><th>能不能改</th></tr></thead>
  <tbody>
    <tr><td><code>var</code></td><td>函数作用域，声明提升</td><td>可改可重声明。<b>新代码不要用</b>。</td></tr>
    <tr><td><code>let</code></td><td>块级作用域（<code>{}</code> 内）</td><td>可改，不可重声明。</td></tr>
    <tr><td><code>const</code></td><td>块级作用域</td><td>绑定不可改 —— <b>但内容可以改</b>。实测：<code>const a = [1,2]; a.push(3)</code> 完全合法，得到 <code>[1,2,3]</code>。</td></tr>
  </tbody>
</table>

<p><code>const</code> 只锁住「这个名字指向哪个对象」，不锁对象内部。<code>const a = [1,2]; a = []</code> 会报错，
但 <code>a.push(3)</code> 不会。想要真正不可变需要 <code>Object.freeze()</code>（且只冻结一层）。</p>

<h4>闭包在循环里的经典表现</h4>

<pre><code><span class="cm">// 用 var：三个函数共享同一个 i，循环结束后 i 是 3</span>
const f1 = [];
for (var i = 0; i &lt; 3; i++) f1.push(() =&gt; i);
f1.map(fn =&gt; fn());   <span class="cm">// [3, 3, 3]   —— 实测，几乎肯定不是你要的</span>
<span class="cm">// 用 let：每一轮循环都有自己的 i</span>
const f2 = [];
for (let i = 0; i &lt; 3; i++) f2.push(() =&gt; i);
f2.map(fn =&gt; fn());   <span class="cm">// [0, 1, 2]   —— 实测</span></code></pre>

<h3>5.5 this：谁调用，就指向谁</h3>

<p><code>this</code> 的值由<b>调用方式</b>决定，不由定义位置决定。这一条规则能解释绝大多数困惑：</p>

<pre><code>const obj = { v: 7, normal() { return this.v; } };
obj.normal();        <span class="cm">// 7          —— 实测：作为对象的方法被调用，this = obj</span>
const bare = obj.normal;
bare();              <span class="cm">// undefined  —— 实测：脱钩后 this 不再是 obj（严格模式下为 undefined）</span>
<span class="cm">// 对策一：用箭头函数。箭头函数没有自己的 this，直接沿用外层的。</span>
<span class="cm">// 对策二：把方法写成 obj.normal = () =&gt; {...} 时注意，此时 this 是外层的，不是 obj。</span></code></pre>

<p>实践建议：在事件回调里尽量用箭头函数，或者把需要的对象提前解构成局部变量，
这样就不必推理 <code>this</code> 是什么。</p>

<h3>5.6 数组：从「向量化」到「遍历」</h3>

<p>这是 R / Python / SAS 使用者最需要重学的部分。这些语言里对一列数据做变换是<b>一次声明</b>，
JS 里是<b>一次遍历</b>。三个方法承担了这个工作，实测结果如下：</p>

<pre><code>const v = [1, 2, 3];
v.map(x =&gt; x * 2);              <span class="cm">// [2, 4, 6]    —— 实测：返回新数组，长度不变</span>
v.forEach(x =&gt; x * 2);          <span class="cm">// undefined    —— 实测：只遍历，不返回任何东西</span>
v.filter(x =&gt; x &gt; 1);           <span class="cm">// [2, 3]       —— 返回新数组，长度可变</span>
v.reduce((s, x) =&gt; s + x, 0);   <span class="cm">// 10           —— 折叠成单个值（求和、计数、分组）</span>
v                       <span class="cm">// [1, 2, 3]    —— 原数组没被改动，三个方法都不改原数组</span>
<span class="cm">// 分组：用 reduce 把行按组归拢（可以理解为减少一次 group_by）</span>
const rows = [{ g: 'A', v: 1 }, { g: 'B', v: 2 }, { g: 'A', v: 3 }];
rows.reduce((acc, r) =&gt; { (acc[r.g] ||= []).push(r.v); return acc; }, {});
<span class="cm">// {"A":[1,3],"B":[2]}   —— 实测</span></code></pre>

<div class="box finding">
  <span class="t">最危险的一条：sort 默认按字符串比较</span>
  <p>实测：<code>[10, 9, 100].sort()</code> 得到 <code>[10, 100, 9]</code> —— 因为默认把元素转成字符串逐位比较。
  必须显式给比较函数：<code>sort((a, b) =&gt; a - b)</code> 才得到 <code>[9, 10, 100]</code>。
  另外 <code>sort</code> 是<b>原地修改</b>的（实测 <code>a.sort() === a</code> 为 <code>true</code>），
  所以它会改掉原数组 —— 想保留原顺序要先复制：<code>[...rows].sort(...)</code>。</p>
</div>

<figure>
<svg viewBox="0 0 680 250" role="img" aria-label="同一数据变换在 R、Python、SAS、JavaScript 中的四种写法对照">
  <g font-family="-apple-system,BlinkMacSystemFont,'Segoe UI','PingFang SC','Microsoft YaHei',Helvetica,Arial,sans-serif">
    <text x="16" y="16" font-size="11" font-weight="700" fill="#17181a">同一个意图：取出 value 大于 10 的记录</text>
    <rect x="16" y="28" width="68" height="30" rx="4" fill="#f7f8f9" stroke="#dfe5ea"/>
    <text x="50" y="48" text-anchor="middle" font-size="11.5" font-weight="700" fill="#17181a">R</text>
    <text x="98" y="48" font-size="11.5" fill="#1f2328" font-family="Consolas,'Liberation Mono',Menlo,monospace">df$value[df$value &gt; 10]   # 一行声明，无需循环</text>
    <rect x="16" y="76" width="68" height="30" rx="4" fill="#f7f8f9" stroke="#dfe5ea"/>
    <text x="50" y="96" text-anchor="middle" font-size="11.5" font-weight="700" fill="#17181a">Python</text>
    <text x="98" y="96" font-size="11.5" fill="#1f2328" font-family="Consolas,'Liberation Mono',Menlo,monospace">df.loc[df.value &gt; 10, "value"</text>
    <text x="98" y="112" font-size="11.5" fill="#1f2328" font-family="Consolas,'Liberation Mono',Menlo,monospace">]   # 列表推导同理</text>
    <rect x="16" y="124" width="68" height="30" rx="4" fill="#f7f8f9" stroke="#dfe5ea"/>
    <text x="50" y="144" text-anchor="middle" font-size="11.5" font-weight="700" fill="#17181a">SAS</text>
    <text x="98" y="144" font-size="11.5" fill="#1f2328" font-family="Consolas,'Liberation Mono',Menlo,monospace">where value &gt; 10;   /* 在 PROC 步骤内声明 */</text>
    <rect x="16" y="172" width="68" height="30" rx="4" fill="#eef3f8" stroke="#1b4f8a"/>
    <text x="50" y="192" text-anchor="middle" font-size="11.5" font-weight="700" fill="#1b4f8a">JS</text>
    <text x="98" y="192" font-size="11.5" fill="#0b3d68" font-family="Consolas,'Liberation Mono',Menlo,monospace">rows.filter(r =&gt; r.value &gt; 10)</text>
    <line x1="16" y1="216" x2="664" y2="216" stroke="#eaeef2" stroke-width="1"/>
    <text x="16" y="236" font-size="10.5" fill="#8b949e">前三种是「声明要什么」，JS 是「说明怎么走一遍」—— 差别就来自有没有向量化和表格类型。</text>
  </g>
</svg>
<figcaption><b>图 5 |</b> 同一个意图的四种写法。R 与 pandas 的写法把条件当作列上的一个整体操作；
JS 的写法显式遍历每一行。理解这一点，就理解了为什么 JS 处理表格数据通常要借助库（§9.4）。</figcaption>
</figure>

<h3>5.7 对象：数据在 JS 里的形状</h3>

<p>没有 data.frame，一行数据通常就是一个<b>对象</b>，多行就是一个对象数组。
这与 R 的按列存储是反的，是转过来之后需要习惯的第一件事。</p>

<pre><code><span class="cm">// 一行数据 = 一个对象</span>
const row = { id: 1, age: 57.3, sex: 'F' };
row.age                          <span class="cm">// 57.3   点号取值</span>
row['age']                        <span class="cm">// 57.3   方括号取值，键是变量时必须用这种</span>
Object.keys(row)                 <span class="cm">// ['id','age','sex']   —— 相当于列名</span>
<span class="cm">// 解构：把字段取成局部变量，读起来更短</span>
const { age, sex } = row;
<span class="cm">// 展开：生成新对象，而不是修改原对象（修改原对象会让页面状态难追踪）</span>
const updated = { ...row, age: 58 };</code></pre>

<div class="box">
  <span class="t">一条与数据语言相反的直觉</span>
  <p>在 R 或 pandas 里，<code>df$age &lt;- 58</code> 是很自然的写法 —— 原地改一列。
  在 JS 里<b>惯例是生成新对象</b>而不是改旧的，因为界面需要知道「什么变了」才能只重画变化的部分。
  这条习惯在 §9 讲框架时会直接决定你能不能看懂状态更新的代码。</p>
</div>

<h3>5.8 异步与事件循环</h3>

<p>网络请求、读文件、等用户点击，这些事都需要等。JS 的处理方式是<b>不阻塞</b>：
把后续动作写成一个函数交给引擎，引擎在结果就绪时再调用它。</p>

<pre><code>console.log('1 同步开始');
setTimeout(() =&gt; console.log('5 setTimeout 回调'), 0);
Promise.resolve().then(() =&gt; console.log('3 promise.then'));
queueMicrotask(() =&gt; console.log('4 queueMicrotask'));
console.log('2 同步结束');
<span class="cm">// 实测输出顺序：1 同步开始 → 2 同步结束 → 3 promise.then → 4 queueMicrotask → 5 setTimeout 回调</span></code></pre>

<figure>
<svg viewBox="0 0 680 280" role="img" aria-label="JavaScript 事件循环示意图：调用栈、微任务队列与宏任务队列">
  <g font-family="-apple-system,BlinkMacSystemFont,'Segoe UI','PingFang SC','Microsoft YaHei',Helvetica,Arial,sans-serif">
    <rect x="20" y="44" width="180" height="76" rx="5" fill="#ffffff" stroke="#c9d2dc"/>
    <text x="110" y="68" text-anchor="middle" font-size="11.5" font-weight="700" fill="#17181a">调用栈</text>
    <text x="110" y="86" text-anchor="middle" font-size="10" fill="#5b6570">Call Stack</text>
    <text x="110" y="104" text-anchor="middle" font-size="10" fill="#5b6570">正在执行的函数</text>
    <rect x="240" y="58" width="120" height="48" rx="24" fill="#eef3f8" stroke="#1b4f8a"/>
    <text x="300" y="87" text-anchor="middle" font-size="11.5" font-weight="700" fill="#1b4f8a">事件循环</text>
    <line x1="400" y1="76" x2="366" y2="76" stroke="#1b4f8a" stroke-width="1.3"/>
    <polygon points="358,76 366,72.5 366,79.5" fill="#1b4f8a"/>
    <line x1="240" y1="82" x2="206" y2="82" stroke="#1b4f8a" stroke-width="1.3"/>
    <polygon points="198,82 206,78.5 206,85.5" fill="#1b4f8a"/>
    <rect x="400" y="44" width="264" height="64" rx="5" fill="#ffffff" stroke="#c9d2dc"/>
    <text x="418" y="66" font-size="11.5" font-weight="700" fill="#17181a">微任务队列</text>
    <text x="418" y="84" font-size="10.5" fill="#5b6570">Promise.then / queueMicrotask</text>
    <text x="418" y="100" font-size="10.5" fill="#8b949e">当前代码跑完后立刻全部清空</text>
    <rect x="400" y="128" width="264" height="64" rx="5" fill="#ffffff" stroke="#c9d2dc"/>
    <text x="418" y="150" font-size="11.5" font-weight="700" fill="#17181a">宏任务队列</text>
    <text x="418" y="168" font-size="10.5" fill="#5b6570">setTimeout / 事件回调 / 网络回调</text>
    <text x="418" y="184" font-size="10.5" fill="#8b949e">每轮只取一个，取完先清空微任务</text>
    <line x1="400" y1="160" x2="366" y2="160" stroke="#1b4f8a" stroke-width="1.3"/>
    <polygon points="358,160 366,156.5 366,163.5" fill="#1b4f8a"/>
    <rect x="16" y="206" width="120" height="34" rx="4" fill="#f7f8f9" stroke="#dfe5ea"/>
    <text x="76" y="227" text-anchor="middle" font-size="10.5" fill="#17181a">1 同步代码</text>
    <rect x="148" y="206" width="120" height="34" rx="4" fill="#f7f8f9" stroke="#dfe5ea"/>
    <text x="208" y="227" text-anchor="middle" font-size="10.5" fill="#17181a">2 同步结束</text>
    <rect x="280" y="206" width="120" height="34" rx="4" fill="#eef3f8" stroke="#1b4f8a"/>
    <text x="340" y="227" text-anchor="middle" font-size="10.5" fill="#1b4f8a">3 promise.then</text>
    <rect x="412" y="206" width="120" height="34" rx="4" fill="#eef3f8" stroke="#1b4f8a"/>
    <text x="472" y="227" text-anchor="middle" font-size="10.5" fill="#1b4f8a">4 queueMicrotask</text>
    <rect x="544" y="206" width="120" height="34" rx="4" fill="#fdf7ec" stroke="#e8d3a8"/>
    <text x="604" y="227" text-anchor="middle" font-size="10.5" fill="#8a5a00">5 setTimeout</text>
    <text x="16" y="264" font-size="10.5" fill="#8b949e">实测顺序（Node v22.22.2）。要点：setTimeout(fn, 0) 的「0」是最短等待，不是立刻执行。</text>
  </g>
</svg>
<figcaption><b>图 6 |</b> 事件循环。为什么要关心这个：它解释了「为什么我 <code>setTimeout</code> 写在前面，却最后才执行」，
也解释了为什么接口还没返回时页面不会卡死 —— 等待期间引擎继续处理其他事情。入门阶段只需记住那条执行顺序。</figcaption>
</figure>

<p>实际写代码时用 <code>async</code> / <code>await</code>，它的含义是「在这里等结果，但等待期间不阻塞页面」：</p>

<pre><code>async function loadRows() {
  const res = await fetch('/api/rows');   <span class="cm">// 等价于「等这个 Promise 出结果」</span>
  const data = await res.json();          <span class="cm">// 解析 JSON 也是异步的</span>
  render(data);
}
<span class="cm">// 错误必须显式处理，否则会静默失败</span>
loadRows().catch(err =&gt; console.error('加载失败', err));</code></pre>

<h3>5.9 DOM 与事件：真正操作页面的地方</h3>

<p>DOM（Document Object Model）是浏览器把 HTML 解析出来的那棵对象树。JS 通过它读改页面。
下面这段把一组统计结果渲染成表格 —— 它是后面结课项目的核心动作：</p>

<pre><code>const rows = [
  { variable: '年龄',      mean: 57.3, sd: 11.4 },
  { variable: '体质指数',  mean: 24.8, sd: 3.1  },
];
const tbody = document.querySelector('#result tbody');   <span class="cm">// (1) 选中容器</span>
tbody.replaceChildren();                                  <span class="cm">// (2) 清空，避免重复渲染</span>
for (const r of rows) {                                   <span class="cm">// (3) 逐行构造真实元素</span>
  const tr = document.createElement('tr');
  const tdName = document.createElement('td');
  tdName.textContent = r.variable;         <span class="cm">// 用 textContent 而不是 innerHTML</span>
  const tdStat = document.createElement('td');
  tdStat.textContent = `${r.mean.toFixed(1)} (${r.sd.toFixed(1)})`;
  tr.append(tdName, tdStat);
  tbody.append(tr);
}</code></pre>

<div class="box finding">
  <span class="t">不要用 innerHTML 拼接用户可见的数据</span>
  <p><code>innerHTML = '&lt;td&gt;' + value + '&lt;/td&gt;'</code> 会把 <code>value</code> 当成 HTML 解析。
  如果这个值来自用户输入或外部文件，里面一个 <code>&lt;script&gt;</code> 或 <code>&lt;img onerror=...&gt;</code>
  就能在你的页面上执行任意代码（跨站脚本攻击，XSS）。<code>textContent</code> 只设置纯文本，永远更安全，
  而且更快。<code>innerHTML</code> 留给「你自己写的、不含任何外部数据的静态片段」。</p>
</div>

<h4>事件：不要给每一行都绑监听</h4>

<pre><code><span class="cm">// 反例：行多了就是几百个监听器，新增的行还得补绑</span>
document.querySelectorAll('tr').forEach(tr =&gt; tr.addEventListener('click', onClick));
<span class="cm">// 正例：事件委托 —— 只在父容器上绑一次，靠 event.target 判断点到了谁</span>
tbody.addEventListener('click', (e) =&gt; {
  const tr = e.target.closest('tr');    <span class="cm">// 从被点的元素向上找最近的行</span>
  if (!tr) return;
  console.log('点击了第', tr.rowIndex, '行');
});</code></pre>

<h3>5.10 实测原始输出</h3>

<p>本节所有标注「实测」的结论，来自下面这次运行。环境为 Node v22.22.2，命令为
<code>node fe-verify.js</code>，脚本只用语言内置对象，不涉及 DOM。</p>

<pre><code>== runtime ==
node            | v22.22.2
== types and equality ==
typeof null                        | "object"
typeof []                          | "object"
Array.isArray([])                  | true
typeof document                    | "undefined"
'1' + 1                            | "11"
'3' * 2                            | 6
'3' - 1                            | 2
'12abc' * 1                        | null        &lt;-- NaN，被 JSON 编码成 null
Number("12abc")                    | null        &lt;-- 同上，实际是 NaN
Number("")                         | 0
parseInt("12abc")                  | 12
"" == 0                            | true
"" === 0                           | false
[] == false                        | true
null == undefined                  | true
null === undefined                 | false
NaN === NaN                        | false
[] ? a : b                         | "truthy"
Boolean("0")                       | true
Boolean("")                        | false
0.1 + 0.2                          | 0.30000000000000004
0.1 + 0.2 === 0.3                  | false
== scope, hoisting, this, closures ==
typeof hoistedVar (var, before dec | "undefined"
typeof tdzLet (let, before decl)   | THROW ReferenceError: Cannot access 'tdzLet' before initialization
objThis.normal()                   | 7
detached method call               | undefined
var in for-loop closures           | [3,3,3]
let in for-loop closures           | [0,1,2]
== arrays: in-place vs returning ==
[10,9,100].sort()                  | [10,100,9]
[10,9,100].sort((a,b)=&gt;a-b)        | [9,10,100]
sort() returns the SAME array      | true
[1,2,3].map(x=&gt;x*2)                | [2,4,6]
[1,2,3].forEach(x=&gt;x*2)            | undefined
map on sparse hole                 | "[2,null,6]"
const array stays mutable          | [1,2,3]
push returns                       | 3
reduce sum                         | 10
groupBy-free tally pattern         | {"A":[1,3],"B":[2]}
== event loop ==
observed order   | ["1 sync start","2 sync end","3 promise.then","4 queueMicrotask","5 setTimeout(0) callback"]</code></pre>

<p class="small">三处需要额外说明：<b>(1)</b> 用 <code>JSON.stringify</code> 输出时 <code>NaN</code> 会变成 <code>null</code>，
所以 <code>'12abc' * 1</code> 显示为 <code>null</code>，它真实的值是 <code>NaN</code>；
<b>(2)</b> 稀疏数组的 <code>map</code> 会跳过空位，空位在输出里同样显示为 <code>null</code>；
<b>(3)</b> 这次运行里 <code>typeof document</code> 是 <code>'undefined'</code>，因为 Node 没有 DOM ——
这也是 §1.2 那个边界的实测依据：同一门语言，在不同环境里能用的东西不一样。</p>

<!-- ============================================================ -->
<h2><span class="n">6</span>浏览器：从输入网址到屏幕上的像素</h2>
<p class="lede">理解这条链路，是为了知道「代码写在哪、什么时候执行、什么操作贵」。</p>

<p>输入网址到看见页面，浏览器做的事可以分成两段：先<b>取回文件</b>（网络部分，见 §7），
再把文件<b>变成像素</b>（渲染部分，本节）。后者五个阶段依次进行，任一阶段被打断都会表现为「页面白了一下」或「点了没反应」。</p>

<figure>
<svg viewBox="0 0 680 272" role="img" aria-label="浏览器关键渲染路径流程图：HTML 生成 DOM，CSS 生成 CSSOM，两者合成渲染树，再经布局、绘制、合成">
  <g font-family="-apple-system,BlinkMacSystemFont,'Segoe UI','PingFang SC','Microsoft YaHei',Helvetica,Arial,sans-serif">
    <rect x="20" y="24" width="116" height="38" rx="4" fill="#f7f8f9" stroke="#dfe5ea"/>
    <text x="78" y="48" text-anchor="middle" font-size="11.5" font-weight="700" fill="#17181a">HTML 文件</text>
    <line x1="136" y1="43" x2="148" y2="43" stroke="#1b4f8a" stroke-width="1.3"/>
    <polygon points="156,43 148,39.5 148,46.5" fill="#1b4f8a"/>
    <rect x="156" y="24" width="116" height="38" rx="4" fill="#ffffff" stroke="#c9d2dc"/>
    <text x="214" y="48" text-anchor="middle" font-size="11.5" font-weight="700" fill="#17181a">DOM 树</text>
    <rect x="20" y="96" width="116" height="38" rx="4" fill="#f7f8f9" stroke="#dfe5ea"/>
    <text x="78" y="120" text-anchor="middle" font-size="11.5" font-weight="700" fill="#17181a">CSS 文件</text>
    <line x1="136" y1="115" x2="148" y2="115" stroke="#1b4f8a" stroke-width="1.3"/>
    <polygon points="156,115 148,111.5 148,118.5" fill="#1b4f8a"/>
    <rect x="156" y="96" width="116" height="38" rx="4" fill="#ffffff" stroke="#c9d2dc"/>
    <text x="214" y="120" text-anchor="middle" font-size="11.5" font-weight="700" fill="#17181a">CSSOM 树</text>
    <polyline points="272,43 296,43 296,115 272,115" fill="none" stroke="#c9d2dc" stroke-width="1.3"/>
    <line x1="296" y1="79" x2="320" y2="79" stroke="#1b4f8a" stroke-width="1.4"/>
    <polygon points="328,79 320,75.5 320,82.5" fill="#1b4f8a"/>
    <rect x="330" y="59" width="330" height="40" rx="4" fill="#eef3f8" stroke="#1b4f8a"/>
    <text x="346" y="84" font-size="11.5" font-weight="700" fill="#1b4f8a">渲染树 Render Tree</text>
    <text x="492" y="84" font-size="10.5" fill="#17181a">只保留要画的节点</text>
    <line x1="495" y1="99" x2="495" y2="111" stroke="#1b4f8a" stroke-width="1.3"/>
    <polygon points="495,119 491.5,111 498.5,111" fill="#1b4f8a"/>
    <rect x="330" y="119" width="330" height="40" rx="4" fill="#ffffff" stroke="#c9d2dc"/>
    <text x="346" y="144" font-size="11.5" font-weight="700" fill="#17181a">布局 Layout（重排 Reflow）</text>
    <text x="546" y="144" font-size="10.5" fill="#5b6570">算位置与尺寸</text>
    <line x1="495" y1="159" x2="495" y2="171" stroke="#1b4f8a" stroke-width="1.3"/>
    <polygon points="495,179 491.5,171 498.5,171" fill="#1b4f8a"/>
    <rect x="330" y="179" width="330" height="40" rx="4" fill="#ffffff" stroke="#c9d2dc"/>
    <text x="346" y="204" font-size="11.5" font-weight="700" fill="#17181a">绘制 Paint（重绘 Repaint）</text>
    <text x="546" y="204" font-size="10.5" fill="#5b6570">填像素</text>
    <line x1="495" y1="219" x2="495" y2="231" stroke="#1b4f8a" stroke-width="1.3"/>
    <polygon points="495,239 491.5,231 498.5,231" fill="#1b4f8a"/>
    <rect x="330" y="239" width="330" height="30" rx="4" fill="#f7f8f9" stroke="#dfe5ea"/>
    <text x="346" y="259" font-size="11.5" font-weight="700" fill="#17181a">合成 Composite</text>
    <text x="470" y="259" font-size="10.5" fill="#5b6570">分层交给 GPU</text>
    <text x="20" y="170" font-size="10" fill="#8b949e">两者先各自</text>
    <text x="20" y="186" font-size="10" fill="#8b949e">建树，再合并</text>
    <text x="20" y="216" font-size="10" fill="#8b949e">任一步被 JS</text>
    <text x="20" y="232" font-size="10" fill="#8b949e">阻塞即白屏</text>
  </g>
</svg>
<figcaption><b>图 7 |</b> 关键渲染路径。HTML 与 CSS 必须<b>都</b>就绪才能开始画 —— 这是为什么把 CSS 放在
<code>&lt;head&gt;</code> 里、把阻塞脚本放到最后或加 <code>defer</code>，页面会明显更快出现内容（§6.2）。</figcaption>
</figure>

<h3>6.1 五个阶段的含义</h3>

<table>
  <thead><tr><th style="width:150px;">阶段</th><th>做什么</th><th style="width:130px;">代价</th></tr></thead>
  <tbody>
    <tr><td>解析 HTML → DOM</td><td>边下载边解析成对象树；遇到 <code>&lt;img&gt;</code> 等资源会去下载，遇到同步脚本会停下来等它</td><td>受脚本影响</td></tr>
    <tr><td>解析 CSS → CSSOM</td><td>所有样式规则合成一张总表</td><td><b>阻塞渲染</b>：CSS 没下完不画</td></tr>
    <tr><td>合并 → 渲染树</td><td>把 <code>display: none</code> 的节点剔除掉</td><td>轻</td></tr>
    <tr><td>布局 / 重排</td><td>算每个盒子的位置与大小</td><td><span class="pill cav">贵</span></td></tr>
    <tr><td>绘制 / 重绘</td><td>把颜色、文字、边框填成像素</td><td><span class="pill cav">中</span></td></tr>
    <tr><td>合成</td><td>分层交给 GPU 合成最终画面</td><td>轻（用 <code>transform</code> / <code>opacity</code> 可只走这一步）</td></tr>
  </tbody>
</table>

<p>日常最有用的推论：<b>改动的属性决定代价</b>。改 <code>width</code>、<code>top</code>、<code>font-size</code>
会引发重排加重绘；改 <code>color</code>、<code>background</code> 只引发重绘；
而改 <code>transform</code> 与 <code>opacity</code> 一般只走合成。所以做动画优先用 <code>transform: translate()</code>
而不是 <code>left</code>。</p>

<h3>6.2 script 怎么放：三种写法</h3>

<table>
  <thead><tr><th style="width:190px;">写法</th><th style="width:130px;">下载</th><th>执行时机与影响</th></tr></thead>
  <tbody>
    <tr><td><code>&lt;script src&gt;</code></td><td>解析到就下载</td><td><span class="pill bad">阻塞</span> 下载完立即执行，解析暂停。放在 <code>&lt;head&gt;</code> 会让首屏延迟。</td></tr>
    <tr><td><code>&lt;script defer&gt;</code></td><td>与解析并行</td><td><span class="pill ok">不阻塞</span> 等 HTML 解析完，<b>按出现顺序</b>执行。要操作 DOM 的脚本用这个。</td></tr>
    <tr><td><code>&lt;script async&gt;</code></td><td>与解析并行</td><td><span class="pill cav">不阻塞但乱序</span> 下载完就执行，谁先下完谁先跑。适合统计代码这类互不依赖的脚本。</td></tr>
  </tbody>
</table>

<p>实用结论：把 <code>&lt;script&gt;</code> 放在 <code>&lt;/body&gt;</code> 之前，或者写在 <code>&lt;head&gt;</code> 里加 <code>defer</code>。
两者都行，选一个并保持一致。</p>

<h3>6.3 开发者工具：四个面板够用到出师</h3>

<table>
  <thead><tr><th style="width:140px;">面板</th><th>用来回答什么问题</th></tr></thead>
  <tbody>
    <tr><td><b>Elements</b></td><td>现在真实的 DOM 长什么样？这条样式为什么被覆盖？盒模型的四层数值各是多少？</td></tr>
    <tr><td><b>Console</b></td><td>有没有报错？<code>console.log</code> 打出了什么？可以直接在这里敲一行代码试验。</td></tr>
    <tr><td><b>Network</b></td><td>请求发出去了吗？状态码是多少？返回的 JSON 是什么样子？这几个问题只能在这里回答。</td></tr>
    <tr><td><b>Application</b></td><td>本地存储里存了什么？Cookie 有哪些？</td></tr>
  </tbody>
</table>

<!-- ============================================================ -->
<h2><span class="n">7</span>数据通路：HTTP、fetch 与 JSON</h2>
<p class="lede">页面上的数据从哪来。这一节也是「本地能跑、线上报错」的答案所在。</p>

<figure>
<svg viewBox="0 0 680 268" role="img" aria-label="浏览器与服务器之间一次数据请求的往返时序图">
  <g font-family="-apple-system,BlinkMacSystemFont,'Segoe UI','PingFang SC','Microsoft YaHei',Helvetica,Arial,sans-serif">
    <rect x="40" y="16" width="240" height="36" rx="5" fill="#eef3f8" stroke="#1b4f8a"/>
    <text x="160" y="39" text-anchor="middle" font-size="12" font-weight="700" fill="#1b4f8a">页面里的 JavaScript</text>
    <rect x="400" y="16" width="240" height="36" rx="5" fill="#ffffff" stroke="#c9d2dc"/>
    <text x="520" y="39" text-anchor="middle" font-size="12" font-weight="700" fill="#17181a">服务器 / API</text>
    <line x1="160" y1="52" x2="160" y2="248" stroke="#c9d2dc" stroke-width="1" stroke-dasharray="4 4"/>
    <line x1="520" y1="52" x2="520" y2="248" stroke="#c9d2dc" stroke-width="1" stroke-dasharray="4 4"/>
    <text x="340" y="80" text-anchor="middle" font-size="10.5" fill="#17181a">① fetch('/api/rows?sex=F')</text>
    <line x1="160" y1="90" x2="512" y2="90" stroke="#1b4f8a" stroke-width="1.4"/>
    <polygon points="520,90 512,86.5 512,93.5" fill="#1b4f8a"/>
    <text x="340" y="122" text-anchor="middle" font-size="10.5" fill="#17181a">② 响应 200 + JSON 文本</text>
    <line x1="520" y1="132" x2="168" y2="132" stroke="#1b4f8a" stroke-width="1.4"/>
    <polygon points="160,132 168,128.5 168,135.5" fill="#1b4f8a"/>
    <text x="340" y="164" text-anchor="middle" font-size="10.5" fill="#17181a">③ await res.json() 解析 → 更新 DOM</text>
    <polyline points="160,174 96,174 96,200 152,200" fill="none" stroke="#8b949e" stroke-width="1.3"/>
    <polygon points="160,200 152,196.5 152,203.5" fill="#8b949e"/>
    <text x="340" y="226" text-anchor="middle" font-size="10.5" fill="#5b6570">④ 用户点了筛选 → 回到 ①</text>
    <text x="16" y="260" font-size="10.5" fill="#8b949e">注意 ③ 是所有前端 bug 的高发区：数据拿到了，但渲染用的结构假设错了。排查从 Network 面板看原始 JSON 开始。</text>
  </g>
</svg>
<figcaption><b>图 8 |</b> 一次数据往返。真正的前端工作有相当一部分是「①到③之间的差错定位」——
请求有没有发出（Network 面板）、返回的是什么形状（看原始响应）、解析后有没有落到 DOM 上（Elements 面板）。</figcaption>
</figure>

<h3>7.1 请求与响应是什么</h3>

<table>
  <thead><tr><th style="width:120px;">部分</th><th>内容</th></tr></thead>
  <tbody>
    <tr><td><b>请求方法</b></td><td><code>GET</code> 取数据、<code>POST</code> 新建、<code>PUT</code>/<code>PATCH</code> 更新、<code>DELETE</code> 删除。</td></tr>
    <tr><td><b>请求头</b></td><td>元信息，如 <code>Content-Type: application/json</code> 声明「我发的是 JSON」。</td></tr>
    <tr><td><b>请求体</b></td><td>只有 POST / PUT 这类才带，内容是字符串（JSON 要先用 <code>JSON.stringify</code> 序列化）。</td></tr>
    <tr><td><b>响应状态码</b></td><td>三位数字，第一位表示类别，见下表。</td></tr>
    <tr><td><b>响应体</b></td><td>返回的数据，通常是 JSON 文本。</td></tr>
  </tbody>
</table>

<table>
  <thead><tr><th style="width:96px;">状态码</th><th>含义</th><th style="width:150px;">你的下一步</th></tr></thead>
  <tbody>
    <tr><td class="num">200</td><td>成功</td><td>解析响应体</td></tr>
    <tr><td class="num">301 / 302</td><td>重定向</td><td>通常不用管，浏览器会自动跟随</td></tr>
    <tr><td class="num">304</td><td>未修改，用缓存</td><td>正常现象，不是错误</td></tr>
    <tr><td class="num">400</td><td>请求格式有误</td><td>检查参数与 JSON 结构</td></tr>
    <tr><td class="num">401 / 403</td><td>未认证 / 无权限</td><td>检查登录状态与凭据</td></tr>
    <tr><td class="num">404</td><td>路径不存在</td><td>检查 URL，注意相对路径的基准点</td></tr>
    <tr><td class="num">500</td><td>服务器内部错误</td><td>不是前端问题，去看服务端日志</td></tr>
  </tbody>
</table>

<h3>7.2 fetch：唯一的请求入口</h3>

<pre><code><span class="cm">// GET 取数据</span>
async function getRows(sex) {
  const res = await fetch(`/api/rows?sex=${encodeURIComponent(sex)}`);
  <span class="cm">// 关键：4xx / 5xx 不会让 fetch 抛错，必须自己检查 ok</span>
  if (!res.ok) throw new Error(`请求失败：HTTP ${res.status}`);
  return res.json();
}
<span class="cm">// POST 提交 JSON</span>
async function saveRow(payload) {
  const res = await fetch('/api/rows', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },   <span class="cm">// 不写这行，后端多半收不到内容</span>
    body: JSON.stringify(payload),                     <span class="cm">// body 只能是字符串</span>
  });
  if (!res.ok) throw new Error(`保存失败：HTTP ${res.status}`);
  return res.json();
}</code></pre>

<div class="box finding">
  <span class="t">fetch 只在网络层失败时抛错</span>
  <p>服务器返回 404 或 500，<code>fetch</code> 本身<b>不会</b> reject，你会在 <code>res.ok</code> 为 <code>false</code> 的情况下
  继续往下解析一个错误页面的响应体。这是「明明接口报错了，页面却显示成功」的最常见原因。
  <b>规范</b>行为如此，所以每个请求后面都要跟一行 <code>if (!res.ok) throw ...</code>。</p>
</div>

<h3>7.3 CORS：为什么本地打开 HTML 会报错</h3>

<p>浏览器有一条<b>同源策略</b>：只有当协议、主机、端口三者完全相同，才允许读取对方的响应。
<code>file:///C:/note.html</code> 打开的页面没有正常的源，它发出的请求会被浏览器拦下。</p>

<table>
  <thead><tr><th style="width:200px;">现象</th><th>原因与解法</th></tr></thead>
  <tbody>
    <tr><td>双击 HTML 打开，<code>fetch</code> 一律报 CORS 错误</td><td>页面来自 <code>file://</code>，没有合法的源。解法：起一个本地服务，例如在目录下运行 <code>python -m http.server 8000</code>，然后访问 <code>http://localhost:8000</code>。</td></tr>
    <tr><td>请求本地服务成功，请求别的域名失败</td><td>跨源了，需要服务端在响应里加 CORS 头（如 <code>Access-Control-Allow-Origin</code>）。前端改代码解决不了。</td></tr>
    <tr><td>Network 里看到请求，但仍报 CORS 错误</td><td>这恰恰说明<b>CORS 是浏览器在拦你，不是服务器拒绝了你</b> —— 请求确实发出去了，服务端日志里能看到。分清这一点能省下大量排查时间。</td></tr>
    <tr><td>需带 Cookie 的跨源请求，额外多一个 OPTIONS 请求</td><td>这是预检（preflight），浏览器先问服务器允不允许。属于正常流程。</td></tr>
  </tbody>
</table>

<h3>7.4 和你的现有工具对照</h3>

<table>
  <thead><tr><th style="width:150px;">意图</th><th>R</th><th>Python</th><th>JavaScript</th></tr></thead>
  <tbody>
    <tr><td>GET 取数据</td><td><code>httr::GET(url)</code></td><td><code>requests.get(url)</code></td><td><code>await fetch(url)</code></td></tr>
    <tr><td>POST 提交 JSON</td><td><code>httr::POST(body = ...)</code></td><td><code>requests.post(url, json = p)</code></td><td>见 §7.2 第二个片段</td></tr>
    <tr><td>解析 JSON</td><td><code>jsonlite::fromJSON()</code></td><td><code>r.json()</code></td><td><code>await res.json()</code></td></tr>
    <tr><td>URL 编码参数</td><td>参数自动编码</td><td>参数自动编码</td><td>要自己写 <code>encodeURIComponent()</code></td></tr>
    <tr><td>检查请求是否成功</td><td>返回状态码需自取</td><td><code>r.raise_for_status()</code></td><td><code>if (!res.ok) throw ...</code></td></tr>
  </tbody>
</table>

<h3>7.5 数据放在浏览器哪里</h3>

<table>
  <thead><tr><th style="width:170px;">方式</th><th>适合</th><th>限制</th></tr></thead>
  <tbody>
    <tr><td><code>localStorage</code></td><td>记住用户的筛选条件、折叠状态这类小配置</td><td>只能存字符串（对象要 <code>JSON.stringify</code>）；同源隔离；不要放敏感数据</td></tr>
    <tr><td>内存变量</td><td>页面当前显示的这份数据</td><td>刷新即丢失</td></tr>
    <tr><td><code>&lt;input type="file"&gt;</code></td><td>让用户选本地 CSV 直接在浏览器里处理，不上传</td><td>需要用户手动选择；只能用 <code>FileReader</code> 或 <code>file.text()</code> 读</td></tr>
    <tr><td>Cookie</td><td>登录凭据（由后端设置）</td><td>每次请求都会带上，容量小，前端一般不直接写</td></tr>
  </tbody>
</table>

<!-- ============================================================ -->
<h2><span class="n">8</span>工程化：依赖、构建与部署</h2>
<p class="lede">从「我电脑上能打开」到「别人点开链接就能用」，中间差的就是这一层。</p>

<p>前面七节的代码都可以「写完双击打开」，但真实项目很快就会遇到三件原生浏览器解决不了的事：
依赖包怎么管、多文件怎么组织、TypeScript 浏览器不认。工程化这一层就是为这三件事存在的。
<b>入门阶段的策略是：先做出一个纯 HTML/CSS/JS 的页面并成功部署，再回来加工具</b> ——
否则你会把「工具配置问题」误当成「我不会写前端」。</p>

<h3>8.1 为什么需要构建</h3>

<table>
  <thead><tr><th style="width:220px;">浏览器原生不支持</th><th>构建工具做的事</th></tr></thead>
  <tbody>
    <tr><td>裸模块导入 <code>import x from 'pkg'</code></td><td>把依赖解析出来并合进最终文件（打包，bundling）</td></tr>
    <tr><td>TypeScript（<code>.ts</code> 文件）</td><td>类型检查并编译成普通 JavaScript</td></tr>
    <tr><td>JSX（<code>&lt;Card /&gt;</code> 这种语法）</td><td>编译成创建元素的函数调用</td></tr>
    <tr><td>新版语法、CSS 预处理器</td><td>转译成目标浏览器支持的写法</td></tr>
  </tbody>
</table>

<figure>
<svg viewBox="0 0 680 202" role="img" aria-label="前端工具链流程图：源码经本地开发服务与构建，产出静态文件后部署到托管服务">
  <g font-family="-apple-system,BlinkMacSystemFont,'Segoe UI','PingFang SC','Microsoft YaHei',Helvetica,Arial,sans-serif">
    <rect x="6" y="30" width="98" height="54" rx="4" fill="#f7f8f9" stroke="#dfe5ea"/>
    <text x="55" y="52" text-anchor="middle" font-size="10.5" font-weight="700" fill="#17181a">你的源码</text>
    <text x="55" y="70" text-anchor="middle" font-size="9.5" fill="#5b6570">HTML/CSS/JS/TS</text>
    <rect x="120" y="30" width="98" height="54" rx="4" fill="#eef3f8" stroke="#1b4f8a"/>
    <text x="169" y="52" text-anchor="middle" font-size="10.5" font-weight="700" fill="#1b4f8a">本地服务</text>
    <text x="169" y="70" text-anchor="middle" font-size="9.5" fill="#17181a">改完立即刷新</text>
    <rect x="234" y="30" width="98" height="54" rx="4" fill="#eef3f8" stroke="#1b4f8a"/>
    <text x="283" y="52" text-anchor="middle" font-size="10.5" font-weight="700" fill="#1b4f8a">构建 build</text>
    <text x="283" y="70" text-anchor="middle" font-size="9.5" fill="#17181a">合并、转译、压缩</text>
    <rect x="348" y="30" width="98" height="54" rx="4" fill="#f7f8f9" stroke="#dfe5ea"/>
    <text x="397" y="52" text-anchor="middle" font-size="10.5" font-weight="700" fill="#17181a">dist 产物</text>
    <text x="397" y="70" text-anchor="middle" font-size="9.5" fill="#5b6570">一堆静态文件</text>
    <rect x="462" y="30" width="98" height="54" rx="4" fill="#f7f8f9" stroke="#dfe5ea"/>
    <text x="511" y="52" text-anchor="middle" font-size="10.5" font-weight="700" fill="#17181a">静态托管</text>
    <text x="511" y="70" text-anchor="middle" font-size="9.5" fill="#5b6570">CDN / 对象存储</text>
    <rect x="576" y="30" width="98" height="54" rx="4" fill="#ffffff" stroke="#c9d2dc"/>
    <text x="625" y="52" text-anchor="middle" font-size="10.5" font-weight="700" fill="#17181a">用户浏览器</text>
    <text x="625" y="70" text-anchor="middle" font-size="9.5" fill="#5b6570">HTTPS 访问</text>
    <line x1="104" y1="57" x2="114" y2="57" stroke="#1b4f8a" stroke-width="1.3"/>
    <polygon points="120,57 113,54 113,60" fill="#1b4f8a"/>
    <line x1="218" y1="57" x2="228" y2="57" stroke="#1b4f8a" stroke-width="1.3"/>
    <polygon points="234,57 227,54 227,60" fill="#1b4f8a"/>
    <line x1="332" y1="57" x2="342" y2="57" stroke="#8b949e" stroke-width="1.3"/>
    <polygon points="348,57 341,54 341,60" fill="#8b949e"/>
    <line x1="446" y1="57" x2="456" y2="57" stroke="#8b949e" stroke-width="1.3"/>
    <polygon points="462,57 455,54 455,60" fill="#8b949e"/>
    <line x1="560" y1="57" x2="570" y2="57" stroke="#8b949e" stroke-width="1.3"/>
    <polygon points="576,57 569,54 569,60" fill="#8b949e"/>
    <line x1="6" y1="100" x2="332" y2="100" stroke="#c9d2dc" stroke-width="1"/>
    <line x1="6" y1="100" x2="6" y2="106" stroke="#c9d2dc" stroke-width="1"/>
    <line x1="332" y1="100" x2="332" y2="106" stroke="#c9d2dc" stroke-width="1"/>
    <text x="169" y="122" text-anchor="middle" font-size="10" fill="#1b4f8a">开发时：只在你电脑上跑</text>
    <line x1="348" y1="100" x2="674" y2="100" stroke="#c9d2dc" stroke-width="1"/>
    <line x1="348" y1="100" x2="348" y2="106" stroke="#c9d2dc" stroke-width="1"/>
    <line x1="674" y1="100" x2="674" y2="106" stroke="#c9d2dc" stroke-width="1"/>
    <text x="511" y="122" text-anchor="middle" font-size="10" fill="#5b6570">上线时：产物与源码无关，浏览器只认它</text>
    <text x="6" y="158" font-size="10.5" fill="#8b949e">入门阶段实际只需要记住两条命令：npm run dev（开发预览）与 npm run build（出产物）。</text>
    <text x="6" y="180" font-size="10.5" fill="#8b949e">dist 里全是静态文件 —— 这意味着部署不需要服务器，任何静态托管都能放（§8.5）。</text>
  </g>
</svg>
<figcaption><b>图 9 |</b> 工具链的两段。左边的三个框只在你的开发机上存在，右边的三个框是用户能接触到的一切。
分不清这两段，就会出现「本地改好了但线上没变」的困惑 —— 因为线上跑的是 <code>dist</code>，不是源码。</figcaption>
</figure>

<h3>8.2 npm 与 package.json</h3>

<table>
  <thead><tr><th style="width:250px;">命令</th><th>作用</th></tr></thead>
  <tbody>
    <tr><td><code>npm init -y</code></td><td>生成 <code>package.json</code>，记录项目信息与依赖清单</td></tr>
    <tr><td><code>npm install 包名</code></td><td>装一个运行时要用的依赖</td></tr>
    <tr><td><code>npm install -D 包名</code></td><td>装一个只在开发时用的依赖（构建工具、检查工具）</td></tr>
    <tr><td><code>npm run 脚本名</code></td><td>执行 <code>package.json</code> 里 <code>scripts</code> 定义的命令</td></tr>
    <tr><td><code>npx 工具名</code></td><td>临时执行一个包，不装进项目</td></tr>
  </tbody>
</table>

<p><code>package.json</code> 里的版本号（如 <code>"vite": "^7.0.0"</code>）遵循语义化版本 <b>主.次.补丁</b>：
主版本号变化表示可能不兼容，补丁号变化表示只是修 bug。<code>^</code> 表示允许升级到同一主版本内的最新版。
依赖目录 <code>node_modules</code> 与锁文件 <code>package-lock.json</code> 一起进版本库控制，
<b>但 <code>node_modules</code> 本身不要提交</b>（它体积大且可由锁文件还原）。</p>

<h3>8.3 开发与构建</h3>

<pre><code><span class="cm">// package.json 里最常改的一段</span>
{
  <span class="mk">"scripts"</span>: {
    <span class="mk">"dev"</span>:   <span class="mk">"vite"</span>,            <span class="cm">// 起本地服务，改文件自动刷新</span>
    <span class="mk">"build"</span>: <span class="mk">"vite build"</span>,      <span class="cm">// 产出可部署的 dist 目录</span>
    <span class="mk">"preview"</span>: <span class="mk">"vite preview"</span>   <span class="cm">// 本地预览 build 的结果（部署前的最后一关）</span>
  }
}</code></pre>

<div class="box">
  <span class="t">部署前一定要跑一次 preview</span>
  <p><code>dev</code> 服务会做一些「贴心」的处理（路径重写、模块即时编译），这些问题在 <code>build</code> 之后才暴露。
  如果 <code>dev</code> 里一切正常、上线却是白屏，第一步就是在本地跑 <code>npm run preview</code>，
  通常立刻能看到真正的原因（最常见的是「绝对路径写成了相对路径」）。</p>
</div>

<h3>8.4 TypeScript 值不值得</h3>

<table>
  <thead><tr><th style="width:230px;">收益</th><th>成本</th></tr></thead>
  <tbody>
    <tr><td>在编辑器里就发现类型错误，而不是等运行时白屏</td><td>需要写类型标注，前期代码量增加约三分之一</td></tr>
    <tr><td>接口返回的数据结构有据可依，减少「字段名猜错」</td><td>需要理解泛型、联合类型等概念</td></tr>
    <tr><td>重构时可信度高：改名、改结构后编辑器会指出所有受影响处</td><td>第三方库的类型定义质量参差，偶尔要写额外声明</td></tr>
  </tbody>
</table>

<p><b>建议</b>：第一个页面不要用；第二个页面开始，如果你已经会写基本类型标注，就值得上。
对数据背景的人而言，TypeScript 的收益往往比一般前端更高 —— 因为你本来就习惯先想清楚字段是什么类型再动手。</p>

<h3>8.5 部署：把文件放到网上</h3>

<table>
  <thead><tr><th style="width:200px;">方式</th><th>适合</th><th>要点</th></tr></thead>
  <tbody>
    <tr><td>GitHub Pages</td><td>个人项目、演示页</td><td>把 <code>dist</code> 推到指定分支并开启 Pages；免费且自带 HTTPS；子路径部署时注意资源路径</td></tr>
    <tr><td>对象存储 + CDN</td><td>正式一点的站点</td><td>上传 <code>dist</code>，绑定域名与证书；需要了解缓存刷新</td></tr>
    <tr><td>平台托管（自动构建）</td><td>想省心</td><td>连上代码仓库，push 即自动构建部署；本质是把图 9 的后半段交给平台</td></tr>
  </tbody>
</table>

<h3>8.6 入门期的工具取舍</h3>

<table>
  <thead><tr><th style="width:280px;">工具</th><th style="width:110px;">什么时候需要</th><th>理由</th></tr></thead>
  <tbody>
    <tr><td>编辑器 + 浏览器</td><td><span class="pill ok">第一天</span></td><td>真的够了。VS Code 与浏览器开发者工具是全部必需</td></tr>
    <tr><td>Git</td><td><span class="pill ok">第一天</span></td><td>不是为了协作，是为了「改坏了能退回去」</td></tr>
    <tr><td>本地 HTTP 服务</td><td><span class="pill ok">第一天</span></td><td>写第一个 <code>fetch</code> 就需要，见 §7.3</td></tr>
    <tr><td>npm + 构建工具</td><td><span class="pill cav">第二个项目</span></td><td>有了多文件、要用包的时候再上</td></tr>
    <tr><td>TypeScript</td><td><span class="pill cav">会写基本类型后</span></td><td>见 §8.4</td></tr>
    <tr><td>代码检查与格式化工具</td><td><span class="pill cav">有协作者时</span></td><td>一个人写代码时，风格统一收益有限</td></tr>
    <tr><td>测试框架、CI、容器</td><td><span class="pill bad">先放下</span></td><td>入门阶段投入产出比最低的部分</td></tr>
  </tbody>
</table>

<!-- ============================================================ -->
<h2><span class="n">9</span>框架：什么时候才需要 React / Vue</h2>
<p class="lede">框架不是进阶必修课，而是特定问题出现之后才值得引入的工具。</p>

<p>框架要解决的唯一问题是：<b>当数据变化时，让界面跟着变</b>。这个问题在原生写法里之所以麻烦，
是因为「数据」和「页面」是两份需要你手工同步的状态 —— 你改了数组，忘了更新表格，界面就与数据不一致了。
在数据类页面上这个矛盾尤其突出：筛选条件一多，需要手工同步的地方就成倍增长。</p>

<pre><code><span class="cm">// 原生写法：数据与界面各改一次，漏一处就不一致</span>
let rows = allRows;
function applyFilters() {
  rows = allRows.filter(r =&gt; r.age &gt;= minAge);   <span class="cm">// (1) 改数据</span>
  renderTable(rows);                              <span class="cm">// (2) 别忘了重画表格</span>
  renderCount(rows.length);                       <span class="cm">// (3) 别忘了同步计数</span>
  renderChart(rows);                              <span class="cm">// (4) 别忘了同步图</span>
}</code></pre>

<p>框架的答案是<b>声明式</b>：你只描述「界面是数据的什么函数」，数据一变，框架负责找出要更新的部分。
这个转变就是从「命令式操作 DOM」变成「描述结果长什么样」。</p>

<table>
  <thead><tr><th style="width:150px;">概念</th><th>含义</th></tr></thead>
  <tbody>
    <tr><td><b>组件</b></td><td>把「一段 HTML + 它的样式 + 它的逻辑」合成一个可复用的单元，例如 <code>&lt;ResultTable rows={rows} /&gt;</code>。</td></tr>
    <tr><td><b>props</b></td><td>父组件传给子组件的数据，只读。相当于函数参数。</td></tr>
    <tr><td><b>state</b></td><td>组件自己拥有的、会变化的数据。变化后触发重渲染。</td></tr>
    <tr><td><b>单向数据流</b></td><td>数据从上往下传，事件从下往上发。避免「谁改了这块数据」变成无解问题。</td></tr>
  </tbody>
</table>

<table>
  <thead><tr><th style="width:300px;">你的情况</th><th style="width:130px;">结论</th><th>说明</th></tr></thead>
  <tbody>
    <tr><td>一个统计报告页，展示若干张表与图，基本无交互</td><td><span class="pill ok">不要</span></td><td>纯 HTML/CSS 加一点 JS 就够，加载更快、问题更少</td></tr>
    <tr><td>有筛选、排序、分页，但都在同一个页面上</td><td><span class="pill cav">可选</span></td><td>原生写法能撑住，要注意把「改数据 + 重渲染」收进同一个函数（如上例）</td></tr>
    <tr><td>多视图切换、表单联动、列表里每一项都有局部状态</td><td><span class="pill bad">该上了</span></td><td>手工同步的复杂度开始失控，框架的收益会明显超过学习成本</td></tr>
    <tr><td>需要多人协作、页面会持续迭代几个月</td><td><span class="pill bad">该上了</span></td><td>组件的边界就是团队分工的边界</td></tr>
  </tbody>
</table>

<div class="box note">
  <span class="t">给数据背景读者的一条捷径</span>
  <p>如果你的目标是「把分析结果做成一个可看的页面」，那么最高效的路线通常是：
  <b>用 R 或 Python 把数据整理好、导出成 JSON 或 CSV，再用纯 HTML/CSS/JS 做一个静态展示页</b>。
  这样前端只需要负责展示，不需要负责计算 —— 你已有的工具承担了它最擅长的部分，
  而框架此时带来的复杂度是纯粹的负担。等展示层真的复杂到需要状态管理，再引入也不迟。</p>
</div>

<!-- ============================================================ -->
<h2><span class="n">10</span>学习路径与阶段验收</h2>
<p class="lede">每个阶段都必须产出一个能给别人看的东西，否则无法判断自己是否真的学会了。</p>

<figure>
<svg viewBox="0 0 680 312" role="img" aria-label="前端学习路径阶梯图：从环境准备到工程与交付共五个阶段">
  <g font-family="-apple-system,BlinkMacSystemFont,'Segoe UI','PingFang SC','Microsoft YaHei',Helvetica,Arial,sans-serif">
    <line x1="8" y1="300" x2="656" y2="300" stroke="#d8dde3" stroke-width="1"/>
    <polygon points="664,300 655,296.5 655,303.5" fill="#d8dde3"/>
    <text x="332" y="292" text-anchor="middle" font-size="10" fill="#8b949e">累积投入 →</text>
    <rect x="8" y="238" width="104" height="46" rx="4" fill="#f7f8f9" stroke="#dfe5ea"/>
    <text x="60" y="256" text-anchor="middle" font-size="11" font-weight="700" fill="#17181a">阶段 0</text>
    <text x="60" y="273" text-anchor="middle" font-size="9.5" fill="#5b6570">环境与工具</text>
    <rect x="148" y="190" width="104" height="46" rx="4" fill="#ffffff" stroke="#c9d2dc"/>
    <text x="200" y="208" text-anchor="middle" font-size="11" font-weight="700" fill="#17181a">阶段 1</text>
    <text x="200" y="225" text-anchor="middle" font-size="9.5" fill="#5b6570">HTML + CSS</text>
    <rect x="288" y="142" width="104" height="46" rx="4" fill="#ffffff" stroke="#c9d2dc"/>
    <text x="340" y="160" text-anchor="middle" font-size="11" font-weight="700" fill="#17181a">阶段 2</text>
    <text x="340" y="177" text-anchor="middle" font-size="9.5" fill="#5b6570">JavaScript</text>
    <rect x="428" y="94" width="104" height="46" rx="4" fill="#eef3f8" stroke="#1b4f8a"/>
    <text x="480" y="112" text-anchor="middle" font-size="11" font-weight="700" fill="#1b4f8a">阶段 3</text>
    <text x="480" y="129" text-anchor="middle" font-size="9.5" fill="#17181a">数据接通</text>
    <rect x="568" y="46" width="104" height="46" rx="4" fill="#eef3f8" stroke="#1b4f8a"/>
    <text x="620" y="64" text-anchor="middle" font-size="11" font-weight="700" fill="#1b4f8a">阶段 4</text>
    <text x="620" y="81" text-anchor="middle" font-size="9.5" fill="#17181a">工程与交付</text>
    <line x1="112" y1="261" x2="140" y2="224" stroke="#1b4f8a" stroke-width="1.3"/>
    <polygon points="144,219 137,221 141,226" fill="#1b4f8a"/>
    <line x1="252" y1="213" x2="280" y2="176" stroke="#1b4f8a" stroke-width="1.3"/>
    <polygon points="284,171 277,173 281,178" fill="#1b4f8a"/>
    <line x1="392" y1="165" x2="420" y2="128" stroke="#1b4f8a" stroke-width="1.3"/>
    <polygon points="424,123 417,125 421,130" fill="#1b4f8a"/>
    <line x1="532" y1="117" x2="560" y2="80" stroke="#1b4f8a" stroke-width="1.3"/>
    <polygon points="564,75 557,77 561,82" fill="#1b4f8a"/>
  </g>
</svg>
<figcaption><b>图 10 |</b> 五个阶段。阶梯的用意是强调<b>顺序</b>：阶段 1 与阶段 2 是地基，跳过它们直接进阶段 4，
会遇到「工具链报错看不懂、样式不对查不出」的双重困境。每一阶段的具体目标与验收产物见下表。</figcaption>
</figure>

<h3>10.1 阶段目标与验收</h3>

<table>
  <thead><tr><th style="width:80px;">阶段</th><th style="width:170px;">必须掌握</th><th style="width:180px;">验收产物</th><th>常见卡点</th></tr></thead>
  <tbody>
    <tr>
      <td><b>0 环境</b></td>
      <td>编辑器、浏览器开发者工具、Git 基本操作、本地起服务</td>
      <td>一个能双击打开的 HTML 页面；一个能通过 <code>http://localhost</code> 访问的目录</td>
      <td>不知道「文件放在哪」；路径写错导致图片与 CSS 加载不出来。用相对路径并注意大小写。</td>
    </tr>
    <tr>
      <td><b>1 结构<br>与表现</b></td>
      <td>语义标签、表单与 label、盒模型、选择器与特异性、Flex、Grid、媒体查询</td>
      <td>一个「统计结果一览页」：含表头区、筛选表单、数据表、页脚，在窄屏下自动重排</td>
      <td>布局卡在居中与对齐上。先把目标拆成「一维还是二维」（图 4），再选机制；用开发者工具量数值而不是猜。</td>
    </tr>
    <tr>
      <td><b>2 行为</b></td>
      <td>类型与 <code>===</code>、数组三件套、函数与作用域、DOM 增删改、事件委托、<code>async/await</code></td>
      <td>把一份固定数据渲染成表格；点表头能按该列排序；有筛选控件且界面与数据始终一致</td>
      <td>「数据改了界面没变」——绝大多数是忘了重新渲染，或者变量作用域搞错。用 <code>console.log</code> 检查数据，用 Elements 面板检查 DOM。</td>
    </tr>
    <tr>
      <td><b>3 数据接通</b></td>
      <td>HTTP 方法与状态码、<code>fetch</code> 与 <code>res.ok</code>、JSON 解析、同源与 CORS</td>
      <td>页面从后端接口或本地 JSON 取数据并渲染；能处理加载中、失败、空数据三种状态</td>
      <td>CORS 报错与路径错误。记住：Network 面板里能看到请求就说明是浏览器拦的，不是服务器拒的。</td>
    </tr>
    <tr>
      <td><b>4 工程与交付</b></td>
      <td>npm 与 <code>package.json</code>、构建与 <code>dist</code>、部署、缓存与 HTTPS 的基本概念</td>
      <td>一个公网可访问的网址，并且你能说清楚它是由哪次 <code>build</code> 产出的</td>
      <td>「本地好、线上白」。先跑 <code>preview</code>，再查资源路径与大小写。</td>
    </tr>
  </tbody>
</table>

<h3>10.2 资料的使用顺序</h3>

<table>
  <thead><tr><th style="width:180px;">资料</th><th>怎么用</th></tr></thead>
  <tbody>
    <tr><td>MDN（权威参考）</td><td>遇到某个属性或方法不确定时的第一查询处。查「这个属性有哪些取值」比查教程可靠得多。</td></tr>
    <tr><td>HTML / ECMAScript 规范</td><td>只在需要确认「这到底是不是规定行为」时看，例如 <code>==</code> 的转换规则、<code>defer</code> 的执行顺序。</td></tr>
    <tr><td>框架官方文档</td><td>决定使用框架之后再读，按官方入门教程走一遍，不要先看二手教程。</td></tr>
    <tr><td>视频教程</td><td>适合建立第一印象；细节与最新用法一律回到官方文档核对。</td></tr>
  </tbody>
</table>

<div class="box">
  <span class="t">三条效率建议</span>
  <p><b>(1)</b> 每学一个概念，立刻用它改一遍自己的页面 —— 脱离项目学的知识留存率极低。
  <b>(2)</b> 遇到报错先读报错信息本身，再搜索；报错信息里通常已经给出了类型不对或属性不存在。
  <b>(3)</b> 不要同时学两件新东西（比如「一边学 JS 一边学 React」），把变量控制成一个。</p>
</div>

<!-- ============================================================ -->
<h2><span class="n">11</span>排错手册</h2>
<p class="lede">把「现象」直接映射到「最可能的三个原因」，比从原理推起更快。</p>

<table>
  <thead><tr><th style="width:210px;">症状</th><th style="width:250px;">最可能的原因</th><th>第一步动作</th></tr></thead>
  <tbody>
    <tr><td>整页白屏</td><td>JS 在解析阶段就抛错，中断了后续渲染</td><td>打开 Console 看第一条红色报错，通常就在这一条上</td></tr>
    <tr><td>页面能显示，但样式全没了</td><td>CSS 文件没加载成功（路径错）或选择器没匹配</td><td>Network 面板看 CSS 请求是否为 404；再看 Elements 里的样式列表</td></tr>
    <tr><td>改了 CSS，页面没变化</td><td>被更高优先级规则覆盖，或浏览器缓存了旧文件</td><td>样式面板看是否有删除线；强制刷新（<kbd>Ctrl</kbd>+<kbd>F5</kbd>）</td></tr>
    <tr><td>图片显示成破图</td><td>路径错、文件名大小写不符、或文件没一起部署</td><td>Network 面板看该图片的请求状态码</td></tr>
    <tr><td>点击没有反应</td><td>元素没被选到、事件绑在了会被替换的节点上、或报错中断</td><td>先在监听里打一行 <code>console.log</code>，确认回调有没有执行</td></tr>
    <tr><td>数据没出来</td><td><code>fetch</code> 失败、字段名与接口不一致、或忘了 <code>await</code></td><td>Network 面板看原始响应内容，逐字核对字段名</td></tr>
    <tr><td>数字算出来不对</td><td>拿到的是字符串（<code>'57.3'</code>）而不是数字</td><td><code>console.log(typeof v, v)</code>，必要时 <code>Number(v)</code></td></tr>
    <tr><td>本地正常，线上白屏</td><td>资源路径是绝对路径、文件名大小写不符（Linux 服务器区分大小写）</td><td>本地跑 <code>npm run preview</code>，再看控制台</td></tr>
    <tr><td>排序结果很奇怪</td><td><code>sort</code> 默认按字符串比较</td><td>补上比较函数 <code>(a, b) =&gt; a - b</code>，并注意它会改原数组</td></tr>
  </tbody>
</table>

<h3>11.1 通用的三步定位法</h3>

<ol>
  <li><b>先分域。</b>是数据错了，还是渲染错了？在 Console 里把数据 <code>console.log</code> 出来，
  在 Elements 里看 DOM 是什么样。两者一比就知道该往哪边查。</li>
  <li><b>再二分。</b>在可疑区间中间打一行日志或注释掉一半代码，看问题还在不在。这比从头读代码快得多，
  而且不会漏掉自己「以为对」的地方。</li>
  <li><b>最后读报错原文。</b>报错信息通常已经给出了文件和原因，逐字读完再搜索，
  搜索时带上「关键字 + 你用的具体技术名」，而不是整段描述。</li>
</ol>

<!-- ============================================================ -->
<h2><span class="n">12</span>结课项目：一份统计结果的展示页</h2>
<p class="lede">把前十一节串成一个能拿去用的东西。目标产物：一个网址，打开后能看到可筛选、可排序的结果表。</p>

<figure>
<svg viewBox="0 0 680 202" role="img" aria-label="结课项目的数据流：从 CSV 文件到上线部署的六个步骤">
  <g font-family="-apple-system,BlinkMacSystemFont,'Segoe UI','PingFang SC','Microsoft YaHei',Helvetica,Arial,sans-serif">
    <rect x="11" y="46" width="98" height="56" rx="4" fill="#f7f8f9" stroke="#dfe5ea"/>
    <text x="60" y="68" text-anchor="middle" font-size="10.5" font-weight="700" fill="#17181a">数据文件</text>
    <text x="60" y="86" text-anchor="middle" font-size="9.5" fill="#5b6570">R/Python 导出的 CSV</text>
    <rect x="123" y="46" width="98" height="56" rx="4" fill="#ffffff" stroke="#c9d2dc"/>
    <text x="172" y="68" text-anchor="middle" font-size="10.5" font-weight="700" fill="#17181a">fetch 载入</text>
    <text x="172" y="86" text-anchor="middle" font-size="9.5" fill="#5b6570">需要本地服务</text>
    <rect x="235" y="46" width="98" height="56" rx="4" fill="#ffffff" stroke="#c9d2dc"/>
    <text x="284" y="68" text-anchor="middle" font-size="10.5" font-weight="700" fill="#17181a">解析</text>
    <text x="284" y="86" text-anchor="middle" font-size="9.5" fill="#5b6570">转为对象数组</text>
    <rect x="347" y="46" width="98" height="56" rx="4" fill="#ffffff" stroke="#c9d2dc"/>
    <text x="396" y="68" text-anchor="middle" font-size="10.5" font-weight="700" fill="#17181a">筛选排序</text>
    <text x="396" y="86" text-anchor="middle" font-size="9.5" fill="#5b6570">filter / sort</text>
    <rect x="459" y="46" width="98" height="56" rx="4" fill="#eef3f8" stroke="#1b4f8a"/>
    <text x="508" y="68" text-anchor="middle" font-size="10.5" font-weight="700" fill="#1b4f8a">渲染</text>
    <text x="508" y="86" text-anchor="middle" font-size="9.5" fill="#17181a">表格 + 条形</text>
    <rect x="571" y="46" width="98" height="56" rx="4" fill="#eef3f8" stroke="#1b4f8a"/>
    <text x="620" y="68" text-anchor="middle" font-size="10.5" font-weight="700" fill="#1b4f8a">部署</text>
    <text x="620" y="86" text-anchor="middle" font-size="9.5" fill="#17181a">静态托管</text>
    <line x1="109" y1="74" x2="117" y2="74" stroke="#1b4f8a" stroke-width="1.3"/>
    <polygon points="123,74 116,71 116,77" fill="#1b4f8a"/>
    <line x1="221" y1="74" x2="229" y2="74" stroke="#1b4f8a" stroke-width="1.3"/>
    <polygon points="235,74 228,71 228,77" fill="#1b4f8a"/>
    <line x1="333" y1="74" x2="341" y2="74" stroke="#1b4f8a" stroke-width="1.3"/>
    <polygon points="347,74 340,71 340,77" fill="#1b4f8a"/>
    <line x1="445" y1="74" x2="453" y2="74" stroke="#1b4f8a" stroke-width="1.3"/>
    <polygon points="459,74 452,71 452,77" fill="#1b4f8a"/>
    <line x1="557" y1="74" x2="565" y2="74" stroke="#1b4f8a" stroke-width="1.3"/>
    <polygon points="571,74 564,71 564,77" fill="#1b4f8a"/>
    <polyline points="396,102 396,132 347,132" fill="none" stroke="#8b949e" stroke-width="1.2" stroke-dasharray="4 3"/>
    <text x="300" y="146" font-size="10" fill="#8b949e">改了筛选条件就回到第 4 步重跑一遍</text>
    <line x1="11" y1="176" x2="445" y2="176" stroke="#c9d2dc" stroke-width="1"/>
    <text x="228" y="192" text-anchor="middle" font-size="10" fill="#5b6570">第 1～4 步全在浏览器里完成，不需要服务器参与计算</text>
    <text x="571" y="192" text-anchor="middle" font-size="10" fill="#1b4f8a">第 6 步之后才有网址</text>
  </g>
</svg>
<figcaption><b>图 11 |</b> 项目数据流。关键设计：<b>计算留在你熟悉的工具里，前端只负责展示</b>。
这样这个页面的复杂度被压到最低，而它已经能解决「把结果发给别人看」这个真实需求。</figcaption>
</figure>

<h3>12.1 目录结构</h3>

<pre><code>result-page/
├── index.html          <span class="cm">页面结构：表头、筛选区、结果表</span>
├── styles.css          <span class="cm">全部样式，先用 grid 搭骨架</span>
├── app.js              <span class="cm">全部行为：载入、筛选、排序、渲染</span>
└── data/
    └── summary.csv     <span class="cm">由 R / Python / SAS 导出的结果，前端只读不改</span></code></pre>

<h3>12.2 关键代码</h3>

<h4>载入与解析</h4>

<pre><code><span class="cm">// 把 CSV 文本变成对象数组。列名来自第一行，一行数据就是一个对象。</span>
async function loadCsv(path) {
  const res = await fetch(path);
  if (!res.ok) throw new Error(`载入失败：HTTP ${res.status}`);
  const text = await res.text();
  const [head, ...lines] = text.trim().split(/\r?\n/);
  const cols = head.split(',');
  return lines.map((line) =&gt;
    Object.fromEntries(cols.map((c, i) =&gt; [c, line.split(',')[i]]))
  );
}
<span class="cm">// 注意：这种写法只适用于「字段内没有逗号」的规整文件。</span>
<span class="cm">// 真实 CSV 可能带引号包裹的逗号，那种情况请在 R / Python 侧先整理干净，</span>
<span class="cm">// 或改用成熟的解析库 —— 不要手写一个能处理所有情况的 CSV 解析器。</span></code></pre>

<h4>筛选、排序、渲染</h4>

<pre><code>let allRows = [];        <span class="cm">// 原始数据，永远不改</span>
let viewRows = [];       <span class="cm">// 当前视图，由筛选与排序算出来</span>
function applyView() {
  const minAge = Number(document.querySelector('#ageMin').value) || 0;
  viewRows = allRows
    .filter(r =&gt; Number(r.age) &gt;= minAge)      <span class="cm">// CSV 里全是字符串，必须转数字</span>
    .sort((a, b) =&gt; Number(b.mean) - Number(a.mean));   <span class="cm">// 一定要给比较函数</span>
  render(viewRows);
  document.querySelector('#count').textContent = `${viewRows.length} 条`;
}
function render(rows) {
  const tbody = document.querySelector('#result tbody');
  tbody.replaceChildren();
  const max = Math.max(...rows.map(r =&gt; Number(r.mean)));
  for (const r of rows) {
    const tr = document.createElement('tr');
    const tdName = document.createElement('td');
    tdName.textContent = r.variable;
    const tdStat = document.createElement('td');
    tdStat.textContent = Number(r.mean).toFixed(1);
    <span class="cm">// 条形：宽度按最大值的比例给，纯 CSS 就够，不需要绘图库</span>
    const tdBar = document.createElement('td');
    const bar = document.createElement('div');
    bar.className = 'bar';
    bar.style.width = `${(Number(r.mean) / max) * 100}%`;
    tdBar.append(bar);
    tr.append(tdName, tdStat, tdBar);
    tbody.append(tr);
  }
}
<span class="cm">// 事件：筛选控件变了就重算视图。整个页面只有这一个同步入口。</span>
document.querySelector('#filter').addEventListener('input', applyView);
loadCsv('data/summary.csv')
  .then(rows =&gt; { allRows = rows; applyView(); })
  .catch(err =&gt; {
    document.querySelector('#result').textContent = `数据载入失败：${err.message}`;
  });</code></pre>

<h4>部署</h4>

<pre><code><span class="cm"># 1. 把整个目录提交到一个 Git 仓库（data 目录一起提交，页面要靠它）</span>
git init &amp;&amp; git add . &amp;&amp; git commit -m <span class="mk">"结果展示页"</span>
<span class="cm"># 2. 推到 GitHub 后，在仓库设置里开启 Pages，指向分支根目录</span>
<span class="cm"># 3. 等一两分钟，得到形如 https://用户名.github.io/仓库名/ 的网址</span>
<span class="cm"># 若使用构建工具：先 npm run build，再部署 dist 目录</span></code></pre>

<div class="box finding">
  <span class="t">这个项目最容易卡住的一步</span>
  <p>直接双击 <code>index.html</code> 打开，<code>fetch('data/summary.csv')</code> 会被浏览器按跨源规则拦下（§7.3）。
  不要怀疑代码，在项目目录里运行 <code>python -m http.server 8000</code>，然后访问
  <code>http://localhost:8000</code> —— 这是每个前端项目都要迈过去的一道门槛：<b>页面必须由一个服务提供，不能靠双击打开</b>。</p>
</div>

<h3>12.3 复用清单</h3>

<ul>
  <li><strong>列名要和数据文件一致。</strong>CSV 的表头就是代码里的字段名，改一处要改两处；建议列名先用 Latin 命名，显示时再换成中文表头。</li>
  <li><strong>所有从文件读来的值都是字符串。</strong>参与比较或计算前一律 <code>Number()</code>，这一条能消掉大半「结果不对」的问题。</li>
  <li><strong>把 <code>allRows</code> 与 <code>viewRows</code> 分开。</strong>筛选永远基于原始数据算，不要在上一次的结果上再筛，否则条件会累加而无法撤销。</li>
  <li><strong><code>sort</code> 先复制再排。</strong>写 <code>[...rows].sort(...)</code>，避免改掉原始数据。</li>
  <li><strong>三种状态都要处理。</strong>加载中、失败、空结果 —— 缺一个，用户就会看到一片空白而不知道发生了什么。</li>
  <li><strong>数值格式化用 <code>toFixed</code>。</strong>统计结果的位数要统一，且注意 <code>toFixed</code> 返回的是字符串。</li>
</ul>

<!-- ============================================================ -->
<h2 class="spn-skip">附录 A · 术语对照</h2>
<p class="lede">按出现频率排序。中英对照是为了让你能搜到准确资料 —— 用中文搜到的往往是二手教程。</p>

<table>
  <thead><tr><th style="width:170px;">英文</th><th style="width:130px;">中文</th><th>一句话</th></tr></thead>
  <tbody>
    <tr><td>DOM</td><td>文档对象模型</td><td>HTML 在浏览器里被解析成的那棵对象树，JS 通过它读写页面</td></tr>
    <tr><td>CSSOM</td><td>CSS 对象模型</td><td>样式规则合成的一张总表，与 DOM 合并成渲染树</td></tr>
    <tr><td>Reflow / Layout</td><td>重排 / 布局</td><td>重新计算盒子的位置与尺寸，代价最高</td></tr>
    <tr><td>Repaint</td><td>重绘</td><td>重新填充像素，不改位置</td></tr>
    <tr><td>Composite</td><td>合成</td><td>把分层结果交给 GPU 合成，改 transform 只走这一步</td></tr>
    <tr><td>Specificity</td><td>特异性</td><td>决定哪条 CSS 规则胜出的权重计数</td></tr>
    <tr><td>Box model</td><td>盒模型</td><td>content / padding / border / margin 四层</td></tr>
    <tr><td>Event loop</td><td>事件循环</td><td>调度「同步代码、微任务、宏任务」的机制</td></tr>
    <tr><td>Microtask / Task</td><td>微任务 / 宏任务</td><td>Promise 回调属微任务，setTimeout 属宏任务；微任务先清空</td></tr>
    <tr><td>Closure</td><td>闭包</td><td>函数记住了定义时所在作用域里的变量</td></tr>
    <tr><td>TDZ</td><td>暂时性死区</td><td><code>let</code> / <code>const</code> 声明前访问会直接报错</td></tr>
    <tr><td>Same-origin policy</td><td>同源策略</td><td>协议、主机、端口三者相同才允许读取响应</td></tr>
    <tr><td>CORS / Preflight</td><td>跨源资源共享 / 预检</td><td>服务端声明允许哪些源；复杂请求前先发 OPTIONS 询问</td></tr>
    <tr><td>Bundling / Build</td><td>打包 / 构建</td><td>把多文件与依赖合成浏览器能直接运行的文件</td></tr>
    <tr><td>Declarative UI</td><td>声明式界面</td><td>描述「界面是数据的什么函数」，由框架负责更新</td></tr>
    <tr><td>XSS</td><td>跨站脚本攻击</td><td>把外部数据当 HTML 执行导致的注入，用 textContent 规避</td></tr>
    <tr><td>a11y</td><td>无障碍</td><td>accessibility 的缩写，让所有人（含辅助技术）都能用</td></tr>
  </tbody>
</table>

<h2 class="spn-skip">附录 B · 参考来源</h2>
<p class="lede">下列链接在 2026-09 逐一验证可访问。规范原文用于确证「规定行为」，MDN 用于日常查询。</p>

<ul>
  <li><b>入门总览</b> — <a href="https://developer.mozilla.org/en-US/docs/Learn_web_development">MDN · Learn web development</a></li>
  <li><b>CSS 层叠与继承</b> — <a href="https://developer.mozilla.org/en-US/docs/Learn_web_development/Core/Styling_basics/Cascade_and_inheritance">MDN · Cascade and inheritance</a></li>
  <li><b>选择器特异性</b> — <a href="https://developer.mozilla.org/en-US/docs/Web/CSS/Specificity">MDN · Specificity</a></li>
  <li><b>盒模型</b> — <a href="https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_box_model/Introduction_to_the_CSS_box_model">MDN · Introduction to the CSS box model</a></li>
  <li><b>事件循环</b> — <a href="https://developer.mozilla.org/en-US/docs/Web/JavaScript/Event_loop">MDN · Event loop</a>；语言规范 <a href="https://tc39.es/ecma262/">ECMAScript Language Specification</a></li>
  <li><b>脚本加载时机</b> — <a href="https://developer.mozilla.org/en-US/docs/Web/HTML/Element/script">MDN · <code>&lt;script&gt;</code>（defer / async）</a>；解析规则见 <a href="https://html.spec.whatwg.org/multipage/dom.html">HTML Standard · DOM</a></li>
  <li><b>关键渲染路径</b> — <a href="https://developer.mozilla.org/en-US/docs/Web/Performance/Critical_rendering_path">MDN · Critical rendering path</a></li>
  <li><b>网络请求</b> — <a href="https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API">MDN · Fetch API</a>；<a href="https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS">MDN · CORS</a></li>
  <li><b>无障碍</b> — <a href="https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA">MDN · ARIA</a></li>
  <li><b>工具与部署</b> — <a href="https://vite.dev/guide/">Vite 官方指南</a>；<a href="https://docs.npmjs.com/about-semantic-versioning">npm · 语义化版本</a>；<a href="https://pages.github.com/">GitHub Pages</a></li>
  <li><b>框架（决定使用后再读）</b> — <a href="https://react.dev/learn">React</a>；<a href="https://vuejs.org/guide/introduction.html">Vue</a></li>
  <li><b>本地运行时</b> — <a href="https://nodejs.org/api/">Node.js API 文档</a></li>
</ul>

<footer>
  <p><b>证据状态。</b>本文标注「实测」的结论来自本机一次运行：脚本 <code>fe-verify.js</code>，运行时 Node v22.22.2，
  仅使用语言内置对象，不涉及 DOM、CSS 或网络。原始输出完整复制于 §5.10，未做删改，仅在两处 NaN 的显示上加了说明。</p>
  <p><b>未执行的部分。</b>CSS 层叠与布局、浏览器渲染路径、脚本加载时机、HTTP 与 CORS 行为均按 MDN 与 WHATWG / ECMAScript
  现行文档陈述，未在本机浏览器中逐步复现；§12 的项目代码为可读的完整片段，但未在浏览器中运行验证，也未部署。
  凡属工程取舍的论断均标注为「惯例」或放入了对比表中，供读者自行判断。</p>
  <p><b>时效。</b>参考链接于 2026-09-19 验证可访问。前端生态变化快，涉及具体版本与工具配置的部分请以官方文档为准。</p>
</footer>
