---
kind: assignment
track: practice
order: 3
title: "A2 工具与主循环：让模型的动作有形状"
short: "A2 · 工具与主循环"
summary: "注册表、文本工具协议、主循环。这一作业把「模型能做的动作」从一个闭集变成一套注册表，顺便定下六条不变量 —— 每一条都对应一个后面会踩到的坑。"
part: "第二部 · 主循环"
label: "A2"
prereq: "A0、A1；第 4、6 章"
reading: "约 80 分钟"
problems: "P5–P8 · 17 分"
deliverable: "registry.py / protocol.py / agent.py / toolset.py"
date: 2026-10-24
ready: true
tags: [ai-agents, 作业, 工具调用, 参考实现]
lang: zh
---

<h2><span class="n">1</span>这个作业要解决什么</h2>

<p class="lede">A1 的 P4 已经有"模型选动作"了，但动作集合只有两个（search / answer）。A2 要做的不是"加更多工具"，而是<b>把动作集合变成数据</b>：一份描述、一个校验器、一个执行器。变成数据之后，模型才能写错、才能被拒绝、才能被审批。</p>

<table>
  <thead><tr><th style="width:56px;">题</th><th style="width:170px;">组件</th><th style="width:150px;">它引入的新问题</th><th>答案在哪</th></tr></thead>
  <tbody>
    <tr><td class="num">P5</td><td>工具注册表</td><td>模型传的参数不对怎么办</td><td>校验与执行分成两步</td></tr>
    <tr><td class="num">P6</td><td>工具调用协议</td><td>模型怎么写"我要调用"，怎么解析</td><td>围栏 JSON + 截断安全的手写扫描器</td></tr>
    <tr><td class="num">P7</td><td>主循环</td><td>什么时候该停</td><td>五种停止原因，全部是返回状态</td></tr>
    <tr><td class="num">P8</td><td>完整工具集</td><td>十个工具怎么描述给模型</td><td>描述就是提示词；索引要惰性建</td></tr>
  </tbody>
</table>

<div class="box finding"><span class="t">这一作业的隐藏主题：所有失败都是返回值，不是异常</span>
<p><code>send()</code> 对模型写的任何东西、工具做的任何事都不抛异常。它返回一个 <code>AgentResult(text, status, transcript)</code>，<code>status</code> 是五种之一。这个决定看起来只是风格，实际上决定了三件事：<b>① 评测可以把"停得对不对"当成指标</b>（A6 的 persona 检查 <code>status not in ("done",)</code> 直接判失败）；<b>② 用户拿到的是解释而不是堆栈</b>；<b>③ 你可以给每种停止原因写一条测试</b>。异常会让这三件事全部失效，因为异常没有类型化的"为什么"。</p></div>

<h2><span class="n">2</span>接口签名</h2>

<table>
  <thead><tr><th style="width:290px;">签名</th><th>语义与不变量</th></tr></thead>
  <tbody>
    <tr><td><code>ToolSpec(name, description, parameters, fn, read_only=False)</code></td><td><code>parameters</code> 是 JSON Schema 对象；<code>read_only</code> 决定要不要审批</td></tr>
    <tr><td><code>ToolRegistry.validate(name, args) -> ToolResult | None</code></td><td><b>不执行、不抛异常。</b>返回结果表示"不能跑，原因在此"</td></tr>
    <tr><td><code>ToolRegistry.execute(name, args) -> ToolResult</code></td><td>内部先 validate 一次；工具抛出的异常收敛为 <code>tool_error</code></td></tr>
    <tr><td><code>ToolRegistry.schemas() -> list[dict]</code></td><td><b>恰好三个键</b>：name / description / parameters</td></tr>
    <tr><td><code>render_tools(schemas) -> str</code></td><td>系统提示词里的那一段说明 + 每个工具的 schema</td></tr>
    <tr><td><code>parse_response(text) -> ParsedResponse(text, tool_call, error)</code></td><td>至多一个调用；截断与损坏分开</td></tr>
    <tr><td><code>format_tool_call(text, call) -> str</code></td><td>测试用：把一个 <code>ToolCall</code> 写成协议文本</td></tr>
    <tr><td><code>Session(lm, tools=None, config=None, *, terminal=None)</code></td><td><code>tools=None</code> 时装配完整十工具</td></tr>
    <tr><td><code>Session.send(message) -> AgentResult</code></td><td>永不抛异常（除了 A0 的 <code>BudgetExceeded</code> 之外不重试的错误）</td></tr>
    <tr><td><code>Session.set_mode("confirm"|"auto")</code></td><td>唯一的模式切换入口</td></tr>
    <tr><td><code>Session.transcript</code></td><td>事件列表：<code>user / assistant / tool_call / tool_result / error</code></td></tr>
  </tbody>
</table>

<p><code>Status</code> 是五个值，比 HTTP 状态码少，但每个都对应一种"下一步该做什么"：<code>ok</code>、<code>unknown_tool</code>、<code>invalid_args</code>、<code>tool_error</code>、<code>denied</code>。注意 <b><code>denied</code> 不是错误</b> —— 它是用户行使了权力，agent 应当换个做法而不是重试。</p>

<h2><span class="n">3</span>模块划分</h2>

<table>
  <thead><tr><th style="width:140px;">文件</th><th style="width:56px;">行数</th><th>责任</th><th>不知道什么</th></tr></thead>
  <tbody>
    <tr><td><code>registry.py</code></td><td class="num">173</td><td>约 80 行 JSON Schema 子集校验 + 注册表</td><td>不知道模型、不知道协议</td></tr>
    <tr><td><code>protocol.py</code></td><td class="num">177</td><td>渲染工具清单、解析回复</td><td>不知道工具怎么执行</td></tr>
    <tr><td><code>agent.py</code></td><td class="num">390</td><td>循环、预算、压缩、审批、steering</td><td>不知道具体工具的业务逻辑</td></tr>
    <tr><td><code>toolset.py</code></td><td class="num">331</td><td>十个工具 + <code>ToolContext</code>（惰性索引）</td><td>不知道循环怎么跑</td></tr>
  </tbody>
</table>

<p>这四层里有一条不太明显的依赖：<code>agent.py</code> 同时 import 了 <code>registry</code>、<code>protocol</code>、<code>toolset</code>、<code>memory</code>、<code>terminal</code>。这是<b>故意</b>的，不是耦合失控。文件头写着理由：压缩改变模型看到什么、审批改变工具跑不跑、steering 改变这一轮看到什么 —— <b>三者都是关于同一份消息列表的决定</b>。把它们拆成插件，就是 harness 变得无法解释的开始。</p>

<p>对比一下框架的代价：LangGraph 会把这三件事分别放进 node、interrupt、checkpoint 三个概念里，你要写三个文件并读一遍它的状态机才能回答"为什么这一轮模型没看到上一条工具结果"。<b>A2 的价值就在于你能在一个 390 行的文件里读出答案。</b></p>

<h2><span class="n">4</span>关键逻辑逐段解读</h2>

<h3>4.1 为什么 validate 要独立于 execute</h3>

<p>这是 P5 的全部要点，用一句话说：<b>审批界面绝不能展示一个本来就会失败的命令。</b></p>

<pre><code>def _authorize_and_run(self, call):
    failure = self.registry.validate(call.name, call.args)   # 1
    if failure is not None:
        return failure
    ...  # 2 deny 规则, 3 审批, 4 执行</code></pre>

<p>如果校验藏在 <code>execute</code> 里，那么执行顺序会变成"问用户 → 用户同意 → 发现参数少了一个 → 报错"。用户被问了一个无意义的问题，而且他会记住"这个 agent 老让我点同意然后又失败"。</p>

<p>校验器本身只有 80 行，实现的是 JSON Schema 的一个子集：<code>type</code>、<code>required</code>、<code>properties</code>、<code>enum</code>、数值与字符串边界、<code>items</code>、<code>additionalProperties: false</code>。真实项目应该用 <code>jsonschema</code> 库，这里自己写是为了让你看清一件事 —— <b>校验器要知道"多传的参数要不要拒"</b>。<code>additionalProperties: false</code> 是一个产品决策：模型多传了 <code>{"query": "x", "reasoning": "..."}</code>，你要不要因为 <code>reasoning</code> 而拒绝整个调用？参考实现选"拒"，因为静默忽略会让模型永远学不会正确的参数集。</p>

<p>还有一行值得单独看：</p>

<pre><code>def _type_ok(value, wanted):
    if wanted == "integer":
        return isinstance(value, int) and not isinstance(value, bool)</code></pre>

<p>Python 里 <code>True</code> 是 <code>int</code> 的实例。<code>{"k": true}</code> 如果不排除 bool，会被当成 <code>k=1</code> 通过校验，然后在 <code>search(index, query, True)</code> 里变成一个奇怪的 <code>k</code>。<b>这类"类型系统漏了一个洞"的 bug，在 agent 项目里会以"检索结果数量莫名其妙"的形式出现。</b></p>

<h3>4.2 手写花括号扫描器：为什么不用正则</h3>

<p>协议是这样一个块：</p>

<pre><code>```tool
{"name": "search_emails", "arguments": {"query": "larchfield audit", "k": 5}}
```</code></pre>

<p>用正则 <code>```tool\s*(\{.*?\})\s*```</code> 能解析出九成情况。剩下的一成包括：参数里带 <code>}</code>（比如一段代码）、参数里带完整的协议块、回复被 <code>max_tokens</code> 截断在参数中间。第三种最致命 —— <b>正则匹配不到时，你分不清"没有调用"和"调用被截断了"</b>，而这两种情况的处理方式相反（前者应当结束，后者应当重试）。</p>

<pre><code>def _balanced_object(text, start):
    # 找到起点，然后跟踪 depth / in_string / escaped
    while i &lt; n:
        if in_string:
            if escaped: escaped = False
            elif ch == "\\": escaped = True
            elif ch == '"': in_string = False
        else:
            if ch == '"': in_string = True
            elif ch == "{": depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0: return i + 1
    return None      # 永远没闭合 → 截断</code></pre>

<p>三个状态变量是必要的：<code>depth</code> 数括号，<code>in_string</code> 让字符串里的 <code>{</code> 不算结构，<code>escaped</code> 让 <code>\"</code> 不结束字符串。少任何一个，下面这条测试就会失败：</p>

<pre><code>def test_argument_may_contain_the_protocol():
    inner = format_tool_call("", ToolCall("inner", {"k": 1}))
    call = ToolCall("outer", {"cmd": inner})

    parsed = parse_response(format_tool_call("", call))
    assert parsed.error is None
    assert parsed.tool_call.name == "outer"
    assert parsed.tool_call.args["cmd"] == inner</code></pre>

<p>这条测试在 A5 会变得非常重要：<b>一封邮件正文里可以写一整个伪造的工具调用块</b>，如果解析器在里面找到它，间接注入就从"模型可能被骗"升级为"解析器一定被骗"。</p>

<p>另一条测试是逐字符截断：</p>

<pre><code>for i in range(len(reply)):
    parsed = parse_response(reply[:i])
    assert parsed.tool_call is None or parsed.tool_call == call</code></pre>

<p>语义是：<b>截断只能导致"没有调用"或"原封不动的调用"，永远不能导致"半个调用被执行"</b>。中间状态（切在参数里）必须设 <code>error</code>，让主循环把这次回复当成格式错误而不是动作。</p>

<h3>4.3 主循环的六条规则</h3>

<p><code>agent.py</code> 的文件头列了六条，每条都有一个测试守着。它们的共同点是：<b>都是"出错时的行为"而不是"正常时的行为"</b> —— 这也解释了为什么它们容易被漏掉。</p>

<table>
  <thead><tr><th style="width:46px;">#</th><th style="width:280px;">规则</th><th>没有它会怎样</th></tr></thead>
  <tbody>
    <tr><td class="num">1</td><td><code>send</code> 不为模型或工具的行为抛异常，只返回状态</td><td>一次畸形回复炸掉整个评测 run，其余 19 条 persona 白跑</td></tr>
    <tr><td class="num">2</td><td>两个预算都在<b>模型调用之前</b>检查</td><td>越过预算的那次调用照样付费（A0 已实测）</td></tr>
    <tr><td class="num">3</td><td>解析失败是错误事件，连续三次才终止</td><td>一次手滑就结束整个会话；或者永远重试</td></tr>
    <tr><td class="num">4</td><td>工具结果<b>逐字</b>出现在下一次调用里</td><td>模型看不到自己刚查到的东西，于是重复查</td></tr>
    <tr><td class="num">5</td><td>授权顺序：校验 → deny → 审批 → 执行</td><td>见 4.1</td></tr>
    <tr><td class="num">6</td><td>工具输出不能改变 mode 或规则</td><td>一封邮件就能把 agent 变成 <code>auto</code> 模式</td></tr>
  </tbody>
</table>

<p>规则 2 有一个必须说清的细节：<code>tokens</code> 每次累加的是 <code>count_message_tokens(messages) + count_tokens(reply)</code>，也就是<b>整段 prompt 每次都重新计一遍</b>。所以 <code>token_budget=400000</code> 约束的是"整个 send 累计计费量"，不是"上下文大小"。这两个概念在长会话里差十倍以上，混淆它们会导致你在调 <code>context_budget</code> 时以为在调成本。</p>

<p>规则 2 还有个反直觉的后果，测试名叫 <code>test_answer_that_crosses_the_budget_is_still_done</code>：如果某次调用<b>开始前</b>还没超预算，它拿到了完整答案，那么这次 send 的结果是 <code>done</code>，不是 <code>token_budget</code>。<b>完成比预算优先</b> —— 否则一个恰好用完预算的正确回答会被判成失败，而用户明明看到答案了。</p>

<h3>4.4 malformed 是计数器，不是布尔</h3>

<pre><code>if parsed.tool_call is None and parsed.error:
    self.transcript.append({"type": "error", "content": parsed.error})
    malformed += 1
    if malformed >= MAX_MALFORMED:      # 3
        return self._finish(last_text, "malformed")
    continue</code></pre>

<p>为什么是三次而不是一次：模型偶尔会写出半个 JSON，给它一次机会成本很低。为什么不是无限：一个反复写坏的模型会烧光预算，而你看不到任何进展。</p>

<p>关键在于<b>什么算 malformed</b>：解析失败、<code>unknown_tool</code>、<code>invalid_args</code> 都算；<code>tool_error</code> 和 <code>denied</code> <b>不算</b>。这个区分是有理由的 —— 前三种说明模型对接口的理解错了，重复只会重复错；后两种说明接口是对的、世界不配合，模型完全可能换个方式成功。所以代码里 <code>malformed = 0</code> 的重置写在成功执行之后：</p>

<pre><code>if result.status in ("unknown_tool", "invalid_args"):
    malformed += 1
    ...
    continue
malformed = 0            # 真跑成功了，之前的坏回复一笔勾销</code></pre>

<h3>4.5 <code>stuck</code>：官方四种停止条件之外的一种</h3>

<p>官方的四种是 <code>done / max_turns / token_budget / malformed</code>，它们约束的是"一次 send 最多做多少事"。<b>没有一种能发现"在预算内反复做同一件事"。</b>一个 agent 可以连续 15 轮调用同一个 <code>search_emails("larchfield")</code>，每轮都拿到一样的结果，然后在第 20 轮被 <code>max_turns</code> 停掉 —— 报告上写的是"轮数用尽"，真实原因是"它卡住了"。</p>

<pre><code>def _note_repeat(self, call) -> bool:
    limit = getattr(self.config, "repeat_limit", 0)
    if not limit:
        return False                      # 默认关闭
    key = f"{call.name}:{json.dumps(call.args, sort_keys=True, ensure_ascii=False)}"
    self._repeat_counts[key] = self._repeat_counts.get(key, 0) + 1
    return self._repeat_counts[key] >= limit</code></pre>

<p>三个设计选择值得注意：<b>① 默认关闭</b>（<code>repeat_limit=0</code>）—— 因为有些合法场景确实要查两次同样的东西（第一次结果被压缩掉了）；<b>② 键包含规范化后的参数</b>（<code>sort_keys</code>）—— 否则 <code>{"a":1,"b":2}</code> 与 <code>{"b":2,"a":1}</code> 会被当成两次不同的调用；<b>③ 计数在<b>成功执行后</b>才加</b> —— 被 deny 的调用重复不算卡住，那是用户在拒绝，agent 该做的是换方案（这一条由 A5 的 <code>denied_then_adapted</code> 检查负责）。</p>

<p>这一条是从仿写仓库的自学计划里吸收的（它的 Week 8 提到"检测重复动作"），<b>官方 handout 没有</b>。加它的理由不是"更完整"，而是"归因更准"：<code>max_turns</code> 和 <code>stuck</code> 在报告里是两件不同的事，前者说明预算不够，后者说明提示词或工具描述有问题。</p>

<h3>4.6 工具描述就是提示词</h3>

<p><code>toolset.py</code> 的文件头写了一句话，值得抄在显示器上：<b>"Run one shell command" 和 "Run one shell command. No here-documents; write multi-line Python as python3 -c '...'" 会让同一个模型产生可测量的不同行为。</b></p>

<p>所以十个工具的描述里，有一半的篇幅在说<b>不要做什么</b>：</p>

<table>
  <thead><tr><th style="width:150px;">工具</th><th>描述里的否定句</th><th>它挡掉的失败</th></tr></thead>
  <tbody>
    <tr><td><code>search_docs</code></td><td>"This is a pointer, not the document: call read_doc"</td><td>模型以为拿到了全文，直接根据标题编答案</td></tr>
    <tr><td><code>read_doc</code></td><td>"call again with the next start_line to continue"</td><td>读完窗口就以为读完了全文</td></tr>
    <tr><td><code>run_terminal</code></td><td>"no here-documents, no substitution, no redirection"</td><td>被拒绝三次才学会正确的写法</td></tr>
    <tr><td><code>remember</code></td><td>"Store what the user told you, not what you guessed"</td><td>把幻觉写进长期记忆，污染之后所有会话</td></tr>
    <tr><td><code>ask_user</code></td><td>"Do not use it to confirm something you can look up"</td><td>把检索工作推给用户</td></tr>
  </tbody>
</table>

<p><code>schemas()</code> 只暴露三个键，这条有测试（<code>test_schemas_expose_exactly_three_keys</code>）。如果顺手把 <code>read_only</code> 或 <code>fn</code> 也传进去，一是浪费 token，二是<b>把实现细节泄漏进提示词</b> —— 模型会开始讨论"这个工具是只读的所以我应该……"，而它根本不需要知道。</p>

<p>实测：完整十工具的系统提示词是 <b>1149 token</b>，占 16000 上下文预算的 <b>7.2%</b>。这个比例是 A4 的前提 —— 如果系统提示词就吃掉 40%，压缩策略再聪明也救不回来。</p>

<h3>4.7 惰性索引：创建会话不读语料</h3>

<pre><code>@property
def emails(self):
    if self._emails is None:
        self._emails = load_emails()
    return self._emails</code></pre>

<p>看起来只是懒加载的常规写法，但它解决一个具体问题：<code>test_session_creation_does_not_touch_the_corpus</code> 断言"构造 Session 不读语料"。理由有两条 —— <b>测试速度</b>（87 个测试里大半要建 Session，每次都建两份索引会让套件从 1.2 秒变成十几秒），<b>以及一个只挂两个工具的会话不该为它没有的工具付费</b>。</p>

<p>这条约束还带来一个结构上的好处：<code>ToolContext</code> 成为所有工具的闭包依赖，于是"这个工具需要什么"变成显式的。要加一个工具，你得先想清楚它需要 emails 还是 docs 还是 memory —— 而不是把一个全局变量 import 进来。</p>

<h2><span class="n">5</span>实现步骤</h2>

<ol>
  <li><b>先写 registry 的校验器</b>（不含注册表）。用一个手写的小 schema 跑通 9 条校验测试。<b>先写 <code>_type_ok</code> 里那个 bool 的判断</b>，它是最容易漏的一条。</li>
  <li><b>再写 ToolRegistry</b>。注意 <code>add</code> 要保留注册顺序（<code>_order</code> 列表），因为模型看到的工具顺序会影响它的选择倾向，而且测试要能断言顺序稳定。</li>
  <li><b>protocol 的渲染部分先写</b>。<code>render_tools</code> 输出的是给人看的说明 + 给模型看的 schema，写完打印一遍，<b>自己读一遍像不像一份 API 文档</b>。</li>
  <li><b>再写解析器</b>。先写 <code>_balanced_object</code>，单独测它；然后写 <code>parse_response</code> 的三条分支（无调用 / 截断 / 非法 JSON）。<b>先写"逐字符截断"那条测试，再写实现</b> —— 它会逼你正确区分 <code>None</code> 与 <code>error</code>。</li>
  <li><b>agent 的主循环</b>。按 4.3 的六条规则逐条写，每写一条配一条测试。<code>_finish</code> 的兜底文案先写好 —— 它保证"停下来了但没话说"不会给用户一个空字符串。</li>
  <li><b>压缩先留空</b>（<code>_compact</code> 直接 return）。A4 再实现。此时所有测试应当已经通过，除了压缩那几条。</li>
  <li><b>toolset 的十个工具</b>。先接 A1 的四个，再接文档两个，最后终端、记忆、<code>ask_user</code>。<b>每加一个，跑一次"模型要能看到它"的测试。</b></li>
  <li><b>接上 <code>Config</code></b>。<code>tools=None</code> 装配全套；传了 <code>tools</code> 就按传的来，但要补上 <code>ask_user</code> 和记忆两个（如果配置里需要）。这段补全逻辑容易写错，写完后用一个只传一个工具、但有 user 的会话验证一次。</li>
</ol>

<h2><span class="n">6</span>验证标准</h2>

<h3>协议层（7 条，离线）</h3>

<table>
  <thead><tr><th style="width:290px;">测试</th><th>通过标准</th></tr></thead>
  <tbody>
    <tr><td><code>round_trip_preserves_json_types</code></td><td><code>3</code> 出来还是 int，<code>true</code> 出来还是 bool</td></tr>
    <tr><td><code>truncation_at_any_character_is_safe</code></td><td>对回复的每个前缀，结果只能是"无调用"或"原调用"</td></tr>
    <tr><td><code>cut_inside_arguments_sets_error</code></td><td>切在参数中间 → <code>error</code> 非空且 <code>tool_call is None</code></td></tr>
    <tr><td><code>argument_may_contain_the_protocol</code></td><td>参数里套完整协议块，解析出的仍是外层调用</td></tr>
    <tr><td><code>two_calls_are_an_error</code></td><td>两个围栏块 → <code>error</code>，不是"跑两个"</td></tr>
    <tr><td><code>plain_prose_has_no_call</code></td><td>纯文本 → <code>tool_call is None</code> 且 <code>error is None</code></td></tr>
    <tr><td><code>render_tools_names_every_tool_and_the_format</code></td><td>每个工具名都出现，且出现 <code>```tool</code></td></tr>
  </tbody>
</table>

<h3>注册表层（9 条，离线）</h3>

<table>
  <thead><tr><th style="width:290px;">测试</th><th>通过标准</th></tr></thead>
  <tbody>
    <tr><td><code>schemas_expose_exactly_three_keys</code></td><td><code>set(s) == {"name","description","parameters"}</code></td></tr>
    <tr><td><code>registration_order_is_preserved</code></td><td>加入顺序 == 输出顺序</td></tr>
    <tr><td><code>unknown_tool</code></td><td><code>unknown_tool</code> 且消息里列出所有可用工具名</td></tr>
    <tr><td><code>missing_required_argument_is_not_executed</code></td><td>工具函数<b>一次都没被调用</b></td></tr>
    <tr><td><code>wrong_type_is_rejected</code> / <code>schema_violation_is_not_executed</code></td><td>同上，且状态是 <code>invalid_args</code></td></tr>
    <tr><td><code>tool_exception_is_contained</code></td><td>工具内部 <code>raise</code> → <code>tool_error</code>，不冒泡</td></tr>
    <tr><td><code>success_is_str_of_the_return_value</code></td><td>返回 <code>None</code> → content 是空串（不是 <code>"None"</code>）</td></tr>
    <tr><td><code>additional_properties_rejected_when_forbidden</code></td><td>多传一个键 → <code>invalid_args</code></td></tr>
    <tr><td><code>boolean_is_not_an_integer</code></td><td><code>{"k": true}</code> 被拒</td></tr>
  </tbody>
</table>

<h3>主循环（11 条，离线）</h3>

<table>
  <thead><tr><th style="width:320px;">测试</th><th>它在守哪一条规则</th></tr></thead>
  <tbody>
    <tr><td><code>plain_answer_is_done</code></td><td>不调工具 → <code>done</code>，text 是回复本身</td></tr>
    <tr><td><code>tool_result_appears_verbatim_in_the_next_call</code></td><td>规则 4</td></tr>
    <tr><td><code>unparseable_reply_recovers</code></td><td>规则 3：一次坏回复后还能继续</td></tr>
    <tr><td><code>three_malformed_replies_stop_the_send</code></td><td>规则 3：三次终止于 <code>malformed</code></td></tr>
    <tr><td><code>unknown_tool_counts_as_malformed</code></td><td>4.4 的分类</td></tr>
    <tr><td><code>max_turns</code></td><td><code>status == "max_turns"</code> 且 text 非空</td></tr>
    <tr><td><code>token_budget_checked_before_the_call</code></td><td>规则 2：预算用尽后模型<b>不再被调用</b></td></tr>
    <tr><td><code>answer_that_crosses_the_budget_is_still_done</code></td><td>规则 2 的例外：完成优先</td></tr>
    <tr><td><code>truncated_output_is_reported_and_retried</code></td><td><code>OutputTruncated</code> 转成错误事件并重试</td></tr>
    <tr><td><code>transcript_is_returned_as_a_copy</code></td><td>调用方改返回的 transcript 不影响会话</td></tr>
    <tr><td><code>session_creation_does_not_touch_the_corpus</code></td><td>4.7</td></tr>
  </tbody>
</table>

<p>跑一遍：</p>

<pre><code>$ pytest tests/ -q
87 passed in 1.12s

$ python -c "
from agentlab.agent import Session
from agentlab.tokens import count_message_tokens
from agentlab.lm import ScriptedLM
s = Session(ScriptedLM(['ok']))
print('system prompt tokens:', count_message_tokens(s._compose()))
"
system prompt tokens: 1149</code></pre>

<div class="box takeaway"><span class="t">A2 的完成判据</span>
<p><b>① 27 条测试全绿（7 + 9 + 11）；② 能说出五种停止原因各自对应什么真实故障；③ 能回答"为什么被 deny 的调用重复不算 stuck"。</b>第 ③ 问是理解"失败分两类"的分水岭 —— 模型错（重复无益）和世界不配合（换法有用）。</p></div>

<h2><span class="n">7</span>常见坑</h2>

<table>
  <thead><tr><th style="width:260px;">现象</th><th style="width:230px;">原因</th><th>改法</th></tr></thead>
  <tbody>
    <tr><td>模型反复调同一个不存在的工具</td><td><code>unknown_tool</code> 没计入 malformed</td><td>见 4.4</td></tr>
    <tr><td>模型看到的是上上次的工具结果</td><td>transcript 事件顺序写反，或 <code>_compose</code> 漏了 <code>tool_result</code></td><td>断言"下一次调用的 messages 里包含刚才的 content"</td></tr>
    <tr><td><code>{"k": true}</code> 通过了校验</td><td>bool 是 int 的子类</td><td><code>not isinstance(value, bool)</code></td></tr>
    <tr><td>两个围栏块时执行了第一个</td><td>解析器只找第一个 <code>```tool</code> 就返回</td><td>解析完要检查尾部还有没有 <code>OPEN</code></td></tr>
    <tr><td>截断的回复被执行</td><td>用 <code>json.loads</code> 的异常当"没有调用"</td><td>区分 <code>None</code>（截断）与"找不到"（无调用）</td></tr>
    <tr><td>评测里一个坏回复炸掉整轮</td><td><code>parse_response</code> 里 <code>raise</code> 了</td><td>返回 <code>ParsedResponse(error=...)</code></td></tr>
    <tr><td>Session 建得慢</td><td>构造时建了索引</td><td>惰性 property</td></tr>
    <tr><td>模型不知道工具有哪些</td><td><code>render_tools</code> 没拼进系统提示词</td><td><code>SYSTEM_PROMPT + render_tools(registry.schemas())</code></td></tr>
  </tbody>
</table>

<h2><span class="n">8</span>自评备忘题</h2>

<ol>
  <li><b>为什么"最多三个工具调用/轮"这种限制不能靠提示词？</b>把它和 <code>HOP_BUDGET</code> 放在一起答：这两处是同一个原则的两次应用。</li>
  <li><b>你的 <code>malformed</code> 计数器在什么情况下会误伤？</b>（提示：一个模型第一次见到某工具时，很可能先传错一次参数试水。）三次够吗？如果不改次数，还能改什么？</li>
  <li><b>如果 <code>repeat_limit=1</code>，什么合法行为会被杀掉？</b>如果你把 <code>repeat_limit</code> 默认设成 2，代价是什么？</li>
  <li><b>工具描述里哪一句是你删掉之后行为会变差的？</b>删掉它跑一遍评测，如果分数没变，说明那句话是装饰。</li>
  <li><b>为什么 <code>schemas()</code> 不把 <code>read_only</code> 给模型看？</b>如果给了，模型可能做出什么你不希望的行为？</li>
</ol>

<div class="box note"><span class="t">下一作业的接口依赖</span>
<p>A3 会替换 <code>search_docs</code> 的返回形态（从"文档片段"变成"指针 + 短证据"）并新增 <code>run_terminal</code> 的观测策略。<b>A2 里 <code>ToolSpec</code> 的 <code>read_only</code> 标记是 A5 审批逻辑的唯一依据</b>，所以 A3 加工具时必须想清楚它是不是只读 —— 想错的后果不是报错，是<b>一个会改文件的工具静默地不需要审批</b>。</p></div>
