---
kind: chapter
order: 7
title: "编译原理：把人的意图翻译成机器指令"
part: "第三部 · 系统侧纵深"
prereq: "第一、二、三章"
reading: "—"
date: 2026-10-03
ready: false
tags: [计算机科学, 自学路线, 教材式笔记]
lang: zh
---

<div class="box finding"><span class="t">本章尚未动笔</span>
<p>这一章的位置已经在系列里定下来了：它是<b>第三部 · 系统侧纵深</b>的第 7 章，前置是<b>第一、二、三章</b>。下面把规划好的骨架先摆出来，方便你判断这一章是否是你现在需要的。正文会在写完后替换掉这一页。</p></div>

<div class="box note"><span class="t">读这一章之前</span>
<p>需要：递归与树、基本的汇编阅读能力。</p></div>

<h2><span class="n">1</span>这一章会讲什么</h2>
<p class="lede">从源码到可执行文件的完整流水线。</p>

<table>
  <thead><tr><th style="width:52px;">节</th><th style="width:250px;">标题</th><th>要解决的问题</th></tr></thead>
  <tbody>
    <tr><td class="num">§1</td><td><b>编译器在做什么</b></td><td>从源码到可执行文件的完整流水线。</td></tr>
    <tr><td class="num">§2</td><td><b>词法与语法分析</b></td><td>正则表达式、自动机与上下文无关文法。</td></tr>
    <tr><td class="num">§3</td><td><b>语义分析与类型检查</b></td><td>符号表、作用域与类型推导。</td></tr>
    <tr><td class="num">§4</td><td><b>中间表示与优化</b></td><td>SSA、常量传播、死代码消除。</td></tr>
    <tr><td class="num">§5</td><td><b>目标代码生成与寄存器分配</b></td><td>图着色分配与指令选择。</td></tr>
    <tr><td class="num">§6</td><td><b>动手写一个小语言</b></td><td>从词法分析器到可运行的解释器。</td></tr>
  </tbody>
</table>

<h2><span class="n">2</span>这一章会用到哪些材料</h2>
<p class="lede">推荐理由、适用阶段与难度都写在表里 —— 换一门替代课完全可能更适合你，判断标准永远是你自己的进度。</p>

<table>
  <thead><tr><th style="width:86px;">类型</th><th style="width:250px;">材料</th><th>推荐理由</th><th style="width:96px;">适用阶段</th><th style="width:56px;">难度</th></tr></thead>
  <tbody>
    <tr><td>教材</td><td><b>《Compilers: Principles, Techniques, and Tools》（龙书）</b></td><td>经典参考，覆盖全面但叙述偏重</td><td>进阶</td><td>高</td></tr>
    <tr><td>教材</td><td><b>《Engineering a Compiler》（Cooper & Torczon）</b></td><td>比龙书更现代、更适合自学</td><td>进阶</td><td>中</td></tr>
    <tr><td>教材</td><td><b>《Crafting Interpreters》（Robert Nystrom）</b></td><td>免费在线，边读边写就能造出两种解释器</td><td>入门～进阶</td><td>低</td></tr>
    <tr><td>教材</td><td><b>《Writing a C Compiler》（Nora Sandler）</b></td><td>从零写一个能编译真实 C 子集的编译器</td><td>进阶</td><td>中</td></tr>
    <tr><td>课程</td><td><b>Stanford《CS 143 Compilers》</b></td><td>体系完整，作业含完整前端到后端</td><td>进阶</td><td>高</td></tr>
  </tbody>
</table>

<div class="box takeaway"><span class="t">现在可以做什么</span><p>如果你已经满足上面的前置条件，这一章推荐的材料现在就可以开始看；如果你还不确定要不要学这个方向，先读同章材料表里的第一本教材的前两章，通常两三小时就能判断出自己是否想继续。</p></div>

<footer>
  <p><strong>状态</strong> 规划中。章节骨架与材料清单已经确定，正文待写。</p>
  <p><strong>说明</strong> 材料推荐参考了 <a href="https://csdiy.wiki/">csdiy.wiki</a> 与各校公开课程主页；课程编号与工具版本会随时间变化，正文完成时会按当时的现状重新校对。</p>
</footer>
