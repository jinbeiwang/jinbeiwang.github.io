---
kind: chapter
order: 2
title: "数据结构与算法：把现实问题变成可计算的问题"
part: "第二部 · 机器侧主干"
prereq: "第一章"
reading: "—"
date: 2026-10-03
ready: false
tags: [计算机科学, 自学路线, 教材式笔记]
lang: zh
---

<div class="box finding"><span class="t">本章尚未动笔</span>
<p>这一章的位置已经在系列里定下来了：它是<b>第二部 · 机器侧主干</b>的第 2 章，前置是<b>第一章</b>。下面把规划好的骨架先摆出来，方便你判断这一章是否是你现在需要的。正文会在写完后替换掉这一页。</p></div>

<div class="box note"><span class="t">读这一章之前</span>
<p>需要：变量与类型、函数、基本的控制流。</p></div>

<h2><span class="n">1</span>这一章会讲什么</h2>
<p class="lede">为什么用渐进记号而不是秒表，以及三种记号各自回答什么问题。</p>

<table>
  <thead><tr><th style="width:52px;">节</th><th style="width:250px;">标题</th><th>要解决的问题</th></tr></thead>
  <tbody>
    <tr><td class="num">§1</td><td><b>复杂度：算法分析的语言</b></td><td>为什么用渐进记号而不是秒表，以及三种记号各自回答什么问题。</td></tr>
    <tr><td class="num">§2</td><td><b>线性结构：数组、链表、栈、队列</b></td><td>同一组数据，四种访问模式。附现实中各自出现的场景。</td></tr>
    <tr><td class="num">§3</td><td><b>哈希表：平均 O(1) 是怎么来的</b></td><td>从哈希函数、冲突处理到装载因子，推导期望复杂度。</td></tr>
    <tr><td class="num">§4</td><td><b>树与堆：有序性带来的收益</b></td><td>BST、平衡树、堆与优先队列，附 Python 标准库的实现选型。</td></tr>
    <tr><td class="num">§5</td><td><b>排序与查找</b></td><td>比较排序的下界证明、快排/归并/堆排的取舍、二分查找的边界写法。</td></tr>
    <tr><td class="num">§6</td><td><b>图与最短路</b></td><td>BFS/DFS/拓扑排序/Dijkstra，附用图思考问题的建模方法。</td></tr>
    <tr><td class="num">§7</td><td><b>算法设计范式</b></td><td>分治、贪心、动态规划、回溯：四种「想不出来时该怎么办」的套路。</td></tr>
  </tbody>
</table>

<h2><span class="n">2</span>这一章会用到哪些材料</h2>
<p class="lede">推荐理由、适用阶段与难度都写在表里 —— 换一门替代课完全可能更适合你，判断标准永远是你自己的进度。</p>

<table>
  <thead><tr><th style="width:86px;">类型</th><th style="width:250px;">材料</th><th>推荐理由</th><th style="width:96px;">适用阶段</th><th style="width:56px;">难度</th></tr></thead>
  <tbody>
    <tr><td>教材</td><td><b>《算法（第 4 版）》（Sedgewick & Wayne）</b></td><td>配图与代码最友好，Java 示例可读性强</td><td>入门～进阶</td><td>中</td></tr>
    <tr><td>教材</td><td><b>《Algorithms Illuminated》三卷（Tim Roughgarden）</b></td><td>推导详细、配套视频，适合自学</td><td>进阶</td><td>中</td></tr>
    <tr><td>教材</td><td><b>《Introduction to Algorithms》（CLRS，中文版《算法导论》）</b></td><td>公认权威参考，不建议零基础通读，适合当字典</td><td>进阶以上</td><td>高</td></tr>
    <tr><td>课程</td><td><b>Princeton《Algorithms, Part I/II》（Coursera）</b></td><td>与 Sedgewick 教材配套，有自动评测作业</td><td>入门～进阶</td><td>中</td></tr>
    <tr><td>课程</td><td><b>stanford《CS 161 Design and Analysis of Algorithms》</b></td><td>理论更完整，适合想补证明的人</td><td>进阶</td><td>高</td></tr>
    <tr><td>课程</td><td><b>UC Berkeley《CS 61B Data Structures》</b></td><td>项目驱动，Java；强调实现而非只做题</td><td>入门～进阶</td><td>中</td></tr>
    <tr><td>论文 · 文档</td><td><b>Python 官方文档《TimeComplexity》维基页</b></td><td>标准库操作的实测复杂度，写代码时最该查的一页</td><td>全程</td><td>低</td></tr>
  </tbody>
</table>

<div class="box takeaway"><span class="t">现在可以做什么</span><p>如果你已经满足上面的前置条件，这一章推荐的材料现在就可以开始看；如果你还不确定要不要学这个方向，先读同章材料表里的第一本教材的前两章，通常两三小时就能判断出自己是否想继续。</p></div>

<footer>
  <p><strong>状态</strong> 规划中。章节骨架与材料清单已经确定，正文待写。</p>
  <p><strong>说明</strong> 材料推荐参考了 <a href="https://csdiy.wiki/">csdiy.wiki</a> 与各校公开课程主页；课程编号与工具版本会随时间变化，正文完成时会按当时的现状重新校对。</p>
</footer>
