---
kind: chapter
order: 2
title: "数据结构与算法：把现实问题变成可计算的问题"
part: "第二部 · 机器侧主干"
prereq: "第一章"
reading: "约 75 分钟"
date: 2026-10-03
ready: true
tags: [计算机科学, 自学路线, 教材式笔记, Python, 数据结构, 算法]
lang: zh
---

<div class="meta-row">
    <span><b>读者</b> &nbsp;读完第一章、能写几百行 Python，但说不清「这段代码为什么慢」的人</span>
    <span><b>整章目标</b> &nbsp;掌握一把尺子（复杂度）、四种基本结构、四种设计范式，并能用它们判断方案好坏</span>
    <span><b>代码语言</b> &nbsp;Python 3.12+；复杂度结论以 CPython 实测为准，与语言无关的部分会说明</span>
    <span><b>校对时点</b> &nbsp;2026-10。标准库复杂度以 Python 官方 TimeComplexity 页为准</span>
</div>

<div class="box note" style="margin-top:26px;">
  <span class="t">这一章与第一章怎么衔接</span>
  <div class="small">
  <p><b>第一章的伏笔在这一章兑现。</b>第一章 §2.4 讲了循环不变式，并承诺「二分查找的边界靠它推导而不是靠记忆」—— 那是这一章 §5.4 的内容。
  第一章 §4.1 说「<code>list</code> 和 <code>set</code> 的查找写法一样但代价差几个数量级」，并说「第二章会把它写成精确的复杂度结论」—— 那是这一章 §1 和 §3 的内容。</p>
  <p><b>这一章开始有「计算机科学」的味道了。</b>第一章关心的是「代码能不能跑对」，这一章关心的是<b>「在什么输入规模下、花多少代价」</b>。
  这是两种不同性质的判断，也是从「会写程序」到「会设计程序」的分界线。后面每一章都要用这套语言：第三章讲缓存时会说「局部性如何影响实际复杂度」，
  第四章讲调度时会说「这个算法的摊销代价」，第六章讲索引时会说「B+ 树把查找从 O(n) 降到 O(log n) 意味着什么」。</p>
  </div>
</div>

<h2><span class="n">1</span>复杂度：算法分析的语言</h2>
<p class="lede">为什么不用秒表，而是用 Asymptotic notation？因为秒表测的是「这台机器」，而我们要问的是「这个问题本身有多难」。</p>

<h3>1.1 为什么不能用秒表</h3>

<p>一个自然的想法是：把两段代码都跑一遍，谁快用谁。这个做法在具体场景下完全正确，但它回答不了三个更重要的问题：</p>

<table>
  <thead><tr><th style="width:180px;">问题</th><th>为什么秒表答不了</th></tr></thead>
  <tbody>
    <tr><td><b>数据变大之后呢？</b></td><td>在 100 条数据上 A 比 B 快 2 倍，在 100 万条上可能 B 比 A 快 1000 倍。<b>秒表只测了你测过的那一个规模。</b></td></tr>
    <tr><td><b>换台机器还算数吗？</b></td><td>换 CPU、换 Python 版本、甚至只是内存够不够，排名都可能变。你要的是「与机器无关」的结论。</td></tr>
    <tr><td><b>这段代码最坏能坏到什么程度？</b></td><td>秒表测的是「这次输入」。真实系统要面对的是「任何人都可能传来的输入」，包括那些专门为难你的。</td></tr>
  </tbody>
</table>

<p>复杂度分析就是来回答这三个问题的。它的做法出人意料地简单：<b>不测时间，数操作次数；不关心系数，只关心增长趋势。</b></p>

<h3>1.2 三种记号，三种不同的问题</h3>

<p>日常说「这个算法是 O(n log n)」时，其实混用了三种不同的记号。分清它们，是读懂算法分析的第一道门槛。</p>

<table>
  <thead><tr><th style="width:74px;">记号</th><th style="width:156px;">读作</th><th style="width:230px;">严谨含义</th><th>它回答的问题</th></tr></thead>
  <tbody>
    <tr>
      <td><b>O</b></td>
      <td>大 O</td>
      <td>存在常数 c、n₀，使得当 n ≥ n₀ 时 f(n) ≤ c·g(n)</td>
      <td><b>上界</b> —— 最坏不会超过这个量级。工程上最常用，因为它给的是保证。</td>
    </tr>
    <tr>
      <td><b>Ω</b></td>
      <td>大 Omega</td>
      <td>存在常数 c、n₀，使得当 n ≥ n₀ 时 f(n) ≥ c·g(n)</td>
      <td><b>下界</b> —— 至少要花这么多。常用于证明「这个问题不可能更快」。</td>
    </tr>
    <tr>
      <td><b>Θ</b></td>
      <td>大 Theta</td>
      <td>同时是 O 和 Ω</td>
      <td><b>紧确界</b> —— 上下都卡住了，这才是「恰好是这个量级」。</td>
    </tr>
  </tbody>
</table>

<pre><code><span class="cm"># 数操作次数：在一个列表里找最大值</span>
<span class="kw">def</span> max_of(nums):
    best = nums[<span class="mk">0</span>]              <span class="cm"># 1 次赋值</span>
    <span class="kw">for</span> x <span class="kw">in</span> nums[<span class="mk">1</span>:]:         <span class="cm"># 遍历 n-1 次</span>
        <span class="kw">if</span> x &gt; best:            <span class="cm"># 每次 1 次比较</span>
            best = x            <span class="cm"># 最多再多 1 次赋值</span>
    <span class="kw">return</span> best
<span class="cm"># 总操作数 ~ 2n，于是：</span>
<span class="cm">#   O(n)    上界成立（2n ≤ 3n）</span>
<span class="cm">#   Ω(n)    下界成立（2n ≥ n，因为每个元素都必须至少看一次）</span>
<span class="cm">#   Θ(n)    两者都有，所以是紧的</span></code></pre>

<div class="box finding"><span class="t">模型修正 1 —— 「O 是最坏情况」不完全对</span>
<p>常见说法是「O 表示最坏情况，Ω 表示最好情况」。<b>这个对应关系是错的</b>，它把两件正交的事混成了一件：</p>
<p><b>O / Ω / Θ 描述的是「以一个函数为界」</b>，而<b>最坏 / 平均 / 最好描述的是「取哪个输入」</b>。它们可以任意组合：
你可以说「快排的最坏情况是 Θ(n²)」、「快排的平均情况是 Θ(n log n)」—— 两个都在用 Θ。</p>
<p>之所以给人「O = 最坏」的印象，是因为工程上普遍只关心上界（保证不会更差），所以习惯用 O 去包最坏情况。
但只要记住「记号管界、形容词管输入」，就不会混。</p>
</div>

<h3>1.3 一条实用的判据：乘法变加法</h3>

<p>不用背公式，用数循环嵌套层数就能得出大部分结论：</p>

<table>
  <thead><tr><th style="width:210px;">代码形态</th><th style="width:110px;">复杂度</th><th>怎么判断</th></tr></thead>
  <tbody>
    <tr><td>不含循环的语句</td><td>O(1)</td><td>与 n 无关，无论它是 1 行还是 100 行。</td></tr>
    <tr><td>单层循环，循环 n 次</td><td>O(n)</td><td>遍历一次。</td></tr>
    <tr><td>两层嵌套，各 n 次</td><td>O(n²)</td><td>外层每走一步，内层完整走一遍 —— <b>嵌套的层数相乘</b>。</td></tr>
    <tr><td>两层循环但内层与 i 相关（<code>for j in range(i)</code>）</td><td>O(n²)</td><td>次数是 1+2+…+n = n(n+1)/2，仍是平方量级（常数 1/2 被丢掉）。</td></tr>
    <tr><td>两段先后执行的循环</td><td>O(n)</td><td>顺序执行取<b>较大</b>的那个，而不是相加。</td></tr>
    <tr><td>每轮把规模减半</td><td>O(log n)</td><td>「还剩多少轮」是 n 能除以 2 几次。</td></tr>
  </tbody>
</table>

<div class="box note"><span class="t">为什么常数系数可以被丢掉 —— 它的边界在哪</span>
<p>扔掉系数在<b>比较不同增长量级</b>时永远正确，因为 n 足够大时指数项必然压倒常数。但有两个实际场景必须把系数捡回来：</p>
<p><b>① 你的 n 其实不大。</b>当 n ≤ 50 时，一个 O(n²) 的简单实现常常比 O(n log n) 的复杂实现更快 —— 因为后者的常数因子大得多。
标准库里的 Python <code>sort</code> 就是在小数组上切回插入排序的（Timsort 的做法），原因正是这个。</p>
<p><b>② 你在两个同量级的算法之间选。</b>两个都是 O(n log n) 的排序算法，常数因子可能相差两倍以上。这时要做的是实测，而不是继续看复杂度。</p>
</div>

<h3>1.4 摊销分析：平均代价不等于每次的代价</h3>

<p>有一个比「平均情况」更精细、也更有用的概念，叫<b>摊销（amortized）代价</b>。
它回答的是：<b>「一连串操作的总代价，平均到每次是多少」</b>，而不是「随机一次操作期望花多少」。</p>

<p>Python 的 <code>list.append</code> 是最标准的例子。直接数它会得出一个奇怪的结果：</p>

<pre><code><span class="cm"># 如果每次 append 都要申请「刚好够用」的新数组并搬过去</span>
xs = []
<span class="kw">for</span> i <span class="kw">in</span> <span class="kw">range</span>(n):
    xs.append(i)     <span class="cm"># 第 i 次要搬 i 个元素</span>
<span class="cm"># 总搬运量 = 0 + 1 + 2 + ... + (n-1) = n(n-1)/2</span>
<span class="cm"># 平均每次 = (n-1)/2 —— 也就是 O(n)</span>
<span class="cm"># 那样 append 就成了 O(n) 操作，在循环里用它会退化到 O(n²)</span></code></pre>

<p>但实测不是这样，<code>append</code> 摊销下来是 <b>O(1)</b>。原因是 CPython 的策略不是「刚好够用」，而是<b>按比例扩容</b>：
装满了就申请一块更大的（约 1.125 倍），把旧内容搬过去，然后留下空位给后面连续使用。</p>

<figure>
<svg viewBox="0 0 680 296" role="img" aria-label="动态数组按比例扩容的摊销代价示意">
  <g font-family="-apple-system,BlinkMacSystemFont,'Segoe UI','PingFang SC','Microsoft YaHei',Helvetica,Arial,sans-serif">
    <text x="24" y="20" font-size="10.5" font-weight="700" fill="#8b949e">朴素做法：每次只申请「刚好够用」的空间</text>
    <rect x="24" y="30" width="34" height="26" rx="3" fill="#eef3f8" stroke="#1b4f8a" stroke-width="1.2"/>
    <rect x="62" y="30" width="68" height="26" rx="3" fill="#eef3f8" stroke="#1b4f8a" stroke-width="1.2"/>
    <rect x="134" y="30" width="102" height="26" rx="3" fill="#eef3f8" stroke="#1b4f8a" stroke-width="1.2"/>
    <rect x="240" y="30" width="136" height="26" rx="3" fill="#eef3f8" stroke="#1b4f8a" stroke-width="1.2"/>
    <rect x="380" y="30" width="170" height="26" rx="3" fill="#eef3f8" stroke="#1b4f8a" stroke-width="1.2"/>
    <text x="562" y="47" font-size="10.5" fill="#5b6570">每次都要重新申请 + 全搬</text>
    <text x="24" y="74" font-size="10.5" fill="#17181a">n 次 append 的总搬运量是 n(n-1)/2 → 平摊到每次是 O(n)，循环用它会退化成 O(n²)</text>
    <line x1="24" y1="92" x2="656" y2="92" stroke="#dfe5ea" stroke-width="1.5"/>
    <text x="24" y="114" font-size="10.5" font-weight="700" fill="#0f7b5f">按比例扩容：容量满了就翻倍申请，搬家后留下空位</text>
    <rect x="24" y="126" width="140" height="26" rx="3" fill="#f0f7f4" stroke="#0f7b5f" stroke-width="1.2"/>
    <text x="94" y="143" font-size="10" fill="#0f7b5f" text-anchor="middle">capacity 4</text>
    <text x="176" y="143" font-size="10" fill="#8b949e">满了 → 申请 8</text>
    <rect x="246" y="126" width="264" height="26" rx="3" fill="#f0f7f4" stroke="#0f7b5f" stroke-width="1.2"/>
    <text x="378" y="143" font-size="10" fill="#0f7b5f" text-anchor="middle">capacity 8</text>
    <text x="522" y="143" font-size="10" fill="#8b949e">满了 → 申请 16</text>
    <rect x="24" y="162" width="632" height="26" rx="3" fill="#f7f8f9" stroke="#dfe5ea" stroke-dasharray="4 3"/>
    <text x="38" y="179" font-size="10" fill="#5b6570">搬家的次数：log₂n 次，第 k 次搬 2^k 个 → 总搬运量 &lt; 2n → 平摊到每次是 O(1)</text>
    <line x1="24" y1="204" x2="656" y2="204" stroke="#dfe5ea" stroke-width="1.5"/>
    <text x="24" y="226" font-size="11" font-weight="700" fill="#17181a">为什么这个技巧值一页纸</text>
    <text x="24" y="248" font-size="10.5" fill="#5b6570">① 它解释了为什么「偶尔很慢」和「平均很快」可以同时成立 —— 摊销代价不是平均情况，是把总账摊平。</text>
    <text x="24" y="266" font-size="10.5" fill="#5b6570">② 它是后面几章反复用到的工具：哈希表的扩容、第六章的 WAL 日志、第八章的一致性协议，都靠这套论证。</text>
    <text x="24" y="284" font-size="10.5" fill="#8b949e">③ 代价是「最坏情况下单次很慢」——对实时系统这是真问题，所以工程上会出现「预留容量」这类接口（Python 里是 list.__init__ 的预分配）。</text>
  </g>
</svg>
<figcaption><b>图 1 |</b> 摊销分析的做法：不看单次操作，看<b>一整串操作的总代价</b>再摊到每次。左上是朴素做法（每次搬家），右下是按比例扩容（搬家次数是 O(log n) 而总搬运量是 O(n)）。这个论证模式在本系列后四章会反复出现。</figcaption>
</figure>

<div class="box takeaway"><span class="t">本节结论</span><p>复杂度问的是<b>增长趋势</b>而不是秒数，所以它换机器不失效。O / Ω / Θ 管的是「界」，最坏 / 平均管的是「输入」，两者不要混。
日常估算靠一条规则：<b>循环嵌套层数就是指数</b>。摊销分析则回答「偶尔很慢、平均很快」这类问题，是后面几章反复要用的工具。</p></div>

<footer>
  <p><strong>本节自测</strong> ① 下面这段代码的复杂度是多少？说出推理过程：<code>for i in range(n): for j in range(1000): pass</code>
  ② 说明为什么「快排最坏是 O(n²)，平均是 O(n log n)」这句话里两个「O」其实指同一件事（都用 Θ 也行）。
  ③ 用摊销论证解释：为什么「<code>list</code> 的 append 是 O(1)」和「append 有时候要搬整个数组」不矛盾。</p>
</footer>

<h2><span class="n">2</span>线性结构：同一组数据，四种访问模式</h2>
<p class="lede">数组、链表、栈、队列装的是同一类东西，区别只在「你怎么取它」—— 而这一点决定了它们的全部性能差异。</p>

<h3>2.1 数组与链表：连续与分散的根本取舍</h3>

<p>这一对结构值得放在一起看，因为它们是从同一个问题出发的两种相反答案。问题都是：<b>我要存一批元素，并且能按序号访问它们。</b></p>

<figure>
<svg viewBox="0 0 680 300" role="img" aria-label="数组与链表的内存布局对比">
  <g font-family="-apple-system,BlinkMacSystemFont,'Segoe UI','PingFang SC','Microsoft YaHei',Helvetica,Arial,sans-serif">
    <text x="24" y="20" font-size="11" font-weight="700" fill="#1b4f8a">数组：一段连续的内存，第 i 个元素的地址 = 基址 + i × 元素大小</text>
    <rect x="24" y="32" width="76" height="42" rx="3" fill="#eef3f8" stroke="#1b4f8a" stroke-width="1.5"/>
    <text x="62" y="58" font-size="12" fill="#1b4f8a" text-anchor="middle">10</text>
    <rect x="100" y="32" width="76" height="42" rx="3" fill="#eef3f8" stroke="#1b4f8a" stroke-width="1.5"/>
    <text x="138" y="58" font-size="12" fill="#1b4f8a" text-anchor="middle">20</text>
    <rect x="176" y="32" width="76" height="42" rx="3" fill="#eef3f8" stroke="#1b4f8a" stroke-width="1.5"/>
    <text x="214" y="58" font-size="12" fill="#1b4f8a" text-anchor="middle">30</text>
    <rect x="252" y="32" width="76" height="42" rx="3" fill="#eef3f8" stroke="#1b4f8a" stroke-width="1.5"/>
    <text x="290" y="58" font-size="12" fill="#1b4f8a" text-anchor="middle">40</text>
    <text x="62" y="90" font-size="9.5" fill="#8b949e" text-anchor="middle">+0</text>
    <text x="138" y="90" font-size="9.5" fill="#8b949e" text-anchor="middle">+4</text>
    <text x="214" y="90" font-size="9.5" fill="#8b949e" text-anchor="middle">+8</text>
    <text x="290" y="90" font-size="9.5" fill="#8b949e" text-anchor="middle">+12</text>
    <rect x="366" y="32" width="290" height="42" rx="3" fill="#f0f7f4" stroke="#0f7b5f" stroke-width="1.5"/>
    <text x="380" y="50" font-size="10.5" fill="#0f7b5f">取 xs[2]：一次乘法 + 一次访存，与 n 无关</text>
    <text x="380" y="66" font-size="10.5" fill="#0f7b5f">→ 随机访问 O(1)</text>
    <line x1="24" y1="110" x2="656" y2="110" stroke="#dfe5ea" stroke-width="1.5"/>
    <text x="24" y="132" font-size="11" font-weight="700" fill="#1b4f8a">链表：每个节点分散在内存任意位置，靠指针串起来</text>
    <rect x="24" y="144" width="104" height="42" rx="3" fill="#fff" stroke="#1b4f8a" stroke-width="1.5"/>
    <text x="76" y="170" font-size="11.5" fill="#1b4f8a" text-anchor="middle">10 | →</text>
    <path d="M132 165 H182" stroke="#1b4f8a" stroke-width="1.5" fill="none"/>
    <path d="M174 159 L184 165 L174 171" fill="none" stroke="#1b4f8a" stroke-width="1.5"/>
    <rect x="188" y="144" width="104" height="42" rx="3" fill="#fff" stroke="#1b4f8a" stroke-width="1.5"/>
    <text x="240" y="170" font-size="11.5" fill="#1b4f8a" text-anchor="middle">20 | →</text>
    <path d="M296 165 H346" stroke="#1b4f8a" stroke-width="1.5" fill="none"/>
    <path d="M338 159 L348 165 L338 171" fill="none" stroke="#1b4f8a" stroke-width="1.5"/>
    <rect x="352" y="144" width="104" height="42" rx="3" fill="#fff" stroke="#1b4f8a" stroke-width="1.5"/>
    <text x="404" y="170" font-size="11.5" fill="#1b4f8a" text-anchor="middle">30 | ⌀</text>
    <text x="24" y="206" font-size="10.5" fill="#5b6570">取第 3 个：必须从头沿着指针走两步 —— 与位置相关，与 n 无关的「一次性计算」不存在</text>
    <text x="24" y="224" font-size="10.5" fill="#5b6570">→ 按序号访问是 O(i)，即 O(n)；但「已知某个节点，删掉它」只需改两个指针 = O(1)</text>
    <line x1="24" y1="240" x2="656" y2="240" stroke="#dfe5ea" stroke-width="1.5"/>
    <text x="24" y="262" font-size="11" font-weight="700" fill="#0f7b5f">这一取舍的真实后果（不是理论差别）</text>
    <text x="24" y="282" font-size="10.5" fill="#5b6570">数组因为连续，CPU 缓存能一次抓一整块，所以「顺序遍历」比链表快数倍，尽管两者都是 O(n)。第三章会解释这一点。</text>
  </g>
</svg>
<figcaption><b>图 2 |</b> 数组与链表。图下方的最后一句话是本章最重要的一处提醒：<b>复杂度相同的两个结构，在实际机器上可能差几倍</b>。原因要等到第三章讲缓存才讲得透，这里先留下这个问号。</figcaption>
</figure>

<table>
  <thead><tr><th style="width:170px;">操作</th><th style="width:110px;">数组（Python list）</th><th style="width:110px;">链表</th><th>说明</th></tr></thead>
  <tbody>
    <tr><td>按下标取</td><td><span class="pill ok">O(1)</span></td><td><span class="pill bad">O(n)</span></td><td>数组靠地址算术，链表靠走指针。</td></tr>
    <tr><td>在末尾追加</td><td><span class="pill ok">O(1) 摊销</span></td><td><span class="pill ok">O(1)</span></td><td>数组靠扩容策略，见 §1.4。</td></tr>
    <tr><td>在开头插入</td><td><span class="pill bad">O(n)</span></td><td><span class="pill ok">O(1)</span></td><td>数组要把后面全部后移；链表只改指针。</td></tr>
    <tr><td>删除已知节点</td><td><span class="pill bad">O(n)</span></td><td><span class="pill ok">O(1)</span></td><td>注意「已知节点」这个前提 —— 链表找到这个节点本身可能已经是 O(n)。</td></tr>
    <tr><td>顺序遍历</td><td><span class="pill ok">O(n)</span></td><td><span class="pill ok">O(n)</span></td><td><b>理论上相同，实际上数组快得多</b>（缓存友好）。</td></tr>
  </tbody>
</table>

<div class="box finding"><span class="t">模型修正 2 —— 「链表插入删除快，所以该用链表」是错的</span>
<p>这个结论在教科书里正确，在真实程序里经常误导。原因是它忽略了两件事：</p>
<p><b>① 找到位置本身就要 O(n)。</b>「删除已知节点是 O(1)」的前提是「已知」—— 而在链表里找到第 k 个节点要走 k 步。
所以「删除第 k 个元素」在链表上是 O(n)，在数组上也是 O(n)（虽然数组是搬运而不是查找）。</p>
<p><b>② 数组的 O(n) 是内存搬运，链表的 O(n) 是随机访存。</b>现代 CPU 上，连续搬运 n 个元素的吞吐量远高于沿指针跳 n 次（每次都可能 cache miss）。
这就是为什么实践中 <b>list 在绝大多数场景下比手写链表更快</b>。</p>
<p>真正该用链表的场景其实很窄：<b>你已经持有节点引用</b>（例如 LRU 缓存里由哈希表直接指向节点），
或者数据量大到内存需要分片管理（例如操作系统里的空闲块链）。<b>「我觉得插入删除多」不是理由。</b></p>
</div>

<h3>2.2 栈与队列：把「顺序」本身当成语义</h3>

<p>栈和队列不是新数据结构，它们是在数组或链表上加了一层<b>访问限制</b>。限制带来的好处是：<b>接口变窄，正确性更容易保证。</b></p>

<table>
  <thead><tr><th style="width:74px;">结构</th><th style="width:130px;">规则</th><th style="width:210px;">现实对应</th><th>一旦放宽限制会怎样</th></tr></thead>
  <tbody>
    <tr><td><b>栈</b></td><td>后进先出</td><td>撤销操作、括号匹配、函数调用（第一章 §3.3 的调用栈）、深度优先搜索</td><td>你可以任意访问中间元素 —— 那就退化成数组，撤销功能要自己去追踪「撤销到哪一步」。</td></tr>
    <tr><td><b>队列</b></td><td>先进先出</td><td>打印任务排队、消息队列、广度优先搜索、请求限流</td><td>你可以插队 —— 公平性失去保证，需要额外机制来恢复。</td></tr>
  </tbody>
</table>

<pre><code><span class="cm"># Python 里直接用 list 当栈：append / pop 都在尾部，都是 O(1)</span>
stack = []
stack.append(<span class="mk">1</span>)
stack.append(<span class="mk">2</span>)
top = stack.pop()          <span class="cm"># 2</span>
<span class="cm"># 用 list 当队列是常见的错误：pop(0) 要把后面全部前移，是 O(n)</span>
queue = []
queue.append(<span class="mk">1</span>)
queue.append(<span class="mk">2</span>)
first = queue.pop(<span class="mk">0</span>)     <span class="cm"># 1，但代价是 O(n)</span>
<span class="cm"># 正确做法：collections.deque，两端操作都是 O(1)</span>
<span class="kw">from</span> collections <span class="kw">import</span> deque
queue = deque()
queue.append(<span class="mk">1</span>)
queue.append(<span class="mk">2</span>)
first = queue.popleft()    <span class="cm"># 1，O(1)</span></code></pre>

<div class="box note"><span class="t">为什么栈能保证「撤销」是对的</span>
<p>把「限制接口」的价值说具体一点：撤销功能如果用数组实现，你必须自己维护一个「当前光标」变量，而这个变量在每次操作后都要记得更新 ——
这正是第一章 §2.5 说的「多一个可能被忘记更新的变量」。</p>
<p>用栈实现则是：撤销 = <code>pop()</code>，做操作 = <code>push()</code>。没有光标变量，所以不存在「忘了更新」的可能。
<b>数据结构的作用之一，就是让某些错误在结构上不可能发生。</b>这个思路在第四章讲并发（用锁把不确定的时序变得确定）时会再次出现。</p>
</div>

<h3>2.3 一个把前面串起来的例子：括号匹配</h3>

<p>这是栈最经典的应用，值得写完整，因为它的正确性可以直接用循环不变式论证（第一章 §2.4 的方法）：</p>

<pre><code><span class="kw">def</span> balanced(s):
    pairs = {<span class="mk">")"</span>: <span class="mk">"("</span>, <span class="mk">"]"</span>: <span class="mk">"["</span>, <span class="mk">"}"</span>: <span class="mk">"{"</span>}
    stack = []
    <span class="kw">for</span> ch <span class="kw">in</span> s:
        <span class="kw">if</span> ch <span class="kw">in</span> <span class="mk">"([{"</span>:
            stack.append(ch)
        <span class="kw">elif</span> ch <span class="kw">in</span> <span class="mk">")]}"</span>:
            <span class="kw">if</span> <span class="kw">not</span> stack <span class="kw">or</span> stack[-<span class="mk">1</span>] != pairs[ch]:
                <span class="kw">return</span> <span class="kw">False</span>
            stack.pop()
    <span class="kw">return</span> <span class="kw">not</span> stack       <span class="cm"># 别忘了：还有没闭合的左括号也算不平衡</span></code></pre>

<p><b>不变式</b>：「处理完前缀 <code>s[0:i]</code> 之后，栈里存的是<b>尚未匹配的左括号，且按出现顺序自底向上排列</b>」。</p>

<table>
  <thead><tr><th style="width:104px;">步骤</th><th>为什么成立</th></tr></thead>
  <tbody>
    <tr><td><b>初始化</b></td><td><code>i = 0</code> 时没有处理任何字符，栈为空，与「没有未匹配的左括号」一致。</td></tr>
    <tr><td><b>保持</b></td><td>遇到左括号就入栈（多了一个待匹配的）；遇到右括号，栈顶必须是它的配对（否则这个右括号永远不可能被匹配），配对成功就出栈。两种情况下不变式都保持。</td></tr>
    <tr><td><b>终止</b></td><td>循环结束时处理完了整个串。此时栈空 ⟺ 没有未匹配的左括号 ⟺ 全部平衡。所以 <code>return not stack</code> 正好正确。</td></tr>
  </tbody>
</table>

<div class="box takeaway"><span class="t">本节结论</span><p>同一种数据，四种访问模式：<b>数组</b>（按位置，O(1)）、<b>链表</b>（已知位置，改指针 O(1)）、
<b>栈</b>（只看最近）、<b>队列</b>（只看最早）。后两者的价值不在性能，而在<b>把「顺序」写进类型里，让错误不可能发生</b>。</p></div>

<footer>
  <p><strong>本节自测</strong> ① 说明为什么「删除第 k 个元素在数组和链表上都是 O(n)」，但两个 O(n) 的常数因子差很多。
  ② 用 list 当队列有什么问题？给出两种正确做法。
  ③ 自己写出「判断一个字符串是否是回文」的解法，并说明用栈和用双指针哪个更好、为什么。</p>
</footer>

<h2><span class="n">3</span>哈希表：平均 O(1) 是怎么来的</h2>
<p class="lede">第一章说「判断某个值出现过没有，就用 set」。这一节推导它为什么能做到 O(1) —— 以及它在什么情况下做不到。</p>

<h3>3.1 从「按位置取」到「按内容取」</h3>

<p>数组的 O(1) 访问建立在一个前提上：<b>你事先知道位置</b>。但现实中更常见的需求是「我知道的是内容，想要的是位置」。例如：</p>

<pre><code><span class="cm"># 需求：给定受试者编号，找到他的访视记录</span>
records = [(<span class="mk">"S001"</span>, <span class="mk">4</span>), (<span class="mk">"S002"</span>, <span class="mk">3</span>), (<span class="mk">"S003"</span>, <span class="mk">5</span>), ...]
<span class="cm"># 线性扫描：每次都要一个个比对编号</span>
<span class="kw">def</span> find(records, sid):
    <span class="kw">for</span> s, v <span class="kw">in</span> records:
        <span class="kw">if</span> s == sid:
            <span class="kw">return</span> v
    <span class="kw">return</span> <span class="kw">None</span>
<span class="cm"># n 条记录，找一次是 O(n)；找 m 次是 O(n·m)</span></code></pre>

<p>哈希表的核心想法一句话就能说明：<b>把「内容」用某种计算变成「位置」。</b></p>

<figure>
<svg viewBox="0 0 680 330" role="img" aria-label="哈希表：键经哈希函数映射到桶下标，以及冲突处理">
  <g font-family="-apple-system,BlinkMacSystemFont,'Segoe UI','PingFang SC','Microsoft YaHei',Helvetica,Arial,sans-serif">
    <text x="24" y="20" font-size="10.5" font-weight="700" fill="#8b949e">查找「S003」：一次哈希计算得到下标，直接落到那一格 —— 不需要逐个比较</text>
    <rect x="24" y="34" width="120" height="34" rx="3" fill="#eef3f8" stroke="#1b4f8a" stroke-width="1.5"/>
    <text x="84" y="56" font-size="12" fill="#1b4f8a" text-anchor="middle">"S003"</text>
    <path d="M150 51 H206" stroke="#1b4f8a" stroke-width="1.5" fill="none"/>
    <path d="M198 45 L208 51 L198 57" fill="none" stroke="#1b4f8a" stroke-width="1.5"/>
    <rect x="214" y="34" width="150" height="34" rx="3" fill="#fff" stroke="#1b4f8a" stroke-width="1.5"/>
    <text x="289" y="56" font-size="11.5" fill="#1b4f8a" text-anchor="middle">hash(k) % 8</text>
    <path d="M370 51 H426" stroke="#1b4f8a" stroke-width="1.5" fill="none"/>
    <path d="M418 45 L428 51 L418 57" fill="none" stroke="#1b4f8a" stroke-width="1.5"/>
    <rect x="436" y="34" width="60" height="34" rx="3" fill="#f0f7f4" stroke="#0f7b5f" stroke-width="1.5"/>
    <text x="466" y="56" font-size="12" fill="#0f7b5f" text-anchor="middle">5</text>
    <text x="510" y="56" font-size="10.5" fill="#0f7b5f">= 桶下标，直接取</text>
    <text x="24" y="96" font-size="10.5" fill="#5b6570">总共两步：算哈希值（与键长相关，与表的大小无关）、按下标取一格。这就是「平均 O(1)」的来源。</text>
    <line x1="24" y1="112" x2="656" y2="112" stroke="#dfe5ea" stroke-width="1.5"/>
    <text x="24" y="134" font-size="11" font-weight="700" fill="#17181a">冲突：不同键算到同一个下标，必须处理</text>
    <text x="24" y="154" font-size="10.5" fill="#5b6570">办法一 · 链地址法：每个桶挂一条链（Python dict 用的是开放寻址，见下）</text>
    <rect x="24" y="166" width="42" height="30" rx="3" fill="#f7f8f9" stroke="#dfe5ea"/>
    <text x="45" y="186" font-size="10.5" fill="#5b6570" text-anchor="middle">0</text>
    <rect x="24" y="200" width="42" height="30" rx="3" fill="#f7f8f9" stroke="#dfe5ea"/>
    <text x="45" y="220" font-size="10.5" fill="#5b6570" text-anchor="middle">1</text>
    <rect x="24" y="234" width="42" height="30" rx="3" fill="#f7f8f9" stroke="#dfe5ea"/>
    <text x="45" y="254" font-size="10.5" fill="#5b6570" text-anchor="middle">2</text>
    <rect x="90" y="200" width="76" height="30" rx="3" fill="#eef3f8" stroke="#1b4f8a" stroke-width="1.2"/>
    <text x="128" y="220" font-size="10.5" fill="#1b4f8a" text-anchor="middle">"S002"</text>
    <path d="M172 215 H206" stroke="#1b4f8a" stroke-width="1.2" fill="none"/>
    <path d="M198 210 L208 215 L198 220" fill="none" stroke="#1b4f8a" stroke-width="1.2"/>
    <rect x="214" y="200" width="76" height="30" rx="3" fill="#eef3f8" stroke="#1b4f8a" stroke-width="1.2"/>
    <text x="252" y="220" font-size="10.5" fill="#1b4f8a" text-anchor="middle">"S007"</text>
    <text x="310" y="220" font-size="10.5" fill="#5b6570">← 挂在同一桶上的两个键，查找时要在这条链里比对</text>
    <line x1="24" y1="276" x2="656" y2="276" stroke="#dfe5ea" stroke-width="1.5"/>
    <text x="24" y="296" font-size="11" font-weight="700" fill="#0f7b5f">于是「O(1)」其实是有条件的</text>
    <text x="24" y="316" font-size="10.5" fill="#5b6570">链的平均长度 = 装载因子 α = 元素数 / 桶数。只要 α 是常数（Python 保持在 2/3 以下并会自动扩容），链就短，查找就是 O(1)。</text>
  </g>
</svg>
<figcaption><b>图 3 |</b> 哈希表的两步：算哈希、取桶。下半部分的冲突处理解释了「O(1)」的真实含义 —— <b>不是「永远一次命中」，而是「平均要检查的候选数是常数」</b>。这个「平均」依赖装载因子被控制在常数内。</figcaption>
</figure>

<h3>3.2 期望复杂度的推导</h3>

<p>把上面的直觉做成推导。<b>用简单均匀哈希假设</b>（每个键等概率落到每个桶，且与其他键独立）：</p>

<ol>
  <li>表里有 m 个桶，n 个键，装载因子 α = n/m。</li>
  <li>一次查找要检查的候选数，等于「落到同一个桶的键的个数」的期望值 —— 也就是 α。</li>
  <li>所以一次查找的期望代价是 <b>O(1 + α)</b>。</li>
  <li><b>只要保证 α 不超过某个常数</b>（Python 用的是 2/3），这个式子就是 O(1)。</li>
</ol>

<p>第 4 步正是「扩容」的职责：元素超过阈值就申请一块更大的表（Python 是约 4 倍或翻倍），把所有键重新计算位置搬过去。
而这次搬家的代价，靠的是<b>摊销分析</b>（§1.4）—— 与动态数组扩容是同一个论证。</p>

<div class="box finding"><span class="t">模型修正 3 —— O(1) 讲的是「平均」和「期望」，不是「任意一次」</span>
<p>三件事必须同时说清，否则「哈希表是 O(1)」会给人错误的保证感：</p>
<p><b>① 它是期望值，不是上界。</b>理论上存在一组键，全部哈希到同一个桶 —— 此时查找退化到 O(n)。
防这件事的办法有两个层次：哈希函数要足够好（让攻击者难以构造这样的键集），以及某些语言在链过长时把链转成树（Java 8 的 HashMap 就是这么做的）。</p>
<p><b>② 单次可能很慢。</b>触发扩容的那一次 <code>insert</code> 要重建整张表，是 O(n)。摊销下来才是 O(1)。</p>
<p><b>③ 「与表的大小无关」也有前提。</b>计算哈希值本身要遍历整个键 —— 对一个很长的字符串，这一步是与键长成正比的，
只是在通常的算法分析里，键被视为「一个单位」。<b>处理超长键（比如整个文件的内容）时要记得这一点。</b></p>
</div>

<h3>3.3 Python 里的三个实现细节</h3>

<p>知道这些细节不是为了考试，而是为了解释你实际会遇到的两个行为。</p>

<table>
  <thead><tr><th style="width:150px;">细节</th><th style="width:230px;">内容</th><th>你能观察到的后果</th></tr></thead>
  <tbody>
    <tr>
      <td>键必须可哈希</td>
      <td>要求「相等的对象哈希值相同」，且哈希值在对象生命周期内不变 —— 所以只有不可变对象能当键（第一章 §4.4）。</td>
      <td><code>d[[1,2]] = 1</code> 报 <code>TypeError: unhashable type</code>；要按一组值做键就用 tuple。</td>
    </tr>
    <tr>
      <td>开放寻址（而非链地址）</td>
      <td>Python dict 把冲突的键存在表内的下一个空位，而不是挂链；查找时按固定探测序列往后找。</td>
      <td>内存更紧凑、缓存更友好，但删除需要「墓碑」标记 —— 这也是为什么 dict 的内存占用在不同版本间变化过。</td>
    </tr>
    <tr>
      <td>保持插入顺序（3.7+）</td>
      <td>Python 3.7 起，dict 的遍历顺序 = 插入顺序。这是一个<b>语言保证</b>，不是实现巧合。</td>
      <td>可以放心地用 <code>list(d)</code> 拿到插入序的键；但这与「有序字典」是两件事 —— 它不按 key 排序。</td>
    </tr>
  </tbody>
</table>

<div class="box note"><span class="t">一个必须记住的对比：<code>set</code> vs <code>list</code> 的判断代价</span>
<p>第一章说「<code>x in some_list</code> 和 <code>x in some_set</code> 写法一样，代价差几个数量级」，现在可以给出精确表述：</p>

<pre><code><span class="cm"># 在一批数据里找出「首次出现」的元素</span>
<span class="kw">def</span> first_unique(nums):
    <span class="cm"># 用 list 计数：每个元素都要扫描已收集的列表</span>
    <span class="cm"># 总代价 O(n²)</span>
    seen = []
    <span class="kw">for</span> x <span class="kw">in</span> nums:
        <span class="kw">if</span> x <span class="kw">not</span> <span class="kw">in</span> seen:
            seen.append(x)
    <span class="cm"># 用 dict 计数：每个元素一次哈希，总代价 O(n)</span>
    counts = {}
    <span class="kw">for</span> x <span class="kw">in</span> nums:
        counts[x] = counts.get(x, <span class="mk">0</span>) + <span class="mk">1</span></code></pre>
<p>n = 10 万时，这是「几秒」与「跑不完」的差别。<b>而代码看起来几乎一样</b> —— 这是本章最值得记住的一类优化：
它不是「写得更聪明」，而是「选对结构」。</p>
</div>

<h3>3.4 什么时候不该用哈希表</h3>

<p>哈希表很强，但它有一个明确的能力缺口：<b>它不保持顺序。</b>凡是「范围查询」「按大小取前 k 个」「有序遍历」的需求，哈希表都无法胜任。
这时需要的是 §4 的树。</p>

<table>
  <thead><tr><th style="width:190px;">需求</th><th style="width:130px;">哈希表</th><th>该用什么</th></tr></thead>
  <tbody>
    <tr><td>按键精确查找</td><td><span class="pill ok">O(1) 平均</span></td><td>哈希表，这是它的主场。</td></tr>
    <tr><td>找出 18 到 65 岁之间的记录</td><td><span class="pill bad">不支持</span></td><td>有序结构（平衡树、跳表）或对键排好序后二分。</td></tr>
    <tr><td>按从小到大遍历所有键</td><td><span class="pill bad">不支持</span></td><td><code>sorted(d.items())</code> 是一次 O(n log n) 的排序，而不是遍历。</td></tr>
    <tr><td>取最小的 k 个</td><td><span class="pill bad">不支持</span></td><td>堆（§4.4）。</td></tr>
  </tbody>
</table>

<div class="box takeaway"><span class="t">本节结论</span><p>哈希表把「内容」变成「位置」，所以查找平均是 O(1) —— 但这个 O(1) 是<b>期望值</b>，
成立条件是装载因子被控制在常数内。</p><p>它换来的是顺序的丧失：任何与「顺序」有关的需求，哈希表都做不了。这不是缺陷，而是取舍的代价 —— 下一节的树正是用 O(log n) 换回顺序。</p></div>

<footer>
  <p><strong>本节自测</strong> ① 用自己的话解释「平均 O(1)」中的「平均」是对什么取平均。
  ② 为什么 <code>k = sorted(d)[0]</code> 这种「取字典里最小的键」的写法是 O(n log n)，而堆能做到 O(n)？
  ③ 有一个需求是「统计每个编号出现次数，并最后按编号从小到大输出」。用 dict 怎么写？总共多少代价？</p>
</footer>

<h2><span class="n">4</span>树与堆：用 O(log n) 把顺序买回来</h2>

<p>上一节结尾留下了哈希表的缺口：它能 O(1) 地回答「这个键在不在」，却回答不了「比 33 大的最小键是谁」。
如果有一张表的键是有序的，并且你总能<b>一步砍掉一半</b>，那么 n 个键里定位任意一个只需要 30 步。
§4 讲的就是怎么把这种结构维持住 —— 而且是在不断插入、删除的情况下仍然维持住。</p>

<h3>4.1 从二分查找说起：有序性值多少钱</h3>

<p>第一章 §2.4 留过一个承诺：二分的循环不变式会在本章结清。先看代码，这次把不变式写在开头。</p>

<pre><code><span class="cm"># 前提：a 已经从小到大排好序</span>
<span class="cm"># 循环不变式：若 t 在 a 中，则它一定落在 [lo, hi) 这个区间里</span>
<span class="cm"># 初始 lo=0, hi=len(a)：整个数组满足不变式</span>
<span class="kw">def</span> <span class="mk">bsearch</span>(a, t):
    lo, hi = <span class="mk">0</span>, len(a)          <span class="cm"># hi 是「开」的：区间不含 hi</span>
    <span class="kw">while</span> lo &lt; hi:                <span class="cm"># 区间非空时继续</span>
        mid = (lo + hi) // <span class="mk">2</span>
        <span class="kw">if</span> a[mid] == t:
            <span class="kw">return</span> mid
        <span class="kw">elif</span> a[mid] &lt; t:
            lo = mid + <span class="mk">1</span>       <span class="cm"># a[mid] 及左边都不可能是答案</span>
        <span class="kw">else</span>:
            hi = mid               <span class="cm"># a[mid] 及右边都不可能是答案</span>
    <span class="kw">return</span> -<span class="mk">1</span>                    <span class="cm"># 区间空 → 不变式逼出结论：t 不在 a 中</span></code></pre>

<p>三处细节都直接来自不变式，不是「习惯写法」：</p>

<ul>
  <li><b>区间是半开的 <code>[lo, hi)</code></b>。这样「空区间」就是 <code>lo == hi</code>，循环条件写成 <code>lo &lt; hi</code> 就够，不需要
  再讨论 <code>lo &lt;= hi</code> 时 mid 越界的问题。</li>
  <li><b>回写时 <code>lo = mid + 1</code> 但 <code>hi = mid</code></b>。因为 hi 本身不在区间里：新的左端点必须跳过已排除的 mid（+1），
  而新的右端点「取到 mid」就已经把它排除了。</li>
  <li><b><code>a[mid] == t</code> 可以直接返回</b>，是因为我们要找「任意一个」相等的位置。如果要找<b>第一个</b>相等的（lower_bound），
  这一支就不能返回，得写成 <code>hi = mid</code> 继续往左收。</li>
</ul>

<div class="box note"><span class="t">为什么二分容易写错</span><p>二分被公认为「思路对但边界错」的典型。原因不是边界难，而是
<b>不变式没有写下来</b>。一旦把「答案在这半开区间里」写在注释里，三处边界就被它唯一确定了，没有可挑选的余地。
凡是「循环里维护一个不变式」的算法（二分、快排的分区、并查集、KMP），写法错误几乎都能追溯到不变式模糊。</p></div>

<p>现在算清楚有序性值多少钱。<b>想一下</b>：如果数组无序，找出某个值只能逐个看，n 次；排好序之后是 log₂n 次。
n = 100 万时，是 100 万次对 20 次 —— 差了 5 万倍。这就是 §4 全部内容的动机：<b>维护顺序是有成本的，
但一旦维持住了，查询的收益大到足以覆盖它。</b></p>

<figure>
<svg viewBox="0 0 640 224" role="img" aria-label="二分查找每步砍掉一半，以及对数增长与线性增长的对比">
  <text x="0" y="14" fill="#5b6068" font-size="11" font-family="sans-serif">每次比较把候选区间砍掉一半</text>
  <g font-family="sans-serif" font-size="12">
    <text x="0" y="46" fill="#17181a">第 1 步</text>
    <rect x="70" y="34" width="440" height="16" fill="none" stroke="#1b4f8a" stroke-width="1"/>
    <rect x="290" y="34" width="220" height="16" fill="none" stroke="#0f7b5f" stroke-width="2"/>
    <text x="522" y="46" fill="#5b6068" font-size="11">剩 1/2</text>
    <text x="0" y="74" fill="#17181a">第 2 步</text>
    <rect x="290" y="62" width="220" height="16" fill="none" stroke="#1b4f8a" stroke-width="1"/>
    <rect x="290" y="62" width="110" height="16" fill="none" stroke="#0f7b5f" stroke-width="2"/>
    <text x="522" y="74" fill="#5b6068" font-size="11">剩 1/4</text>
    <text x="0" y="102" fill="#17181a">第 3 步</text>
    <rect x="290" y="90" width="110" height="16" fill="none" stroke="#1b4f8a" stroke-width="1"/>
    <rect x="345" y="90" width="55" height="16" fill="none" stroke="#0f7b5f" stroke-width="2"/>
    <text x="522" y="102" fill="#5b6068" font-size="11">剩 1/8</text>
    <text x="0" y="130" fill="#17181a">第 20 步</text>
    <rect x="400" y="118" width="1" height="16" fill="#0f7b5f" stroke="#0f7b5f" stroke-width="1"/>
    <text x="522" y="130" fill="#5b6068" font-size="11">剩 1/100 万</text>
  </g>
  <line x1="0" y1="156" x2="600" y2="156" stroke="#d8dbe0" stroke-width="1"/>
  <g font-family="sans-serif" font-size="11">
    <text x="0" y="178" fill="#17181a">n = 100 万时的比较次数</text>
    <text x="0" y="200" fill="#0f7b5f">二分：约 20 次</text>
    <text x="96" y="200" fill="#5b6068">（log₂ 10⁶ ≈ 19.9）</text>
    <text x="270" y="200" fill="#b4463c">逐个扫描：最坏 100 万次</text>
  </g>
</svg>
<figcaption>图 4　二分查找每步把候选区间减半，20 步就能覆盖一百万个元素。这是「对数」在工程里最直观的一次亮相。</figcaption>
</figure>

<div class="box note"><span class="t">二分的前提是「随机访问」</span><p>二分能跳着走，依赖 <code>a[mid]</code> 是 O(1) 的。
<p>数组满足这一点，链表不满足 —— 在链表上「跳到中间」本身就要 O(n)，二分退化成 O(n log n)，比直接扫还慢。
这一条会在第三章（存储器层次）里再回看一次：<b>数组的随机访问便宜，不只是因为寻址公式，还因为 CPU 会帮你提前把邻近的数据搬进缓存。</b></p></div>

<h3>4.2 二叉搜索树：把有序性做成结构</h3>

<p>数组的问题在于插入和删除：往中间插一个元素，后面全部要挪位，O(n)。能不能既要有序，又要 O(log n) 的插入？
把二分的过程「反过来」做成结构就行 —— 不是让检索去找数据，而是让数据按照二分的方式组织起来。</p>

<div class="box note"><span class="t">二叉搜索树（BST）的定义</span><p>每个结点存一个键，并且满足：<b>左子树里所有键都小于根，右子树里所有键都大于根</b>，
且这个性质对每一棵子树都成立。查找时从根出发，比根小就往左、比根大就往右 —— 每一步的决策和二分完全一样。</p></div>

<figure>
<svg viewBox="0 0 640 270" role="img" aria-label="一棵二叉搜索树与一次查找路径的对比">
  <text x="0" y="14" fill="#5b6068" font-size="11" font-family="sans-serif">查找 62：从根出发，每步排除一整棵子树</text>
  <g stroke="#1b4f8a" stroke-width="1">
    <line x1="310" y1="56" x2="190" y2="112"/>
    <line x1="310" y1="56" x2="430" y2="112"/>
    <line x1="190" y1="112" x2="120" y2="168"/>
    <line x1="190" y1="112" x2="260" y2="168"/>
    <line x1="430" y1="112" x2="360" y2="168"/>
    <line x1="430" y1="112" x2="500" y2="168"/>
    <line x1="500" y1="168" x2="500" y2="224"/>
  </g>
  <g font-family="sans-serif" font-size="13" text-anchor="middle" dominant-baseline="central">
    <circle cx="310" cy="56" r="21" fill="#fff" stroke="#0f7b5f" stroke-width="2"/>
    <text x="310" y="56" fill="#0f7b5f">50</text>
    <circle cx="190" cy="112" r="21" fill="#fff" stroke="#1b4f8a" stroke-width="1"/>
    <text x="190" y="112" fill="#17181a">30</text>
    <circle cx="430" cy="112" r="21" fill="#fff" stroke="#0f7b5f" stroke-width="2"/>
    <text x="430" y="112" fill="#0f7b5f">70</text>
    <circle cx="120" cy="168" r="21" fill="#fff" stroke="#1b4f8a" stroke-width="1"/>
    <text x="120" y="168" fill="#17181a">15</text>
    <circle cx="260" cy="168" r="21" fill="#fff" stroke="#1b4f8a" stroke-width="1"/>
    <text x="260" y="168" fill="#17181a">40</text>
    <circle cx="360" cy="168" r="21" fill="#fff" stroke="#0f7b5f" stroke-width="2"/>
    <text x="360" y="168" fill="#0f7b5f">62</text>
    <circle cx="500" cy="168" r="21" fill="#fff" stroke="#1b4f8a" stroke-width="1"/>
    <text x="500" y="168" fill="#17181a">85</text>
    <circle cx="500" cy="224" r="21" fill="#fff" stroke="#1b4f8a" stroke-width="1"/>
    <text x="500" y="224" fill="#17181a">90</text>
  </g>
  <g font-family="sans-serif" font-size="11">
    <text x="0" y="256" fill="#0f7b5f">62 &gt; 50 往右　→　62 &lt; 70 往左　→　命中。第一次比较就排除了左子树的全部结点（15、30、40）</text>
  </g>
</svg>
<figcaption>图 5　BST 的查找路径。深绿结点是实际比较过的：查 62 只用了 3 次比较。形状恰好时，树高 ≈ log₂n。</figcaption>
</figure>

<p>BST 的三种遍历也值得记一下，它们决定了输出顺序：</p>

<table>
  <thead><tr><th style="width:130px;">遍历</th><th style="width:200px;">访问顺序</th><th>用途</th></tr></thead>
  <tbody>
    <tr><td>中序 in-order</td><td>左 → 根 → 右</td><td><b>输出严格递增的序列</b>。这是「有序性」最直接的体现：BST 排序只要一次中序遍历，O(n)。</td></tr>
    <tr><td>前序 pre-order</td><td>根 → 左 → 右</td><td>序列化/反序列化一棵树（先写根才能知道往哪接）。</td></tr>
    <tr><td>后序 post-order</td><td>左 → 右 → 根</td><td>先算子树再汇总：算目录大小、释放内存、表达式求值。</td></tr>
  </tbody>
</table>

<h3>4.3 平衡：BST 的病与药</h3>

<p>BST 的查找代价是<b>树高</b>，不是结点数。麻烦在于树高取决于插入顺序，而插入顺序通常不由你决定。</p>

<figure>
<svg viewBox="0 0 660 230" role="img" aria-label="同一组键按不同顺序插入得到极不平衡与平衡两种形状">
  <text x="0" y="16" fill="#5b6068" font-size="11" font-family="sans-serif">同一组键 {10,20,30,40,50}，两种插入顺序</text>
  <g font-family="sans-serif" font-size="12">
    <text x="0" y="46" fill="#b4463c">按 10,20,30,40,50 插入 → 退化成链表，树高 5</text>
  </g>
  <g font-family="sans-serif" font-size="12" text-anchor="middle">
    <circle cx="60" cy="76" r="16" fill="none" stroke="#b4463c" stroke-width="1"/>
    <text x="60" y="80" fill="#17181a">10</text>
    <line x1="76" y1="76" x2="112" y2="76" stroke="#b4463c" stroke-width="1"/>
    <circle cx="128" cy="76" r="16" fill="none" stroke="#b4463c" stroke-width="1"/>
    <text x="128" y="80" fill="#17181a">20</text>
    <line x1="144" y1="76" x2="180" y2="76" stroke="#b4463c" stroke-width="1"/>
    <circle cx="196" cy="76" r="16" fill="none" stroke="#b4463c" stroke-width="1"/>
    <text x="196" y="80" fill="#17181a">30</text>
    <line x1="212" y1="76" x2="248" y2="76" stroke="#b4463c" stroke-width="1"/>
    <circle cx="264" cy="76" r="16" fill="none" stroke="#b4463c" stroke-width="1"/>
    <text x="264" y="80" fill="#17181a">40</text>
    <line x1="280" y1="76" x2="316" y2="76" stroke="#b4463c" stroke-width="1"/>
    <circle cx="332" cy="76" r="16" fill="none" stroke="#b4463c" stroke-width="1"/>
    <text x="332" y="80" fill="#17181a">50</text>
  </g>
  <text x="0" y="132" fill="#0f7b5f" font-family="sans-serif" font-size="12">按 30,10,20,40,50 插入 → 树高 3</text>
  <g font-family="sans-serif" font-size="12" text-anchor="middle">
    <line x1="330" y1="162" x2="270" y2="196" stroke="#1b4f8a" stroke-width="1"/>
    <line x1="330" y1="162" x2="400" y2="196" stroke="#1b4f8a" stroke-width="1"/>
    <circle cx="330" cy="162" r="16" fill="none" stroke="#0f7b5f" stroke-width="2"/>
    <text x="330" y="166" fill="#0f7b5f">30</text>
    <circle cx="270" cy="196" r="16" fill="none" stroke="#1b4f8a" stroke-width="1"/>
    <text x="270" y="200" fill="#17181a">10</text>
    <circle cx="400" cy="196" r="16" fill="none" stroke="#1b4f8a" stroke-width="1"/>
    <text x="400" y="200" fill="#17181a">40</text>
    <line x1="286" y1="196" x2="330" y2="196" stroke="#1b4f8a" stroke-width="1"/>
    <circle cx="346" cy="196" r="16" fill="none" stroke="#1b4f8a" stroke-width="1"/>
    <text x="346" y="200" fill="#17181a">20</text>
    <line x1="416" y1="196" x2="464" y2="196" stroke="#1b4f8a" stroke-width="1"/>
    <circle cx="480" cy="196" r="16" fill="none" stroke="#1b4f8a" stroke-width="1"/>
    <text x="480" y="200" fill="#17181a">50</text>
  </g>
</svg>
<figcaption>图 6　退化：有序数据依次插入 BST 会变成一条链，查找退化为 O(n)。这正是「平衡」要解决的问题 —— 插入后主动旋转，把树高钉死在 O(log n)。</figcaption>
</figure>

<div class="box finding"><span class="t">模型修正</span><p>「BST 的查找是 O(log n)」这句话<b>只在树平衡时成立</b>。
精确说法是：BST 的查找代价是 O(h)，h 是树高；h 在最好情况下是 log₂n，最坏是 n。
<p>如果你要往 BST 里插入一批已经排好序的数据（很常见：日志按时间到达、编号按序分配），退化不是「可能」而是「必然」。
所以工业界几乎不用裸 BST，用的是<b>自平衡</b>变体：AVL 树、红黑树（C++ <code>std::map</code>、Java <code>TreeMap</code>、Linux 内核的 CFS 调度器）、
B 树/B+ 树（第六章数据库的索引结构）。它们通过「旋转」在插入后把树高差控制在常数内，把最坏 O(n) 变成保证 O(log n)。</p></div>

<div class="box note"><span class="t">回看点（第三章）</span><p>B 树不是二叉的 —— 一个结点存几百个键。为什么数据库宁可要「矮胖」也不要「瘦高」？
因为一次结点访问通常意味着一次磁盘 I/O，而 I/O 的次数等于树高。把分支因子从 2 提到 100，树高就按 log₁₀₀ 而不是 log₂ 增长：
十亿条记录，二叉要 30 层、100 叉只要 5 层。<b>这是「复杂度相同但常数差一个数量级」的又一个实例。</b></p></div>

<h3>4.4 堆：只要「最值」，不要全序</h3>

<p>现在换一个需求。假设有一个任务队列，每个任务有优先级，你只需要反复问同一个问题：<b>当前优先级最高的任务是谁？</b>
用有序数组：每次取最大 O(1)，但插入要挪位 O(n)。
用 BST：两者都 O(log n)，但为了取一个最大值去维护整棵树的全序，属于杀鸡用牛刀。</p>

<p>堆给出的答案很精确：<b>放弃整体有序，只维护一条弱得多的性质 —— 父结点不小于（或不大于）两个子结点。</b>
这条性质只保证了「根是全局最值」，对兄弟之间、堂兄弟之间的顺序不做任何要求。</p>

<figure>
<svg viewBox="0 0 640 216" role="img" aria-label="大顶堆的结构：只保证父结点不小于子结点">
  <text x="0" y="14" fill="#5b6068" font-size="11" font-family="sans-serif">大顶堆：只保证「父 ≥ 子」，不保证任何横向顺序</text>
  <g stroke="#1b4f8a" stroke-width="1">
    <line x1="170" y1="58" x2="104" y2="108"/>
    <line x1="170" y1="58" x2="236" y2="108"/>
    <line x1="104" y1="108" x2="66" y2="158"/>
    <line x1="104" y1="108" x2="142" y2="158"/>
    <line x1="236" y1="108" x2="198" y2="158"/>
    <line x1="236" y1="108" x2="274" y2="158"/>
  </g>
  <g font-family="sans-serif" font-size="12" text-anchor="middle" dominant-baseline="central">
    <circle cx="170" cy="58" r="21" fill="#fff" stroke="#0f7b5f" stroke-width="2"/>
    <text x="170" y="58" fill="#0f7b5f">91</text>
    <circle cx="104" cy="108" r="19" fill="#fff" stroke="#1b4f8a" stroke-width="1"/>
    <text x="104" y="108" fill="#17181a">72</text>
    <circle cx="236" cy="108" r="19" fill="#fff" stroke="#1b4f8a" stroke-width="1"/>
    <text x="236" y="108" fill="#17181a">58</text>
    <circle cx="66" cy="158" r="19" fill="#fff" stroke="#1b4f8a" stroke-width="1"/>
    <text x="66" y="158" fill="#17181a">35</text>
    <circle cx="142" cy="158" r="19" fill="#fff" stroke="#1b4f8a" stroke-width="1"/>
    <text x="142" y="158" fill="#17181a">41</text>
    <circle cx="198" cy="158" r="19" fill="#fff" stroke="#1b4f8a" stroke-width="1"/>
    <text x="198" y="158" fill="#17181a">17</text>
    <circle cx="274" cy="158" r="19" fill="#fff" stroke="#1b4f8a" stroke-width="1"/>
    <text x="274" y="158" fill="#17181a">23</text>
  </g>
  <g font-family="sans-serif" font-size="11">
    <text x="330" y="58" fill="#5b6068">注意 41 与 35 谁大谁小无关紧要；</text>
    <text x="330" y="78" fill="#5b6068">但 41 一定不超过它的父亲 72，</text>
    <text x="330" y="98" fill="#5b6068">58 一定不超过 91。</text>
    <text x="330" y="128" fill="#5b6068">「局部有序」是堆的全部承诺 ——</text>
    <text x="330" y="148" fill="#5b6068">用更弱的不变式换更便宜的操作。</text>
    <text x="0" y="196" fill="#5b6068">存法：完全二叉树按层编号，下标 i 的左右孩子是 2i+1、2i+2，父亲是 (i−1)/2 —— 不需要任何指针。</text>
  </g>
</svg>
<figcaption>图 7　大顶堆。只要「父 ≥ 子」，根结点就必然是全局最大值，而不需要任何全局比较。</figcaption>
</figure>

<p>堆还有一个漂亮的工程事实：<b>它不需要指针，直接用数组存。</b>完全二叉树按层编号后，编号 i 的左右孩子恰好是 2i+1、2i+2，父亲是 (i-1)/2。
没有指针、没有额外内存、父子的移动就是下标算术 —— 这是 §2 提到的「用位置关系代替显式指针」的又一次胜利。</p>

<pre><code><span class="kw">import</span> heapq
h = []
heapq.heappush(h, <span class="mk">5</span>)          <span class="cm"># 插入：放到末尾，再「上浮」到不超过父亲为止</span>
heapq.heappush(h, <span class="mk">2</span>)
heapq.heappush(h, <span class="mk">9</span>)
heapq.heappush(h, <span class="mk">7</span>)
heapq.heappop(h)                <span class="cm"># 弹出：取走根(最小值)，把末尾元素搬到根再「下沉」</span>
                                <span class="cm"># 上浮/下沉都只沿着一条从根到叶的路径，代价 = 树高 = O(log n)</span>
<span class="cm"># Python 的 heapq 是小顶堆。要大顶堆就存负数，或者存 (priority, item)。</span>
<span class="cm"># 取最小的 3 个：比 sorted(h)[:3] 便宜得多（后者 O(n log n)）</span>
<span class="kw">for</span> _ <span class="kw">in</span> range(<span class="mk">3</span>):
    <span class="kw">print</span>(heapq.heappop(h))
<span class="cm"># nlargest / nsmallest 内部就是「大小为 k 的堆」，n 很大 k 很小时优势明显</span>
<span class="kw">import</span> heapq <span class="kw">as</span> h2
h2.nsmallest(<span class="mk">3</span>, [<span class="mk">5</span>, <span class="mk">1</span>, <span class="mk">9</span>, <span class="mk">3</span>, <span class="mk">7</span>])   <span class="cm"># [1, 3, 5]</span></code></pre>

<table>
  <thead><tr><th style="width:200px;">操作</th><th style="width:150px;">堆</th><th>说明</th></tr></thead>
  <tbody>
    <tr><td>查看最值</td><td><span class="pill ok">O(1)</span></td><td>就是根，直接读 <code>h[0]</code>。</td></tr>
    <tr><td>插入</td><td><span class="pill ok">O(log n)</span></td><td>上浮，只走一条路径。</td></tr>
    <tr><td>弹出最值</td><td><span class="pill ok">O(log n)</span></td><td>下沉，只走一条路径。</td></tr>
    <tr><td>从无序数组建堆</td><td><span class="pill ok">O(n)</span></td><td>自底向上下沉。<b>不是 O(n log n)</b> —— 因为大部分结点离叶子很近，下沉步数很少，求和后是线性。</td></tr>
    <tr><td>查找任意一个元素</td><td><span class="pill bad">O(n)</span></td><td>堆不提供这个能力。要「按值查找 + 取最值」，得用别的东西。</td></tr>
    <tr><td>有序遍历</td><td><span class="pill bad">不支持</span></td><td>反复 pop 能得到降序，但那会破坏堆本身。</td></tr>
  </tbody>
</table>

<div class="box note"><span class="t">回看点（第七章）</span><p>堆在系统里的地位被低估了：操作系统用堆做<b>定时器</b>（最近的超时事件在根）、
Linux CFS 调度器早期版本用堆挑出最小虚拟运行时间的进程、Dijkstra 最短路（§6.3）靠堆把 O(V²) 压到 O(E log V)、
Huffman 编码（§7.2）靠反复取两个最小值。凡是「反复问最值」的地方，背后几乎都是一个堆。</p></div>

<footer>
  <p><strong>本节自测</strong> ① 一个 BST 中序遍历后得到 [3,5,7,9]。画出至少两种可能的树形状，并说明树高为何不同。
  ② 为什么「从无序数组建堆」能做到 O(n)，而「排序」做不到低于 O(n log n)？（提示：堆没有承诺让你拿到有序序列，它承诺得更少。）
  ③ 需要用堆来管理「优先队列」，同时又要能够按 id 删除任意一个任务。堆能直接做到吗？如果不行，你会怎么补上？（这一问会在第五章的「索引结构」里再次出现。）</p>
</footer>

<h2><span class="n">5</span>排序与查找：一个被证明无法再快的任务</h2>

<p>排序是整个计算机科学里被研究得最透的问题，没有之一。它的特殊之处在于：<b>我们不仅知道怎么做，还知道做不到多快。</b>
这一节会把「下界」这个思想讲清楚 —— 它是本章唯一一处「证明某件事不可能」，也是你日后判断「这个优化还有没有空间」的通用工具。</p>

<h3>5.1 先分清：内排序与外排序</h3>

<p>排序的算法选择，第一个分岔不是「快不快」，而是<b>数据装不装得下内存</b>。</p>

<table>
  <thead><tr><th style="width:150px;">类型</th><th style="width:230px;">前提</th><th>代表算法</th></tr></thead>
  <tbody>
    <tr><td>内排序</td><td>所有数据能一次性放进内存</td><td>快速排序、归并排序、堆排序。本章讨论的默认是这一类。</td></tr>
    <tr><td>外排序</td><td>数据大于内存，必须借助磁盘</td><td>归并排序的扩展：分段排序 → 多路归并。数据库的 <code>ORDER BY</code> 走的就是这条路。</td></tr>
  </tbody>
</table>

<p>为什么外排序几乎必然是「归并」？因为归并只要求<b>顺序扫描</b>输入，一次读出、一次写入，对磁盘极其友好；
而快排的分区会来回跳跃访问，在磁盘上等于反复随机读。这个理由要到第六章（数据库）和第三章（存储层次）才彻底讲透，
先记住结论：<b>算法好不好，取决于它在哪一层存储上跑。</b></p>

<h3>5.2 三个 O(n log n) 算法，三种性格</h3>

<div class="box note"><span class="t">归并排序：先分到最小，再合并回来</span>
<p>把数组从中间劈成两半，递归排好两半，然后把两个已经有序的序列<b>合并</b>成一个有序序列。
合并的代价是 O(n)（两个指针各扫一遍），劈成 log n 层，所以总共 O(n log n)。</p></div>

<pre><code><span class="kw">def</span> <span class="mk">merge_sort</span>(a):
    <span class="kw">if</span> len(a) &lt;= <span class="mk">1</span>:
        <span class="kw">return</span> a                      <span class="cm"># 一个元素天然有序：递归的基例</span>
    mid = len(a) // <span class="mk">2</span>
    L = merge_sort(a[:mid])          <span class="cm"># 递归：左边排好（这个切片本身是 O(n) 的复制）</span>
    R = merge_sort(a[mid:])          <span class="cm"># 递归：右边排好</span>
    out, i, j = [], <span class="mk">0</span>, <span class="mk">0</span>
    <span class="kw">while</span> i &lt; len(L) <span class="kw">and</span> j &lt; len(R):
        <span class="cm"># 取两堆里较小的那个头，摘下来放进结果 —— 这一步保证结果有序</span>
        <span class="kw">if</span> L[i] &lt;= R[j]:
            out.append(L[i]); i += <span class="mk">1</span>
        <span class="kw">else</span>:
            out.append(R[j]); j += <span class="mk">1</span>
    out += L[i:] + R[j:]             <span class="cm"># 剩下那一堆必然已经有序，直接接上</span>
    <span class="kw">return</span> out</code></pre>

<p>归并的三个性质决定了它的适用场景：<b>稳定</b>（相等的元素保持原相对顺序，因为判断用的是 <code>&lt;=</code>）；
<b>代价可预测</b>（永远 O(n log n)，没有最坏情况）；<b>需要额外空间 O(n)</b>（合并时要一块和原数组等大的地方）。
pandas 的 <code>sort_values</code>、Python 的 <code>sorted</code> 都要求稳定 —— 因为「先按城市排，再按年龄排」这种多关键字排序，
要靠稳定性把前一次的顺序保留下来。</p>

<div class="box note"><span class="t">快速排序：选一个基准，把数组劈成「小的一边」和「大的一边」</span>
<p>取一个基准值 pivot，扫描一遍把小于它的放左边、大于它的放右边（这一步叫<b>分区</b>），然后对两边递归。
平均 O(n log n)，但最坏是 O(n²)。</p></div>

<pre><code><span class="kw">def</span> <span class="mk">quicksort</span>(a, lo=<span class="mk">0</span>, hi=<span class="mk">None</span>):
    <span class="kw">if</span> hi <span class="kw">is</span> None:
        hi = len(a) - <span class="mk">1</span>
    <span class="kw">if</span> lo &gt;= hi:
        <span class="kw">return</span>                          <span class="cm"># 区间长度 ≤ 1，已有序</span>
    pivot = a[(lo + hi) // <span class="mk">2</span>]
    i, j = lo, hi
    <span class="kw">while</span> i &lt;= j:
        <span class="kw">while</span> a[i] &lt; pivot: i += <span class="mk">1</span>  <span class="cm"># 找左边第一个 ≥ pivot 的</span>
        <span class="kw">while</span> a[j] &gt; pivot: j -= <span class="mk">1</span>  <span class="cm"># 找右边第一个 ≤ pivot 的</span>
        <span class="kw">if</span> i &lt;= j:
            a[i], a[j] = a[j], a[i]   <span class="cm"># 交换，两边各归位一个</span>
            i += <span class="mk">1</span>; j -= <span class="mk">1</span>
    <span class="cm"># 此时 [lo, j] 全 ≤ pivot，[i, hi] 全 ≥ pivot</span>
    quicksort(a, lo, j)
    quicksort(a, i, hi)</code></pre>

<div class="box finding"><span class="t">模型修正</span><p>「快排平均最快」这句话容易被误读成「快排一定比归并快」。真实情况是：
<p>① 快排的常数因子小（原地交换、无额外数组），所以在内存里通常确实更快；<br>
② 但它的 O(n log n) 是<b>期望</b>复杂度，取决于基准选得好不好。<b>如果每次分区都极度不均（比如固定取首元素，而输入恰好已经有序），
递归深度变成 n，总共 O(n²)，并且递归栈会爆掉。</b>这是真实事故的常见来源（早期很多库因此被有计划地攻击）。<br>
③ 工程上的对策是「随机选基准」或「三数取中」，把最坏情况变成可控的期望 —— 注意这不是消除最坏情况，而是让别人无法构造它。<br>
④ 另外，现代库用的是<b>混合策略</b>：Python 的 <code>sorted</code> 用 Timsort（归并 + 插入排序，对已有部分有序的数据特别快），
C++ <code>std::sort</code> 用 Introsort（快排 + 堆排兜底 + 小区间用插入排序）。没有人在生产里手写纯快排。</p></div>

<div class="box note"><span class="t">堆排序：用 §4 的堆，原地完成</span>
<p>先把数组建堆（O(n)），然后反复「把根（最大值）和末尾交换，堆大小减一，再下沉」。
每次下沉 O(log n)，做 n 次，总共 O(n log n)。它不需要额外空间，且最坏情况保证 O(n log n)，但常数比快排大、对缓存不友好，所以实际少用。</p></div>

<table>
  <thead><tr><th style="width:130px;">算法</th><th style="width:110px;">平均</th><th style="width:110px;">最坏</th><th style="width:90px;">额外空间</th><th style="width:80px;">稳定</th><th>什么时候选它</th></tr></thead>
  <tbody>
    <tr><td>归并排序</td><td>O(n log n)</td><td>O(n log n)</td><td>O(n)</td><td><span class="pill ok">稳定</span></td><td>要求稳定、或者数据在磁盘上（外排序）。</td></tr>
    <tr><td>快速排序</td><td>O(n log n)</td><td><span class="pill bad">O(n²)</span></td><td>O(log n)</td><td><span class="pill bad">不稳定</span></td><td>内存里的通用排序，要最快。</td></tr>
    <tr><td>堆排序</td><td>O(n log n)</td><td>O(n log n)</td><td>O(1)</td><td><span class="pill bad">不稳定</span></td><td>空间严格受限，且必须防最坏情况。</td></tr>
    <tr><td>插入排序</td><td>O(n²)</td><td>O(n²)</td><td>O(1)</td><td><span class="pill ok">稳定</span></td><td>n 很小（如 &lt; 32），或数据几乎已有序时是 O(n)。</td></tr>
    <tr><td>计数/桶排序</td><td>O(n+k)</td><td>O(n+k)</td><td>O(n+k)</td><td><span class="pill ok">可稳定</span></td><td>数据是范围有限的小整数。<b>不受下面的下界约束。</b></td></tr>
  </tbody>
</table>

<div class="box note"><span class="t">插入排序为什么还活着</span><p>它是最慢的，却是所有高效排序算法的收尾工序。
原因有两个：一是 n 很小时 O(n²) 的常数因子优势压过 O(n log n)（当 n=16，16²=256 次比较 vs 16×4=64 次，但前者是顺序内存访问、分支可预测）；
二是<b>它对「几乎已排好序」的输入是 O(n)</b> —— 每个元素只要看前一个就停。真实数据往往接近有序，这个性质价值极高。</p></div>

<h3>5.3 下界：为什么比较排序不可能快过 O(n log n)</h3>

<p>讲完怎么做，讲「做不到多快」。这是本节的核心，也是全章唯一一处严格的<b>不可能性证明</b>。</p>

<p>先明确「比较排序」的含义：算法只能通过「a 和 b 哪个大」来获取信息，不能假设元素是数字、不能做算术。</p>

<p><b>第一步，把算法的执行过程画成一棵树。</b>每一次比较有两个结果（小于、大于等于），所以每个内部结点分出两条边。
从根到叶的一条路径，就对应算法在某个输入下「问过的问题序列」和最终的输出。</p>

<figure>
<svg viewBox="0 0 660 280" role="img" aria-label="比较排序的判定树：三个元素的六种排列对应六片叶子">
  <text x="0" y="16" fill="#5b6068" font-size="11" font-family="sans-serif">对 3 个元素排序的判定树：叶子必须覆盖全部 3! = 6 种排列</text>
  <g font-family="sans-serif" font-size="11" text-anchor="middle">
    <text x="330" y="46" fill="#17181a">a &lt; b ?</text>
    <line x1="310" y1="54" x2="180" y2="90" stroke="#1b4f8a" stroke-width="1"/>
    <line x1="350" y1="54" x2="480" y2="90" stroke="#1b4f8a" stroke-width="1"/>
    <text x="238" y="68" fill="#0f7b5f">是</text>
    <text x="424" y="68" fill="#0f7b5f">否</text>
    <text x="180" y="106" fill="#17181a">b &lt; c ?</text>
    <text x="480" y="106" fill="#17181a">a &lt; c ?</text>
    <line x1="162" y1="114" x2="90" y2="150" stroke="#1b4f8a" stroke-width="1"/>
    <line x1="198" y1="114" x2="270" y2="150" stroke="#1b4f8a" stroke-width="1"/>
    <line x1="462" y1="114" x2="390" y2="150" stroke="#1b4f8a" stroke-width="1"/>
    <line x1="498" y1="114" x2="570" y2="150" stroke="#1b4f8a" stroke-width="1"/>
    <text x="90" y="166" fill="#17181a">a &lt; c ?</text>
    <text x="270" y="166" fill="#17181a">a &lt; c ?</text>
    <text x="390" y="166" fill="#17181a">b &lt; c ?</text>
    <text x="570" y="166" fill="#17181a">b &lt; c ?</text>
  </g>
  <g font-family="sans-serif" font-size="10" fill="#0f7b5f" text-anchor="middle">
    <text x="46" y="200">abc</text>
    <text x="88" y="200">acb</text>
    <text x="140" y="200">cab</text>
    <text x="228" y="200">cba</text>
    <text x="298" y="200">bca</text>
    <text x="356" y="200">bac</text>
    <text x="420" y="200">acb</text>
    <text x="466" y="200">abc</text>
    <text x="524" y="200">bca</text>
    <text x="612" y="200">cba</text>
  </g>
  <line x1="0" y1="222" x2="620" y2="222" stroke="#d8dbe0" stroke-width="1"/>
  <text x="0" y="244" fill="#5b6068" font-family="sans-serif" font-size="11">高度 h 的二叉树最多有 2^h 片叶子；而这棵树至少要 n! 片叶子（每种排列必须能到达）。</text>
  <text x="0" y="262" fill="#0f7b5f" font-family="sans-serif" font-size="11">所以 2^h ≥ n!　→　h ≥ log₂(n!) ≈ n log₂n − 1.44n　→　至少 Ω(n log n) 次比较。</text>
</svg>
<figcaption>图 8　判定树论证。这不是「我们还没找到更快的算法」，而是「这样的算法在逻辑上不存在」——任何比较排序都必须问够这么多问题。</figcaption>
</figure>

<p>把论证整理成三步，这是可以照着复用的模板：</p>

<ol>
  <li><b>把算法的所有可能执行路径画成一棵树。</b>树的分支来自「信息」的取值为数不多（这里是二值）。</li>
  <li><b>数清楚叶子必须有多少片。</b>n 个元素有 n! 种排列，每一种都必须能走到一个不同的叶子 —— 因为输出的排列必须不同。</li>
  <li><b>用「高度为 h 的二叉树最多 2^h 片叶子」反推高度。</b>得到 h ≥ log₂(n!)，而 Stirling 近似给出 log₂(n!) = Θ(n log n)。</li>
</ol>

<div class="box takeaway"><span class="t">本节结论</span>
<p>任何只依赖「两两比较」的排序，最坏情况下至少要问 Ω(n log n) 次问题。归并排序和堆排序达到了这个下界，所以它们在这个模型下是<b>最优</b>的 —— 再优化也只能优化常数因子，不可能改数量级。</p>
<p>那计数排序为什么能 O(n)？因为它<b>没有遵守比较模型</b>：它直接读元素的值当数组下标（<code>count[x] += 1</code>），
一次操作获取的信息远多于一次「a &lt; b」。<b>下界永远是针对某个模型成立的。当有人说「这件事做不到更好」时，
先问：在什么前提下。</b></p></div>

<h3>5.4 查找的三种武器</h3>

<p>排好序之后，查找才有了 §4.1 的二分。把查找手段放在一张表里，选择的依据就清楚了：</p>

<table>
  <thead><tr><th style="width:130px;">前提</th><th style="width:140px;">手段</th><th style="width:130px;">查找代价</th><th>取舍</th></tr></thead>
  <tbody>
    <tr><td>无序、一次性</td><td>线性扫描</td><td>O(n)</td><td>不用预处理，最省事。只在查很少几次时划算。</td></tr>
    <tr><td>有序数组</td><td>二分查找</td><td>O(log n)</td><td>预处理 O(n log n) 排一次；插入删除仍是 O(n)，因为要挪位。</td></tr>
    <tr><td>频繁按键查</td><td>哈希表（§3）</td><td>O(1) 平均</td><td>不支持范围查询和有序遍历。</td></tr>
    <tr><td>既要查又要范围</td><td>平衡树（§4.3）</td><td>O(log n)</td><td>保证最坏，且支持「找出 [a,b] 之间的所有键」。</td></tr>
    <tr><td>字符串前缀匹配</td><td>字典树 Trie</td><td>O(键长)</td><td>和元素总数无关，只和查询串长度有关。搜索框自动补全用它。</td></tr>
  </tbody>
</table>

<div class="box finding"><span class="t">模型修正</span><p>「二分查找是 O(log n) 所以很快」这个说法漏掉了一个关键前提：
<p><b>它是「跳跃访问」的。</b>每次都跳到数组中间，这在数组上没问题，但一旦数据在磁盘或很远的内存里，
跳跃就意味着每次访问都可能触发一次昂贵的取数。所以数据库索引不用二分数组，而用 B+ 树 ——
B+ 树的叶子结点在磁盘上是<b>连续排列并用指针串起来的</b>，范围查询可以顺着链表顺序读，把随机 I/O 变成顺序 I/O。
<b>同样的 O(log n)，在存储层面前可以差几个数量级。</b>这就是为什么「复杂度相同」不等于「性能相同」。</p></div>

<h3>5.5 二分查找的边界写法：一个完整的推演</h3>

<p>§4.1 给了基础版。工程里真正需要的是<b>四种变体</b>，而它们的区别只在于「相等时怎么办」。
把下面这张表记住，比记住四段代码有用得多。</p>

<pre><code><span class="cm"># 通用模板：区间始终是 [lo, hi)，循环结束后 lo 就是「分界点」</span>
<span class="kw">def</span> <span class="mk">lower_bound</span>(a, t):
    <span class="cm"># 返回第一个 ≥ t 的下标（找不到就是 len(a)）</span>
    lo, hi = <span class="mk">0</span>, len(a)
    <span class="kw">while</span> lo &lt; hi:
        mid = (lo + hi) // <span class="mk">2</span>
        <span class="kw">if</span> a[mid] &lt; t:
            lo = mid + <span class="mk">1</span>            <span class="cm"># 中点也小于 t，排除它</span>
        <span class="kw">else</span>:
            hi = mid                  <span class="cm"># 中点是候选，保留在区间里（关键差异）</span>
    <span class="kw">return</span> lo
<span class="kw">def</span> <span class="mk">upper_bound</span>(a, t):
    <span class="cm"># 返回第一个 &gt; t 的下标</span>
    lo, hi = <span class="mk">0</span>, len(a)
    <span class="kw">while</span> lo &lt; hi:
        mid = (lo + hi) // <span class="mk">2</span>
        <span class="kw">if</span> a[mid] &lt;= t:              <span class="cm"># 唯一的差异：&lt; 变成 &lt;=</span>
            lo = mid + <span class="mk">1</span>
        <span class="kw">else</span>:
            hi = mid
    <span class="kw">return</span> lo</code></pre>

<p>这两个函数一旦有了，四种问题都变成一次减法：</p>

<table>
  <thead><tr><th style="width:280px;">需求</th><th style="width:250px;">写法</th><th>说明</th></tr></thead>
  <tbody>
    <tr><td>是否存在</td><td><code>lower_bound(a,t) &lt; len(a) and a[i] == t</code></td><td>找到后还要验一次相等。</td></tr>
    <tr><td>相等元素的个数</td><td><code>upper_bound(a,t) - lower_bound(a,t)</code></td><td>一个减法解决。这是这对函数的威力所在。</td></tr>
    <tr><td>第一个 ≥ t 的位置</td><td><code>lower_bound(a,t)</code></td><td>「插入位置」也是它：把 t 插在这里，数组仍然有序。</td></tr>
    <tr><td>最后一个 ≤ t 的位置</td><td><code>upper_bound(a,t) - 1</code></td><td>注意可能得 -1（没有满足条件的元素）。</td></tr>
  </tbody>
</table>

<div class="box note"><span class="t">「二分答案」：二分不止用于数组</span><p>更重要的推广：<b>只要一个问题的判定条件是「单调的」（小于某点全不行、大于某点全行），就可以对它二分。</b>
比如「最小化最大装载量，使得 k 辆车能在 D 天内运完」—— 装载量越大越容易满足，于是对「装载量」二分。
这类题在内核的写回阈值、调度器的时间片调优里都有真实对应。<b>二分是一种搜索答案空间的方法，数组只是它最常见的载体。</b></p></div>

<footer>
  <p><strong>本节自测</strong> ① 用判定树的思路，说明「在 n 个元素里找最大值」的下界为什么是 n−1 次比较。这个下界能被达到吗？
  ② 为什么计数排序不算违反下界？如果把它的前提（值域有界）去掉，会退化成什么？
  ③ 一个需求是「从 10 亿条日志里取出访问量最高的 10 个 IP」。用堆还是全排序？分别的复杂度是多少？
  ④ 回到第一章 §2.4 的二分不变式：为什么 <code>lower_bound</code> 里相等时写 <code>hi = mid</code> 而不是 <code>return mid</code>？</p>
</footer>

<h2><span class="n">6</span>图：当数据之间是「多对多」的关系</h2>

<p>前面的结构都在处理「一个元素」或者「元素与元素的一对一关系」。但有一大类问题，本质是<b>关系本身才是数据</b>：
谁认识谁、哪个网页链接到哪个网页、任务 A 必须在任务 B 之前完成、两地之间有多少条路。
把这些关系交给数组和哈希表去表达会很别扭，于是有了图。</p>

<h3>6.1 图的两种存法</h3>

<p>图由<b>顶点</b>（vertex，也叫结点）和<b>边</b>（edge）组成。边的概念很宽：可以带权（两地距离）、可以有向（A 关注了 B，B 未必回关）、
可以带标签（这条边表示「属于」）。存法只有两种主流选择，而选择依据是「图有多稠密」。</p>

<figure>
<svg viewBox="0 0 660 300" role="img" aria-label="同一张有向图用邻接矩阵和邻接表两种方式存储">
  <text x="0" y="16" fill="#5b6068" font-size="11" font-family="sans-serif">一张 5 个顶点的有向图（A→B, A→C, B→D, C→D, D→E）</text>
  <g font-family="sans-serif" font-size="11">
    <text x="0" y="46" fill="#5b6068">邻接矩阵：5×5，用 0/1 表示 A[i][j] 是否有边。查询「A 到 C 有边吗」是 O(1)。</text>
  </g>
  <g font-family="monospace" font-size="11" fill="#17181a">
    <text x="0" y="70">      A  B  C  D  E</text>
    <text x="0" y="88">  A   .  1  1  .  .</text>
    <text x="0" y="106">  B   .  .  .  1  .</text>
    <text x="0" y="124">  C   .  .  .  1  .</text>
    <text x="0" y="142">  D   .  .  .  .  1</text>
    <text x="0" y="160">  E   .  .  .  .  .</text>
  </g>
  <g font-family="sans-serif" font-size="11">
    <text x="230" y="46" fill="#5b6068">邻接表：每个顶点挂一个列表，只存真实存在的边。</text>
  </g>
  <g font-family="monospace" font-size="11" fill="#17181a">
    <text x="230" y="70">A → [B, C]</text>
    <text x="230" y="88">B → [D]</text>
    <text x="230" y="106">C → [D]</text>
    <text x="230" y="124">D → [E]</text>
    <text x="230" y="142">E → []</text>
  </g>
  <line x1="0" y1="182" x2="620" y2="182" stroke="#d8dbe0" stroke-width="1"/>
  <g font-family="sans-serif" font-size="11">
    <text x="0" y="204" fill="#0f7b5f">空间：矩阵恒为 O(V²)，表为 O(V+E)</text>
    <text x="0" y="226" fill="#0f7b5f">查一条边：矩阵 O(1)，表 O(出度)</text>
    <text x="0" y="248" fill="#0f7b5f">遍历一个点的全部邻居：矩阵要扫 O(V)，表只要 O(出度)</text>
    <text x="0" y="274" fill="#5b6068">100 万个用户、平均 20 个好友：矩阵要 10¹² 格（放不下），表只要约 2000 万条记录。</text>
  </g>
</svg>
<figcaption>图 9　两种存法。稠密图（边接近 V²）用矩阵，稀疏图（边接近 V）用邻接表。真实世界的图几乎都是稀疏的。</figcaption>
</figure>

<pre><code><span class="cm"># Python 里「邻接表」最顺手的写法就是字典套列表</span>
g = {
    <span class="mk">'A'</span>: [<span class="mk">'B'</span>, <span class="mk">'C'</span>],
    <span class="mk">'B'</span>: [<span class="mk">'D'</span>],
    <span class="mk">'C'</span>: [<span class="mk">'D'</span>],
    <span class="mk">'D'</span>: [<span class="mk">'E'</span>],
    <span class="mk">'E'</span>: [],
}
<span class="cm"># 带权图：把邻居换成 (邻居, 权重)</span>
w = {
    <span class="mk">'A'</span>: [(<span class="mk">'B'</span>, <span class="mk">4</span>), (<span class="mk">'C'</span>, <span class="mk">2</span>)],
    <span class="mk">'B'</span>: [(<span class="mk">'D'</span>, <span class="mk">7</span>)],
    <span class="mk">'C'</span>: [(<span class="mk">'D'</span>, <span class="mk">1</span>)],
    <span class="mk">'D'</span>: [],
}</code></pre>

<p>注意一件事：<b>图本身不是一种「容器」，而是一种「建模方式」。</b>同一批数据，你可以建成有向图、无向图、带权图、
二分图，取决于你要问什么问题。建模错了，算法再好也答不出正确的答案 —— 这一点在第七、八章（编译器的依赖图、分布式的一致性模型）会反复出现。</p>

<h3>6.2 遍历：DFS 与 BFS，一个栈的距离</h3>

<p>图的遍历比树麻烦一点点：树没有环、有唯一的根，而图可能成环、可能不连通。所以遍历必须显式记住<b>访问过的顶点</b>，
否则会在环里转圈。</p>

<pre><code><span class="kw">def</span> <span class="mk">dfs</span>(g, start):
    <span class="cm"># 深度优先：一条路走到黑，走不动了再回头 —— 用一个栈实现</span>
    seen, order = {start}, []
    stack = [start]
    <span class="kw">while</span> stack:
        u = stack.pop()                 <span class="cm"># 后进先出</span>
        order.append(u)
        <span class="kw">for</span> v <span class="kw">in</span> g.get(u, []):
            <span class="kw">if</span> v <span class="kw">not</span> <span class="kw">in</span> seen:
                seen.add(v)             <span class="cm"># 入栈时就标记，避免重复入栈</span>
                stack.append(v)
    <span class="kw">return</span> order
<span class="kw">from</span> collections <span class="kw">import</span> deque
<span class="kw">def</span> <span class="mk">bfs</span>(g, start):
    <span class="cm"># 广度优先：先看完所有距离 1 的，再看距离 2 的 —— 用一个队列实现</span>
    dist = {start: <span class="mk">0</span>}
    q = deque([start])
    <span class="kw">while</span> q:
        u = q.popleft()                 <span class="cm"># 先进先出（不是 list.pop(0)，那是 O(n) 的）</span>
        <span class="kw">for</span> v <span class="kw">in</span> g.get(u, []):
            <span class="kw">if</span> v <span class="kw">not</span> <span class="kw">in</span> dist:
                dist[v] = dist[u] + <span class="mk">1</span>
                q.append(v)
    <span class="kw">return</span> dist
<span class="cm"># 复杂度的关键：每个顶点入队/出队一次，每条边被看一次 → O(V + E)</span>
<span class="cm"># 注意它和 O(V²) 的区别：后者是「每个顶点都扫一遍所有邻居」，只在用邻接矩阵时才出现</span></code></pre>

<div class="box takeaway"><span class="t">本节结论</span><p>DFS 和 BFS 的代码只差一个数据结构：栈（LIFO）对队列（FIFO）。
<p>但这个差别决定了它们能回答什么问题 —— <b>BFS 的层序性质来自「队列保证先到先服务」，所以第一次到达某点时走过的路径必然是最短的（边权相等时）。</b>
DFS 没有这个保证。</p>
<p>所以选哪个不是风格问题，而是「你要问什么」：</p>
<ul>
  <li>无权图的最短路径、社交网络的「几度人脉」→ <b>BFS</b></li>
  <li>拓扑排序、连通分量、判断有环、走迷宫找一条路（不求最短）→ <b>DFS</b></li>
</ul>
<p>这个「用容器定顺序」的思想，会在第七章（编译器的语法分析、寄存器分配）和第八章（分布式一致性协议的日志复制）再次出现。</p></div>

<h3>6.3 最短路径：Dijkstra 与「贪心的前提」</h3>

<p>BFS 能算最短路，但前提是「每条边代价相同」。现实里的边几乎总是带权的：两地距离、网络延迟、任务耗时。
这时需要 Dijkstra 算法。</p>

<pre><code><span class="kw">import</span> heapq
<span class="kw">def</span> <span class="mk">dijkstra</span>(g, src):
    <span class="cm"># g[u] = [(v, w), ...]。返回 src 到所有点的最短距离</span>
    INF = float(<span class="mk">'inf'</span>)
    dist = {u: INF <span class="kw">for</span> u <span class="kw">in</span> g}
    dist[src] = <span class="mk">0</span>
    pq = [(<span class="mk">0</span>, src)]                   <span class="cm"># 小顶堆：(当前已知距离, 顶点)</span>
    <span class="kw">while</span> pq:
        d, u = heapq.heappop(pq)
        <span class="kw">if</span> d &gt; dist[u]:
            <span class="kw">continue</span>                    <span class="cm"># 过期条目（u 后来被更短的路径更新过），跳过</span>
        <span class="kw">for</span> v, w <span class="kw">in</span> g.get(u, []):
            nd = d + w                  <span class="cm"># 松弛(relax)：试着用 u 去改进 v</span>
            <span class="kw">if</span> nd &lt; dist[v]:
                dist[v] = nd
                heapq.heappush(pq, (nd, v))
    <span class="kw">return</span> dist
<span class="cm"># 复杂度：每条边最多触发一次 push → 堆里最多 E 个元素 → O(E log E) ≈ O(E log V)</span>
<span class="cm"># 朴素实现（每次线性扫描找最小 dist）是 O(V²)，稠密图上反而更快</span></code></pre>

<p>Dijkstra 的核心动作叫<b>松弛</b>（relaxation）：<code>if nd &lt; dist[v]: dist[v] = nd</code>。
它的含义是「原本以为到 v 要 dist[v]，现在发现经由 u 只要 nd，更新它」。整张图的收敛过程就是不断松弛直到稳定，
和第一章 §2.3 讲的循环不变式是同一回事：<b>不变式是「已出堆的顶点，距离已是最终值」。</b></p>

<div class="box finding"><span class="t">模型修正</span><p>Dijkstra 之所以正确，依赖一个前提：<b>所有边的权重非负。</b>
<p>证明直觉是这样的：小顶堆每次弹出的是当前未定顶点中距离最小的 u。如果存在一条更短的路到 u，它必然要先经过某个距离更大的中间点，
再加上一段非负的边 —— 那就比「当前最小」更大了，矛盾。所以 u 的距离已经确定，不会再有改进。</p>
<p><b>如果边权可以是负数，这个论证立刻崩掉</b>：你可以先绕到一个「大距离」的点，再走一条负边回来把总距离拉低。
这时必须换成 Bellman-Ford（对每条边反复松弛 V−1 轮，O(VE)），它没有这个前提。
再进一步，如果图里存在总权为负的<b>环</b>，最短路根本不存在（可以无限走），Bellman-Ford 能检测出这种情况。</p>
<p>工程上的对应：网络路由协议里，距离向量算法（RIP）本质上就是 Bellman-Ford，因为它能处理「链路代价变化」甚至暂时的不一致；
而 OSPF 用的是 Dijkstra，因为它要求链路代价非负、并且要有全局拓扑视图。<b>协议的选择直接由算法的前提决定。</b></p></div>

<h3>6.4 拓扑排序：只要顺序，不要距离</h3>

<p>最后一类图问题，不问「多远」，只问「谁先谁后」。典型场景：编译时的模块依赖、构建系统的任务顺序、课程表。
这类关系天然是一个<b>有向无环图</b>（DAG）—— 如果有环，就说明「A 依赖 B 且 B 依赖 A」，任务永远无法开始。</p>

<pre><code><span class="kw">from</span> collections <span class="kw">import</span> deque
<span class="kw">def</span> <span class="mk">toposort</span>(nodes, prereq):
    <span class="cm"># prereq[u] = u 依赖的顶点的列表，即边 v → u 表示「v 是 u 的前置」</span>
    indeg = {u: <span class="mk">0</span> <span class="kw">for</span> u <span class="kw">in</span> nodes}
    <span class="kw">for</span> u <span class="kw">in</span> nodes:
        <span class="kw">for</span> v <span class="kw">in</span> prereq.get(u, []):
            indeg[u] += <span class="mk">1</span>               <span class="cm"># 统计每个点还有几个前置没完成</span>
    q = deque([u <span class="kw">for</span> u <span class="kw">in</span> nodes <span class="kw">if</span> indeg[u] == <span class="mk">0</span>])   <span class="cm"># 没有前置的可以直接做</span>
    order = []
    <span class="kw">while</span> q:
        u = q.popleft()
        order.append(u)
        <span class="kw">for</span> v <span class="kw">in</span> nodes:                   <span class="cm"># 找到所有依赖 u 的点，把它们的计数减一</span>
            <span class="kw">if</span> u <span class="kw">in</span> prereq.get(v, []):
                indeg[v] -= <span class="mk">1</span>
                <span class="kw">if</span> indeg[v] == <span class="mk">0</span>:          <span class="cm"># 它的前置全部就绪了，可以入队</span>
                    q.append(v)
    <span class="kw">if</span> len(order) &lt; len(nodes):
        <span class="kw">raise</span> ValueError(<span class="mk">'存在环，无法拓扑排序：'</span> + str(set(nodes) - set(order)))
    <span class="kw">return</span> order
<span class="cm"># 这个算法叫 Kahn 算法：反复「取出入度为 0 的点，然后删掉它的出边」</span>
<span class="cm"># 复杂度的瓶颈在上面的双重循环 O(V²)；用真正的邻接表写就是 O(V+E)</span></code></pre>

<div class="box takeaway"><span class="t">本节结论</span><p>把图这一节压成一句话：<b>图的算法几乎都是「遍历 + 一个容器 + 一个不变式」的组合。</b>
<p>BFS 是遍历 + 队列，DFS 是遍历 + 栈，Dijkstra 是遍历 + 优先队列（堆）并在出堆时固定答案，
拓扑排序是遍历 + 入度计数。它们的骨架完全一样 —— 都是「从已知推向未知，直到没有新的可推」。
<b>差别只在「谁先被处理」这个顺序上，而这个顺序由容器决定。</b></p>
<p>理解了这一点，你再看图算法就不需要背了：先问「我要的顺序是什么」，再选容器，剩下的就是维护不变式。</p></div>

<footer>
  <p><strong>本节自测</strong> ① 一张有 100 万个顶点的图，如果「谁和谁是朋友」要在线查询（A 是 B 的朋友吗），邻接矩阵和邻接表各自的查询代价是多少？你会怎么选？
  ② Dijkstra 里的 <code>if d &gt; dist[u]: continue</code> 这一行，删掉会怎样？（提示：想想一个顶点可能被 push 几次。）
  ③ 为什么「检测有没有环」用拓扑排序的返回值就能判断，而不需要单独写一个算法？
  ④ 一个任务依赖图里存在环，说明业务上有什么问题？（这一问会直接连到第八章的分布式死锁检测。）</p>
</footer>

<h2><span class="n">7</span>算法设计范式：四把可以复用的锤子</h2>

<p>前面六节都在讲「具体结构」和「具体算法」。但真正需要迁移的能力不是记住它们，而是<b>面对一个新问题时，知道往哪个方向想</b>。
这一节给出四个范式。它们的共同点是：都不是某个算法，而是「面对问题时的第一反应」。</p>

<figure>
<svg viewBox="0 0 640 286" role="img" aria-label="四种算法设计范式的判别流程">
  <g font-family="sans-serif" font-size="11" text-anchor="middle">
    <rect x="240" y="10" width="180" height="34" fill="none" stroke="#1b4f8a" stroke-width="1"/>
    <text x="330" y="31" fill="#17181a">拿到一个新问题</text>
    <line x1="330" y1="44" x2="330" y2="66" stroke="#1b4f8a" stroke-width="1"/>
    <text x="470" y="60" fill="#0f7b5f" font-size="10" text-anchor="start">能否拆成同型子问题？</text>
    <rect x="240" y="66" width="180" height="34" fill="none" stroke="#1b4f8a" stroke-width="1"/>
    <text x="330" y="87" fill="#17181a">边界是否清晰可判？</text>
  </g>
  <g font-family="sans-serif" font-size="11">
    <line x1="240" y1="83" x2="120" y2="120" stroke="#0f7b5f" stroke-width="2"/>
    <line x1="420" y1="83" x2="520" y2="120" stroke="#b4463c" stroke-width="1"/>
    <text x="140" y="112" fill="#0f7b5f" font-size="11" text-anchor="start">是</text>
    <text x="430" y="112" fill="#b4463c" font-size="10" text-anchor="start" dominant-baseline="auto">否，但有重叠子问题</text>
  </g>
  <g font-family="sans-serif" font-size="11" text-anchor="middle">
    <rect x="20" y="128" width="200" height="86" fill="none" stroke="#0f7b5f" stroke-width="1"/>
    <text x="120" y="150" fill="#0f7b5f">① 分治</text>
    <text x="120" y="172" fill="#17181a" font-size="10">拆 → 递归解 → 合并</text>
    <text x="120" y="192" fill="#5b6068" font-size="10">归并排序、二分查找</text>
    <text x="120" y="208" fill="#5b6068" font-size="10">快排、大整数乘法</text>
    <rect x="420" y="128" width="200" height="86" fill="none" stroke="#b4463c" stroke-width="1"/>
    <text x="520" y="150" fill="#b4463c">② 动态规划</text>
    <text x="520" y="172" fill="#17181a" font-size="10">定义状态 + 转移方程</text>
    <text x="520" y="192" fill="#5b6068" font-size="10">背包、编辑距离</text>
    <text x="520" y="208" fill="#5b6068" font-size="10">最长公共子序列</text>
    <line x1="120" y1="214" x2="120" y2="236" stroke="#d8dbe0" stroke-width="1"/>
    <line x1="520" y1="214" x2="520" y2="236" stroke="#d8dbe0" stroke-width="1"/>
    <rect x="20" y="236" width="200" height="44" fill="none" stroke="#1b4f8a" stroke-width="1"/>
    <text x="120" y="254" fill="#1b4f8a">③ 贪心</text>
    <text x="120" y="272" fill="#17181a" font-size="10">每步取局部最优 + 能证明全局最优</text>
    <rect x="420" y="236" width="200" height="44" fill="none" stroke="#1b4f8a" stroke-width="1"/>
    <text x="520" y="254" fill="#1b4f8a">④ 回溯 / 搜索</text>
    <text x="520" y="272" fill="#17181a" font-size="10">试 + 撤销 + 剪枝</text>
    <text x="320" y="254" fill="#5b6068" font-size="10">局部最优推不出全局最优时，</text>
    <text x="320" y="272" fill="#5b6068" font-size="10">退回 ②；连最优解都不要求时用 ④ 找可行解。</text>
  </g>
</svg>
<figcaption>图 10　四个范式的选择路径。注意③旁边那行：贪心失败不是死路，而是「回到动态规划」的信号。</figcaption>
</figure>

<h3>7.1 分治：把问题对半砍，然后合并</h3>

<p>分治的三个动作固定：<b>分解</b>（把问题拆成规模更小的同类问题）、<b>求解</b>（递归，直到基例）、<b>合并</b>（把小答案拼成大答案）。
§5.2 的归并排序是最标准的例子：拆成两半、分别排好、合并。</p>

<p>分治的复杂度有统一的估算法：画递归树，把每一层的工作量加起来。以归并为例：</p>

<figure>
<svg viewBox="0 0 660 270" role="img" aria-label="归并排序的递归树：每层总工作量都是 n，共 log n 层">
  <text x="0" y="16" fill="#5b6068" font-size="11" font-family="sans-serif">T(n) = 2·T(n/2) + n　→　展开成递归树，每层之和都是 n</text>
  <g font-family="sans-serif" font-size="11" text-anchor="middle">
    <rect x="280" y="30" width="100" height="24" fill="none" stroke="#0f7b5f" stroke-width="1"/>
    <text x="330" y="46" fill="#0f7b5f">n</text>
    <text x="450" y="46" fill="#17181a">合并代价 n</text>
    <line x1="300" y1="54" x2="240" y2="80" stroke="#1b4f8a" stroke-width="1"/>
    <line x1="360" y1="54" x2="420" y2="80" stroke="#1b4f8a" stroke-width="1"/>
    <rect x="190" y="80" width="100" height="24" fill="none" stroke="#0f7b5f" stroke-width="1"/>
    <text x="240" y="96" fill="#0f7b5f">n/2</text>
    <rect x="370" y="80" width="100" height="24" fill="none" stroke="#0f7b5f" stroke-width="1"/>
    <text x="420" y="96" fill="#0f7b5f">n/2</text>
    <text x="530" y="96" fill="#17181a">合计 n</text>
    <line x1="210" y1="104" x2="150" y2="130" stroke="#1b4f8a" stroke-width="1"/>
    <line x1="270" y1="104" x2="330" y2="130" stroke="#1b4f8a" stroke-width="1"/>
    <line x1="390" y1="104" x2="330" y2="130" stroke="#1b4f8a" stroke-width="1"/>
    <line x1="450" y1="104" x2="510" y2="130" stroke="#1b4f8a" stroke-width="1"/>
    <text x="330" y="146" fill="#0f7b5f">n/4 · 4 份　合计 n</text>
    <text x="330" y="168" fill="#5b6068">…</text>
    <text x="330" y="192" fill="#0f7b5f">1 · n 份　合计 n</text>
  </g>
  <line x1="0" y1="212" x2="620" y2="212" stroke="#d8dbe0" stroke-width="1"/>
  <g font-family="sans-serif" font-size="11">
    <text x="0" y="234" fill="#0f7b5f">层数 = log₂n（每次减半）　每层合计 = n　→　T(n) = n·log₂n = O(n log n)</text>
    <text x="0" y="256" fill="#5b6068">这个方法叫「主定理」的直观版：只要是「a 个规模 n/b 的子问题 + O(n) 的合并」，先画层数再看每层和。</text>
  </g>
</svg>
<figcaption>图 11　递归树估算法。它比背主定理公式更实用：绝大多数分治算法的复杂度，用「层数 × 每层之和」就能看出来。</figcaption>
</figure>

<div class="box note"><span class="t">分治的关键难点在「合并」，不在「分解」</span><p>写分治时，递归调用本身几乎不会出错，
真正需要动脑的是<b>怎么把小答案拼成大答案</b>。归并排序的合并是「两路归并」；
二分查找把「合并」变成了「丢弃一半」（合并代价为零，所以从 O(n log n) 降到 O(log n)）；
求最大子数组和的分治里，合并必须额外考虑「跨越中点的那一段」—— 这一项最容易漏，漏了答案就错。</p></div>

<h3>7.2 贪心：只做眼前最优，然后证明它居然是对的</h3>

<p>贪心的写法通常极短，短到让人怀疑。以「区间调度」为例：给你一堆会议的时间段，最多能安排几个不冲突的会议？</p>

<pre><code><span class="kw">def</span> <span class="mk">max_meetings</span>(intervals):
    <span class="cm"># intervals = [(start, end), ...]</span>
    <span class="cm"># 贪心策略：按「结束时间」升序，能接就接</span>
    intervals.sort(key=<span class="kw">lambda</span> x: x[<span class="mk">1</span>])       <span class="cm"># 关键的一步：排序依据不是开始时间</span>
    count, last_end = <span class="mk">0</span>, float(<span class="mk">'-inf'</span>)
    <span class="kw">for</span> s, e <span class="kw">in</span> intervals:
        <span class="kw">if</span> s &gt;= last_end:                      <span class="cm"># 和上一个不冲突</span>
            count += <span class="mk">1</span>
            last_end = e
    <span class="kw">return</span> count
<span class="cm"># O(n log n)，全是排序的开销；循环本身是 O(n)</span></code></pre>

<div class="box finding"><span class="t">模型修正</span><p>「选最早开始的会议」看起来更自然，但它<b>是错的</b>。
<p>反例：会议 A = (0, 10)、B = (1, 2)、C = (2, 3)。按开始时间贪心会先选 A，然后一个都接不上，答案是 1；
而正确答案是先选 B 再选 C，答案是 2。</p>
<p><b>贪心算法的正确性必须被证明，不能靠直觉。</b>常用的两种证明套路：</p>
<ol>
  <li><b>交换论证</b>（exchange argument）：假设存在一个最优解，如果它没有选贪心选的那一项，就把它替换成贪心的那一项，
  证明结果不会变差。从而「存在一个包含贪心选择的最优解」。</li>
  <li><b>归纳法</b>：证明「贪心选完第一步之后，剩下的问题仍然是原问题的同类子问题」，且实际的最优解一定包含贪心选择。</li>
</ol>
<p>区间调度的交换论证是：设贪心选的是结束最早的会议 g，任意最优解 O 里的第一个会议是 o。
因为 g 的结束时间 ≤ o 的结束时间，把 O 里的 o 换成 g，剩下的会议不会因为换而变得冲突 —— 所以 O' 也是最优解，且包含了 g。
归纳下去，贪心解就是最优解。<b>注意这个论证里的关键一句「g 的结束时间 ≤ o 的结束时间」，
正是「按结束时间排序」这个策略的用途所在。</b></p></div>

<p>什么时候可以考虑贪心？一个实用的判断信号：<b>问题有「无后效性」的局部结构</b> —— 当前的选择不会让未来的选择集变得更差。
如果每个选择都会「消耗」某种资源、且资源消耗方式影响后面（比如背包问题里放一个小物品 vs 放一个大物品会占掉不同的容量组合），
贪心就失效，得用动态规划。下面这张表是这一节最该记住的：</p>

<table>
  <thead><tr><th style="width:230px;">问题</th><th style="width:110px;">贪心可行？</th><th>为什么</th></tr></thead>
  <tbody>
    <tr><td>区间调度（最多不冲突会议）</td><td><span class="pill ok">可行</span></td><td>按结束时间排序。交换论证成立。</td></tr>
    <tr><td>Huffman 编码</td><td><span class="pill ok">可行</span></td><td>每次合并频率最小的两个，用堆实现（§4.4）。</td></tr>
    <tr><td>最小生成树（Kruskal/Prim）</td><td><span class="pill ok">可行</span></td><td>按边权递增取边，只要不成环就要。拟阵结构保证最优。</td></tr>
    <tr><td>Dijkstra 最短路（非负权）</td><td><span class="pill ok">可行</span></td><td>每次固定当前最近的顶点（§6.3）。</td></tr>
    <tr><td>找零钱（币值是 1,5,10,25）</td><td><span class="pill ok">可行</span></td><td>每次拿最大面额。这个币值体系「恰好」满足贪心性质。</td></tr>
    <tr><td>找零钱（币值含 1,3,4）</td><td><span class="pill bad">不可行</span></td><td>要凑 6：贪心拿 4+1+1=3 枚，最优是 3+3=2 枚。</td></tr>
    <tr><td>0/1 背包</td><td><span class="pill bad">不可行</span></td><td>按「单位价值最高」贪心会被容量组合击败。必须动态规划。</td></tr>
  </tbody>
</table>

<div class="box note"><span class="t">回看点（信息论的连接）</span><p>注意「找零钱」那一行的措辞：贪心可行是币值体系的<b>巧合性质</b>，
不是问题的普遍性质。现实中「贪心恰好成立」的例子往往还有更深的结构解释 ——
Huffman 编码的最优性最终由<b>信息熵</b>给出下界（这是概率论与信息论的入口，
也是压缩算法、甚至一些机器学习模型损失函数的理论基础）。</p></div>

<h3>7.3 动态规划：用一张表把重复计算买下来</h3>

<p>动态规划是这四个范式里最难的，难在「想不出来状态怎么定义」。先看它要解决什么：<b>递归里出现了大量重复的子问题。</b></p>

<p>最经典的是斐波那契数列。直接把递归式写成代码：</p>

<pre><code><span class="kw">def</span> <span class="mk">fib_naive</span>(n):
    <span class="kw">if</span> n &lt; <span class="mk">2</span>:
        <span class="kw">return</span> n
    <span class="kw">return</span> fib_naive(n - <span class="mk">1</span>) + fib_naive(n - <span class="mk">2</span>)   <span class="cm"># 指数级 O(2ⁿ)</span>
<span class="cm"># fib(5) = fib(4) + fib(3)</span>
<span class="cm">#        = (fib(3)+fib(2)) + (fib(2)+fib(1))   ← fib(3) 被算了两次，fib(2) 被算了三次</span>
<span class="cm"># n 每加 1，调用树几乎翻倍。n=40 就要跑十几亿次，n=50 跑不动。</span></code></pre>

<figure>
<svg viewBox="0 0 640 246" role="img" aria-label="斐波那契递归树中的重复子问题，以及用一张表把每个状态只算一次">
  <text x="0" y="14" fill="#5b6068" font-size="11" font-family="sans-serif">朴素递归：同一状态被反复求解（红色为重复出现的子问题）</text>
  <g stroke="#c8ccd2" stroke-width="1">
    <line x1="330" y1="46" x2="230" y2="76"/>
    <line x1="330" y1="46" x2="430" y2="76"/>
    <line x1="230" y1="76" x2="160" y2="106"/>
    <line x1="230" y1="76" x2="300" y2="106"/>
    <line x1="430" y1="76" x2="370" y2="106"/>
    <line x1="430" y1="76" x2="500" y2="106"/>
    <line x1="160" y1="106" x2="100" y2="136"/>
    <line x1="160" y1="106" x2="220" y2="136"/>
    <line x1="300" y1="106" x2="260" y2="136"/>
    <line x1="300" y1="106" x2="340" y2="136"/>
  </g>
  <g font-family="sans-serif" font-size="12" text-anchor="middle" dominant-baseline="central">
    <text x="330" y="46" fill="#17181a">f(5)</text>
    <text x="230" y="76" fill="#17181a">f(4)</text>
    <text x="430" y="76" fill="#17181a">f(3)</text>
    <text x="160" y="106" fill="#17181a">f(3)</text>
    <text x="300" y="106" fill="#b4463c">f(2)</text>
    <text x="370" y="106" fill="#b4463c">f(2)</text>
    <text x="500" y="106" fill="#b4463c">f(1)</text>
    <text x="100" y="136" fill="#b4463c">f(2)</text>
    <text x="220" y="136" fill="#b4463c">f(1)</text>
    <text x="260" y="136" fill="#b4463c">f(1)</text>
    <text x="340" y="136" fill="#b4463c">f(0)</text>
  </g>
  <text x="0" y="164" fill="#5b6068" font-family="sans-serif" font-size="11">f(3) 被算了 2 次，f(2) 被算了 3 次；n 每加 1，调用次数几乎翻倍 —— 总代价 O(2ⁿ)</text>
  <line x1="0" y1="180" x2="600" y2="180" stroke="#d8dbe0" stroke-width="1"/>
  <text x="0" y="200" fill="#0f7b5f" font-family="sans-serif" font-size="11">改成自底向上填表：每个状态只算一次，n 个状态 × O(1) 转移 = O(n)</text>
  <text x="0" y="222" fill="#17181a" font-family="monospace" font-size="11">f(0) f(1) f(2) f(3) f(4) f(5) … f(n)</text>
  <text x="0" y="240" fill="#17181a" font-family="monospace" font-size="11">0    1    1    2    3    5    …</text>
</svg>
<figcaption>图 12　动态规划的本质：把「重复的子问题」用一张表缓存起来，把指数级的重复计算换成多项式级的填表。</figcaption>
</figure>

<p>把动态规划拆成两个必备成分，缺一不可：</p>

<ol>
  <li><b>最优子结构</b>：大问题的最优解可以由子问题的最优解拼出来。（这保证了「用子问题的答案拼答案」是合法的。）</li>
  <li><b>重叠子问题</b>：不同的分支会反复遇到同一个子问题。（这保证了「缓存」是有收益的。如果子问题从不重复，那就是普通分治，用不着表。）</li>
</ol>

<p>写 DP 的标准流程是「先写递归式，再决定填表顺序」：</p>

<pre><code><span class="cm"># 例：0/1 背包。n 件物品，每件有重量 w[i] 和价值 v[i]，背包容量 C，求最大价值。</span>
<span class="cm"># 状态定义：dp[i][c] = 只考虑前 i 件物品、容量为 c 时能获得的最大价值</span>
<span class="cm"># 转移方程（这是 DP 的灵魂，写对了代码几乎不用想）：</span>
<span class="cm">#   dp[i][c] = max( 不放第 i 件：dp[i-1][c],</span>
<span class="cm">#                   放第 i 件：dp[i-1][c - w[i]] + v[i]  (仅当 c >= w[i]) )</span>
<span class="kw">def</span> <span class="mk">knapsack</span>(w, v, C):
    n = len(w)
    dp = [[<span class="mk">0</span>] * (C + <span class="mk">1</span>) <span class="kw">for</span> _ <span class="kw">in</span> range(n + <span class="mk">1</span>)]
    <span class="kw">for</span> i <span class="kw">in</span> range(<span class="mk">1</span>, n + <span class="mk">1</span>):
        <span class="kw">for</span> c <span class="kw">in</span> range(C + <span class="mk">1</span>):
            dp[i][c] = dp[i - <span class="mk">1</span>][c]                    <span class="cm"># 不放</span>
            <span class="kw">if</span> c &gt;= w[i - <span class="mk">1</span>]:
                dp[i][c] = <span class="kw">max</span>(dp[i][c],
                                 dp[i - <span class="mk">1</span>][c - w[i - <span class="mk">1</span>]] + v[i - <span class="mk">1</span>])
    <span class="kw">return</span> dp[n][C]
<span class="cm"># 复杂度 O(n·C)：状态数 n×C，每个状态 O(1) 转移</span>
<span class="cm"># 注意：这是「伪多项式」。C 是数值不是位数，所以 C = 10⁹ 时这个表放不下 ——</span>
<span class="cm"># 这也是为什么背包问题是 NP-hard，却没有违反「多项式时间」的直觉。</span></code></pre>

<div class="box takeaway"><span class="t">本节结论</span><p>DP 的难点从来不在代码，而在<b>状态的定义</b>。
<p>一个可操作的判断方法：<b>问「我做完一个决策后，为了让后续决策能正确进行，我必须记住什么？」</b>
那个「必须记住的最小信息集」就是状态。背包里必须记住「已经考虑前几件」和「还剩多少容量」，
两者一起构成状态；再多记就是冗余，再少记就无法推出正确答案。</p>
<p>三个层次递进地掌握它：① 能看懂别人的状态定义；② 能对着转移方程写出填表代码；③ 面对新问题能自己定义出状态。
第三层只能靠练，但第二层是完全机械的 —— 而工程中绝大多数 DP 应用停在第二层。</p></div>

<h3>7.4 回溯：把「试错」写成代码</h3>

<p>回溯是最朴素也最万能的方法：<b>逐个位置尝试所有可能，走不通就撤销这一步换下一个。</b>
它天然对应一棵「决策树」，而代码几乎是决策树的直译。</p>

<pre><code><span class="kw">def</span> <span class="mk">permute</span>(nums):
    <span class="cm"># 输出所有排列。经典回溯：三个动作 —— 做选择 / 递归 / 撤销选择</span>
    res = []
    path = []
    <span class="kw">def</span> <span class="mk">backtrack</span>(remaining):
        <span class="kw">if</span> <span class="kw">not</span> remaining:              <span class="cm"># 到达叶子：一条完整的决策路径已形成</span>
            res.append(path[:])           <span class="cm"># 必须复制！path 后面还会被修改</span>
            <span class="kw">return</span>
        <span class="kw">for</span> i, x <span class="kw">in</span> enumerate(remaining):
            path.append(x)                <span class="cm"># ① 做选择</span>
            backtrack(remaining[:i] + remaining[i + <span class="mk">1</span>:])   <span class="cm"># ② 递归到下一层</span>
            path.pop()                    <span class="cm"># ③ 撤销选择 —— 这一行是「回溯」这两个字的来源</span>
        <span class="cm"># 撤销现场，是为了让 for 循环的下一次迭代从干净的状态开始</span>
    backtrack(nums)
    <span class="kw">return</span> res</code></pre>

<p>回溯的复杂度通常是指数级（n! 或 2ⁿ），所以它唯一的实用技巧就是<b>剪枝</b>：
在递归前先判断「这条路是否已经不可能通向有效解」，如果是就直接返回，不再展开整棵子树。
N 皇后问题里「同一行同一列同一斜线不能有两个皇后」这一条，就是最有效的剪枝规则。</p>

<div class="box note"><span class="t">回溯与 DFS 的关系</span><p>回溯就是「带撤销的 DFS」，只不过遍历的对象是<b>状态空间树</b>而不是图的顶点。
一旦你意识到这一点，「为什么 §6.2 的 DFS 不需要撤销、而这里需要」也就清楚了：
图的 DFS 里，一个顶点被访问过就是被访问过，不因为后来走了别的路而改变（它有 <code>seen</code> 集合）；
而状态空间树里，「选了 3」这个临时状态在换分支时必须还原，否则会污染兄弟分支。</p></div>

<h3>7.5 四个范式的关系</h3>

<table>
  <thead><tr><th style="width:110px;">范式</th><th style="width:170px;">核心动作</th><th style="width:150px;">典型复杂度</th><th>失败的信号</th></tr></thead>
  <tbody>
    <tr><td>分治</td><td>拆成独立的同类子问题，合并结果</td><td>O(n log n) 常见</td><td>子问题互相重叠时退化为指数级（该上 DP）。</td></tr>
    <tr><td>贪心</td><td>每步取局部最优，不回头</td><td>取决于排序，O(n log n)</td><td>找不到交换论证 / 找到反例 → 换 DP。</td></tr>
    <tr><td>动态规划</td><td>定义状态 + 转移方程 + 填表</td><td>状态数 × 转移代价</td><td>状态定义不完整（记的信息不够推出转移）。</td></tr>
    <tr><td>回溯</td><td>试 + 撤销 + 剪枝</td><td>指数级，靠剪枝续命</td><td>问题规模稍大就跑不动（该找多项式解法或近似算法）。</td></tr>
  </tbody>
</table>

<div class="box note"><span class="t">回看点（第八章）</span><p>这四把锤子会一路上走到最后：
Kubernetes 的调度器用贪心 + 打分；数据库的查询优化器用动态规划搜索连接顺序（状态是「已连接的表集合」，经典的 DP over subsets）；
编译器的指令选择用 DP；分布式共识里的日志压缩用分治。
<b>范式不是学术概念，而是工程师日常思考的默认姿势。</b></p></div>

<footer>
  <p><strong>本节自测</strong> ① 用「递归树 + 每层之和」估算 T(n) = 2·T(n/2) + n² 的复杂度。和 T(n) = 2·T(n/2) + n 相比，差别出在哪一层？
  ② 给「Huffman 编码」写出它的贪心策略，并试着给出交换论证的第一步（提示：频率最小的两个符号一定可以放在最深的一层）。
  ③ 用动态规划求解「最长公共子序列」，先写出状态定义和转移方程，再写代码。注意区分「状态」和「返回值」。
  ④ 判断这几个问题分别该用哪个范式：找零钱（面额任意）、任务调度（有截止期和收益）、走迷宫的所有路径、矩阵链乘法。</p>
</footer>


<h2><span class="n">8</span>参考资料</h2>

<p>这一章的参考书比第一章更依赖「读哪一本」。原因很实际：数据结构与算法的教材风格差异极大，
有的极度数学化（CLRS），有的纯工程（Sedgewick），有的专为面试（《剑指 Offer》一类）。
下面按「适用阶段」分类，并写清楚每本的推荐理由和难度。</p>

<table>
  <thead><tr><th style="width:230px;">资料</th><th style="width:110px;">难度</th><th style="width:110px;">适合阶段</th><th>推荐理由</th></tr></thead>
  <tbody>
    <tr>
      <td><b>《算法（第 4 版）》</b><br><span class="small">Sedgewick &amp; Wayne</span></td>
      <td><span class="pill cav">中等</span></td>
      <td>入门首选</td>
      <td>本书最大的优势是<b>每个算法都配了可运行的完整实现和可视化</b>（配套的 algs4 库与动画站点）。
      它把「复杂度分析」放在实现之后讲，所以读起来不抽象。缺点是略偏 Java 语境、覆盖面不如 CLRS 全。
      如果你只想读一本，读这本。</td>
    </tr>
    <tr>
      <td><b>《算法导论》</b><br><span class="small">CLRS，第 4 版</span></td>
      <td><span class="pill bad">较难</span></td>
      <td>当工具书 / 第二本</td>
      <td>权威性最高，覆盖最全，<b>证明是完整的</b>（§5.3 那种论证在书里有一整个章节）。
      但不适合从第一页顺序读到最后一页 —— 数学密度太大。正确用法是：概念不通时翻对应的那一章，
      或者把它当作「下界与最优性」的查询手册。</td>
    </tr>
    <tr>
      <td><b>《数据结构与算法分析》</b><br><span class="small">Weiss</span></td>
      <td><span class="pill cav">中等</span></td>
      <td>课程同步</td>
      <td>结构最接近一门大学课程，每章末的习题质量很高。它把「摊还分析」讲得比 CLRS 更平易（§1.4 的势能法）。
      适合跟着一门课一起读。</td>
    </tr>
    <tr>
      <td><b>MIT 6.006 Introduction to Algorithms</b></td>
      <td><span class="pill cav">中等</span></td>
      <td>视频入门</td>
      <td>课程视频 + 讲义齐全，<b>有完整的习题和答案</b>。优点是节奏快、工程味足（讲哈希、讲排序的下界、讲图算法都很干脆）。
      比 6.046（进阶算法）适合作为第一遍。</td>
    </tr>
    <tr>
      <td><b>Princeton Algorithms（Part I &amp; II）</b><br><span class="small">Coursera，Sedgewick 本人讲</span></td>
      <td><span class="pill ok">较易</span></td>
      <td>零基础视频</td>
      <td>和上面的书完全配套。<b>强烈推荐给第一次系统学算法的人</b>：作业有自动评分，可视化做得好，
      讲「为什么这样写」多于「为什么正确」。难度门槛最低。</td>
    </tr>
    <tr>
      <td><b>《算法设计手册》</b><br><span class="small">Skiena</span></td>
      <td><span class="pill cav">中等</span></td>
      <td>建模与实战</td>
      <td>本书最独特的价值是它<b>教你「拿到问题后怎么选算法」</b>（有整整一章「算法设计的一般原则」）。
      §7 的四个范式在书里由大量「这个问题属于哪一类」的实例展开。工程视角强于学术视角。</td>
    </tr>
    <tr>
      <td><b>《编程珠玑》</b><br><span class="small">Bentley</span></td>
      <td><span class="pill cav">中等</span></td>
      <td>工程直觉</td>
      <td>薄，但每一章都在教同一件事：<b>一个「正确的」算法和一个「快的」算法之间常常差一个数量级</b>。
      它讨论的问题（磁盘排序、位图、抽样）都非常具体，是「复杂度分析落到现实」的最好训练。</td>
    </tr>
    <tr>
      <td><b>CS Wiki（csdiy.wiki）</b></td>
      <td><span class="pill ok">索引</span></td>
      <td>选课导航</td>
      <td>不提供内容，只回答「这条路该上哪门课、用什么教材、大概多长时间」。这一章对应它的「数据结构与算法」小块。
      价值在于<b>帮你把上面这些材料排成一个可执行的顺序</b>，而不是替代它们。</td>
    </tr>
    <tr>
      <td><b>《具体数学》</b><br><span class="small">Graham, Knuth, Patashnik</span></td>
      <td><span class="pill bad">较难</span></td>
      <td>补齐数学</td>
      <td>当你在 §7.1 的递归树推导、或者 §5.3 的 Stirling 近似上感到吃力时，缺的不是算法知识而是这套工具。
      不必通读，按需查「求和」「递推式」「二项式系数」几章即可。</td>
    </tr>
    <tr>
      <td><b>LeetCode / 算法竞赛入门经典</b></td>
      <td><span class="pill ok">练习</span></td>
      <td>刷题</td>
      <td>唯一作用是<b>把「知道」变成「会写」</b>。建议方式：按 §7 的四个范式分组刷，而不是按题目编号顺序刷 ——
      同一范式连做十题，比随机做三十题更能形成模式识别。注意不要把它当成学习的主要来源。</td>
    </tr>
  </tbody>
</table>

<div class="box takeaway"><span class="t">本书的推荐读法</span>
<p>第一阶段（建立框架）：看 Princeton 的课或读 Sedgewick，把 §2/§4/§5 的结构和它们各自的操作代价做成一张自己的表。</p>
<p>第二阶段（补齐证明）：读 CLRS 的第 3、4、5、15、16、22–25 章，重点看「为什么正确」和「为什么不能更快」，
这一阶段是本章 §5.3 和 §7.2 那种推理能力的来源。</p>
<p>第三阶段（建立直觉）：读《编程珠玑》和 Skiena，把注意力从「这个算法怎么写」转向「这个问题该归到哪一类」。</p>
<p>三个阶段不必严格串行 —— 但<b>不要在第二阶段没开始时就去大量刷题</b>，那样很容易变成记模式而不是理解。</p></div>

<h2><span class="n">9</span>小结与自测</h2>

<p>这一章的主线只有一句话：<b>数据结构是「用什么样的代价换取什么样的能力」的显式合同。</b>
把本章的九张表压成下面这一张总表：</p>

<table>
  <thead><tr><th style="width:130px;">结构</th><th style="width:150px;">查找 / 访问</th><th style="width:150px;">插入 / 删除</th><th>它的核心承诺</th></tr></thead>
  <tbody>
    <tr><td>数组</td><td><span class="pill ok">按下标 O(1)</span></td><td>尾部摊销 O(1)，中间 O(n)</td><td>连续存储，随机访问最便宜，且对 CPU 缓存友好。</td></tr>
    <tr><td>链表</td><td>O(n)</td><td><span class="pill ok">已知位置时 O(1)</span></td><td>插入删除不改动其他元素，但失去随机访问。</td></tr>
    <tr><td>栈 / 队列</td><td>只看一端 O(1)</td><td>O(1)</td><td>用「访问顺序」本身表达语义（后进先出 / 先进先出）。</td></tr>
    <tr><td>哈希表</td><td><span class="pill ok">O(1) 平均</span>，O(n) 最坏</td><td>O(1) 平均</td><td>内容寻址，但放弃顺序。</td></tr>
    <tr><td>二叉搜索树（平衡）</td><td>O(log n) 保证</td><td>O(log n) 保证</td><td>保序地查找，且支持范围查询。裸 BST 会退化。</td></tr>
    <tr><td>堆</td><td>只看最值 O(1)</td><td>O(log n)</td><td>只维护「父 ≥ 子」，用最弱的不变式换最值的即时可得。</td></tr>
    <tr><td>图（邻接表）</td><td>遍历 O(V+E)</td><td>加一条边 O(1)</td><td>表达任意两两关系，是「建模」而非「容器」。</td></tr>
  </tbody>
</table>

<table>
  <thead><tr><th style="width:170px;">本章的结论</th><th>它来自哪一节</th></tr></thead>
  <tbody>
    <tr><td>O 记号描述的是「增长率的上界」，不是「运行的秒数」，也不是「最坏情况」</td><td>§1.2 与模型修正 1</td></tr>
    <tr><td>摊还分析把「偶尔很贵」平摊成「平均便宜」，动态数组的扩容是标准例子</td><td>§1.4</td></tr>
    <tr><td>「链表插入更快」只在「已经拿到位置」时成立；按值插入两者都是 O(n)</td><td>§2.1 与模型修正 2</td></tr>
    <tr><td>哈希表的 O(1) 是期望值，成立条件是装载因子被控制住</td><td>§3.2</td></tr>
    <tr><td>BST 的查找是 O(h)，不是天生 O(log n)；退化是必然而非偶然</td><td>§4.3 与模型修正 3</td></tr>
    <tr><td>比较排序的下界 Ω(n log n) 是被证明的，但它只约束「比较」这一种信息获取方式</td><td>§5.3</td></tr>
    <tr><td>二分是「搜索答案空间」的方法，判定条件的单调性才是它真正的前提</td><td>§5.5</td></tr>
    <tr><td>Dijkstra 的正确性依赖非负边权；前提变了，算法必须换</td><td>§6.3 与模型修正 4</td></tr>
    <tr><td>贪心必须被证明（交换论证），否则一个反例就够推翻它</td><td>§7.2</td></tr>
    <tr><td>动态规划的难点是状态定义，可操作的方法是问「我还必须记住什么」</td><td>§7.3</td></tr>
  </tbody>
</table>

<div class="box takeaway"><span class="t">本章的收尾：为什么这一章是分界线</span>
<p>第一章教你「程序能正确地跑」。这一章之后，你开始能回答一个更难的问题：<b>这个程序跑得对吗，还是只是恰好在小数据上跑得对？</b>
<p>本章反复出现的三种推理 —— 复杂度分析、不变式、下界证明 —— 是后面每一章的共同语言。
第三章会解释为什么「复杂度相同但常数差一个数量级」（缓存与存储层次）；
第四章会解释哈希表和堆这些结构在操作系统里如何被用来管理进程和内存；
第六章会把 B+ 树放在磁盘上重新讲一遍本章的平衡树。
<b>结构会变，权衡不变。</b></p></div>

<h3>综合思考题</h3>

<ol>
  <li><b>（§1 + §3）</b>用 Python 实现一个「最近使用过的 key 优先淘汰」的缓存（LRU）。
  要求 get 和 put 都是 O(1)。提示：需要两个结构配合 —— 哈希表负责 O(1) 定位，什么结构负责 O(1) 维护访问顺序？
  为什么单独用哈希表做不到？为什么单独用双向链表也做不到？</li>
  <li><b>（§4 + §5）</b>你需要从 10 亿条记录中取出最大的 100 条。数据分批从磁盘读入，内存只能放 10 万条。
  设计要求：用多大的堆？总共多少 I/O？如果改成「取出最大的 100 万条」，方案要变吗？</li>
  <li><b>（§6 + §7）</b>一个任务依赖图有 10 万个结点，现在要在多核上并行执行，要求「任一时刻，没有正在执行的任务依赖于另一个正在执行的任务」。
  你打算怎么用拓扑排序 + 队列实现调度？这个方案在「某些任务特别久」时会暴露什么问题？</li>
  <li><b>（§5 + §7）</b>判断真假并说明理由：「如果能快速判断一个答案对不对，就能快速找到答案。」
  如果这句是假的，它对「算法能在什么时间内解决」这件事意味着什么？（这是一条通向计算复杂性理论的台阶，第七章会涉及。）</li>
  <li><b>（全章）</b>回头审视你第一章写过的任意一段代码（如果有的话）。用本章的语言回答：
  它的时间复杂度是多少？瓶颈在哪个数据结构上？换一个结构能不能降一个数量级？
  <b>能对这个问题的答案给出具体数字（而不是「大概更快」），就是本章学会了。</b></li>
</ol>
