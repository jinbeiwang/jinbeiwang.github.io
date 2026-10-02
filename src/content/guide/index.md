---
kind: index
title: "计算机科学核心：一条走得通的自学主线"
short: "系列说明"
summary: "按依赖顺序串起编程基础、数据结构与算法、计算机组成、操作系统、计算机网络、数据库、编译原理、分布式系统八条主线。先说清排序依据，再一章一章写透；每章标注前置依赖与学习顺序，配权威教材与公开课。"
date: 2026-10-03
tags: [计算机科学, 自学路线, 教材式笔记, Python]
lang: zh
steps:
  - part: 第零部 · 出发前
    items:
      - title: 学习主线
        href: /guide.html
        note: 排序依据、用法、依赖图
        state: current
  - part: 第一部 · 地基
    items:
      - title: 编程基础
        href: /guide/01-programming-basics.html
        note: 第一章 · 已写完
        state: done
  - part: 第二部 · 机器侧主干
    items:
      - title: 数据结构与算法
        href: /guide/02-data-structures-and-algorithms.html
        note: 第二章 · 已写完
        state: done
      - title: 计算机组成与体系结构
        note: 第三章 · 下一章
        state: next
      - title: 操作系统
        note: 第四章
        state: planned
      - title: 计算机网络
        note: 第五章
        state: planned
      - title: 数据库系统
        note: 第六章
        state: planned
  - part: 第三部 · 系统侧纵深
    items:
      - title: 编译原理
        note: 第七章
        state: planned
      - title: 分布式系统
        note: 第八章
        state: planned
---

<div class="meta-row">
    <span><b>读者</b> &nbsp;有零散编程经验、想系统补齐计算机基础的人</span>
    <span><b>目标</b> &nbsp;沿一条有依赖关系的路径，把主干知识一章一章学透</span>
    <span><b>体例</b> &nbsp;教材式：背景与动机 → 核心概念 → 原理（推导 / 伪代码 / 图解）→ 示例与类比 → 易错点 → 思考题</span>
    <span><b>代码语言</b> &nbsp;中文讲解，<b>Python 为主</b>；涉及底层时用 C 的伪码或 ARM/RISC-V 汇编片段补充</span>
</div>

<div class="box note" style="margin-top:26px;">
  <span class="t">这个系列是什么，不是什么</span>
  <div class="small">
  <p><b>是一套可以按顺序读完的正文，不是一份书单。</b>每一章都按教材写：先讲清「这个东西为什么存在」，再讲「它怎么工作」（有推导、有伪代码、有图解），然后才是「怎么用」。
  读完一章你应该能回答那章的思考题，而不是只知道有哪些关键词。</p>
  <p><b>它取代不了动手。</b>计算机科学里没有哪门课能靠阅读学会 —— 操作系统要自己写调度器，网络要自己抓包看三次握手，数据库要自己实现一个 B+ 树才能体会为什么它是页式存储的最优解。
  本系列的作用是<b>在你动手之前把地图讲清楚，动手之后帮你把散落的知识串成体系</b>。</p>
  <p><b>资源推荐是「社区共识」，不是唯一答案。</b>文中出现的教材与公开课都有推荐理由、适用阶段和难度标注。同一门课换一门替代课完全可能更适合你 —— 判断标准在每章的开头（前置依赖）与结尾（如何自测）。</p>
  </div>
</div>

<!-- ============================================================ -->
<h2><span class="n">1</span>为什么是这个顺序</h2>
<p class="lede">顺序不是拍脑袋定的。每一条主线都问同一个问题：<b>学它需要先会什么，不学它会卡住什么。</b></p>

<p>计算机科学作为一个学科，真正的难点不在知识点的数量，而在<b>知识之间的依赖方向</b>。
同样是「内存」这个词，在编程基础里指「一个变量住在哪」，在数据结构里指「一段连续排列的格子」，在操作系统里指「分页、虚拟地址与缺页异常」，
在计算机组成里指「DRAM 芯片、行缓冲与刷新」。四个层面都对，错的是把它们的顺序搞乱 —— 从最抽象的那层开始，你永远解释不清为什么下层要那么设计；
从最底层开始，你又不知道那些设计是在解决什么问题。所以这套笔记选了一条<b>从「你已经在做的事」出发，一层一层往下钉</b>的路线。</p>

<figure>
<svg viewBox="0 0 680 428" role="img" aria-label="八个方向的依赖关系与学习顺序图">
  <g font-family="-apple-system,BlinkMacSystemFont,'Segoe UI','PingFang SC','Microsoft YaHei',Helvetica,Arial,sans-serif">
    <text x="24" y="20" font-size="10.5" font-weight="700" fill="#8b949e">抽象层次：越往上越接近「人的意图」，越往下越接近「机器的实现」</text>
    <rect x="24" y="30" width="632" height="42" rx="4" fill="#eef3f8" stroke="#1b4f8a" stroke-width="1.5"/>
    <text x="40" y="48" font-size="12" font-weight="700" fill="#1b4f8a">第一章 · 编程基础</text>
    <text x="40" y="64" font-size="10.5" fill="#5b6570">表达意图的最小工具集：变量、控制流、函数、数据结构、调试</text>
    <text x="640" y="56" font-size="10" fill="#1b4f8a" text-anchor="end">无前置</text>
    <line x1="340" y1="72" x2="340" y2="88" stroke="#c9d2dc" stroke-width="1.5"/>
    <path d="M334 83 L340 93 L346 83" fill="none" stroke="#c9d2dc" stroke-width="1.5"/>
    <rect x="24" y="94" width="632" height="42" rx="4" fill="#f0f7f4" stroke="#0f7b5f" stroke-width="1.5"/>
    <text x="40" y="112" font-size="12" font-weight="700" fill="#0f7b5f">第二章 · 数据结构与算法</text>
    <text x="40" y="128" font-size="10.5" fill="#5b6570">把现实问题变成「可计算」的问题；复杂度是之后每一章的分析语言</text>
    <text x="640" y="120" font-size="10" fill="#0f7b5f" text-anchor="end">前置：第一章</text>
    <line x1="340" y1="136" x2="340" y2="152" stroke="#c9d2dc" stroke-width="1.5"/>
    <path d="M334 147 L340 157 L346 147" fill="none" stroke="#c9d2dc" stroke-width="1.5"/>
    <rect x="24" y="158" width="632" height="42" rx="4" fill="#f7f8f9" stroke="#dfe5ea"/>
    <rect x="24" y="158" width="3" height="42" fill="#1b4f8a"/>
    <text x="40" y="176" font-size="12" font-weight="700" fill="#17181a">第三章 · 计算机组成与体系结构</text>
    <text x="40" y="192" font-size="10.5" fill="#5b6570">一行代码如何变成电信号：指令集、流水线、存储层次、缓存</text>
    <text x="640" y="184" font-size="10" fill="#1b4f8a" text-anchor="end">前置：第一章</text>
    <line x1="340" y1="200" x2="340" y2="216" stroke="#c9d2dc" stroke-width="1.5"/>
    <path d="M334 211 L340 221 L346 211" fill="none" stroke="#c9d2dc" stroke-width="1.5"/>
    <rect x="24" y="222" width="308" height="42" rx="4" fill="#f7f8f9" stroke="#dfe5ea"/>
    <rect x="24" y="222" width="3" height="42" fill="#1b4f8a"/>
    <text x="40" y="240" font-size="12" font-weight="700" fill="#17181a">第四章 · 操作系统</text>
    <text x="40" y="256" font-size="10.5" fill="#5b6570">进程、内存、文件：资源怎么被分配</text>
    <text x="320" y="248" font-size="10" fill="#1b4f8a" text-anchor="end">前置：二、三</text>
    <rect x="348" y="222" width="308" height="42" rx="4" fill="#f7f8f9" stroke="#dfe5ea"/>
    <rect x="348" y="222" width="3" height="42" fill="#1b4f8a"/>
    <text x="364" y="240" font-size="12" font-weight="700" fill="#17181a">第五章 · 计算机网络</text>
    <text x="364" y="256" font-size="10.5" fill="#5b6570">两台机器怎么对话：分层与协议</text>
    <text x="644" y="248" font-size="10" fill="#1b4f8a" text-anchor="end">前置：一、二</text>
    <line x1="178" y1="264" x2="178" y2="280" stroke="#c9d2dc" stroke-width="1.5"/>
    <line x1="502" y1="264" x2="502" y2="280" stroke="#c9d2dc" stroke-width="1.5"/>
    <line x1="178" y1="280" x2="502" y2="280" stroke="#c9d2dc" stroke-width="1.5"/>
    <line x1="340" y1="280" x2="340" y2="296" stroke="#c9d2dc" stroke-width="1.5"/>
    <path d="M334 291 L340 301 L346 291" fill="none" stroke="#c9d2dc" stroke-width="1.5"/>
    <text x="352" y="293" font-size="10" fill="#8b949e">第四、五章在此汇合</text>
    <rect x="24" y="302" width="632" height="42" rx="4" fill="#f0f7f4" stroke="#0f7b5f" stroke-width="1.5"/>
    <text x="40" y="320" font-size="12" font-weight="700" fill="#0f7b5f">第六章 · 数据库系统</text>
    <text x="40" y="336" font-size="10.5" fill="#5b6570">算法的检索 + 存储的页式管理 + 并发的隔离，三样缺一不可</text>
    <text x="640" y="328" font-size="10" fill="#0f7b5f" text-anchor="end">前置：二、三、四</text>
    <line x1="340" y1="344" x2="340" y2="360" stroke="#c9d2dc" stroke-width="1.5"/>
    <path d="M334 355 L340 365 L346 355" fill="none" stroke="#c9d2dc" stroke-width="1.5"/>
    <rect x="24" y="366" width="308" height="42" rx="4" fill="#f7f8f9" stroke="#dfe5ea"/>
    <rect x="24" y="366" width="3" height="42" fill="#1b4f8a"/>
    <text x="40" y="384" font-size="12" font-weight="700" fill="#17181a">第七章 · 编译原理</text>
    <text x="40" y="400" font-size="10.5" fill="#5b6570">把人的意图翻译成机器指令</text>
    <rect x="348" y="366" width="308" height="42" rx="4" fill="#f7f8f9" stroke="#dfe5ea"/>
    <rect x="348" y="366" width="3" height="42" fill="#1b4f8a"/>
    <text x="364" y="384" font-size="12" font-weight="700" fill="#17181a">第八章 · 分布式系统</text>
    <text x="364" y="400" font-size="10.5" fill="#5b6570">把失败当成常态的一致性问题</text>
  </g>
</svg>
<figcaption><b>图 1 |</b> 八条主线与它们的依赖关系。<b>蓝框</b>是「你已经在做的事」，<b>绿框</b>是两处最关键的地基（算法决定了后面所有课的项目能不能做下去，数据库是前四章的交汇点），<b>灰框</b>是机器侧主干与系统侧纵深。箭头代表真实的前置依赖，不是「建议先学」的礼貌说法。</figcaption>
</figure>

<h3>1.1 三条排序原则</h3>

<table>
  <thead><tr><th style="width:120px;">原则</th><th>含义</th><th style="width:230px;">它决定了什么</th></tr></thead>
  <tbody>
    <tr>
      <td><b>依赖优先</b></td>
      <td>如果理解 B 必须先理解 A，那 A 一定排在 B 前面。这条最硬，没有例外。</td>
      <td>算法在操作系统之前；组成原理在操作系统之前；并发与存储在数据库之前。</td>
    </tr>
    <tr>
      <td><b>先抽象后实现</b></td>
      <td>先告诉你「这层接口承诺了什么」，再拆开看「它怎么做到的」。反之你会拿着实现细节去猜接口存在的理由。</td>
      <td>编程基础在最前；汇编、门电路这类「纯实现层」放进组成原理，不提前。</td>
    </tr>
    <tr>
      <td><b>先高频后低频</b></td>
      <td>依赖关系并列时，先学你在工作中真正会撞上的那一个。</td>
      <td>网络与操作系统并列，但如果你每天在调接口、看日志，网络可以提前。</td>
    </tr>
  </tbody>
</table>

<h3>1.2 一个必须说清的取舍</h3>

<p>严密的依赖图会得出一个略微反直觉的结论：<b>数据结构与算法其实同时依赖「编程基础」和「机器的运行成本」</b>。
你当然可以先学数组和链表，但「为什么链表插入快、随机访问慢」这件事，真正的答案是「因为内存是连续排列的字节，
而 CPU 缓存一次会抓一整块」，这在组成原理里才讲得透。</p>

<div class="box finding"><span class="t">为什么还是把算法排在组成原理前面</span>
<p>因为<b>教学顺序可以不完全等于依赖顺序</b>。算法的前半部分（复杂度、数组、链表、栈、队列、哈希、排序、查找）只需要「内存是一排格子」这个直觉就够了，
这个直觉用一张图就能建立，不必等到第三章。而算法的后半部分（缓存友好性、分支预测对排序的影响、并发数据结构）确实是组成原理的应用 ——
所以本系列会在第二章标注「这几节建议在读完第三章后回看」，而不是把整章往后挪。<b>标记回看点是比强行重排更诚实的做法。</b></p></div>

<h3>1.3 每一章都长什么样</h3>

<p>为了让你能横向对照，每章用相同的骨架：</p>

<ul>
  <li><b>前置与自测</b> —— 开头写清「需要先会什么」和「读完后你应该能回答什么」，你可以先做自测题再决定要不要细读。</li>
  <li><b>背景与动机</b> —— 这一层要解决什么问题，它在没有它的时候是什么样子。不写「这东西很重要」这种空话。</li>
  <li><b>核心概念与原理</b> —— 主体部分。有推导就写推导，有伪代码就写伪代码，能画图就画图，三者都有的尽量都给。</li>
  <li><b>示例与类比</b> —— 尽量用日常经验做锚点，但类比之后一定紧跟一句「这个类比在哪里失效」，否则类比会变成新的误解。</li>
  <li><b>易错点与常见误区</b> —— 单独成框。这些是真正扣分的地方，往往不是不懂，而是「以为懂了」。</li>
  <li><b>思考题</b> —— 不给标准答案，但给「怎么判断自己答对了」的线索。</li>
  <li><b>参考资料</b> —— 表格形式，含推荐理由、适用阶段、难度。</li>
</ul>

<div class="box takeaway"><span class="t">本章结论</span><p>顺序的依据是<b>依赖方向</b>，不是难易或流行度：先拿住「表达意图的工具」（编程基础），再拿住「把问题变可计算的方法」（算法），
然后按兴趣进入机器侧的四条主干（组成、操作系统、网络、数据库），最后是两处纵深（编译、分布式）。
不是八门平行课 —— 走通一条，比浅尝八条有价值得多。</p></div>

<!-- ============================================================ -->
<h2><span class="n">2</span>怎么用这套笔记</h2>
<p class="lede">它是一本「按需展开的参考书」，不是一个必须从头读到尾的连载。</p>

<h3>2.1 三种读法</h3>

<table>
  <thead><tr><th style="width:130px;">你的情况</th><th style="width:210px;">建议路径</th><th>为什么</th></tr></thead>
  <tbody>
    <tr>
      <td><b>完全按顺序</b></td>
      <td>第一 → 第二 → 第三 → 第四 → 第五 → 第六</td>
      <td>依赖最少，每章都能在前一章找到支点。代价是前几章比较基础，需要耐心。</td>
    </tr>
    <tr>
      <td><b>带着问题来</b></td>
      <td>直接跳到目标章，读开头的「前置」框，缺哪块补哪块</td>
      <td>本系列每章首节都有一个依赖框，明确列出「如果不熟这些，先回看哪一节」。</td>
    </tr>
    <tr>
      <td><b>已经在动手</b></td>
      <td>先做项目，卡住时按章节回查</td>
      <td>本系列更适合当「你写代码时的背景解释器」——遇到不懂的概念，回来看对应的那节，比从第一章啃起效率高得多。</td>
    </tr>
  </tbody>
</table>

<h3>2.2 关于配套练习</h3>

<p>每章的思考题都<b>不给答案</b>，只给判断线索。原因很实际：这类题目的答案通常不是一句话，而是一段推理过程，
给出标准答案反而会让你跳过推理。如果你需要一个更硬的标准，每章参考资料里都会指向带自动评分或公开评测的课程作业
（例如算法章的公开 OJ、操作系统章的 MIT 6.1810 labs），那些是真正有反馈的练习。</p>

<div class="box note"><span class="t">当前位置</span><p>目前完成的是<b>第一章 · 编程基础</b>与<b>第二章 · 数据结构与算法</b>。
先做第一章，是因为它是唯一的「没有它你连后面章节的代码都读不下去」的一章，也是最容易写砸的一章 ——
把「变量是什么」讲深很难，讲浅又毫无价值。第二章则是从「会写程序」到「会设计程序」的分界线，
它把第一章留下的几处伏笔（二分的循环不变式、<code>list</code> 与 <code>set</code> 的查找代价差）一次结清。
这两章也共同构成了全套笔记的<b>体例样板</b>：后面的章节会按同一密度和结构来写 ——
每节先讲动机、再讲原理（带推导或图）、然后拆掉一个流行误解、最后留自测题。
后续章节会陆续补上，每补一章都会在这里更新。</p></div>

<footer>
  <p><strong>关于取材</strong> 各章的课程与教材推荐参考了 <a href="https://csdiy.wiki/">csdiy.wiki</a> 的 CS 自学规划，以及各校公开课程主页与经典教材；具体到每一章，会在该章末列出并注明推荐理由、适用阶段与难度。</p>
  <p><strong>截至</strong> 2026-10。文中涉及课程编号、工具版本、生态现状的部分都标注了校对时点；教材本身的内容不会过期，课程编号与工具链版本会，请以各校官网与官方文档为准。</p>
</footer>
