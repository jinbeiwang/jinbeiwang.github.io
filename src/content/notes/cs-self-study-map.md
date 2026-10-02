---
title: "计算机科学自学地图：从编程语言到操作系统"
summary: "以 csdiy.wiki 的自学路线为底稿，按方向重排成一张总览图：编程语言、数据结构与算法、计算机组成、操作系统、计算机网络、数据库六个主干，每个方向说清学习价值、核心知识点、入门资源，并标出可以继续深入的 topic。原文成文较早，本文按 2026 年现状校对，变化之处均已标注。"
date: 2026-10-02
category: Learning log
tags: [计算机科学, 自学路线, 学习方法, 课程推荐]
lang: zh
---

<div class="meta-row">
    <span><b>读者</b> &nbsp;想系统补齐 CS 基础、但不知道从哪切入、怕走弯路的人</span>
    <span><b>目标</b> &nbsp;建立全貌 + 找到下一步该学哪个方向，不求立刻学完</span>
    <span><b>底稿</b> &nbsp;<a href="https://csdiy.wiki/CS学习规划/">csdiy.wiki · 一个仅供参考的 CS 学习规划</a></span>
    <span><b>校对时点</b> &nbsp;2026-10；原文较旧，变化处标 <span class="pill cav">已更新</span></span>
</div>

<div class="box note" style="margin-top:26px;">
  <span class="t">这篇的定位与边界</span>
  <div class="small">
  <p><b>它是一张地图，不是一本教材。</b>每个方向只给「为什么学、学什么、用哪门课、之后能往哪走」四件事，每件一两段话。
  真正的知识要靠你跟着某门课做完项目才能长出来，看这篇不会让你学会操作系统。</p>
  <p><b>底稿与改动的关系。</b>方向划分与大部分课程推荐沿用 csdiy.wiki（下称「原文」）。本文做了三件事：
  ① 把原文的线性叙述按「方向」重排，方便横向比较；② 每个方向补上「可继续深入的 topic」，原文较散；
  ③ 用 2026-10 的事实校对课程编号与版本，凡有变化都标 <span class="pill cav">已更新</span> 并说明改了什么。</p>
  <p><b>关于资源推荐的性质。</b>下面出现的课程名、教材名都来自原文或各校公开课程页，属于<b>社区共识而非绝对最优</b>。
  同一门课换一门替代课，完全可能更适合你 —— 判断标准在 §8，不在推荐列表本身。</p>
  </div>
</div>

<!-- ============================================================ -->
<h2><span class="n">1</span>先建立全貌：这张地图长什么样</h2>
<p class="lede">在钻进任何一门课之前，先花五分钟看清六个方向之间谁支撑谁。</p>

<p>计算机科学听起来庞杂，但作为「工程师的基础」，真正需要打通的主干其实只有六条。它们之间有明确的依赖关系：
编程语言是你的<b>工具</b>，数据结构与算法是你的<b>方法</b>，剩下四门是你所操作对象的<b>内部构造</b>。
越往下越是「机器怎么工作」，越往上越是「人怎么表达意图」。</p>

<figure>
<svg viewBox="0 0 680 340" role="img" aria-label="计算机科学六个方向的依赖关系图">
  <g font-family="-apple-system,BlinkMacSystemFont,'Segoe UI','PingFang SC','Microsoft YaHei',Helvetica,Arial,sans-serif">
    <text x="24" y="22" font-size="11" font-weight="700" fill="#8b949e">抽象层次：越靠上越接近人的意图，越靠下越接近机器</text>
    <rect x="24" y="34" width="632" height="46" rx="4" fill="#eef3f8" stroke="#1b4f8a" stroke-width="1.5"/>
    <text x="40" y="54" font-size="12" font-weight="700" fill="#1b4f8a">编程语言</text>
    <text x="40" y="71" font-size="10.5" fill="#5b6570">你的工具 · 学会一两种就够起步，重点是「抽象」与「调试」的能力，不是语言数量</text>
    <text x="640" y="62" font-size="10" fill="#1b4f8a" text-anchor="end">§3</text>
    <rect x="24" y="92" width="632" height="46" rx="4" fill="#f0f7f4" stroke="#0f7b5f" stroke-width="1.5"/>
    <text x="40" y="112" font-size="12" font-weight="700" fill="#0f7b5f">数据结构与算法</text>
    <text x="40" y="129" font-size="10.5" fill="#5b6570">你的方法 · 把现实问题转成「可计算」的问题，是几乎所有后续课程的基础</text>
    <text x="640" y="120" font-size="10" fill="#0f7b5f" text-anchor="end">§4</text>
    <line x1="340" y1="138" x2="340" y2="154" stroke="#c9d2dc" stroke-width="1.5"/>
    <text x="352" y="152" font-size="10" fill="#8b949e">往下都是「机器怎么运转」</text>
    <rect x="24" y="160" width="200" height="72" rx="4" fill="#f7f8f9" stroke="#dfe5ea"/>
    <rect x="24" y="160" width="3" height="72" fill="#1b4f8a"/>
    <text x="38" y="180" font-size="11.5" font-weight="700" fill="#17181a">计算机组成</text>
    <text x="38" y="199" font-size="10" fill="#5b6570">从逻辑门到 CPU</text>
    <text x="38" y="215" font-size="10" fill="#5b6570">理解程序如何被执行</text>
    <text x="212" y="200" font-size="10" fill="#1b4f8a" text-anchor="end">§5</text>
    <rect x="240" y="160" width="200" height="72" rx="4" fill="#f7f8f9" stroke="#dfe5ea"/>
    <rect x="240" y="160" width="3" height="72" fill="#1b4f8a"/>
    <text x="254" y="180" font-size="11.5" font-weight="700" fill="#17181a">操作系统</text>
    <text x="254" y="199" font-size="10" fill="#5b6570">进程 / 内存 / 文件</text>
    <text x="254" y="215" font-size="10" fill="#5b6570">资源怎么被分配</text>
    <text x="428" y="200" font-size="10" fill="#1b4f8a" text-anchor="end">§6</text>
    <rect x="456" y="160" width="200" height="72" rx="4" fill="#f7f8f9" stroke="#dfe5ea"/>
    <rect x="456" y="160" width="3" height="72" fill="#1b4f8a"/>
    <text x="470" y="180" font-size="11.5" font-weight="700" fill="#17181a">计算机网络</text>
    <text x="470" y="199" font-size="10" fill="#5b6570">分层与协议</text>
    <text x="470" y="215" font-size="10" fill="#5b6570">两台机器怎么对话</text>
    <text x="644" y="200" font-size="10" fill="#1b4f8a" text-anchor="end">§7</text>
    <line x1="340" y1="232" x2="340" y2="248" stroke="#c9d2dc" stroke-width="1.5"/>
    <rect x="24" y="250" width="632" height="46" rx="4" fill="#f7f8f9" stroke="#dfe5ea"/>
    <rect x="24" y="250" width="3" height="46" fill="#1b4f8a"/>
    <text x="40" y="270" font-size="11.5" font-weight="700" fill="#17181a">数据库系统</text>
    <text x="40" y="287" font-size="10.5" fill="#5b6570">数据的组织与查询 · 上面几门的交汇应用：既要用算法，也要懂存储与并发</text>
    <text x="640" y="280" font-size="10" fill="#1b4f8a" text-anchor="end">§8</text>
    <text x="24" y="322" font-size="10.5" fill="#8b949e">蓝框 = 起点与「工具侧」；绿框 = 全文最重要的地基；灰框 = 「机器侧」的四个方向，彼此耦合，可并行也能按兴趣挑。</text>
  </g>
</svg>
<figcaption><b>图 1 |</b> 六个主干与它们的层次关系。注意两处箭头：向下是根本性的依赖（不懂算法，后面几门课的项目都做不下去），三框之间横向则没有强前后序 —— 先学哪个取决于你的兴趣与目标。</figcaption>
</figure>

<div class="box"><span class="t">怎么用这张图</span><p>如果你完全没开始，走<b>自上而下</b>：先有编程能力，再补算法，然后按兴趣挑一门「机器侧」的方向切入。
如果你已经在工作里写过不少代码，可以<b>横向切入</b>：直接选一个你天天在用、却说不清原理的方向（多半是网络或数据库），
从那里往下挖，动力最足。</p></div>

<div class="box takeaway"><span class="t">本章结论</span><p>六个方向不是六门平行课，而是一棵树：<b>语言与算法是地基，机器侧四门是分支</b>。
不要试图一次全学，先把地基铺好，再挑一条分支走通全程 —— 走通一条比浅尝六条有价值得多。</p></div>


<!-- ============================================================ -->
<h2><span class="n">2</span>开始之前：两件比选课更重要的事</h2>
<p class="lede">原文把「必学工具」放在最前面，这个顺序是对的 —— 但工具里真正要紧的只有两样。</p>

<h3>2.1 学会提问</h3>

<p>原文把它放在第一条，理由值得原样保留：<b>「能自己解决问题」是自学 CS 的核心能力</b>。
遇到问题先尝试自己定位（读报错、查文档、缩小范围），实在解决不了再去社区问；
而问的时候，能把「我做了什么、期望什么、实际什么」说清楚，本身就是一种训练。
原文推荐阅读《提问的智慧》—— 这一点到今天没有变化。</p>

<h3>2.2 命令行与环境</h3>

<p>命令行是唯一一项<b>「不学就处处受阻、学了处处省力」</b>的基础技能。原文推荐的
<a href="https://github.com/jlevy/the-art-of-command-line">The Art of Command Line</a> 和
MIT 的 <b>Missing Semester</b>（6.NULL）仍然是这个领域最好的入门材料。</p>

<div class="box note"><span class="t">相比原文的一个变化</span><p>原文写「翻墙几乎是内地 CSer 的必备技能」，并推荐了一系列自建方案。
几年过去，更省事的做法已经普及：<b>把优质课程直接找国内镜像与公开的中文翻译</b>。
例如 MIT 6.1810、6.5840 都有社区维护的中文课程视频翻译文档，多个 Git 托管服务也提供了可直连的加速入口。
这些不改变「掌握命令行与 Git」的必要性，但确实降低了入门门槛。</p></div>

<div class="box takeaway"><span class="t">本章结论</span><p>在挑课程之前，先花一两周把<b>命令行与 Git</b>用得顺手。这笔投入会在之后每一门课里反复回本，是全文性价比最高的一段。</p></div>


<!-- ============================================================ -->
<h2><span class="n">3</span>方向一：编程语言</h2>
<p class="lede">这是唯一一个「你已经在做、但很可能没做对」的方向。</p>

<h3>3.1 学习价值</h3>

<p>入门课的目标<b>不是学会一门语言，而是建立抽象能力与调试能力</b>。语言随时可以换，语言背后的东西 ——
变量作用域、递归、高阶函数、对象与接口、库的设计 —— 才是能迁移的能力。原文那句
「Languages are tools, you choose the right tool to do the right thing」说到了要害：不存在完美语言。</p>

<h3>3.2 核心知识点</h3>

<table>
  <thead><tr><th style="width:150px;">主题</th><th>要理解到什么程度</th></tr></thead>
  <tbody>
    <tr><td><b>基本控制流</b></td><td>分支、循环、函数定义与调用 —— 这部分不必在入门课上花太多时间。</td></tr>
    <tr><td><b>抽象手段</b></td><td>过程抽象（函数）、数据抽象（对象 / 记录）、控制抽象（高阶函数、递归、生成器）。这是入门课的真正主线。</td></tr>
    <tr><td><b>程序如何被构造</b></td><td>模块化、接口与实现分离、错误处理。为什么大程序必须分层。</td></tr>
    <tr><td><b>调试与测试</b></td><td>读堆栈、二分定位、写最小复现、写测试。这项技能的价值高于任何语法细节。</td></tr>
  </tbody>
</table>

<h3>3.3 入门资源</h3>

<table>
  <thead><tr><th style="width:130px;">语言</th><th>推荐课程 / 材料</th></tr></thead>
  <tbody>
    <tr><td><b>通用入门</b></td><td>Harvard <b>CS50x</b>（This is CS50）—— 覆盖面广、作业扎实，很多人第一次写出链表与哈希表就在这里。MIT <b>Missing Semester</b> 可与之并行。</td></tr>
    <tr><td><b>Python</b></td><td>UCB <b>CS61A</b>（Structure and Interpretation of Computer Programs）—— 以「抽象」为主线讲编程，是原文与社区公认的最佳选择之一。CS50P 与 MIT 6.100L 是更轻的替代。</td></tr>
    <tr><td><b>Java</b></td><td>MIT 6.092 —— 篇幅小，适合只想先跑通一门静态类型语言的人。</td></tr>
    <tr><td><b>C / C++</b></td><td>Stanford <b>CS106B/X</b>（Programming Abstractions）与 <b>CS106L</b>（Standard C++ Programming）—— 后者讲现代 C++ 的写法，质量高。</td></tr>
    <tr><td><b>Rust</b></td><td>Stanford <b>CS110L</b>（Safety in Systems Programming）—— 从系统编程视角切入 Rust，比单纯背语法更有意义。</td></tr>
    <tr><td><b>OCaml</b></td><td>Cornell <b>CS3110</b> —— 想体验函数式编程范式时的首选。</td></tr>
  </tbody>
</table>

<div class="box note"><span class="t">相比原文的一个变化</span><p>原文的 Python 入门还推荐了 <b>MIT 6.100L</b>，这条仍然有效。
需要说明的是 <b>CS61A 的课程编号与内容没有变化</b>（仍是 <em class="ev">CS 61A</em>，Berkeley 每学期开课，官网 <a href="https://cs61a.org/">cs61a.org</a> 持续更新）。
但要注意一个趋势：<b>越来越多学校在入门课里引入 AI 辅助工具的使用规范</b>，作业要求以当学期官网为准，不要照搬旧帖。</p></div>

<h3>3.4 之后可以深入</h3>

<ul>
  <li>编程范式：函数式、面向对象、逻辑式 —— 各写一点真实代码，而不只是知道名词</li>
  <li>类型系统：静态类型、泛型、类型推导（这条正好接上我刚写的 <a href="/notes/ts-primer-note.html">TypeScript 入门</a>）</li>
  <li>程序语言理论：语法与语义、解释器与编译器（后续接编译原理）</li>
</ul>

<div class="box takeaway"><span class="t">本章结论</span><p>选<b>一门</b>入门课做完，比在六门课之间横跳有用得多。判断学没学会的标准很朴素：能不能独立写出一百行以上、有测试、能跑对的小程序。</p></div>


<!-- ============================================================ -->
<h2><span class="n">4</span>方向二：数据结构与算法</h2>
<p class="lede">如果说只能推荐一个方向，是这个。它是所有后续课程的公共前提。</p>

<h3>4.1 学习价值</h3>

<p>原文的定位很准：<b>「如何把实际问题抽象成算法问题，并选用合适的数据结构在时间与内存限制下解决它」</b>，
是算法课的永恒主题。它也是面试与工程实践里复用率最高的知识 —— 你在写 SAS / R / Python 时，
每次纠结「用 hash 还是排序合并」，本质上都是这门课的内容。</p>

<h3>4.2 核心知识点</h3>

<table>
  <thead><tr><th style="width:170px;">板块</th><th>核心内容</th></tr></thead>
  <tbody>
    <tr><td><b>复杂度分析</b></td><td>大 O 记号、常见量级的直觉、均摊分析。这是整门课的「度量衡」。</td></tr>
    <tr><td><b>线性结构</b></td><td>数组、链表、栈、队列、哈希表。重点理解哈希表为什么平均 O(1)、什么情况下退化。</td></tr>
    <tr><td><b>树</b></td><td>二叉树、二叉搜索树、平衡树（红黑树 / B 树）、堆与优先队列。B 树会直接用在数据库中。</td></tr>
    <tr><td><b>图</b></td><td>遍历（BFS / DFS）、最短路径、最小生成树、拓扑排序。</td></tr>
    <tr><td><b>排序与查找</b></td><td>快排、归并、堆排序、基数排序；二分与其变体。</td></tr>
    <tr><td><b>算法设计范式</b></td><td>分治、贪心、动态规划 —— 动态规划是公认的难点，别指望一遍过。</td></tr>
  </tbody>
</table>

<h3>4.3 入门资源</h3>

<table>
  <thead><tr><th style="width:170px;">课程 / 材料</th><th>特点</th></tr></thead>
  <tbody>
    <tr><td><b>UCB CS61B</b></td><td><span class="pill ok">首选</span> 深入浅出，编程实验丰富，用 Java 描述。课程网站按学期开放（如 <a href="https://sp26.datastructur.es/">sp26.datastructur.es</a>）。</td></tr>
    <tr><td><b>Princeton Algorithms I &amp; II</b>（Coursera）</td><td>结构严谨，配套作业质量极高。与 CS61B 二选一即可。</td></tr>
    <tr><td><b>MIT 6.006</b></td><td>偏好 Python 描述时的算法入门课。</td></tr>
    <tr><td><b>Stanford CS106B/X</b></td><td>偏好 C++ 描述时的对应课程。</td></tr>
    <tr><td><b>UCB CS170 / MIT 6.046</b></td><td>进阶：更高级的算法与 NP 问题。做完入门课再碰。</td></tr>
  </tbody>
</table>

<div class="box note"><span class="t">相比原文：这一块基本没有变化</span><p>算法是 CS 里最稳定的知识领域 —— 十年里推荐的课几乎没动过。
唯一值得提醒的是<b>练习方式变了</b>：原文时代主要靠课程作业，现在还有大量在线判题平台可以即时验证。
做完课内作业后，用题库补手感是效率很高的补充。</p></div>

<h3>4.4 之后可以深入</h3>

<ul>
  <li>高级算法与复杂度理论：NP 完全性、近似算法、随机化算法</li>
  <li>字符串算法：KMP、后缀数组、Trie</li>
  <li>竞赛方向：动态规划进阶、图论进阶、数论</li>
  <li>对应的工作场景：性能优化、大规模数据处理（这一条与前文提到的统计编程实际工作直接相关）</li>
</ul>

<div class="box takeaway"><span class="t">本章结论</span><p>这是六个方向里<b>唯一值得「无条件先学」</b>的。哪怕你只想学一门，就从这里开始 —— 它决定了你后面能不能看懂另外四门的项目。</p></div>


<!-- ============================================================ -->
<h2><span class="n">5</span>方向三：计算机组成 / 体系结构</h2>
<p class="lede">回答那个最原始的问题：我写的代码，机器到底是怎么执行的。</p>

<h3>5.1 学习价值</h3>

<p>原文把这一门放在「满足好奇心」的位置上，其实低估了它。它的实际价值有两层：
一是<b>建立从 0/1 到程序的完整链条</b>，之后看任何底层细节都不会觉得神秘；
二是<b>理解性能从哪里来</b> —— 缓存、流水线、并行，这些概念决定了你的程序为什么快或慢。</p>

<h3>5.2 核心知识点</h3>

<table>
  <thead><tr><th style="width:170px;">板块</th><th>核心内容</th></tr></thead>
  <tbody>
    <tr><td><b>数字逻辑</b></td><td>布尔代数、逻辑门、组合逻辑与时序逻辑、寄存器与内存。</td></tr>
    <tr><td><b>指令集与汇编</b></td><td>机器语言、汇编、指令如何被编码。RISC-V 是当前教学主流（Berkeley 是 RISC-V 发源地）。</td></tr>
    <tr><td><b>CPU 内部</b></td><td>取指 — 译码 — 执行 — 访存 — 写回；流水线与冒险。</td></tr>
    <tr><td><b>存储层次</b></td><td>寄存器 / 缓存 / 内存 / 磁盘的容量与延迟差异，局部性原理。</td></tr>
    <tr><td><b>程序与硬件之间</b></td><td>编译、汇编、链接、加载；为什么链接错误那么难查。</td></tr>
  </tbody>
</table>

<h3>5.3 入门资源</h3>

<table>
  <thead><tr><th style="width:190px;">课程 / 材料</th><th>特点</th></tr></thead>
  <tbody>
    <tr><td><b>Nand2Tetris</b></td><td><span class="pill ok">最佳零门槛</span> 从与非门开始，一路造到能跑俄罗斯方块的计算机。覆盖数字电路、汇编、体系结构、编译、虚拟机。原文推荐的 Coursera 版本（Hebrew University of Jerusalem 开设）仍在使用中。</td></tr>
    <tr><td><b>UCB CS61C</b></td><td>本科难度的体系结构课，注重实践，会在项目中手写汇编、搭 CPU。原文推荐的一门。</td></tr>
    <tr><td><b>CMU 15-213</b></td><td>配教材《Computer Systems: A Programmer's Perspective》（CS:APP）。这本书把「程序员视角的系统」讲得极清楚，强烈建议配合阅读。</td></tr>
  </tbody>
</table>

<div class="box note"><span class="t">相比原文：课程编号的演进</span><p>原文推荐的 <b>MIT 6.S081</b> 与 <b>6.824</b>，现在都已改名 ——
6.S081 于 2022 年统一更名为 <b>6.1810</b>（Operating System Engineering），6.824 自 2023 春季起变更为 <b>6.5840</b>（Distributed Systems）。
两类课程另有本科生 / 研究生的对应编号区分。搜索教材与视频时<b>新旧编号都要试</b>，否则容易扑空。这两门分别属于下面的操作系统与分布式方向，此处一并说明。</p></div>

<h3>5.4 之后可以深入</h3>

<ul>
  <li>计算机体系结构（研究生难度）：乱序执行、分支预测、多核一致性协议</li>
  <li>并行计算：CUDA / OpenMP / MPI，以及并行算法设计（CMU 15-418 / Stanford CS149）</li>
  <li>嵌入式与实时系统</li>
  <li>硬件加速：为深度学习等负载设计专用芯片（这条与当下热点直接相关）</li>
</ul>

<div class="box takeaway"><span class="t">本章结论</span><p>如果想「用最少的课时获得最大的世界观改变」，这一方向的性价比最高。
Nand2Tetris 用一到两个月就能给你一条完整链条，投入产出比在六个方向里排前列。</p></div>


<!-- ============================================================ -->
<h2><span class="n">6</span>方向四：操作系统</h2>
<p class="lede">原文那句判词值得原样保留：没有什么能比自己写个内核更能加深对操作系统的理解。</p>

<h3>6.1 学习价值</h3>

<p>操作系统是硬件与应用之间的那层抽象：它把纷繁的底层硬件，虚拟化成一套规范优雅的接口给所有程序使用。
学它的收益很直接 —— <b>你会开始理解平时那些「玄学」现象</b>：为什么进程会卡住、内存为什么会不够、
文件为什么会损坏、为什么加一个锁程序反而变慢。</p>

<h3>6.2 核心知识点</h3>

<table>
  <thead><tr><th style="width:170px;">板块</th><th>核心内容</th></tr></thead>
  <tbody>
    <tr><td><b>进程与线程</b></td><td>进程抽象、上下文切换、线程模型、用户态与内核态。</td></tr>
    <tr><td><b>系统调用与中断</b></td><td>程序如何从用户态进入内核；陷阱、中断、异常的区别。</td></tr>
    <tr><td><b>虚拟内存</b></td><td>页表、地址翻译、缺页、写时复制。这是最抽象也最有收获的一块。</td></tr>
    <tr><td><b>并发与同步</b></td><td>锁、条件变量、信号量、竞态条件、死锁。</td></tr>
    <tr><td><b>调度</b></td><td>时间片、优先级、多核调度。</td></tr>
    <tr><td><b>文件系统</b></td><td>inode、日志、崩溃恢复、缓存。</td></tr>
  </tbody>
</table>

<h3>6.3 入门资源</h3>

<table>
  <thead><tr><th style="width:200px;">课程</th><th>特点</th></tr></thead>
  <tbody>
    <tr><td><b>MIT 6.1810</b>（原 6.S081）<span class="pill cav">已更新编号</span></td><td> MIT PDOS 实验室出品，在一个优雅的小型类 Unix 系统 <b>xv6</b> 上做 11 个实验。<b>原文与社区公认的首选</b>。有完整的中文视频翻译文档。</td></tr>
    <tr><td><b>UCB CS162</b></td><td>用教学操作系统 <b>Pintos</b>，项目强度高。</td></tr>
    <tr><td><b>NJU 操作系统</b>（蒋炎岩）</td><td>中文授课，全部内容可看，讲得深入浅出 —— 对中文读者是极大的便利，这一点原文特别强调过。</td></tr>
    <tr><td><b>HIT 操作系统</b>（李治军）</td><td>中文课程，基于 Linux 0.11 源码，注重代码实践。</td></tr>
  </tbody>
</table>

<div class="box note"><span class="t">相比原文的两个变化</span><p>① <b>课程入口变了</b>：6.S081 的官方课程页现在是 6.1810，旧版讲义仍在网上可查（原文引用的 2021 秋季版本页面仍可访问）。
② <b>xv6 的形态变了</b>：xv6 已从最初的 x86 移植到 <b>RISC-V</b>，教材也更新为 RISC-V 版本；社区还出现了用 Rust 重写的 xv6，
可以作为「同一系统、不同语言」的对照阅读材料。选题时注意对应版本，否则实验与讲义会对不上。</p></div>

<h3>6.4 之后可以深入</h3>

<ul>
  <li>分布式系统：MIT <b>6.5840</b>（原 6.824）—— 精读经典论文 + 用 Go 实现一个基于 Raft 的 KV 存储。以难度大著称。</li>
  <li>系统安全：栈攻击、密码学、Web 安全（UCB CS161）；动手向可看 Syracuse 的 SEED Labs</li>
  <li>虚拟化与容器：Docker / cgroup / namespace 的底层原理</li>
  <li>实时系统与嵌入式操作系统</li>
</ul>

<div class="box takeaway"><span class="t">本章结论</span><p>做系统不是靠 PPT 念出来的，是几万行代码累起来的。这一方向<b>必须动手</b> —— 只读教材收益极低。
建议直接从 MIT 6.1810 的实验切入，遇到不懂再回看讲义。</p></div>


<!-- ============================================================ -->
<h2><span class="n">7</span>方向五：计算机网络</h2>
<p class="lede">你在工作中遇到的大部分「说不清为什么」的问题，一半以上出在这一层。</p>

<h3>7.1 学习价值</h3>

<p>网络课的收益非常实用：<b>排查连不上 / 时快时慢的问题、理解为什么要有分层、看懂抓包结果</b>。
对于前端、后端、数据工程、乃至临床统计里「数据从中心实验室传到分析环境」这条链路，都有直接帮助。</p>

<h3>7.2 核心知识点</h3>

<table>
  <thead><tr><th style="width:170px;">板块</th><th>核心内容</th></tr></thead>
  <tbody>
    <tr><td><b>分层与封装</b></td><td>为什么网络要分层、每层职责边界、封装与解封装。这是整门课的地基。</td></tr>
    <tr><td><b>寻址</b></td><td>IP 地址、子网与 CIDR、ARP、DNS。地址如何在层次中分配与聚合。</td></tr>
    <tr><td><b>路由</b></td><td>域内路由（距离向量 / 链路状态）、域间路由（BGP）与策略。</td></tr>
    <tr><td><b>传输层</b></td><td>TCP 的三次握手、可靠传输、滑动窗口、拥塞控制；UDP 的取舍。</td></tr>
    <tr><td><b>应用层</b></td><td>HTTP/HTTPS、DNS 解析过程、CDN 与缓存。</td></tr>
  </tbody>
</table>

<h3>7.3 入门资源</h3>

<table>
  <thead><tr><th style="width:200px;">课程 / 材料</th><th>特点</th></tr></thead>
  <tbody>
    <tr><td><b>Stanford CS144</b></td><td><span class="pill ok">动手首选</span> 8 个实验带你实现整个 TCP/IP 协议栈。原文称其为「大名鼎鼎」，这个评价没有过时。需要一定的 C++ 基础。</td></tr>
    <tr><td><b>UCB CS168</b></td><td><span class="pill cav">理论主线</span> 聚焦 Internet 的设计原则与协议机制，配轻量项目验证直觉。适合「先建立全局认知，再动手实现」的路径，或只做理论学习。</td></tr>
    <tr><td><b>《Computer Networking: A Top-Down Approach》</b></td><td>经典自顶向下教材，配套 UMass 课程；与 CS168 知识范围高度重合，可交叉复习。</td></tr>
  </tbody>
</table>

<div class="box note"><span class="t">相比原文的说明</span><p>原文对 CS168 的描述是「推荐阅读其配套教材」，措辞偏保守。
按 2026 年的课程现状看，<b>CS168 本身就是一门可跟学的完整课程</b>（Internet Architecture and Protocols），
与 CS144 形成「理论 / 工程」双主线，可以直接按课跟，不必只读书。两门课的分工是原文里最实用的建议之一，建议保留：
<b>先 CS168 建立心智模型，再 CS144 亲手实现协议栈</b>，会少走很多弯路。</p></div>

<h3>7.4 之后可以深入</h3>

<ul>
  <li>HTTP/3 与 QUIC：新一代传输协议，理解它为什么绕开 TCP</li>
  <li>网络安全：TLS 握手细节、中间人攻击与防护</li>
  <li>分布式网络：一致性哈希、负载均衡、服务发现</li>
  <li>网络性能：带宽延迟积、拥塞控制算法演进（从 Reno 到 BBR）</li>
</ul>

<div class="box takeaway"><span class="t">本章结论</span><p>想动手就 CS144，想先懂原理就 CS168，两个都做效果最好。判断学没学会的标准：<b>给你一个抓包文件，能不能说清一次 HTTP 请求经历了什么</b>。</p></div>


<!-- ============================================================ -->
<h2><span class="n">8</span>方向六：数据库系统</h2>
<p class="lede">原文的判词同样值得保留：没有什么能比自己写个关系型数据库更能加深对数据库系统的理解。</p>

<h3>8.1 学习价值</h3>

<p>数据库是前面几门的<b>交汇点</b>：它要用到数据结构（B+ 树、哈希）、操作系统（缓冲、并发、日志）、
网络（客户端协议）、算法（查询优化、连接算法）。学完它，你会对「一条 SQL 是怎么跑出结果的」有完整的图像，
也会更清楚什么时候该加索引、什么时候该反范式。</p>

<h3>8.2 核心知识点</h3>

<table>
  <thead><tr><th style="width:170px;">板块</th><th>核心内容</th></tr></thead>
  <tbody>
    <tr><td><b>存储与索引</b></td><td>页式存储、缓冲池、B+ 树索引、哈希索引。为什么索引能让查询快几个数量级。</td></tr>
    <tr><td><b>查询执行</b></td><td>迭代器模型、连接算法（嵌套循环 / 哈希 / 归并）、排序与聚合。</td></tr>
    <tr><td><b>查询优化</b></td><td>代价估算、执行计划、统计信息。</td></tr>
    <tr><td><b>事务与并发</b></td><td>ACID、隔离级别、两阶段锁、MVCC。为什么会有幻读与脏读。</td></tr>
    <tr><td><b>恢复</b></td><td>日志（WAL）、检查点、崩溃恢复。</td></tr>
  </tbody>
</table>

<h3>8.3 入门资源</h3>

<table>
  <thead><tr><th style="width:180px;">课程</th><th>特点</th></tr></thead>
  <tbody>
    <tr><td><b>CMU 15-445 / 645</b></td><td><span class="pill ok">首选</span> 用 4 个项目带你在教学数据库 <b>BusTub</b> 上实现缓冲池、索引、查询执行与并发控制。评测框架开源，非 CMU 学生也可提交。Andy Pavlo 讲授，风格生动。</td></tr>
    <tr><td><b>UCB CS186</b></td><td>用 Java 实现一个支持并发查询、B+ 树索引与故障恢复的关系型数据库。与 15-445 二选一。</td></tr>
  </tbody>
</table>

<div class="box note"><span class="t">相比原文的三个变化（这一块变动最大）</span>
<ul>
  <li><b>BusTub 的语言标准升级了</b>：实验代码现在使用 <b>C++20</b>（原文写的是 C++11），并且第一个项目<b>必须先通过一个 C++ 能力测试</b>。这意味着<b>C++ 基础现在是硬门槛</b>，不要抱着「边做边学」的心态进去。</li>
  <li><b>项目内容有调整</b>：以 2025 秋季学期为例，第一个项目从传统的 LRU 替换策略换成了 <b>ARC（自适应替换缓存）</b>，并加入了磁盘调度器等组件。也就是说，网上早期版本的博客题解<b>可能与当前实验对不上</b>，务必先看当学期官网的 project 说明。</li>
  <li><b>新增了学术诚信约束</b>：课程明确要求不得把项目实现公开到 GitHub，使用自动评测需要先签署协议。<b>自学时请务必遵守</b>。</li>
</ul>
</div>

<h3>8.4 之后可以深入</h3>

<ul>
  <li>查询优化器与执行引擎（进阶课 CMU 15-721）</li>
  <li>分布式数据库：分片、复制、一致性协议（与 §6.4 的 6.5840 衔接）</li>
  <li>列式存储与 OLAP：向量化执行、压缩编码</li>
  <li>键值存储与 NoSQL：LSM-Tree、最终一致性</li>
</ul>

<div class="box takeaway"><span class="t">本章结论</span><p>这一方向的<b>前提门槛最高</b>（要会用 C++20，要懂数据结构与操作系统），但收获也最完整。
建议放在算法与操作系统之后，作为「把前面都串起来」的一门收口课。</p></div>


<!-- ============================================================ -->
<h2><span class="n">9</span>怎么选：给你的实际操作建议</h2>
<p class="lede">地图看完了，回到最实际的问题 —— 我到底该从哪一门开始。</p>

<h3>9.1 按你的起点选</h3>

<table>
  <thead><tr><th style="width:200px;">你的情况</th><th>建议路径</th></tr></thead>
  <tbody>
    <tr>
      <td><b>完全零基础</b></td>
      <td>命令行 + Git（§2）→ 一门编程入门课（§3）→ 数据结构与算法（§4）→ 然后按兴趣挑机器侧一门。</td>
    </tr>
    <tr>
      <td><b>会写代码，但没学过 CS 基础</b></td>
      <td>直接跳到数据结构与算法（§4）。这门课补上之后，机器侧四门都能挑着学。</td>
    </tr>
    <tr>
      <td><b>已在工作中写了不少代码</b></td>
      <td>横向切入：选一个你天天用却说不清原理的方向（多半是网络或数据库），从那里往下挖。动力最足，见效最快。</td>
    </tr>
    <tr>
      <td><b>时间有限，只想补最关键的</b></td>
      <td>算法 + 计算机组成（Nand2Tetris）。这两门分别补上「方法」与「世界观」，性价比最高。</td>
    </tr>
  </tbody>
</table>

<h3>9.2 三条通用原则</h3>

<ol>
  <li><b>一门课做完，胜过六门课开始。</b>每门课都做到能独立完成项目为止，再换下一门。半途而废的课几乎不产生能力。</li>
  <li><b>必做项目，不做项目等于没学。</b>系统类课程（操作系统、网络、数据库）尤其如此 —— 这是原文反复强调的一点，也是最容易被自学的人忽略的一点。</li>
  <li><b>围绕一个真实目标学。</b>比如「我想做一个能查数据的网页」，就会自然串起编程语言、网络、数据库。有目标的路径比按目录刷课走得远。</li>
</ol>

<div class="box finding"><span class="t">给「已经有熟练专业语言」的人</span><p>如果你已经在 SAS / R 里写了多年程序，别把入门课当作「重学一遍」——
你的抽象能力与调试直觉是能迁移的，缺的往往是<b>底层与系统侧</b>的知识。更高效的路径是：
跳过语言入门，直取算法 + 计算机组成 + 数据库，把「为什么」补齐。</p></div>

<div class="box takeaway"><span class="t">本章结论</span><p>不要因为「地图太大」而不开始。<b>选一门，做完它。</b>这六个方向不是必须全部学完才能算入门 —— 走通一条全程，你就会自己知道下一条该往哪走。</p></div>


<!-- ============================================================ -->
<h2><span class="n">10</span>附：一页速查表</h2>
<p class="lede">把六个方向压成一页，方便你之后回来看。</p>

<table>
  <thead><tr><th style="width:110px;">方向</th><th style="width:230px;">一句话价值</th><th style="width:190px;">首选入门</th><th>可深入 topic</th></tr></thead>
  <tbody>
    <tr>
      <td><b>编程语言</b></td>
      <td>建立抽象与调试能力，语言是可替换的</td>
      <td>UCB CS61A / CS50x</td>
      <td>编程范式、类型系统、语言理论</td>
    </tr>
    <tr>
      <td><b>数据结构与算法</b></td>
      <td>把现实问题转成可计算问题的公共基础</td>
      <td>UCB CS61B</td>
      <td>NP 完全性、字符串算法、竞赛方向</td>
    </tr>
    <tr>
      <td><b>计算机组成</b></td>
      <td>理解程序如何被执行、性能从哪里来</td>
      <td>Nand2Tetris</td>
      <td>体系结构进阶、并行计算、嵌入式</td>
    </tr>
    <tr>
      <td><b>操作系统</b></td>
      <td>理解硬件与应用之间的抽象层</td>
      <td>MIT 6.1810（原 6.S081）</td>
      <td>分布式系统、系统安全、虚拟化</td>
    </tr>
    <tr>
      <td><b>计算机网络</b></td>
      <td>排查「说不清为什么」的连通与性能问题</td>
      <td>Stanford CS144 / UCB CS168</td>
      <td>HTTP/3、TLS、分布式网络、拥塞控制</td>
    </tr>
    <tr>
      <td><b>数据库系统</b></td>
      <td>前面几门的交汇点，理解一条 SQL 的完整旅程</td>
      <td>CMU 15-445</td>
      <td>查询优化器、分布式数据库、OLAP</td>
    </tr>
  </tbody>
</table>

<div class="box takeaway"><span class="t">本章结论</span><p>把这张表存下来。等你决定「下一步学什么」时，回来看一眼就够了 —— 至于具体怎么学，去对应那一节。</p></div>

<footer>
  <p><strong>底稿与引用</strong> 方向划分与主要课程推荐来自 <a href="https://csdiy.wiki/CS学习规划/">csdiy.wiki《一个仅供参考的 CS 学习规划》</a>，本文按「方向」重排并补充了「可深入 topic」与 2026 年现状校对。CS 学习规划一文本身仍在更新（页面标注 2026-09）。</p>
  <p><strong>时效性说明</strong> 标注 <span class="pill cav">已更新</span> 的内容均为 2026-10 校对结果：课程编号变更（6.S081→6.1810、6.824→6.5840）来自 MIT PDOS 官方课程页；BusTub 的 C++20 与 ARC 项目、学术诚信要求来自 CMU 15-445 2026 秋季官网与仓库说明。各课程每学期会调整内容，动手前请以当学期官网为准。</p>
  <p><strong>没有本地复现的部分</strong> 本文为路线导读，未实际运行上述任何课程的实验；所有课程内容描述来自官方课程页与公开文档，不构成「我已做过」的声明。</p>
</footer>
