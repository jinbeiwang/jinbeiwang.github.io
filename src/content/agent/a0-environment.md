---
kind: assignment
track: practice
order: 1
title: "A0 环境与 LM 层：先让模型可控"
short: "A0 · 环境与 LM 层"
summary: "在写第一行 agent 代码之前，先把模型变成一个可复现、可记账、可脚本化的函数。这一步看起来像样板代码，但它决定了后面六百行代码能不能被测试。"
part: "第一部 · 打底"
label: "A0"
prereq: "第 1、2 章"
reading: "约 40 分钟"
problems: "前置 · 0 分"
deliverable: "tokens.py / tokenizer.py / lm.py"
date: 2026-10-24
ready: true
tags: [ai-agents, 作业, 参考实现]
lang: zh
---

<h2><span class="n">1</span>这个作业要解决什么</h2>

<p class="lede">后面六个作业加起来要调用模型几千次。如果每一次调用都直接 <code>requests.post</code> 出去，你会同时失去三样东西：<b>复现</b>（同一次测试跑两遍结果不同）、<b>成本可见性</b>（不知道钱花在哪）、<b>故障定位</b>（分不清是提示词写错还是模型抽风）。这三样丢了之后，任何一项"改进"都无法被证伪。</p>

<p>A0 不做业务逻辑。它只做一件事：把「模型」变成一个签名固定的函数，并在它外面套三层外壳 —— 缓存、账本、预算。课程 handout 把这一步放在 problem 之前，作为环境准备，但它在整条链上的权重远大于"0 分"这个名字给人的印象。</p>

<table>
  <thead><tr><th style="width:130px;">你要交付</th><th style="width:220px;">它挡住什么</th><th>验收方式</th></tr></thead>
  <tbody>
    <tr><td><b>确定的计数器</b></td><td>预算类断言随环境漂移</td><td>同样的文本在任何机器上算出同样的数字</td></tr>
    <tr><td><b>缓存</b></td><td>同一个测试反复付费、结果漂移</td><td>第二次相同调用不产生新的付费记录</td></tr>
    <tr><td><b>账本</b></td><td>"这次实验花了多少"无法回答</td><td><code>totals()</code> 能按模型和按用途分组</td></tr>
    <tr><td><b>预算</b></td><td>死循环把额度烧穿</td><td>超限时抛出可捕获的异常，且不产生费用</td></tr>
    <tr><td><b>可脚本化模型</b></td><td>没有 key 就无法测试</td><td>整套测试离线跑通</td></tr>
  </tbody>
</table>

<div class="box finding"><span class="t">A0 最重要的判断：先有假模型，才有测试</span>
<p>大多数人的顺序是「先写实现，跑通了再接真实模型」。这个顺序会逼你在调试时同时怀疑两个变量。<b>正确顺序是先写一个能按脚本说话的假模型，用它把控制流测死，再接真模型。</b>这也是为什么 A0 的验收全部离线 —— 一个需要 API key 才能跑通的测试，在 CI 里等于不存在。</p></div>

<h2><span class="n">2</span>接口签名</h2>

<p class="lede">五个类型、三个函数、一个类。<b>表里每一行都是后面作业会 import 的东西</b>，签名一旦定下来就不该再动。</p>

<table>
  <thead><tr><th style="width:210px;">符号</th><th style="width:90px;">所在</th><th>语义</th></tr></thead>
  <tbody>
    <tr><td><code>Message = dict</code></td><td>types.py</td><td><code>{"role": "system"|"user"|"assistant", "content": str}</code></td></tr>
    <tr><td><code>LMCallable</code></td><td>types.py</td><td><code>Callable[[list[Message]], str]</code> —— 整个项目只认这一个签名</td></tr>
    <tr><td><code>count_tokens(text) -> int</code></td><td>tokens.py</td><td>4 字符 / token，向上取整</td></tr>
    <tr><td><code>count_message_tokens(msgs) -> int</code></td><td>tokens.py</td><td>内容之和 + 每条 4 token 的框架开销</td></tr>
    <tr><td><code>tokenize(text) -> list[str]</code></td><td>tokenizer.py</td><td>小写 + <code>[^a-z0-9]+</code> 切分，保留数字</td></tr>
    <tr><td><code>LM(model, *, provider, cache_dir, budget_usd, max_tokens, tag, salt)</code></td><td>lm.py</td><td>可调用对象：<code>lm(messages, *, tag=None, max_tokens=None) -> str</code></td></tr>
    <tr><td><code>LM.totals() -> dict</code></td><td>lm.py</td><td><code>{"by_model": {...}, "by_tag": {...}, "calls": n, "cached": n}</code></td></tr>
    <tr><td><code>ScriptedLM(replies, *, formatter=None)</code></td><td>lm.py</td><td>按顺序回放固定回复；耗尽时抛 <code>ScriptExhausted</code></td></tr>
    <tr><td><code>FnLM(fn, *, record=False)</code></td><td>lm.py</td><td>按 prompt 内容计算回复，用于并发场景</td></tr>
    <tr><td><code>AuxLM(lm)</code></td><td>lm.py</td><td>辅助调用包装器，打上 <code>tag="aux"</code></td></tr>
  </tbody>
</table>

<p>三个异常，语义必须分清 —— 混用它们会让调用方无法决定"该重试还是该停"：</p>

<table>
  <thead><tr><th style="width:180px;">异常</th><th style="width:180px;">什么时候抛</th><th>调用方应当</th></tr></thead>
  <tbody>
    <tr><td><code>BudgetExceeded</code></td><td>付费调用开始前，累计花费已到上限</td><td>停止整个 run，不要重试</td></tr>
    <tr><td><code>OutputTruncated</code></td><td>回复被 max_tokens 截断（携带已生成的部分文本）</td><td>重试，并要求更短的输出</td></tr>
    <tr><td><code>ScriptExhausted</code></td><td>假模型的脚本用完了</td><td>说明测试的预期调用次数写错了 —— 这是测试的 bug，不是产品的</td></tr>
  </tbody>
</table>

<h2><span class="n">3</span>模块划分</h2>

<table>
  <thead><tr><th style="width:130px;">文件</th><th style="width:56px;">行数</th><th style="width:230px;">责任</th><th>明确不做什么</th></tr></thead>
  <tbody>
    <tr><td><code>types.py</code></td><td class="num">121</td><td>跨边界的形状：Email、ToolSpec、AgentConfig…</td><td>不含任何逻辑</td></tr>
    <tr><td><code>tokens.py</code></td><td class="num">36</td><td>两个计数器与一个常量</td><td>不提供"精确"模式</td></tr>
    <tr><td><code>tokenizer.py</code></td><td class="num">25</td><td>检索与事实匹配共用的切词</td><td>不做词干化、不做停用词</td></tr>
    <tr><td><code>lm.py</code></td><td class="num">337</td><td>缓存 / 账本 / 预算 / 三种假模型 / 两个 provider</td><td>不认识 agent，不认识工具</td></tr>
  </tbody>
</table>

<p>依赖方向是单向的，<b>而且必须保持单向</b>：<code>lm.py → tokens.py</code>，<code>pipelines.py → lm 的调用方</code>。任何让 <code>lm.py</code> 反过来 import <code>agent.py</code> 的改动，都会让"用假模型测 agent"这件事失效。检查方法是一条命令：</p>

<pre><code>grep -rn "from .agent\|from .toolset\|import agent" agentlab/lm.py agentlab/tokens.py</code></pre>

<p>期望：无输出。</p>

<h2><span class="n">4</span>关键逻辑逐段解读</h2>

<h3>4.1 为什么是 4 字符一个 token</h3>

<p>handout 里写死了这个换算，理由是它在英文散文上离真实 BPE 分词器约 20% 以内，而且<b>跨模型稳定</b>。这一点很重要：如果计数器随模型变化，那么"上下文预算 16000"就变成了一个随模型漂移的阈值，A4 的压缩测试会跟着漂。</p>

<pre><code>CHARS_PER_TOKEN = 4

def count_tokens(text: str) -> int:
    if not text:
        return 0
    return (len(text) + CHARS_PER_TOKEN - 1) // CHARS_PER_TOKEN</code></pre>

<p>向上取整而不是向下：一个 1 字符的回复不该被算成 0 token，否则"空回复"和"单字符回复"在账本上无法区分。</p>

<p>第二条计数器要注意 <code>+4</code>：</p>

<pre><code>def count_message_tokens(messages: list[dict]) -> int:
    total = 0
    for m in messages:
        total += count_tokens(str(m.get("content", "")))
        total += 4  # role + framing
    return total</code></pre>

<p>这个 +4 是承重的。一个压缩到极致的会话可能有 200 条极短的工具结果：文本总量只有 400 token，但框架开销是 800 token —— <b>是文本量的两倍</b>。如果漏掉这一项，A4 的压缩策略会在"每条都变短了"之后仍然超预算，而你会以为是摘要没生效。</p>

<h3>4.2 缓存键：五个东西都进哈希</h3>

<pre><code>def cache_key(model, messages, max_tokens, salt) -> str:
    h = hashlib.sha256()
    h.update(model.encode())
    h.update(json.dumps(messages, ensure_ascii=False, sort_keys=True).encode())
    h.update(str(max_tokens).encode())
    h.update(salt.encode())
    return h.hexdigest()</code></pre>

<p>四件事容易漏：<b>model</b>（换模型必须失效）、<b>max_tokens</b>（同一个 prompt 在 200 和 2000 下会得到不同回复）、<b>sort_keys</b>（否则 dict 顺序不同就算不同的键，缓存命中率会莫名其妙地低）、<b>salt</b>（想主动让缓存失效时用它，比删目录安全）。</p>

<p>缓存只存<b>成功的回复文本</b>，不存异常。这个选择有代价：一次因超时失败的调用会被反复重试、反复失败。所以生产实现应该在缓存里放"负面条目"，但作业里不做 —— 因为它会让"重试能救回一次网络抖动"这件事不再成立。</p>

<h3>4.3 预算检查的位置：在付费调用之前</h3>

<p>这是 A0 最容易被写错的一行。检查如果放在调用之后，超限的那一次已经把费用花掉了，而你的上限只是一个"事后通知"。</p>

<pre><code># 命中缓存 —— 付费 0，直接返回
if path.exists():
    self._append_ledger(LedgerEntry(..., usd=0.0, cached=True))
    return text

# 冷调用 —— 先查预算，再花钱
if self.budget_usd is not None and self.spent_usd >= self.budget_usd:
    raise BudgetExceeded(
        f"spent ${self.spent_usd:.4f} of a ${self.budget_usd:.2f} cap; "
        "cached replies still work"
    )

text = self.provider(messages, cap)</code></pre>

<p>注意顺序：<b>先查缓存，再查预算</b>。反过来的话，预算耗尽的 run 连已经付过费的缓存都读不到，离线复现就断在这里。</p>

<div class="box note"><span class="t">实测：预算不是"最多花这么多"</span>
<p>用 <code>budget_usd=0.02</code>、每次调用约 $0.035 的假 provider，实测结果是：</p>
<pre><code>call 1 ok  spent=0.0350
call 2 被拒（零成本）: spent $0.0350 of a $0.02 cap
最终 spent 0.0350</code></pre>
<p>第一次调用直接越过了上限，因为<b>它开始之前账上还是 0</b>。所以这个预算的真实语义是「最多<b>开始</b>这么多次付费调用」，不是「最多花这么多钱」。单次调用的成本无法被这个机制约束 —— 要约束它，只能限制 <code>max_tokens</code> 和输入长度。<b>这个限制要写进你的备忘，而不是假装它不存在。</b></p></div>

<h3>4.4 账本是追加写的 JSONL</h3>

<pre><code>@dataclass
class LedgerEntry:
    model: str
    tag: str
    prompt_tokens: int
    completion_tokens: int
    usd: float
    cached: bool</code></pre>

<p>为什么不用一个 JSON 文件整体读写：并发调用会互相覆盖。JSONL 的每行是一个独立事件，写是 <code>open("a")</code> 追加，读是逐行解析并跳过坏行 —— <b>一次写到一半的崩溃只会丢掉最后一行，不会毁掉整个账本</b>。</p>

<p><code>totals()</code> 同时按 <code>model</code> 和 <code>tag</code> 分组，是因为这两个维度回答不同的问题：按模型分组告诉你钱花在贵模型还是便宜模型上，按 tag 分组告诉你花在<b>哪一步</b>（分类、摘要、压缩、judge）。后者才是能指导优化的那个。</p>

<h3>4.5 ScriptedLM 的三种条目</h3>

<pre><code>ScriptedLM([
    {"name": "search_emails", "arguments": {"query": "larchfield"}},  # 工具调用
    "I could not find it.",                                          # 纯文本
    {"repeat": "SEARCH: larchfield"},                                # 之后一直这样
])</code></pre>

<p>dict 形式要用 <code>format_tool_call</code> 转成协议文本，这样<b>测试不需要知道协议长什么样</b>。这一点是 A2 的关键：如果你在测试里手写围栏块加一段 JSON，那么换协议时你要改几十个测试；用 dict 形式，只需换一个 formatter。</p>

<p><code>{"repeat": ...}</code> 是最后一条才能用的"无限重复"，专门用来测"模型永远不停"这类情况 —— 它是唯一一种让 <code>ScriptExhausted</code> 不触发的写法，所以用它的时候要确认你测的确实是"停不下来"，而不是"脚本写少了"。</p>

<h3>4.6 FnLM：并发让顺序失去意义</h3>

<p>A1 的每日摘要用线程池并发分类邮件。<code>ScriptedLM</code> 是顺序依赖的 —— 第 3 条回复给哪个线程，取决于调度。<b>这时测试会间歇性失败，而且失败的是"标签贴错邮件"而不是"程序崩溃"，极难归因。</b></p>

<pre><code>def by_subject(messages):
    prompt = messages[-1]["content"]
    return "CATEGORY: urgent" if "OUTAGE" in prompt else "CATEGORY: normal"

lm = FnLM(by_subject)</code></pre>

<p><code>FnLM</code> 从 prompt 里读出它要回答的对象，所以无论线程以什么顺序跑，标签都落在正确的邮件上。<b>规则：任何被测代码里出现 <code>ThreadPoolExecutor</code> 或 <code>asyncio.gather</code>，就必须用 FnLM。</b></p>

<h3>4.7 AuxLM：辅助调用不占轮次</h3>

<p>A2 的主循环有轮次预算，A4 的压缩会调用模型做摘要。如果这些辅助调用和主循环共用同一个计数器，一次压缩就会让 agent 少一轮 —— 而你调压缩参数时，看到的"性能变化"其实来自轮次变化。</p>

<pre><code>aux = AuxLM(other_lm)          # 打 tag="aux"
config = AgentConfig(aux_lm=aux)  # 主循环用 self.lm，压缩用 aux</code></pre>

<p>在账本里它们被分开统计，于是"压缩花了多少"变成一个可回答的问题。</p>

<h2><span class="n">5</span>实现步骤</h2>

<ol>
  <li><b>建包与 pyproject</b>。Python 3.11+，零运行时依赖（<code>urllib</code> 用标准库）。先写 <code>pyproject.toml</code>，<code>pip install -e .</code>，确认 <code>python -c "import agentlab"</code> 不报错。</li>
  <li><b>types.py</b>。只放形状，不放逻辑。注意 <code>Email</code> 用 <code>TypedDict</code>（要能直接进 JSON fixture），<code>ToolSpec</code> 用 <code>dataclass</code>（要在代码里构造和传递）。<code>"from"</code> 是 Python 关键字，无法作为字段名声明 —— 这个不一致要在注释里写清，否则下一个人会以为是笔误。</li>
  <li><b>tokens.py</b>。两个函数，十几行。写完立刻在 REPL 里验一次：<code>count_tokens("Hello, world!") == 4</code>，<code>count_message_tokens([{"role":"user","content":"Hello, world!"}]) == 8</code>。</li>
  <li><b>tokenizer.py</b>。<code>re.split(r"[^a-z0-9]+", text.lower())</code>，去掉空串。<b>保留数字</b>：<code>240k</code>、<code>2026</code> 是后面问答题的答案本体，丢了就答不了。</li>
  <li><b>lm.py 的 provider 抽象</b>。先写 <code>mock_provider</code>，再写 <code>openai_compatible_provider</code>（<code>urllib.request</code> + <code>/chat/completions</code>）。<code>get_provider</code> 按前缀分派，<code>mock/</code> 开头一律走假模型。</li>
  <li><b>LM 类</b>。按 4.3 的顺序写：算 key → 查缓存 → 查预算 → 调 provider → 写缓存 → 记账 → 累加花费。注意 <code>spent_usd</code> 的累加要加锁。</li>
  <li><b>三种假模型</b>。<code>ScriptedLM</code> 先写，<code>FnLM</code> 和 <code>AuxLM</code> 各十行。</li>
  <li><b>写测试</b>。至少四条：缓存第二次 <code>cached=True</code> 且花费不变；零预算冷启动抛 <code>BudgetExceeded</code>；<code>ScriptExhausted</code> 的信息里带调用序号；<code>FnLM</code> 在乱序调用下仍返回正确标签。</li>
</ol>

<h2><span class="n">6</span>验证标准</h2>

<p class="lede">下面每一条都是可执行的。<b>不要用"看起来对了"当验收。</b></p>

<table>
  <thead><tr><th style="width:52px;">#</th><th style="width:300px;">判定</th><th style="width:190px;">怎么做</th><th>通过标准</th></tr></thead>
  <tbody>
    <tr><td class="num">V1</td><td>计数器确定性</td><td>对同一段 1000 字符文本连算两次</td><td>两次结果相同且为 250</td></tr>
    <tr><td class="num">V2</td><td>消息开销计入</td><td>1 条 9 字符消息</td><td>结果为 3 + 4 = 7（不是 3）</td></tr>
    <tr><td class="num">V3</td><td>缓存命中不花钱</td><td>同一 prompt 调两次，读 <code>totals()</code></td><td><code>calls=2, cached=1</code>，<code>spent_usd</code> 不变</td></tr>
    <tr><td class="num">V4</td><td>预算在付费前拦截</td><td><code>budget_usd=0.02</code>，两次冷调用</td><td>第 1 次成功，第 2 次抛 <code>BudgetExceeded</code>，花费不再增长</td></tr>
    <tr><td class="num">V5</td><td>缓存键随模型变化</td><td>同 messages、不同 model</td><td>两个 key 不相等</td></tr>
    <tr><td class="num">V6</td><td>脚本耗尽可诊断</td><td>脚本 1 条，代码调 3 次</td><td>异常信息含 <code>#2</code> 且说明脚本只有 1 条</td></tr>
    <tr><td class="num">V7</td><td>依赖方向正确</td><td><code>grep -rn "from .agent" agentlab/lm.py</code></td><td>无输出</td></tr>
    <tr><td class="num">V8</td><td>离线可跑</td><td>断网，<code>pytest tests/ -q</code></td><td>全绿</td></tr>
  </tbody>
</table>

<p>跑一遍参考实现，期望看到：</p>

<pre><code>$ python -c "from agentlab.tokens import count_tokens, count_message_tokens as m; \
  print(count_tokens('Hello, world!'), m([{'role':'user','content':'Hello, world!'}]))"
4 8

$ pytest tests/ -q
87 passed in 1.12s</code></pre>

<div class="box takeaway"><span class="t">A0 的完成判据只有一句</span>
<p><b>拿掉 API key、拔掉网线，你的整套测试仍然全绿，并且你能用 <code>totals()</code> 说清任何一次运行花了多少次调用。</b>做不到这两点，不要往下走 A1 —— 后面的作业会把这里的每个缺陷放大十倍。</p></div>

<h2><span class="n">7</span>常见坑</h2>

<table>
  <thead><tr><th style="width:230px;">现象</th><th style="width:250px;">原因</th><th>改法</th></tr></thead>
  <tbody>
    <tr><td>缓存命中率接近 0</td><td>消息列表拼进哈希时没 <code>sort_keys</code>，或 dict 里混进了时间戳</td><td>哈希内容里只放确定性的东西；时间戳放 <code>tag</code>，不进 key</td></tr>
    <tr><td>预算永远不触发</td><td>检查写在 <code>provider()</code> 之后</td><td>移到之前，见 4.3</td></tr>
    <tr><td>并发测试随机失败</td><td>用 <code>ScriptedLM</code> 测线程池</td><td>换 <code>FnLM</code></td></tr>
    <tr><td><code>BudgetExceeded</code> 冒到用户面前</td><td>主循环没有 catch 它，或者 catch 了当成普通异常继续重试</td><td>它是终止信号，不是可重试错误；在 A2 里映射为 <code>token_budget</code></td></tr>
    <tr><td>账本行数比实际调用多</td><td>缓存命中也写一行（这是<b>对的</b>）</td><td>区分 <code>calls</code> 与 <code>cached</code>，别把两者相加</td></tr>
    <tr><td>零预算下第一次调用就挂</td><td><code>budget_usd=0.0</code> 被当成"没设置"（用了 <code>or</code> 而不是 <code>is not None</code>）</td><td>用 <code>if self.budget_usd is not None</code></td></tr>
  </tbody>
</table>

<h2><span class="n">8</span>自评备忘题</h2>

<p>这四题不交，但要在 A6 的 design memo 里有答案。它们问的都是"你为什么这么选"，而不是"你实现了什么"。</p>

<ol>
  <li><b>你的预算约束的是钱还是次数？</b>如果一次调用就能越过上限，你的上限保护的是什么？要真正约束花费，你还缺哪个旋钮？</li>
  <li><b>缓存键里为什么不能放 <code>temperature</code> 之外的东西？</b>如果你把 <code>temperature</code> 放进去了，会发生什么？如果不放，会有什么后果？</li>
  <li><b>缓存命中要不要算进"轮次"？</b>你的 agent 轮次预算统计的是"模型调用次数"还是"付费调用次数"？两者在缓存命中的会话里会差多少？</li>
  <li><b>如果 <code>mock_provider</code> 的规则写得太好，会发生什么？</b>参考实现里它<b>故意</b>比黄金标签差（分类 20/25、问答 3/6）。这个"故意变差"保护了哪一类错误？</li>
</ol>

<div class="box note"><span class="t">下一作业的接口依赖</span>
<p>A1 会用到 A0 的 <code>LMCallable</code>（四个 pipeline 全部以它为参数）、<code>ScriptedLM</code> 与 <code>FnLM</code>（测试）、<code>count_tokens</code>（决定搜索结果和文档窗口的大小）。<b>如果 A1 的测试里出现了 <code>openai</code> 或 <code>requests</code>，说明 A0 的抽象没做对。</b></p></div>
