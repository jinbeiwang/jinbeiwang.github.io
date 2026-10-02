---
kind: chapter
order: 5
title: "计算机网络：两台机器怎么对话"
part: "第二部 · 机器侧主干"
prereq: "第一、二章"
reading: "—"
date: 2026-10-03
ready: false
tags: [计算机科学, 自学路线, 教材式笔记]
lang: zh
---

<div class="box finding"><span class="t">本章尚未动笔</span>
<p>这一章的位置已经在系列里定下来了：它是<b>第二部 · 机器侧主干</b>的第 5 章，前置是<b>第一、二章</b>。下面把规划好的骨架先摆出来，方便你判断这一章是否是你现在需要的。正文会在写完后替换掉这一页。</p></div>

<div class="box note"><span class="t">读这一章之前</span>
<p>需要：基本的编程能力与复杂度直觉。</p></div>

<h2><span class="n">1</span>这一章会讲什么</h2>
<p class="lede">为什么是分层而不是一个协议，附 OSI 与 TCP/IP 的对应。</p>

<table>
  <thead><tr><th style="width:52px;">节</th><th style="width:250px;">标题</th><th>要解决的问题</th></tr></thead>
  <tbody>
    <tr><td class="num">§1</td><td><b>分层：网络设计的第一性原理</b></td><td>为什么是分层而不是一个协议，附 OSI 与 TCP/IP 的对应。</td></tr>
    <tr><td class="num">§2</td><td><b>链路层与以太网</b></td><td>帧、MAC 地址、交换与 ARP。</td></tr>
    <tr><td class="num">§3</td><td><b>网络层：IP 与路由</b></td><td>子网、CIDR、NAT、BGP 的直观解释。</td></tr>
    <tr><td class="num">§4</td><td><b>传输层：TCP 与 UDP</b></td><td>三次握手、拥塞控制、重传与流量控制。</td></tr>
    <tr><td class="num">§5</td><td><b>应用层：HTTP 与 DNS</b></td><td>从一次浏览器请求串起前面四层。</td></tr>
    <tr><td class="num">§6</td><td><b>抓包实战</b></td><td>用 tcpdump/Wireshark 亲手看见握手与重传。</td></tr>
  </tbody>
</table>

<h2><span class="n">2</span>这一章会用到哪些材料</h2>
<p class="lede">推荐理由、适用阶段与难度都写在表里 —— 换一门替代课完全可能更适合你，判断标准永远是你自己的进度。</p>

<table>
  <thead><tr><th style="width:86px;">类型</th><th style="width:250px;">材料</th><th>推荐理由</th><th style="width:96px;">适用阶段</th><th style="width:56px;">难度</th></tr></thead>
  <tbody>
    <tr><td>教材</td><td><b>《Computer Networking: A Top-Down Approach》（自顶向下方法）</b></td><td>从应用层往下讲，最符合初学者的认知顺序</td><td>入门～进阶</td><td>中</td></tr>
    <tr><td>教材</td><td><b>《TCP/IP 详解 卷 1》</b></td><td>协议细节的权威参考，适合当字典</td><td>进阶</td><td>高</td></tr>
    <tr><td>课程</td><td><b>Stanford《CS 144 Introduction to Computer Networking》</b></td><td>有 Beej 的 beejs 项目，动手性极强</td><td>进阶</td><td>高</td></tr>
    <tr><td>课程</td><td><b>UMass《CS 453 Computer Networks》</b></td><td>配套自顶向下教材的公开课</td><td>入门～进阶</td><td>中</td></tr>
    <tr><td>课程</td><td><b>Coursera《Computer Communications》（伊利诺伊）</b></td><td>适合先建立整体印象</td><td>入门</td><td>低</td></tr>
  </tbody>
</table>

<div class="box takeaway"><span class="t">现在可以做什么</span><p>如果你已经满足上面的前置条件，这一章推荐的材料现在就可以开始看；如果你还不确定要不要学这个方向，先读同章材料表里的第一本教材的前两章，通常两三小时就能判断出自己是否想继续。</p></div>

<footer>
  <p><strong>状态</strong> 规划中。章节骨架与材料清单已经确定，正文待写。</p>
  <p><strong>说明</strong> 材料推荐参考了 <a href="https://csdiy.wiki/">csdiy.wiki</a> 与各校公开课程主页；课程编号与工具版本会随时间变化，正文完成时会按当时的现状重新校对。</p>
</footer>
