---
kind: chapter
order: 3
title: "计算机组成与体系结构：一行代码如何变成电信号"
part: "第二部 · 机器侧主干"
prereq: "第一章"
reading: "—"
date: 2026-10-03
ready: false
tags: [计算机科学, 自学路线, 教材式笔记]
lang: zh
---

<div class="box finding"><span class="t">本章尚未动笔</span>
<p>这一章的位置已经在系列里定下来了：它是<b>第二部 · 机器侧主干</b>的第 3 章，前置是<b>第一章</b>。下面把规划好的骨架先摆出来，方便你判断这一章是否是你现在需要的。正文会在写完后替换掉这一页。</p></div>

<div class="box note"><span class="t">读这一章之前</span>
<p>需要：二进制与基本的逻辑概念。不要求电路基础。</p></div>

<h2><span class="n">1</span>这一章会讲什么</h2>
<p class="lede">门电路、布尔代数与「为什么计算机用二进制」。</p>

<table>
  <thead><tr><th style="width:52px;">节</th><th style="width:250px;">标题</th><th>要解决的问题</th></tr></thead>
  <tbody>
    <tr><td class="num">§1</td><td><b>从比特到指令：抽象层的起点</b></td><td>门电路、布尔代数与「为什么计算机用二进制」。</td></tr>
    <tr><td class="num">§2</td><td><b>指令集：机器真正认识的语言</b></td><td>RISC 与 CISC 的分野，附一段汇编与 Python 的对照。</td></tr>
    <tr><td class="num">§3</td><td><b>处理器：数据通路与流水线</b></td><td>取指—译码—执行的分工，以及流水线冒险与转发。</td></tr>
    <tr><td class="num">§4</td><td><b>存储层次：为什么缓存能救命</b></td><td>局部性原理、缓存命中率，以及它如何解释算法的实际快慢。</td></tr>
    <tr><td class="num">§5</td><td><b>内存与 I/O</b></td><td>DRAM、总线、中断与 DMA。</td></tr>
    <tr><td class="num">§6</td><td><b>并行与性能</b></td><td>流水线、多核、SIMD；以及「摩尔定律之后」发生了什么。</td></tr>
  </tbody>
</table>

<h2><span class="n">2</span>这一章会用到哪些材料</h2>
<p class="lede">推荐理由、适用阶段与难度都写在表里 —— 换一门替代课完全可能更适合你，判断标准永远是你自己的进度。</p>

<table>
  <thead><tr><th style="width:86px;">类型</th><th style="width:250px;">材料</th><th>推荐理由</th><th style="width:96px;">适用阶段</th><th style="width:56px;">难度</th></tr></thead>
  <tbody>
    <tr><td>教材</td><td><b>《Computer Organization and Design》（Patterson & Hennessy）</b></td><td>RISC-V 版更适合入门，配套实验完整</td><td>入门～进阶</td><td>中</td></tr>
    <tr><td>教材</td><td><b>《Computer Systems: A Programmer's Perspective》（CSAPP）</b></td><td>从程序员视角打通组成与操作系统，本系列第三章与第四章的最佳桥梁</td><td>进阶</td><td>高</td></tr>
    <tr><td>课程</td><td><b>MIT 6.004《Computation Structures》</b></td><td>从门电路一路搭到处理器，有在线仿真器</td><td>入门～进阶</td><td>中</td></tr>
    <tr><td>课程</td><td><b>UC Berkeley《CS 61C Great Ideas in Computer Architecture》</b></td><td>CSAPP 路线的公开课版本</td><td>进阶</td><td>中</td></tr>
    <tr><td>课程</td><td><b>Coursera《Nand2Tetris》</b></td><td>从 NAND 门造出一台能跑游戏的计算机，动手性最强</td><td>入门</td><td>低</td></tr>
  </tbody>
</table>

<div class="box takeaway"><span class="t">现在可以做什么</span><p>如果你已经满足上面的前置条件，这一章推荐的材料现在就可以开始看；如果你还不确定要不要学这个方向，先读同章材料表里的第一本教材的前两章，通常两三小时就能判断出自己是否想继续。</p></div>

<footer>
  <p><strong>状态</strong> 规划中。章节骨架与材料清单已经确定，正文待写。</p>
  <p><strong>说明</strong> 材料推荐参考了 <a href="https://csdiy.wiki/">csdiy.wiki</a> 与各校公开课程主页；课程编号与工具版本会随时间变化，正文完成时会按当时的现状重新校对。</p>
</footer>
