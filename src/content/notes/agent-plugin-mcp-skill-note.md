---
title: "插件、MCP 与 Skill：三个被混用的词，和一条消息的三种走法"
summary: "「插件」在 Agent 语境里至少指三件不同的东西：宿主进程内的可替换组件、平台自定义的外部 API 清单、以及市场里一切可安装扩展的泛称。被淘汰的只有中间那一种，而它当年的需求被 MCP 接管了。MCP 不区分本地与商用，本地 stdio 和厂商托管的 Streamable HTTP 走的是同一套 JSON-RPC，差别在传输、凭据放在哪、以及赌的是代码可信还是厂商可信——规范对此有一条硬规定：STDIO 传输不应遵循 OAuth，改从环境读凭据。Skill 的价值也不在复述模型已知的知识，而在私有口径、可执行脚本、固定输出与版本留痕这四样。全文用本机实跑的 9 条 JSON-RPC 报文、一份 HTTP/SSE 往返记录和两个零依赖脚本，把「host / client 太抽象」和「三种传输是什么」拆到能看见每一条字节。"
date: 2026-11-08
category: Learning log
tags: [MCP, AI agents, Skill, 协议, 插件]
lang: zh
---

<div class="meta-row">
    <span><b>来源</b> &nbsp;MCP 2025-06-18 规范（architecture / transports / authorization / lifecycle）、Anthropic Agent Skills 文档、OpenAI 2023 插件公告、DeepSeek Harness 官网；报文与实验脚本为自行编写并实跑</span>
    <span><b>状态</b> &nbsp;官方条文与措辞已抓取正文逐条核对；报文为运行输出原文，未做修饰</span>
</div>

<div class="box note" style="margin-top:26px;">
  <span class="t">证据怎么标，以及怎么自己验</span>
  <div class="small">
  <p>标 <em class="ev">[doc]</em> 的，能在官方规范或文档里查到原句；标 <em class="ev">[实践]</em> 的，是从工程角度做的判断，可以被合理反对；只在时间线或技术形态上取信、没拿到一手出处的，正文会直接写明「二手」，不拿它撑定义。</p>
  <p>第 5、6 节引用的每一行报文，都来自文末两个可下载的脚本。它们只用 Node 内置模块、只走 <code>127.0.0.1</code>、不发任何外部请求，跑一遍就能和正文对照。</p>
  </div>
</div>

<p class="lede">这几个词被混用得太厉害，以至于「插件是不是过时了」「MCP 和 Skill 该选哪个」这类问题本身就问偏了方向。先把同名词拆开，再谈新旧，最后把一条消息从宿主走到服务端的每一步摊开看。</p>

<h2><span class="n">1</span>先给结论：六处最容易绕住的地方</h2>

<table>
  <thead><tr><th style="width:38%;">常见的说法</th><th>更准确的说法</th></tr></thead>
  <tbody>
    <tr><td>「一切皆插件」说明插件没过时，所以 ChatGPT 插件也没过时</td><td>两句里的「插件」不在同一层。前者是宿主<b>进程内</b>的可替换组件，后者是宿主<b>进程外</b>的第三方 API 清单。过时的是后一种产品形态，机制本身没有。</td></tr>
    <tr><td>MCP 是插件模式的标准化演进</td><td>只在「外部服务接入」这一层成立。宿主内部的组件化是另一条线，它和 MCP 没有替代关系——在 DeepSeek Harness 里，把 MCP 接进来这件事本身就是一个插件。</td></tr>
    <tr><td>自建 local MCP 和厂商托管的 MCP 是两种东西</td><td>协议层完全一样，都是同一套 <code>initialize</code> / <code>tools/list</code> / <code>tools/call</code>。差别在传输、部署位置、鉴权方式与信任边界。</td></tr>
    <tr><td>host / client / server 这三个角色很抽象</td><td>它们是三个进程边界。Host 是正在用的那个应用，Client 是它内部为每一个 server 单独建的连接对象，Server 是真正干活的子进程或远程服务。模型从头到尾没跟 server 直接说过一句话。</td></tr>
    <tr><td>Skill 就是写长一点的 prompt</td><td>只对了一半，而且这一半正在贬值。纯知识型 Skill 确实可以还原成 prompt；含私有口径、可执行脚本、固定输出、版本留痕的不能。</td></tr>
    <tr><td>宿主支持 STDIO、SSE、HTTP 三种传输</td><td>SSE 不是与 HTTP 并列的第三种东西，它是 HTTP 之上的一种响应方式。MCP 规范里真正并列的只有两种：stdio 与 Streamable HTTP。</td></tr>
  </tbody>
</table>

<h2><span class="n">2</span>「插件」是三层东西，不是一个词</h2>

<p class="lede">同一个中文词，在三层完全不同的位置上被使用。不先拆开，后面所有的新旧之争都会打架。</p>

### 2.1 三种同名物

<table>
  <thead><tr><th style="width:20%;">层</th><th style="width:18%;">叫什么</th><th style="width:20%;">运行在哪</th><th>扩展的是什么</th><th style="width:18%;">现状</th></tr></thead>
  <tbody>
    <tr><td><b>L1 宿主内组件</b></td><td>进程内插件 / 扩展模块</td><td><b>与宿主同进程或同生命周期</b></td><td><b>宿主本身</b>：能换模型、换循环、换 UI、注册服务与事件。典型形态是 VS Code Extension、DeepSeek Harness 的 Cordis 插件</td><td>没过时，正在强化</td></tr>
    <tr><td><b>L2 宿主外服务</b></td><td>外部工具插件</td><td>第三方服务器，进程外</td><td>只给模型<b>新增可调用的 HTTP API</b>，插件作者碰不到宿主。典型形态是 2023 年的 ChatGPT Plugins、后来的 GPT Actions</td><td>旧形态已下线；需求被 MCP 接管</td></tr>
    <tr><td><b>L3 市场口径</b></td><td>「插件」泛称</td><td>——</td><td>应用商店里一切可安装扩展的统称</td><td>只是命名，不指技术</td></tr>
  </tbody>
</table>

混淆点就在这里：DeepSeek 说的是 L1，ChatGPT Plugins 是 L2，两者只共享一个中文词。而 L3 是市场语言，讨论技术时应该先把它排除掉。

### 2.2 「一切皆插件」到底指什么

DeepSeek Harness 官网的自述是：「基于 Cordis 的<b>「一切皆插件」架构</b>构建」，以及「安装现有插件，或在『创造模式』中通过对话创建插件，扩展<b>工具、技能和界面</b>」。<em class="ev">[doc]</em>

英文页把清单列得更完整：**Every capability is a plugin that can be swapped or recomposed: models, tools, skills, sessions, sandboxes, storage, loops, scheduling, and the UI.** 同一页还给了定义「**Agent = Model + Harness**」，并说明 Cordis kernel 负责插件的挂载、卸载与依赖。

注意这份清单里有**模型适配器、Agent 循环、会话日志、沙箱、调度、UI**。这不是「给 Agent 加几个工具」，而是「没有特权核心」：宿主只剩一个极小的运行时内核，能力全靠插件往共享 Context 里注册服务。

社区对 Cordis 的解读是三要素——服务注册、类型化事件、可逆副作用，插件卸载时自动撤销注册过的服务、事件与资源，因此可以热插拔。这一条是**二手**，官方页面没有逐条列出。对应到工程体验就是「换掉任一部件不用改框架源码，装错了卸掉能精确回滚」。

由此得到一个反直觉的结论：在 Harness 里，MCP 与 Skills 不是与插件并列的概念，而是**被插件承载的能力**。官方清单里明确含 `skills`；MCP 接入层以插件形态存在则是社区解读。也就是说，那一层的「插件」是比 MCP 和 Skill 更上位的架构范式。

### 2.3 ChatGPT Plugins 是什么，为什么下线

它只有三样东西拼起来（技术细节来自二手资料，已交叉核对）：

1. 一个开发者自托管的 REST API；
2. 托管在 `https://域名/.well-known/ai-plugin.json` 的 manifest，含 `name_for_model` / `description_for_model` 与认证方式；
3. 一份 OpenAPI schema，描述端点、参数与返回。

运行时，ChatGPT 把 manifest 与 schema **拼成一段工具说明塞进模型上下文**，模型据此决定调哪个 endpoint，宿主再把 HTTP 结果回灌对话。2023 年那篇官方公告印证了这一点：「which then **lists the enabled plugins in the prompt shown to the language model** as well as documentation to instruct the model how to use each」。<em class="ev">[doc]</em>

下线证据要分两级，别把二手当一手：

- **一手**：那篇官方博客现在页首挂着 **«Note: OpenAI plugins have been deprecated.»**
- **一手但已失效**：官方帮助文章 `help.openai.com/en/articles/8988022-winding-down-the-chatgpt-plugins-beta` 实测返回 404，无法引用其措辞。
- **二手**：2024-03-19 起不能安装新插件或用插件开新对话、2024-04-09 现有对话终止、由 Custom GPTs 加 Actions 承接，来自开发者社区对该帮助文章的转述与多家媒体。具体日期只能标二手。

技术上值得注意的一点：GPT Actions 几乎原样复用了 manifest 加 OpenAPI 的模式。对开发者来说，主要是**打包方式变了**，能力模型没变。

### 2.4 那篇 2023 年公告里最有意思的一句话

> "We expect that **open standards will emerge to unify the ways in which applications expose an AI-facing interface**. We are working on an early attempt at what such a standard might look like."
> —— OpenAI, ChatGPT plugins, 2023-03-23 <em class="ev">[doc]</em>

OpenAI 当年就预判会有一个开放标准来统一 AI-facing interface。MCP 就是后来长出来的那个标准。

所以更准确的叙事不是「插件被 MCP 淘汰」，而是两条线各自在演化：

- **外部能力接入**这条线：从「每家平台自定义 manifest、把 API 文档塞进 prompt」，收敛到「统一 JSON-RPC、结构化工具发现、跨宿主复用」。被淘汰的是私有 manifest 形态，不是外部工具这件事。
- **宿主内部架构**这条线：从「能力硬编码」走向「全插件化、可组合、可热插拔」，VS Code 到 Harness 是同一方向。这条线跟 MCP 没有替代关系。

<h2><span class="n">3</span>三者到底什么关系：两层，不是并列</h2>

<p class="lede">插件、MCP、Skill 经常被平铺成「三种扩展方式」，这是最常见的误解来源。它们分属两个层次，一个是连接，一个是认知。</p>

### 3.1 连接层与认知层

| 层次 | 回答的问题 | 代表形态 | 类比 |
|---|---|---|---|
| 连接层（早期） | 模型能不能调用这个外部 API | 插件、function calling | 每台设备自带专用接口 |
| 连接层（标准化） | 不同宿主能否共用同一套外部能力 | MCP | USB-C 统一接口 |
| 认知层 | 这类任务该按什么流程做、用哪些工具、产出什么格式 | Skill | 岗位 SOP 加工具箱 |

**MCP 与插件是横向对比关系**（同层、代际不同）；**Skill 与它们是纵向叠加关系**（不同层）。这个判断能解释后面所有的组合方式。

### 3.2 横向对比

| 维度 | 插件 Plugin | MCP | Skill |
|---|---|---|---|
| 本质 | 平台侧的能力挂载方式 | 开放的通信协议与标准 | Agent 侧的知识与工作流包 |
| 主要载体 | manifest 加 OpenAPI schema | JSON-RPC 会话与 host/client/server | 目录：`SKILL.md` 加 `scripts/` 加 `references/` |
| 回答的问题 | 能不能调这个 API | 怎么统一地连、怎么协商能力 | 这类任务该怎么做 |
| 复用范围 | 通常绑定单一平台 | 跨宿主复用，一次实现多处接入 | 跨会话复用，依赖宿主执行环境 |
| 是否定义网络协议 | 平台自定义 | 是 | 否 |
| 上下文占用 | schema 常驻 | 工具清单常驻 | 仅元数据常驻，指令按需加载 |
| 典型产出 | 一次外部调用的结果 | 一组 tools / resources / prompts | 一套流程、脚本与交付物 |
| 安全边界 | 平台授权 | host 审批、能力协商、server 之间互相隔离 | 宿主执行脚本，须审查来源与权限 |

### 3.3 一个叠加的实例

任务：检索某个主题的最新资料，整理成带来源的报告，存到指定目录。

| 环节 | 由谁承担 | 具体动作 |
|---|---|---|
| 判断属于哪类任务 | Skill 的 Level 1 元数据 | description 命中「查最新资料 / 整理报告」 |
| 给出流程与口径 | Skill 的 Level 2 指令 | 定义检索、提炼、导出的分工与证据分层要求 |
| 真正发出检索请求 | Skill 的 Level 3 脚本，或 MCP 工具 | 可以走 CLI 直连 REST，也可以换成 MCP 的 `search` 工具 |
| 生成文档 | Skill 的 Level 3 脚本 | 本地转换，不联网 |

同一任务里 MCP 与 Skill 并不互斥：Skill 可以规定「第一步调用某个 MCP 工具」，MCP 负责把那个工具稳定地暴露给宿主。反过来说，一个任务完全不用 MCP 也能做成——只要 Skill 里的脚本自己会发请求。

### 3.4 四个常见误区

1. **「MCP 是插件的一种」**。更准确的说法：插件是产品形态，MCP 是协议标准。一个 MCP server 不是「装进某个 App 的插件」，而是可被多个宿主连接的独立服务。
2. **「Skill 就是写长一点的 prompt」**。这个说法忽略了文件系统、可执行脚本与三级渐进披露。脚本能被执行却不进上下文，这是 prompt 做不到的。
3. **「三者选一个就行」**。多数真实场景是叠加，见上一节。
4. **「装了 Skill 就等于数据外发」**。不一定，取决于脚本里有没有网络调用、有没有配密钥。同一个技能包可以设计成「没有密钥就退化为本地处理」的两条路径，触发哪条由文件是否存在决定。

### 3.5 怎么选

| 需求 | 优先选 |
|---|---|
| 让 Agent 连上一个外部系统或数据源，且希望多个客户端都能用 | 写或接一个 MCP server |
| 只在某个平台里快速挂一个 API | 平台自带的插件 / Actions / function calling |
| 把一类重复任务的口径、流程、模板、校验规则沉淀下来 | 写一个 Skill |
| 既有固定流程又要调外部数据 | Skill 管流程，MCP 或 REST 管数据，两者叠加 |
| 涉及敏感数据 | 先查链路：脚本是否联网、密钥放在哪、server 是本地还是远程 |

<h2><span class="n">4</span>local MCP 与商用远程 MCP：同协议，不同信任边界</h2>

<p class="lede">这两个词经常被当成两类技术来讨论，其实它们的邮件内容一模一样，只是寄信方式不同。真正要评估的是另外三件事：传输、凭据放在哪、以及你在赌什么。</p>

### 4.1 先拆掉一个维度混淆

「谁开发的、部署在哪」（自建与商用）和「用哪套协议」（MCP、Skill、直连 REST）是两个正交维度，很容易串在一起：

| | 本地自建 | 厂商托管 |
|---|---|---|
| **作为 MCP server** | 自己写的 stdio 子进程（本文 demo 就是） | Notion 官方远程 MCP、各类托管 MCP 端点 |
| **作为 Skill** | 本机 `~/.workbuddy/skills/<name>/SKILL.md` 加脚本 | 技能市场装下来的包（运行仍在本机） |
| **都不走 MCP** | 本地脚本直连 REST API | 厂商 SDK 或 REST API |

一个具体的例子：某个检索服务既有托管 MCP 端点，也有一个本地 CLI 技能包。两者能力重叠，但**它们不是同一个接入物**——前者经过 MCP 协议，后者是本地脚本直接打 REST。排查「数据到底从哪条路出去」时，这个区分是第一步。同理，Notion 既有官方托管 MCP，也完全可以自己写一个本地 stdio 版 server，同一个能力四种组合都可能。

### 4.2 协议层：完全一样

MCP 架构规范原文说 server「**Can be local processes or remote services**」。本地与远程在规范里是同一个抽象，都实现同一组 JSON-RPC 方法。<em class="ev">[doc]</em>

第 5 节那 9 条报文，换成远程只是**信封换了**（换行分隔的 stdin/stdout 变成每条消息一个 HTTP POST），信的内容一个字不变。

### 4.3 六个维度

| 维度 | 本地 stdio MCP | 托管 Streamable HTTP MCP |
|---|---|---|
| **谁启动** | **Host 把 server 作为子进程拉起**（规范原话：The client launches the MCP server as a subprocess） | 厂商常驻服务，Host 只建连接 |
| **通信** | stdin/stdout，消息换行分隔、不得含内嵌换行；stdout 只允许协议消息，日志走 stderr | 每条 client 到 server 的 JSON-RPC 都是**一次新的 HTTP POST**；server 可用 GET/SSE 流回推 |
| **并发模型** | 一个子进程服务一个 client，随 Host 启停 | server 作为独立进程，**可处理多个 client 连接** |
| **鉴权 / 凭据** | **规范明确：STDIO 传输不应遵循 OAuth 授权规范，改从环境读凭据** | **HTTP 传输应当遵循**：OAuth 2.1 加 PKCE 加 RFC 8707 Resource Indicators；或厂商自定义 API Key header |
| **数据流向** | 原则上不出本机（除非工具自己联网）；凭据躺在本地环境变量里 | 每次查询词、参数、结果都出本机到厂商；授出去的是第三方账号的 scope |
| **升级 / 可用性** | 自己管版本、依赖、崩溃；断网可用；换设备要重装 | 厂商热更新即时生效；依赖网络、受配额与计费约束；多设备共用 |
| **配置写法** | `mcp.json` 里 `command` 加 `args` 加 `env` | `mcp.json` 里 `url` 加 `headers` 或 OAuth |

WorkBuddy 侧的一手依据：官方文档列出 STDIO、SSE、HTTP 三种传输，`user / project / local` 三种作用域（优先级 `local > project > user`），以及**项目作用域的 MCP 服务器在首次连接时需要用户审批**。<em class="ev">[doc]</em> 该文档仍列 SSE，而 MCP 规范中 HTTP 加 SSE 是 2024-11-05 的旧传输，已被 Streamable HTTP 取代，宿主保留它多半是兼容项。

### 4.4 几条判断依据，不是推断

> Authorization is **OPTIONAL** for MCP implementations. When supported:
> - Implementations using an HTTP-based transport **SHOULD** conform to this specification.
> - Implementations using an **STDIO transport SHOULD NOT follow this specification, and instead retrieve credentials from the environment**.
>
> —— MCP 2025-06-18 basic/authorization <em class="ev">[doc]</em>

> When implementing Streamable HTTP transport: Servers **MUST validate the `Origin` header** on all incoming connections to prevent DNS rebinding attacks; when running locally, servers **SHOULD bind only to localhost (127.0.0.1)**; servers SHOULD implement proper authentication.
>
> —— MCP 2025-06-18 basic/transports <em class="ev">[doc]</em>

> In the stdio transport: The client launches the MCP server as a subprocess… Messages are delimited by newlines, and MUST NOT contain embedded newlines… The server MUST NOT write anything to its `stdout` that is not a valid MCP message.
>
> —— 同上

第一条是最硬的依据。它把「本地和远程差在哪」从产品叙事变成了规范条文：**凭据的来源不同**。本地从环境读，远程走 OAuth。

### 4.5 信任边界：赌的东西不一样

- **本地 stdio**：等于给了第三方脚本**本机用户的全部权限**——读文件、跑命令、拿到 `env` 里所有凭据。风险是任意代码执行；好处是没有网络监听、没有第三方账号授权、断网可用。缓解手段是看源码、最小权限的 `env`、沙箱。
- **远程 HTTP**：不给本机权限，但给出**第三方账号的 scope** 和**每一次查询的内容**。风险是数据留存、scope 过宽，以及授权规范单列一节的 **confused deputy problem**（MCP server 作为中介去调第三方 API 时被利用）与 token 透传。
- 结论：**本地赌代码可信，远程赌厂商可信加授权范围合适**。这与「谁更商用、谁更专业」无关，是两类完全不同的风险。
- 还有中间形态：自己在本机起一个 HTTP MCP server。这时上面那条 DNS rebinding 警告就直接适用——只绑 `127.0.0.1`，校验 `Origin`。

<h2><span class="n">5</span>MCP 到底怎么跑：9 条真实报文</h2>

<p class="lede">host / client 显得抽象，是因为文档在讲职责，而职责看不见。换成进程边界和实际字节，它就变成一件很朴素的事。</p>

### 5.1 三个角色 = 三个进程边界

MCP 架构规范的定义：<em class="ev">[doc]</em>

| 角色 | 规范里的职责 | 换成大白话 |
|---|---|---|
| **Host** | 创建并管理多个 client 实例；执行安全策略与用户授权；协调 AI/LLM 集成；管理上下文聚合 | **正在用的那个应用**（WorkBuddy、Claude Desktop、Harness）。管模型、UI、会话、权限弹窗、结果汇总。它是容器，不是网络协议角色 |
| **Client** | 与每一个 server 建立**一条有状态会话**；处理协议协商与能力交换；维持 server 之间的安全边界 | Host 内部**为每一个 server 单独创建**的连接对象。规范原话：「each client having a **1:1 relationship** with a particular server」。装 3 个 MCP 就有 3 个 client 实例 |
| **Server** | 暴露 resources、tools、prompts；独立运行；可以是本地进程或远程服务 | 真正提供工具的独立进程或服务 |

**为什么非要夹一层 client**：为了隔离。每个 server 一条独立会话，握手状态、能力协商、权限与故障都不串台；Host 只跟 client 打交道，不必关心对面是 stdio 子进程还是远程 HTTP。这也是为什么叫 client-**host**-server，而不是普通的 client-server。

### 5.2 一次工具调用的完整流程

下面的编号对应第 5.3 节报文里的 `[01]` 到 `[09]`。

| 步 | 谁做 | 动作 |
|---|---|---|
| 0 | **Host** | 读 `mcp.json`，为每个 server 拉起子进程或建连接，创建对应 client |
| 1 | Client → Server | `[01] initialize`：带上 `protocolVersion`、`capabilities`、`clientInfo` |
| 2 | Server → Client | `[02]` 回协议版本与自己的支持能力（`tools`）加 `serverInfo`。**握手完成，版本与能力协商成功** |
| 3 | Client → Server | `[03] notifications/initialized`：通知进入操作阶段。**无 id，按规范不回应** |
| 4 | Client → Server | `[04] tools/list` |
| 5 | Server → Client | `[05]` 返回工具清单，每个工具带 `name`、`description`、**`inputSchema`** |
| 6 | **Host → 模型** | Host 把 `inputSchema` 转成模型可见的 tool 定义，放进本次模型请求。**这是模型第一次「看见」这个工具** |
| 7 | 模型 → Host | 模型输出一个 tool_call（函数名加参数）；Host 收到后做权限确认 |
| 8 | Client → Server | `[06] tools/call`：`{"name":"check_required_vars","arguments":{...}}` |
| 9 | Server → Client | `[07]` 执行**真实代码**，返回 `content` 加 `isError` |
| 10 | Host → 模型 | 结果作为 tool 消息追加进对话；模型读完后生成人话回答 |
| 11 | 验证 | `[08]` / `[09]` 用**完全相同参数再调一次**，两次返回字节级一致 |

### 5.3 关键报文，原样未修饰

```json
C → S  {"jsonrpc":"2.0","method":"initialize","id":15878,"params":{"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"workbuddy-demo-host","version":"1.0.0"}}}
S → C  {"jsonrpc":"2.0","id":15878,"result":{"protocolVersion":"2025-06-18","capabilities":{"tools":{"listChanged":false}},"serverInfo":{"name":"adam-check-demo","version":"0.1.0"}}}
C → S  {"jsonrpc":"2.0","method":"notifications/initialized"}
C → S  {"jsonrpc":"2.0","method":"tools/list","id":15774,"params":{}}
S → C  {"jsonrpc":"2.0","id":15774,"result":{"tools":[{"name":"check_required_vars","description":"...","inputSchema":{"type":"object","properties":{"dataset":{...},"present_vars":{...},"required_vars":{...}},"required":[...]}}]}}
C → S  {"jsonrpc":"2.0","method":"tools/call","id":15322,"params":{"name":"check_required_vars","arguments":{"dataset":"ADSL","present_vars":["USUBJID","AGE","SEX","RACE"],"required_vars":["USUBJID","AGE","TRT01P","TRT01PN"]}}}
S → C  {"jsonrpc":"2.0","id":15322,"result":{"content":[{"type":"text","text":"{\"dataset\":\"ADSL\",\"checked\":4,\"missing\":[\"TRT01P\",\"TRT01PN\"],\"status\":\"FAIL\",\"engine\":\"deterministic-code-v1.0.0\"}"}],"isError":true}}
```

三条值得注意的细节：

- `initialize` 的 `id` 是 15878，`tools/list` 是 15774，`tools/call` 是 15322——id 由客户端自增或随机生成，只用来配对请求与响应，没有语义。
- `notifications/initialized` **没有 `id`**。这是 JSON-RPC 的通知语义：收到不用回。
- `tools/call` 的返回里 `isError: true` 表示工具执行失败（这里是校验不通过），而**不是协议层错误**。协议层错误会走 JSON-RPC 的 `error` 字段。这个区分经常被混淆：前者是「业务结果是否通过」，后者是「这次调用本身成没成」。

### 5.4 模型在哪里、不在哪里

**这 9 条报文里没有任何一条包含模型推理。** 模型全程只做两件事：

1. 读 `tools/list` 得到的 schema，决定**要不要调**、**参数填什么**；
2. 读 `tools/call` 的返回，把 JSON 翻译成人话。

协议握手、能力协商、消息路由、工具执行、结果封装，全部由 Host 里的 client 和 server 进程完成。

所以「MCP 是给模型装插件」这个说法容易误导——**MCP 是给宿主应用定义一个标准化的外设接口**；模型从来不直接跟 MCP server 通信。换成 Streamable HTTP 时，上面每个 `C → S` 变成一次 HTTP POST，每个 `S → C` 变成 POST 响应或 SSE 流，而 JSON-RPC 的 `method` / `params` / `result` 一模一样。这就是「本地与商用只有信封不同」的确切含义。

<h2><span class="n">6</span>STDIO / HTTP / SSE：三种走法，一串信纸</h2>

<p class="lede">「支持三种传输」难懂，是因为这句话把协议内容和送信方式压成了一句。分开看，这一层其实最简单。</p>

### 6.1 总框架：JSON-RPC 是信纸，传输是信封

MCP 要送的东西永远是同一串 JSON：`{"jsonrpc":"2.0","method":...}`。传输层只回答一个问题——**这串字节怎么从 A 搬到 B**。它不关心内容、不参与工具执行、不改变结果。

所以第 5 节那 9 条报文在三种传输下内容完全一样，变的只有「怎么送」。它们不是三种 MCP，是同一个 MCP 的三种信封。

### 6.2 STDIO：不是网络，是同一台机器里的一根管道

STDIO = **ST**an**D**ard **I**nput / **O**utput，每个命令行程序生来就带三个流：`stdin`（进）、`stdout`（出）、`stderr`（报错）。

Host 用 `spawn` 把 server 当**子进程**拉起来，操作系统在父子之间接一根管道：Host 往子进程 stdin 写一行，子进程读一行、处理、往 stdout 写一行，Host 从 stdout 读到。**一行就是一条 JSON-RPC 消息，换行就是分隔符**（规范：消息内不得含内嵌换行；stdout 被协议独占，日志只能走 stderr）。

> 类比：两个人在同一间屋里，隔着桌上的传递窗口递纸条。纸条从不出这个房间。

关键点：**没有 IP、没有端口、没有 URL、没有 HTTP 头、零网络往返**。所以断网照用，也所以规范说凭据从环境变量读、不必上 OAuth。代价是 server 只服务这一个 Host、随 Host 启停、装在哪台机器就只能在哪台用。

### 6.3 HTTP：一次调用就是一次「问一句、答一句」

HTTP 是**客户端主动发一个请求报文、服务端回一个响应报文**的一问一答协议：

- **请求报文** = 请求行（方法加路径加版本）+ 请求头（若干 `键: 值`）+ 可选请求体
- **响应报文** = 状态行（`200 OK` / `401` / `404`）+ 响应头 + 响应体

**「发起一次 HTTP 调用」就是完整走完这样一趟往返。** 下面这段是实验里真实打印出来的报文，不是示意图：

```text
POST /mcp HTTP/1.1                          ← 请求行：方法、路径、协议版本
Host: 127.0.0.1:12252                       ← 请求头：找谁
Content-Type: application/json              ← 请求头：body 是什么格式
Authorization: Bearer ***DEMO_KEY***        ← 请求头：我是谁（每趟都要重带）
Mcp-Session-Id: demo-session-1              ← 请求头：HTTP 无状态，靠它维持逻辑会话
Content-Length: 58                          ← 请求头：body 有多少字节

{"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}}   ← 请求体：信纸
```

服务端回：

```text
HTTP/1.1 200 OK                             ← 状态行
Content-Type: application/json

{"jsonrpc":"2.0","id":2,"result":{"tools":[]}}               ← 响应体
```

这一来一回，就叫**一次 HTTP 调用**。几个容易卡住的点：

- `Content-Length` 只是告诉对方「body 有几个字节，读到这儿就够了」，不是内容本身；
- `Authorization` **每一趟都要重新带**，因为 HTTP 本身无状态，服务端不记得上一趟是谁；
- TCP 连接可能复用（keep-alive），但**这一问一答已经结束了**——连接复用不等于调用没结束。

> 类比：每说一句话都要重新拨一通电话，先报身份，说一句，等对方答，挂断；下一句再拨一次。

换算到 MCP：规范原话「Every JSON-RPC message sent from the client MUST be a new HTTP POST request」。<em class="ev">[doc]</em> 所以第 5 节那 9 条报文里，client 到 server 的 `[01] [03] [04] [06] [08]` 在 HTTP 下是 **5 趟独立的 POST 往返**，每趟重复带全套 header；而在 stdio 下它们只是同一根管道里的 5 行文本、**0 趟网络往返**。

换来什么：server 是独立常驻进程，能同时服务多个 client、能跨机器跨设备、厂商可热更新。代价：网络依赖、延迟、要管 token、要防 DNS rebinding（规范强制校验 `Origin`、本地只绑 `127.0.0.1`）。

### 6.4 SSE：把那通电话挂着，让对方一直说

SSE = **Server-Sent Events**，仍然是 HTTP，但服务端**不立刻结束响应**：回一个 `Content-Type: text/event-stream`，然后连接保持打开，隔一会儿写一段数据，客户端逐段收。方向是**单向的：服务器到客户端**。

```text
id: 1
event: message
data: {"jsonrpc":"2.0","method":"notifications/progress","params":{"progress":1,"total":3}}

id: 2
event: message
data: {"jsonrpc":"2.0","method":"notifications/progress","params":{"progress":2,"total":3}}
```

每个事件以空行结尾；`data:` 后面那段就是信纸，往往仍是 JSON-RPC 通知。用途是进度播报、日志流、长任务分段返回，以及让 server 主动推 `notifications/tools/list_changed`。

> 类比：打电话不挂，对方每隔几秒播报一条进展。**你要说话，得另外再拨一通**——SSE 不能反向传。

实验里 1 次 GET 建连，服务端在同一条连接上推了 3 条事件，请求数**不随事件数增长**。这正是它相对「反复轮询 HTTP」的价值。

### 6.5 为什么文档列三种，规范只讲两种

要分清「宿主实现口径」和「协议版本口径」：

| | 端点 | 怎么送 |
|---|---|---|
| **STDIO** | 无端点 | 父子进程管道，换行分隔 |
| **HTTP + SSE**（MCP 2024-11-05，旧） | **两个**：一个 POST 端点发消息，一个 SSE 端点收推送 | 发与收走不同的连接 |
| **Streamable HTTP**（MCP 2025-06-18 起，取代上一个） | **单个** MCP endpoint | 每条 client 到 server 消息一个 POST；服务端可把**该次 POST 的响应**升级成 SSE 流，用来推多条消息 |

宿主文档写 STDIO / SSE / HTTP，是宿主侧的配置口径，很可能对应「本地进程 / 旧版 SSE 传输 / 新版 Streamable HTTP」三项并存。宿主具体怎么映射，没有一手资料，不下断言。能确定的是：SSE 与 HTTP 都基于 HTTP，**SSE 是 HTTP 之上的一种响应方式，不是与 HTTP 并列的第三种东西**——所以「三选一」这个心智模型本身就不对。

### 6.6 一张表收尾

| | STDIO | HTTP（Streamable） | SSE |
|---|---|---|---|
| 本质 | 本机进程管道 | 一问一答的请求/响应 | 挂着的 HTTP 响应流 |
| 方向 | 双向（两个流） | 客户端问、服务端答 | 单向：服务端到客户端 |
| 一条 JSON-RPC 要几次往返 | 0 次网络 | 1 次 POST | 建 1 次 GET，可收 N 条 |
| 网络与端口 | 无 | 有 | 有 |
| 凭据 | 环境变量 | header（Bearer 或 OAuth） | 同 HTTP |
| 典型场景 | 本地自建 server | 厂商托管 MCP | 进度通知、服务端主动推 |

<div class="box takeaway"><span class="t">一句话</span><p>STDIO 是「不出门的管道」，HTTP 是「每次重新拨号的问答」，SSE 是「不挂电话的单向播报」；信纸始终是那一串 JSON。</p></div>

<h2><span class="n">7</span>Skill 是不是鸡肋：一半对，而且官方也这么说</h2>

<p class="lede">如果 Skill 只是把公开知识整理成一份说明文档，那对一个足够强的模型来说确实没有增量。问题是，很多 Skill 确实只做到了这一步，而另一些能做的事 prompt 做不到。界线是可以划清楚的。</p>

### 7.1 先承认：知识型 Skill 在贬值

如果「CDISC ADaM 核查 Skill」等于把 CDISC 规范整理成一份 `SKILL.md`、让模型照着读一遍再判断，那质疑完全成立：2026 年的模型读得懂 CDISC，一个 prompt 就能做得差不多，做成 Skill 只是把 prompt 存进了文件夹，还多一层维护成本。

这不是客套。Anthropic 官方最佳实践的头一条原则就是：

> **Default assumption: Claude is already very smart.** Only add context Claude doesn't already have. … "Can I assume Claude has this information?" "Does this paragraph justify its token cost?"
>
> —— Skill authoring best practices <em class="ev">[doc]</em>

把模型已知的知识复述一遍的 Skill，官方自己就不建议写。技能市场里大量这类包，觉得鸡肋不是错觉。

### 7.2 但同一份文档里还有另一条

> **Prefer scripts for deterministic operations:** Write `validate_form.py` rather than asking Claude to generate validation code.
>
> **Bundle comprehensive resources:** Include complete API docs, extensive examples, and large datasets. **These incur no context penalty until accessed.**
>
> **Low freedom** (specific scripts, few or no parameters) — Use when: Operations are fragile and error-prone; **Consistency is critical**; A specific sequence must be followed.
>
> —— 同上 <em class="ev">[doc]</em>

以及 overview 里那句定位：

> Skills use Claude's VM environment to provide **capabilities beyond what's possible with prompts alone** … **progressive disclosure**: Claude loads information in stages as needed, rather than consuming context upfront.
>
> —— Agent Skills overview <em class="ev">[doc]</em>

这两组话放在一起，界线就清楚了：**Skill 的价值不在「教模型怎么做」，而在「给系统加上模型给不了的东西」。**

### 7.3 两类能力要分开算

| | 知识 / 方法（模型能不能想明白） | 执行 / 口径 / 留痕（每次能否一模一样地做） |
|---|---|---|
| 典型 | 「ADaM 里 USUBJID 该唯一」「派生变量怎么命名」 | 「按机构 SOP v3.2 的 12 条规则逐项判定，输出固定 JSON，附规则版本号」 |
| 模型变强后 | **贬值**，prompt 足够 | **不贬值**，甚至更值钱，因为要可审计 |
| 纯 prompt 能交付吗 | 能 | 不能稳定交付 |

「一个 prompt 就能实现」通常只覆盖了左列。右列里 prompt 给不了的是**可复核性**：让模型看一眼数据集说缺哪些变量，20 次里可能 19 次对，但没法证明第 20 次也对，也没有一份可签字、可 diff、可追溯版本的执行记录。在临床与合规语境里，这不是风格差异，是实质差异。

### 7.4 一个能自己跑的证据

第 5 节那个 demo 里，用完全相同参数连调了两次 `tools/call`：

```text
[07] {"dataset":"ADSL","checked":4,"missing":["TRT01P","TRT01PN"],"status":"FAIL","engine":"deterministic-code-v1.0.0"}
[09] {"dataset":"ADSL","checked":4,"missing":["TRT01P","TRT01PN"],"status":"FAIL","engine":"deterministic-code-v1.0.0"}
两次调用字节级一致 : 是（确定性执行）
```

`engine` 字段带版本号，意味着这份结果可以被另一个人、在另一台机器上、用同一个脚本重算并对齐。Skill 完全可以捆绑这样的脚本——官方 Level 3 明确包含 `scripts/`，且脚本代码**不必加载进上下文**就能执行。

这一段是「prompt 替代不了」最硬的落点：不是模型不够聪明，是「每次重新生成校验逻辑」这件事本身就不该交给概率模型。

### 7.5 上下文经济：一本诚实的账

渐进披露（Level 1/2/3）是 Skill 最容易讲虚的地方，把数字摊开，也把不适用情形说清。

设机构内部核查口径 12 条共约 2400 字，约 1800 token；100 次会话中只有 10 次涉及 ADaM。

| 方案 | 上下文开销 | 额外代价 |
|---|---|---|
| 甲：写进常驻 system prompt 或项目知识 | 100 × 1800 = **180,000 token**，且始终挤占窗口 | 与所有无关任务抢上下文 |
| 乙：Skill 渐进披露 | 常驻 description 约 30 token × 100 = 3,000；命中 10 次 × 1800 = 18,000，合计**约 21,000 token**（省约 88%） | 需要写对 `description`，否则不触发 |
| 丙：每次手动贴 prompt | token 上与乙接近 | **人要记得贴、贴的版本可能不同、新人不知道存在、无法 review** |

**别误读这张表**：如果每次会话都跟 ADaM 有关，乙和丙的 token 差距趋近于零，Skill 在 token 上并不划算。Skill 真正的规模优势是「**装 50 个 Skill 不会把 50 份说明书都塞进上下文**」，以及丙那一列里被省掉的**组织记忆成本**。

所以准确说法是：**Skill 省的主要不是 token，是人和版本。**

### 7.6 不可替代的四件事

1. **确定性执行**：捆绑脚本，结果可复核、可署名版本、能进 CI。
2. **上下文经济**：三级渐进披露，Level 3 的大部头不访问就不付上下文成本。
3. **资产化**：版本号、owner、变更记录、评审、跨人跨会话复用、可挂自动化定时任务。prompt 躺在聊天记录里，这些全没有。
4. **触发可靠性**：`description` 由框架匹配，不依赖用户每次记得把规范贴进来。

### 7.7 明确「别做 Skill」的清单

命中三条以上，直接写 prompt：

- 一次性任务，做完不会再有第二次；
- 模型先验充分（「用 pandas 读 csv 画折线图」这类）；
- 纯解释、纯讨论，无外部数据、无副作用；
- 没有固定口径要求，输出每次不同反而更好；
- 规则还在频繁变，写下来就过期；
- 只有一个人用、也不打算沉淀给团队；
- 内容只有模型已知的公开知识，没有私有增量。

反过来，命中两条以上才值得做成 Skill：会重复三次以上、多人共用、含机构内部口径、需要跑脚本且结果要可复核、要留痕过审计、要挂无人值守自动化、材料很大不能每次塞窗口。

### 7.8 为什么市场上大量 Skill 确实鸡肋

这是结构性原因，不是个别作者的水平问题：

- **只有 `SKILL.md`，没有 `scripts/`、没有 `references/`**，退化成一份排版好看的 prompt；
- 内容是对官方文档的复述，模型本来就知道，零增量；
- `description` 写得含糊，触发不稳，用户觉得「装了跟没装一样」；
- 装得太多，光 description 也占上下文、互相抢触发，还引入第三方脚本的供应链风险；
- 把「输出格式漂亮」当成价值——格式是导出脚本的事，不是 Skill 的护城河。

顺带说一句：一份排版讲究的 Word 报告只是导出脚本的机械转换，不构成论证。能构成论证的是可运行脚本、原始报文、可复核的版本号。

### 7.9 把 CDISC 例子重写成值得做的版本

同一个主题，换成下面这个结构，它就不是 prompt 能替代的了：

```text
adam-check/
├── SKILL.md                      # 很薄：只写触发条件、路由、引用哪个 SOP 版本
├── references/
│   └── site-sop-v3.2.md          # 机构内部口径 —— 模型不可能知道，这是核心增量
├── scripts/
│   └── validate_adam.py          # 确定性校验，输出机器可读 JSON + rule_version + engine 版本
├── templates/
│   └── finding-report.md         # 固定输出口径，便于归档与比对
└── CHANGELOG.md                  # v3.1 → v3.2 改了哪条规则、谁批准、何时生效
```

- `SKILL.md` 只回答「什么时候跑、按哪个版本、结果怎么报」，不复述 CDISC 常识；
- 校验逻辑全部在 `validate_adam.py`，与第 5 节 demo 同理，两次运行字节级一致；
- 输出里带 `sop_version` 与 `engine_version`，可以写进交付物供复核；
- `CHANGELOG.md` 让「三个月前那份报告是按哪版规则出的」这个问题有答案。

它还可以和第 5 节组合：**脚本通过本地 MCP tool 暴露，Skill 负责决定何时调用、按哪版口径、结果如何呈报**。这时三者叠加的理由就从「概念上互补」变成了三件具体的事：确定性执行、组织口径、标准化接口。

<div class="box takeaway"><span class="t">判断标准</span><p>模型越强，Skill 的价值重心越从「教模型」迁移到「约束系统」。拿到一个 Skill，只看它有没有这四样：<b>私有数据、可执行代码、固定口径、版本留痕</b>。一样都没有，基本就是一份漂亮的 prompt。</p></div>

<h2><span class="n">8</span>把五件事放回一张图</h2>

```text
宿主进程（Host：WorkBuddy / Harness / Claude Desktop）
│
├─ L1 内部组件层 —— 「插件」在 Harness 里的含义
│    模型适配器 / 工具注册 / 会话日志 / 沙箱 / Agent loop / UI
│    全部可替换、可卸载、可逆（Cordis）
│    └─ 其中若干组件承载下面两种能力：
│         ├─ MCP Client ────── 标准化外设接口 ──→ MCP Server（本地 stdio / 远程 HTTP）
│         │                                      提供 tools / resources / prompts
│         └─ Skill 加载器 ───── 认知层 ──→ SKILL.md + scripts/ + references/
│                                          私有口径 / 确定性执行 / 版本留痕
│
└─ L2 外部服务层 —— ChatGPT Plugins 当年的含义（旧形态已下线）
     ai-plugin.json + OpenAPI → 把 API 说明塞进 prompt
     ↓ 被统一
     MCP（JSON-RPC + tools/list 结构化发现 + 跨宿主复用）
```

三句话收尾：

1. **插件不是被淘汰的概念，是被用滥的词。** 先问「在进程内还是进程外」，再谈新旧。
2. **MCP 不区分本地或商用**，协议相同。真正要评估的是传输方式、凭据放在哪、数据出不出本机，以及赌的是代码还是厂商。
3. **Skill 不跟 prompt 比谁写得好**，比的是有没有模型给不了的东西。纯知识型 Skill 会继续贬值，含脚本与私有口径的会继续增值。

<h2><span class="n">9</span>证据与来源</h2>

**一手：官方原文，已抓正文核对**

- [DeepSeek Harness 官网](https://www.deepseek.com/harness) 与[英文页](https://deepseek.com/harness/en)：一切皆插件、Cordis、扩展工具与技能与界面
- [OpenAI, ChatGPT plugins (2023-03-23)](https://openai.com/blog/chatgpt-plugins)：页首 deprecated 声明、manifest 进 prompt 的机制、「预期出现开放标准」原句
- [MCP 2025-06-18 architecture](https://modelcontextprotocol.io/specification/2025-06-18/architecture)：Host/Client/Server 职责、1:1 关系、server 可为本地或远程
- [MCP 2025-06-18 basic/transports](https://modelcontextprotocol.io/specification/2025-06-18/basic/transports)：stdio、Streamable HTTP、安全警告
- [MCP 2025-06-18 basic/authorization](https://modelcontextprotocol.io/specification/2025-06-18/basic/authorization)：STDIO 与 HTTP 的授权分野、OAuth 2.1、RFC 8707、confused deputy
- [MCP 2025-06-18 basic/lifecycle](https://modelcontextprotocol.io/specification/2025-06-18/basic/lifecycle)：initialize、notifications/initialized、操作阶段
- [Anthropic, Agent Skills overview](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)：beyond prompts alone、Level 1/2/3、progressive disclosure
- [Anthropic, Skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)：context window is a public good、default assumption、prefer scripts、low freedom
- [WorkBuddy / CodeBuddy MCP 文档](https://www.workbuddy.cn/docs/cli/mcp)：三种传输、配置作用域、项目级首次连接审批
- [OpenAI Developers: Function calling](https://developers.openai.com/api/docs/guides/function-calling)

**二手：只用于时间线与技术形态，未作为定义依据**

- ChatGPT Plugins 停用的具体日期（2024-03-19 / 2024-04-09）与 GPT Actions 的承接关系：开发者社区转述与技术百科；官方帮助文章实测已 404，无法直接引用。
- `ai-plugin.json` 加 OpenAPI 的具体字段（`name_for_model` / `description_for_model`）：技术百科与 2023 年开发教程交叉核对。
- Cordis 的「服务 / 类型化事件 / 可逆副作用」三要素与热插拔：社区架构解读。
- 「MCP 以插件形态接入 Harness」：社区解读；官方清单可确认的只有 `skills`。

**本机实跑：零外发**

- [minimal-mcp.js](/demos/mcp-demo/minimal-mcp.js)：按 2025-06-18 规范手写的最小 MCP stdio server 与 client
- [mcp-session.txt](/demos/mcp-demo/mcp-session.txt)：9 条真实 JSON-RPC 报文、版本协商、工具发现、两次调用的确定性比对
- [http-transport-demo.js](/demos/mcp-demo/http-transport-demo.js)：在本机 `127.0.0.1` 起 HTTP 服务，实测 POST 往返与 SSE 推流
- [http-transport-session.txt](/demos/mcp-demo/http-transport-session.txt)：3 趟 HTTP 请求的原始请求行、请求头、请求体、响应，以及 1 次 GET 连推 3 条 SSE 事件

<h2><span class="n">10</span>附：怎么自己复现</h2>

四个文件都在站上，直接下载即可：

- <a href="/demos/mcp-demo/minimal-mcp.js" download>minimal-mcp.js</a>
- <a href="/demos/mcp-demo/mcp-session.txt" download>mcp-session.txt</a>
- <a href="/demos/mcp-demo/http-transport-demo.js" download>http-transport-demo.js</a>
- <a href="/demos/mcp-demo/http-transport-session.txt" download>http-transport-session.txt</a>

放进同一个目录，然后：

```bash
node minimal-mcp.js client         # stdio：打印 9 条 JSON-RPC 报文 + 会话结论
node minimal-mcp.js client > my-log.txt   # 留档
node minimal-mcp.js server         # 单独启动 server，可对接任何 MCP client
node http-transport-demo.js        # HTTP/SSE：打印真实请求行、请求头、请求体与响应
```

两个脚本只用 Node 内置模块、零依赖、只走 `127.0.0.1`，**不发任何外部请求**。`http-transport-demo.js` 的输出会明确列出：3 条 JSON-RPC 等于 3 次 POST 往返、每次 `Authorization` 重带、SSE 一次 GET 连推 3 条事件。

`minimal-mcp.js` 是单文件双模式：`server` 模式只从 stdin 读 JSON-RPC、只往 stdout 写 JSON-RPC（日志走 stderr）；`client` 模式用 `spawn` 拉起子进程，逐条记录方向、方法名与完整报文。工具故意写成纯集合运算，用来验证确定性。

<p class="small">版本说明：本文与 demo 基于 MCP 2025-06-18。检索中已出现 2025-11-25 版规范页面，核心生命周期与传输机制一致，具体细则以实际使用的协议版本为准。</p>
