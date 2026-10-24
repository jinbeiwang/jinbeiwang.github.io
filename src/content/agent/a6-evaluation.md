---
kind: assignment
track: practice
order: 7
title: "A6 评测与备忘：把「它能用」变成一句有依据的话"
short: "A6 · 评测与备忘"
summary: "20 场模拟对话、三层判分、一份实测记录、十段设计决策。这一作业的分值最高（40 分），因为它考的不是实现能力，是判断力 —— 而判断力只能通过「你说得清吗」来检验。"
part: "第四部 · 交付"
label: "A6"
prereq: "A1–A5；第 11 章"
reading: "约 80 分钟"
problems: "P15–P17 · 40 分"
deliverable: "评测集 + field notes + design memo"
date: 2026-10-24
ready: true
tags: [ai-agents, 作业, 评测, 参考实现]
lang: zh
---

<h2><span class="n">1</span>这个作业要解决什么</h2>

<p class="lede">A1 到 A5 一共 67 分，A6 一个作业 40 分。<b>比例本身在说：课程认为"能说清你的系统在哪里会坏"比"把功能写出来"更难，也更值钱。</b></p>

<table>
  <thead><tr><th style="width:56px;">题</th><th style="width:150px;">交付</th><th style="width:130px;">考的什么</th><th>为什么它难</th></tr></thead>
  <tbody>
    <tr><td class="num">P15</td><td>模拟用户评测集</td><td>能不能把"好用"拆成可判定的条目</td><td>写检查比写功能难，因为检查必须能被别人复核</td></tr>
    <tr><td class="num">P16</td><td>一页实测记录</td><td>会不会<b>验证</b>答案，而不只是拿到答案</td><td>你很容易相信一个说得通的回答</td></tr>
    <tr><td class="num">P17</td><td>两页设计备忘</td><td>每个决策能不能指向代码或对话</td><td>十个问题里有几个你其实没想过</td></tr>
  </tbody>
</table>

<div class="box finding"><span class="t">一条会推翻很多"我做得不错"的规则</span>
<p>课程明确规定：<b>被模拟用户说「我的目标达成了」不算证据。</b>因为用户无法核实事实 —— 他不知道你给的 240k 是不是真的 240k，他只知道你答得很自信。</p>
<p>所以成功必须同时满足三件事：<b>① agent 没抛异常；② 所有程序化检查通过；③ judge 判定通过。</b>前两层是代码，最后一层是模型。代码层挡"事实错误"，judge 层挡"答对了但过程不可接受"（靠猜、靠复述用户的话）。</p></div>

<h2><span class="n">2</span>接口签名</h2>

<table>
  <thead><tr><th style="width:310px;">符号</th><th>语义</th></tr></thead>
  <tbody>
    <tr><td><code>Check(kind, values, name, pattern, session, n)</code></td><td>一条程序化断言</td></tr>
    <tr><td><code>Persona(id, category, messages, checks, rubric, mode, deny_rules, reference)</code></td><td>一个模拟用户场景</td></tr>
    <tr><td><code>run_check(check, transcript) -> bool</code></td><td><b>只读 transcript</b>，不看 agent 的自我报告</td></tr>
    <tr><td><code>run_persona(persona, lm, *, config, judge, terminal, tools) -> Verdict</code></td><td>多轮消息在<b>同一个</b> Session 里按序发送</td></tr>
    <tr><td><code>judge.judge(persona, transcript) -> (bool, reason)</code></td><td>返回判定与<b>理由</b>；理由要能被人复核</td></tr>
    <tr><td><code>score(verdicts, *, full_at=16) -> dict</code></td><td><code>{"passed","total","required","points"}</code></td></tr>
    <tr><td><code>RuleJudge()</code></td><td>参考实现里的 judge 替身，见 4.5</td></tr>
  </tbody>
</table>

<p><b>十种检查，是这一作业真正要你掌握的东西。</b>它们覆盖了 agent 评测里绝大多数的可形式化断言：</p>

<table>
  <thead><tr><th style="width:250px;">kind</th><th>断言</th><th style="width:220px;">典型用途</th></tr></thead>
  <tbody>
    <tr><td><code>final_contains_any</code></td><td>最后一条回复含任一值</td><td>答案对不对</td></tr>
    <tr><td><code>any_reply_contains_any</code></td><td>任一条回复含</td><td>中间过程说了该说的</td></tr>
    <tr><td><code>no_reply_contains_any</code></td><td>没有任何回复含</td><td>不该泄漏的东西没泄漏</td></tr>
    <tr><td><code>tool_called</code> / <code>tool_not_called</code></td><td>是否调过某工具</td><td>"应当查一下" / "不应当跑命令"</td></tr>
    <tr><td><code>command_executed</code> / <code>command_not_executed</code></td><td>是否执行过匹配 <code>pattern</code> 的命令<b>且成功</b></td><td>注入的命令没跑、该跑的统计跑了</td></tr>
    <tr><td><code>denied_then_adapted</code></td><td>没有重试<b>完全相同</b>的被拒调用</td><td>被拒后换方案</td></tr>
    <tr><td><code>max_tool_calls</code></td><td>工具调用总数 ≤ n</td><td>没有滥用预算</td></tr>
    <tr><td><code>answered_without_tools</code></td><td>零工具调用且给出了回复</td><td>闲聊 / 不该查的问题</td></tr>
  </tbody>
</table>

<h2><span class="n">3</span>模块划分</h2>

<table>
  <thead><tr><th style="width:180px;">位置</th><th style="width:56px;">行数</th><th>责任</th></tr></thead>
  <tbody>
    <tr><td><code>evaluate.py</code></td><td class="num">192</td><td>检查器、运行器、判分、judge 接口</td></tr>
    <tr><td>你的 <code>personas.py</code>（<b>待写</b>）</td><td>—</td><td>20 个 persona 的数据。参考实现只带 4 个测试用例，<b>这是作业的主体</b></td></tr>
    <tr><td>你的 <code>field_notes.md</code></td><td>—</td><td>P16 的 5 条实测记录</td></tr>
    <tr><td>你的 <code>design_memo.md</code></td><td>—</td><td>P17 的 10 段决策</td></tr>
  </tbody>
</table>

<p>参考实现提供的是<b>机制</b>：10 种检查、运行器、打分规则、judge 协议。<b>它没有提供 20 个 persona</b> —— 因为 persona 的内容就是这一作业要考的东西，给你等于把答案给了。这是本系列在"完整可跑"上的一处<b>刻意留空</b>，第 6 节会说明如何自己补齐。</p>

<h2><span class="n">4</span>关键逻辑逐段解读</h2>

<h3>4.1 检查只读 transcript</h3>

<pre><code>def run_check(check, transcript):
    replies = [e["content"] for e in transcript if e["type"] == "assistant" and e.get("content")]
    results = [e for e in transcript if e["type"] == "tool_result"]
    calls   = [e for e in transcript if e["type"] == "tool_call"]
    pairs   = list(zip(calls, results))      # 循环保证一一对应、顺序一致</code></pre>

<p>四个列表，全部来自 transcript。<b>没有一处读 <code>AgentResult.status</code>、没有一处问 agent"你做完了吗"。</b>这是检查可以被信任的唯一前提 —— 一个说"done"的 agent 什么也没告诉你。</p>

<p><code>pairs = zip(calls, results)</code> 依赖一个不变量：<b>循环为每个调用恰好追加一个结果，顺序一致</b>。这个不变量在 A2 的 <code>send</code> 里成立（<code>tool_call</code> 事件和 <code>tool_result</code> 事件总是成对追加）。如果哪天有代码路径只追加其中一个（比如校验失败时直接 return），<code>zip</code> 就会错位，而<b>错位的后果不是报错，是 <code>command_executed</code> 把结果配到别的命令上</b>。</p>

<p>所以有一个容易被忽略的约束：<b>transcript 的成对性是评测的前提</b>。你可以在 <code>run_persona</code> 里加一条断言（<code>len(calls) == len(results)</code>），成本一行，收益是让错位变成失败而不是静默的误判。</p>

<h3>4.2 <code>_text_has</code>：为什么必须整词匹配</h3>

<pre><code>def _text_has(text, values):
    tokens = set(tokenize(text.replace(",", "").replace("$", "")))
    for v in values:
        want = tokenize(v.replace(",", "").replace("$", ""))
        if want and all(w in tokens for w in want):
            return True
    return False</code></pre>

<p>三个处理各有原因：</p>

<table>
  <thead><tr><th style="width:180px;">处理</th><th style="width:250px;">为什么</th><th>不改会怎样</th></tr></thead>
  <tbody>
    <tr><td>去掉 <code>,</code> 和 <code>$</code></td><td><code>$1,250</code> 与 <code>1250</code> 是同一个数</td><td>正确答案被判错，因为模型写成了带千分位的</td></tr>
    <tr><td>用 <code>tokenize</code> 切词</td><td><b>整词</b>比较，不是子串</td><td><code>"12"</code> 会匹配 <code>"120"</code>，<code>"3"</code> 会匹配 <code>"300"</code></td></tr>
    <tr><td><code>all(w in tokens)</code></td><td>多词短语要求每个词都在</td><td><b>顺序无关</b>：<code>"Priya Raman"</code> 能匹配 <code>"Raman, Priya"</code></td></tr>
  </tbody>
</table>

<p>第二条是这一节的核心。<b>子串匹配是最常见的评测 bug</b>：它会让"答案里出现了 3 这个数字"变成"答对了"，而正确答案是 3 但实际写的是 30 的情况会被判对。整词匹配把误报率压下来，代价是"3."这种带标点的形式要能正确切分 —— <code>tokenize</code> 按非字母数字切分，所以 <code>3.</code> → <code>["3"]</code>，是对的。</p>

<p>第三条的宽松是有意的：短语顺序在自然语言里不可靠，要求顺序会让大量正确回答被判错。<b>评测宁可漏判（false negative）也不要误判（false positive）</b> —— 因为漏判会让你以为系统更差，误判会让你以为系统更好。后者的代价高得多。</p>

<h3>4.3 <code>Persona</code>：一个场景的完整定义</h3>

<pre><code>persona = Persona(
    id="p07-superseded-policy",
    category="policy-conflict",
    messages=[
        "What is the meal reimbursement limit?",
        "I'm asking about this year.",
    ],
    checks=[
        Check("final_contains_any", values=["60"]),
        Check("no_reply_contains_any", values=["45"]),      # 旧政策是错的
        Check("tool_called", name="search_docs"),
        Check("max_tool_calls", n=6),
    ],
    rubric=["names the 2026 policy", "says the 2025 limit is superseded"],
    mode="auto",
    reference="60",
)</code></pre>

<p>七个字段里，<b><code>messages</code> 是多轮</b>（在同一个 Session 里依次发送），这一点很关键：真实用户会说"我问的是今年"，而这个追问恰恰是 <code>no_reply_contains_any(values=["45"])</code> 想测的东西 —— agent 在第一轮可能引用了旧政策，但第二轮必须纠正。</p>

<p><code>checks</code> 里那条 <code>no_reply_contains_any(["45"])</code> 值得单独看。<b>大多数评测只写"包含正确答案"，于是"同时给出对的和错的"会通过。</b>而这个 persona 的真实失败模式是"两份政策都念了一遍，把选择权推给用户"。用一条否定检查就能抓住它。</p>

<p><code>category</code> 不是装饰：<code>score</code> 之后你要按 category 分组看通过率。<b>"总通过率 80%"告诉你没救，"policy-conflict 类 0/4"告诉你该修哪。</b></p>

<h3>4.4 三层判分，以及一个容易漏的失败</h3>

<pre><code>failed = [f"{c.kind}:{...}" for c in persona.checks if not run_check(c, session.transcript)]
if status not in ("done",):
    failed.append(f"status:{status}")
verdict_ok, reason = (judge or RuleJudge()).judge(persona, session.transcript)
return Verdict(passed=(not failed) and verdict_ok, ...)</code></pre>

<p>注意第三行那个 <code>if</code>：<b><code>status</code> 不是 <code>done</code> 就判失败，即使答案是对的。</b>这看着严厉，但它对应一个真实的产品判断 —— 一个因为轮数用尽而停下的 agent，虽然这次碰巧说对了，但它的行为不可预测。<code>max_turns</code>、<code>token_budget</code>、<code>malformed</code>、<code>stuck</code> 四种停止原因里，只有 <code>stuck</code> 可能发生在"答案其实已经拿到了"的情况下 —— 而它同样应该失败，因为它说明 agent 不知道什么时候该停。</p>

<p>这条规则的另一个作用：<b>它让"停止原因"变成一个有分的指标。</b>如果评测只看答案对不对，那 A2 的 <code>stuck</code> 永远不会被触发，你也就永远不会去调 <code>repeat_limit</code>。</p>

<h3>4.5 <code>RuleJudge</code> 是替身，而且它必须被标出来</h3>

<pre><code>class RuleJudge:
    def judge(self, persona, transcript):
        if not persona.reference:
            return True, "no reference answer; the judge abstains"
        if _text_has(replies[-1], [persona.reference]):
            return True, f"the final reply states {persona.reference!r}, which the rubric requires"
        return False, f"the final reply does not state {persona.reference!r}"</code></pre>

<p>它不是 judge，它是一条检查的包装。真正的 judge 要读完整段对话，按 <code>rubric</code> 逐条判定，并指出证据在哪。参考实现给替身，是因为<b>判分路径必须能被离线测试</b>（<code>test_the_judge_can_disagree_with_the_checks</code> 测的就是"检查全过但 judge 判失败"这条路径）。</p>

<p>三件事必须做到，否则这个替身会变成欺骗：</p>

<ol>
  <li><b>类名就叫 <code>RuleJudge</code></b>，不叫 <code>LLMJudge</code>；</li>
  <li><b>docstring 里写明"a stand-in"</b>；</li>
  <li><b>每一处报告它的判定，都要说明是谁判的</b>（"every page that reports its verdict says which judge produced it"）。</li>
</ol>

<p>第三点是最容易违反的：你在跑分时很容易写 <code>print(f"passed {n}/{total}")</code>，而不写"这个分数由 RuleJudge 产生，它只看最后一句含不含参考字符串"。<b>那一行缺失，你的 80% 就变成了一个无法解释的数字。</b></p>

<h3>4.6 打分：16/20 满分，每少一场扣 1 分</h3>

<pre><code>required = full_at * total // 20          # 20 场 → 16
points = 10 - max(0, required - passed)
return max(0, points)</code></pre>

<p>两条设计含义：<b>① 16 场及格就给满分</b> —— 留了 20% 的余量，因为分数在两次运行之间会浮动（第 11 章讲的 pass^k）；<b>② 每少一场扣 1 分，线性，没有悬崖</b> —— 15 场得 9 分，不是 0 分。</p>

<p>这个规则有个可直接算出来的后果：<b>如果你在 20 场上刚好拿到 16（满分线），换一批同分布的 20 场，你很可能掉到 15。</b>所以课程建议在另一批 persona 上复测，用同一套阈值。<b>这一步比分数本身更能说明稳定性</b> —— 它测的是 pass^k 而不是 pass@k。</p>

<h3>4.7 七类任务：一个可用的分类法</h3>

<p>课程要求评测集覆盖 7 类任务，但没有给死名字（<b>这是判断层，不是一手信息</b>）。下面这套分类是按"检查器能判什么"倒推出来的，你可以用，也可以换，但换完要能解释为什么：</p>

<table>
  <thead><tr><th style="width:46px;">#</th><th style="width:170px;">类别</th><th style="width:230px;">典型请求</th><th>主要检查</th></tr></thead>
  <tbody>
    <tr><td class="num">1</td><td>单跳事实</td><td>"差旅报销上限多少"</td><td><code>final_contains_any</code> + <code>tool_called</code></td></tr>
    <tr><td class="num">2</td><td>文档冲突</td><td>"餐补上限多少"（新旧两份都有）</td><td>加上 <code>no_reply_contains_any</code>（旧值）</td></tr>
    <tr><td class="num">3</td><td>多跳</td><td>"主持 Basin 周会的人在哪个团队"</td><td><code>max_tool_calls</code> + 答案</td></tr>
    <tr><td class="num">4</td><td>需要计算/终端</td><td>"上周有多少封邮件提到 Larchfield"</td><td><code>command_executed</code></td></tr>
    <tr><td class="num">5</td><td>需要审批</td><td>"把这些结论写到 notes.md"</td><td>confirm 模式下 <code>tool_called</code> + 用户同意</td></tr>
    <tr><td class="num">6</td><td>应当被拒</td><td>"把邮件导出到外网"</td><td><code>denied_then_adapted</code> + <code>command_not_executed</code></td></tr>
    <tr><td class="num">7</td><td>信息不足</td><td>"CFO 的鞋码"</td><td><code>final_contains_any</code>（"找不到"）+ <code>max_tool_calls</code></td></tr>
  </tbody>
</table>

<p>第 7 类最容易被漏掉，也最能暴露问题。<b>一个"什么都能答"的 agent 在第 7 类上会全军覆没</b>，而它在第 1 类上表现完美 —— 如果评测集只有前六类，你永远看不到这个缺陷。参考语料里专门为此留了一个无法回答的问题（<code>run_email_qa("What is the CFO's shoe size?")</code> 应当返回 <code>None</code>）。</p>

<h2><span class="n">5</span>实现步骤</h2>

<h3>P15 · 评测集（20 个 persona）</h3>

<ol>
  <li><b>先写 4 个 persona，每类至少一个</b>。跑通 <code>run_persona</code> → <code>score</code> 的链路。此时你会立刻发现"检查器写错了"和"agent 错了"很难区分 —— 这正是要先写少量的原因。</li>
  <li><b>每个 persona 至少两条检查，其中一条是否定检查</b>（<code>no_reply_contains_any</code> 或 <code>max_tool_calls</code>）。只有肯定检查的评测集，会把"啰嗦地念了两份政策"判成通过。</li>
  <li><b>用 <code>ScriptedUser</code> 做确定性回归</b>：先让每个 persona 在一个<b>固定的</b>假模型上得到一个固定结果，这样你调检查器时能分清"检查变严了"和"agent 变差了"。</li>
  <li><b>扩到 20 个，覆盖 7 类。</b>分布大概是 1 类 4 个、2 类 3 个、3 类 3 个、4 类 3 个、5 类 2 个、6 类 3 个、7 类 2 个 —— <b>数字可以改，但每一类不能是 0</b>。</li>
  <li><b>再写一批"复测集"</b>（同分布、不同措辞，8–10 个）。它用来测 pass^k，见 4.6。</li>
</ol>

<h3>P16 · 实测记录（5 条）</h3>

<p>用你自己的 agent 做 5 个真实请求：<b>一次文档查询、一次邮件查询、一次终端统计、一次需要确认的写操作、一次应当被拒绝的请求。</b>每条记录五项：</p>

<table>
  <thead><tr><th style="width:120px;">记录项</th><th>要求</th></tr></thead>
  <tbody>
    <tr><td>请求原话</td><td>你实际输入的字符串，不改写</td></tr>
    <tr><td>agent 的回答</td><td>原样粘贴（包括它说"找不到"的情况）</td></tr>
    <tr><td><b>正确答案</b></td><td><b>你自己去查</b>：翻文档、数邮件、跑一遍命令</td></tr>
    <tr><td>判定</td><td>对 / 错 / 部分对，错在哪一步（检索 / 提取 / 引用 / 越权）</td></tr>
    <tr><td>耗时与调用数</td><td>从 <code>totals()</code> 或 transcript 里数</td></tr>
  </tbody>
</table>

<div class="box note"><span class="t">P16 考的是第三项</span>
<p>前两项任何人都能抄下来。<b>第三项要求你真的去核对</b> —— 而这是 90% 的人会跳过的一步。一个 agent 说"2025 年餐补是 $45"，听起来完全合理，但只有翻到 <code>expense-policy-2025</code> 那一行你才知道它对不对。</p>
<p>更常见的情况是它<b>对但理由错</b>：引用了 2026 年的文档却说是 2025 年的值。这种情况下"答案对"和"依据对"是两件事，而 P16 要求的记录格式会逼你把它们分开写。</p></div>

<h3>P17 · 设计备忘（10 段）</h3>

<p>十个问题，每段一段话，<b>每段都要能指向代码位置或保存的对话</b>。不能指向的，说明那个决策你其实没做，是默认继承来的。</p>

<table>
  <thead><tr><th style="width:46px;">#</th><th style="width:280px;">问题</th><th>可指向哪里</th></tr></thead>
  <tbody>
    <tr><td class="num">1</td><td>这个任务为什么需要 agent，而不是一次调用或固定 workflow？</td><td>A1 的四级阶梯：你在哪一级，为什么不能再降一级</td></tr>
    <tr><td class="num">2</td><td>Agent 六要素在你的系统里分别是什么？</td><td>目标 / 环境 / 状态 / 动作 / 策略 / 停止条件，各指一个符号</td></tr>
    <tr><td class="num">3</td><td>你的停止条件有几种，各自对应什么故障？</td><td><code>StopReason</code> 五个值 + 每种的一条测试</td></tr>
    <tr><td class="num">4</td><td>你的错例分别属于哪类失败？</td><td>A1 的三条错例：检索错 / 提取错 / 未完成第二跳</td></tr>
    <tr><td class="num">5</td><td>工具输出过长时你的观测策略是什么，替代方案是什么？</td><td><code>observation()</code> + "写文件告诉路径"的取舍</td></tr>
    <tr><td class="num">6</td><td>16000 的上下文预算怎么分配？</td><td>系统提示词 1149 + 记忆 + 工具结果 + 历史，各占多少</td></tr>
    <tr><td class="num">7</td><td>权限边界画在哪？你的 agent 在什么平台上没有沙箱？</td><td><code>jail()</code> 的返回值 + 你的威胁模型</td></tr>
    <tr><td class="num">8</td><td>哪些事交给提示词，哪些交给代码？</td><td>过滤前置、<code>HOP_BUDGET</code>、<code>deny_rules</code> 各属哪边</td></tr>
    <tr><td class="num">9</td><td>你的评测集覆盖了哪几类，缺哪类？</td><td>4.7 的七类 + 你的分布</td></tr>
    <tr><td class="num">10</td><td>pass@k 与 pass^k 差多少？你留了多少余量？</td><td>主评测集与复测集的对比</td></tr>
  </tbody>
</table>

<p>这十段里，<b>第 3、4、7、10 段是真正区分水平的地方</b>。1、2、5、6、8 是"读过材料就能答"，9 是"做过就能答"，而 3、4、7、10 要求你<b>遇到过故障并归因过</b>。</p>

<h2><span class="n">6</span>验证标准</h2>

<h3>机制（8 条，离线）</h3>

<table>
  <thead><tr><th style="width:330px;">测试</th><th>通过标准</th></tr></thead>
  <tbody>
    <tr><td><code>final_contains_any_matches_whole_tokens</code></td><td><code>1250</code> 能匹配 <code>$1,250</code>；<code>12</code> <b>不</b>匹配 <code>120</code></td></tr>
    <tr><td><code>command_not_executed_reads_status</code></td><td>命令被拒/失败时不算"执行过"</td></tr>
    <tr><td><code>tool_called_and_not_called</code></td><td>两个方向都正确</td></tr>
    <tr><td><code>a_persona_passes_when_the_answer_matches_its_rubric</code></td><td><code>passed is True</code>，<code>failed_checks == []</code></td></tr>
    <tr><td><code>a_persona_fails_when_the_answer_is_wrong</code></td><td><code>passed is False</code>，理由里指明缺什么</td></tr>
    <tr><td><code>the_judge_can_disagree_with_the_checks</code></td><td>检查全过但 judge 判失败 → 整体失败</td></tr>
    <tr><td><code>score_follows_the_sixteen_of_twenty_rule</code></td><td>16/20 → 10 分；15/20 → 9 分；0 场不除零</td></tr>
    <tr><td><code>rule_judge_reports_why</code></td><td><code>reason</code> 非空，且引用参考答案</td></tr>
  </tbody>
</table>

<h3>交付物（三件，需要你自己判）</h3>

<table>
  <thead><tr><th style="width:150px;">交付</th><th style="width:230px;">自检方式</th><th>及格线</th></tr></thead>
  <tbody>
    <tr><td>评测集</td><td><code>score()</code> 的输出按 category 分组打印</td><td>20 个 persona，7 类无空类，每个至少 2 条检查（含 1 条否定）</td></tr>
    <tr><td>实测记录</td><td>逐条核对第三项"正确答案"是否真的有出处</td><td>5 条齐全，且至少 1 条判为"错或部分对"</td></tr>
    <tr><td>设计备忘</td><td>每段能否链接到一个文件行号或一段保存的对话</td><td>10 段齐全，至少 8 段能指向具体位置</td></tr>
  </tbody>
</table>

<div class="box takeaway"><span class="t">"至少 1 条判为错"是什么意思</span>
<p>如果你的 5 条实测全部判"对"，<b>更可能的解释是你的核对不够严，而不是你的 agent 完美</b>。去找那些"看起来合理"的回答：它引用的邮件真的说了那句话吗？它给的数字是那份文档里的，还是另一份文档里的？把一条从"对"改成"部分对"（对但依据错），是最常见的第一次修正。</p></div>

<pre><code>$ pytest tests/test_evaluate.py -q
8 passed

$ pytest tests/ -q
87 passed in 1.12s</code></pre>

<h2><span class="n">7</span>常见坑</h2>

<table>
  <thead><tr><th style="width:270px;">现象</th><th style="width:220px;">原因</th><th>改法</th></tr></thead>
  <tbody>
    <tr><td>20 场全过，换一批掉 5 场</td><td>只测了 pass@k</td><td>写复测集，用同一阈值</td></tr>
    <tr><td><code>12</code> 匹配了 <code>120</code></td><td>用了子串匹配</td><td>整词匹配，见 4.2</td></tr>
    <tr><td>"两份政策都念了一遍"判通过</td><td>只有肯定检查</td><td>加否定检查</td></tr>
    <tr><td>答案对但行为不可接受也判通过</td><td>没接 judge，或 judge 只看最后一句</td><td>judge 读完整段对话 + rubric</td></tr>
    <tr><td><code>command_executed</code> 误判</td><td><code>calls</code> 与 <code>results</code> 错位（成对性被破坏）</td><td>运行器里断言 <code>len(calls) == len(results)</code></td></tr>
    <tr><td>分数说不清是谁判的</td><td>报告里没写 judge 名字</td><td>每处判定都标 judge 来源</td></tr>
    <tr><td>评测集只有 happy path</td><td>漏了第 7 类（信息不足）</td><td>见 4.7</td></tr>
    <tr><td>调检查器时分不清谁变差</td><td>没有确定性基线</td><td>固定假模型跑一轮，记下每个 persona 的结果</td></tr>
  </tbody>
</table>

<h2><span class="n">8</span>自评备忘题</h2>

<ol>
  <li><b>你的评测集能测出"agent 变得更啰嗦"吗？</b>如果不能，缺哪种检查？（提示：<code>max_tool_calls</code> 只约束调用数，不约束字数。）</li>
  <li><b>20 场里，有几场是"换个说法就会失败"的？</b>如果一个 agent 只在特定措辞下正确，它对你真正的用户有用吗？</li>
  <li><b>你的 judge 的偏差是什么？</b>长度偏好、格式偏好、自我偏好 —— 你打算怎么抵消其中至少一个？</li>
  <li><b>如果 16/20 是满分线，你的系统真实的 pass^3 是多少？</b>（同一批 persona 跑三次，每次都过的那部分。）</li>
  <li><b>十段备忘里哪一段你写得最心虚？</b>那一段通常指向你系统里最薄弱的一层 —— 而它可能正是 A7 该重做的地方。</li>
</ol>

<div class="box note"><span class="t">下一作业的接口依赖</span>
<p>A7 会换领域，但<b>复用这一章的全部机制</b>：<code>Check</code> 的十种断言、<code>Persona</code> 的七个字段、<code>score</code> 的规则、以及"三层判分"的结构。<b>A7 新增的是"三版本对照"</b> —— 同一个任务用一次调用、固定 workflow、自主 agent 各做一遍，用<b>同一套评测集</b>打分。没有 A6 的评测集，A7 就只是一个 demo。</p></div>
