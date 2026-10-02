---
title: "TypeScript 入门：给 JavaScript 加一层类型，图什么"
summary: "面向只会一点 JavaScript 的初学者，说清 TypeScript 是什么、与 JavaScript 到底什么关系、类型系统在解决什么问题、常用语法看一眼就懂、以及在哪些场景里值得上手。以「初识和了解」为度，点到为止。"
date: 2026-10-02
category: Languages and practice
tags: [TypeScript, JavaScript, 类型系统, 学习路径]
lang: zh
---

<div class="meta-row">
    <span><b>读者</b> &nbsp;会写一点 JavaScript、听过 TypeScript 但没系统看过的人</span>
    <span><b>目标</b> &nbsp;建立整体认知，能判断「这个场景要不要用 TS」</span>
    <span><b>版本基准</b> &nbsp;TypeScript 7.0（2026-07 正式版，Go 重写编译器）；Node 24.12+ 原生类型擦除</span>
    <span><b>更新状态</b> &nbsp;原文写作较早，本文按 2026-10 现状校对，变化处标 <span class="pill cav">已更新</span></span>
</div>

<div class="box note" style="margin-top:26px;">
  <span class="t">阅读约定</span>
  <div class="small">
  <p><b>三类说法分开标注。</b>写「<b>规范</b>」的，指 TypeScript 官方文档或 ECMAScript 标准已明确规定、可查原文；写「<b>现状</b>」的，指 2026-10 时点的工具生态事实（版本、支持范围）——这类会随时间变化；写「<b>经验</b>」的，是工程界的取舍，可以被合理反对，不是必须遵守的规矩。</p>
  <p><b>这篇讲到哪为止。</b>只到「知道 TS 是什么、能读懂一段 TS、能判断要不要用」为止。不涉及泛型进阶写法（条件类型、映射类型、模板字面量类型）、不涉及装饰器与元编程、不讲构建工具选型细节。这些留给你之后按需深入。</p>
  <p><b>代码示例。</b>全部可在 <code>tsc</code> 或 TypeScript Playground 里直接跑。文中出现的版本号与速度数字来自官方博客与公开的第三方基准，已标注来源性质。</p>
  </div>
</div>

<!-- ============================================================ -->
<h2><span class="n">1</span>一句话说清：TypeScript 是「带类型标注的 JavaScript」</h2>
<p class="lede">先把最容易搞混的一件事定下来：TS 不是一门新语言，它是 JS 的超集。</p>

<p>你在 <code>.ts</code> 文件里写的所有内容，只要去掉那些类型标注，剩下的就是一份合法的 JavaScript。
反过来不成立 —— 有些 JavaScript 写法不能直接放进 TS。所以更准确的说法是：
<b>TypeScript = JavaScript 的全部语法 + 一层可选的类型标注 + 一个在编码阶段检查这些标注的工具</b>。</p>

<div class="box">
  <span class="t">一个能立刻检验的理解</span>
  <p>把下面两段并排看。左边是 TS，右边是把类型删干净之后的 JS。你会发现：<b>删掉类型，程序的行为一点没变</b>。
  这不是巧合，而是 TypeScript 的根本设计 —— 类型只服务于「写代码和查错」这两个阶段，到了真正运行的时候，它们不存在。</p>
</div>

<pre><code><span class="cm">// 左边：TypeScript（.ts）</span>
<span class="kw">function</span> add(a<span class="mk">:</span> number, b<span class="mk">:</span> number)<span class="mk">:</span> number {
  <span class="kw">return</span> a + b;
}

<span class="cm">// 右边：编译/擦除之后运行的就是这个（.js）</span>
<span class="kw">function</span> add(a, b) {
  <span class="kw">return</span> a + b;
}</code></pre>

<h3>1.1 类型到底「活」在哪一步</h3>

<p>这是初学者最该建立的心智模型。TypeScript 的类型<b>只在开发阶段存在</b>：</p>

<figure>
<svg viewBox="0 0 680 168" role="img" aria-label="TypeScript 类型在编译阶段存在，运行时已消失的时间轴">
  <g font-family="-apple-system,BlinkMacSystemFont,'Segoe UI','PingFang SC','Microsoft YaHei',Helvetica,Arial,sans-serif">
    <line x1="30" y1="92" x2="650" y2="92" stroke="#dfe5ea" stroke-width="1.5"/>
    <rect x="30" y="60" width="180" height="64" rx="4" fill="#eef3f8" stroke="#1b4f8a" stroke-width="1.5"/>
    <text x="120" y="82" font-size="12.5" font-weight="700" fill="#1b4f8a" text-anchor="middle">你写代码时</text>
    <text x="120" y="102" font-size="11" fill="#5b6570" text-anchor="middle">编辑器实时标红 · 有类型</text>
    <rect x="240" y="60" width="180" height="64" rx="4" fill="#eef3f8" stroke="#1b4f8a" stroke-width="1.5"/>
    <text x="330" y="82" font-size="12.5" font-weight="700" fill="#1b4f8a" text-anchor="middle">构建 / 类型检查</text>
    <text x="330" y="102" font-size="11" fill="#5b6570" text-anchor="middle">tsc --noEmit · 出错就拦</text>
    <rect x="450" y="60" width="200" height="64" rx="4" fill="#f0f7f4" stroke="#0f7b5f" stroke-width="1.5"/>
    <text x="550" y="82" font-size="12.5" font-weight="700" fill="#0f7b5f" text-anchor="middle">浏览器 / Node 运行</text>
    <text x="550" y="102" font-size="11" fill="#5b6570" text-anchor="middle">类型已被擦除 · 只剩 JS</text>
    <circle cx="30" cy="92" r="4" fill="#1b4f8a"/>
    <circle cx="420" cy="92" r="4" fill="#1b4f8a"/>
    <circle cx="650" cy="92" r="4" fill="#0f7b5f"/>
    <text x="30" y="142" font-size="10.5" fill="#8b949e">类型在这里有意义 ────────────────┤ 类型在这里已经不存在</text>
    <text x="30" y="160" font-size="10.5" fill="#8b949e">「运行时没有类型」解释了两件事：为什么加类型不影响运行速度；为什么类型挡不住的数据错误，运行时照样出错。</text>
  </g>
</svg>
<figcaption><b>图 1 |</b> 类型存在的边界。这个边界是理解后面所有讨论的前提：TS 帮你<b>在写的时候</b>发现「类型对不上」的错，但它不帮你在运行时拦住任何东西。</figcaption>
</figure>

<div class="box finding"><span class="t">最常见的误解 —— 「用了 TS 就不会在运行时出错」</span><p>不是的。类型只在检查阶段生效。如果你从网络接口收到一个本该是数字、实际是字符串的值，而这个值的类型被你<b>手工声明</b>成了 <code>number</code>，TypeScript 会完全相信你，运行时该出错还是出错。类型系统检查的是<b>你自己写的代码内部是否自洽</b>，不是外部世界是否守信用。</p></div>

<h3>1.2 那它和 JavaScript 到底是什么关系</h3>

<table>
  <thead><tr><th style="width:150px;">关系维度</th><th>具体说法</th></tr></thead>
  <tbody>
    <tr><td><b>语法</b></td><td>超集。合法 JS 几乎都是合法 TS；TS 额外提供类型标注、接口、枚举等语法糖。</td></tr>
    <tr><td><b>运行</b></td><td>无独立运行时。TS 代码最终仍是以 JS 的形式被浏览器或 Node.js 执行。</td></tr>
    <tr><td><b>谁维护</b></td><td>微软主导，开源。与 JavaScript 的 ECMAScript 标准是两个体系 —— TS 跟标准走，但会先一步提供还在提案阶段的新特性。</td></tr>
    <tr><td><b>能不能只用 TS</b></td><td>能。但也随时可以退回纯 JS，或在同一个项目里混用（<code>.js</code> 与 <code>.ts</code> 并存）。</td></tr>
  </tbody>
</table>

<div class="box takeaway"><span class="t">本章结论</span><p>TypeScript 是<b>给 JavaScript 加的一层开发期护栏</b>，不是一门替代品。它不改变程序跑起来的样子，只改变你写程序时能不能更早发现错误。</p></div>


<!-- ============================================================ -->
<h2><span class="n">2</span>为什么需要它：三种真实存在的痛</h2>
<p class="lede">如果 JavaScript 已经够用，为什么还要多写类型？因为 JS 的灵活，恰恰在大项目里变成负担。</p>

<h3>2.1 三种痛，各自对应一个解法</h3>

<table>
  <thead><tr><th style="width:118px;">痛点</th><th style="width:250px;">纯 JavaScript 里的表现</th><th>TypeScript 怎么缓解</th></tr></thead>
  <tbody>
    <tr>
      <td><b>拼写与结构</b></td>
      <td>把 <code>user.name</code> 写成 <code>user.nmae</code>，不报错，运行时得到 <code>undefined</code>，等页面显示「undefined」你才发现。</td>
      <td>编辑器当场标红：<i>属性 'nmae' 不存在</i>。错误从运行时提前到了敲键盘那一刻。</td>
    </tr>
    <tr>
      <td><b>函数契约</b></td>
      <td>某函数期望收到数字，有人传了字符串。JS 不会拦，函数内部算出一个莫名其妙的结果往上传。</td>
      <td>调用处直接报错：<i>类型 'string' 不能赋给 'number'</i>。契约写在函数签名上，调用方看得见。</td>
    </tr>
    <tr>
      <td><b>重构与协作</b></td>
      <td>改一个字段名，要全项目搜字符串找引用；漏改一处就埋雷。多人协作时，不知道别人写的函数该传什么。</td>
      <td>重命名能一键联动；类型签名本身就是<b>可执行的文档</b>，比注释更不容易过期。</td>
    </tr>
  </tbody>
</table>

<div class="box"><span class="t">一句话概括收益</span><p>TypeScript 把「你会在几小时后、或上线后才发现的错误」，提前到你打字的那一秒。省下的不是编译时间，是<b>调试和返工的时间</b>。</p></div>

<h3>2.2 代价是什么</h3>

<p>没有任何东西是白来的。上 TS 意味着你要接受这几件事：</p>

<ul>
  <li><b>多写一些字。</b>函数参数、返回值、对象结构都要标注。写得多，但改的时候省得多。</li>
  <li><b>多一步构建。</b>浏览器不认识 <code>.ts</code>，得先转成 <code>.js</code>。不过这一步现在越来越轻（见 §6.2）。</li>
  <li><b>类型报错要处理。</b>刚开始会撞上一堆红波浪线，有些是真 bug，有些只是类型没写对。这段时间是必然的成本。</li>
</ul>

<div class="box takeaway"><span class="t">本章结论</span><p>值不值得，取决于<b>代码规模与生命周期</b>。几十行的脚本，TS 是负担；几千行、要多个人改好几年的项目，TS 是划算的。判断标准在 §5。</p></div>


<!-- ============================================================ -->
<h2><span class="n">3</span>类型系统：够用就好的那部分</h2>
<p class="lede">TS 的类型系统很庞大，但日常写代码真正高频用到的，其实是一个不大的子集。</p>

<h3>3.1 基础类型：一眼就懂</h3>

<pre><code><span class="kw">let</span> title<span class="mk">:</span> string = <span class="mk">"hello"</span>;      <span class="cm">// 字符串</span>
<span class="kw">let</span> count<span class="mk">:</span> number = <span class="mk">42</span>;          <span class="cm">// 数字（不区分整数小数）</span>
<span class="kw">let</span> done<span class="mk">:</span> boolean = <span class="mk">true</span>;        <span class="cm">// 布尔</span>
<span class="kw">let</span> ids<span class="mk">:</span> number[] = [<span class="mk">1</span>, <span class="mk">2</span>, <span class="mk">3</span>];     <span class="cm">// 数字数组，也可写 Array&lt;number&gt;</span>
<span class="kw">let</span> maybe<span class="mk">:</span> string | <span class="mk">null</span> = <span class="mk">null</span>; <span class="cm">// 联合类型：字符串或空</span></code></pre>

<p>有几处值得单独点出来，因为它们常在初学阶段造成困惑：</p>

<table>
  <thead><tr><th style="width:150px;">写法</th><th style="width:200px;">含义</th><th>什么时候用</th></tr></thead>
  <tbody>
    <tr><td><code>any</code></td><td>关掉这个值的类型检查</td><td><b>尽量别用</b>。它等于把 TS 退化成 JS，还会「传染」给用到它的地方。</td></tr>
    <tr><td><code>unknown</code></td><td>「我还不知道，但用之前必须收窄」</td><td>接外部数据（API 返回、用户输入）时的正确姿势，比 <code>any</code> 安全。</td></tr>
    <tr><td><code>void</code></td><td>函数没有返回值</td><td>写在一类「只做副作用」的函数返回值位置。</td></tr>
    <tr><td><code>never</code></td><td>永远不会出现的值</td><td>穷尽判断、抛出异常的函数。初学可以晚点再看。</td></tr>
    <tr><td><code>string | null</code></td><td>可能是字符串，也可能是空</td><td>处理「可能查不到」的数据。联合类型是 TS 最常用的类型之一。</td></tr>
  </tbody>
</table>

<h3>3.2 类型推断：大部分时候你不用写</h3>

<p>一个常见的误会是以为 TS 要求你到处标类型。其实不 —— <b>只要它自己能推出来，就不用你写</b>：</p>

<pre><code><span class="kw">const</span> n = <span class="mk">10</span>;          <span class="cm">// 自动推断为 number</span>
<span class="kw">const</span> s = <span class="mk">「hi」</span>;        <span class="cm">// 自动推断为 string</span>
<span class="kw">const</span> list = [<span class="mk">1</span>, <span class="mk">2</span>];   <span class="cm">// 自动推断为 number[]</span>

<span class="cm">// 推断 vs 显式：只在「边界」上需要你手写</span>
<span class="cm">// 函数的参数 —— 推断不出来，必须标注</span>
<span class="kw">function</span> greet(name<span class="mk">:</span> string) { <span class="kw">return</span> <span class="mk">「Hi 」</span> + name; }
<span class="cm">// 函数返回值 —— 通常能让它自己推，不用写</span></code></pre>

<div class="box note"><span class="t">实践建议</span><p>给<b>函数参数</b>和<b>跨模块暴露的数据结构</b>写类型，其余交给推断。这样做的好处是代码噪音最小，而真正需要「契约」的地方一个不落。这是社区较普遍的取舍，不是硬规范。</p></div>

<h3>3.3 对象与接口：描述数据长什么样</h3>

<p>这是 TS 最有价值的部分，因为前端、后端代码里 90% 的时间都在处理对象。</p>

<pre><code><span class="cm">// interface：给对象结构起个名字（推荐用于描述对象）</span>
<span class="kw">interface</span> User {
  id<span class="mk">:</span> number;
  name<span class="mk">:</span> string;
  email<span class="mk">?:</span> string;      <span class="cm">// 问号 = 这个字段可有可无</span>
  <span class="kw">readonly</span> createdAt<span class="mk">:</span> string; <span class="cm">// 只读，赋值后不能改</span>
}

<span class="cm">// 用起来：任何「长得不像 User」的值都会被拦下</span>
<span class="kw">const</span> u<span class="mk">:</span> User = { id<span class="mk">:</span> <span class="mk">1</span>, name<span class="mk">:</span> <span class="mk">「Jinbei」</span>, createdAt<span class="mk">:</span> <span class="mk">「2026-10-02」</span> };
<span class="cm">// u.name = 123;        // 报错：number 不能赋给 string</span>
<span class="cm">// u.email = 「x@y.z」;   // 可选字段，补上没问题</span></code></pre>

<p><code>type</code> 和 <code>interface</code> 都能给类型起名，初学不必纠结：<b>描述对象用 <code>interface</code>，描述联合、元组、函数签名用 <code>type</code></b>。两者在多数场景下可以互换。</p>

<h3>3.4 收窄：TS 最聪明的部分</h3>

<p>当你写 <code>string | null</code> 这种联合类型，TS 不会让你直接对它调用字符串方法。但只要你<b>先判断</b>，它就自动算出当前分支里这个值是什么类型：</p>

<pre><code><span class="kw">function</span> upper(text<span class="mk">:</span> string | <span class="mk">null</span>) {
  <span class="cm">// text 此刻是 string | null，不能直接 .toUpperCase()</span>
  <span class="kw">if</span> (text === <span class="mk">null</span>) <span class="kw">return</span> <span class="mk">「」</span>;
  <span class="cm">// 到这里 TS 已经知道 text 一定是 string 了 —— 可以放心调用</span>
  <span class="kw">return</span> text.toUpperCase();
}</code></pre>

<p>这个能力叫<b>类型收窄（narrowing）</b>。它让 TS 能配合你平时就在写的 <code>if</code> / <code>typeof</code> / <code>in</code> 判断，
而不需要你额外声明。这也是很多人第一次用 TS 时会「哦」一下的地方。</p>

<div class="box takeaway"><span class="t">本章结论</span><p>日常 80% 的场景，掌握这四样就够：<b>基础类型 + 类型推断 + interface 描述对象 + 联合类型与收窄</b>。剩下的（泛型进阶、条件类型等）都是在这四样之上的延伸，遇到再学。</p></div>


<!-- ============================================================ -->
<h2><span class="n">4</span>常用语法特性：挑出真正常用的</h2>
<p class="lede">TS 的语法特性有不少，但把「天天用」和「偶尔用」分开之后，清单会短很多。</p>

<h3>4.1 泛型：让类型也能「传参」</h3>

<p>泛型的动机很朴素：同一段逻辑，要能处理不同<b>类型</b>的数据。看对比例子就懂了。</p>

<pre><code><span class="cm">// 不用泛型：要么写死一种类型，要么用 any 放弃检查</span>
<span class="kw">function</span> firstAny(arr<span class="mk">:</span> <span class="kw">any</span>[])<span class="mk">:</span> <span class="kw">any</span> { <span class="kw">return</span> arr[<span class="mk">0</span>]; }

<span class="cm">// 用泛型：T 是一个「类型参数」，由调用时自动推出来</span>
<span class="kw">function</span> first&lt;T&gt;(arr<span class="mk">:</span> T[])<span class="mk">:</span> T { <span class="kw">return</span> arr[<span class="mk">0</span>]; }

<span class="kw">const</span> a = first([<span class="mk">1</span>, <span class="mk">2</span>, <span class="mk">3</span>]);        <span class="cm">// a 被推为 number</span>
<span class="kw">const</span> b = first([<span class="mk">「x」</span>, <span class="mk">「y」</span>]);      <span class="cm">// b 被推为 string</span></code></pre>

<p>你不必现在就写复杂的泛型，但<b>要能读懂 <code>&lt;T&gt;</code></b> —— 它是「这里先留个类型位，用的时候再填」。
刚上手时，泛型主要出现在第三方库的文档和类型提示里。</p>

<h3>4.2 联合与字面量类型：把「只能是这几个值」写清楚</h3>

<pre><code><span class="cm">// 字面量类型：不是 "string"，而是"这几个具体的字符串"</span>
<span class="kw">type</span> Status = <span class="mk">「draft」</span> | <span class="mk">「published」</span> | <span class="mk">「archived」</span>;

<span class="kw">function</span> publish(s<span class="mk">:</span> Status) { <span class="cm">/* ... */</span> }
publish(<span class="mk">「draft」</span>);      <span class="cm">// 合法</span>
<span class="cm">// publish(「finish」);  // 报错：不在允许的取值范围内</span></code></pre>

<p>这个特性在实践里非常值钱：它把「只能传这几个值」这种口头约定，变成了工具能检查的规则。任何带状态、带枚举语义的字段都适合这么写。</p>

<h3>4.3 函数与可选参数</h3>

<pre><code><span class="cm">// 参数可选（?）与默认值</span>
<span class="kw">function</span> buildUrl(path<span class="mk">:</span> string, host<span class="mk">?:</span> string) {
  <span class="kw">return</span> (host ?? <span class="mk">「https://example.com」</span>) + path;
}
buildUrl(<span class="mk">「/notes」</span>);                    <span class="cm">// 第二个参数可省</span>
buildUrl(<span class="mk">「/notes」</span>, <span class="mk">「https://a.com」</span>);      <span class="cm">// 也可以传</span>

<span class="cm">// 箭头函数同样可以标类型</span>
<span class="kw">const</span> double = (x<span class="mk">:</span> number)<span class="mk">:</span> number <span class="kw">=&gt;</span> x * <span class="mk">2</span>;</code></pre>

<h3>4.4 只读与不可变</h3>

<pre><code><span class="kw">const</span> nums<span class="mk">:</span> <span class="kw">readonly</span> number[] = [<span class="mk">1</span>, <span class="mk">2</span>, <span class="mk">3</span>];
<span class="cm">// nums.push(4);   // 报错：只读数组不能改</span>

<span class="cm">// as const：把对象的所有字段都锁成字面量、都只读</span>
<span class="kw">const</span> CONFIG = { theme<span class="mk">:</span> <span class="mk">「light」</span>, retries<span class="mk">:</span> <span class="mk">3</span> } <span class="kw">as const</span>;</code></pre>

<div class="box takeaway"><span class="t">本章结论</span><p>四样里，<b>联合与字面量类型</b>最快见效，<b>泛型</b>最需要时间消化。建议先熟练前三样，泛型留着「读懂即可、暂不手写」。</p></div>


<!-- ============================================================ -->
<h2><span class="n">5</span>典型使用场景：什么时候真的该上 TS</h2>
<p class="lede">不是所有项目都值得上 TS。把它用在收益最大的地方，而不是「因为流行所以用」。</p>

<table>
  <thead><tr><th style="width:170px;">场景</th><th style="width:130px;">适配度</th><th>理由</th></tr></thead>
  <tbody>
    <tr>
      <td><b>多人协作的中大型前端</b></td>
      <td><span class="pill ok">强烈推荐</span></td>
      <td>类型签名就是接口文档，改一处编辑器能找出所有受影响的地方。项目越大、人越多，收益越明显。</td>
    </tr>
    <tr>
      <td><b>Node.js 后端服务</b></td>
      <td><span class="pill ok">强烈推荐</span></td>
      <td>接口入参出参、数据库模型都有明确结构，类型能挡住大量「字段名写错、类型传错」的低级错误。</td>
    </tr>
    <tr>
      <td><b>要长期维护的工具库</b></td>
      <td><span class="pill ok">推荐</span></td>
      <td>给别人用的库，类型提示直接改善使用体验。现在流行的库几乎都自带类型声明。</td>
    </tr>
    <tr>
      <td><b>一次性的小脚本</b></td>
      <td><span class="pill bad">不必</span></td>
      <td>跑完就扔的脚本，写类型的时间大于它省下的时间。</td>
    </tr>
    <tr>
      <td><b>只有自己看的原型</b></td>
      <td><span class="pill cav">视情况</span></td>
      <td>如果你清楚它会后长成大项目，一开始就上 TS 比中途迁移便宜；否则先用 JS 跑通更快。</td>
    </tr>
  </tbody>
</table>

<div class="box finding"><span class="t">反直觉的一点 —— 中途迁到 TS 比一开始就上贵得多</span><p>给一个已经写了几千行 JS 的项目补类型，比在空项目里从第一天就用 TS 麻烦得多。所以真正的判断不是「现在要不要」，而是「<b>这个东西三年后还在不在</b>」。在，就尽早。</p></div>

<h3>5.1 顺带说清楚两个近年的变化</h3>

<p>原文写作时，「用 TS 一定要配一套构建工具」是常识。到 2026 年，这两件事都变了。</p>

<table>
  <thead><tr><th style="width:170px;">变化</th><th style="width:130px;">状态</th><th>说明</th></tr></thead>
  <tbody>
    <tr>
      <td><b>编译器换成 Go 重写</b></td>
      <td><span class="pill cav">已更新</span></td>
      <td>TypeScript 7.0（2026-07 正式版）把编译器从 TypeScript 自举改为 Go 实现，类型检查速度官方与公开基准约快 <b>8–12 倍</b>（如 VS Code 全量检查 125.7s → 10.6s）。语言本身、写法、报错语义保持不变，只是更快。</td>
    </tr>
    <tr>
      <td><b>不必先编译再运行</b></td>
      <td><span class="pill cav">已更新</span></td>
      <td>Node.js 自 22.18 / 23.6 起默认支持直接运行 <code>.ts</code>，24.12 起标记为稳定。原理是<b>类型擦除</b>（把类型换成空格），不改变代码行为。<code>node script.ts</code> 直接就能跑。</td>
    </tr>
  </tbody>
</table>

<div class="box note"><span class="t">擦除模式的边界（重要）</span><p>「Node 能跑 TS」靠的是<b>只删不编译</b>，所以凡是「会生成运行时代码」的 TS 语法，Node 一概不支持：
<b>enum</b>、带运行时代码的 <b>namespace</b>、构造函数里的<b>参数属性</b>（<code>constructor(private x: number)</code>）、<b>装饰器</b>。
遇到这些要么改用普通写法（enum 换成 <code>as const</code> 对象），要么仍走编译器 / 打包器。另外，<b>擦除不等于类型检查</b> —— 跑得动不代表类型没错，CI 里仍应保留 <code>tsc --noEmit</code>。</p></div>

<div class="box takeaway"><span class="t">本章结论</span><p>判断标准就三条：<b>会不会变大、会不会多人改、会不会长期在</b>。三个里中两个，就上 TS。另外记住：2026 年上 TS 的成本比几年前低了不少，「要编译」不再是拒绝它的理由。</p></div>


<!-- ============================================================ -->
<h2><span class="n">6</span>怎么开始：一条最小路径</h2>
<p class="lede">不求全，只求能跑起来看见效果。走通这条路径，你就有了判断力。</p>

<h3>6.1 五步上手</h3>

<pre><code><span class="cm"># 1) 装编译器（项目里作为开发依赖，不要全局装）</span>
npm install -D typescript

<span class="cm"># 2) 生成配置（会问几个问题，不懂就按回车）</span>
npx tsc --init

<span class="cm"># 3) 写一个 .ts 文件，然后只做类型检查、不输出文件</span>
npx tsc --noEmit

<span class="cm"># 4) 如果只是想在 Node 里跑跑看（24.12+）</span>
node your-file.ts

<span class="cm"># 5) 想看类型报错长什么样，直接去 TypeScript Playground</span>
<span class="cm">#    https://www.typescriptlang.org/play</span></code></pre>

<p>第 2 步生成的 <code>tsconfig.json</code> 里，初学阶段只要先认这几项：</p>

<table>
  <thead><tr><th style="width:190px;">配置项</th><th>作用</th></tr></thead>
  <tbody>
    <tr><td><code>"strict": true</code></td><td>打开严格检查。<b>建议保持开启</b>，新项目务必开；TypeScript 7.0 起这已是默认值。</td></tr>
    <tr><td><code>"noEmit": true</code></td><td>只检查、不出文件。配合打包器或 Node 擦除模式时用这个。</td></tr>
    <tr><td><code>"target"</code></td><td>编译产出什么年代的 JS。现代项目用较新的值即可。</td></tr>
    <tr><td><code>"lib"</code></td><td>声明可以用哪些内置 API。注意 7.0 已移除 ES5 支持。</td></tr>
  </tbody>
</table>

<h3>6.2 两种运行方式，怎么选</h3>

<table>
  <thead><tr><th style="width:150px;">方式</th><th style="width:210px;">适合</th><th>注意</th></tr></thead>
  <tbody>
    <tr>
      <td><b>直接跑 <code>.ts</code></b></td>
      <td>学习阶段、Node 小工具、后端服务</td>
      <td>零构建步骤，启动快。但只支持可擦除语法，且不做类型检查。</td>
    </tr>
    <tr>
      <td><b>打包器 / 编译器</b></td>
      <td>任何要上浏览器的项目、用框架的项目</td>
      <td>浏览器不认识 <code>.ts</code>，必须有一步转换。现代工具（如 Vite）已内置，通常无感。</td>
    </tr>
  </tbody>
</table>

<div class="box note"><span class="t">给「学 TS 只为看懂别人的代码」的人</span><p>那连环境都不用装。<b>TypeScript Playground</b> 直接在网页里写、实时看到类型报错，还有官方手册示例可改。
想验证「某个写法是否合法」，打开它比搭环境快十倍。</p></div>

<div class="box takeaway"><span class="t">本章结论</span><p>上手 TS 的最小成本是<b>一条 <code>npm install -D typescript</code></b>，或者干脆零成本用 Playground。真正花时间的不是装环境，而是习惯「先想类型、再写逻辑」这个顺序。</p></div>


<!-- ============================================================ -->
<h2><span class="n">7</span>回头看：这篇讲清了什么</h2>
<p class="lede">用一张图把全文收起来，方便你之后回看。</p>

<figure>
<svg viewBox="0 0 680 250" role="img" aria-label="TypeScript 认知地图：是什么、为什么、学什么、用在哪">
  <g font-family="-apple-system,BlinkMacSystemFont,'Segoe UI','PingFang SC','Microsoft YaHei',Helvetica,Arial,sans-serif">
    <rect x="240" y="16" width="200" height="42" rx="4" fill="#eef3f8" stroke="#1b4f8a" stroke-width="1.5"/>
    <text x="340" y="42" font-size="13" font-weight="700" fill="#1b4f8a" text-anchor="middle">TypeScript</text>
    <line x1="340" y1="58" x2="340" y2="76" stroke="#c9d2dc" stroke-width="1.5"/>
    <line x1="96" y1="76" x2="584" y2="76" stroke="#c9d2dc" stroke-width="1.5"/>
    <line x1="96" y1="76" x2="96" y2="92" stroke="#c9d2dc" stroke-width="1.5"/>
    <line x1="259" y1="76" x2="259" y2="92" stroke="#c9d2dc" stroke-width="1.5"/>
    <line x1="421" y1="76" x2="421" y2="92" stroke="#c9d2dc" stroke-width="1.5"/>
    <line x1="584" y1="76" x2="584" y2="92" stroke="#c9d2dc" stroke-width="1.5"/>
    <rect x="24" y="92" width="144" height="120" rx="4" fill="#f7f8f9" stroke="#dfe5ea"/>
    <rect x="24" y="92" width="3" height="120" fill="#1b4f8a"/>
    <text x="38" y="112" font-size="11.5" font-weight="700" fill="#17181a">§1 是什么</text>
    <text x="38" y="132" font-size="10.5" fill="#5b6570">带类型的 JS 超集</text>
    <text x="38" y="150" font-size="10.5" fill="#5b6570">类型只在开发期存在</text>
    <text x="38" y="168" font-size="10.5" fill="#5b6570">运行时就是普通 JS</text>
    <rect x="187" y="92" width="144" height="120" rx="4" fill="#f7f8f9" stroke="#dfe5ea"/>
    <rect x="187" y="92" width="3" height="120" fill="#1b4f8a"/>
    <text x="201" y="112" font-size="11.5" font-weight="700" fill="#17181a">§2 为什么</text>
    <text x="201" y="132" font-size="10.5" fill="#5b6570">拼写 / 契约 / 重构</text>
    <text x="201" y="150" font-size="10.5" fill="#5b6570">错误提前到打字时</text>
    <text x="201" y="168" font-size="10.5" fill="#5b6570">代价：多写字多构建</text>
    <rect x="349" y="92" width="144" height="120" rx="4" fill="#f0f7f4" stroke="#0f7b5f" stroke-width="1.2"/>
    <rect x="349" y="92" width="3" height="120" fill="#0f7b5f"/>
    <text x="363" y="112" font-size="11.5" font-weight="700" fill="#0f7b5f">§3–4 学什么</text>
    <text x="363" y="132" font-size="10.5" fill="#5b6570">基础类型 + 推断</text>
    <text x="363" y="150" font-size="10.5" fill="#5b6570">interface 描述对象</text>
    <text x="363" y="168" font-size="10.5" fill="#5b6570">联合类型 + 收窄</text>
    <text x="363" y="186" font-size="10.5" fill="#5b6570">泛型：先读懂即可</text>
    <rect x="512" y="92" width="144" height="120" rx="4" fill="#f7f8f9" stroke="#dfe5ea"/>
    <rect x="512" y="92" width="3" height="120" fill="#1b4f8a"/>
    <text x="526" y="112" font-size="11.5" font-weight="700" fill="#17181a">§5–6 用在哪</text>
    <text x="526" y="132" font-size="10.5" fill="#5b6570">多人前端 / Node 后端</text>
    <text x="526" y="150" font-size="10.5" fill="#5b6570">长期工具库</text>
    <text x="526" y="168" font-size="10.5" fill="#5b6570">小脚本：不必上</text>
    <text x="24" y="236" font-size="10.5" fill="#8b949e">绿框 = 本篇花笔墨最多的地方（真正高频的部分）；蓝框 = 需要知道但不必现在就精的部分。</text>
  </g>
</svg>
<figcaption><b>图 2 |</b> 全文的认知地图。绿色那格是「值得先花时间」的核心；其余三格是「知道有这回事」即可。之后要深入，从绿区往细处走。</figcaption>
</figure>

<h3>7.1 之后可以往哪深入</h3>

<table>
  <thead><tr><th style="width:240px;">方向</th><th>什么时候该看</th></tr></thead>
  <tbody>
    <tr><td><b>泛型进阶</b>（约束、条件类型、映射类型）</td><td>开始写自己的工具类型、或读不懂某个库的声明文件时。</td></tr>
    <tr><td><b>类型声明文件 <code>.d.ts</code></b></td><td>要给一个没有类型的 JS 库补类型，或发布自己的包时。</td></tr>
    <tr><td><b>官方 Handbook 的 Everyday Types 一节</b></td><td>想要一份系统、权威的日常类型清单，随时可查。</td></tr>
    <tr><td><b>TS 与框架的配合</b></td><td>用 React / Vue / Astro 时，各框架有自己的类型约定，届时按框架文档学更快。</td></tr>
  </tbody>
</table>

<h3>7.2 如果只记一件事</h3>

<div class="box takeaway"><span class="t">本章结论</span><p><b>TypeScript 是在 JavaScript 上加一层开发期护栏。</b>它不变程序怎么跑，只让你更早发现错误。它的核心价值在「多人、长期、会变大」的项目里 —— 判断要不要用，就问自己：这东西三年后还在不在。</p></div>

<footer>
  <p><strong>事实来源</strong> 语言与类型系统部分依据 TypeScript 官方文档（Handbook / Release Notes）；版本与性能数字来自 TypeScript 官方 7.0 发布公告及公开的第三方基准（VS Code、Sentry 等仓库）；Node.js 类型擦除依据 Node.js 官方 Learn 文档与 TypeScript 5.8 起引入的 <code>--erasableSyntaxOnly</code> 说明。生态支持范围（ESLint / Volar 等）以 2026-10 时点为准，会随版本变化。</p>
  <p><strong>时效提醒</strong> 标注「现状」的内容（版本号、工具支持范围）具有保质期；语言本身的结论（类型只存在于开发期、擦除不等于检查）来自设计而非版本，长期有效。</p>
</footer>
