---
kind: chapter
order: 8
title: "分布式系统：把失败当成常态"
part: "第三部 · 系统侧纵深"
prereq: "第四、五、六章"
reading: "—"
date: 2026-10-03
ready: false
tags: [计算机科学, 自学路线, 教材式笔记]
lang: zh
---

<div class="box finding"><span class="t">本章尚未动笔</span>
<p>这一章的位置已经在系列里定下来了：它是<b>第三部 · 系统侧纵深</b>的第 8 章，前置是<b>第四、五、六章</b>。下面把规划好的骨架先摆出来，方便你判断这一章是否是你现在需要的。正文会在写完后替换掉这一页。</p></div>

<div class="box note"><span class="t">读这一章之前</span>
<p>需要：并发与同步、网络协议、事务与日志。</p></div>

<h2><span class="n">1</span>这一章会讲什么</h2>
<p class="lede">CAP 与 PACELC 的准确含义，纠正常见误用。</p>

<table>
  <thead><tr><th style="width:52px;">节</th><th style="width:250px;">标题</th><th>要解决的问题</th></tr></thead>
  <tbody>
    <tr><td class="num">§1</td><td><b>为什么分布式，以及代价是什么</b></td><td>CAP 与 PACELC 的准确含义，纠正常见误用。</td></tr>
    <tr><td class="num">§2</td><td><b>时间与顺序</b></td><td>物理时钟、逻辑时钟与因果序。</td></tr>
    <tr><td class="num">§3</td><td><b>复制与一致性</b></td><td>主从、多主、共识（Raft/Paxos）。</td></tr>
    <tr><td class="num">§4</td><td><b>分区与容错</b></td><td>一致性哈希、Gossip、故障检测。</td></tr>
    <tr><td class="num">§5</td><td><b>分布式事务</b></td><td>两阶段提交、Spanner 的 TrueTime。</td></tr>
    <tr><td class="num">§6</td><td><b>工程实践</b></td><td>幂等、重试、超时、熔断与可观测性。</td></tr>
  </tbody>
</table>

<h2><span class="n">2</span>这一章会用到哪些材料</h2>
<p class="lede">推荐理由、适用阶段与难度都写在表里 —— 换一门替代课完全可能更适合你，判断标准永远是你自己的进度。</p>

<table>
  <thead><tr><th style="width:86px;">类型</th><th style="width:250px;">材料</th><th>推荐理由</th><th style="width:96px;">适用阶段</th><th style="width:56px;">难度</th></tr></thead>
  <tbody>
    <tr><td>教材</td><td><b>《Designing Data-Intensive Applications》（DDIA）</b></td><td>公认最好的入门与总览，先读它再读论文</td><td>进阶</td><td>中</td></tr>
    <tr><td>教材</td><td><b>《Distributed Systems》（Maarten van Steen & Tanenbaum，免费在线）</b></td><td>体系完整的教科书</td><td>进阶</td><td>中</td></tr>
    <tr><td>课程</td><td><b>MIT 6.5840《Distributed Systems》（原 6.824）</b></td><td>含 Raft/MapReduce/KV 等 labs，难度高但收益极大</td><td>高级</td><td>高</td></tr>
    <tr><td>课程</td><td><b>CMU 15-440/15-640《Distributed Systems》</b></td><td>覆盖面广，含 Paxi 实验</td><td>进阶～高级</td><td>高</td></tr>
    <tr><td>论文 · 文档</td><td><b>《Raft 论文》《Google Spanner 论文》《Amazon Dynamo 论文》</b></td><td>三期经典必读，先把 DDIA 对应章节读完再读</td><td>高级</td><td>高</td></tr>
  </tbody>
</table>

<div class="box takeaway"><span class="t">现在可以做什么</span><p>如果你已经满足上面的前置条件，这一章推荐的材料现在就可以开始看；如果你还不确定要不要学这个方向，先读同章材料表里的第一本教材的前两章，通常两三小时就能判断出自己是否想继续。</p></div>

<footer>
  <p><strong>状态</strong> 规划中。章节骨架与材料清单已经确定，正文待写。</p>
  <p><strong>说明</strong> 材料推荐参考了 <a href="https://csdiy.wiki/">csdiy.wiki</a> 与各校公开课程主页；课程编号与工具版本会随时间变化，正文完成时会按当时的现状重新校对。</p>
</footer>
