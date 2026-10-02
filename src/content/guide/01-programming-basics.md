---
kind: chapter
order: 1
title: "编程基础：把意图翻译成机器能执行的东西"
part: "第一部 · 地基"
prereq: "无（零基础即可）"
reading: "约 60 分钟"
date: 2026-10-03
ready: true
tags: [计算机科学, 自学路线, 教材式笔记, Python, 编程基础]
lang: zh
---

<div class="meta-row">
    <span><b>读者</b> &nbsp;从没系统学过编程，或学过语法但说不清「为什么是这样」的人</span>
    <span><b>整章目标</b> &nbsp;建立五个能支撑后面所有章节的心智模型，并养成三个工程习惯</span>
    <span><b>代码语言</b> &nbsp;Python 3.12+；涉及内存与地址时用文字描述 C 的做法作对照，不要求会写 C</span>
    <span><b>校对时点</b> &nbsp;2026-10。语言行为以 Python 官方文档为准，工具链部分会随时间变化</span>
</div>

<div class="box note" style="margin-top:26px;">
  <span class="t">这一章为什么排在第一章</span>
  <div class="small">
  <p><b>因为它是唯一一章「不读就会处处受阻」的。</b>后面每一章都要读代码：第二章要分析算法的复杂度，第三章要读汇编片段，第四章要看系统调用的签名。
  如果「变量是什么、函数怎么调用、程序在哪里出错」这三件事没有稳固的模型，后面每一章都会变成死记硬背。</p>
  <p><b>也因为它是全系列最容易写砸的一章。</b>把「变量是什么」讲浅了，就是又一份语法清单，你看完还是不会写程序；
  讲深了，就要牵扯到内存模型、名字绑定、作用域链 —— 而这些概念在第一章直接铺开，又会让人一头雾水。
  这一章采取的折中是：<b>先用一个足够用但不完全准确的模型把事情讲通，再明确告诉你它在哪一步失效、正确的模型是什么。</b>
  每个这样的地方都会用 <span class="pill cav">模型修正</span> 标出来。请务必读完这些修正 —— 它们是这一章真正的内容。</p>
  </div>
</div>

<h2><span class="n">1</span>程序的本质：不是命令，是描述</h2>
<p class="lede">如果只记住这一章的一句话，记住这句：计算机不会「理解」你的意图，它只按你写下的规则机械地搬运数据。</p>

<h3>1.1 一个反直觉的起点</h3>

<p>初学者对程序的第一个想象，通常是「我下命令，计算机执行」。这个想象在很大范围内好用，一旦遇到调试就会失效：
程序出错时，你以为是「它不听话」，实际上是「你的描述不够完整」。这两者的区别决定了一件事 ——
<b>你该修改的是描述，而不是抱怨执行者。</b></p>

<p>为了把这句话讲实，看一个具体例子。假设你要算「一组测量值的平均」，你会写：</p>

<pre><code><span class="cm"># 计算一组测量值的算术平均</span>
<span class="kw">def</span> mean(values):
    total = <span class="mk">0</span>
    <span class="kw">for</span> v <span class="kw">in</span> values:
        total = total + v
    <span class="kw">return</span> total / <span class="kw">len</span>(values)

print(mean([<span class="mk">2</span>, <span class="mk">4</span>, <span class="mk">6</span>]))   <span class="cm"># 4.0</span></code></pre>

<p>这段代码里有三处「描述不完整」的地方，而它们都不会在这一行报错，只会在别的场景下暴露：</p>

<table>
  <thead><tr><th style="width:180px;">输入</th><th style="width:130px;">实际结果</th><th>为什么</th></tr></thead>
  <tbody>
    <tr><td><code>mean([])</code>（空列表）</td><td>抛 <code>ZeroDivisionError</code></td><td>你写了「除以元素个数」，但没描述「一个元素都没有时怎么办」。</td></tr>
    <tr><td><code>mean([1000000000, 1000000001, 1000000002])</code></td><td>Python 里正确，C/Java 里溢出</td><td>你写了「加起来」，但没描述「加到超出机器整数范围时怎么办」。Python 的整数是任意精度的，这层保护被语言兜住了，换个语言就暴露。</td></tr>
    <tr><td><code>mean(None)</code></td><td>抛 <code>TypeError</code>，但报错点在函数内部</td><td>你写了「遍历 values」，但没描述「values 不是可遍历对象时怎么办」。报错发生在 <code>len()</code> 或 <code>for</code>，离真正的错误源头（调用方）很远。</td></tr>
  </tbody>
</table>

<p><b>这三个都不是「计算机不听话」，而是「描述有缺口」。</b>程序员成长的过程，很大程度上就是把「在我预设的输入下能跑」扩展成
「在现实会出现的输入下都有确定行为」的过程。第二章讲算法分析时会反复用到这个视角：算法不只要「对」，还要「在什么输入规模下、花多少代价」。</p>

<div class="box takeaway"><span class="t">本节结论</span><p>写程序 = 把解决问题的步骤写成<b>一组无歧义的规则</b>。调试的主要工作不是猜机器想干什么，而是找回自己描述里那些没写出来的前提。</p></div>

<h3>1.2 三个逐渐贴近机器的模型</h3>

<p>「描述」这个词还是太抽象。下面三个模型能把它落下地，它们是递进的：每个都能解释一部分现象，也都会在某个地方失效。
<b>理解它们的失效点，比记住任何一条结论都重要。</b></p>

<figure>
<svg viewBox="0 0 680 322" role="img" aria-label="程序的三个执行模型：解释、编译、虚拟机">
  <g font-family="-apple-system,BlinkMacSystemFont,'Segoe UI','PingFang SC','Microsoft YaHei',Helvetica,Arial,sans-serif">
    <rect x="24" y="18" width="196" height="118" rx="4" fill="#eef3f8" stroke="#1b4f8a" stroke-width="1.5"/>
    <text x="40" y="40" font-size="12" font-weight="700" fill="#1b4f8a">模型一 · 解释执行</text>
    <text x="40" y="60" font-size="10.5" fill="#5b6570">逐行读取源码，边读边做</text>
    <text x="40" y="77" font-size="10.5" fill="#5b6570">没有独立的「编译」阶段</text>
    <text x="40" y="98" font-size="10.5" fill="#17181a">适合：写几行就想看到结果</text>
    <text x="40" y="115" font-size="10.5" fill="#17181a">失效点：慢；错误在跑到那</text>
    <text x="40" y="130" font-size="10.5" fill="#17181a">一行之前不会暴露</text>
    <path d="M228 77 H262" stroke="#1b4f8a" stroke-width="1.5" fill="none"/>
    <path d="M254 71 L264 77 L254 83" fill="none" stroke="#1b4f8a" stroke-width="1.5"/>
    <rect x="272" y="18" width="184" height="118" rx="4" fill="#f0f7f4" stroke="#0f7b5f" stroke-width="1.5"/>
    <text x="288" y="40" font-size="12" font-weight="700" fill="#0f7b5f">模型二 · 编译</text>
    <text x="288" y="60" font-size="10.5" fill="#5b6570">源码 → 机器指令文件</text>
    <text x="288" y="77" font-size="10.5" fill="#5b6570">再交给 CPU 直接执行</text>
    <text x="288" y="98" font-size="10.5" fill="#17181a">适合：性能与交付</text>
    <text x="288" y="115" font-size="10.5" fill="#17181a">失效点：改一行要重编</text>
    <text x="288" y="130" font-size="10.5" fill="#17181a">译；平台相关</text>
    <path d="M464 77 H498" stroke="#1b4f8a" stroke-width="1.5" fill="none"/>
    <path d="M490 71 L500 77 L490 83" fill="none" stroke="#1b4f8a" stroke-width="1.5"/>
    <rect x="508" y="18" width="148" height="118" rx="4" fill="#f7f8f9" stroke="#dfe5ea"/>
    <rect x="508" y="18" width="3" height="118" fill="#1b4f8a"/>
    <text x="522" y="40" font-size="12" font-weight="700" fill="#17181a">模型三 · 虚拟机</text>
    <text x="522" y="60" font-size="10.5" fill="#5b6570">源码 → 字节码</text>
    <text x="522" y="77" font-size="10.5" fill="#5b6570">虚拟机循环执行字节码</text>
    <text x="522" y="98" font-size="10.5" fill="#17181a">Python 走的是这条</text>
    <text x="522" y="115" font-size="10.5" fill="#17181a">折中：跨平台 + 比纯解</text>
    <text x="522" y="130" font-size="10.5" fill="#17181a">释快</text>
    <line x1="24" y1="156" x2="656" y2="156" stroke="#dfe5ea" stroke-width="1.5"/>
    <text x="24" y="180" font-size="11" font-weight="700" fill="#17181a">三个模型的共同前提（也是最常被误解的一点）</text>
    <text x="24" y="202" font-size="10.5" fill="#5b6570">无论走哪条路，最终执行的都是「非常简单的指令」，每条指令只做一件小事：读一个数、加两个数、跳到一个地址。</text>
    <text x="24" y="220" font-size="10.5" fill="#5b6570">所谓「程序能做复杂的事情」，是把几百万条这样的小指令按特定顺序排起来的结果，不存在「懂语义」的中间层。</text>
    <rect x="24" y="238" width="632" height="70" rx="4" fill="#fff" stroke="#dfe5ea"/>
    <rect x="24" y="238" width="3" height="70" fill="#0f7b5f"/>
    <text x="40" y="258" font-size="11" font-weight="700" fill="#0f7b5f">对 Python 读者的直接影响</text>
    <text x="40" y="278" font-size="10.5" fill="#5b6570">① 语法错误在「编译到字节码」时就被拦下，语法正确但类型不对的问题要跑到那一行才炸 —— 这解释了为什么调试要「走到出错的那一步」。</text>
    <text x="40" y="295" font-size="10.5" fill="#5b6570">② 同一份 .py 文件在任何装了 Python 的机器上都能跑，因为字节码由各自的解释器现场执行 —— 跨平台靠的是「统一字节码 + 各自实现」。</text>
  </g>
</svg>
<figcaption><b>图 1 |</b> 三种执行方式。它们的差异不在「高级 / 低级」，而在<b>翻译发生在什么时候</b>：解释是边跑边翻，编译是先全翻完再跑，虚拟机是先翻成一种中性指令再由软件执行。第三章会从这台「软件执行者」再往下走一层，看 CPU 到底怎么执行一条指令。</figcaption>
</figure>

<h3>1.3 变量到底是什么</h3>

<p>「变量是一个盒子，你把值放进去」—— 这是绝大多数入门教材的第一个类比。它好用，但在 Python 里会立刻出错。看这段代码：</p>

<pre><code>a = [<span class="mk">1</span>, <span class="mk">2</span>, <span class="mk">3</span>]
b = a          <span class="cm"># 如果变量是盒子，这里应该复制了一个盒子</span>
b.append(<span class="mk">99</span>)

print(a)       <span class="cm"># [1, 2, 3, 99]  ← 改了 b，a 也变了</span></code></pre>

<p>如果 <code>a</code> 是一个装着列表的盒子，<code>b = a</code> 应该把列表整个复制一份给 <code>b</code>，那么改 <code>b</code> 不该影响 <code>a</code>。
但实际结果是 <code>a</code> 也变了。<b>「盒子」这个类比在这里失效了</b>，因为 <code>b = a</code> 复制的不是列表本身，而是「a 指向哪个列表」这条信息。</p>

<div class="box finding"><span class="t">模型修正 1 —— 变量不是盒子，是贴在数据上的一个名字</span>
<p>Python 里更准确的模型是：<b>变量是一个名字标签，指向内存中的某个对象</b>。<code>a = [1,2,3]</code> 做两件事：在内存里造出一个列表对象，然后把名字 <code>a</code> 贴到它上面。
<code>b = a</code> 不造新对象，只是把名字 <code>b</code> 贴到<b>同一个</b>对象上。于是 <code>b.append(99)</code> 修改的是那唯一一个列表，<code>a</code> 和 <code>b</code> 看到的是同一个东西。</p>
<p>这也解释了两个看起来矛盾的事实：对<b>不可变</b>对象（数字、字符串、元组），「盒子模型」几乎总是对的，因为你没法修改它们，只能造一个新的再让名字指过去；
对<b>可变</b>对象（列表、字典、自定义对象），「盒子模型」会系统地给出错误预测。</p>
</div>

<pre><code><span class="cm"># 不可变对象：看起来像盒子，因为「修改」实际上是「换一个对象」</span>
x = <span class="mk">10</span>
y = x
y = y + <span class="mk">1</span>       <span class="cm"># 注意：这不是修改 10，而是造了 11 并把名字 y 贴上去</span>
print(x, y)      <span class="cm"># 10 11  ← x 没变，因为它指向的 10 从未被修改</span>

<span class="cm"># 可变对象：名字共享同一份数据</span>
xs = [<span class="mk">1</span>, <span class="mk">2</span>]
ys = xs
ys.append(<span class="mk">3</span>)    <span class="cm"># 修改的是那个唯一的列表</span>
print(xs, ys)    <span class="cm"># [1, 2, 3] [1, 2, 3]</span></code></pre>

<p>这个区分在什么时候会真的坑到你？最常见的两种场景：</p>

<pre><code><span class="cm"># 陷阱 A：在循环里基于同一个可变对象反复 append</span>
row = []
table = []
<span class="kw">for</span> i <span class="kw">in</span> <span class="kw">range</span>(<span class="mk">3</span>):
    row.append(i)
    table.append(row)   <span class="cm"># 每次都把同一个 row 贴进 table</span>
print(table)

<span class="cm"># 实际输出：[[0, 1, 2], [0, 1, 2], [0, 1, 2]]</span>
<span class="cm"># 直觉期待：[[0], [0, 1], [0, 1, 2]]</span>
<span class="cm"># 修法：table.append(row.copy())  或  把 row = [] 放进循环体</span></code></pre>

<pre><code><span class="cm"># 陷阱 B：函数默认参数只求值一次（Python 里最著名的坑之一）</span>
<span class="kw">def</span> collect(item, box=[]):     <span class="cm"># 这个 [] 在函数定义时就创建了，且只有这一个</span>
    box.append(item)
    <span class="kw">return</span> box

print(collect(<span class="mk">1</span>))   <span class="cm"># [1]</span>
print(collect(<span class="mk">2</span>))   <span class="cm"># [1, 2]  ← 不是 [2]</span>
print(collect(<span class="mk">3</span>))   <span class="cm"># [1, 2, 3]</span>

<span class="cm"># 修法：默认值用 None，在函数体内新建</span>
<span class="kw">def</span> collect(item, box=<span class="kw">None</span>):
    <span class="kw">if</span> box <span class="kw">is</span> <span class="kw">None</span>:
        box = []
    box.append(item)
    <span class="kw">return</span> box</code></pre>

<div class="box note"><span class="t">怎么判断某个操作是「修改」还是「新建」</span>
<p>一个可操作的判据：<b>看这个操作有没有赋值符号 <code>=</code></b>。有 <code>=</code>，就是让一个名字指向一个新对象；没有 <code>=</code>（例如 <code>lst.append(x)</code>、<code>d[k] = v</code>、<code>obj.attr = v</code>），就是就地修改那个对象。
这条判据覆盖了绝大多数日常情况，例外是那些名字里就带 <code>copy</code>、<code>copy_</code> 的方法，它们顾名思义。</p>
<p>要查看两个名字是否指向同一个对象，用 <code>is</code> 而不是 <code>==</code>：<code>a is b</code> 问的是「是不是同一个东西」，<code>a == b</code> 问的是「值是否相等」。
对列表来说，<code>[1,2] == [1,2]</code> 为真，<code>[1,2] is [1,2]</code> 为假。</p></div>

<h3>1.4 类型是什么，Python 的类型在哪里</h3>

<p>既然名字和对象是两个东西，那么「类型」属于谁？答案在 Python 里非常干脆：<b>类型属于对象，不属于名字。</b>
同一个名字可以先指一个字符串，再指一个整数，再指一个函数 —— 因为名字本身没有类型，它只是一个标签。</p>

<pre><code>v = <span class="mk">"3"</span>          <span class="cm"># 此刻 v 指向一个字符串对象</span>
v = <span class="mk">3</span>            <span class="cm"># 此刻 v 指向一个整数对象；前一个字符串没人引用，会被回收</span>
print(<span class="kw">type</span>(<span class="mk">3</span>))   <span class="cm"># &lt;class 'int'&gt;      类型是对象自带的</span>
print(<span class="kw">type</span>(v))   <span class="cm"># &lt;class 'int'&gt;</span></code></pre>

<div class="box finding"><span class="t">模型修正 2 —— 「变量有类型」在这句话里是错的</span>
<p>准确说法是：<b>对象有类型，名字只是引用</b>。这被称为<b>动态类型</b>。它和 C、Java 的<b>静态类型</b>是两种不同的设计取舍：</p>
<p><b>动态类型的好处</b>是代码短、迭代快，不用为「这个变量该声明成什么类型」分心。
<b>代价</b>是两类错误只能在运行时发现：一是「名字当前指向的对象不支持这个操作」（<code>TypeError</code>），
二是「这个类型的操作语义和你想的不一样」（例如 <code>"3" * 2</code> 得到 <code>"33"</code> 而不是 <code>6</code>）。</p>
<p>Python 3.5 之后提供了<b>类型标注</b>（<code>def f(x: int) -&gt; str:</code>），但默认<b>不检查、不影响运行</b> ——
它由 <code>mypy</code>、<code>pyright</code> 这类外部工具静态检查，相当于在动态语言上外挂一层可选的静态类型。
「标注只是给人和工具看的，运行时一律忽略」这一点，和后面要讲的 Java 完全不同。</p>
</div>

<table>
  <thead><tr><th style="width:120px;">语言</th><th style="width:110px;">类型检查在何时</th><th>典型代价与收益</th></tr></thead>
  <tbody>
    <tr><td>Python / JavaScript</td><td>运行时</td><td>写得快、读起来短；但拼写错、参数类型错这类问题要跑到那一步才发现。</td></tr>
    <tr><td>C / C++</td><td>编译时（并在运行时也不检查）</td><td>编译期就拦下大量错误、执行极快；代价是类型错误会变成「未定义行为」这种更难查的问题。</td></tr>
    <tr><td>Java / C# / Go</td><td>编译时（运行时补一部分检查）</td><td>错误提前到编译期，且运行时有明确的类型异常；代价是要写更多声明。</td></tr>
    <tr><td>TypeScript</td><td>编译时（编译产物擦掉类型）</td><td>给 JavaScript 外挂静态检查，运行时行为和 JS 完全一致。</td></tr>
  </tbody>
</table>

<div class="box takeaway"><span class="t">本节结论</span><p>变量是<b>指向对象的名字</b>，类型是<b>对象的属性</b>。
可变对象上的赋值共享数据，不可变对象上的赋值等于换对象 —— 这一个区分能解释 Python 中相当一部分「莫名其妙」的行为。</p></div>

<h3>1.5 一个常被写错的细节：is 与 == 不是一回事</h3>

<p>上面反复用到 <code>is</code>，这里把它和 <code>==</code> 的区别一次说清，因为它是本章第一个「看起来一样、实际完全不同」的例子。</p>

<table>
  <thead><tr><th style="width:120px;">写法</th><th style="width:230px;">问的问题</th><th>什么时候该用</th></tr></thead>
  <tbody>
    <tr><td><code>a == b</code></td><td>两个对象<b>值</b>相等吗</td><td>绝大多数比较。列表、字典、字符串的相等都靠它，可以自定义（<code>__eq__</code>）。</td></tr>
    <tr><td><code>a is b</code></td><td>两个名字指向<b>同一个对象</b>吗</td><td>只用于和<b>单例</b>比较：<code>is None</code>、<code>is True</code>、<code>is not None</code>。</td></tr>
  </tbody>
</table>

<pre><code>a = [<span class="mk">1</span>, <span class="mk">2</span>]
b = [<span class="mk">1</span>, <span class="mk">2</span>]
print(a == b)   <span class="cm"># True   两个列表内容相同</span>
print(a <span class="kw">is</span> b)   <span class="cm"># False  它们是内存里两个不同的对象</span>

c = a
print(a <span class="kw">is</span> c)   <span class="cm"># True   c 和 a 指向同一份数据</span>

<span class="cm"># 小整数会被缓存，导致 is 偶尔「看起来能用」——这正是它危险的地方</span>
print(<span class="mk">256</span> <span class="kw">is</span> <span class="mk">256</span>)   <span class="cm"># True   （CPython 缓存 -5..256）</span>
print(<span class="mk">257</span> <span class="kw">is</span> <span class="mk">257</span>)   <span class="cm"># 可能是 False —— 不要依赖这个结果</span></code></pre>

<div class="box finding"><span class="t">模型修正 3 —— <code>is</code> 不是「更严格的 ==」</span>
<p>初学者常以为 <code>is</code> 是「更强的相等判断」，所以重要场合用它更保险。<b>方向正好相反</b>：<code>is</code> 问的是身份，不是内容；
对不在缓存范围内的小整数、浮点数、字符串，<code>is</code> 的结果取决于解释器的实现细节，不是一个可以依赖的语言保证。</p>
<p>这条规则的正确用法只有一句：<b>除了和 <code>None</code>（以及 <code>True</code>/<code>False</code>）比较，其他一律用 <code>==</code>。</b>
PEP 8 就是这么写的 <em class="ev">[实践]</em>，理由是 <code>None</code> 是单例，比较身份就是比较值。</p>
</div>

<h3>1.6 本章用的读者约定：三种说法</h3>

<p>后面每一章都会遇到三类不同性质的陈述，混在一起读会出问题，所以这里把标注方式固定下来：</p>

<table>
  <thead><tr><th style="width:110px;">标注</th><th style="width:200px;">含义</th><th>举例</th></tr></thead>
  <tbody>
    <tr><td><em class="ev">[doc]</em></td><td>规范 / 官方文档已明确规定，可查原文</td><td>「Python 的函数默认参数只在定义时求值一次」——见 Python 官方教程 4.7.1。</td></tr>
    <tr><td><em class="ev">[实测]</em></td><td>本机跑出来的结果，附复现方式</td><td><code>dis.dis()</code> 显示两种写法的字节码一致。</td></tr>
    <tr><td><em class="ev">[实践]</em></td><td>工程取舍或社区共识，可以被合理反对</td><td>「PEP 8 建议用 <code>is not</code>」是风格建议，不是语言规则。</td></tr>
  </tbody>
</table>

<p>没有标注的句子，属于「本系列认为的基础事实」—— 如果发现某一句是错的，欢迎指出，那是最值得修的（也是这套笔记最需要被质疑的地方）。</p>

<footer>
  <p><strong>本节自测</strong> ① 写出 <code>a = [1,2]; b = a; b += [3]</code> 之后 <code>a</code> 的值，并说明为什么 <code>b += [3]</code> 和 <code>b = b + [3]</code> 的结果不同。
  ② 解释为什么 <code>def f(x, acc=[])</code> 是坏习惯，并给出两种修法。③ 已知 <code>x = "3"</code>，说明 <code>x * 2</code> 和 <code>int(x) * 2</code> 分别得到什么，以及为什么这两个结果都「不算错」。④ 判断 <code>a is b</code> 和 <code>a == b</code> 分别在什么场合使用，并说明为什么 <code>257 is 257</code> 的答案不可依赖。</p>
</footer>

<h2><span class="n">2</span>控制流：让程序会做判断和重复</h2>
<p class="lede">如果程序只能从上到下执行一遍，它什么也做不了。控制流的三种形态是所有算法的原材料。</p>

<h3>2.1 顺序、分支、循环：三种，也只有三种</h3>

<p>在早期的程序设计中，「结构化程序定理」给出了一个结论：<b>任何可计算的过程，都可以只用顺序、选择、循环三种结构组合出来</b>，
不需要 <code>goto</code> 这种任意跳转 <em class="ev">[doc]</em>（Böhm &amp; Jacopini, 1966）。这不是教学上的约定，而是一个可证明的结论 ——
它解释了为什么现代语言的语法里几乎只剩这三种形态。</p>

<table>
  <thead><tr><th style="width:88px;">结构</th><th style="width:170px;">Python 写法</th><th>它回答的问题</th></tr></thead>
  <tbody>
    <tr><td><b>顺序</b></td><td>一行接一行</td><td>「先做什么，再做什么」。</td></tr>
    <tr><td><b>分支</b></td><td><code>if / elif / else</code>，<code>match</code></td><td>「在什么条件下走哪条路」。</td></tr>
    <tr><td><b>循环</b></td><td><code>for</code>，<code>while</code></td><td>「同样的动作重复多少次，或重复到什么时候为止」。</td></tr>
  </tbody>
</table>

<h3>2.2 分支：最容易忽略的是「都不满足」</h3>

<pre><code><span class="kw">def</span> grade(score):
    <span class="kw">if</span> score &gt;= <span class="mk">90</span>:
        <span class="kw">return</span> <span class="mk">"A"</span>
    <span class="kw">elif</span> score &gt;= <span class="mk">80</span>:
        <span class="kw">return</span> <span class="mk">"B"</span>
    <span class="kw">elif</span> score &gt;= <span class="mk">60</span>:
        <span class="kw">return</span> <span class="mk">"C"</span>
    <span class="kw">return</span> <span class="mk">"F"</span>          <span class="cm"># 别漏掉这一行</span></code></pre>

<p>这段代码有一个不容易看出来的性质：<b>分支的顺序就是它的一部分语义</b>。
如果先写 <code>if score &gt;= 60: return "C"</code>，那么 95 分也会拿到 C —— 因为条件一旦满足就返回了，后面的分支根本不会被检查。
所以写分支时的第一个问题不是「条件写对没有」，而是 <b>「这些条件的先后顺序会不会改变结果」</b>。</p>

<div class="box finding"><span class="t">常见误区 —— 忘了「所有条件都不满足」的情况</span>
<p>上面那段函数如果去掉最后一行 <code>return "F"</code>，<code>grade(50)</code> 会返回 <code>None</code> 而不是报错。
这个 <code>None</code> 会一路传到调用它的地方，可能是打印出「你的成绩是 None」，也可能是在几层调用之后引发一个看不出源头的错误。</p>
<p>这是初学者最常踩的一类坑，也是「描述不完整」最典型的样子（§1.1）。防御方法很具体：<b>每个分支结构都想一遍「什么输入会走到所有分支之外」</b>，
能提前 <code>return</code> 就提前，最后留一个兜底分支。</p>
</div>

<h3>2.3 循环：for 与 while 的分工</h3>

<p>Python 的两个循环各有明确适用场景，混着用会让代码难读：</p>

<table>
  <thead><tr><th style="width:96px;">循环</th><th style="width:250px;">适合</th><th>不该用它的时候</th></tr></thead>
  <tbody>
    <tr><td><code>for</code></td><td>「对一批已知的东西，每个都做一遍」：列表、字典、文件的行。<b>遍历序列一律用 for。</b></td><td>你其实只需要知道「做了几次」——那就用 <code>for i in range(n)</code>，而不是把 <code>for</code> 硬套在别的对象上。</td></tr>
    <tr><td><code>while</code></td><td>「重复到条件不成立为止」：读输入直到用户停下、迭代求解直到误差足够小。</td><td>你已知要重复多少次 —— 用 <code>for</code> 更不容易写错（少了手动的计数器更新）。</td></tr>
  </tbody>
</table>

<div class="box finding"><span class="t">常见误区 —— 在遍历时修改序列</span>
<p>下面这段代码看起来完全合理，实际会漏掉元素：</p>
<pre><code>nums = [<span class="mk">1</span>, <span class="mk">2</span>, <span class="mk">3</span>, <span class="mk">4</span>, <span class="mk">5</span>, <span class="mk">6</span>]
<span class="kw">for</span> n <span class="kw">in</span> nums:
    <span class="kw">if</span> n % <span class="mk">2</span> == <span class="mk">0</span>:
        nums.remove(n)     <span class="cm"># 边遍历边删</span>
print(nums)                <span class="cm"># [1, 3, 5]？ 不，是 [1, 3, 5, 6]</span></code></pre>
<p>原因是：删掉一个元素之后，后面所有元素的下标都往前挪了一位，循环的下标却照旧往下走 —— 于是紧跟在被删元素后面的那个元素<b>被跳过了</b>。
这是「下标 + 就地修改」两个机制叠加出的后果，与语言无关，Java、C++ 里同样会发生（虽然 Java 会直接抛 <code>ConcurrentModificationException</code>）。</p>
<p>修法有两种，都比原本的写法更清楚地表达了意图：<b>建一个新列表</b>（<code>nums = [n for n in nums if n % 2]</code>），
或<b>在副本上遍历</b>（<code>for n in nums[:]:</code>）。后者虽然短，但要意识到 <code>nums[:]</code> 是在做一次复制。</p>
</div>

<h3>2.4 循环不变式：让「循环写对了」变成可论证的事</h3>

<p>到这里为止，判断一个循环对不对，靠的还是「看一遍、感觉没问题」。这在简单循环上够用，在复杂循环上完全不够。
有一种可操作的方法能把「感觉对」换成「能论证」 —— <b>循环不变式</b>。这是本章第一个需要动脑子的概念，值得慢读。</p>

<p><b>做法是三步：找到一个断言，然后证明它在你希望成立的所有时刻都成立。</b></p>

<ol>
  <li><b>初始化</b>：在进入循环之前，这个断言成立。</li>
  <li><b>保持</b>：如果循环体开始时断言成立，那么循环体结束时它仍然成立。</li>
  <li><b>终止 + 有用</b>：循环结束时（条件为假，且断言仍成立），它能推出你想要的结果。</li>
</ol>

<p>用一个例子把它落地。下面这个函数在列表里找 <code>target</code>，返回下标，找不到返回 <code>-1</code>：</p>

<pre><code><span class="kw">def</span> find(nums, target):
    i = <span class="mk">0</span>
    <span class="kw">while</span> i &lt; <span class="kw">len</span>(nums):
        <span class="kw">if</span> nums[i] == target:
            <span class="kw">return</span> i
        i = i + <span class="mk">1</span>
    <span class="kw">return</span> -<span class="mk">1</span></code></pre>

<p>取不变式为：<b>「<code>nums[0:i]</code> 里不包含 target」</b>。逐条验证：</p>

<table>
  <thead><tr><th style="width:104px;">步骤</th><th>为什么成立</th></tr></thead>
  <tbody>
    <tr><td><b>初始化</b></td><td>进入循环前 <code>i = 0</code>，<code>nums[0:0]</code> 是空列表，当然不含 target。</td></tr>
    <tr><td><b>保持</b></td><td>循环体只有在 <code>nums[i] != target</code> 时才会走到 <code>i = i + 1</code>；也就是说，扩展进「已检查区域」的这一格确实不是 target，所以 <code>nums[0:i+1]</code> 仍不含 target。</td></tr>
    <tr><td><b>终止</b></td><td>循环因 <code>i == len(nums)</code> 结束。此时不变式说 <code>nums[0:len(nums)]</code> 不含 target —— 也就是<b>整个列表</b>不含 target，所以返回 <code>-1</code> 是正确的。而中途 <code>return i</code> 的那条路，也已证明了 <code>nums[i] == target</code>。</td></tr>
  </tbody>
</table>

<div class="box note"><span class="t">为什么值得学这个「学院派」的方法</span>
<p>三个实际理由，都不抽象：</p>
<p><b>① 它把「边界该用 &lt; 还是 &lt;=」变成可推导的问题。</b>上面若把条件写成 <code>i &lt;= len(nums)</code>，终止时不变式只能推出「<code>nums[0:i]</code> 不含 target」而 <code>i</code> 可能是 <code>len+1</code> ——
推导不下去。你会立刻发现这里有错，而不是等运行时 <code>IndexError</code>。</p>
<p><b>② 它是二分查找类问题的唯一可靠解法。</b>二分查找的边界（取左中还是右中、区间是闭还是半开）有十来种写法，几乎人人写错过。
用不变式把「答案始终在区间内」写清楚，这些选择就不再是凭记忆，而是推导结果。这一条在第二章讲算法时会具体用上。</p>
<p><b>③ 它和后面几章的核心方法同源。</b>第四章讲并发时要论证「锁保护下的不变量不被破坏」，第六章讲事务时要论证「隔离级别保证了什么性质」，
用的都是同一套「找一个断言、证明它被保持」的思路。这里是最早、也是最简单的练习场。</p>
</div>

<h3>2.5 提前退出的两种写法：break 与 return</h3>

<p>上面 <code>find</code> 用的技巧值得单独点出来：它在循环体内部 <code>return</code>，而不是设一个标志位再在循环外面判断。
这一点在初学阶段通常被当作「风格问题」，实际上它关系到代码的正确性和长度：</p>

<pre><code><span class="cm"># 用标志位：需要一个额外的变量，还要在循环外再判断一次</span>
found = -<span class="mk">1</span>
<span class="kw">for</span> i, n <span class="kw">in</span> <span class="kw">enumerate</span>(nums):
    <span class="kw">if</span> n == target:
        found = i
        <span class="kw">break</span>
<span class="kw">if</span> found != -<span class="mk">1</span>:
    ...

<span class="cm"># 直接 return：意图更直接，少一个可能被忘记更新的变量</span>
<span class="kw">def</span> find(nums, target):
    <span class="kw">for</span> i, n <span class="kw">in</span> <span class="kw">enumerate</span>(nums):
        <span class="kw">if</span> n == target:
            <span class="kw">return</span> i
    <span class="kw">return</span> -<span class="mk">1</span></code></pre>

<p>「少一个可能被忘记更新的变量」不是修辞。标志位写法有一个具体的失败模式：如果循环体里有 <code>continue</code> 或嵌套分支，
很容易写出「找到了但没 <code>break</code>」或「<code>break</code> 了但标志位没设」的版本，而这种错误不会报错，只会给出错误结果。
<b>能用 <code>return</code> 就不用 <code>break</code>，能用 <code>break</code> 就不用标志位</b>，是一条性价比很高的经验规则 <em class="ev">[实践]</em>。</p>

<div class="box takeaway"><span class="t">本节结论</span><p>控制流只有三种形态，但每种都有「顺序即语义」的性质：<b>分支的条件顺序、循环的边界条件、提前退出的位置</b>，
都会改变结果而不改变语法正确性。循环不变式是把这个性质从「靠感觉」提升到「靠推导」的工具，也是后面几章反复出现的方法的原型。</p></div>

<footer>
  <p><strong>本节自测</strong> ① 把 <code>grade</code> 函数里的四个条件重新排序，找出哪些顺序会产生错误结果，并说明错误的原因。
  ② 对 <code>while i &lt; len(nums)</code> 改成 <code>while i &lt;= len(nums)</code>，用不变式推导出它会出错在哪一步。
  ③ 写出「在有序列表里二分查找 target」的循环不变式，并说出它帮你定了哪个边界选择。</p>
</footer>

<h2><span class="n">3</span>函数：抽象的第一个真正武器</h2>
<p class="lede">把代码装进一个盒子里，然后忘掉盒子里的细节 —— 这件事的价值远超「少写几行」。</p>

<h3>3.1 函数解决的不是重复，是「可以被忘掉」</h3>

<p>入门教材通常把函数的好处说成「避免重复代码」。这个说法不错，但漏掉了更重要的一半。</p>

<p>考虑一个真实场景：你在处理一批临床数据，需要把「日期字符串」转成标准格式。如果不写函数，你会在十几个地方各写一遍解析逻辑。
这时如果发现某个格式的处理错了，你要在十几个地方各改一遍 —— 而且很可能漏掉一处。这是「重复」的代价，属于比较容易被看到的那一面。</p>

<p>更关键的是另一面：<b>函数给一段逻辑起了名字，从此你可以在更高的层次上思考问题。</b>
写 <code>parse_date(s)</code> 之后，读代码的人（包括三个月后的你）看到的是「解析日期」这件事，而不必同时在大脑里维护「先 split 再取前四位再做合法性检查」的细节。
认知负荷被转移到了函数内部，而且是<b>一次性的</b>。</p>

<div class="box note"><span class="t">一个来自软件工程文献的视角</span>
<p>Peter Naur 在 1985 年的论文《Programming as Theory Building》里提出一个观点：<b>程序真正的价值不在源码本身，而在维护者脑子里的那套「理论」</b> ——
即「这个系统为什么是这么设计的、每一部分在承担什么职责」。源码只是这套理论的外在痕迹。</p>
<p>按这个视角看，「函数化」的意义就是<b>把理论显式地写进代码结构里</b>：一个名字取得好的函数，就是把「这一块在做什么」这件事保存了下来，
让下一个人能在不了解细节的前提下正确地使用它。反过来，一段复制粘贴出来的代码不携带任何理论，读者必须自己从零重建 —— 这才是重复代码真正的成本 <em class="ev">[lit]</em>。</p>
</div>

<h3>3.2 参数与返回：函数的接口就是它的契约</h3>

<p>一个函数的「签名」（名字、参数、返回值）是它对外承诺的全部内容。把签名写好，比把函数体写好更影响长期维护成本。</p>

<pre><code><span class="cm"># 不好：参数含义要靠读函数体才知道，调用处更难懂</span>
<span class="kw">def</span> process(data, <span class="mk">1</span>, <span class="mk">True</span>):
    ...

<span class="cm"># 好：调用处自带说明，参数顺序也不容易记错</span>
<span class="kw">def</span> process(data, *, mode=<span class="mk">"strict"</span>, drop_missing=<span class="kw">True</span>):
    ...

process(rows, mode=<span class="mk">"lenient"</span>, drop_missing=<span class="kw">False</span>)</code></pre>

<p>那个孤零零的 <code>*</code> 是 Python 的关键字参数标记：<b>它强制调用方用「名字=值」的形式传参</b>。
对于取值含义不直观的布尔参数（<code>process(rows, 1, True)</code> 里的 <code>True</code> 是什么意思？），这个约束能直接消灭一整类调用错误。</p>

<table>
  <thead><tr><th style="width:150px;">设计选择</th><th style="width:200px;">什么时候用</th><th>代价</th></tr></thead>
  <tbody>
    <tr><td>参数少（≤3 个）</td><td>默认。参数越多，调用处越容易传错位置。</td><td>参数超过三四个时，函数往往在承担太多职责，该拆。</td></tr>
    <tr><td>关键字参数 <code>*</code></td><td>参数含义不自明，或同类型参数多于一个（例如 <code>from_</code> 与 <code>to</code>）。</td><td>调用处写得更长，但可读性提升通常值得。</td></tr>
    <tr><td>返回多个值（元组）</td><td>几个值天然成组，且调用方通常一起用（例如 <code>x, y = divmod(a, b)</code>）。</td><td>调用方必须记住顺序；若超过三个值，考虑返回一个具名对象或 dataclass。</td></tr>
    <tr><td>就地修改参数</td><td>几乎不该用。惯例上，<b>函数返回值，不修改传入的列表/字典</b>。</td><td>调用方无法从调用形式看出数据被改了，是难以排查的 bug 来源。</td></tr>
  </tbody>
</table>

<div class="box finding"><span class="t">常见误区 —— 返回值和就地修改混着来</span>
<p>下面这个函数做了两件事，读者无法从名字判断是哪件：</p>
<pre><code><span class="kw">def</span> normalize(rows):
    <span class="kw">for</span> r <span class="kw">in</span> rows:
        r[<span class="mk">"name"</span>] = r[<span class="mk">"name"</span>].strip()
    <span class="kw">return</span> rows        <span class="cm"># 既改了传入的列表，又返回了它</span></code></pre>
<p>调用方 <code>rows2 = normalize(rows)</code> 看起来像是「得到一份处理过的副本」，实际上 <code>rows</code> 也被改了。
这在一次数据清洗里可能没事，在多处共享同一份数据的程序里会导致「数据莫名其妙变了」这类极难定位的问题。
<b>选一种并坚持：要么返回新对象（<code>out = []</code> 再逐条生成），要么明确命名成 <code>normalize_in_place</code>。</b></p>
</div>

<h3>3.3 调用栈：函数调用时到底发生了什么</h3>

<p>要理解递归，必须先看清「一次函数调用」的执行过程。这段描述是本节的原理部分，请对照下面这张图读。</p>

<figure>
<svg viewBox="0 0 680 300" role="img" aria-label="调用栈示意图：main 调用 fan，fan 调用 step，逐层压栈与返回">
  <g font-family="-apple-system,BlinkMacSystemFont,'Segoe UI','PingFang SC','Microsoft YaHei',Helvetica,Arial,sans-serif">
    <text x="24" y="20" font-size="10.5" font-weight="700" fill="#8b949e">调用栈：每进入一个函数，就压入一个「帧」；每返回一次，就弹出最上面那个帧</text>
    <rect x="24" y="34" width="300" height="120" rx="4" fill="#f7f8f9" stroke="#dfe5ea"/>
    <text x="38" y="54" font-size="11" font-weight="700" fill="#17181a">时刻 3：最深处</text>
    <rect x="38" y="62" width="272" height="26" rx="3" fill="#f0f7f4" stroke="#0f7b5f" stroke-width="1.2"/>
    <text x="48" y="79" font-size="10.5" fill="#0f7b5f">step(i=2)  ← 栈顶，正在执行</text>
    <rect x="38" y="92" width="272" height="26" rx="3" fill="#eef3f8" stroke="#1b4f8a" stroke-width="1.2"/>
    <text x="48" y="109" font-size="10.5" fill="#1b4f8a">fan(n=2)   等待 step 返回</text>
    <rect x="38" y="122" width="272" height="26" rx="3" fill="#eef3f8" stroke="#1b4f8a" stroke-width="1.2"/>
    <text x="48" y="139" font-size="10.5" fill="#1b4f8a">main       等待 fan 返回</text>
    <path d="M336 94 H372" stroke="#8b949e" stroke-width="1.5" fill="none"/>
    <path d="M364 88 L374 94 L364 100" fill="none" stroke="#8b949e" stroke-width="1.5"/>
    <rect x="384" y="34" width="272" height="120" rx="4" fill="#f7f8f9" stroke="#dfe5ea"/>
    <text x="398" y="54" font-size="11" font-weight="700" fill="#17181a">时刻 4：step 返回后</text>
    <rect x="398" y="62" width="244" height="26" rx="3" fill="#eef3f8" stroke="#1b4f8a" stroke-width="1.2"/>
    <text x="408" y="79" font-size="10.5" fill="#1b4f8a">fan(n=2)  ← 栈顶，继续往下执行</text>
    <rect x="398" y="92" width="244" height="26" rx="3" fill="#eef3f8" stroke="#1b4f8a" stroke-width="1.2"/>
    <text x="408" y="109" font-size="10.5" fill="#1b4f8a">main       等待 fan 返回</text>
    <text x="408" y="140" font-size="10" fill="#8b949e">step 的那个帧已经消失，它的局部变量也随之消失</text>
    <line x1="24" y1="172" x2="656" y2="172" stroke="#dfe5ea" stroke-width="1.5"/>
    <text x="24" y="194" font-size="11" font-weight="700" fill="#17181a">由这张图能直接推出的几件事</text>
    <text x="24" y="216" font-size="10.5" fill="#5b6570">① 「函数正在执行」= 它的帧在栈顶；报错时打印的 traceback 就是这张栈的快照，从最深的帧往上读。</text>
    <text x="24" y="234" font-size="10.5" fill="#5b6570">② 递归之所以消耗内存，是因为每一层都在栈上新增一个帧 —— 这正是「递归深度超限」报错的原因。</text>
    <text x="24" y="252" font-size="10.5" fill="#5b6570">③ 每个帧里放的是本次调用的参数与局部变量，所以同名函数被不同分支调用时互不干扰 —— 「作用域」的来源。</text>
    <text x="24" y="272" font-size="10.5" fill="#8b949e">第四章会再往前走一步：线程切换时，保存与恢复的就是这一整套帧所依赖的寄存器状态。</text>
  </g>
</svg>
<figcaption><b>图 2 |</b> 调用栈。左边是递归到最深处时的三个帧，右边是 <code>step</code> 返回之后的两个帧。<b>这张图是理解递归、作用域和报错信息的共同基础</b> —— 它们看起来是三件事，其实是同一套机制的三个侧面。</figcaption>
</figure>

<pre><code><span class="kw">def</span> step(i):
    <span class="kw">if</span> i == <span class="mk">0</span>:
        <span class="kw">return</span> <span class="mk">0</span>
    <span class="kw">return</span> step(i - <span class="mk">1</span>) + <span class="mk">1</span>       <span class="cm"># 先压一步，再回填</span>

<span class="kw">def</span> fan(n):
    <span class="kw">return</span> step(n) * <span class="mk">2</span>

print(fan(<span class="mk">2</span>))    <span class="cm"># 4</span>
<span class="cm"># step(2) -> step(1) -> step(0)</span>
<span class="cm">#         &lt;- 0+1    &lt;- 1+1       三层，从最深往回填</span></code></pre>

<h3>3.4 递归：把「大问题」化成「同类的小问题」</h3>

<p>递归不是「函数调用自身」这种技巧，而是<b>一种定义方式</b>：把问题 P(n) 的答案，定义为 P(n−1) 的答案与一次运算的组合。
上一小节的 <code>step</code> 就是这个形式：<code>step(n) = step(n−1) + 1</code>，终止条件是 <code>step(0) = 0</code>。</p>

<p>写递归时只要回答三个问题，答案就是完整的：</p>

<ol>
  <li><b>基准情形</b>：什么问题小到可以直接回答？（<code>i == 0</code> 返回 0）</li>
  <li><b>递推关系</b>：大问题的答案怎么由小一号的答案拼出来？（<code>step(i-1) + 1</code>）</li>
  <li><b>收敛性</b>：每次递归，问题是否确实在变小，从而一定会碰到基准情形？（<code>i - 1</code> 每次减 1，必然归零）</li>
</ol>

<div class="box finding"><span class="t">常见误区 —— 缺少收敛性论证，导致栈溢出</span>
<p>把上面第三个问题忽略掉，就会写出这种代码：</p>
<pre><code><span class="kw">def</span> countdown(n):
    <span class="kw">print</span>(n)
    countdown(n - <span class="mk">1</span>)      <span class="cm"># 没有 terminate 条件</span></code></pre>
<p>它会一直压栈，直到 Python 抛出 <code>RecursionError: maximum recursion depth exceeded</code>。
关键要理解的是：<b>这个错误不是「递归用得太深」，而是「递归忘了停」</b>。前者是性能问题，后者是逻辑错误 —— 它们报的是同一个异常，但修法完全不同。</p>
</div>

<p>接着看一个真正体现递归价值的例子 —— 计算一个目录树里所有文件的总大小：</p>

<pre><code><span class="kw">def</span> total_size(path):
    <span class="cm"># 基准情形：这是一个文件，直接返回它的大小</span>
    <span class="kw">if</span> os.path.isfile(path):
        <span class="kw">return</span> os.path.getsize(path)
    <span class="cm"># 递推：这是一个目录，总和 = 每个子项各自的总和之和</span>
    total = <span class="mk">0</span>
    <span class="kw">for</span> name <span class="kw">in</span> os.listdir(path):
        total += total_size(os.path.join(path, name))
    <span class="kw">return</span> total</code></pre>

<p>这段代码值得玩味的地方是：<b>它没有在任何地方区分「目录有多少层」</b>。
第一次看到的读者往往会疑惑「这样怎么能处理很深的目录」，答案是「因为 <code>total_size</code> 的定义本身就是递归的」——
「一个目录的总大小 = 它所有子项的总大小之和」，而子项可能是文件（基准情形）也可能是目录（同一个递推）。
递归在这里不是绕圈，而是<b>把定义直接翻译成了代码</b>。</p>

<div class="box note"><span class="t">什么时候该用递归，什么时候不该</span>
<p><b>该用</b>：问题本身是递归定义的（树、目录、语法结构、分治算法），且深度可控（几十到几百层）。</p>
<p><b>不该用</b>：深度可能很大（处理百万行数据、深链表的遍历）—— Python 默认递归深度约 1000 层，超过就会 <code>RecursionError</code>。
另外 Python 没有尾调用优化 <em class="ev">[doc]</em>，所以「尾递归会变快」这类来自函数式语言的经验在这里不成立，深递归只能改成迭代。</p>
<p><b>一个可行的判据</b>：如果你把递推关系写下来之后，发现自己需要「先递归到底、再在回来的路上做点什么」（像 <code>step</code> 那样回填），那用递归是自然的；
如果整个循环只是「从头到尾扫一遍」，迭代更简单也更省内存。</p>
</div>

<div class="box takeaway"><span class="t">本节结论</span><p>函数的第一个价值是<b>把一段逻辑命名</b>，让读者能在更高层次上思考，第二个价值才是消除重复。
理解函数调用要看调用栈：<b>帧的压入与弹出</b>同时解释了递归、作用域和 traceback。写递归只需回答三件事 —— 基准、递推、收敛。</p></div>

<footer>
  <p><strong>本节自测</strong> ① 用不变式的三步（基准 / 递推 / 收敛）论证 <code>step(i)</code> 一定终止，并说明把 <code>i - 1</code> 改成 <code>i - 2</code> 之后会发生什么。
  ② 把 <code>total_size</code> 改写成不用递归的版本，并说明改写过程中你必须额外维护什么数据结构。
  ③ 下面这个函数有什么问题？<code>def f(n): return n * f(n - 1)</code></p>
</footer>

<h2><span class="n">4</span>数据组织：从序列到字典</h2>
<p class="lede">Python 的内置容器不是语法糖，它们各自对应一种访问模式 —— 选错容器的代价会在数据量上来之后显现。</p>

<h3>4.1 三种容器，三种访问模式</h3>

<p>日常用得最多的三种内置容器，差异不在「能装什么」，而在<b>「你想怎么找东西」</b>：</p>

<table>
  <thead><tr><th style="width:104px;">容器</th><th style="width:200px;">访问模式</th><th>典型场景</th></tr></thead>
  <tbody>
    <tr><td><code>list</code></td><td>按位置取：<code>xs[3]</code>，按顺序遍历</td><td>有天然的先后次序，或需要按序号访问 —— 时间序列、日志行。</td></tr>
    <tr><td><code>dict</code></td><td>按键取：<code>d["id"]</code></td><td>需要用某个字段快速找到记录 —— 按受试者编号查访视。</td></tr>
    <tr><td><code>set</code></td><td>只问在不在：<code>x in s</code></td><td>去重、求交集、判重 —— 已经处理过哪些编号。</td></tr>
  </tbody>
</table>

<p>这三种选择有一个量化的判据，第二章会正式讲，这里先给出直觉：<b>「按位置取」和「按键取」在代价上完全不是一回事</b>。
在一个 10 万个元素的列表里查一个值，平均要比较 5 万次；在同样规模的集合里查，几乎是瞬间。</p>

<pre><code><span class="cm"># 这段代码慢在哪？</span>
seen = []
<span class="kw">for</span> row <span class="kw">in</span> rows:            <span class="cm"># 假设 rows 有 10 万行</span>
    <span class="kw">if</span> row[<span class="mk">"id"</span>] <span class="kw">not</span> <span class="kw">in</span> seen:   <span class="cm"># 每次都在列表里从头扫一遍</span>
        seen.append(row[<span class="mk">"id"</span>])
        process(row)

<span class="cm"># 改成集合：语义完全一样，代价从「与已处理数量成正比」变成「常数」</span>
seen = <span class="kw">set</span>()
<span class="kw">for</span> row <span class="kw">in</span> rows:
    <span class="kw">if</span> row[<span class="mk">"id"</span>] <span class="kw">not</span> <span class="kw">in</span> seen:
        seen.add(row[<span class="mk">"id"</span>])
        process(row)</code></pre>

<div class="box finding"><span class="t">模型修正 4 —— 「列表也能查，为什么还要 set」</span>
<p>对初学者来说，<code>list</code> 是万能的，什么都能做。这个印象的危险之处在于：<b><code>x in some_list</code> 和 <code>x in some_set</code> 写法一样，代价差几个数量级</b>，
而代码看起来几乎没变。10 行数据时毫无感觉，10 万行时从 0.1 秒变成几十分钟。</p>
<p>记住一条经验规则就够用：<b>只要你在判断「某个值出现过没有」，就用 <code>set</code>；只要你在按某个字段找记录，就用 <code>dict</code>。</b>
这条规则在第二章会被写成精确的复杂度表述，但你现在就可以开始用。</p>
</div>

<h3>4.2 遍历的三种正确姿势</h3>

<pre><code>ages = {<span class="mk">"a"</span>: <span class="mk">30</span>, <span class="mk">"b"</span>: <span class="mk">45</span>}

<span class="cm"># 只要键（dict 的默认行为就是遍历键）</span>
<span class="kw">for</span> name <span class="kw">in</span> ages: ...

<span class="cm"># 键和值都要 —— 用 items()，不要退回到 ages[k]</span>
<span class="kw">for</span> name, age <span class="kw">in</span> ages.items(): ...

<span class="cm"># 需要序号 —— 用 enumerate，不要自己数 i = i + 1</span>
<span class="kw">for</span> i, row <span class="kw">in</span> <span class="kw">enumerate</span>(rows): ...

<span class="cm"># 两个序列并排走 —— 用 zip</span>
<span class="kw">for</span> name, age <span class="kw">in</span> <span class="kw">zip</span>(names, ages_list): ...</code></pre>

<p>这四种写法有一个共同点：<b>它们都省掉了一个需要手动维护的中间变量</b>（下标、计数器、临时取值）。
§2.5 说过「少一个可能被忘记更新的变量」不是修辞，这里又出现一次 —— 这类「让编译器替你管状态」的写法，是新手最容易获得的无成本提升。</p>

<div class="box finding"><span class="t">常见误区 —— 用下标遍历</span>
<p><code>for i in range(len(xs)): x = xs[i]</code> 这种写法在 Python 里几乎总是错的（除了需要下标值本身的情况）。
它的两个问题：一是多了一个可能在循环体里被意外修改的 <code>i</code>；二是当你从 <code>list</code> 换成 <code>dict</code> 或生成器时，整段代码都要重写。</p>
<p><code>for x in xs</code> 这种写法依赖的接口是「可迭代」，<b>几乎所有容器都支持</b>，所以它更不容易被数据结构的更换打破。</p>
</div>

<h3>4.3 推导式：一句话描述「从一批数据得到另一批」</h3>

<pre><code><span class="cm"># 过滤 + 变换</span>
squares_of_even = [n * n <span class="kw">for</span> n <span class="kw">in</span> nums <span class="kw">if</span> n % <span class="mk">2</span> == <span class="mk">0</span>]

<span class="cm"># 构造字典</span>
by_id = {row[<span class="mk">"id"</span>]: row <span class="kw">for</span> row <span class="kw">in</span> rows}

<span class="cm"># 构造集合（顺便去重）</span>
ids = {row[<span class="mk">"id"</span>] <span class="kw">for</span> row <span class="kw">in</span> rows}</code></pre>

<p>推导式的价值不是「短」，而是<b>它把「遍历 + 条件 + 收集」压缩成一个表达式，读者一眼就能看出「输入是什么、输出是什么」</b>。
对应的显式循环版本需要读四五行才能建立同样的印象。</p>

<div class="box"><span class="t">什么时候不要用推导式</span>
<p>三条判据，满足任一条就该退回普通循环：<b>①</b> 循环体里有副作用（打印、写文件、调用接口），
<b>②</b> 需要嵌套超过两层，<b>③</b> 需要在循环之间共享状态（例如「累计和」）。
推导式的定位是「构造一个新容器」，超出这个范围就会写得又长又难读。</p>
<p>另外注意一个语义细节：方括号 <code>[]</code> 会<b>立刻</b>构造出整个列表，而圆括号 <code>()</code> 生成的是「生成器」——
后者不占内存但只能遍历一次。处理大文件时，这个区别是「能不能跑起来」的区别。</p>
</div>

<h3>4.4 可变与不可变：说回 §1.3 的那个区分</h3>

<p>容器选择还有一个维度是「能不能改」。它决定了这个对象能不能当作字典的键，也决定了函数传参时的行为：</p>

<table>
  <thead><tr><th style="width:130px;">类型</th><th style="width:110px;">可变？</th><th style="width:150px;">能否当 dict 的键</th><th>为什么</th></tr></thead>
  <tbody>
    <tr><td><code>list</code></td><td>可变</td><td><span class="pill bad">不能</span></td><td>内容会变，无法确定它「一直哈希到同一个位置」。</td></tr>
    <tr><td><code>dict</code> / <code>set</code></td><td>可变</td><td><span class="pill bad">不能</span></td><td>同上。</td></tr>
    <tr><td><code>tuple</code></td><td>不可变</td><td><span class="pill ok">能</span></td><td>内容固定，哈希值稳定。</td></tr>
    <tr><td><code>str</code> / <code>int</code> / <code>float</code></td><td>不可变</td><td><span class="pill ok">能</span></td><td>同上。</td></tr>
  </tbody>
</table>

<div class="box takeaway"><span class="t">本节结论</span><p>选容器的依据是<b>访问模式</b>而不是习惯：「按位置」用 list，「按字段找」用 dict，「判断有没有」用 set。
<code>list</code> 与 <code>set</code> 的查找写法一样但代价相差几个数量级 —— 这是初学阶段最容易无成本避免的一类性能问题。</p></div>

<footer>
  <p><strong>本节自测</strong> ① 有一个 100 万行的 CSV，每行有唯一编号，你需要按编号查出若干行。用 <code>list</code> 和用 <code>dict</code> 分别怎么写？为什么后者更合适？
  ② 下面这段代码有两个问题，找出来：<code>xs = [1,2,3]; for i in range(len(xs)): xs.append(xs[i] * 2)</code>
  ③ 说明为什么 <code>[1,2]</code> 不能当作字典的键，而 <code>(1,2)</code> 可以。</p>
</footer>

<h2><span class="n">5</span>调试与错误处理：程序一定会写错</h2>
<p class="lede">这一节不讲「怎么一次写对」，讲「写错之后怎么最快找到原因」—— 后者是更实际的能力。</p>

<h3>5.1 三类错误，三种不同的排查方式</h3>

<p>把所有出错的情况混成一种「报错了」来处理，是效率最低的做法。按<b>发现时机</b>分类，每一类都有自己的应对方式：</p>

<table>
  <thead><tr><th style="width:120px;">类型</th><th style="width:190px;">什么时候被发现</th><th>典型例子与排查手段</th></tr></thead>
  <tbody>
    <tr>
      <td><b>语法错误</b></td>
      <td>还没开始运行，编译成字节码时就拦下</td>
      <td><code>SyntaxError</code>、缩进不一致。<b>读数、看箭头位置</b>即可，通常错在箭头<b>之前</b>那一行的末尾。</td>
    </tr>
    <tr>
      <td><b>运行时错误</b></td>
      <td>执行到那一行时抛出异常</td>
      <td><code>TypeError</code>、<code>IndexError</code>、<code>KeyError</code>。<b>看 traceback 最下面一行的帧</b> —— 那是真正出错的位置。</td>
    </tr>
    <tr>
      <td><b>逻辑错误</b></td>
      <td>程序正常结束，结果是错的</td>
      <td><b>没有报错信息可用</b>，最难的一类。只能靠「缩小输入规模 + 打印中间状态」定位。</td>
    </tr>
  </tbody>
</table>

<div class="box note"><span class="t">怎么读 traceback（这是本节最实用的一段）</span>
<p>Python 的报错信息是从上往下读<b>调用过程</b>、从下往上读<b>出错原因</b>的。以这段为例：</p>
<pre><code>Traceback (most recent call last):
  File <span class="mk">"main.py"</span>, line <span class="mk">42</span>, <span class="kw">in</span> &lt;module&gt;
    total = summarize(rows)
  File <span class="mk">"main.py"</span>, line <span class="mk">28</span>, <span class="kw">in</span> summarize
    <span class="kw">return</span> sum(r[<span class="mk">"value"</span>] <span class="kw">for</span> r <span class="kw">in</span> rows) / <span class="kw">len</span>(rows)
<span class="kw">ZeroDivisionError</span>: division by zero</code></pre>
<p><b>最后一段</b>是「什么错、错在源码的哪一行」：<code>ZeroDivisionError</code> 发生在 <code>len(rows)</code> 为 0 时。
<b>倒数第二段</b>是「是谁调用了它」：<code>main.py</code> 第 42 行。这两条信息合起来就是「症状 + 触发路径」，
绝大多数运行时错误靠这两段就能定位，不需要打断点。</p>
<p>初学者常见的两个误操作：一是只看到最后一行 <code>ZeroDivisionError</code> 就去猜，
二是看到一长串 traceback 就慌。<b>正确做法是先看最后三行</b>，再决定要不要往上读。</p>
</div>

<h3>5.2 异常处理：把「出错」当成一种正常输入</h3>

<p>异常不是为了「让程序不崩」，而是为了让<b>「某个操作可能失败」这件事显式地出现在代码里</b>。
理解这一点，就能理解为什么裸 <code>except</code> 是有害的：</p>

<pre><code><span class="cm"># 反面例子：捕获一切，然后什么都不说</span>
<span class="kw">try</span>:
    value = config[<span class="mk">"threshold"</span>]
<span class="kw">except</span>:
    <span class="kw">pass</span>

<span class="cm"># 后果：如果 config 其实是个字符串（写错了代码），这个错也被吞掉了</span>
<span class="cm">#      你会得到一个莫名其妙的 NameError，在几十行之后才出现</span>

<span class="cm"># 正面写法：只处理你预期的那个失败，并给出可操作的替代</span>
<span class="kw">try</span>:
    value = config[<span class="mk">"threshold"</span>]
<span class="kw">except</span> KeyError:
    value = <span class="mk">0.05</span>          <span class="cm"># 明确写下「缺省是多少」</span>
    log.warning(<span class="mk">"threshold 未配置，使用默认值 %s"</span>, value)</code></pre>

<p>两者的差别不在长短，而在<b>「错误会不会被静默吞掉」</b>。裸 <code>except</code> 的代价是把所有 bug 变成「程序没报错但结果不对」，
这是 §5.1 里最难排查的那一类。</p>

<table>
  <thead><tr><th style="width:150px;">写法</th><th style="width:170px;">什么时候用</th><th>风险</th></tr></thead>
  <tbody>
    <tr><td><code>except SpecificError:</code></td><td>默认选择。你已经想清楚哪个操作会怎样失败。</td><td>几乎无风险；唯一要注意是别写成一串 <code>except</code> 把逻辑稀释掉。</td></tr>
    <tr><td><code>except Exception:</code></td><td>只用在程序的最外层（日志、清理、退出），<b>用一次，记录完整 traceback</b>。</td><td>用在内层就会吞掉 bug。</td></tr>
    <tr><td>裸 <code>except:</code></td><td>几乎永远不要用。它会连 <code>KeyboardInterrupt</code> 一起吞掉，Ctrl+C 都停不下来。</td><td>高。</td></tr>
  </tbody>
</table>

<div class="box finding"><span class="t">常见误区 —— 用异常做流程控制</span>
<p>下面这种写法能跑，但把「正常路径」和「异常路径」颠倒了：</p>
<pre><code><span class="kw">try</span>:
    v = d[key]
<span class="kw">except</span> KeyError:
    v = default     <span class="cm"># 「键不存在」是常见情况，不该走异常分支</span></code></pre>
<p>异常在 Python 里<b>有实实在在的性能开销</b>（构造异常对象、回溯调用栈），而且它表达的语义是「发生了意外」。
如果「键不存在」在你的场景里很正常，应该用 <code>d.get(key, default)</code>；只有真正异常的情况才用 <code>try</code>。
这不是风格洁癖，而是「让代码的语序反映实际的执行频次」。</p>
</div>

<h3>5.3 一个可复用的排查流程</h3>

<p>面对一个「结果不对但没报错」的程序，下面是按性价比排序的步骤。它适用于任何语言，后面几章遇到的 bug 也照样能用：</p>

<ol>
  <li><b>缩小输入规模。</b>把处理 10 万行改成处理 3 行，并且手工算出这 3 行的正确答案。这一步能解决相当比例的问题 —— 因为多数 bug 只在特定输入下出现，而你缩小输入时正好需要想清楚「什么样的输入才是关键输入」。</li>
  <li><b>确认「在哪一步开始不对」。</b>在中间位置打印状态，确定错误是出现在这一半之前还是之后。反复二分，几步就能把范围压到几行。</li>
  <li><b>把怀疑的假设写成断言。</b><code>assert len(rows) &gt; 0</code>、<code>assert isinstance(x, int)</code>。断言如果通过，说明你「以为」的某个前提其实是错的 —— 这本身是重要信息。Python 的 <code>assert</code> 会在带 <code>-O</code> 运行时被跳过，所以它只用于调试，不用于校验外部输入。</li>
  <li><b>读文档，而不是猜。</b>到这一步还查不出来，往往是因为你对某个函数的行为有错误假设（例如「排序是稳定的吗」「切片越界会不会报错」）。这类问题只能靠查官方文档解决，靠试出来的结论不可靠。</li>
  <li><b>构造最小可复现例子。</b>把问题压缩成一段十几行、可以贴给别人跑的代码。这个动作的价值在于：<b>有相当一部分 bug 在构造最小例子的过程中自己就暴露了</b>；剩下的那些，因为例子足够小，别人也才有耐心帮你看。</li>
</ol>

<div class="box"><span class="t">一条常被忽略的建议</span>
<p>第 5 步不只是「为了问别人」，更是<b>自我排查的技术</b>。当你必须在一页纸里把一个 bug 讲清楚时，你会被迫把每条「我以为」写下来 ——
而错误几乎总是躲在这些「我以为」里。这个技巧在 Stack Overflow 式提问文化里被称为「橡皮鸭调试法」，
但它真正的用途不是问问题，而是让隐藏的前提显形 <em class="ev">[实践]</em>。</p>
</div>

<div class="box takeaway"><span class="t">本节结论</span><p>先分清错误属于<b>语法 / 运行时 / 逻辑</b>哪一类，再选手段：前两类靠 traceback 的后三行定位，第三类只能靠「缩小输入 + 二分定位」。
异常用于「预期之外的失败」，不要用于常见情况；裸 <code>except</code> 会把 bug 变成更难查的错误结果。</p></div>

<footer>
  <p><strong>本节自测</strong> ① 说明为什么 <code>except: pass</code> 会导致「程序不报错但结果不对」这类最难排查的问题，举一个具体场景。
  ② 有一段代码在 10 万行数据上结果错了，在小样本上是对的。写出你的前三步排查动作。
  ③ 用一句话说明 <code>assert</code> 适合用在哪里、不适合用在哪里。</p>
</footer>

<h2><span class="n">6</span>工程习惯：让半年后的自己还能读懂</h2>
<p class="lede">这一节不是风格讲评。它的判据只有一个：<b>三个月后你回来改这段代码，需要多久才能安全地改动它。</b></p>

<h3>6.1 命名的唯一标准是可检索</h3>

<p>命名争论通常停留在「好名字更优雅」，但有一个更硬的判据：<b>你之后要用什么词去搜它</b>。</p>

<table>
  <thead><tr><th style="width:170px;">写法</th><th style="width:130px;">问题</th><th>改法</th></tr></thead>
  <tbody>
    <tr><td><code>d</code> / <code>x</code> / <code>tmp</code></td><td>无法搜索，也无法判断作用域</td><td>按内容命名：<code>visits_by_id</code>、<code>threshold_value</code>。</td></tr>
    <tr><td><code>data2</code> / <code>new_data</code></td><td>「新」是相对什么？过一个月就失效</td><td>按处理阶段命名：<code>raw_rows</code> → <code>cleaned_rows</code> → <code>analysis_rows</code>。</td></tr>
    <tr><td><code>flag</code> / <code>status</code></td><td>布尔还是枚举？含义不明确</td><td>布尔用 <code>is_</code> / <code>has_</code> 前缀：<code>is_complete</code>、<code>has_missing</code>。</td></tr>
  </tbody>
</table>

<div class="box note"><span class="t">为什么「命名」列在工程习惯的第一条</span>
<p>因为它是唯一一项<b>成本几乎为零、收益贯穿全项目生命周期</b>的改进。它不需要重构、不需要测试、不会引入风险 ——
想清楚一个变量的名字只需十秒钟，而这十秒会在之后每次读这段代码时反复回本。</p>
<p>反过来，命名混乱的累积代价也很大：当 <code>data1</code>、<code>data2</code>、<code>tmp</code> 遍布一个文件时，读者必须把每个变量的生命周期在脑子里重建一遍才能动手，
而这个重建过程每次都要重来。</p>
</div>

<h3>6.2 注释解释「为什么」，不解释「是什么」</h3>

<pre><code><span class="cm"># 无用的注释：把代码翻译一遍，代码改了注释还是旧的</span>
i = i + <span class="mk">1</span>      <span class="cm"># i 加 1</span>

<span class="cm"># 有用的注释：解释代码看不出来的决策</span>
<span class="cm"># 用 1e-9 而不是 0，避免浮点误差导致永远无法收敛</span>
<span class="kw">while</span> <span class="kw">abs</span>(new - old) &gt; <span class="mk">1e-9</span>:
    ...

<span class="cm"># 有用的注释：标注出处与约束</span>
<span class="cm"># 依据 CDISC SDTMIG 3.4 §4.4.1，这里必须保留原始数值</span>
raw_value = row[<span class="mk">"original"</span>]</code></pre>

<p>一个可操作的判据：<b>如果你的注释可以直接翻译成一行代码，删掉它。</b>
如果它回答的是「为什么这样写」「依据是什么」「有什么限制」，保留它 —— 这些信息无法从代码本身读出。</p>

<h3>6.3 版本控制：把「改了什么」变成可查的事实</h3>

<p>即使只是自学练手，也用 Git。理由不是「规范」，而是<b>它给了你一次后悔的机会</b>：
当你把一段能跑的代码改坏了、又说不清改了哪几行时，<code>git diff</code> 是唯一能告诉你答案的工具。</p>

<pre><code>git init
git add .
git commit -m <span class="mk">"实现基本的日期解析"</span>

<span class="cm"># 改坏了想看看改了什么</span>
git diff

<span class="cm"># 想回到上一个能跑的版本（未提交的改动会被丢弃）</span>
git checkout -- .

<span class="cm"># 想让某个已经提交的版本回到工作区</span>
git show &lt;hash&gt;:main.py</code></pre>

<div class="box"><span class="t">提交信息的写法</span>
<p>「修复 bug」「更新」这类信息在一个月后毫无价值。<b>好的提交信息回答「为什么改」</b>：
「修复空列表导致的除零错误」比「修复 bug」多提供了一条可搜索的线索。这一条与 §6.2 的判据同源 —— 都在记录「看不见的东西」。</p>
</div>

<h3>6.4 三条可以立刻执行的经验规则</h3>

<table>
  <thead><tr><th style="width:196px;">规则</th><th>为什么</th></tr></thead>
  <tbody>
    <tr><td><b>一个函数只做一件事</b></td><td>「做两件事」的函数无法被可靠复用，测试和改动的成本都翻倍。判据：能否用一句不含「和」的话说明它做什么。</td></tr>
    <tr><td><b>把魔法数字提成常量</b></td><td><code>if age &gt; 65</code> 中的 65 出现在五个地方时，改判定标准要改五处。写成 <code>ELDERLY_AGE = 65</code> 只需改一处，且名字解释了含义。</td></tr>
    <tr><td><b>早返回，减少嵌套</b></td><td><code>if not valid: return</code> 比把主体逻辑包进 <code>if valid:</code> 少一层缩进。嵌套深度是阅读难度的主要来源之一。</td></tr>
  </tbody>
</table>

<div class="box takeaway"><span class="t">本节结论</span><p>工程习惯的判据不是「是否规范」，而是<b>「降低下一次改动的成本」</b>：可检索的命名、解释为什么的注释、可回退的版本控制。
三者都不需要额外工具，今天就可以开始。</p></div>

<footer>
  <p><strong>本节自测</strong> ① 找出你最近写过的一段代码，把其中三个「无信息的命名」改成可检索的，说明改的前提是你必须理解什么。
  ② 给你正在写的代码加一条「解释为什么」的注释 —— 如果找不到可以这样写的地方，说明这段代码没有需要解释的决策，或你对它还不够熟悉。
  ③ 用一句话说明：为什么「早返回」能降低阅读难度。</p>
</footer>

<h2><span class="n">7</span>参考资料</h2>
<p class="lede">推荐理由、适用阶段与难度都写在表里。同一门课换一门替代课完全可能更适合你 —— 判据永远是你自己的进度，不是列表本身。</p>

<table>
  <thead><tr><th style="width:86px;">类型</th><th style="width:250px;">材料</th><th>推荐理由</th><th style="width:96px;">适用阶段</th><th style="width:52px;">难度</th></tr></thead>
  <tbody>
    <tr><td>教材</td><td><b>《Python 编程：从入门到实践》（Eric Matthes）</b></td><td>章节短、例子多，适合零基础的第一遍。本篇 §1–§6 的语法部分与它第 2–9 章基本对应。</td><td>入门</td><td>低</td></tr>
    <tr><td>教材</td><td><b>《Think Python》（Allen Downey）</b></td><td>把编程当思维训练而不是语法练习。第 4 章（函数接口）、第 5 章（条件与递归）、第 11 章（字典）对本章尤其有用。</td><td>入门～进阶</td><td>低</td></tr>
    <tr><td>教材</td><td><b>《Structure and Interpretation of Computer Programs》（SICP）</b></td><td>抽象与递归的经典源头。不必读完 —— 读第 1 章就能获得本篇 §3 想要的那种理解，且用 Scheme 讲反而更能看清「函数是什么」。</td><td>进阶</td><td>高</td></tr>
    <tr><td>教材</td><td><b>《Programming as Theory Building》（Peter Naur, 1985）</b></td><td>本篇 §3.1 与 §6 的理论依据。一篇二十页的论文，解释「为什么代码是给人看的」不是软要求。发表年代早，但论点不随语言变化。</td><td>进阶</td><td>中</td></tr>
    <tr><td>课程</td><td><b>MIT 6.100L《Introduction to CS and Programming Using Python》</b></td><td>完整公开课，有作业与自动评测。适合需要外部节奏、希望有人给反馈的人 —— 这是纯读材料给不了的。</td><td>入门</td><td>低</td></tr>
    <tr><td>课程</td><td><b>CS50x（Harvard）</b></td><td>从 C 与内存讲起，把「变量是地址」讲得比多数 Python 入门课更透。做完它前几周的内容，本篇 §1.3 会从「记住了」变成「看见了」。</td><td>入门</td><td>中</td></tr>
    <tr><td>课程</td><td><b>MIT《The Missing Semester of Your CS Education》（6.NULL）</b></td><td>命令行、Git、调试器与环境配置。这是本篇 §6.3 的实践部分，也是后面每一章都要用到的工具链。课时很短，性价比极高。</td><td>入门即可看</td><td>低</td></tr>
    <tr><td>文档</td><td><b>Python 官方教程与语言参考 docs.python.org</b></td><td>唯一权威口径。遇到「为什么是这样」时以它为准，而不是以博客或本篇为准。注意区分「教程」与「参考」：前者讲用法，后者定语义。</td><td>全程</td><td>中</td></tr>
    <tr><td>文档</td><td><b>PEP 8《Style Guide for Python Code》</b></td><td>Python 社区对「写给人看」的成文答案。本篇 §6 的三条规则都能在它里面找到出处。</td><td>全程</td><td>低</td></tr>
    <tr><td>文档</td><td><b>PEP 20《The Zen of Python》</b></td><td>二十句设计哲学（在解释器里 <code>import this</code> 即可看到）。它是理解 Python 各种取舍的钥匙 —— 例如「显式优于隐式」解释了为什么 <code>explicit</code> 的参数风格被偏爱。</td><td>全程</td><td>低</td></tr>
  </tbody>
</table>

<div class="box note"><span class="t">关于本表的性质</span>
<p>表中的教材与课程都来自公开课程主页与社区长期共识，属于 <em class="ev">[实践]</em> 层面的推荐，不是「最优解」。
唯一带有强制性的两条是：<b>语言语义以官方文档为准</b>，<b>动手练习不能省</b> —— 前者保证你不会学到错的，后者保证你学到的是会用的。</p>
<p>本表没有列「Python 速查表」这类材料，因为本章的目标不是记住语法，而是建立模型。速查表在你已经开始写代码之后自然会有用，但那时你需要的是一份好的搜索引擎，而不是一份清单。</p>
</div>

<h2><span class="n">8</span>小结与自测</h2>
<p class="lede">这一章建立的五个模型，是后面七章共同的地基。</p>

<table>
  <thead><tr><th style="width:44px;">节</th><th style="width:220px;">应该带走的模型</th><th>它在后面哪里会被用到</th></tr></thead>
  <tbody>
    <tr><td>§1</td><td>程序是<b>无歧义的描述</b>；变量是名字，类型属于对象</td><td>第二章分析算法时，所有代价分析都建立在「对象与引用」的区分上。</td></tr>
    <tr><td>§2</td><td>控制流三种形态；<b>循环不变式</b>把「对」变成可论证的</td><td>第二、三章的算法与流水线论证用的是同一套方法。</td></tr>
    <tr><td>§3</td><td>函数的价值是<b>命名和隔离</b>；调用栈解释递归与作用域</td><td>第四章的线程栈、第六章的查询执行计划都会回到「帧」这个概念。</td></tr>
    <tr><td>§4</td><td>容器选择依据<b>访问模式</b>；list 与 set 的查找代价相差数量级</td><td>第二章会把这个直觉写成精确的复杂度结论。</td></tr>
    <tr><td>§5</td><td>错误分三类；traceback 从上读调用、从下读原因</td><td>第四、六章的并发与事务 bug 都属于「逻辑错误」，排查流程相同。</td></tr>
    <tr><td>§6</td><td>工程习惯的判据是<b>降低下一次改动的成本</b></td><td>全系列共用；第二章的复杂度分析、第三章的性能调优都要先有可读的代码。</td></tr>
  </tbody>
</table>

<h3>8.1 综合思考题</h3>

<p>下面五题综合了本章多个小节，且都<b>没有唯一答案</b>。判断自己是否答对的方法写在每题后面 —— 如果你能说清推理过程，答对与否不重要；如果只能给出结论，说明还有一节需要回看。</p>

<ol>
  <li><b>下面这段代码的注释是错的，请指出并解释注释里那句「不会被修改」为什么不成立。</b>
  <pre><code><span class="kw">def</span> add_item(items, item):
    result = items
    result.append(item)
    <span class="kw">return</span> result
<span class="cm"># add_item 返回一个新列表，原列表不会被修改</span></code></pre>
  <span class="small">判断线索：回到 §1.3，问「result 这个名字指向哪个对象」。</span></li>

  <li><b>一个函数要求输入一个「已排序的整数列表」，请写两三条断言把这件事写出来，并说明哪一条不该用 <code>assert</code> 写。</b>
  <span class="small">判断线索：§5.3 提到 <code>assert</code> 在 <code>-O</code> 下会被跳过 —— 那么校验外部输入该用什么？</span></li>

  <li><b>把 <code>total_size</code>（§3.4）改写成迭代版本之后，多出来的那个数据结构是什么？为什么递归版本不需要显式维护它？</b>
  <span class="small">判断线索：这个数据结构在递归版本里，其实就是「调用栈」本身。§3.3 那张图里的「帧」是什么？</span></li>

  <li><b>一个程序对 10 行数据正确、对 10 万行数据结果错误但不报错。写出你的排查顺序，并说明每一步期望得到什么信息。</b>
  <span class="small">判断线索：§5.1 告诉你是「逻辑错误」，§5.3 给了五步流程。注意「10 行对、10 万行错」本身提示了方向 —— 什么会随数据量变化？</span></li>

  <li><b>说明为什么「用 <code>if x is not None</code> 而不是 <code>if not x is None</code>」这个建议和性能无关。</b>
  <span class="small">判断线索：§1.5 的模型修正 3 给了 <code>is</code> 的正确用法，§1.6 给了三类标注。这条建议属于哪一类？</span></li>
</ol>

<div class="box takeaway"><span class="t">本章结论</span>
<p>编程基础的核心不是语法，而是<b>五个模型加一套习惯</b>：程序是无歧义的描述；变量是指向对象的名字；控制流只有三种形态，但顺序即语义；函数的价值在于命名与隔离；容器要按访问模式选。
习惯只有三条判据 —— 可检索的命名、解释为什么的注释、能回退的版本控制。</p>
<p>下一章会在这个地基上做第一件有「计算机科学味道」的事：<b>不再只说「这段代码能跑」，而是精确地说「它在什么规模下花多少代价」</b>。
你现在已经具备读懂它的全部前提。</p>
</div>

<footer>
  <p><strong>验证说明</strong> 本章代码片段均可在 Python 3.12+ 直接运行，输出与文中标注一致；涉及 CPython 实现细节的两处（小整数缓存、<code>is</code> 的字节码）已标明属于实现相关行为、不可依赖。</p>
  <p><strong>取材与出处</strong> 结构化程序定理引自 Böhm &amp; Jacopini (1966)；「程序即理论」引自 Peter Naur (1985)；语言语义以 Python 官方文档为准；教材与课程推荐见 §7，属社区共识而非唯一答案。</p>
  <p><strong>截至</strong> 2026-10。</p>
</footer>
