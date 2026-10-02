---
kind: chapter
order: 4
title: "操作系统：资源怎么被分配"
part: "第二部 · 机器侧主干"
prereq: "第二、三章"
reading: "—"
date: 2026-10-03
ready: false
tags: [计算机科学, 自学路线, 教材式笔记]
lang: zh
---

<div class="box finding"><span class="t">本章尚未动笔</span>
<p>这一章的位置已经在系列里定下来了：它是<b>第二部 · 机器侧主干</b>的第 4 章，前置是<b>第二、三章</b>。下面把规划好的骨架先摆出来，方便你判断这一章是否是你现在需要的。正文会在写完后替换掉这一页。</p></div>

<div class="box note"><span class="t">读这一章之前</span>
<p>需要：进程与并发的基本概念、缓存与存储层次。</p></div>

<h2><span class="n">1</span>这一章会讲什么</h2>
<p class="lede">从「一台裸机」到「多道程序」的动机。</p>

<table>
  <thead><tr><th style="width:52px;">节</th><th style="width:250px;">标题</th><th>要解决的问题</th></tr></thead>
  <tbody>
    <tr><td class="num">§1</td><td><b>操作系统在解决什么问题</b></td><td>从「一台裸机」到「多道程序」的动机。</td></tr>
    <tr><td class="num">§2</td><td><b>进程与线程</b></td><td>上下文切换、调度算法，附 Linux CFS 的直观解释。</td></tr>
    <tr><td class="num">§3</td><td><b>并发与同步</b></td><td>竞态条件、锁、信号量与条件变量；附一个可复现的竞态 demo。</td></tr>
    <tr><td class="num">§4</td><td><b>虚拟内存</b></td><td>分页、页表、TLB、缺页异常与换页。</td></tr>
    <tr><td class="num">§5</td><td><b>文件系统</b></td><td>inode、目录项、日志式写入与崩溃一致性。</td></tr>
    <tr><td class="num">§6</td><td><b>I/O 与设备</b></td><td>中断、驱动、阻塞与非阻塞、epoll。</td></tr>
  </tbody>
</table>

<h2><span class="n">2</span>这一章会用到哪些材料</h2>
<p class="lede">推荐理由、适用阶段与难度都写在表里 —— 换一门替代课完全可能更适合你，判断标准永远是你自己的进度。</p>

<table>
  <thead><tr><th style="width:86px;">类型</th><th style="width:250px;">材料</th><th>推荐理由</th><th style="width:96px;">适用阶段</th><th style="width:56px;">难度</th></tr></thead>
  <tbody>
    <tr><td>教材</td><td><b>《Operating Systems: Three Easy Pieces》（OSTEP）</b></td><td>免费在线，写作风趣、推导清楚，事实上的首选入门教材</td><td>入门～进阶</td><td>中</td></tr>
    <tr><td>教材</td><td><b>《Operating System Concepts》（恐龙书）</b></td><td>体系完整，适合当参考书</td><td>进阶</td><td>中</td></tr>
    <tr><td>教材</td><td><b>《现代操作系统》（Tanenbaum）</b></td><td>覆盖面广，MINIX 案例详细</td><td>进阶</td><td>高</td></tr>
    <tr><td>课程</td><td><b>MIT 6.1810《Operating System Engineering》（原 6.S081）</b></td><td>xv6 labs 是公认最好的系统编程练习</td><td>进阶</td><td>高</td></tr>
    <tr><td>课程</td><td><b>UC Berkeley《CS 162 Operating Systems》</b></td><td>含 Pintos 项目，强调并发与文件系统</td><td>进阶</td><td>高</td></tr>
    <tr><td>论文 · 文档</td><td><b>Linux 内核文档 Documentation/ 目录</b></td><td>涉及具体实现时以它为准</td><td>进阶</td><td>中</td></tr>
  </tbody>
</table>

<div class="box takeaway"><span class="t">现在可以做什么</span><p>如果你已经满足上面的前置条件，这一章推荐的材料现在就可以开始看；如果你还不确定要不要学这个方向，先读同章材料表里的第一本教材的前两章，通常两三小时就能判断出自己是否想继续。</p></div>

<footer>
  <p><strong>状态</strong> 规划中。章节骨架与材料清单已经确定，正文待写。</p>
  <p><strong>说明</strong> 材料推荐参考了 <a href="https://csdiy.wiki/">csdiy.wiki</a> 与各校公开课程主页；课程编号与工具版本会随时间变化，正文完成时会按当时的现状重新校对。</p>
</footer>
