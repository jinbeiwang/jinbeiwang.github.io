---
title: "DeepSeek 技术报告精读手册：演进、对比与原理拆解"
summary: "写给初学者的技术报告精读手册：先用一句话说清每个概念要解决什么问题，再拆开公式与结构，最后用一个可交互的小实验亲手拨动参数。纵向是 DeepSeek 的版本演化，横向是与 GPT / Claude / Gemini 的对比，纵深是 MLA、MoE、GRPO、FP8、DSA、CED 这些名词背后的原理。"
date: 2026-09-21
category: Learning log
tags: [DeepSeek, LLM, 技术报告, 学习路径]
lang: zh
---

<div class="meta-row">
    <span><b>依据</b> &nbsp;DeepSeek 官方发布页与技术报告、Hugging Face 模型卡、arXiv 论文、OpenAI / Anthropic 官方页面</span>
    <span><b>数据截至</b> &nbsp;2026-09-21 —— V4.1-Pro 未发布；V4-Pro 的下线计划已被官方收回</span>
  </div>

<p class="lede">这是一份<b>写给初学者的技术报告精读手册</b>。它不把原报告改写成大白话，而是给你一副「脚手架」： 先用一句话说清每个概念<b>要解决什么问题</b>，再拆开它的<b>公式与结构</b>，最后用一个<b>可交互的小实验</b>让你亲手拨动参数、看见结果。 三条线索贯穿全文 —— <b>纵向</b>（DeepSeek 版本怎么一路演化过来）、<b>横向</b>（它与 GPT、Claude、Gemini 差在哪里）、<b>纵深</b>（MLA、MoE、GRPO、FP8、DSA 这些名词背后的原理）。</p>

<style>
/* ============================================================
   设计定调：Editorial × Technical Blueprint（浅色纸张 + 蓝图网格）
   展示字：衬线（Iowan / Palatino / 宋体）  正文：中文无衬线
   数字与代码：等宽 + tabular-nums
   主色：纸白  强调色：单一「深研蓝」  警示：砖红（仅用于局限与风险）
   ============================================================ */
:root{
  --paper:#ffffff;
  --paper-2:#fbfcfd;
  --card:#FFFFFF;
  --ink:#17181a;
  --ink-2:#5b6570;
  --ink-3:#5b6570;
  --ink-4:#8b949e;
  --rule:#d8dde3;
  --rule-2:#eaeef2;
  --accent:#1b4f8a;
  --accent-2:#2f6fb8;
  --accent-soft:rgba(27,79,138,.07);
  --accent-line:rgba(27,79,138,.22);
  --warn:#a8611f;
  --warn-soft:rgba(168,97,31,.07);
  --ok:#0f7b5f;
  --mono:ui-monospace,"JetBrains Mono","Cascadia Mono","SFMono-Regular",Consolas,"Liberation Mono",monospace;
  --sans:"PingFang SC","HarmonyOS Sans SC","Source Han Sans SC","Noto Sans SC","Hiragino Sans GB","Microsoft YaHei",system-ui,-apple-system,sans-serif;
  --serif:var(--sans);
  --sh-1:0 1px 2px rgba(24,20,12,.05),0 2px 6px rgba(24,20,12,.04);
  --sh-2:0 2px 4px rgba(24,20,12,.05),0 8px 22px rgba(24,20,12,.07);
  --sh-3:0 4px 8px rgba(24,20,12,.06),0 24px 60px rgba(24,20,12,.11);
  --ease:cubic-bezier(.16,1,.3,1);
  --r-s:6px; --r-m:12px; --r-l:20px;
  --nav-w:236px;
}

*,*::before,*::after{box-sizing:border-box}
::selection{background:rgba(47,111,184,.22)}
.mono{font-family:var(--mono);font-variant-numeric:tabular-nums}
/* ---------- 阅读进度 ---------- */
/* ---------- 布局 ---------- */
.rule{height:1px;background:var(--rule);border:0;margin:0}

/* ---------- 侧栏目录 ---------- */
@media(min-width:1120px){
}
/* ---------- 首屏 ---------- */
@media(min-width:820px){.metrics{grid-template-columns:repeat(4,minmax(0,1fr))}}
/* ---------- 通用章节 ---------- */
.sec{padding-top:56px}
.sec-head{display:flex;gap:20px;align-items:baseline;border-top:2px solid var(--ink);padding-top:16px;margin-bottom:30px}
.sec-num{font-family:var(--mono);font-size:13px;color:var(--accent);letter-spacing:.1em;padding-top:6px;flex:0 0 auto}
.sec-head h2{font-size:clamp(27px,3.5vw,40px);letter-spacing:-.03em;flex:1 1 auto}
.sec-head .sub{flex:0 0 auto;font-family:var(--mono);font-size:11px;color:var(--ink-4);letter-spacing:.12em;padding-top:6px}
.cols{max-width:74ch}
.cols p{color:var(--ink-2)}
/* ---------- 卡片 / 标签 / 提示 ---------- */
.card{background:var(--card);border:1px solid var(--rule);border-radius:var(--r-m);padding:22px 24px;box-shadow:var(--sh-1)}
.grid2{display:grid;gap:16px;grid-template-columns:1fr}
@media(min-width:860px){.grid2{grid-template-columns:1fr 1fr}}
.grid3{display:grid;gap:14px;grid-template-columns:1fr}
@media(min-width:760px){.grid3{grid-template-columns:repeat(3,1fr)}}
.tag{display:inline-block;font-family:var(--mono);font-size:11px;letter-spacing:.08em;padding:2.5px 8px;border-radius:999px;border:1px solid var(--rule);color:var(--ink-3);background:var(--paper-2);white-space:nowrap}
.tag.acc{border-color:var(--accent-line);color:var(--accent);background:var(--accent-soft)}
.tag.warn{border-color:rgba(168,97,31,.28);color:var(--warn);background:var(--warn-soft)}
.src{font-size:12.5px;color:var(--ink-4);font-family:var(--mono);margin-top:10px;line-height:1.6}

/* ---------- 时间轴 ---------- */
.tl{position:relative;margin:26px 0 0;padding:0 0 6px}
.tl-rail{display:flex;gap:0;overflow-x:auto;padding:26px 4px 18px;scrollbar-width:thin;border-top:1px solid var(--rule-2);position:relative}
.tl-rail::-webkit-scrollbar{height:7px}
.tl-rail::-webkit-scrollbar-thumb{background:var(--rule);border-radius:4px}
.tl-rail::before{content:"";position:absolute;left:0;right:0;top:59px;height:1px;background:var(--rule);pointer-events:none;z-index:0}
.tl-node{
  flex:0 0 auto;width:132px;background:none;border:0;padding:0;cursor:pointer;text-align:left;
  font-family:inherit;color:inherit;position:relative;
}
.tl-node .d{font-family:var(--mono);font-size:10.5px;color:var(--ink-4);letter-spacing:.06em;display:block;margin-bottom:12px}
.tl-node .m{width:11px;height:11px;border-radius:50%;background:var(--paper);border:2px solid var(--rule);display:block;margin:0 0 12px 16px;transition:all .2s var(--ease)}
.tl-node .nm{font-size:13.5px;font-weight:600;line-height:1.35;display:block;padding-right:10px}
.tl-node .tp{font-size:11.5px;color:var(--ink-3);display:block;margin-top:4px;line-height:1.45;padding-right:10px}
.tl-node:hover .m{border-color:var(--accent-2);background:var(--accent-soft)}
.tl-node.on .m{border-color:var(--accent);background:var(--accent);box-shadow:0 0 0 5px var(--accent-soft)}
.tl-node.on .nm{color:var(--accent)}
.vcard{display:none;animation:fade .34s var(--ease) both}
.vcard.on{display:block}
@keyframes fade{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:none}}
.vhead{display:flex;flex-wrap:wrap;gap:10px 14px;align-items:baseline;margin-bottom:6px}
.vhead h4{font-family:var(--serif);font-size:24px;margin:0;letter-spacing:-.02em}
.vhead .vd{font-family:var(--mono);font-size:12px;color:var(--ink-4)}
.vgrid{display:grid;gap:1px;background:var(--rule-2);border:1px solid var(--rule-2);border-radius:var(--r-m);overflow:hidden;margin:16px 0 0;grid-template-columns:1fr}
@media(min-width:780px){.vgrid{grid-template-columns:repeat(2,1fr)}}
.vcell{background:var(--card);padding:14px 16px}
.vcell .k{font-family:var(--mono);font-size:10.5px;letter-spacing:.12em;text-transform:uppercase;color:var(--ink-4);display:block;margin-bottom:5px}
.vcell .v{font-size:14.5px;color:var(--ink-2);line-height:1.65}
.vcell .v b{color:var(--ink)}
.keylist{margin:14px 0 0;padding:0;list-style:none}
.keylist li{position:relative;padding-left:22px;margin-bottom:9px;font-size:15.5px;color:var(--ink-2);line-height:1.68}
.keylist li::before{content:"";position:absolute;left:4px;top:.62em;width:7px;height:7px;border-radius:2px;background:var(--accent-2);opacity:.75}
.keylist li b{color:var(--ink)}

/* ---------- 表格 ---------- */
.tbl-wrap{overflow-x:auto;margin:18px 0;overflow-x:auto;border:1px solid var(--rule);border-radius:var(--r-m);background:var(--card);box-shadow:var(--sh-1);margin:20px 0}
td.num,th.num{font-family:var(--mono);font-variant-numeric:tabular-nums;text-align:right;white-space:nowrap}
td.nm{font-weight:600;color:var(--ink);white-space:nowrap}
.hi{color:var(--accent);font-weight:600}
.lo{color:var(--warn)}

/* ---------- 图示容器 ---------- */
.legend{display:flex;flex-wrap:wrap;gap:8px 18px;font-size:12.5px;color:var(--ink-3);margin-top:10px}
.legend i{display:inline-block;width:10px;height:10px;border-radius:2px;margin-right:6px;vertical-align:-1px}

/* ---------- 实验台（交互） ---------- */
.lab{
  background:var(--card);border:1px solid var(--rule);border-radius:var(--r-m);
  box-shadow:var(--sh-2);margin:24px 0;overflow:hidden;
}
.lab-head{
  display:flex;flex-wrap:wrap;gap:10px 14px;align-items:center;justify-content:space-between;
  padding:13px 18px;background:var(--paper-2);border-bottom:1px solid var(--rule-2);
}
.lab-head .lt{font-family:var(--mono);font-size:11px;letter-spacing:.14em;text-transform:uppercase;color:var(--accent)}
.lab-head .lh{font-size:14.5px;font-weight:600;flex:1 1 auto}
.lab-body{padding:20px 18px}
.lab-ctrl{display:flex;flex-wrap:wrap;gap:12px 20px;align-items:center;margin-bottom:18px}
.lab-ctrl label{font-size:13px;color:var(--ink-3);font-family:var(--mono);letter-spacing:.04em}
input[type=range]{
  -webkit-appearance:none;appearance:none;height:4px;border-radius:2px;background:var(--rule);
  outline:none;flex:1 1 200px;max-width:340px;min-width:150px;
}
input[type=range]::-webkit-slider-thumb{-webkit-appearance:none;width:20px;height:20px;border-radius:50%;background:var(--accent);border:3px solid #fff;box-shadow:0 1px 4px rgba(0,0,0,.28);cursor:pointer}
input[type=range]::-moz-range-thumb{width:16px;height:16px;border-radius:50%;background:var(--accent);border:3px solid #fff;cursor:pointer}
button.btn{
  font-family:var(--mono);font-size:12.5px;letter-spacing:.06em;padding:10px 18px;min-height:44px;
  border-radius:999px;border:1px solid var(--accent);background:var(--accent);color:#fff;cursor:pointer;
  transition:all .18s var(--ease);font-weight:600;
}
button.btn:hover{background:#174573;border-color:#174573;transform:translateY(-1px);box-shadow:var(--sh-2)}
button.btn:active{transform:none}
button.btn:focus-visible,a:focus-visible{outline:3px solid var(--accent-2);outline-offset:2px}
button.btn.ghost{background:transparent;color:var(--accent)}
button.btn.ghost:hover{background:var(--accent-soft);box-shadow:none}
.readout{font-family:var(--mono);font-variant-numeric:tabular-nums;font-size:13px;color:var(--ink-2);line-height:1.9}
.readout .rl{display:flex;justify-content:space-between;gap:18px;border-bottom:1px dashed var(--rule-2);padding:5px 0}
.readout .rl:last-child{border-bottom:0}
.readout .rv{color:var(--accent);font-weight:600;text-align:right}
.readout .rv.plain{color:var(--ink);font-weight:400}

/* 通用条形 */
.bars{display:flex;flex-direction:column;gap:9px}
.bar-row{display:grid;grid-template-columns:112px 1fr 84px;gap:12px;align-items:center;font-size:12.5px}
@media(max-width:560px){.bar-row{grid-template-columns:88px 1fr 70px;font-size:11.5px;gap:8px}}
.bar-row .bl{color:var(--ink-3);font-family:var(--mono);text-align:right;letter-spacing:.02em}
.bar-row .bt{height:16px;background:var(--rule-2);border-radius:3px;overflow:hidden;position:relative}
.bar-row .bf{height:100%;width:0;background:var(--accent);border-radius:3px;transition:width .5s var(--ease)}
.bar-row .bf.alt{background:linear-gradient(90deg,var(--accent),var(--accent-2))}
.bar-row .bf.gray{background:var(--ink-4)}
.bar-row .bf.warn{background:var(--warn)}
.bar-row .bv{font-family:var(--mono);color:var(--ink-2);text-align:right;font-variant-numeric:tabular-nums}

/* MoE 专家网格 */
#moeWrap{display:grid;gap:20px;grid-template-columns:1fr}
@media(min-width:820px){#moeWrap{grid-template-columns:minmax(0,1.25fr) minmax(0,1fr)}}
#moeGrid{display:grid;grid-template-columns:repeat(16,1fr);gap:3px;background:var(--paper-2);border:1px solid var(--rule-2);border-radius:var(--r-s);padding:8px}
#moeGrid .ex{
  aspect-ratio:1/1;border-radius:2px;background:var(--rule-2);transition:background .22s var(--ease),transform .22s var(--ease);
}
#moeGrid .ex.shared{box-shadow:inset 0 0 0 2px var(--accent-2);background:#eef3f8}
#moeGrid .ex.hot{background:var(--accent-2);transform:scale(1.28)}
#moeGrid .ex.over{background:var(--warn);opacity:.85}
#moeGrid .ex.under{background:#e3e8ee}

/* GRPO 输出 */
#grpoOut{display:grid;grid-template-columns:repeat(4,1fr);gap:8px;margin-bottom:16px}
@media(min-width:760px){#grpoOut{grid-template-columns:repeat(8,1fr)}}
#grpoOut .sm{
  border:1px solid var(--rule);border-radius:var(--r-s);background:var(--paper-2);padding:8px 4px;text-align:center;
  font-family:var(--mono);font-size:11px;line-height:1.4;transition:all .3s var(--ease);
}
#grpoOut .sm .r{display:block;font-size:16px;font-weight:600;margin-top:3px}
#grpoOut .sm.r1{border-color:rgba(15,123,95,.4);background:rgba(15,123,95,.06)}
#grpoOut .sm.r1 .r{color:var(--ok)}
#grpoOut .sm.r0{border-color:rgba(168,97,31,.28);background:var(--warn-soft)}
#grpoOut .sm.r0 .r{color:var(--warn)}

/* 精度切换 */
.pills{display:flex;gap:8px;flex-wrap:wrap}
.pills button{
  font-family:var(--mono);font-size:12.5px;padding:9px 16px;min-height:44px;border-radius:999px;border:1px solid var(--rule);
  background:var(--paper-2);color:var(--ink-3);cursor:pointer;transition:all .18s var(--ease);
}
.pills button:hover{border-color:var(--accent-line);color:var(--ink)}
.pills button.on{background:var(--accent);border-color:var(--accent);color:#fff;font-weight:600}
.pills button:focus-visible{outline:3px solid var(--accent-2);outline-offset:2px}

/* 揭示动效 */
@media(prefers-reduced-motion:reduce){
*{animation-duration:.001ms!important;transition-duration:.001ms!important}
}
/* 首屏入场编排 */
@keyframes rise{from{opacity:0;transform:translateY(20px)}to{opacity:1;transform:none}}

/* 页脚 */
.kbd{font-family:var(--mono);font-size:11.5px;border:1px solid var(--rule);border-bottom-width:2px;border-radius:4px;padding:1px 6px;background:var(--paper-2);color:var(--ink-2)}

/* ---- brought onto the note's palette. Everything above is the guide's own
   chrome; these are the few places where it meets the note's typography. ---- */
h3 .n{font-family:var(--mono);font-size:12.5px;color:var(--accent);margin-right:8px;letter-spacing:.06em}
.sec{padding-top:0}
.sec-head{display:flex;flex-wrap:wrap;gap:8px 14px;align-items:baseline;border-top:0;padding-top:0;margin:0 0 4px}
.sec-head h2{flex:1 1 auto;margin:0}
.sec-head .sub{flex:0 0 auto}
.cols{max-width:none}
.src{color:var(--ink-4)}
.box.note,.box.finding{margin:18px 0}
</style>

<!-- ============================ 第 0 章 ============================ -->
<section class="sec reveal" id="howto" style="padding-top:44px">
  <div class="sec-head">
    <span class="sec-"">00</span>
    <h2>怎么读一份技术报告</h2>
    <span class="sub">READING PROTOCOL</span>
  </div>
  <div class="cols">
    <p>你的困难不是「看不懂中文」，而是<b>缺少承接新术语的框架</b>。技术报告的写法是：默认读者已经知道上一代方法，于是只写「相对于上一代，我改了什么」。所以直接从头读，会不断撞到没有定义的词。</p>
    <p>推荐的顺序是四遍法，每一遍只解决一个问题，刻意忽略其余内容：</p>
  </div>
  <div class="grid2" style="margin-top:18px">
    <div class="card"><h4><span class="tag acc">第 1 遍</span> 只读摘要与图表标题</h4>
      <p style="font-size:15px;color:var(--ink-2);margin:0">技术报告的<b>摘要（Abstract）</b>和<b>所有图的标题</b>已经包含 80% 的信息量。这一遍只回答：它是什么模型、多大、比谁强、凭什么省。不查任何术语。</p></div>
    <div class="card"><h4><span class="tag acc">第 2 遍</span> 读架构章节，画方框图</h4>
      <p style="font-size:15px;color:var(--ink-2);margin:0">把 <code>Architecture</code> 一节抄成一张方框图：数据从输入到输出经过哪些模块。凡是出现在图里的模块，就是你后面必须搞懂的名词清单。</p></div>
    <div class="card"><h4><span class="tag acc">第 3 遍</span> 逐个攻克公式</h4>
      <p style="font-size:15px;color:var(--ink-2);margin:0">不要试图一次看懂所有公式。按这个次序问自己三件事：<b>输入是什么</b>、<b>输出是什么</b>、<b>为什么不直接用上一代的写法</b>。第三问才是技术报告真正想说的话。</p></div>
    <div class="card"><h4><span class="tag acc">第 4 遍</span> 读实验与消融</h4>
      <p style="font-size:15px;color:var(--ink-2);margin:0"><b>消融实验（Ablation）</b>是作者自己做的「去掉了会怎样」的对照。这一节的表格，往往比主结果表更能告诉你：哪个创新是真的关键，哪个只是锦上添花。</p></div>
  </div>
  <div class="box note">
    <span class="t">贯穿全文的提醒</span>
    <b>「参数总量」不等于「计算量」。</b>DeepSeek V4-Pro 有 1.6 万亿参数，但每生成一个词只激活 490 亿。看到「7B / 671B / 1.6T」这类数字时，永远要追问一句：<b>激活了多少</b>？这是理解整个 DeepSeek 技术路线的第一把钥匙。
  </div>
</section>
<!-- ============================ 术语速查 ============================ -->
<section class="sec reveal" id="glossary" style="padding-top:40px">
  <h3 style="margin-top:0"><span class="n">0.1</span>术语速查表（先混个脸熟）</h3>
  <div class="cols"><p>不用背，扫一眼即可。后文每个术语都会有独立小节，这里只建立「它大概是什么」的印象。</p></div>
  <div class="tbl-wrap">
    <table>
      <thead><tr><th style="width:130px">缩写</th><th style="width:150px">英文全称</th><th>一句话理解</th><th style="width:96px">详见</th></tr></thead>
      <tbody>
        <tr><td class="nm">Attention</td><td class="mono">Attention</td><td>让每个词「看着」上下文中所有其他词来决定自己的含义，是 Transformer 的核心运算</td><td><a href="#c-attn">3.1</a></td></tr>
        <tr><td class="nm">KV Cache</td><td class="mono">Key-Value Cache</td><td>把历史词的 Key / Value 向量存下来避免重复计算。它是长上下文推理时显存的第一大开销</td><td><a href="#c-attn">3.1</a></td></tr>
        <tr><td class="nm">MHA / MQA / GQA</td><td class="mono">Multi-/Multi-Query/Grouped-Query Attention</td><td>注意力「多头数」的三种共享策略，共享越多缓存越小，但表达力也越受限</td><td><a href="#c-mla">3.2</a></td></tr>
        <tr><td class="nm">MLA</td><td class="mono">Multi-head Latent Attention</td><td>把 KV 压缩成一个低维「潜在向量」再缓存，缓存降到约 1/10 而性能不降</td><td><a href="#c-mla">3.2</a></td></tr>
        <tr><td class="nm">MoE</td><td class="mono">Mixture-of-Experts</td><td>把前馈网络切成很多「专家」，每个词只调用其中几个，参数大但算得少</td><td><a href="#c-moe">3.3</a></td></tr>
        <tr><td class="nm">Router</td><td class="mono">Gating / Router</td><td>MoE 里的「分诊台」，决定这个词该派给哪几个专家</td><td><a href="#c-moe">3.3</a></td></tr>
        <tr><td class="nm">MTP</td><td class="mono">Multi-Token Prediction</td><td>训练时让模型一次预测未来多个词，逼它想得更远，还能加速推理</td><td><a href="#c-mtp">3.5</a></td></tr>
        <tr><td class="nm">FP8 / FP4</td><td class="mono">8-/4-bit Floating Point</td><td>用更少的比特表示小数，省显存省带宽，代价是精度风险</td><td><a href="#c-precision">3.6</a></td></tr>
        <tr><td class="nm">RL / RLHF</td><td class="mono">Reinforcement Learning (from Human Feedback)</td><td>用打分反馈去调整模型行为，从「会说话」到「说得好」</td><td><a href="#c-rl">3.7</a></td></tr>
        <tr><td class="nm">GRPO</td><td class="mono">Group Relative Policy Optimization</td><td>同一道题采样一组答案，组内互相比，用相对高低当训练信号</td><td><a href="#c-rl">3.7</a></td></tr>
        <tr><td class="nm">CoT</td><td class="mono">Chain-of-Thought</td><td>让模型先写推理过程再给答案，即「思考链」</td><td><a href="#c-test">3.16</a></td></tr>
        <tr><td class="nm">Distillation</td><td class="mono">Knowledge Distillation</td><td>大模型当老师，小模型学它的输出，从而「继承」能力</td><td><a href="#c-distill">3.9</a></td></tr>
        <tr><td class="nm">DSA</td><td class="mono">DeepSeek Sparse Attention</td><td>先挑出最相关的少量词再算注意力，把长文本成本从平方级压下来</td><td><a href="#c-sparse">3.10</a></td></tr>
        <tr><td class="nm">CSA / HCA</td><td class="mono">Compressed Sparse / Heavily Compressed Attention</td><td>两种「压缩后再看」的注意力分支，分别负责远距离检索与全局概览</td><td><a href="#c-hybrid">3.11</a></td></tr>
        <tr><td class="nm">mHC</td><td class="mono">Manifold-Constrained Hyper-Connections</td><td>把残差连接升级成「受约束的多路高速路」，让超深网络信号更稳</td><td><a href="#c-train">3.13</a></td></tr>
        <tr><td class="nm">Muon</td><td class="mono">Muon Optimizer</td><td>一种替代 AdamW 的优化器，用矩阵正交化加速收敛</td><td><a href="#c-train">3.13</a></td></tr>
        <tr><td class="nm">Engram</td><td class="mono">Engram Conditional Memory</td><td>用查表方式做「条件记忆」，是 MoE 之外新的一条稀疏轴</td><td><a href="#c-mem">3.14</a></td></tr>
        <tr><td class="nm">OPD</td><td class="mono">On-Policy Distillation</td><td>把多个领域专家的能力合并回一个统一模型</td><td><a href="#c-opd">3.17</a></td></tr>
      </tbody>
    </table>
  </div>
</section>
<!-- ============================ 第一部分 ============================ -->
<section class="sec reveal" id="p1">
  <div class="sec-head">
    <span class="sec-"">01</span>
    <h2>纵向：DeepSeek 的演进路线</h2>
    <span class="sub">EVOLUTION · 2024.01 → 2026.09</span>
  </div>
  <div class="cols">
    <p>把 DeepSeek 的迭代看成一条不断解方程的主线：<b>每一个版本都在解「更强的能力」与「更低的成本」之间的同一个矛盾</b>，只是每一代换了一个约束条件。下面 12 个节点，点击任意一个即可展开该版本的技术要点。</p>
  </div>
  <h3 id="p1-timeline"><span class="n">1.1</span>12 个版本节点</h3>
  <div class="tl">
    <div class="tl-rail" role="tablist" aria-label="DeepSeek 版本时间轴">
      <button class="tl-node on" data-v="v1" role="tab" aria-selected="true"><span class="d">2024.01</span><span class="m"></span><span class="nm">DeepSeek LLM 67B</span><span class="tp">第一代，密集架构</span></button>
      <button class="tl-node" data-v="v2" role="tab" aria-selected="false"><span class="d">2024.05</span><span class="m"></span><span class="nm">DeepSeek-V2</span><span class="tp">MLA + MoE 双创新</span></button>
      <button class="tl-node" data-v="v3" role="tab" aria-selected="false"><span class="d">2024.12</span><span class="m"></span><span class="nm">DeepSeek-V3</span><span class="tp">671B / 37B，FP8 训练</span></button>
      <button class="tl-node" data-v="r1" role="tab" aria-selected="false"><span class="d">2025.01</span><span class="m"></span><span class="nm">DeepSeek-R1</span><span class="tp">纯 RL 涌现推理</span></button>
      <button class="tl-node" data-v="v30324" role="tab" aria-selected="false"><span class="d">2025.03</span><span class="m"></span><span class="nm">V3-0324</span><span class="tp">编程强化，开源登顶</span></button>
      <button class="tl-node" data-v="v31" role="tab" aria-selected="false"><span class="d">2025.08</span><span class="m"></span><span class="nm">V3.1 / Terminus</span><span class="tp">思考-非思考双模式</span></button>
      <button class="tl-node" data-v="v32exp" role="tab" aria-selected="false"><span class="d">2025.09</span><span class="m"></span><span class="nm">V3.2-Exp</span><span class="tp">DSA 稀疏注意力</span></button>
      <button class="tl-node" data-v="v32" role="tab" aria-selected="false"><span class="d">2025.12</span><span class="m"></span><span class="nm">V3.2 正式版</span><span class="tp">思考融入工具使用</span></button>
      <button class="tl-node" data-v="ctx1m" role="tab" aria-selected="false"><span class="d">2026.02</span><span class="m"></span><span class="nm">1M 上下文</span><span class="tp">静默升级到百万级</span></button>
      <button class="tl-node" data-v="v4" role="tab" aria-selected="false"><span class="d">2026.04</span><span class="m"></span><span class="nm">DeepSeek-V4 预览</span><span class="tp">1.6T，混合注意力</span></button>
      <button class="tl-node" data-v="v40813" role="tab" aria-selected="false"><span class="d">2026.08</span><span class="m"></span><span class="nm">V4-Pro-0813</span><span class="tp">Agent 能力正式版</span></button>
      <button class="tl-node" data-v="v41" role="tab" aria-selected="false"><span class="d">2026.09</span><span class="m"></span><span class="nm">V4.1-Flash</span><span class="tp">非对称结构，主力接棒</span></button>
    </div>
    <!-- 版本卡片 -->
    <article class="vcard on" data-v="v1">
      <div class="vhead"><h4>DeepSeek LLM 67B</h4><span class="vd">2024.01</span><span class="tag">第一代 · 密集架构</span></div>
      <p class="cols" style="color:var(--ink-2)">这一代还是「常规路线」：一个 67B 的密集（Dense）模型，每一层的前馈网络对所有词都全量计算。它的价值在于把训练数据和评测体系搭起来，SFT 与 RL 对齐流程也是在这一代成型的。</p>
      <div class="vgrid">
        <div class="vcell"><span class="k">Architecture</span><span class="v">标准 Transformer + 密集 FFN；没有 MoE，没有压缩注意力。</span></div>
        <div class="vcell"><span class="k">Training</span><span class="v">大规模多语预训练 → SFT → RL 对齐三段式，确立了后续所有版本的训练骨架。</span></div>
        <div class="vcell"><span class="k">Performance</span><span class="v">同尺寸下表现扎实，但每个词都要跑满 67B 参数，推理成本高。</span></div>
        <div class="vcell"><span class="k">Why it matters</span><span class="v">它是后面所有「省算力」创新的<b>基准线</b>：V2 报告里的「缓存降低 93.3%」「训练省 42.5%」都是相对这一代说的。</span></div>
      </div>
    </article>
    <article class="vcard" data-v="v2">
      <div class="vhead"><h4>DeepSeek-V2</h4><span class="vd">2024.05</span><span class="tag acc">MLA + DeepSeekMoE 双创新</span></div>
      <p class="cols" style="color:var(--ink-2)">技术路线的真正转折点。两个创新同时上线：<b>MLA</b> 解决「推理时缓存太占显存」，<b>DeepSeekMoE</b> 解决「训练时每个词都要算全量参数」。一个管推理成本，一个管训练成本，从此成为 DeepSeek 的固定配方。</p>
      <div class="vgrid">
        <div class="vcell"><span class="k">Architecture</span><span class="v">236B 总参数 / 21B 激活；MLA + DeepSeekMoE；支持 128K 上下文。</span></div>
        <div class="vcell"><span class="k">Experts</span><span class="v">每层 2 个共享专家 + 160 个路由专家，每词激活 6 个路由专家；用「设备受限路由」把跨机通信控制在 3 台设备内。</span></div>
        <div class="vcell"><span class="k">Training</span><span class="v">8.1 万亿 token 高质量双语语料；训练成本比上一代省 42.5%。</span></div>
        <div class="vcell"><span class="k">Performance</span><span class="v">KV Cache 降低 <b>93.3%</b>，最大生成吞吐提升 <b>5.76 倍</b>，而只用 21B 激活参数就进入开源第一梯队。</span></div>
      </div>
      <p class="src">来源：DeepSeek-V2 Technical Report（arXiv:2405.04434）</p>
    </article>
    <article class="vcard" data-v="v3">
      <div class="vhead"><h4>DeepSeek-V3</h4><span class="vd">2024.12</span><span class="tag acc">工程效率的标杆</span></div>
      <p class="cols" style="color:var(--ink-2)">沿用 V2 的 MLA + MoE 骨架，把规模推到 671B，然后在<b>工程侧</b>做了三件别人没做成的事：用 FP8 低精度训练万亿级模型、把 MoE 负载均衡从「加惩罚项」改成「调偏置」、以及让每个位置同时预测未来多个词。</p>
      <div class="vgrid">
        <div class="vcell"><span class="k">Architecture</span><span class="v">671B 总参数 / 37B 激活；61 层、隐层 7168、128 个注意力头；每层 1 个共享专家 + 256 个路由专家，激活 8 个。</span></div>
        <div class="vcell"><span class="k">Training</span><span class="v">14.8 万亿 token；<b>FP8 混合精度</b>首次在超大规模模型上验证成功；DualPipe 双向流水线把计算与通信几乎完全重叠；全程 <b>2.788M H800 卡时</b>。</span></div>
        <div class="vcell"><span class="k">Stability</span><span class="v">报告明确写到：整个训练过程没有出现不可恢复的 loss 尖峰，也没有回滚过任何一次。</span></div>
        <div class="vcell"><span class="k">Performance</span><span class="v">综合成绩超越同期所有开源模型，接近头部闭源模型；MATH-500 达 90.2%，Codeforces 百分位 51.6。</span></div>
      </div>
      <p class="src">来源：DeepSeek-V3 Technical Report（arXiv:2412.19437）</p>
    </article>
    <article class="vcard" data-v="r1">
      <div class="vhead"><h4>DeepSeek-R1 / R1-Zero</h4><span class="vd">2025.01</span><span class="tag acc">纯强化学习涌现推理</span></div>
      <p class="cols" style="color:var(--ink-2)">这一代改变了「后训练」的叙事。<b>R1-Zero</b> 完全不使用监督微调，直接对基座做大规模强化学习，模型自己长出了长思维链、自我检查与反思行为；训练中甚至出现「等一下，我重新想想」的<b>顿悟时刻</b>。</p>
      <div class="vgrid">
        <div class="vcell"><span class="k">Algorithm</span><span class="v">GRPO：同一道题采样一组回答，用组内相对分数当基线，省掉与策略模型同规模的价值网络。</span></div>
        <div class="vcell"><span class="k">Reward</span><span class="v">只用两类<b>规则奖励</b>：答案正确性（数学题按格式核对、代码跑测试用例）+ 格式奖励（把思考过程放进指定标签）。刻意不用神经网络奖励模型。</span></div>
        <div class="vcell"><span class="k">Training</span><span class="v">R1 四阶段：冷启动 SFT → 推理导向 RL → 拒绝采样 + 监督微调（约 80 万条，其中约 60 万推理 / 20 万通用）→ 全场景 RL。</span></div>
        <div class="vcell"><span class="k">Performance</span><span class="v">AIME 2024 的 pass@1 从 15.6% 升到 71.0%（多数投票 86.7%）；R1 正式版 AIME 79.8%、MATH-500 97.3%、Codeforces 2030 分左右。</span></div>
      </div>
      <p class="src">来源：DeepSeek-R1 Technical Report（arXiv:2501.12948）；同时开源了 1.5B~70B 六个蒸馏模型。</p>
    </article>
    <article class="vcard" data-v="v30324">
      <div class="vhead"><h4>DeepSeek-V3-0324</h4><span class="vd">2025.03</span><span class="tag">编程强化 · 部署友好</span></div>
      <p class="cols" style="color:var(--ink-2)">一次以「实用」为目标的中期更新：重点打磨编程与数学推理，同时把部署门槛降下来，使模型可以在消费级硬件上运行。这次更新后，它一度成为开源模型中的第一梯队选手。</p>
      <div class="vgrid">
        <div class="vcell"><span class="k">变化重点</span><span class="v">代码与数学能力提升；体积与量化方案优化，支持在个人设备本地部署。</span></div>
        <div class="vcell"><span class="k">意义</span><span class="v">标志着 DeepSeek 的迭代节奏从「发大版本」转向「小步快跑 + 逐项补强」。</span></div>
      </div>
    </article>
    <article class="vcard" data-v="v31">
      <div class="vhead"><h4>DeepSeek-V3.1 / V3.1-Terminus</h4><span class="vd">2025.08 / 2025.09</span><span class="tag">双模式统一</span></div>
      <p class="cols" style="color:var(--ink-2)">把「推理模型」和「通用模型」合并成一个模型：同一个权重，通过开关切换<b>思考模式（Thinking）</b>与<b>非思考模式（Non-Thinking）</b>。上下文扩展到 128K。随后 9 月的 Terminus 版本重点修掉了中英文混杂的输出问题，并优化了代码 Agent 与搜索 Agent 的表现。</p>
      <div class="vgrid">
        <div class="vcell"><span class="k">Architecture</span><span class="v">延续 V3 的 MLA + MoE，不做结构性改动。</span></div>
        <div class="vcell"><span class="k">Training</span><span class="v">在统一模型上做双模式后训练，让「快回答」与「深思考」共用一套知识。</span></div>
        <div class="vcell"><span class="k">Performance</span><span class="v">同一模型在两种模式下都可用，是后续「推理强度可调」的雏形。</span></div>
        <div class="vcell"><span class="k">官方口径</span><span class="v">Terminus 版本「缓解中英文混杂问题，优化 Code Agent 与 Search Agent 表现」。</span></div>
      </div>
      <p class="src">来源：DeepSeek 官方动态（2025-09-22 版本更新说明）</p>
    </article>
    <article class="vcard" data-v="v32exp">
      <div class="vhead"><h4>DeepSeek-V3.2-Exp</h4><span class="vd">2025.09.29</span><span class="tag acc">DSA 稀疏注意力登场</span></div>
      <p class="cols" style="color:var(--ink-2)">引入 <b>DeepSeek Sparse Attention（DSA）</b>：先用一个轻量的「闪电索引器」给所有历史词打分，再只挑分数最高的一小部分真正参与注意力计算。长文本场景下训练与推理效率同时提升，官方同步把 API 价格下调 50% 以上。</p>
      <div class="vgrid">
        <div class="vcell"><span class="k">Architecture</span><span class="v">在 MLA 之上叠加细粒度稀疏选择，注意力只作用于被选中的子集。</span></div>
        <div class="vcell"><span class="k">Training</span><span class="v">稀疏模式需要专门训练，让索引器学会「挑谁看」。</span></div>
        <div class="vcell"><span class="k">Performance</span><span class="v">长上下文成本显著下降，官方称 API 价格降低 50% 以上。</span></div>
        <div class="vcell"><span class="k">注意</span><span class="v">这是「实验版」（Exp），主要目的是把新架构放到真实流量里验证。</span></div>
      </div>
      <p class="src">来源：DeepSeek 官方动态（2025-09-29）</p>
    </article>
    <article class="vcard" data-v="v32">
      <div class="vhead"><h4>DeepSeek-V3.2 正式版</h4><span class="vd">2025.12.01</span><span class="tag acc">思考融入工具使用</span></div>
      <p class="cols" style="color:var(--ink-2)">V3.2 与 V3.2-Speciale 同时发布，重点强化 Agent 能力，并首次把「思考」直接融入工具调用流程 —— 模型可以在调用工具的过程中持续推理，而不是先想完再动手。同系列的 Speciale 是长思考增强版，结合了定理证明模型的能力。</p>
      <div class="vgrid">
        <div class="vcell"><span class="k">Architecture</span><span class="v">沿用 V3.2-Exp 的 DSA 稀疏注意力架构。</span></div>
        <div class="vcell"><span class="k">Training</span><span class="v">面向 Agent 场景的后训练数据与奖励设计，强化多轮工具使用。</span></div>
        <div class="vcell"><span class="k">Performance</span><span class="v">官方称推理能力全球领先，并在 IMO、CMO、ICPC、IOI 等竞赛中取得金牌级成绩。</span></div>
        <div class="vcell"><span class="k">意义</span><span class="v">从「答题模型」转向「干活的模型」，为 V4 的 Agent 定位铺路。</span></div>
      </div>
      <p class="src">来源：DeepSeek 官方动态（2025-12-01）</p>
    </article>
    <article class="vcard" data-v="ctx1m">
      <div class="vhead"><h4>1M 上下文（静默升级）</h4><span class="vd">2026.02.11</span><span class="tag">上下文规模跃迁</span></div>
      <p class="cols" style="color:var(--ink-2)">通过一次没有发布会、没有技术报告的静默更新，把网页端与 App 的上下文处理能力提升到 100 万 token 量级，知识截止时间同步更新。这个节点很适合用来提醒自己：<b>不是所有变化都会以论文形式出现</b>。</p>
      <div class="vgrid">
        <div class="vcell"><span class="k">变化</span><span class="v">上下文从 128K 级别提升到 1M（百万）级别。</span></div>
        <div class="vcell"><span class="k">口径提醒</span><span class="v">静默更新，官方未发布配套技术报告，具体实现细节未公开披露。</span></div>
      </div>
      <p class="src">来源：官方服务端更新（媒体广泛报道，2026-02-11）</p>
    </article>
    <article class="vcard" data-v="v4">
      <div class="vhead"><h4>DeepSeek-V4 预览版</h4><span class="vd">2026.04.24</span><span class="tag acc">百万上下文成为标配</span></div>
      <p class="cols" style="color:var(--ink-2)">全新系列：<b>V4-Pro</b>（1.6T 总参 / 49B 激活）与 <b>V4-Flash</b>（284B / 13B），两者都原生支持 1M 上下文，并同步开源。核心是<b>混合注意力架构</b>：把「压缩后再看」的注意力与「稀疏挑选」的注意力组合起来，让百万级上下文的计算与显存开销大幅回落。</p>
      <div class="vgrid">
        <div class="vcell"><span class="k">Architecture</span><span class="v">延续 DeepSeekMoE 与 MTP；新增混合注意力（CSA + HCA，辅以滑动窗口分支）；<b>mHC</b> 流形约束超连接强化残差连接。</span></div>
        <div class="vcell"><span class="k">Optimizer</span><span class="v">采用 <b>Muon</b> 优化器替换大部分模块的 AdamW，追求更快收敛与更好稳定性。</span></div>
        <div class="vcell"><span class="k">Efficiency</span><span class="v">在 1M 上下文下，V4-Pro 单 token 推理 FLOPs 仅为 V3.2 的 <b>27%</b>，KV Cache 仅为 <b>10%</b>。</span></div>
        <div class="vcell"><span class="k">Training</span><span class="v">预训练超过 32 万亿 token；后训练为两阶段 —— 先分别培养领域专家（SFT + GRPO 强化学习），再用同策略蒸馏合并成一个统一模型。</span></div>
      </div>
      <p class="src">来源：DeepSeek-V4 Technical Report（arXiv:2606.19348）、官方 V4 预览版发布说明</p>
    </article>
    <article class="vcard" data-v="v40813">
      <div class="vhead"><h4>DeepSeek-V4-Pro-0813（正式版）</h4><span class="vd">2026.08</span><span class="tag">面向 Agent 的正式版</span></div>
      <p class="cols" style="color:var(--ink-2)">V4-Pro 的正式发布检查点，取代此前的预览版，重点强化 Agent 相关能力，并附加了推测解码模块用于加速。</p>
      <div class="vgrid">
        <div class="vcell"><span class="k">Architecture</span><span class="v">保持预览版的模型结构，附加推测解码（speculative decoding）模块。</span></div>
        <div class="vcell"><span class="k">Performance</span><span class="v">Agent 类评测大幅提升，官方定位为「面向 Agent 工作的主力模型」。</span></div>
        <div class="vcell"><span class="k">口径提醒</span><span class="v">该检查点细节在第三方追踪站点有汇总，建议以官方模型卡与 API 文档为准。</span></div>
      </div>
    </article>
    <article class="vcard" data-v="v41">
      <div class="vhead"><h4>DeepSeek-V4.1-Flash</h4><span class="vd">2026.09.10</span><span class="tag acc">最新发布 · 非对称结构</span></div>
      <p class="cols" style="color:var(--ink-2)">截至本手册数据截止日（2026-09-21）的最新发布模型。它换上了全新结构：<b>Causal Encoder-Decoder（CED）</b>，输入与输出不对称 —— 读入时只激活 8B 参数，生成时激活 16B。因为 Agent 任务往往是「读一大段、写一点点」，这种不对称直接把成本压了下来。官方同时宣布 V4.1-Flash 在性能、费用、速度、总用时上全面超越 V4-Pro，并计划逐步下线 V4-Pro —— 不过这项下线在 9 月 12 日前后被官方收回：变更日志改为「应广大用户需求，2026 年 9 月 14 日之后继续提供 DeepSeek V4 Pro 的 API 服务，计费方式不变」。截至 2026-09-21，V4-Pro 仍在正常服务，V4.1-Pro 也仍未发布。</p>
      <div class="vgrid">
        <div class="vcell"><span class="k">Architecture</span><span class="v">552B 参数 MoE；40 层 Transformer 拆成 20 层因果编码器 + 20 层解码器；解码器的全局 KV 由编码器最终隐状态投影而来，不再逐层自产；原生多模态视觉理解（DeepSeek-ViT 视觉编码器 + 2D-RoPE + 3×3 像素重排）。</span></div>
        <div class="vcell"><span class="k">Experts</span><span class="v">每层 1 个共享专家 + 384 个路由专家，每词激活 6 个路由专家。</span></div>
        <div class="vcell"><span class="k">Efficiency</span><span class="v">CSA2（每层在 Full / Reindex / Reuse 三种模式间静态分工，共享主 KV 与索引）+ 层次化稀疏索引器 + FP4 主 KV 缓存，把全局 KV 压到 <b>890 字节 / token</b>，约为 V4-Flash 的 1/4；持久化缓存存储约为其 1/8；相比初代模型 KV Cache 缩小 <b>437 倍</b>。</span></div>
        <div class="vcell"><span class="k">Memory</span><span class="v">引入 <b>Engram 条件记忆</b>模块（196B 参数，按 token 查表稀疏访问），是在 MoE 之外新加的一条稀疏轴。</span></div>
        <div class="vcell"><span class="k">Training</span><span class="v">从零训练于 45 万亿 token 的多模态语料；稀疏注意力先在 64K 序列长度训练，再在 34 万亿 token 处扩展到 1M；后训练沿用 SFT → RL → 同策略蒸馏，改动主要在数据管线。</span></div>
        <div class="vcell"><span class="k">Performance</span><span class="v">官方称在 agentic 基准上超越 V4-Pro；第三方报道其 DeepSWE v1.1 得分 74.2（对比 Claude Opus 5 为 74.0、GPT-5.6 Sol 为 73.0）。</span></div>
      </div>
      <div class="box finding">
        <span class="t">官方主动披露的局限</span>
        <p>技术报告同时指出：新架构带来了尚未充分测试的鲁棒性边界 —— 稀疏选择出错、以及近似状态重建，可能在极端情况下削弱能力，尤其是在超长上下文的稀疏检索和缓存恢复的衔接处。官方表示将做进一步压力测试。<b>读技术报告时，作者自己写的 limitation 一节，往往比结论更有价值。</b></p>
      </div>
      <p class="src">来源：DeepSeek 官方发布页（2026-09-10）、《DeepSeek-V4.1-Flash 技术报告》（Hugging Face 公开）</p>
    </article>
  </div>
  <h3 id="p1-arch"><span class="n">1.2</span>架构主线图解：每一代在改什么</h3>
  <div class="cols"><p>把 12 个版本压缩成六个「架构世代」。注意阅读顺序：从左到右不是模型变大，而是<b>同一个矛盾被换了一种解法</b>。</p></div>
  <figure>
    <svg viewBox="0 0 1180 470" role="img" aria-label="DeepSeek 架构演进主线图">
      <defs>
        <linearGradient id="gacc" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0" stop-color="#2f6fb8"/><stop offset="1" stop-color="#1b4f8a"/>
        </linearGradient>
      </defs>
      <!-- 主轨 -->
      <line x1="40" y1="86" x2="1140" y2="86" stroke="#d8dde3" stroke-width="2"/>
      <line x1="40" y1="86" x2="1140" y2="86" stroke="url(#gacc)" stroke-width="2" stroke-dasharray="6 0" opacity=".5"/>
      <!-- 6 个世代节点 -->
      <g font-family="ui-monospace, monospace">
        <g>
          <circle cx="112" cy="86" r="9" fill="#fff" stroke="#5b6570" stroke-width="3"/>
          <text x="112" y="58" text-anchor="middle" font-size="12" fill="#17181a" font-weight="600">① 密集</text>
          <text x="112" y="112" text-anchor="middle" font-size="10.5" fill="#5b6570">2024.01</text>
          <text x="112" y="130" text-anchor="middle" font-size="10.5" fill="#8b949e">Dense 67B</text>
        </g>
        <g>
          <circle cx="310" cy="86" r="9" fill="#2f6fb8" stroke="#fff" stroke-width="3"/>
          <text x="310" y="58" text-anchor="middle" font-size="12" fill="#17181a" font-weight="600">② 压缩+稀疏</text>
          <text x="310" y="112" text-anchor="middle" font-size="10.5" fill="#5b6570">2024.05</text>
          <text x="310" y="130" text-anchor="middle" font-size="10.5" fill="#8b949e">MLA + MoE</text>
        </g>
        <g>
          <circle cx="508" cy="86" r="9" fill="#2f6fb8" stroke="#fff" stroke-width="3"/>
          <text x="508" y="58" text-anchor="middle" font-size="12" fill="#17181a" font-weight="600">③ 低精度+多步</text>
          <text x="508" y="112" text-anchor="middle" font-size="10.5" fill="#5b6570">2024.12</text>
          <text x="508" y="130" text-anchor="middle" font-size="10.5" fill="#8b949e">FP8 · MTP · DualPipe</text>
        </g>
        <g>
          <circle cx="706" cy="86" r="9" fill="#2f6fb8" stroke="#fff" stroke-width="3"/>
          <text x="706" y="58" text-anchor="middle" font-size="12" fill="#17181a" font-weight="600">④ 纯强化学习</text>
          <text x="706" y="112" text-anchor="middle" font-size="10.5" fill="#5b6570">2025.01</text>
          <text x="706" y="130" text-anchor="middle" font-size="10.5" fill="#8b949e">GRPO · 规则奖励</text>
        </g>
        <g>
          <circle cx="904" cy="86" r="9" fill="#2f6fb8" stroke="#fff" stroke-width="3"/>
          <text x="904" y="58" text-anchor="middle" font-size="12" fill="#17181a" font-weight="600">⑤ 稀疏注意力</text>
          <text x="904" y="112" text-anchor="middle" font-size="10.5" fill="#5b6570">2025.09</text>
          <text x="904" y="130" text-anchor="middle" font-size="10.5" fill="#8b949e">DSA</text>
        </g>
        <g>
          <circle cx="1092" cy="86" r="11" fill="#17181a" stroke="#2f6fb8" stroke-width="3"/>
          <text x="1092" y="58" text-anchor="middle" font-size="12" fill="#17181a" font-weight="600">⑥ 混合+非对称</text>
          <text x="1092" y="112" text-anchor="middle" font-size="10.5" fill="#5b6570">2026.04→09</text>
          <text x="1092" y="130" text-anchor="middle" font-size="10.5" fill="#8b949e">CSA/HCA · CED · mHC</text>
        </g>
      </g>
      <!-- 结构缩略图 -->
      <g>
        <!-- ① Dense -->
        <rect x="62" y="176" width="100" height="196" rx="10" fill="#fbfcfd" stroke="#d8dde3"/>
        <text x="112" y="198" text-anchor="middle" font-size="10" fill="#5b6570" font-family="ui-monospace, monospace">Transformer × L</text>
        <rect x="76" y="210" width="72" height="30" rx="5" fill="#eaeef2" stroke="#d8dde3"/>
        <text x="112" y="229" text-anchor="middle" font-size="10" fill="#5b6570" font-family="ui-monospace, monospace">Attention</text>
        <rect x="76" y="248" width="72" height="42" rx="5" fill="#eaeef2" stroke="#d8dde3"/>
        <text x="112" y="265" text-anchor="middle" font-size="10" fill="#5b6570" font-family="ui-monospace, monospace">FFN</text>
        <text x="112" y="280" text-anchor="middle" font-size="9.5" fill="#a8611f" font-family="ui-monospace, monospace">全量计算</text>
        <rect x="76" y="298" width="72" height="30" rx="5" fill="#eaeef2" stroke="#d8dde3"/>
        <text x="112" y="317" text-anchor="middle" font-size="10" fill="#5b6570" font-family="ui-monospace, monospace">× 61 层</text>
        <text x="112" y="352" text-anchor="middle" font-size="10.5" fill="#5b6570">每个词都跑满</text>
        <text x="112" y="366" text-anchor="middle" font-size="10.5" fill="#a8611f">成本最高</text>
        <!-- ② MLA + MoE -->
        <rect x="260" y="176" width="100" height="196" rx="10" fill="#fbfcfd" stroke="#d8dde3"/>
        <rect x="274" y="196" width="72" height="38" rx="5" fill="#eef3f8" stroke="#2f6fb8"/>
        <text x="310" y="212" text-anchor="middle" font-size="10" fill="#1b4f8a" font-family="ui-monospace, monospace">MLA</text>
        <text x="310" y="226" text-anchor="middle" font-size="9" fill="#1b4f8a" font-family="ui-monospace, monospace">缓存↓93%</text>
        <rect x="274" y="242" width="72" height="66" rx="5" fill="#eef3f8" stroke="#2f6fb8"/>
        <text x="310" y="258" text-anchor="middle" font-size="10" fill="#1b4f8a" font-family="ui-monospace, monospace">MoE FFN</text>
        <g fill="#2f6fb8">
          <circle cx="288" cy="272" r="3.4"/><circle cx="302" cy="272" r="3.4"/><circle cx="316" cy="272" r="3.4"/><circle cx="330" cy="272" r="3.4"/>
          <circle cx="288" cy="286" r="3.4" opacity=".3"/><circle cx="302" cy="286" r="3.4" opacity=".3"/><circle cx="316" cy="286" r="3.4" opacity=".3"/><circle cx="330" cy="286" r="3.4" opacity=".3"/>
        </g>
        <text x="310" y="302" text-anchor="middle" font-size="9" fill="#1b4f8a" font-family="ui-monospace, monospace">实心=被激活</text>
        <text x="310" y="352" text-anchor="middle" font-size="10.5" fill="#5b6570">大容量，小计算</text>
        <text x="310" y="366" text-anchor="middle" font-size="10.5" fill="#0f7b5f">训练省 42.5%</text>
        <!-- ③ FP8 -->
        <rect x="458" y="176" width="100" height="196" rx="10" fill="#fbfcfd" stroke="#d8dde3"/>
        <rect x="472" y="196" width="72" height="34" rx="5" fill="#eaeef2" stroke="#d8dde3"/>
        <text x="508" y="217" text-anchor="middle" font-size="10" fill="#5b6570" font-family="ui-monospace, monospace">FP8 计算</text>
        <rect x="472" y="238" width="72" height="34" rx="5" fill="#eaeef2" stroke="#d8dde3"/>
        <text x="508" y="259" text-anchor="middle" font-size="10" fill="#5b6570" font-family="ui-monospace, monospace">DualPipe</text>
        <rect x="472" y="280" width="72" height="34" rx="5" fill="#eaeef2" stroke="#d8dde3"/>
        <text x="508" y="301" text-anchor="middle" font-size="10" fill="#5b6570" font-family="ui-monospace, monospace">MTP 多头预测</text>
        <text x="508" y="352" text-anchor="middle" font-size="10.5" fill="#5b6570">工程换效率</text>
        <text x="508" y="366" text-anchor="middle" font-size="10.5" fill="#0f7b5f">2.79M 卡时</text>
        <!-- ④ GRPO -->
        <rect x="656" y="176" width="100" height="196" rx="10" fill="#fbfcfd" stroke="#d8dde3"/>
        <text x="706" y="196" text-anchor="middle" font-size="10" fill="#5b6570" font-family="ui-monospace, monospace">同一问题 × G</text>
        <g>
          <rect x="672" y="206" width="16" height="16" rx="3" fill="#eaeef2"/><rect x="692" y="206" width="16" height="16" rx="3" fill="#eaeef2"/>
          <rect x="712" y="206" width="16" height="16" rx="3" fill="#eaeef2"/><rect x="732" y="206" width="16" height="16" rx="3" fill="#eaeef2"/>
        </g>
        <rect x="672" y="232" width="76" height="30" rx="5" fill="#eef3f8" stroke="#2f6fb8"/>
        <text x="710" y="251" text-anchor="middle" font-size="9.5" fill="#1b4f8a" font-family="ui-monospace, monospace">组内比高低</text>
        <rect x="672" y="270" width="76" height="30" rx="5" fill="#eef3f8" stroke="#2f6fb8"/>
        <text x="710" y="289" text-anchor="middle" font-size="9.5" fill="#1b4f8a" font-family="ui-monospace, monospace">优势 → 更新</text>
        <text x="706" y="352" text-anchor="middle" font-size="10.5" fill="#5b6570">不教步骤，只给激励</text>
        <text x="706" y="366" text-anchor="middle" font-size="10.5" fill="#0f7b5f">推理能力涌现</text>
        <!-- ⑤ DSA -->
        <rect x="854" y="176" width="100" height="196" rx="10" fill="#fbfcfd" stroke="#d8dde3"/>
        <text x="904" y="196" text-anchor="middle" font-size="10" fill="#5b6570" font-family="ui-monospace, monospace">全部历史词</text>
        <g fill="#d8dde3">
          <circle cx="868" cy="212" r="3"/><circle cx="880" cy="212" r="3"/><circle cx="892" cy="212" r="3"/><circle cx="904" cy="212" r="3"/><circle cx="916" cy="212" r="3"/><circle cx="928" cy="212" r="3"/><circle cx="940" cy="212" r="3"/>
        </g>
        <path d="M866,232 L942,232" stroke="#2f6fb8" stroke-width="1.6" marker-end="url(#ar)"/>
        <text x="904" y="246" text-anchor="middle" font-size="9" fill="#1b4f8a" font-family="ui-monospace, monospace">闪电索引器打分</text>
        <g fill="#2f6fb8">
          <circle cx="904" cy="266" r="4.5"/><circle cx="922" cy="266" r="4.5"/><circle cx="886" cy="266" r="4.5"/>
        </g>
        <text x="904" y="288" text-anchor="middle" font-size="9" fill="#1b4f8a" font-family="ui-monospace, monospace">只看 Top-K</text>
        <text x="904" y="352" text-anchor="middle" font-size="10.5" fill="#5b6570">从平方级到近似线性</text>
        <text x="904" y="366" text-anchor="middle" font-size="10.5" fill="#0f7b5f">API 降价 50%+</text>
        <!-- ⑥ Hybrid -->
        <rect x="1042" y="176" width="100" height="196" rx="10" fill="#17181a" stroke="#17181a"/>
        <text x="1092" y="198" text-anchor="middle" font-size="10" fill="#eef3f8" font-family="ui-monospace, monospace">三条注意力分支</text>
        <rect x="1056" y="208" width="72" height="24" rx="5" fill="#1b4f8a"/>
        <text x="1092" y="224" text-anchor="middle" font-size="9.5" fill="#fff" font-family="ui-monospace, monospace">CSA 压缩稀疏</text>
        <rect x="1056" y="238" width="72" height="24" rx="5" fill="#2f6fb8"/>
        <text x="1092" y="254" text-anchor="middle" font-size="9.5" fill="#fff" font-family="ui-monospace, monospace">HCA 重度压缩</text>
        <rect x="1056" y="268" width="72" height="24" rx="5" fill="#7C92FF"/>
        <text x="1092" y="284" text-anchor="middle" font-size="9.5" fill="#fff" font-family="ui-monospace, monospace">SWA 局部窗口</text>
        <rect x="1056" y="300" width="72" height="26" rx="5" fill="none" stroke="#2f6fb8"/>
        <text x="1092" y="317" text-anchor="middle" font-size="9.5" fill="#eef3f8" font-family="ui-monospace, monospace">mHC / Muon</text>
        <text x="1092" y="352" text-anchor="middle" font-size="10.5" fill="#eef3f8">1M 上下文标配</text>
        <text x="1092" y="366" text-anchor="middle" font-size="10.5" fill="#7C92FF">FLOPs 27% · KV 10%</text>
      </g>
      <!-- 底部说明 -->
      <text x="40" y="412" font-size="11.5" fill="#5b6570" font-family="ui-monospace, monospace">主线：能力↑ 的同时，让「每个 token 的真实计算量」持续↓</text>
      <text x="40" y="434" font-size="11.5" fill="#8b949e" font-family="ui-monospace, monospace">③④ 之后，DeepSeek 的竞争维度从「架构创新」扩展到「训练工程 + 后训练范式」；⑤⑥ 又回到架构，但目标是长上下文经济性。</text>
      <text x="40" y="456" font-size="11.5" fill="#8b949e" font-family="ui-monospace, monospace">标注口径：②相对初代密集模型；⑥相对 V3.2。均为官方报告披露值。</text>
    </svg>
    <figcaption>图 1-1 · DeepSeek 架构演进主线（按官方报告披露口径绘制）</figcaption>
  </figure>
  <h3 id="p1-table"><span class="n">1.3</span>关键参数对照：把数字排成一行行</h3>
  <div class="cols"><p>这张表是全文最值得反复回看的一张。注意两点：<b>「激活」那一列的增长远慢于「总量」</b>；<b>上下文在变长的同时，KV Cache 在变小</b>。</p></div>
  <div class="tbl-wrap">
    <table>
      <thead><tr>
        <th>版本</th><th>时间</th><th class="ds-"">总参数</th><th class="ds-"">激活参数</th><th class="ds-"">预训练规模</th><th>注意力机制</th><th>标志性变化</th>
      </tr></thead>
      <tbody>
        <tr><td class="nm">DeepSeek LLM</td><td class="mono">2024.01</td><td class="ds-"">67B</td><td class="ds-"">67B（全量）</td><td class="ds-"">约 2T</td><td>标准 MHA</td><td>密集架构基线</td></tr>
        <tr><td class="nm">DeepSeek-V2</td><td class="mono">2024.05</td><td class="ds-"">236B</td><td class="ds-"">21B</td><td class="ds-"">8.1T</td><td class="hi">MLA</td><td>缓存↓93.3%、吞吐↑5.76×</td></tr>
        <tr><td class="nm">DeepSeek-V3</td><td class="mono">2024.12</td><td class="ds-"">671B</td><td class="ds-"">37B</td><td class="ds-"">14.8T</td><td>MLA</td><td>FP8 训练 · MTP · 无损负载均衡</td></tr>
        <tr><td class="nm">DeepSeek-R1</td><td class="mono">2025.01</td><td class="ds-"">671B</td><td class="ds-"">37B</td><td class="ds-"">沿用 V3 基座</td><td>MLA</td><td>纯 RL 涌现推理；蒸馏 1.5B–70B</td></tr>
        <tr><td class="nm">V3-0324</td><td class="mono">2025.03</td><td class="ds-"">671B</td><td class="ds-"">37B</td><td class="ds-"">—</td><td>MLA</td><td>编程强化、可本地部署</td></tr>
        <tr><td class="nm">V3.1</td><td class="mono">2025.08</td><td class="ds-"">671B</td><td class="ds-"">37B</td><td class="ds-"">—</td><td>MLA</td><td>思考 / 非思考双模式，128K 上下文</td></tr>
        <tr><td class="nm">V3.2-Exp</td><td class="mono">2025.09</td><td class="ds-"">671B</td><td class="ds-"">37B</td><td class="ds-"">—</td><td class="hi">MLA + DSA</td><td>细粒度稀疏注意力，API 降价 50%+</td></tr>
        <tr><td class="nm">V3.2 / Speciale</td><td class="mono">2025.12</td><td class="ds-"">671B</td><td class="ds-"">37B</td><td class="ds-"">—</td><td>MLA + DSA</td><td>思考融入工具使用，竞赛金牌级</td></tr>
        <tr><td class="nm">V4-Pro</td><td class="mono">2026.04</td><td class="ds-"">1.6T</td><td class="ds-"">49B</td><td class="ds-"">&gt;32T</td><td class="hi">混合注意力 CSA+HCA</td><td>1M 上下文标配；mHC；Muon</td></tr>
        <tr><td class="nm">V4-Flash</td><td class="mono">2026.04</td><td class="ds-"">284B</td><td class="ds-"">13B</td><td class="ds-"">&gt;32T</td><td>混合注意力</td><td>经济版，推理能力接近 Pro</td></tr>
        <tr><td class="nm">V4.1-Flash</td><td class="mono">2026.09</td><td class="ds-"">552B</td><td class="ds-""><span class="hi">8B 输入 / 16B 输出</span></td><td class="ds-"">45T（多模态）</td><td class="hi">CED + CSA2 + FP4 KV</td><td>KV 890 字节/token，接棒主力</td></tr>
      </tbody>
    </table>
  </div>
  <p class="src">表格依据：各版本官方技术报告与官方发布页。部分版本的预训练规模官方未单独披露，标「—」。「激活参数」对 V4.1-Flash 而言是分阶段口径（读入 / 生成）。</p>
  <h3 id="p1-read"><span class="n">1.4</span>三个真正的转折点</h3>
  <div class="grid3">
    <div class="card">
      <span class="tag acc">转折一 · 2024.05</span>
      <h4 style="margin-top:10px">把「省算力」正式变成技术路线</h4>
      <p style="font-size:14.8px;color:var(--ink-2);margin:0">在所有人比参数规模时，V2 用 MLA + MoE 证明了一件事：<b>容量和计算量可以解耦</b>。总量 236B 保留大容量，激活 21B 控制成本。此后「激活参数」成为行业通用指标，而不只是总参数。</p>
    </div>
    <div class="card">
      <span class="tag acc">转折二 · 2025.01</span>
      <h4 style="margin-top:10px">把「教模型」换成「给激励」</h4>
      <p style="font-size:14.8px;color:var(--ink-2);margin:0">R1-Zero 不用任何监督数据、只给正确性与格式两种规则奖励，模型自己长出反思与验证行为。这提示：<b>复杂能力不一定需要被演示，也可以被激励出来</b>。这是后训练范式的分水岭。</p>
    </div>
    <div class="card">
      <span class="tag acc">转折三 · 2026.04→09</span>
      <h4 style="margin-top:10px">竞争重心移到「上下文经济性」</h4>
      <p style="font-size:14.8px;color:var(--ink-2);margin:0">当上下文拉到 100 万 token，瓶颈不再是模型多聪明，而是<b>读这么长的文本要花多少显存和算力</b>。于是有了混合注意力、CED 非对称结构、FP4 缓存 —— 全部围绕同一件事：让长上下文变得便宜。</p>
    </div>
  </div>
</section>
<!-- ============================ 第二部分 ============================ -->
<section class="sec reveal" id="p2">
  <div class="sec-head">
    <span class="sec-"">02</span>
    <h2>横向：与 GPT、Claude 的异同</h2>
    <span class="sub">COMPARISON · 2026.09 快照</span>
  </div>
  <div class="cols">
    <p>做横向对比时，最容易犯的错是「把各家的跑分直接摆在一起比大小」。不同厂商的评测设置（思考强度、是否用工具、采样次数、提示词模板）都不一样，<b>分数只有落在同一张表里才有可比性</b>。所以下面先看一张「谁的评测表」，再看结构性差异。</p>
  </div>
  <h3 id="p2-table"><span class="n">2.1</span>能力与成本对照（截至 2026.09）</h3>
  <div class="tbl-wrap">
    <table>
      <thead><tr>
        <th>模型</th><th>厂商</th><th class="ds-"">规模</th><th class="ds-"">上下文</th><th>权重</th><th>训练 / 对齐方法（官方口径）</th><th class="ds-"">参考单价<br>输入 / 输出（每百万 token）</th>
      </tr></thead>
      <tbody>
        <tr>
          <td class="nm">DeepSeek-V4.1-Flash</td><td>深度求索</td><td class="ds-"">552B<br><span style="color:var(--ink-4)">激活 8B/16B</span></td><td class="ds-"">1M</td>
          <td><span class="tag acc">MIT 开源</span></td>
          <td>MoE + 低精度训练；SFT → RL（GRPO）→ 同策略蒸馏；后训练改动主要在数据管线</td>
          <td class="ds-""><span class="hi">$0.15 / $0.60</span><br><span style="color:var(--ink-4)">缓存命中 $0.003</span></td>
        </tr>
        <tr>
          <td class="nm">DeepSeek-V4-Pro</td><td>深度求索</td><td class="ds-"">1.6T<br><span style="color:var(--ink-4)">激活 49B</span></td><td class="ds-"">1M</td>
          <td><span class="tag acc">MIT 开源</span></td>
          <td>混合注意力 + mHC + Muon；两阶段后训练（领域专家培养 → 统一蒸馏）</td>
          <td class="ds-"">$0.66 / $1.98<br><span style="color:var(--ink-4)">闲时价</span></td>
        </tr>
        <tr>
          <td class="nm">GPT-5.4</td><td>OpenAI</td><td class="ds-"">未公开</td><td class="ds-"">1M<br><span style="color:var(--ink-4)">Codex 实验性</span></td>
          <td><span class="tag">闭源</span></td>
          <td>推理模型通过强化学习训练「先想再答」；合并代码专用模型为主线；安全侧有 Preparedness 框架</td>
          <td class="ds-"">$2.50 / $15.00</td>
        </tr>
        <tr>
          <td class="nm">GPT-5.6 Sol</td><td>OpenAI</td><td class="ds-"">未公开</td><td class="ds-"">—</td>
          <td><span class="tag">闭源</span></td>
          <td>同系列更高配置档；缓存输入单独计价</td>
          <td class="ds-"">$4.00 / $20.00<br><span style="color:var(--ink-4)">缓存命中 $0.40</span></td>
        </tr>
        <tr>
          <td class="nm">Claude Opus 5</td><td>Anthropic</td><td class="ds-"">未公开</td><td class="ds-"">—</td>
          <td><span class="tag">闭源</span></td>
          <td>预训练 + 人类反馈强化学习 + AI 反馈强化学习 + 面向角色与宪法的人工训练；按 ASL 分级做部署决策</td>
          <td class="ds-"">$5.00 / $25.00<br><span style="color:var(--ink-4)">缓存命中 $0.50</span></td>
        </tr>
        <tr>
          <td class="nm">Gemini 3.1 Pro</td><td>Google</td><td class="ds-"">未公开</td><td class="ds-"">—</td>
          <td><span class="tag">闭源</span></td>
          <td>未披露细节；作为高配置档参与各家横向评测</td>
          <td class="ds-"">—</td>
        </tr>
      </tbody>
    </table>
  </div>
  <div class="box finding">
    <span class="t">横向对比的诚实前提</span>
    <p>① 三家都不公开「参数量、预训练数据量、训练卡时」这类底层数字，只有 DeepSeek 逐版本披露 —— 这不是 DeepSeek 更透明，而是<b>开源权重迫使它必须把训练细节写清楚</b>，否则没有人能复现。② 价格是<b>会变动的商业策略</b>，且缓存命中率、峰谷时段会显著改变实际账单，下面第 2.3 节的测算器比单价表更有参考价值。</p>
  </div>
  <h3 id="p2-chart"><span class="n">2.2</span>同一张评测表里的成绩</h3>
  <div class="cols">
    <p>下面这张图的数字全部来自 <b>DeepSeek-V4 技术报告的横向评测表</b> —— 也就是说，这是 DeepSeek 自己选定的对手、自己设定的评测条件。读竞品报告时，时刻记住这一点：<b>它是一份「我方视角」的证据</b>。点击切换指标，看不同能力维度上的座次如何变化。</p>
  </div>
  <div class="lab">
    <div class="lab-head">
      <span class="lt">Experiment 01</span>
      <span class="lh">同一评测表下的能力对比</span>
      <span class="tag">数据源：DeepSeek-V4 技术报告</span>
    </div>
    <div class="lab-body">
      <div class="pills" id="benchPills" role="group" aria-label="选择评测指标"></div>
      <p id="benchDesc" style="font-size:13.5px;color:var(--ink-3);margin:16px 0 14px;line-height:1.6"></p>
      <div class="bars" id="benchBars"></div>
      <div class="legend">
        <span><i style="background:#1b4f8a"></i>DeepSeek</span>
        <span><i style="background:#8b949e"></i>其他厂商</span>
        <span><i style="background:#d8dde3"></i>该项未报告</span>
      </div>
      <p class="src" style="margin-top:14px">思考强度设置：DS-V4-Pro-Max / Claude Opus-4.6-Max / GPT-5.4-xHigh / Gemini-3.1-Pro-High。括号内为百分比或得分，横条长度按该项满分或最高分归一化。</p>
    </div>
  </div>
  <h3 id="p2-cost"><span class="n">2.3</span>成本结构：差距不在单价，在「缓存命中」</h3>
  <div class="cols">
    <p>这是三家最本质的差异，也是 Agent 时代最容易被忽略的一点。当一个 Agent 反复读取同一份代码仓库、同一套工具说明、同一段系统提示时，<b>它读的大部分 token 是可以命中缓存的</b>。所以真正决定账单的，是「缓存命中的那一档多少钱」。</p>
    <p>DeepSeek 把缓存命中的价格压到了输入价的 <b>1/50</b>（$0.003 vs $0.15）；而 Claude Opus 5 的缓存命中价是 $0.50，相对输入价（$5）是 1/10。同样的复用场景，账单差异会被放大到十倍以上。拖动下面的滑块，用你自己的场景算一遍。</p>
  </div>
  <div class="lab">
    <div class="lab-head">
      <span class="lt">Experiment 02</span>
      <span class="lh">一次 Agent 请求的账单测算</span>
      <span class="tag">单位：美元 / 百万 token</span>
    </div>
    <div class="lab-body">
      <div class="lab-ctrl">
        <label for="costIn">输入 token</label>
        <input type="range" id="costIn" min="2000" max="900000" step="2000" value="400000">
        <span class="mono" id="costInV" style="font-size:13px;color:var(--accent);min-width:84px"></span>
      </div>
      <div class="lab-ctrl">
        <label for="costHit">缓存命中率</label>
        <input type="range" id="costHit" min="0" max="100" step="1" value="80">
        <span class="mono" id="costHitV" style="font-size:13px;color:var(--accent);min-width:84px"></span>
      </div>
      <div class="lab-ctrl">
        <label for="costOut">输出 token</label>
        <input type="range" id="costOut" min="200" max="60000" step="200" value="6000">
        <span class="mono" id="costOutV" style="font-size:13px;color:var(--accent);min-width:84px"></span>
      </div>
      <div class="bars" id="costBars"></div>
      <div class="readout" style="margin-top:18px" id="costNote"></div>
    </div>
  </div>
  <div class="cols">
    <p>把上表读成一句话：<b>DeepSeek 卖的从来不是「最聪明」，而是「单位智能的价格」</b>。三家在能力上的差距通常在几个百分点到十几个百分点之间，而在价格上可以差一到两个数量级。这也解释了为什么 V4.1-Flash 一发布就敢宣布「全面超越 V4-Pro 并接替主力」——在 Agent 场景里，成本本身就是能力的一部分。（「接替主力」这一步随后被官方收回：V4-Pro 至今仍在服务，见 1.1 时间线与附录 B。）</p>
  </div>
  <h3 id="p2-method"><span class="n">2.4</span>训练方法的异同：三段式下的三种取舍</h3>
  <div class="tbl-wrap">
    <table>
      <thead><tr><th style="width:120px">环节</th><th>DeepSeek</th><th>GPT 系列</th><th>Claude 系列</th></tr></thead>
      <tbody>
        <tr>
          <td class="nm">预训练</td>
          <td>MoE 稀疏激活 + 低精度（FP8 → FP4）训练；语料规模与卡时逐版本公开（V3 为 14.8T token / 2.788M H800 卡时；V4 超过 32T）</td>
          <td>未公开数据规模与算力；强调数据过滤与安全分类器</td>
          <td>未公开数据规模与算力；公开说明使用 AWS / GCP 云算力与 PyTorch / JAX / Triton 框架</td>
        </tr>
        <tr>
          <td class="nm">监督微调</td>
          <td>SFT 数据大量由模型自己生成（拒绝采样），并明确披露数量级（R1 阶段约 80 万条）</td>
          <td>人类示范与模型生成数据混合，细节未公开</td>
          <td>人类偏好数据 + 标注承包商数据 + 用户可选加入的数据</td>
        </tr>
        <tr>
          <td class="nm">强化学习</td>
          <td><b>规则奖励为主</b>：数学按答案核对、代码跑测试用例、格式检查；刻意避免易被「刷分」的神经网络奖励模型</td>
          <td>通过强化学习训练推理行为（学会先思考、试不同策略、识别自己的错误）</td>
          <td><b>RLHF + RLAIF</b>：人类反馈与 AI 反馈并用，配合「宪法」定义角色与价值观</td>
        </tr>
        <tr>
          <td class="nm">能力合并</td>
          <td>把多个领域专家模型经<b>同策略蒸馏</b>合并回一个统一模型（V4 起明确为两阶段范式）</td>
          <td>把代码专用模型的能力合并进主线模型（GPT-5.4 起）</td>
          <td>以单一系列模型覆盖不同档位（Opus / Sonnet / Haiku）</td>
        </tr>
        <tr>
          <td class="nm">安全与发布</td>
          <td>以技术报告披露局限为主，发布偏工程节奏</td>
          <td>发布 System Card，覆盖生物化学、网络安全等高能力风险缓解</td>
          <td>发布 System Card + 负责任扩展政策（RSP）分级（如 ASL-3），部署前做能力评估</td>
        </tr>
        <tr>
          <td class="nm">开放性</td>
          <td><span class="hi">开源权重（MIT）</span>，可自部署、可商用</td>
          <td>闭源，仅 API</td>
          <td>闭源，仅 API</td>
        </tr>
      </tbody>
    </table>
  </div>
  <div class="box note">
    <span class="t">一句话总结异同</span>
    <b>相同的是骨架</b>：三家都是「预训练 → 指令微调 → 强化学习对齐」的三段式，都在做推理模型的测试时扩展，都在往 Agent 与工具使用方向投入。<b>不同的是取舍</b>：DeepSeek 押注「可验证的规则奖励 + 极致工程效率 + 开源」，OpenAI 押注「统一模型 + 高能力档位 + 安全缓解框架」，Anthropic 押注「人类与 AI 反馈混合 + 价值观对齐 + 分级负责任部署」。
  </div>
  <h3 id="p2-verdict"><span class="n">2.5</span>谁更强，谁更省：把结论落到场景上</h3>
  <figure>
    <svg viewBox="0 0 1180 400" role="img" aria-label="能力与成本示意象限图">
      <defs>
        <linearGradient id="qg" x1="0" y1="1" x2="1" y2="0">
          <stop offset="0" stop-color="#0f7b5f" stop-opacity=".07"/>
          <stop offset="1" stop-color="#1b4f8a" stop-opacity=".07"/>
        </linearGradient>
      </defs>
      <rect x="90" y="30" width="1010" height="300" fill="url(#qg)" stroke="#d8dde3"/>
      <line x1="595" y1="30" x2="595" y2="330" stroke="#d8dde3" stroke-dasharray="4 4"/>
      <line x1="90" y1="180" x2="1100" y2="180" stroke="#d8dde3" stroke-dasharray="4 4"/>
      <text x="118" y="52" font-size="12" fill="#5b6570" font-family="ui-monospace, monospace">高能力 · 低成本（性价比区）</text>
      <text x="1068" y="52" text-anchor="end" font-size="12" fill="#5b6570" font-family="ui-monospace, monospace">高能力 · 高成本（旗舰区）</text>
      <text x="118" y="320" font-size="12" fill="#5b6570" font-family="ui-monospace, monospace">低能力 · 低成本（轻量区）</text>
      <text x="1068" y="320" text-anchor="end" font-size="12" fill="#5b6570" font-family="ui-monospace, monospace">低能力 · 高成本</text>
      <text x="595" y="368" text-anchor="middle" font-size="12" fill="#5b6570" font-family="ui-monospace, monospace">单位成本 →</text>
      <text x="46" y="184" font-size="12" fill="#5b6570" font-family="ui-monospace, monospace" transform="rotate(-90 46 184)">综合能力 →</text>
      <!-- DeepSeek V4.1-Flash -->
      <circle cx="188" cy="112" r="15" fill="#1b4f8a"/>
      <text x="188" y="117" text-anchor="middle" font-size="11" fill="#fff" font-family="ui-monospace, monospace">DS</text>
      <text x="188" y="152" text-anchor="middle" font-size="12.5" fill="#17181a" font-weight="600">V4.1-Flash</text>
      <text x="188" y="168" text-anchor="middle" font-size="10.5" fill="#5b6570" font-family="ui-monospace, monospace">Agent 强 / 知识中等</text>
      <!-- DeepSeek V4-Pro -->
      <circle cx="300" cy="96" r="15" fill="#2f6fb8"/>
      <text x="300" y="101" text-anchor="middle" font-size="11" fill="#fff" font-family="ui-monospace, monospace">DS</text>
      <text x="300" y="136" text-anchor="middle" font-size="12.5" fill="#17181a" font-weight="600">V4-Pro</text>
      <text x="300" y="152" text-anchor="middle" font-size="10.5" fill="#5b6570" font-family="ui-monospace, monospace">开源旗舰</text>
      <!-- Gemini -->
      <circle cx="700" cy="72" r="16" fill="#8b949e"/>
      <text x="700" y="77" text-anchor="middle" font-size="11" fill="#fff" font-family="ui-monospace, monospace">G</text>
      <text x="700" y="112" text-anchor="middle" font-size="12.5" fill="#17181a" font-weight="600">Gemini 3.1 Pro</text>
      <text x="700" y="128" text-anchor="middle" font-size="10.5" fill="#5b6570" font-family="ui-monospace, monospace">知识面最广</text>
      <!-- GPT -->
      <circle cx="880" cy="88" r="16" fill="#5b6570"/>
      <text x="880" y="93" text-anchor="middle" font-size="11" fill="#fff" font-family="ui-monospace, monospace">G</text>
      <text x="880" y="128" text-anchor="middle" font-size="12.5" fill="#17181a" font-weight="600">GPT-5.4</text>
      <text x="880" y="144" text-anchor="middle" font-size="10.5" fill="#5b6570" font-family="ui-monospace, monospace">工具与终端 Agent 强</text>
      <!-- Claude -->
      <circle cx="1010" cy="104" r="16" fill="#a8611f"/>
      <text x="1010" y="109" text-anchor="middle" font-size="11" fill="#fff" font-family="ui-monospace, monospace">C</text>
      <text x="1010" y="144" text-anchor="middle" font-size="12.5" fill="#17181a" font-weight="600">Claude Opus 5</text>
      <text x="1010" y="160" text-anchor="middle" font-size="10.5" fill="#5b6570" font-family="ui-monospace, monospace">长程检索 / 对齐</text>
      <text x="90" y="386" font-size="11" fill="#8b949e" font-family="ui-monospace, monospace">示意图：横轴为综合单位成本量级，纵轴为综合能力量级，位置为定性判断，不代表精确排名。</text>
    </svg>
    <figcaption>图 2-1 · 能力—成本象限（示意）</figcaption>
  </figure>
  <div class="grid3">
    <div class="card">
      <h4 style="margin-top:0"><span class="tag acc">要省钱</span></h4>
      <p style="font-size:14.8px;color:var(--ink-2);margin:0 0 8px">优先 DeepSeek V4.1-Flash。Agent 类、重复读取长上下文、批量代码任务上单位成本优势最大，且权重开源可自部署。</p>
    </div>
    <div class="card">
      <h4 style="margin-top:0"><span class="tag">要最强知识</span></h4>
      <p style="font-size:14.8px;color:var(--ink-2);margin:0 0 8px">Gemini 3.1 Pro 与 GPT 高配档在事实问答、研究生级科学题上仍有明显优势。DeepSeek 在 SimpleQA 这类纯知识题上相对偏弱。</p>
    </div>
    <div class="card">
      <h4 style="margin-top:0"><span class="tag">要长程与安全</span></h4>
      <p style="font-size:14.8px;color:var(--ink-2);margin:0 0 8px">百万级检索（MRCR 1M）Claude Opus 4.6 一档表现突出；若部署场景对安全分级与合规有硬要求，Claude 的发布流程更成熟。</p>
    </div>
  </div>
  <div class="box finding">
    <span class="t">必须写明的边界</span>
    <p>本节的对比数字来自 <b>DeepSeek 官方报告的评测表</b>，以及各家公开的定价页与系统卡。厂商自测分数天然有主场优势；价格随时可能调整；能效与真实任务成功率还会受你的 Agent 框架影响。做技术选型时，请以「你自己仓库上的成本 / 完成率」为最终依据。</p>
  </div>
</section>
<!-- ============================ 第三部分 ============================ -->
<section class="sec reveal" id="p3">
  <div class="sec-head">
    <span class="sec-"">03</span>
    <h2>纵深：核心概念逐个拆开</h2>
    <span class="sub">MECHANISMS · 20+ CONCEPTS</span>
  </div>
  <div class="cols">
    <p>这一部分是全篇的主菜。每个概念都按同一个模板展开：<b>① 它要解决什么问题 → ② 不这么做会怎样 → ③ 具体怎么做（含公式） → ④ 动手试一试 → ⑤ 需要的前置知识</b>。公式不会全部展开推导，但每一个符号都会告诉你它在说什么。</p>
    <p>建议读法：先读「问题」和「直觉」两段，跳过公式往下读实验；等实验看懂了，再回头读公式，你会发现公式其实是实验的数学缩写。</p>
  </div>
  <!-- ---------- 3.1 注意力与 KV Cache ---------- -->
  <h3 id="c-attn"><span class="n">3.1</span>注意力与 KV Cache：一切成本的源头</h3>
  <div class="cols">
    <p><b>要解决的问题。</b>语言里的词义是相互决定的。「苹果」在「我吃了一个苹果」和「苹果发布了新手机」里完全是两个意思。注意力机制就是让每个词去「看」上下文里所有其他词，然后按相关度加权求和，得到自己的新表示。</p>
    <p><b>核心公式。</b>每个词会被投影成三个向量：Query（我要找什么）、Key（我是什么）、Value（我携带的信息）。相关度就是 Query 与 Key 的点积：</p>
  </div>
  <div class="card" style="font-family:var(--mono);font-size:15px;line-height:2.1;overflow-x:auto">
    <div>Attention(Q, K, V) = softmax( Q·K<sup>T</sup> / &radic;d<sub>k</sub> ) · V</div>
    <div style="color:var(--ink-3);font-size:12.5px;font-family:var(--sans);line-height:1.7;margin-top:6px">
      读法：把每个词的 Query 与所有词的 Key 做点积（越像分数越高），除以 &radic;d<sub>k</sub> 防止数值过大，softmax 归一化成权重，再对 Value 加权求和。除以 &radic;d<sub>k</sub> 的原因：维度越高点积越大，不缩放会让 softmax 变得极端，梯度消失。
    </div>
  </div>
  <div class="cols" style="margin-top:20px">
    <p><b>不这么做会怎样。</b>生成文本是一个词一个词往外吐的。生成第 1000 个词时，前 999 个词的 Key 和 Value 都必须重新算一遍 —— 而它们的值其实没变过。这个重复计算是纯浪费，于是有了 <b>KV Cache</b>：把已经算过的 K、V 存下来，新词只算自己的 Q，然后去查缓存。</p>
    <p><b>于是成本转移了。</b>计算省了，但显存被吃掉。<b>缓存大小与上下文长度成正比</b>，与层数、注意力头数、每个头的维度成正比：</p>
  </div>
  <div class="card" style="font-family:var(--mono);font-size:14.5px;line-height:2;overflow-x:auto">
    <div>KV 缓存字节数 = 序列长度 × 层数 × 头数 × 头维度 × 2(K和V) × 每元素字节数</div>
    <div style="color:var(--ink-3);font-size:12.5px;font-family:var(--sans);line-height:1.7;margin-top:6px">
      以 V3 的结构（61 层 × 128 头 × 头维度 128，BF16 即 2 字节）粗算：每个 token 的缓存约 <b>4 MB</b>。100 万 token 就是 <b>约 4 TB</b> —— 这就是「长上下文很贵」的数学根源。
    </div>
  </div>
  <div class="lab">
    <div class="lab-head">
      <span class="lt">Experiment 03</span>
      <span class="lh">KV Cache 到底有多占地方</span>
      <span class="tag">结构粗算 · 非精确测量</span>
    </div>
    <div class="lab-body">
      <div class="lab-ctrl">
        <label for="kvSlider">上下文长度</label>
        <input type="range" id="kvSlider" min="4" max="1024" step="4" value="128">
        <span class="mono" id="kvSliderV" style="font-size:13px;color:var(--accent);min-width:96px"></span>
      </div>
      <div class="bars" id="kvBars"></div>
      <div class="readout" style="margin-top:18px" id="kvOut"></div>
      <p class="src" style="margin-top:14px">
        计算口径（逐项透明）：以「61 层 / 128 头 / 头维度 128 / BF16」作为密集注意力参照，每个 token 约 3.99 MB；
        MLA 按 V2/V3 配置（每层潜向量 512 维 + 解耦 RoPE 的 64 维）约 70 KB；
        V4.1-Flash 的 <b>890 字节 / token</b> 取自官方技术报告披露值。缓存的增长是线性的，所以上下文翻倍，账单翻倍。
      </p>
    </div>
  </div>
  <div class="box note">
    <span class="t">参考知识</span>
    <p>想补基础，按这个顺序读：<b>《Attention Is All You Need》(2017)</b> 理解注意力本身 → <b>KV Cache / MQA / GQA</b> 理解缓存优化谱系 → 再回到 DeepSeek-V2 报告读 MLA。跳过第一步直接读 MLA 公式，会不知道它在优化什么。</p>
  </div>
  <!-- ---------- 3.2 MLA ---------- -->
  <h3 id="c-mla"><span class="n">3.2</span>MLA 多头潜在注意力：把缓存压成一个「潜在向量」</h3>
  <div class="cols">
    <p><b>要解决的问题。</b>上一节的缓存公式里，有四个乘数可以被优化：层数（结构决定，动不了）、头数、头维度、以及「存 K 和 V 两份」。已有的 GQA / MQA 方案是靠<b>让多个头共享同一份 K、V</b> 来省缓存，省得多但会损失表达能力 —— 相当于用「减少分辨率」换空间。</p>
    <p><b>MLA 的思路完全不同：不减少头，而是压缩内容。</b>它不直接存 K、V，而是把 K 和 V 联合投影到一个低维的「潜在向量」c 上，只缓存 c。用的时候再把 c 上投影（升维）还原成各头的 K、V。</p>
  </div>
  <div class="card" style="font-family:var(--mono);font-size:14.5px;line-height:2.1;overflow-x:auto">
    <div>压缩（缓存这个）：  c<sub>t</sub> = W<sup>DKV</sup> · h<sub>t</sub></div>
    <div>还原（用时算）：  k<sub>C</sub> = W<sup>UK</sup> · c<sub>t</sub>&nbsp;&nbsp;&nbsp;&nbsp; v<sub>C</sub> = W<sup>UV</sup> · c<sub>t</sub></div>
    <div style="color:var(--ink-3);font-size:12.5px;font-family:var(--sans);line-height:1.7;margin-top:6px">
      h<sub>t</sub> 是该位置的隐状态（维度 7168），c<sub>t</sub> 是压缩后的潜向量（维度 512）。缓存量从「头数 × 头维度」降到「512」这一维，这就是 93.3% 这个数字的来源。
    </div>
  </div>
  <div class="cols" style="margin-top:20px">
    <p><b>但压缩会撞上一个硬钉子：位置编码。</b>RoPE（旋转位置编码）的原理是给 Q、K 乘一个随位置旋转的角度，让模型感知「谁在前谁在后」。问题在于：如果 K 存的是压缩后的 c，那么位置信息就没法在还原之后再干净地加回去了 —— 旋转操作和低秩压缩不满足交换律。</p>
    <p><b>解决办法叫「解耦 RoPE」。</b>把 Key 拆成两路：一路走压缩还原（负责内容），另一路单独保留一小段维度（64 维）专门承载位置旋转（负责顺序）。两路拼起来用。代价是多了 64 维的缓存，但换来了压缩与位置编码的兼容 —— 这个细节是 MLA 能真正落地而不只是纸上谈兵的关键。</p>
  </div>
  <figure>
    <svg viewBox="0 0 1180 330" role="img" aria-label="MLA 压缩与还原流程">
      <text x="40" y="30" font-size="12" fill="#5b6570" font-family="ui-monospace, monospace">传统 MHA：每个头都要缓存自己的 K 和 V</text>
      <rect x="40" y="44" width="500" height="112" rx="10" fill="#fbfcfd" stroke="#d8dde3"/>
      <text x="60" y="70" font-size="12" fill="#5b6570" font-family="ui-monospace, monospace">隐状态 h（7168 维）</text>
      <g>
        <rect x="60" y="82" width="66" height="52" rx="6" fill="#eaeef2" stroke="#d8dde3"/>
        <text x="93" y="104" text-anchor="middle" font-size="10.5" fill="#5b6570" font-family="ui-monospace, monospace">K₁ 128</text>
        <text x="93" y="120" text-anchor="middle" font-size="10.5" fill="#5b6570" font-family="ui-monospace, monospace">V₁ 128</text>
        <rect x="136" y="82" width="66" height="52" rx="6" fill="#eaeef2" stroke="#d8dde3"/>
        <text x="169" y="104" text-anchor="middle" font-size="10.5" fill="#5b6570" font-family="ui-monospace, monospace">K₂ 128</text>
        <text x="169" y="120" text-anchor="middle" font-size="10.5" fill="#5b6570" font-family="ui-monospace, monospace">V₂ 128</text>
        <rect x="212" y="82" width="66" height="52" rx="6" fill="#eaeef2" stroke="#d8dde3"/>
        <text x="245" y="104" text-anchor="middle" font-size="10.5" fill="#5b6570" font-family="ui-monospace, monospace">K₃ 128</text>
        <text x="245" y="120" text-anchor="middle" font-size="10.5" fill="#5b6570" font-family="ui-monospace, monospace">V₃ 128</text>
        <text x="300" y="112" font-size="14" fill="#8b949e">···</text>
        <rect x="330" y="82" width="66" height="52" rx="6" fill="#eaeef2" stroke="#d8dde3"/>
        <text x="363" y="104" text-anchor="middle" font-size="10.5" fill="#5b6570" font-family="ui-monospace, monospace">K₁₂₈</text>
        <text x="363" y="120" text-anchor="middle" font-size="10.5" fill="#5b6570" font-family="ui-monospace, monospace">V₁₂₈</text>
      </g>
      <text x="470" y="112" font-size="12" fill="#a8611f" font-family="ui-monospace, monospace">每 token ≈ 4 MB</text>
      <text x="640" y="30" font-size="12" fill="#1b4f8a" font-family="ui-monospace, monospace">MLA：只缓存一个压缩潜向量 + 一小段位置维度</text>
      <rect x="640" y="44" width="500" height="112" rx="10" fill="#F5F7FF" stroke="#2f6fb8"/>
      <text x="660" y="70" font-size="12" fill="#1b4f8a" font-family="ui-monospace, monospace">隐状态 h（7168 维）</text>
      <path d="M700,80 L700,96" stroke="#2f6fb8" stroke-width="1.6"/>
      <rect x="660" y="96" width="120" height="42" rx="6" fill="#1b4f8a"/>
      <text x="720" y="114" text-anchor="middle" font-size="10.5" fill="#fff" font-family="ui-monospace, monospace">潜向量 c 512</text>
      <text x="720" y="130" text-anchor="middle" font-size="9.5" fill="#C9D3FF" font-family="ui-monospace, monospace">← 缓存这个</text>
      <rect x="790" y="96" width="72" height="42" rx="6" fill="#fff" stroke="#2f6fb8" stroke-dasharray="3 3"/>
      <text x="826" y="114" text-anchor="middle" font-size="10.5" fill="#1b4f8a" font-family="ui-monospace, monospace">位置 64</text>
      <text x="826" y="130" text-anchor="middle" font-size="9.5" fill="#1b4f8a" font-family="ui-monospace, monospace">解耦 RoPE</text>
      <path d="M880,117 L916,117" stroke="#5b6570" stroke-width="1.6" marker-end="url(#ar)"/>
      <text x="930" y="112" font-size="10.5" fill="#5b6570" font-family="ui-monospace, monospace">上投影还原</text>
      <text x="930" y="130" font-size="10.5" fill="#5b6570" font-family="ui-monospace, monospace">各头 K、V</text>
      <text x="1090" y="117" text-anchor="end" font-size="12" fill="#0f7b5f" font-family="ui-monospace, monospace">每 token ≈ 70 KB</text>
      <line x1="40" y1="188" x2="1140" y2="188" stroke="#eaeef2"/>
      <text x="40" y="214" font-size="12" fill="#17181a" font-family="ui-monospace, monospace" font-weight="600">关键权衡</text>
      <text x="40" y="240" font-size="12" fill="#5b6570" font-family="ui-monospace, monospace">· 与 MQA / GQA 的「减少头数」路线相反：MLA 保住了全部 128 个头的表达能力，只压缩存储内容。</text>
      <text x="40" y="262" font-size="12" fill="#5b6570" font-family="ui-monospace, monospace">· 代价：每次读缓存都要做一次升维矩阵乘法，多了一点计算量 —— 用算力换显存，而显存是长上下文的真瓶颈。</text>
      <text x="40" y="284" font-size="12" fill="#5b6570" font-family="ui-monospace, monospace">· 官方数据：DeepSeek-V2 相对第一代，KV Cache 降低 93.3%，最大生成吞吐提升 5.76 倍。</text>
      <text x="40" y="312" font-size="11" fill="#8b949e" font-family="ui-monospace, monospace">注：维度数值取自 V2 / V3 公开配置；不同版本与层数的具体取值以对应技术报告为准。</text>
    </svg>
    <figcaption>图 3-1 · MLA 的低秩联合压缩与解耦 RoPE</figcaption>
  </figure>
  <!-- ---------- 3.3 MoE ---------- -->
  <h3 id="c-moe"><span class="n">3.3</span>MoE 稀疏专家：参数很大，但每次只用一点点</h3>
  <div class="cols">
    <p><b>要解决的问题。</b>模型越大学得越多，但每个词都跑完整模型，成本会线性上涨。能不能「保留大模型的容量，却只支付小模型的计算」？</p>
    <p><b>做法。</b>把一个巨大的前馈网络（FFN）拆成许多个小专家（Expert），前面放一个「路由 / 分诊台」（Router）。每个 token 进来时，Router 算出它和每个专家的匹配分数，只把 token 发给分数最高的 K 个专家，最后把这 K 个专家的输出加权求和。</p>
  </div>
  <div class="card" style="font-family:var(--mono);font-size:14.5px;line-height:2.1;overflow-x:auto">
    <div>h<sub>out</sub> = SharedExpert(h) + &Sigma;<sub>i &isin; TopK</sub> g<sub>i</sub> · Expert<sub>i</sub>(h)</div>
    <div>g<sub>i</sub> = softmax(score<sub>i</sub>)&nbsp;&nbsp;&nbsp;&nbsp;TopK = 分数最高的 K 个专家（V3 里 K = 8，候选 256）</div>
    <div style="color:var(--ink-3);font-size:12.5px;font-family:var(--sans);line-height:1.7;margin-top:6px">
      <b>共享专家</b>：所有 token 都会经过，用来兜住通用能力；<b>路由专家</b>：按需调用，承担专业化分工。这就是「容量大、计算小」的实现方式。
    </div>
  </div>
  <div class="lab">
    <div class="lab-head">
      <span class="lt">Experiment 04</span>
      <span class="lh">亲自当一次路由器</span>
      <span class="tag">256 专家 · 激活 8 个</span>
    </div>
    <div class="lab-body">
      <div id="moeWrap">
        <div>
          <div id="moeGrid" aria-hidden="true"></div>
          <div class="readout" style="margin-top:14px" id="moeOut"></div>
        </div>
        <div>
          <div class="lab-ctrl" style="margin-bottom:12px">
            <button class="btn" id="moeBtn">送入一个 token</button>
            <button class="btn ghost" id="moeReset">重置</button>
          </div>
          <label style="display:flex;gap:10px;align-items:flex-start;font-size:13.5px;color:var(--ink-2);line-height:1.6;cursor:pointer">
            <input type="checkbox" id="moeBalance" checked style="margin-top:5px;width:18px;height:18px;accent-color:var(--accent)">
            <span>启用「无辅助损失」负载均衡偏置<br><span style="color:var(--ink-3);font-size:12.5px">打开后，过载专家的打分会被压低、闲置专家的打分被抬高，让分工更均匀</span></span>
          </label>
          <div class="bars" style="margin-top:16px" id="moeLoad"></div>
        </div>
      </div>
      <p class="src" style="margin-top:16px">
        蓝框 = 共享专家（始终参与）；深蓝 = 本次被激活的路由专家；砖红 = 累计过载；浅色 = 闲置。
        真实模型里 Router 的分数由可学习的权重算出，这里用随机分数演示「选择」与「均衡」这两件事。
      </p>
    </div>
  </div>
  <div class="box note">
    <span class="t">参考知识</span>
    <p>MoE 的鼻祖是 1991 年的 <b>Adaptive Mixtures of Local Experts</b>；把它搬进 Transformer 的关键工作是 <b>Switch Transformer（2021）</b> 与 <b>GShard（2020）</b>。DeepSeekMoE 的两个原创点是<b>「细粒度专家切分」</b>（把专家切得更小更多，组合更灵活）与<b>「共享专家隔离」</b>（把通用知识从路由专家里独立出来，减少冗余学习）。</p>
  </div>
  <!-- ---------- 3.4 负载均衡 ---------- -->
  <h3 id="c-balance"><span class="n">3.4</span>负载均衡：MoE 最隐蔽的坑</h3>
  <div class="cols">
    <p><b>要解决的问题。</b>MoE 里有个恶性循环：某几个专家一开始被选中得多 → 收到的训练信号多 → 变得更强 → 以后更容易被选中。最后 256 个专家里可能只有十几个在工作，其余全部荒废。学术上叫<b>路由崩塌（routing collapse）</b>。</p>
    <p><b>传统解法：加惩罚项。</b>在损失函数里加一个「负载不均衡惩罚」（辅助损失 / auxiliary loss），谁被选得太频繁就罚谁。但这就引入了新矛盾：<b>你为了均衡而扭曲了模型的优化目标，均衡得越好，语言建模本身可能越差</b>。这是一种「用主任务性能换工程稳定」的交易。</p>
    <p><b>DeepSeek-V3 的解法：不碰损失函数，改调一个偏置。</b>给每个专家维护一个偏置项 b<sub>i</sub>，这个偏置<b>只参与路由决策，不参与最终输出的加权</b>：</p>
  </div>
  <div class="card" style="font-family:var(--mono);font-size:14.5px;line-height:2.1;overflow-x:auto">
    <div>路由打分：  s<sub>i</sub> = score(h, e<sub>i</sub>) + b<sub>i</sub>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;（按 s 排序选 TopK）</div>
    <div>输出加权：  g<sub>i</sub> = softmax( score(h, e<sub>i</sub>) )&nbsp;&nbsp;（注意这里<b>没有</b> b<sub>i</sub>）</div>
    <div>偏置更新：  过载 → b<sub>i</sub> 减小&nbsp;&nbsp;·&nbsp;&nbsp;闲置 → b<sub>i</sub> 增大（一个很小的步长，持续微调）</div>
    <div style="color:var(--ink-3);font-size:12.5px;font-family:var(--sans);line-height:1.7;margin-top:6px">
      妙处在于：偏置<b>只在「选谁」时起作用，不进入「算多少」</b>。所以它既能纠正负载倾斜，又完全不改变模型的优化目标 —— 这就是「无辅助损失」的含义。回到 Experiment 04，把上面的开关关掉，连续送几十个 token，你会亲眼看到两个专家垄断全部流量。
    </div>
  </div>
  <!-- ---------- 3.5 MTP ---------- -->
  <h3 id="c-mtp"><span class="n">3.5</span>MTP 多 token 预测：逼模型想得远一点</h3>
  <div class="cols">
    <p><b>要解决的问题。</b>标准语言模型的训练目标是「预测下一个词」。这个任务有个副作用：模型只需要盯着眼前一步就能拿到不错的奖励，不必规划更远的语义结构，学到的表示偏「局部」。</p>
    <p><b>做法。</b>在训练时给模型加几个额外的预测头，让它在每个位置同时预测未来 2 个、3 个词（V3 用一步 MTP，V4 沿用了这个设计）。这会强迫隐状态里编码更多「接下来会发生什么」的信息。</p>
  </div>
  <figure>
    <svg viewBox="0 0 1180 220" role="img" aria-label="单 token 预测与多 token 预测对比">
      <text x="40" y="28" font-size="12" fill="#5b6570" font-family="ui-monospace, monospace">标准：每个位置只预测下一个词</text>
      <g font-family="ui-monospace, monospace">
        <rect x="40" y="42" width="80" height="36" rx="6" fill="#eaeef2" stroke="#d8dde3"/><text x="80" y="65" text-anchor="middle" font-size="12" fill="#5b6570">h₁</text>
        <rect x="140" y="42" width="80" height="36" rx="6" fill="#eaeef2" stroke="#d8dde3"/><text x="180" y="65" text-anchor="middle" font-size="12" fill="#5b6570">h₂</text>
        <rect x="240" y="42" width="80" height="36" rx="6" fill="#eaeef2" stroke="#d8dde3"/><text x="280" y="65" text-anchor="middle" font-size="12" fill="#5b6570">h₃</text>
        <path d="M120,60 L136,60" stroke="#5b6570" marker-end="url(#ar)"/>
        <path d="M220,60 L236,60" stroke="#5b6570" marker-end="url(#ar)"/>
        <path d="M80,50 L80,28" stroke="#8b949e"/><text x="92" y="24" font-size="11" fill="#5b6570">预测 y₂</text>
        <path d="M180,50 L180,28" stroke="#8b949e"/><text x="192" y="24" font-size="11" fill="#5b6570">预测 y₃</text>
        <path d="M280,50 L280,28" stroke="#8b949e"/><text x="292" y="24" font-size="11" fill="#5b6570">预测 y₄</text>
      </g>
      <text x="470" y="28" font-size="12" fill="#1b4f8a" font-family="ui-monospace, monospace">MTP：每个位置同时预测未来多个词</text>
      <g font-family="ui-monospace, monospace">
        <rect x="470" y="42" width="80" height="36" rx="6" fill="#eef3f8" stroke="#2f6fb8"/><text x="510" y="65" text-anchor="middle" font-size="12" fill="#1b4f8a">h₁</text>
        <rect x="570" y="42" width="80" height="36" rx="6" fill="#eef3f8" stroke="#2f6fb8"/><text x="610" y="65" text-anchor="middle" font-size="12" fill="#1b4f8a">h₂</text>
        <rect x="670" y="42" width="80" height="36" rx="6" fill="#eef3f8" stroke="#2f6fb8"/><text x="710" y="65" text-anchor="middle" font-size="12" fill="#1b4f8a">h₃</text>
        <path d="M550,60 L566,60" stroke="#2f6fb8" marker-end="url(#ar)"/>
        <path d="M650,60 L666,60" stroke="#2f6fb8" marker-end="url(#ar)"/>
        <path d="M510,50 L510,28" stroke="#2f6fb8"/><text x="522" y="24" font-size="11" fill="#1b4f8a">预测 y₂</text>
        <path d="M510,42 L600,20" stroke="#2f6fb8" stroke-dasharray="3 3"/><text x="536" y="12" font-size="11" fill="#2f6fb8">同时预测 y₃</text>
        <path d="M610,50 L610,28" stroke="#2f6fb8"/><text x="622" y="24" font-size="11" fill="#1b4f8a">预测 y₃</text>
        <path d="M610,42 L700,20" stroke="#2f6fb8" stroke-dasharray="3 3"/><text x="636" y="12" font-size="11" fill="#2f6fb8">同时预测 y₄</text>
      </g>
      <line x1="820" y1="20" x2="820" y2="200" stroke="#eaeef2"/>
      <text x="850" y="46" font-size="12" fill="#17181a" font-family="ui-monospace, monospace" font-weight="600">一举两得</text>
      <text x="850" y="72" font-size="12" fill="#5b6570" font-family="ui-monospace, monospace">① 训练收益：隐状态被迫编码更长远的信息，</text>
      <text x="864" y="92" font-size="12" fill="#5b6570" font-family="ui-monospace, monospace">报告称多项评测上有可测量的提升。</text>
      <text x="850" y="118" font-size="12" fill="#5b6570" font-family="ui-monospace, monospace">② 推理收益：这些额外预测头可以改造成</text>
      <text x="864" y="138" font-size="12" fill="#5b6570" font-family="ui-monospace, monospace">推测解码（见 3.15），一次验证多个词，</text>
      <text x="864" y="158" font-size="12" fill="#5b6570" font-family="ui-monospace, monospace">直接加快生成速度。</text>
      <text x="850" y="186" font-size="11" fill="#8b949e" font-family="ui-monospace, monospace">注：MTP 模块权重约 14B，不计入主模型 671B。</text>
    </svg>
    <figcaption>图 3-2 · 单 token 预测 vs 多 token 预测</figcaption>
  </figure>
  <!-- ---------- 3.6 精度 ---------- -->
  <h3 id="c-precision"><span class="n">3.6</span>FP8 / FP4 混合精度：用更少的比特算同一件事</h3>
  <div class="cols">
    <p><b>要解决的问题。</b>训练万亿参数模型时，显存和显卡间通信都是瓶颈。而传统训练用 BF16（16 位）存每一个数。如果把参与矩阵乘的数字压缩到 8 位甚至 4 位，显存和带宽立刻减半甚至减到四分之一。</p>
    <p><b>难点在哪。</b>不是「能不能压」，而是「压了之后模型会不会训崩」。低精度的核心风险有两类：<b>动态范围不够</b>（数值太大溢出成无穷，或太小归零）；<b>有效位数不够</b>（相近的两个数被压成同一个值，梯度更新失效）。所以低精度训练的工程细节 —— 分块量化、把累加算在更高精度上、关键层保留高精度 —— 才是真正的壁垒。DeepSeek-V3 是第一个把 FP8 训练在超大规模模型上跑通并公开验证的案例。</p>
  </div>
  <div class="lab">
    <div class="lab-head">
      <span class="lt">Experiment 05</span>
      <span class="lh">精度选择：省了什么，失去什么</span>
      <span class="tag">相对比较 · 定性演示</span>
    </div>
    <div class="lab-body">
      <div class="pills" id="precTabs" role="group" aria-label="选择数值精度"></div>
      <div class="readout" style="margin-top:18px" id="precOut"></div>
      <div class="bars" style="margin-top:18px" id="precBars"></div>
      <p class="src" style="margin-top:14px">
        浮点格式记法：<b>E</b> 表示指数位（决定动态范围），<b>M</b> 表示尾数位（决定精度）。FP8 有两种常用格式 —— E4M3（范围小、精度高，用于前向计算）和 E5M2（范围大、精度低，用于反向传播）。FP4 的主流格式是 E2M1，只有 2 位指数 1 位尾数，必须配合「每 16 个通道共享一个缩放因子」的分块量化才可用。条形长度为相对量级示意，非实测值。
      </p>
    </div>
  </div>
  <div class="box note">
    <span class="t">参考知识</span>
    <p>想深入这一步，需要<b>浮点数表示法</b>（IEEE 754：符号 / 指数 / 尾数）与<b>量化基础</b>（对称量化、逐通道 vs 分块量化、缩放因子与零点）。V4.1-Flash 已把 MoE 专家参数压到 FP4，并对主 KV 缓存在 FP4 下存储（每 16 通道一个 E4M3 缩放因子）—— 也就是说，低精度已经从「训练技巧」变成了「推理基础设施」。</p>
  </div>
</section>
<section class="sec reveal" id="p3b" style="padding-top:0">
  <!-- ---------- 3.7 GRPO ---------- -->
  <h3 id="c-rl"><span class="n">3.7</span>强化学习与 GRPO：不教步骤，只给激励</h3>
  <div class="cols">
    <p><b>要解决的问题。</b>监督微调（SFT）的本质是模仿：人类写出好答案，模型学着复现。但模仿有个天花板 —— <b>模型无法超越示范数据的水平</b>。强化学习（RL）换了个思路：让模型自己尝试多种解法，做对了就加强、做错了就削弱，能力上限由模型自己探索决定。</p>
    <p><b>常规 RLHF 怎么做。</b>先训练一个奖励模型（RM）给答案打分，再用 PPO 算法优化策略。PPO 有个开销：它需要一个「价值网络」（critic）来估计当前状态的平均期望收益，作为判断「这次比平均好多少」的基准 —— 而这个价值网络的大小通常和策略模型相当。对 671B 的模型来说，等于再养一个 671B。</p>
    <p><b>GRPO 的关键简化：用「同组对比」代替「价值网络」。</b>同一道题，让模型采样一组（比如 16 个）答案，把这一组的平均分当作基准。某个答案比组内平均好，它的概率就被推高；比平均差就被压低。基准不用学，直接从组内算出来。</p>
  </div>
  <div class="card" style="font-family:var(--mono);font-size:14.5px;line-height:2.1;overflow-x:auto">
    <div>优势估计：  A<sub>i</sub> = ( r<sub>i</sub> &minus; mean(r<sub>1</sub>…r<sub>G</sub>) ) / std(r<sub>1</sub>…r<sub>G</sub>)</div>
    <div>优化目标：  J &prop; E[ ( &pi;<sub>&theta;</sub>(o<sub>i</sub>|q) / &pi;<sub>old</sub>(o<sub>i</sub>|q) ) · A<sub>i</sub> ] &minus; &beta; · KL(&pi;<sub>&theta;</sub> &#8214; &pi;<sub>ref</sub>)</div>
    <div style="color:var(--ink-3);font-size:12.5px;font-family:var(--sans);line-height:1.7;margin-top:6px">
      第一式是核心：<b>优势 A</b> 就是「这个答案比同组平均好多少」，除以标准差是为了让不同题目的尺度可比。第二式里，括号中的比值是「新旧策略对这个答案的偏好变化」；KL 项是刹车片，防止模型为了刷分而偏离原本的语言能力太远（这也是为什么 R1 的实现保留了 KL 正则）。
    </div>
  </div>
  <div class="lab">
    <div class="lab-head">
      <span class="lt">Experiment 06</span>
      <span class="lh">GRPO 一轮更新长什么样</span>
      <span class="tag">G = 8 · 规则奖励 0/1</span>
    </div>
    <div class="lab-body">
      <div style="display:flex;gap:10px;flex-wrap:wrap;margin-bottom:16px">
        <button class="btn" id="grpoBtn">采样一组回答</button>
        <button class="btn ghost" id="grpoReset">重置累计</button>
      </div>
      <div id="grpoOut"></div>
      <div class="readout" id="grpoStat"></div>
      <div class="bars" style="margin-top:16px" id="grpoBars"></div>
      <p class="src" style="margin-top:14px">
        绿色 = 答对（奖励 1），砖红 = 答错（奖励 0）。算法不需要知道「哪一步想错了」，它只知道最终对错 —— 为了在这类信号下稳定提分，模型自己长出了反思、验证、重试这些行为。这就是 R1-Zero 中「顿悟时刻」的来历。
      </p>
    </div>
  </div>
  <!-- ---------- 3.8 规则奖励 ---------- -->
  <h3 id="c-reward"><span class="n">3.8</span>规则奖励与奖励攻击：为什么不用神经网络打分器</h3>
  <div class="cols">
    <p><b>奖励从哪来，决定了模型往哪跑。</b>奖励有两类来源：<b>可验证的规则</b>（答案对不对、代码能不能过测试、格式对不对）和<b>学习出来的神经奖励模型</b>（模仿人类偏好的打分器）。R1-Zero 刻意只用了前者。</p>
    <p><b>原因是奖励攻击（reward hacking）。</b>只要是学出来的打分器，它就一定有可被利用的漏洞。在成千上万步的 RL 里，模型会以远超人类预期的效率找到这些漏洞 —— 比如输出特别长、特别自信、特别会迎合打分器口味的文字，从而拿到高分，却并没有真正解决问题。而且奖励模型一旦被「攻破」，你还得重新训练它，训练流程变得又贵又复杂。</p>
    <p><b>规则奖励的代价同样明确。</b>它只能用在「有客观对错」的任务上：数学题可以核对答案，代码可以跑测试用例，形式逻辑可以验证。至于写作品评、开放问答、角色扮演这类没有唯一答案的任务，规则打分无能为力 —— <b>这直接把 R1-Zero 的训练分布限制在了可验证领域</b>。所以 R1 的后续阶段引入了生成式奖励模型与人类偏好数据来补上通用能力。</p>
  </div>
  <div class="grid2" style="margin-top:6px">
    <div class="card">
      <h4 style="margin-top:0"><span class="tag">准确性奖励</span></h4>
      <p style="font-size:14.8px;color:var(--ink-2);margin:0">要求模型按指定格式（如把最终答案放进框内）输出，从而可以用规则可靠地核对。代码题则用编译器跑预定义测试用例来产生反馈。</p>
    </div>
    <div class="card">
      <h4 style="margin-top:0"><span class="tag">格式奖励</span></h4>
      <p style="font-size:14.8px;color:var(--ink-2);margin:0">强制模型把思考过程放进指定标签之间。注意它只约束<b>结构</b>，不规定内容 —— 作者刻意避免「要求反思」这类倾向性引导，以便干净地观察模型的自然演化。</p>
    </div>
  </div>
  <!-- ---------- 3.9 蒸馏 ---------- -->
  <h3 id="c-distill"><span class="n">3.9</span>蒸馏：把「会推理」这件事传下去</h3>
  <div class="cols">
    <p><b>要解决的问题。</b>671B 的模型能推理，但没人想在本地跑它。小模型直接做 RL 效果很差 —— 它连像样的解题路径都采样不出来，也就无从被激励。怎么办？</p>
    <p><b>做法。</b>让大模型当老师，把它的推理过程写成大量数据，拿去微调小模型。DeepSeek-R1 用这种方式开源了 6 个稠密学生模型（1.5B / 7B / 8B / 14B / 32B / 70B，分别基于 Qwen 与 Llama）。</p>
    <p><b>报告里最关键的一个发现。</b>以 Qwen2.5-32B 为基座时，<b>直接从 R1 蒸馏的效果，优于在这同一个模型上做强化学习</b>。这句话的含义很重：它说明「推理模式」是一种可迁移的能力，而且大模型发现的推理模式，小模型自己很难探索出来。</p>
  </div>
  <figure>
    <svg viewBox="0 0 1180 210" role="img" aria-label="蒸馏流程">
      <rect x="40" y="46" width="230" height="112" rx="10" fill="#17181a"/>
      <text x="155" y="82" text-anchor="middle" font-size="14" fill="#fff" font-family="ui-monospace, monospace" font-weight="600">教师：DeepSeek-R1</text>
      <text x="155" y="106" text-anchor="middle" font-size="11.5" fill="#8b949e" font-family="ui-monospace, monospace">671B / 37B 激活</text>
      <text x="155" y="128" text-anchor="middle" font-size="11.5" fill="#8b949e" font-family="ui-monospace, monospace">产出带推理过程的解答</text>
      <path d="M280,102 L340,102" stroke="#5b6570" stroke-width="1.6" marker-end="url(#ar)"/>
      <text x="310" y="92" text-anchor="middle" font-size="11" fill="#5b6570" font-family="ui-monospace, monospace">生成数据</text>
      <rect x="352" y="56" width="180" height="92" rx="10" fill="#fbfcfd" stroke="#d8dde3"/>
      <text x="442" y="88" text-anchor="middle" font-size="12.5" fill="#5b6570" font-family="ui-monospace, monospace">推理数据</text>
      <text x="442" y="110" text-anchor="middle" font-size="11.5" fill="#5b6570" font-family="ui-monospace, monospace">正确轨迹 + 反思 + 验证</text>
      <text x="442" y="130" text-anchor="middle" font-size="11.5" fill="#5b6570" font-family="ui-monospace, monospace">过滤混语 / 长段 / 代码块</text>
      <path d="M532,102 L592,102" stroke="#5b6570" stroke-width="1.6" marker-end="url(#ar)"/>
      <text x="562" y="92" text-anchor="middle" font-size="11" fill="#5b6570" font-family="ui-monospace, monospace">监督微调</text>
      <rect x="604" y="56" width="200" height="92" rx="10" fill="#F5F7FF" stroke="#2f6fb8"/>
      <text x="704" y="88" text-anchor="middle" font-size="12.5" fill="#1b4f8a" font-family="ui-monospace, monospace">学生：小稠密模型</text>
      <text x="704" y="110" text-anchor="middle" font-size="11.5" fill="#1b4f8a" font-family="ui-monospace, monospace">1.5B … 70B</text>
      <text x="704" y="130" text-anchor="middle" font-size="11.5" fill="#1b4f8a" font-family="ui-monospace, monospace">Qwen / Llama 基座</text>
      <line x1="840" y1="30" x2="840" y2="186" stroke="#eaeef2"/>
      <text x="868" y="58" font-size="12" fill="#17181a" font-family="ui-monospace, monospace" font-weight="600">报告里的对照结论</text>
      <text x="868" y="86" font-size="12" fill="#5b6570" font-family="ui-monospace, monospace">· 直接蒸馏 &gt; 在小模型上做 RL（同一基座对比）</text>
      <text x="868" y="110" font-size="12" fill="#5b6570" font-family="ui-monospace, monospace">· 蒸馏 14B 模型大幅超越当时最优的开源推理模型</text>
      <text x="868" y="134" font-size="12" fill="#5b6570" font-family="ui-monospace, monospace">· 蒸馏 32B / 70B 在稠密模型推理榜刷新纪录</text>
      <text x="868" y="164" font-size="11" fill="#8b949e" font-family="ui-monospace, monospace">别混淆：蒸馏 ≠ 量化。量化是压缩同一个模型，蒸馏是转移能力到另一个模型。</text>
    </svg>
    <figcaption>图 3-3 · 从 R1 到小模型的蒸馏流程</figcaption>
  </figure>
  <div class="box note">
    <span class="t">易混淆点</span>
    <p>DeepSeek-V3 的技术报告里也提到「从 DeepSeek-R1 蒸馏」，但那说的是<b>把 R1 的推理能力蒸馏回 V3</b>，属于版本迭代的一部分（V3 后续版本因此推理能力提升）；而 3.9 这里说的是<b>把 R1 蒸馏到小模型</b>。同一件事、两个方向，读报告时注意区分主语。</p>
  </div>
  <!-- ---------- 3.10 DSA ---------- -->
  <h3 id="c-sparse"><span class="n">3.10</span>DSA 稀疏注意力：从平方级到近似线性</h3>
  <div class="cols">
    <p><b>要解决的问题。</b>标准注意力要让每个词跟所有词配对，复杂度是 O(L²)。10 万 token 是 100 亿次配对；100 万 token 是 1 万亿次 —— 这在工程上直接不可行。</p>
    <p><b>关键观察：绝大多数配对是浪费的。</b>写代码时，第 5000 行的括号该跟哪一层配对，其实只取决于少数几个位置。如果能先廉价地判断「哪些历史位置真正重要」，再只为这些位置做完整注意力计算，成本就能降一个数量级。</p>
    <p><b>做法（两阶段）。</b>第一阶段，用一个极轻量的索引器（Lightning Indexer）给所有历史 token 打相关性分数 —— 它只做点积，不做完整的注意力，成本接近线性。第二阶段，只取分数最高的 K 个 token，在这 K 个上做完整的注意力计算。这就是 <b>DeepSeek Sparse Attention（DSA）</b>。</p>
  </div>
  <div class="card" style="font-family:var(--mono);font-size:14.5px;line-height:2.1;overflow-x:auto">
    <div>第一阶段（廉价筛选）：  s<sub>j</sub> = I( q , k<sub>j</sub> )&nbsp;&nbsp;→&nbsp;&nbsp;S = TopK(s<sub>1</sub> … s<sub>L</sub>)</div>
    <div>第二阶段（完整计算）：  Attention( q , K<sub>S</sub> , V<sub>S</sub> ) = softmax( q·K<sub>S</sub><sup>T</sup> / &radic;d ) · V<sub>S</sub></div>
    <div style="color:var(--ink-3);font-size:12.5px;font-family:var(--sans);line-height:1.7;margin-top:6px">
      复杂度对比：标准注意力 O(L²)；DSA 约为 O(L · k)，其中 k 是固定的 Top-K 预算（远小于 L）。所以 L 越大，稀疏的收益越显著。
    </div>
  </div>
  <div class="lab">
    <div class="lab-head">
      <span class="lt">Experiment 07</span>
      <span class="lh">上下文越长，稀疏的收益有多大</span>
      <span class="tag">复杂度量级比较</span>
    </div>
    <div class="lab-body">
      <div class="lab-ctrl">
        <label for="dsaL">上下文长度</label>
        <input type="range" id="dsaL" min="4" max="1024" step="4" value="256">
        <span class="mono" id="dsaLV" style="font-size:13px;color:var(--accent);min-width:96px"></span>
      </div>
      <div class="lab-ctrl">
        <label for="dsaK">Top-K 预算</label>
        <input type="range" id="dsaK" min="1" max="32" step="1" value="8">
        <span class="mono" id="dsaKV" style="font-size:13px;color:var(--accent);min-width:96px"></span>
      </div>
      <div class="fig" style="margin:6px 0 0;box-shadow:none;background:var(--paper-2)">
        <svg viewBox="0 0 1000 300" id="dsaChart" role="img" aria-label="注意力计算量随上下文长度的变化"></svg>
        <p class="figcap">横轴：上下文长度（千 token，对数刻度）· 纵轴：相对计算量（对数刻度，以 4K 长度为 1）</p>
      </div>
      <div class="readout" style="margin-top:16px" id="dsaOut"></div>
      <p class="src" style="margin-top:12px">
        曲线按相对量级绘制（标准注意力 L²，稀疏注意力 L×k），用于说明增长趋势的差异，不代表某次实测的绝对耗时。
        K 的取值在真实系统中是超参数，取决于任务与硬件。「k」此处以千 token 为单位。
      </p>
    </div>
  </div>
  <div class="box finding">
    <span class="t">稀疏不是免费的</span>
    <p>稀疏意味着「放弃看某些 token」。如果索引器判断错误，真正关键的证据就被跳过了。这就是为什么 DeepSeek 在 V4.1-Flash 的官方局限声明里专门点名「稀疏选择错误」与「近似状态重建」两类风险，尤其在超长上下文的稀疏检索与缓存恢复边界上。<b>任何加速手段都会引入新的失效模式，读报告时要专门找这一节。</b></p>
  </div>
  <!-- ---------- 3.11 混合注意力 ---------- -->
  <h3 id="c-hybrid"><span class="n">3.11</span>CSA / HCA 混合注意力：三种距离，三种看法</h3>
  <div class="cols">
    <p><b>要解决的问题。</b>DSA 解决的是「看哪些词」，但长上下文还有第二个瓶颈：<b>即使只挑少数词，KV 本身的存储量仍然与长度成正比</b>。而且不同距离上的信息需要不同的处理方式 —— 紧邻的词要精确，远处的词只要概要，中距离的词要能检索。</p>
    <p><b>做法：用三条互补的注意力分支，各管一段距离。</b>这是 DeepSeek-V4 的核心创新。</p>
  </div>
  <div class="grid3">
    <div class="card" style="border-top:3px solid var(--accent)">
      <h4 style="margin-top:0;font-size:16px">CSA · 压缩稀疏注意力</h4>
      <p style="font-size:14.3px;color:var(--ink-2);margin:0"><b>把每 m 个 token 的 KV 压成一条</b>，然后在这些压缩条目上做稀疏注意力。<br><span style="color:var(--ink-3);font-size:13px">管什么：中远距离的「检索」—— 快速找到相关段落。</span></p>
    </div>
    <div class="card" style="border-top:3px solid var(--accent-2)">
      <h4 style="margin-top:0;font-size:16px">HCA · 重度压缩注意力</h4>
      <p style="font-size:14.3px;color:var(--ink-2);margin:0"><b>压缩得更狠，但保留稠密注意力</b>（不跳过任何条目）。<br><span style="color:var(--ink-3);font-size:13px">管什么：全局概览 —— 相当于始终记得整本书的目录。</span></p>
    </div>
    <div class="card" style="border-top:3px solid #7C92FF">
      <h4 style="margin-top:0;font-size:16px">SWA · 滑动窗口注意力</h4>
      <p style="font-size:14.3px;color:var(--ink-2);margin:0"><b>只看最近 n 个 token</b>，不做任何压缩。<br><span style="color:var(--ink-3);font-size:13px">管什么：局部精确依赖 —— 保证眼前这几句话的语法与指代不出错。</span></p>
    </div>
  </div>
  <div class="cols" style="margin-top:22px">
    <p>官方数据：在 <b>1M 上下文</b>设置下，V4-Pro 单 token 推理的<b>计算量（FLOPs）只需 V3.2 的 27%</b>，<b>KV Cache 只需 10%</b>。这两个数字就是混合注意力架构的全部意义。</p>
    <p>到 V4.1-Flash，这条路线又推进一步：<b>CSA2</b> 让每一层在 Full / Reindex / Reuse 三种模式里静态分工，共享主 KV 与索引，复用 Top-K 索引结果；解码器中再加一个<b>层次化稀疏索引器</b>，把后段索引限制在由首个 Full 层构造的候选池内，使深层索引成本与上下文长度脱钩。配合 FP4 主 KV 缓存，全局 KV 压到 <b>890 字节 / token</b>。</p>
  </div>
  <!-- ---------- 3.12 CED ---------- -->
  <h3 id="c-ced"><span class="n">3.12</span>CED 非对称结构：读得多，就少花力气读</h3>
  <div class="cols">
    <p><b>要解决的问题。</b>看一个真实的 Agent 任务：读入 30 万 token 的代码仓库、工具说明、历史对话，最后只想输出 200 个 token 的代码修改。<b>输入和输出的规模差了三个数量级</b>，但传统 Transformer 对两者用同一套参数、同样的计算方式 —— 这是巨大的结构性浪费。</p>
    <p><b>做法。</b>V4.1-Flash 把 40 层 Transformer 拆成 <b>20 层因果编码器 + 20 层解码器</b>：编码器专门负责把输入压成一套表示；解码器负责生成。关键在于——</p>
  </div>
  <div class="card" style="font-family:var(--mono);font-size:14.5px;line-height:2.1;overflow-x:auto">
    <div>区别：解码器的<b>全局 KV 直接由编码器最终隐状态投影而来</b>，而不是每个解码层自己产一套</div>
    <div style="color:var(--ink-3);font-size:12.5px;font-family:var(--sans);line-height:1.7;margin-top:6px">
      结果是：<b>读入时每 token 只激活 8B 参数，生成时激活 16B</b>。这就是「非对称」的含义 —— 两侧用不同的计算预算。
    </div>
  </div>
  <figure>
    <svg viewBox="0 0 1180 290" role="img" aria-label="CED 非对称编码器解码器结构">
      <rect x="40" y="60" width="150" height="150" rx="10" fill="#F5F7FF" stroke="#2f6fb8"/>
      <text x="115" y="88" text-anchor="middle" font-size="12.5" fill="#1b4f8a" font-family="ui-monospace, monospace" font-weight="600">输入（长）</text>
      <text x="115" y="110" text-anchor="middle" font-size="11.5" fill="#1b4f8a" font-family="ui-monospace, monospace">30 万 token</text>
      <text x="115" y="132" text-anchor="middle" font-size="11" fill="#5b6570" font-family="ui-monospace, monospace">代码仓库 / 工具说明</text>
      <text x="115" y="152" text-anchor="middle" font-size="11" fill="#5b6570" font-family="ui-monospace, monospace">历史对话 / 截图</text>
      <text x="115" y="188" text-anchor="middle" font-size="11" fill="#a8611f" font-family="ui-monospace, monospace">← 曾经这里最贵</text>
      <path d="M190,135 L246,135" stroke="#5b6570" stroke-width="1.6" marker-end="url(#ar)"/>
      <rect x="258" y="46" width="230" height="178" rx="10" fill="#fff" stroke="#d8dde3"/>
      <text x="373" y="72" text-anchor="middle" font-size="12.5" fill="#17181a" font-family="ui-monospace, monospace" font-weight="600">编码器 × 20 层</text>
      <rect x="276" y="86" width="194" height="26" rx="5" fill="#eaeef2"/><text x="373" y="104" text-anchor="middle" font-size="11" fill="#5b6570" font-family="ui-monospace, monospace">因果注意力</text>
      <rect x="276" y="118" width="194" height="26" rx="5" fill="#eaeef2"/><text x="373" y="136" text-anchor="middle" font-size="11" fill="#5b6570" font-family="ui-monospace, monospace">稀疏 / 压缩注意力</text>
      <rect x="276" y="150" width="194" height="26" rx="5" fill="#eaeef2"/><text x="373" y="168" text-anchor="middle" font-size="11" fill="#5b6570" font-family="ui-monospace, monospace">MoE 前馈层</text>
      <text x="373" y="200" text-anchor="middle" font-size="11.5" fill="#0f7b5f" font-family="ui-monospace, monospace">读入激活 ≈ 8B 参数</text>
      <path d="M488,135 L546,135" stroke="#2f6fb8" stroke-width="2" marker-end="url(#ar)"/>
      <text x="517" y="122" text-anchor="middle" font-size="10.5" fill="#1b4f8a" font-family="ui-monospace, monospace">投影</text>
      <text x="517" y="155" text-anchor="middle" font-size="10.5" fill="#1b4f8a" font-family="ui-monospace, monospace">全局 KV</text>
      <rect x="558" y="46" width="230" height="178" rx="10" fill="#fff" stroke="#2f6fb8"/>
      <text x="673" y="72" text-anchor="middle" font-size="12.5" fill="#1b4f8a" font-family="ui-monospace, monospace" font-weight="600">解码器 × 20 层</text>
      <rect x="576" y="86" width="194" height="26" rx="5" fill="#eef3f8" stroke="#2f6fb8"/><text x="673" y="104" text-anchor="middle" font-size="11" fill="#1b4f8a" font-family="ui-monospace, monospace">直接用编码器给的全局 KV</text>
      <rect x="576" y="118" width="194" height="26" rx="5" fill="#eef3f8" stroke="#2f6fb8"/><text x="673" y="136" text-anchor="middle" font-size="11" fill="#1b4f8a" font-family="ui-monospace, monospace">层次化稀疏索引</text>
      <rect x="576" y="150" width="194" height="26" rx="5" fill="#eef3f8" stroke="#2f6fb8"/><text x="673" y="168" text-anchor="middle" font-size="11" fill="#1b4f8a" font-family="ui-monospace, monospace">MoE 前馈层</text>
      <text x="673" y="200" text-anchor="middle" font-size="11.5" fill="#0f7b5f" font-family="ui-monospace, monospace">生成激活 ≈ 16B 参数</text>
      <path d="M788,135 L844,135" stroke="#5b6570" stroke-width="1.6" marker-end="url(#ar)"/>
      <rect x="856" y="76" width="140" height="120" rx="10" fill="#fbfcfd" stroke="#d8dde3"/>
      <text x="926" y="104" text-anchor="middle" font-size="12.5" fill="#5b6570" font-family="ui-monospace, monospace" font-weight="600">输出（短）</text>
      <text x="926" y="128" text-anchor="middle" font-size="11.5" fill="#5b6570" font-family="ui-monospace, monospace">200 token</text>
      <text x="926" y="152" text-anchor="middle" font-size="11" fill="#5b6570" font-family="ui-monospace, monospace">代码修改 / 工具调用</text>
      <text x="926" y="176" text-anchor="middle" font-size="11" fill="#5b6570" font-family="ui-monospace, monospace">最多 384K 输出</text>
      <line x1="1030" y1="46" x2="1030" y2="240" stroke="#eaeef2"/>
      <text x="1052" y="76" font-size="11.5" fill="#17181a" font-family="ui-monospace, monospace" font-weight="600">附属机制</text>
      <text x="1052" y="100" font-size="11" fill="#5b6570" font-family="ui-monospace, monospace">· SWA Bounded Replay</text>
      <text x="1052" y="118" font-size="11" fill="#5b6570" font-family="ui-monospace, monospace">只重放最近 n_win 个 token</text>
      <text x="1052" y="136" font-size="11" fill="#5b6570" font-family="ui-monospace, monospace">恢复窗口状态，不落盘</text>
      <text x="1052" y="160" font-size="11" fill="#5b6570" font-family="ui-monospace, monospace">· FP4 主 KV（E2M1）</text>
      <text x="1052" y="178" font-size="11" fill="#5b6570" font-family="ui-monospace, monospace">每 16 通道 1 个 E4M3 缩放</text>
      <text x="1052" y="202" font-size="11" fill="#5b6570" font-family="ui-monospace, monospace">· 890 字节 / token</text>
      <text x="1052" y="220" font-size="11" fill="#0f7b5f" font-family="ui-monospace, monospace">≈ V4-Flash 的 1/4</text>
    </svg>
    <figcaption>图 3-4 · V4.1-Flash 的 Causal Encoder-Decoder 非对称结构（依官方技术报告口径绘制）</figcaption>
  </figure>
  <div class="box finding">
    <span class="t">官方披露的失效模式</span>
    <p>这种「用近似表示代替逐层自产」的做法引入了新的风险：稀疏选择出错与近似状态重建，可能在极端情况下降低能力 —— 尤其出现在<b>超长上下文的稀疏检索</b>与<b>缓存恢复的衔接边界</b>。官方表示将做进一步压力测试。这类「作者主动写出的局限」是精读报告时信息密度最高的部分。</p>
  </div>
  <!-- ---------- 3.13 mHC & Muon ---------- -->
  <h3 id="c-train"><span class="n">3.13</span>mHC 与 Muon：让上百层的网络稳住</h3>
  <div class="cols">
    <p><b>mHC 要解决的问题。</b>Transformer 靠残差连接（把输入直接加到输出上）让梯度能顺畅地穿过上百层：h<sub>l+1</sub> = h<sub>l</sub> + F(h<sub>l</sub>)。但当层数继续堆叠，单条残差通道会变成瓶颈 —— 信号要么被稀释，要么被逐层放大。一个自然的想法是：<b>把一条通道扩展成多条并行通道，让网络自己学习怎么混合它们</b>（这就是 Hyper-Connections）。可引入更多自由度的同时，也引入了不稳定性。</p>
    <p><b>mHC 的解法是给混合矩阵加「流形约束」。</b>把那些负责混合的矩阵限制在一个性质良好的矩阵集合（流形）上 —— 比如保持范数、保持正交性 —— 这样多路混合既保留了表达力，又不会在深层传播中失控。V4.1-Flash 进一步做了 <b>Single-Pass mHC</b> 与高效的 Mega-mHC 内核，把这份额外的稳定性开销压下来。</p>
    <p><b>Muon 要解决的问题。</b>主流优化器 AdamW 是「逐元素」调节学习率的：每个参数单独根据自己的历史梯度调整步长。它很好用，但对一个巨大的权重矩阵来说，它并不知道「这个矩阵整体的更新方向是否合理」。<b>Muon 的做法是对整个矩阵做近似正交化</b>（常用 Newton-Schulz 迭代实现），让更新在各个方向上尺度更均衡，从而收敛更快、训练更稳 —— 这在万亿参数规模上尤其重要。</p>
  </div>
  <figure>
    <svg viewBox="0 0 1180 200" role="img" aria-label="残差连接与多路混合对比">
      <text x="40" y="26" font-size="12" fill="#5b6570" font-family="ui-monospace, monospace">标准残差：一条通道</text>
      <rect x="40" y="42" width="70" height="34" rx="6" fill="#eaeef2" stroke="#d8dde3"/><text x="75" y="64" text-anchor="middle" font-size="11.5" fill="#5b6570" font-family="ui-monospace, monospace">层 l</text>
      <path d="M110,59 L200,59" stroke="#5b6570" stroke-width="2" marker-end="url(#ar)"/>
      <path d="M110,80 C150,120 190,120 200,80" stroke="#8b949e" stroke-width="1.6" fill="none" stroke-dasharray="4 3"/>
      <text x="155" y="128" text-anchor="middle" font-size="10.5" fill="#5b6570" font-family="ui-monospace, monospace">残差直连</text>
      <rect x="212" y="42" width="70" height="34" rx="6" fill="#eaeef2" stroke="#d8dde3"/><text x="247" y="64" text-anchor="middle" font-size="11.5" fill="#5b6570" font-family="ui-monospace, monospace">层 l+1</text>
      <line x1="330" y1="20" x2="330" y2="180" stroke="#eaeef2"/>
      <text x="366" y="26" font-size="12" fill="#1b4f8a" font-family="ui-monospace, monospace">mHC：多路通道 + 受约束的混合</text>
      <rect x="366" y="42" width="70" height="76" rx="6" fill="#eef3f8" stroke="#2f6fb8"/><text x="401" y="86" text-anchor="middle" font-size="11.5" fill="#1b4f8a" font-family="ui-monospace, monospace">层 l</text>
      <g stroke="#2f6fb8" stroke-width="1.8" fill="none">
        <path d="M436,54 L600,54"/><path d="M436,80 L600,80"/><path d="M436,106 L600,106"/>
      </g>
      <g fill="#2f6fb8" font-family="ui-monospace, monospace" font-size="10">
        <text x="518" y="48" text-anchor="middle">通道 1</text><text x="518" y="74" text-anchor="middle">通道 2</text><text x="518" y="100" text-anchor="middle">通道 3</text>
      </g>
      <rect x="612" y="42" width="96" height="76" rx="6" fill="#fff" stroke="#2f6fb8"/>
      <text x="660" y="70" text-anchor="middle" font-size="10.5" fill="#1b4f8a" font-family="ui-monospace, monospace">混合矩阵</text>
      <text x="660" y="88" text-anchor="middle" font-size="10.5" fill="#1b4f8a" font-family="ui-monospace, monospace">受流形约束</text>
      <text x="660" y="106" text-anchor="middle" font-size="9.5" fill="#0f7b5f" font-family="ui-monospace, monospace">稳定不失控</text>
      <rect x="730" y="42" width="70" height="76" rx="6" fill="#eef3f8" stroke="#2f6fb8"/><text x="765" y="86" text-anchor="middle" font-size="11.5" fill="#1b4f8a" font-family="ui-monospace, monospace">层 l+1</text>
      <line x1="850" y1="20" x2="850" y2="180" stroke="#eaeef2"/>
      <text x="884" y="26" font-size="12" fill="#17181a" font-family="ui-monospace, monospace" font-weight="600">为什么在 V4 才需要</text>
      <text x="884" y="54" font-size="11.5" fill="#5b6570" font-family="ui-monospace, monospace">V4-Pro 是 1.6T 参数、训练语料超 32T token 的规模。</text>
      <text x="884" y="76" font-size="11.5" fill="#5b6570" font-family="ui-monospace, monospace">这个量级上，任何微小的数值不稳定都会被放大成</text>
      <text x="884" y="98" font-size="11.5" fill="#5b6570" font-family="ui-monospace, monospace">「损失尖峰」（loss spike），甚至一次回滚就损失数周。</text>
      <text x="884" y="126" font-size="11.5" fill="#0f7b5f" font-family="ui-monospace, monospace">所以 V4 用 Muon 替换大部分 AdamW，并用 mHC</text>
      <text x="884" y="148" font-size="11.5" fill="#0f7b5f" font-family="ui-monospace, monospace">加固残差通路 —— 这不是「性能优化」，是「稳定性工程」。</text>
      <text x="884" y="176" font-size="10.5" fill="#8b949e" font-family="ui-monospace, monospace">对照：V3 报告称全程未出现不可恢复的 loss 尖峰、未回滚。</text>
    </svg>
    <figcaption>图 3-5 · 从单路残差到受约束多路混合（mHC）</figcaption>
  </figure>
  <!-- ---------- 3.14 Engram ---------- -->
  <h3 id="c-mem"><span class="n">3.14</span>Engram 条件记忆：用「查表」替代一部分「计算」</h3>
  <div class="cols">
    <p><b>要解决的问题。</b>语言里有大量内容是「固定搭配」和「事实」：「北京的省会是……」这类信息，用矩阵乘法去反复运算它，是很昂贵的表达方式。人脑处理这类知识的方式更接近<b>检索</b>，而不是重新推理。</p>
    <p><b>做法。</b>Engram 模块的思路是把「可扩展的查表（lookup）」作为一条新的稀疏轴：根据 token 直接检索一段记忆表示，再与后续计算结合。DeepSeek 的对应工作标题很直白 —— <b>《Conditional Memory via Scalable Lookup: A New Axis of Sparsity for Large Language Models》</b>。</p>
    <p><b>为什么说这是「新的稀疏轴」。</b>MoE 稀疏的是<b>计算</b>（不激活的专家不参与矩阵乘）；Engram 稀疏的是<b>存储</b>（不命中的记忆条目根本不被读取）。两者的收益方向不同：前者省算力，后者省带宽。V4.1-Flash 中 Engram 模块有 196B 参数，按 token 稀疏访问。</p>
  </div>
  <!-- ---------- 3.15 推测解码 ---------- -->
  <h3 id="c-spec"><span class="n">3.15</span>推测解码：一次前向，验证好几个词</h3>
  <div class="cols">
    <p><b>要解决的问题。</b>自回归生成是串行的：出一个词 → 算一次前向 → 再出一个词。但 GPU 是高度并行的硬件，一个字一个字地喂给它，算力利用率极低。瓶颈不在计算，在「没法并行」。</p>
    <p><b>做法。</b>让一个便宜的小「草稿模型」（或模型自身的额外预测头）一口气猜出后面 k 个词，然后把这段草稿<b>一次前向并行验证</b>。验证时模型会算出每个位置上「正确答案应该是什么」，从头依次比对：连续的猜对部分全部接受，第一个猜错的位置截断、改用大模型的正确结果。关键点在于 ——<b>验证 k 个词的成本，约等于生成 1 个词的成本</b>，因为它是同一次前向。</p>
  </div>
  <div class="lab">
    <div class="lab-head">
      <span class="lt">Experiment 08</span>
      <span class="lh">草稿 → 验证 → 接受</span>
      <span class="tag">演示机制 · 概率为示意</span>
    </div>
    <div class="lab-body">
      <div style="display:flex;gap:10px;flex-wrap:wrap;margin-bottom:16px">
        <button class="btn" id="specBtn">生成一小段</button>
        <button class="btn ghost" id="specReset">重置统计</button>
      </div>
      <div class="readout" id="specStat" style="margin-bottom:16px"></div>
      <div id="specOut" style="display:flex;flex-wrap:wrap;gap:8px;margin-bottom:8px"></div>
      <div id="specTokens" style="font-family:var(--mono);font-size:14px;line-height:1.9;color:var(--ink-2);background:var(--paper-2);border:1px solid var(--rule-2);border-radius:var(--r-s);padding:12px 14px;min-height:46px"></div>
      <p class="src" style="margin-top:14px">
        每个方块 = 草稿模型猜的一个词。绿色 = 大模型验证通过（白送），砖红 = 猜错位置（从该处截断重算）。平均一次前向能产出 1 个以上 token，这就是加速的来源。
      </p>
    </div>
  </div>
  <div class="box note">
    <span class="t">DeepSeek 的实现</span>
    <p>V4-Pro-0813 检查点附加了推测解码模块；V4.1-Flash 的方案叫 <b>DSpark</b>：半自回归地生成草稿，并用「置信度」来调度验证策略（对高置信的草稿更激进地一次验证多个，对低置信的更谨慎）。注意它与 MTP（3.5）的关系：MTP 在训练时建立的「多步预测能力」，正好可以被复用来充当草稿。</p>
  </div>
  <!-- ---------- 3.16 测试时计算 ---------- -->
  <h3 id="c-test"><span class="n">3.16</span>测试时计算：多想一会儿，真的会更准吗</h3>
  <div class="cols">
    <p><b>要解决的问题。</b>传统上模型的能力在训练完就固定了。但有些问题（复杂数学、长程规划）本来就需要更多思考步骤 —— 能不能在推理阶段「多花算力换准确率」？</p>
    <p><b>做法。</b>让模型生成长的思维链（Chain-of-Thought），把思考当作计算资源来花，这就是<b>测试时计算扩展（test-time scaling）</b>。工程上它表现为一个可调参数：思考强度 / 推理强度。DeepSeek-V4.1-Flash 把它做成了 <b>1 到 100 的连续可调整数</b>，官方建议复杂 Agent 场景设到 max 档。</p>
  </div>
  <div class="lab">
    <div class="lab-head">
      <span class="lt">Experiment 09</span>
      <span class="lh">推理强度的边际收益</span>
      <span class="tag">数据点：官方披露的两档</span>
    </div>
    <div class="lab-body">
      <div class="lab-ctrl">
        <label for="eff">推理强度</label>
        <input type="range" id="eff" min="1" max="100" step="1" value="25">
        <span class="mono" id="effV" style="font-size:13px;color:var(--accent);min-width:96px"></span>
      </div>
      <div class="bars" id="effBars"></div>
      <div class="readout" style="margin-top:18px" id="effOut"></div>
      <p class="src" style="margin-top:14px">
        两个可锚定的数据点（官方披露）：推理强度从 25 提到 100 时，DeepSWE v1.1 从 66.0% 升到 74.2%，Terminal-Bench 2.1 从 82.4% 升到 90.6%，而输出 token 消耗约为 2.5 倍。
        中间档位的曲线为按此两端点做的平滑插值示意，真实边际收益通常是递减的、且随任务类型而变化。
      </p>
    </div>
  </div>
  <div class="box note">
    <span class="t">一个反直觉的细节</span>
    <p>在 R1-Zero 的训练过程中，报告观察到模型的<b>平均思考时间在持续缩短</b> —— 但这个缩短并不是因为「想得更少」，而是模型内部演化出了更高效的探索方式（比如更早放弃错误路径）。<b>思考更长 ≠ 更好；有效思考才是目标。</b>这句话是理解整个测试时计算方向最有用的一句提醒。</p>
  </div>
  <!-- ---------- 3.17 OPD ---------- -->
  <h3 id="c-opd"><span class="n">3.17</span>同策略蒸馏 OPD：把多个专家合回一个模型</h3>
  <div class="cols">
    <p><b>要解决的问题。</b>V4 的后训练是两阶段范式。第一阶段，为了让每个领域都做到最好，<b>分别培养领域专家</b>（数学的、代码的、Agent 的、写作的……）—— 它们靠 SFT 加 GRPO 强化学习各自做到很强。但上线时你只能部署一个模型，不能同时挂十几个专家让用户自己选。</p>
    <p><b>做法：用同策略蒸馏（On-Policy Distillation, OPD）合并。</b>「同策略」意味着：不是拿专家生成的固定数据集去训练学生，而是<b>让当前学生模型自己走一遍、采样出自己的轨迹，再让专家在这些轨迹上给出指导信号</b>，学生据此纠正。</p>
    <p><b>为什么必须「同策略」。</b>学生模型犯的错，和专家模型犯的错不是同一类。如果只在专家的输出分布上做模仿（离线蒸馏），学生只学会了「专家会怎么答」，却没学会「当自己走偏时该怎么回来」。而同策略蒸馏纠正的正是<b>学生自己会走到的那些状态</b>，所以合并后的模型在统一行为上更稳。</p>
  </div>
  <div class="grid2">
    <div class="card">
      <h4 style="margin-top:0"><span class="tag">离线蒸馏</span></h4>
      <p style="font-size:14.8px;color:var(--ink-2);margin:0">在专家的输出上模仿。数据可以提前生成、反复使用，工程简单，但学生的错误分布没被覆盖。</p>
    </div>
    <div class="card" style="border-color:var(--accent-line)">
      <h4 style="margin-top:0"><span class="tag acc">同策略蒸馏</span></h4>
      <p style="font-size:14.8px;color:var(--ink-2);margin:0">在学生自己采样的轨迹上学习。需要在线生成，成本更高，但能纠正学生自身的偏差 —— V4 系列采用的是这条路线。</p>
    </div>
  </div>
  <div class="box note">
    <span class="t">这条线索的完整拼图</span>
    <p>到这里，整个后训练范式的演进可以串起来了：<b>SFT 模仿</b>（会答）→ <b>规则奖励 RL / GRPO</b>（会推理）→ <b>冷启动 + 多阶段 RL</b>（会推理且能读）→ <b>蒸馏</b>（把能力传给小模型）→ <b>领域专家分头训练</b>（每个领域都最强）→ <b>同策略蒸馏</b>（合回一个模型）。每一步都在解「如何在不牺牲均衡性的前提下把单项做到极致」。</p>
  </div>
  <!-- ============================ 附录 ============================ -->
  <div class="sec-head" style="margin-top:64px">
    <span class="sec-"">APPENDIX</span>
    <h2 id="appx">原始报告与出处</h2>
    <span class="sub">SOURCES</span>
  </div>
  <div class="cols">
    <p>下面是本手册引用的原始资料清单。<b>建议的读法是「先读本手册的对应小节，再点进原始报告只看那一节」</b>，而不是从头啃论文。链接如失效，请在 arXiv 或官方 GitHub 按标题检索。</p>
  </div>
  <div class="grid2" style="margin-top:8px">
    <div class="card">
      <h4 style="margin-top:0">DeepSeek 官方</h4>
      <ul style="padding-left:18px;font-size:14.3px;line-height:1.95;color:var(--ink-2);margin:0">
        <li><a href="https://www.deepseek.com/news/" target="_blank" rel="noopener">官方动态列表</a>（各版本发布说明的权威入口）</li>
        <li><a href="https://www.deepseek.com/news/deepseek-v4-1-flash/" target="_blank" rel="noopener">DeepSeek V4.1 Flash 发布说明</a>（2026-09-10）</li>
        <li><a href="https://www.deepseek.com/news/v4-preview/" target="_blank" rel="noopener">DeepSeek-V4 预览版发布说明</a>（2026-04-24）</li>
        <li><a href="https://www.deepseek.com/news/deepseek-v3-2/" target="_blank" rel="noopener">V3.2 正式版发布说明</a>（2025-12-01）</li>
        <li><a href="https://www.deepseek.com/news/v3-2-exp/" target="_blank" rel="noopener">V3.2-Exp 发布说明</a>（2025-09-29）</li>
        <li><a href="https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash" target="_blank" rel="noopener">V4.1-Flash 模型与技术报告（Hugging Face）</a></li>
        <li><a href="https://github.com/deepseek-ai" target="_blank" rel="noopener">deepseek-ai GitHub 组织</a>（含 FlashMLA / DeepGEMM / DualPipe / Engram 等配套开源）</li>
      </ul>
    </div>
    <div class="card">
      <h4 style="margin-top:0">技术报告与论文</h4>
      <ul style="padding-left:18px;font-size:14.3px;line-height:1.95;color:var(--ink-2);margin:0">
        <li><a href="https://arxiv.org/abs/2412.19437" target="_blank" rel="noopener">DeepSeek-V3 Technical Report</a></li>
        <li><a href="https://arxiv.org/abs/2405.04434" target="_blank" rel="noopener">DeepSeek-V2 Technical Report</a>（MLA 与 DeepSeekMoE 的原始定义）</li>
        <li><a href="https://arxiv.org/abs/2501.12948" target="_blank" rel="noopener">DeepSeek-R1 Technical Report</a></li>
        <li><a href="https://arxiv.org/abs/2606.19348" target="_blank" rel="noopener">DeepSeek-V4 Technical Report</a></li>
        <li><a href="https://arxiv.org/abs/2401.06066" target="_blank" rel="noopener">DeepSeekMoE</a>（细粒度专家 + 共享专家隔离）</li>
        <li><a href="https://arxiv.org/abs/2402.03300" target="_blank" rel="noopener">DeepSeekMath</a>（GRPO 算法的出处）</li>
        <li><a href="https://arxiv.org/abs/2401.02954" target="_blank" rel="noopener">DeepSeek LLM</a>（第一代 67B）</li>
      </ul>
    </div>
    <div class="card">
      <h4 style="margin-top:0">前沿对比来源</h4>
      <ul style="padding-left:18px;font-size:14.3px;line-height:1.95;color:var(--ink-2);margin:0">
        <li><a href="https://openai.com/index/introducing-gpt-5-4" target="_blank" rel="noopener">OpenAI · Introducing GPT-5.4</a></li>
        <li><a href="https://deploymentsafety.openai.com/gpt-5-4-thinking/mle-bench" target="_blank" rel="noopener">GPT-5.4 Thinking System Card</a></li>
        <li><a href="https://www.anthropic.com/system-cards" target="_blank" rel="noopener">Anthropic · 模型系统卡索引</a></li>
        <li><a href="https://www.anthropic.com/claude-opus-4-7-system-card" target="_blank" rel="noopener">Claude Opus 4.7 System Card</a></li>
        <li><a href="https://www.anthropic.com/transparency" target="_blank" rel="noopener">Anthropic · Transparency Hub</a>（训练方法与分层政策口径）</li>
      </ul>
    </div>
    <div class="card">
      <h4 style="margin-top:0">前置知识（按阅读顺序）</h4>
      <ul style="padding-left:18px;font-size:14.3px;line-height:1.95;color:var(--ink-2);margin:0">
        <li><a href="https://arxiv.org/abs/1706.03762" target="_blank" rel="noopener">Attention Is All You Need（Transformer 原始论文）</a></li>
        <li><a href="https://arxiv.org/abs/2006.16668" target="_blank" rel="noopener">GShard</a>（MoE 大规模并行训练）</li>
        <li><a href="https://arxiv.org/abs/2101.03961" target="_blank" rel="noopener">Switch Transformer</a>（MoE 进入 Transformer 的关键一步）</li>
        <li>NSA（Native Sparse Attention，DSA 的技术前身之一）</li>
        <li>Muon 优化器（在 GitHub 检索 KellerJordan/Muon）</li>
      </ul>
    </div>
  </div>
  <h3 id="limits"><span class="n">附录 B</span>口径与局限声明</h3>
  <div class="box finding">
    <span class="t">请务必读完这一节再引用本手册</span>
    <p style="margin:0 0 8px"><b>1 · 时间快照。</b>本手册数据截至 <b>2026-09-21</b>。DeepSeek 的迭代节奏以月为单位（V3.2-Exp 到 V3.2 正式版仅隔两个月）；V4.1-Pro 官方只在 V4.1-Flash 的发布说明里提过一次名字，至今没有发布日期、没有模型 ID、没有价格；同一份公告里「9 月 14 日起 V4-Pro 下线并路由至 V4.1-Flash」的安排，也已在 9 月 12 日前后被官方收回。任何数字与排名都可能在你读到它时已经过时。</p>
    <p style="margin:0 0 8px"><b>2 · 来源分层。</b>带明确出处的数据来自：DeepSeek 官方发布页、Hugging Face 官方模型卡与技术报告、arXiv 论文、OpenAI 与 Anthropic 的官方发布页与系统卡。少量细节（如静默更新的具体范围、正式版检查点的评测汇总）来自第三方追踪站点，已在小节内标注「口径提醒」。</p>
    <p style="margin:0 0 8px"><b>3 · 跑分的可比性。</b>第 2.2 节的成绩全部出自 DeepSeek 官方报告的横向评测表 —— 这是「我方视角」的证据，思考强度、是否使用工具、采样设置均由发布方设定。<b>不同厂商的分数不能直接跨表比较。</b></p>
    <p style="margin:0 0 8px"><b>4 · 演示的性质。</b>所有交互实验都是<b>机制演示</b>，用于说明原理与量级趋势，不是实测性能数据。KV 缓存、稀疏注意力、成本测算的数值基于公开配置的公式推算，已在对应实验下方写明计算口径。</p>
    <p style="margin:0"><b>5 · 定价与商业策略。</b>API 价格为发布时点的公开标价，峰谷时段与缓存命中率会显著改变实际账单。做选型请以官方定价页当日数据为准。</p>
  </div>
</section>

<footer>
  <p>
<p>
</footer>

<script>
(function(){
'use strict';
var $ = function(s,r){ return (r||document).querySelector(s); };
var $$ = function(s,r){ return Array.prototype.slice.call((r||document).querySelectorAll(s)); };
var clamp = function(v,a,b){ return Math.min(b, Math.max(a, v)); };

/* ============ 0 · 阅读进度与目录高亮 ============ */
var prog = $('#progress');
var tocLinks = $$('.toc a');
var spyTargets = tocLinks.map(function(a){
  var id = a.getAttribute('href');
  return { a: a, el: id && id.length > 1 ? $(id) : null };
}).filter(function(o){ return o.el; });

function updateProgress(){
  var h = document.documentElement.scrollHeight - window.innerHeight;
  if(prog) prog.style.width = (h > 0 ? clamp(window.scrollY / h * 100, 0, 100) : 0) + '%';
}
function spy(){
  var best = null;
  for(var i = 0; i < spyTargets.length; i++){
    var top = spyTargets[i].el.getBoundingClientRect().top;
    if(top <= 150) best = spyTargets[i];
  }
  spyTargets.forEach(function(o){ o.a.classList.toggle('on', o === best); });
}
var ticking = false;
window.addEventListener('scroll', function(){
  if(ticking) return;
  ticking = true;
  requestAnimationFrame(function(){ updateProgress(); spy(); ticking = false; });
}, { passive: true });
updateProgress(); spy();

/* ============ 1 · 滚动揭示 ============ */
if('IntersectionObserver' in window){
  var io = new IntersectionObserver(function(es){
    es.forEach(function(e){
      if(e.isIntersecting){ e.target.classList.add('in'); io.unobserve(e.target); }
    });
  }, { rootMargin: '0px 0px -8% 0px', threshold: 0.04 });
  $$('.reveal').forEach(function(el, i){ el.style.transitionDelay = (i % 3) * 60 + 'ms'; io.observe(el); });
}else{
  $$('.reveal').forEach(function(el){ el.classList.add('in'); });
}
/* 兜底：无论观察器是否触发，3 秒后强制显示所有内容 */
setTimeout(function(){ $$('.reveal').forEach(function(el){ el.classList.add('in'); }); }, 2500);

/* ============ 2 · 版本时间轴 ============ */
(function(){
  var nodes = $$('.tl-node'), cards = $$('.vcard');
  if(!nodes.length) return;
  nodes.forEach(function(n){
    n.addEventListener('click', function(){
      var v = n.getAttribute('data-v');
      nodes.forEach(function(x){
        var on = (x === n);
        x.classList.toggle('on', on);
        x.setAttribute('aria-selected', on ? 'true' : 'false');
      });
      cards.forEach(function(c){ c.classList.toggle('on', c.getAttribute('data-v') === v); });
      if(window.innerWidth < 780){
        var panel = $('.vcard.on');
        if(panel) panel.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    });
  });
})();

/* ============ 3 · 实验 01：基准成绩对比 ============ */
(function(){
  var pills = $('#benchPills'), barsEl = $('#benchBars'), descEl = $('#benchDesc');
  if(!pills || !barsEl) return;

  var M = [
    ['MMLU-Pro', 100, '综合知识：研究生级多学科选择题，考察广博度与推理。'],
    ['GPQA Diamond', 100, '研究生级科学问答：物理、化学、生物的专家级难题，人类博士正确率也有限。'],
    ['SimpleQA-Verified', 100, '事实准确性：短问短答的纯知识检索，最考验「知不知道」而不是「会不会推」。'],
    ['HLE', 100, 'Humanity\u2019s Last Exam：跨学科极难题集合，当前前沿模型的分数普遍偏低。'],
    ['HMMT 2026 Feb', 100, '高中数学竞赛：2026 年 2 月 HMMT 试题，考察竞赛级数学推理。'],
    ['Apex', 100, '数学前沿：高难度奥林匹克式证明与推理，区分度很高。'],
    ['LiveCodeBench', 100, '竞赛编程：用近期竞赛题防止数据污染，考察代码推理。'],
    ['SWE Verified', 100, '真实软件工程：在真实代码仓库上修复 issue 并通过测试。'],
    ['Terminal Bench 2.0', 100, '终端 Agent：在命令行环境中自主完成多步任务。'],
    ['BrowseComp', 100, '深度检索 Agent：需要在互联网上做多跳信息搜寻与整合。'],
    ['MRCR 1M', 100, '百万上下文检索：在 100 万 token 的长度里准确找到并整合信息。'],
    ['Toolathlon', 100, '工具使用：多工具协同完成复杂任务的综合能力。']
  ];
  var ROWS = [
    { n: 'DeepSeek-V4-Pro', ds: true,  v: [87.5, 90.1, 57.9, 37.7, 95.2, 38.3, 93.5, 80.6, 67.9, 83.4, 83.5, 51.8] },
    { n: 'DeepSeek-V4-Flash', ds: true, v: [86.2, 88.1, 34.1, 34.8, 94.8, 33.0, 91.6, 79.0, 56.9, 73.2, 78.7, 47.8] },
    { n: 'Claude Opus 4.6', ds: false, v: [89.1, 91.3, 46.2, 40.0, 96.2, 34.5, 88.8, 80.8, 65.4, 83.7, 92.9, 47.2] },
    { n: 'GPT-5.4', ds: false, v: [87.5, 93.0, 45.3, 39.8, 97.7, 54.1, null, null, 75.1, 82.7, null, 54.6] },
    { n: 'Gemini 3.1 Pro', ds: false, v: [91.0, 94.3, 75.6, 44.4, 94.7, 60.9, 91.7, 80.6, 68.5, 85.9, 76.3, 48.8] }
  ];
  var cur = 0;

  pills.innerHTML = M.map(function(m, i){
    return '<button class="btn ' + (i === 0 ? '' : 'ghost') + '" data-i="' + i + '" style="' + (i === 0 ? '' : 'background:transparent;color:var(--accent)') + '">' + m[0] + '</button>';
  }).join('');

  function render(){
    var metric = M[cur];
    descEl.textContent = metric[2] + '（数据源：DeepSeek-V4 技术报告横向评测表）';
    var vals = ROWS.map(function(r){ return r.v[cur]; });
    var max = Math.max.apply(null, vals.filter(function(v){ return v !== null; }));
    barsEl.innerHTML = ROWS.map(function(r, ri){
      var v = r.v[cur];
      var w, txt, cls;
      if(v === null){ w = 0; txt = '未报告'; cls = 'gray'; }
      else { w = clamp(v / max * 100, 2, 100); txt = v.toFixed(1); cls = r.ds ? 'alt' : 'gray'; }
      var dtxt;
      if(v === null){ dtxt = '该项未报告'; }
      else if(v === max && v > 0){ dtxt = '本项最高 ' + v.toFixed(1); }
      else { dtxt = v.toFixed(1); }
      return '<div class="bar-row" title="' + dtxt + '">' +
        '<span class="bl" style="' + (r.ds ? 'color:var(--accent);font-weight:600' : '') + '">' + r.n + '</span>' +
        '<span class="bt"><span class="bf ' + cls + '" style="width:' + w + '%"></span></span>' +
        '<span class="bv">' + txt + '</span></div>';
    }).join('');
    $$('button', pills).forEach(function(b, i){
      var on = (+b.getAttribute('data-i') === cur);
      b.className = 'btn' + (on ? '' : ' ghost');
      b.style.background = on ? '' : 'transparent';
      b.style.color = on ? '' : 'var(--accent)';
    });
  }
  pills.addEventListener('click', function(e){
    var b = e.target.closest('button');
    if(!b) return;
    cur = +b.getAttribute('data-i');
    render();
  });
  render();
})();

/* ============ 4 · 实验 02：成本测算 ============ */
(function(){
  var inEl = $('#costIn'), hitEl = $('#costHit'), outEl = $('#costOut');
  var barsEl = $('#costBars'), noteEl = $('#costNote');
  if(!inEl || !barsEl) return;

  var MODELS = [
    { n: 'DeepSeek V4.1-Flash 闲时', hit: 0.003, miss: 0.15, out: 0.60, ds: true },
    { n: 'DeepSeek V4.1-Flash 高峰', hit: 0.006, miss: 0.30, out: 1.20, ds: true },
    { n: 'GPT-5.6 Sol', hit: 0.40, miss: 4.00, out: 20.00, ds: false },
    { n: 'Claude Opus 5', hit: 0.50, miss: 5.00, out: 25.00, ds: false }
  ];
  var fmtTok = function(n){ return n >= 1000 ? (n / 1000).toFixed(0) + 'K' : String(n); };
  var fmtUsd = function(v){
    if(v >= 1) return '$' + v.toFixed(2);
    if(v >= 0.01) return '$' + v.toFixed(3);
    return '$' + v.toFixed(5);
  };

  function render(){
    var inTok = +inEl.value, hitRate = +hitEl.value / 100, outTok = +outEl.value;
    $('#costInV').textContent = fmtTok(inTok) + ' token';
    $('#costHitV').textContent = hitEl.value + ' %';
    $('#costOutV').textContent = fmtTok(outTok) + ' token';

    var costs = MODELS.map(function(m){
      var inCost = (inTok / 1e6) * (hitRate * m.hit + (1 - hitRate) * m.miss);
      var outCost = (outTok / 1e6) * m.out;
      return { n: m.n, ds: m.ds, total: inCost + outCost, inCost: inCost, outCost: outCost };
    });
    var max = Math.max.apply(null, costs.map(function(c){ return c.total; }));
    var min = Math.min.apply(null, costs.map(function(c){ return c.total; }));

    barsEl.innerHTML = costs.map(function(c){
      var w = clamp(Math.log10(c.total / min + 1) / Math.log10(max / min + 1) * 100, 3, 100);
      return '<div class="bar-row" style="grid-template-columns:170px 1fr 106px" title="输入 ' + fmtUsd(c.inCost) + ' + 输出 ' + fmtUsd(c.outCost) + '">' +
        '<span class="bl" style="' + (c.ds ? 'color:var(--accent);font-weight:600' : '') + '">' + c.n + '</span>' +
        '<span class="bt" style="height:18px"><span class="bf ' + (c.ds ? 'alt' : 'gray') + '" style="width:' + w + '%"></span></span>' +
        '<span class="bv">' + fmtUsd(c.total) + '</span></div>';
    }).join('');

    var ds = costs[0].total, gpt = costs[2].total, cl = costs[3].total;
    noteEl.innerHTML =
      '<div class="rl"><span>本次请求的输入成本（按命中率拆分后）</span><span class="rv plain">' + fmtUsd(costs[0].inCost) + '（DeepSeek 闲时）</span></div>' +
      '<div class="rl"><span>DeepSeek 闲时 vs DeepSeek 高峰</span><span class="rv">×' + (costs[1].total / ds).toFixed(1) + '</span></div>' +
      '<div class="rl"><span>GPT-5.6 Sol 是本场景的</span><span class="rv">' + (gpt / ds).toFixed(0) + ' 倍</span></div>' +
      '<div class="rl"><span>Claude Opus 5 是本场景的</span><span class="rv">' + (cl / ds).toFixed(0) + ' 倍</span></div>' +
      '<div class="rl"><span>条形刻度</span><span class="rv plain">对数刻度（跨度可达三个数量级）</span></div>';
  }
  [inEl, hitEl, outEl].forEach(function(el){ el.addEventListener('input', render); });
  render();
})();

/* ============ 5 · 实验 03：KV Cache ============ */
(function(){
  var sl = $('#kvSlider'), barsEl = $('#kvBars'), outEl = $('#kvOut');
  if(!sl || !barsEl) return;

  var PER_TOKEN = [
    { n: '密集注意力参照', b: 61 * 128 * 128 * 2 * 2, cls: 'warn', note: 'BF16' },
    { n: 'MLA（V2/V3 配置）', b: 61 * (512 + 64) * 2, cls: 'alt', note: '潜向量 512 + 位置 64' },
    { n: 'MLA + FP8 存储', b: 61 * (512 + 64) * 1, cls: 'alt', note: '低精度缓存' },
    { n: 'V4.1-Flash 实际', b: 890, cls: 'alt', note: '官方披露值' }
  ];
  function fmtB(b){
    if(b >= 1e12) return (b / 1e12).toFixed(2) + ' TB';
    if(b >= 1e9)  return (b / 1e9).toFixed(2) + ' GB';
    if(b >= 1e6)  return (b / 1e6).toFixed(1) + ' MB';
    if(b >= 1e3)  return (b / 1e3).toFixed(1) + ' KB';
    return b.toFixed(0) + ' B';
  }
  function render(){
    var L = +sl.value;                      // 千 token
    $('#kvSliderV').textContent = L >= 1024 ? '1M token' : L + 'K token';
    var totals = PER_TOKEN.map(function(p){ return p.b * L * 1000; });
    var max = Math.max.apply(null, totals);
    var lo = Math.log10(1), hi = Math.log10(max);
    barsEl.innerHTML = PER_TOKEN.map(function(p, i){
      var w = clamp((Math.log10(totals[i]) - lo) / (hi - lo) * 100, 4, 100);
      return '<div class="bar-row" style="grid-template-columns:172px 1fr 104px" title="' + p.note + '">' +
        '<span class="bl" style="text-align:left">' + p.n + '</span>' +
        '<span class="bt"><span class="bf ' + p.cls + '" style="width:' + w + '%"></span></span>' +
        '<span class="bv">' + fmtB(totals[i]) + '</span></div>';
    }).join('');
    outEl.innerHTML =
      '<div class="rl"><span>密集注意力每 token 缓存</span><span class="rv plain">4.0 MB</span></div>' +
      '<div class="rl"><span>MLA 每 token 缓存</span><span class="rv">70 KB（约 1/57）</span></div>' +
      '<div class="rl"><span>V4.1-Flash 每 token 缓存</span><span class="rv">' + (890 * L * 1000 < 1e6 ? (890 * L * 1000 / 1e3).toFixed(1) + ' KB' : (890 * L * 1000 / 1e6).toFixed(1) + ' MB') + '（890 B）</span></div>' +
      '<div class="rl"><span>本长度下 MLA 相对密集注意力节省</span><span class="rv">' + (100 - 70.272 / 3997.696 * 100).toFixed(1) + ' %</span></div>' +
      '<div class="rl"><span>本长度下 V4.1-Flash 相对密集注意力节省</span><span class="rv">' + (100 - 890 / 3997696 * 100).toFixed(2) + ' %</span></div>' +
      '<div class="rl"><span>条形刻度</span><span class="rv plain">对数刻度（否则小值不可见）</span></div>';
  }
  sl.addEventListener('input', render);
  render();
})();

/* ============ 6 · 实验 04：MoE 路由 ============ */
(function(){
  var grid = $('#moeGrid'), btn = $('#moeBtn'), resetBtn = $('#moeReset');
  var loadEl = $('#moeLoad'), outEl = $('#moeOut'), balEl = $('#moeBalance');
  if(!grid || !btn) return;

  var N = 256, CLUSTERS = 4;
  var cells = [], base = [], cluster = [], bias = [], load = [], hits = [];
  for(var i = 0; i < N; i++){
    base.push(Math.random());
    cluster.push(i % CLUSTERS);
    bias.push(0); load.push(0); hits.push(0);
  }
  for(var j = 0; j < N; j++){
    var d = document.createElement('div');
    d.className = 'ex';
    d.setAttribute('title', '专家 ' + (j + 1) + ' · 集群 ' + (cluster[j] + 1));
    grid.appendChild(d);
    cells.push(d);
  }
  var chip = document.createElement('div');
  chip.className = 'tag acc';
  chip.style.marginBottom = '10px';
  chip.textContent = '共享专家 × 1：所有 token 都会经过';
  grid.parentNode.insertBefore(chip, grid);

  var CLU = ['集群 1', '集群 2', '集群 3', '集群 4'];
  var steps = 0;

  function paint(hotIdx){
    for(var i = 0; i < N; i++){
      var c = cells[i];
      var over = load[i] > 0 && load[i] > 2 * (steps ? steps * 8 / N : 1);
      var cls = 'ex';
      if(hotIdx && hotIdx.indexOf(i) >= 0) cls += ' hot';
      else if(over) cls += ' over';
      else if(load[i] === 0 && steps > 4) cls += ' under';
      c.className = cls;
    }
  }
  function renderLoad(){
    var sum = [0, 0, 0, 0], total = 0;
    for(var i = 0; i < N; i++){ sum[cluster[i]] += load[i]; total += load[i]; }
    var max = Math.max.apply(null, sum) || 1;
    loadEl.innerHTML = sum.map(function(s, k){
      return '<div class="bar-row" style="grid-template-columns:78px 1fr 74px">' +
        '<span class="bl">' + CLU[k] + '</span>' +
        '<span class="bt"><span class="bf ' + (s > max * 0.75 ? 'warn' : 'alt') + '" style="width:' + (s / max * 100) + '%"></span></span>' +
        '<span class="bv">' + (total ? (s / total * 100).toFixed(1) + ' %' : '—') + '</span></div>';
    }).join('');
    var used = 0; for(var q = 0; q < N; q++) if(load[q] > 0) used++;
    var avg = total ? total / N : 0;
    var mx = Math.max.apply(null, load);
    outEl.innerHTML =
      '<div class="rl"><span>第几次送入</span><span class="rv plain">第 ' + steps + ' 个 token</span></div>' +
      '<div class="rl"><span>本次激活</span><span class="rv">8 / 256 个路由专家 + 1 个共享专家</span></div>' +
      '<div class="rl"><span>累计被使用过的专家</span><span class="rv">' + used + ' / 256</span></div>' +
      '<div class="rl"><span>负载倾斜度（最忙 / 平均）</span><span class="rv">' + (avg ? (mx / avg).toFixed(1) + ' ×' : '—') + '</span></div>' +
      '<div class="rl"><span>对应真实模型的激活比例</span><span class="rv plain">37B / 671B ≈ 5.5 %</span></div>';
  }

  function step(){
    steps++;
    var c = Math.floor(Math.random() * CLUSTERS);
    var star = c + CLUSTERS * Math.floor(Math.random() * (N / CLUSTERS));
    var useBias = balEl && balEl.checked;
    var scored = [];
    for(var i = 0; i < N; i++){
      var s = base[i] + (cluster[i] === c ? 1.2 : 0) + (i === star ? 1.6 : 0) + (useBias ? bias[i] : 0);
      scored.push([i, s]);
    }
    scored.sort(function(a, b){ return b[1] - a[1]; });
    var hot = scored.slice(0, 8).map(function(p){ return p[0]; });
    hot.forEach(function(i){ load[i]++; hits[i]++; });

    if(useBias){
      for(var k = 0; k < N; k++){
        var target = steps * 8 / N;
        if(load[k] > target) bias[k] = clamp(bias[k] - 0.035, -0.9, 0.9);
        else bias[k] = clamp(bias[k] + 0.035, -0.9, 0.9);
      }
    }
    paint(hot);
    renderLoad();
  }
  btn.addEventListener('click', step);
  if(resetBtn) resetBtn.addEventListener('click', function(){
    steps = 0;
    for(var i = 0; i < N; i++){ load[i] = 0; bias[i] = 0; hits[i] = 0; cells[i].className = 'ex'; }
    renderLoad();
  });
  if(balEl) balEl.addEventListener('change', function(){ paint(null); });
  paint(null); renderLoad();
})();

/* ============ 7 · 实验 05：GRPO ============ */
(function(){
  var btn = $('#grpoBtn'), resetBtn = $('#grpoReset');
  var outEl = $('#grpoOut'), statEl = $('#grpoStat'), barsEl = $('#grpoBars');
  if(!btn || !outEl) return;

  var G = 8, round = 0, totR = 0, totN = 0;
  function rnd(){ return Math.random() < 0.5 ? 0 : 1; }

  function run(){
    round++;
    var p = clamp(0.34 + 0.055 * (round - 1), 0.34, 0.88);
    var rs = [], i;
    for(i = 0; i < G; i++) rs.push(Math.random() < p ? 1 : 0);
    if(rs.indexOf(1) < 0) rs[Math.floor(Math.random() * G)] = 1;   // 避免全错导致无对比信号
    var mean = rs.reduce(function(a, b){ return a + b; }, 0) / G;
    var varr = rs.reduce(function(a, b){ return a + Math.pow(b - mean, 2); }, 0) / G;
    var std = Math.sqrt(varr) || 1;
    var adv = rs.map(function(r){ return (r - mean) / std; });
    totR += rs.reduce(function(a, b){ return a + b; }, 0); totN += G;

    outEl.innerHTML = rs.map(function(r, k){
      return '<div class="sm ' + (r ? 'r1' : 'r0') + '">样本 ' + (k + 1) + '<span class="r">' + r + '</span>' +
        '<span style="color:var(--ink-4)">A=' + adv[k].toFixed(2) + '</span></div>';
    }).join('');

    statEl.innerHTML =
      '<div class="rl"><span>第几轮采样</span><span class="rv plain">第 ' + round + ' 轮</span></div>' +
      '<div class="rl"><span>组内平均奖励 mean</span><span class="rv">' + mean.toFixed(3) + '</span></div>' +
      '<div class="rl"><span>组内标准差 std</span><span class="rv">' + std.toFixed(3) + '（当基准用）</span></div>' +
      '<div class="rl"><span>本组答对</span><span class="rv">' + rs.filter(function(x){ return x === 1; }).length + ' / ' + G + '</span></div>' +
      '<div class="rl"><span>累计正确率</span><span class="rv">' + (totR / totN * 100).toFixed(1) + ' %</span></div>';

    barsEl.innerHTML = rs.map(function(r, k){
      var a = adv[k];
      var w = clamp(Math.abs(a) / 1.6 * 100, 4, 100);
      return '<div class="bar-row" style="grid-template-columns:78px 1fr 132px">' +
        '<span class="bl">样本 ' + (k + 1) + '</span>' +
        '<span class="bt"><span class="bf ' + (a >= 0 ? 'alt' : 'warn') + '" style="width:' + w + '%"></span></span>' +
        '<span class="bv" style="color:' + (a >= 0 ? 'var(--ok)' : 'var(--warn)') + '">' + (a >= 0 ? '概率↑ ' : '概率↓ ') + a.toFixed(2) + '</span></div>';
    }).join('');
  }
  btn.addEventListener('click', run);
  if(resetBtn) resetBtn.addEventListener('click', function(){
    round = 0; totR = 0; totN = 0;
    outEl.innerHTML = ''; barsEl.innerHTML = '';
    statEl.innerHTML = '<div class="rl"><span>状态</span><span class="rv plain">已重置，点击「采样一组回答」开始</span></div>';
  });
})();

/* ============ 8 · 实验 06：精度 ============ */
(function(){
  var tabs = $('#precTabs'), outEl = $('#precOut'), barsEl = $('#precBars');
  if(!tabs || !outEl) return;

  var P = [
    { n: 'FP32', s: 1, e: 8, m: 23, mem: 1, note: '传统全精度训练' },
    { n: 'BF16', s: 1, e: 8, m: 7, mem: 0.5, note: '当前训练基线：范围大、精度低' },
    { n: 'FP16', s: 1, e: 5, m: 10, mem: 0.5, note: '精度略高但范围小，容易溢出' },
    { n: 'FP8 · E4M3', s: 1, e: 4, m: 3, mem: 0.25, note: '范围小精度高，用于前向计算' },
    { n: 'FP4 · E2M1', s: 1, e: 2, m: 1, mem: 0.125, note: '必须配合分块缩放因子' }
  ];
  var cur = 1;
  tabs.innerHTML = P.map(function(p, i){
    return '<button data-i="' + i + '" class="' + (i === cur ? 'on' : '') + '">' + p.n + '</button>';
  }).join('');

  function render(){
    var p = P[cur];
    var digits = p.m * 0.30103;
    outEl.innerHTML =
      '<div class="rl"><span>位宽组成</span><span class="rv plain">1 符号 + ' + p.e + ' 指数 + ' + p.m + ' 尾数 = ' + (1 + p.e + p.m) + ' bit</span></div>' +
      '<div class="rl"><span>可表示的不同数值个数</span><span class="rv">2<sup>' + (1 + p.e + p.m) + '</sup> ≈ ' + Math.pow(2, 1 + p.e + p.m).toLocaleString('en-US') + '</span></div>' +
      '<div class="rl"><span>有效十进制精度（≈ 尾数位 × 0.301）</span><span class="rv">' + digits.toFixed(2) + ' 位</span></div>' +
      '<div class="rl"><span>指数位决定动态范围</span><span class="rv plain">' + p.e + ' 位' + (p.e <= 4 ? ' · 范围受限，需分块缩放' : ' · 范围充足') + '</span></div>' +
      '<div class="rl"><span>典型用途</span><span class="rv plain">' + p.note + '</span></div>';
    barsEl.innerHTML =
      '<div class="bar-row" style="grid-template-columns:158px 1fr 82px"><span class="bl" style="text-align:left">相对显存占用</span>' +
      '<span class="bt"><span class="bf alt" style="width:' + (p.mem * 100) + '%"></span></span><span class="bv">' + (p.mem * 100).toFixed(1) + ' %</span></div>' +
      '<div class="bar-row" style="grid-template-columns:158px 1fr 82px"><span class="bl" style="text-align:left">相对有效精度</span>' +
      '<span class="bt"><span class="bf" style="width:' + clamp(digits / 6.9 * 100, 3, 100) + '%"></span></span><span class="bv">' + digits.toFixed(2) + ' 位</span></div>';
    $$('button', tabs).forEach(function(b, i){ b.className = (i === cur ? 'on' : ''); });
  }
  tabs.addEventListener('click', function(e){
    var b = e.target.closest('button');
    if(!b) return;
    cur = +b.getAttribute('data-i');
    render();
  });
  render();
})();

/* ============ 9 · 实验 07：DSA 复杂度 ============ */
(function(){
  var slL = $('#dsaL'), slK = $('#dsaK'), svg = $('#dsaChart'), outEl = $('#dsaOut');
  if(!slL || !svg) return;

  var X0 = 4, X1 = 1024;
  var LX = Math.log10(X1 / X0);
  var MAXSTD = Math.pow(X1 / X0, 2);
  var LY = Math.log10(MAXSTD);

  function px(l){ return 70 + (Math.log10(l) - Math.log10(X0)) / LX * 900; }
  function py(v){ return 262 - clamp(Math.log10(Math.max(v, 1e-6)) / LY, 0, 1) * 228; }

  function render(){
    var L = +slL.value, K = +slK.value;
    $('#dsaLV').textContent = L >= 1024 ? '1M token' : L + 'K token';
    $('#dsaKV').textContent = K + 'K token';

    var stdP = '', spP = '', i, t, l, s, sp;
    for(i = 0; i <= 140; i++){
      t = i / 140; l = X0 * Math.pow(X1 / X0, t);
      s = Math.pow(l / X0, 2);
      sp = (l * K) / (X0 * X0);
      stdP += (i ? ' L' : 'M') + px(l).toFixed(1) + ',' + py(s).toFixed(1);
      spP  += (i ? ' L' : 'M') + px(l).toFixed(1) + ',' + py(sp).toFixed(1);
    }

    var grid = '';
    [1, 10, 100, 1000, 10000].forEach(function(v){
      var y = py(v);
      if(y > 30 && y < 264){
        grid += '<line x1="70" y1="' + y.toFixed(1) + '" x2="970" y2="' + y.toFixed(1) + '" stroke="#eaeef2"/>';
        grid += '<text x="62" y="' + (y + 4).toFixed(1) + '" text-anchor="end" font-size="10.5" fill="#8b949e" font-family="ui-monospace, monospace">' +
          (v >= 1000 ? (v / 1000) + 'K' : v) + '</text>';
      }
    });
    [4, 16, 64, 256, 1024].forEach(function(l){
      var x = px(l);
      grid += '<line x1="' + x.toFixed(1) + '" y1="34" x2="' + x.toFixed(1) + '" y2="262" stroke="#F1EDE4"/>';
      grid += '<text x="' + x.toFixed(1) + '" y="280" text-anchor="middle" font-size="10.5" fill="#8b949e" font-family="ui-monospace, monospace">' +
        (l >= 1024 ? '1M' : l + 'K') + '</text>';
    });

    var stdNow = Math.pow(L / X0, 2), spNow = (L * K) / (X0 * X0);
    var mx = px(L), myStd = py(stdNow), mySp = py(spNow);
    var crossX = px(K), showCross = (K > X0 && K < X1);

    svg.innerHTML = grid +
      '<path d="' + stdP + '" fill="none" stroke="#a8611f" stroke-width="2.2"/>' +
      '<path d="' + spP + '" fill="none" stroke="#1b4f8a" stroke-width="2.2"/>' +
      (showCross ? '<line x1="' + crossX.toFixed(1) + '" y1="34" x2="' + crossX.toFixed(1) + '" y2="262" stroke="#2f6fb8" stroke-dasharray="3 3" opacity=".6"/>' : '') +
      '<line x1="' + mx.toFixed(1) + '" y1="34" x2="' + mx.toFixed(1) + '" y2="262" stroke="#17181a" stroke-dasharray="4 3" opacity=".45"/>' +
      '<circle cx="' + mx.toFixed(1) + '" cy="' + myStd.toFixed(1) + '" r="5" fill="#fff" stroke="#a8611f" stroke-width="2.4"/>' +
      '<circle cx="' + mx.toFixed(1) + '" cy="' + mySp.toFixed(1) + '" r="5" fill="#fff" stroke="#1b4f8a" stroke-width="2.4"/>' +
      '<text x="80" y="52" font-size="11.5" fill="#a8611f" font-family="ui-monospace, monospace">标准注意力 ∝ L²</text>' +
      '<text x="80" y="72" font-size="11.5" fill="#1b4f8a" font-family="ui-monospace, monospace">DSA 稀疏注意力 ∝ L × k</text>';

    var ratio = stdNow / spNow;
    var save = (1 - spNow / stdNow) * 100;
    outEl.innerHTML =
      '<div class="rl"><span>当前上下文长度</span><span class="rv plain">' + (L >= 1024 ? '1M token' : L + 'K token') + '</span></div>' +
      '<div class="rl"><span>Top-K 预算</span><span class="rv plain">' + K + 'K token</span></div>' +
      '<div class="rl"><span>标准注意力相对计算量</span><span class="rv plain">' + stdNow.toFixed(0) + ' ×（以 4K 为 1）</span></div>' +
      '<div class="rl"><span>稀疏注意力相对计算量</span><span class="rv plain">' + spNow.toFixed(0) + ' ×</span></div>' +
      '<div class="rl"><span>稀疏带来的计算量倍数</span><span class="rv">' + (ratio >= 1 ? '降到 1/' + ratio.toFixed(0) : '反而增加 ' + (1 / ratio).toFixed(1) + ' 倍') + '</span></div>' +
      '<div class="rl"><span>节省比例</span><span class="rv">' + (save > 0 ? save.toFixed(1) + ' %' : '0 %（此长度下不划算）') + '</span></div>' +
      '<div class="rl"><span>结论</span><span class="rv plain">' + (L > K ? '当前长度已超过 Top-K 预算，稀疏划算' : '长度还没超过 Top-K 预算，全覆盖更便宜') + '</span></div>';
  }
  slL.addEventListener('input', render);
  slK.addEventListener('input', render);
  render();
})();

/* ============ 10 · 实验 08：推测解码 ============ */
(function(){
  var btn = $('#specBtn'), resetBtn = $('#specReset');
  var outEl = $('#specOut'), tokEl = $('#specTokens'), statEl = $('#specStat');
  if(!btn || !outEl) return;

  var POOL = ['模型', '通过', '稀疏', '注意力', '把', '缓存', '压缩', '成', '一个', '潜向量', '从而', '显著', '降低', '显存', '占用'];
  var WRONG = ['模板', '通果', '稀梳', '注意利', '吧', '缓冲', '压宿', '城', '一各', '潜向亮', '从儿', '显箸', '降底', '显卡', '占佣'];
  var forwards = 0, produced = 0, text = '';

  function run(){
    forwards++;
    var drafts = '', ok = 0, i, input = [], output = [];
    for(i = 0; i < 5; i++){
      var idx = Math.floor(Math.random() * POOL.length);
      input.push(idx);
      var good = Math.random() < 0.76;
      output.push(good);
      if(good && ok === i) ok++;
    }
    var accepted = ok;
    var total = accepted + 1;             // 首个正确 token 由大模型给出
    produced += total;
    var picked = Math.floor(Math.random() * POOL.length);
    text += POOL[picked];
    // 追加被接受的部分
    for(i = 1; i < accepted; i++) text += POOL[Math.floor(Math.random() * POOL.length)];
    tokEl.textContent = text;

    drafts = input.map(function(idx, k){
      var state = output[k] && k < accepted;
      return '<div class="sm ' + (state ? 'r1' : 'r0') + '" style="padding:10px 6px;min-width:82px">' +
        (state ? POOL[idx] : '<s style="opacity:.6">' + POOL[idx] + '</s>') +
        '<span class="r" style="font-size:13px">' + (state ? '接受' : '驳回') + '</span></div>';
    }).join('');
    outEl.innerHTML = drafts +
      '<div class="sm" style="padding:10px 6px;min-width:96px;border-color:var(--accent-line);background:var(--accent-soft)">' +
      '第 ' + (accepted + 1) + ' 位<span class="r" style="font-size:13px;color:var(--accent)">大模型给出</span></div>';

    statEl.innerHTML =
      '<div class="rl"><span>本次草稿长度</span><span class="rv plain">5 个 token</span></div>' +
      '<div class="rl"><span>验证通过</span><span class="rv">' + accepted + ' 个</span></div>' +
      '<div class="rl"><span>本次前向产出</span><span class="rv">' + total + ' 个 token（1 次前向）</span></div>' +
      '<div class="rl"><span>累计：前向次数 / 产出 token</span><span class="rv plain">' + forwards + ' 次 / ' + produced + ' 个</span></div>' +
      '<div class="rl"><span>平均每次前向产出</span><span class="rv">' + (produced / forwards).toFixed(2) + ' 个 token</span></div>' +
      '<div class="rl"><span>相对逐 token 生成的加速上限</span><span class="rv">约 ' + (produced / forwards).toFixed(2) + ' ×</span></div>';
  }
  btn.addEventListener('click', run);
  if(resetBtn) resetBtn.addEventListener('click', function(){
    forwards = 0; produced = 0; text = ''; tokEl.textContent = ''; outEl.innerHTML = '';
    statEl.innerHTML = '<div class="rl"><span>状态</span><span class="rv plain">已重置</span></div>';
  });
})();

/* ============ 11 · 实验 09：推理强度 ============ */
(function(){
  var sl = $('#eff'), barsEl = $('#effBars'), outEl = $('#effOut');
  if(!sl || !barsEl) return;

  function render(){
    var e = +sl.value;
    var t = (e - 25) / 75;
    var deep = 66.0 + t * (74.2 - 66.0);
    var term = 82.4 + t * (90.6 - 82.4);
    var mul = 1 + t * 1.5;
    $('#effV').textContent = e + ' / 100';

    barsEl.innerHTML =
      '<div class="bar-row" style="grid-template-columns:150px 1fr 92px"><span class="bl" style="text-align:left">DeepSWE v1.1</span>' +
      '<span class="bt" style="height:18px"><span class="bf alt" style="width:' + deep.toFixed(1) + '%"></span></span>' +
      '<span class="bv">' + deep.toFixed(1) + ' %</span></div>' +
      '<div class="bar-row" style="grid-template-columns:150px 1fr 92px"><span class="bl" style="text-align:left">Terminal-Bench 2.1</span>' +
      '<span class="bt" style="height:18px"><span class="bf alt" style="width:' + term.toFixed(1) + '%"></span></span>' +
      '<span class="bv">' + term.toFixed(1) + ' %</span></div>' +
      '<div class="bar-row" style="grid-template-columns:150px 1fr 92px"><span class="bl" style="text-align:left">输出 token 消耗</span>' +
      '<span class="bt" style="height:18px"><span class="bf warn" style="width:' + (mul / 2.5 * 100).toFixed(1) + '%"></span></span>' +
      '<span class="bv">' + mul.toFixed(2) + ' ×</span></div>';

    outEl.innerHTML =
      '<div class="rl"><span>当前推理强度</span><span class="rv plain">' + e + '（官方支持 1–100 连续可调）</span></div>' +
      '<div class="rl"><span>相对最低档多花的输出 token</span><span class="rv">' + ((mul - 1) * 100).toFixed(0) + ' %</span></div>' +
      '<div class="rl"><span>相对最低档提升的准确率</span><span class="rv">+ ' + (deep - 66.0).toFixed(1) + ' 个百分点（DeepSWE）</span></div>' +
      '<div class="rl"><span>边际效率</span><span class="rv plain">' + ((deep - 66.0) / Math.max(mul - 1, 0.01)).toFixed(1) + ' 个百分点 / 每 1× token</span></div>' +
      '<div class="rl"><span>口径</span><span class="rv plain">两端点为官方披露值，中间为线性插值示意</span></div>';
  }
  sl.addEventListener('input', render);
  render();
})();

})();
</script>
