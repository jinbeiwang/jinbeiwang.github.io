---
kind: chapter
order: 6
title: "数据库系统：数据怎么被可靠地存下来"
part: "第二部 · 机器侧主干"
prereq: "第二、三、四章"
reading: "—"
date: 2026-10-03
ready: false
tags: [计算机科学, 自学路线, 教材式笔记]
lang: zh
---

<div class="box finding"><span class="t">本章尚未动笔</span>
<p>这一章的位置已经在系列里定下来了：它是<b>第二部 · 机器侧主干</b>的第 6 章，前置是<b>第二、三、四章</b>。下面把规划好的骨架先摆出来，方便你判断这一章是否是你现在需要的。正文会在写完后替换掉这一页。</p></div>

<div class="box note"><span class="t">读这一章之前</span>
<p>需要：B 树与哈希、页式存储与缓存、并发控制的基本概念。</p></div>

<h2><span class="n">1</span>这一章会讲什么</h2>
<p class="lede">为什么文件系统不够用：并发、持久化、查询。</p>

<table>
  <thead><tr><th style="width:52px;">节</th><th style="width:250px;">标题</th><th>要解决的问题</th></tr></thead>
  <tbody>
    <tr><td class="num">§1</td><td><b>数据库解决的是「同时」问题</b></td><td>为什么文件系统不够用：并发、持久化、查询。</td></tr>
    <tr><td class="num">§2</td><td><b>存储引擎：页、缓冲池与记录格式</b></td><td>从磁盘页到元组，附缓冲池替换策略。</td></tr>
    <tr><td class="num">§3</td><td><b>索引：B+ 树为什么赢了</b></td><td>与 B 树、哈希索引、LSM 树的定量比较。</td></tr>
    <tr><td class="num">§4</td><td><b>查询执行：从 SQL 到结果</b></td><td>算子、连接算法与代价估算。</td></tr>
    <tr><td class="num">§5</td><td><b>事务与并发控制</b></td><td>ACID、两阶段锁、MVCC；附可复现的隔离级别实验。</td></tr>
    <tr><td class="num">§6</td><td><b>恢复与日志</b></td><td>WAL、检查点，以及为什么顺序写是关键。</td></tr>
  </tbody>
</table>

<h2><span class="n">2</span>这一章会用到哪些材料</h2>
<p class="lede">推荐理由、适用阶段与难度都写在表里 —— 换一门替代课完全可能更适合你，判断标准永远是你自己的进度。</p>

<table>
  <thead><tr><th style="width:86px;">类型</th><th style="width:250px;">材料</th><th>推荐理由</th><th style="width:96px;">适用阶段</th><th style="width:56px;">难度</th></tr></thead>
  <tbody>
    <tr><td>教材</td><td><b>《Database System Concepts》（Silberschatz 等）</b></td><td>体系最完整的入门教材</td><td>入门～进阶</td><td>中</td></tr>
    <tr><td>教材</td><td><b>《Architecture of a Database System》（Hellerstein 等）</b></td><td>一篇论文讲清数据库整体架构，性价比极高</td><td>进阶</td><td>中</td></tr>
    <tr><td>教材</td><td><b>《Readings in Database Systems》（红皮书，第 5 版在线）</b></td><td>论文选集，适合确定深入方向</td><td>进阶以上</td><td>高</td></tr>
    <tr><td>课程</td><td><b>CMU 15-445《Database Systems》</b></td><td>公认最好的数据库实现课，BusTub 项目含金量高</td><td>进阶</td><td>高</td></tr>
    <tr><td>课程</td><td><b>CMU 15-721《Advanced Database Systems》</b></td><td>面向分析与内存数据库，进阶选读</td><td>高级</td><td>高</td></tr>
  </tbody>
</table>

<div class="box takeaway"><span class="t">现在可以做什么</span><p>如果你已经满足上面的前置条件，这一章推荐的材料现在就可以开始看；如果你还不确定要不要学这个方向，先读同章材料表里的第一本教材的前两章，通常两三小时就能判断出自己是否想继续。</p></div>

<footer>
  <p><strong>状态</strong> 规划中。章节骨架与材料清单已经确定，正文待写。</p>
  <p><strong>说明</strong> 材料推荐参考了 <a href="https://csdiy.wiki/">csdiy.wiki</a> 与各校公开课程主页；课程编号与工具版本会随时间变化，正文完成时会按当时的现状重新校对。</p>
</footer>
