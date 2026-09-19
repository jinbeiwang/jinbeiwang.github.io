---
title: 这个站怎么组织：新增一篇笔记的完整流程
summary: 目录约定、frontmatter 字段、版式从哪来、本地预览与发布，以及那 9 个独立项目站现在放在哪里。
date: 2026-09-19
category: Site notes
tags: [Astro, GitHub Pages, 笔记规范]
lang: zh
---

这篇是本站的维保说明。改动站点的结构之前先读它一遍；日常写笔记只需要看前三节。

## 一页纸的结论

新增一篇笔记 = **跑一条命令，改一个文件，然后 push**。首页条目、分类分组、标签页、正文左侧目录全部自动生成，不需要碰任何别的地方。

```bash
npm run new hash-basics                          # 1. 生成 src/content/notes/hash-basics.md
npm run dev                                      # 2. 边写边看（或 npm run build）
git add -A && git commit -m "..." && git push    # 3. 发布
```

`npm run new <slug>` 把 `templates/new-note.md` 复制成 `src/content/notes/<slug>.md`，并把今天的日期填进 frontmatter。

**模板本身就是一篇能跑的笔记**，把每个部件都示范了一遍、也注明了各自用途 —— 把内容换成你的，再把注释删掉就完事。想看成品长什么样，照着它写一篇然后 `npm run dev`。

文件名就是 URL。`hash-basics.md` 对应 `https://jinbeiwang.github.io/notes/hash-basics.html`，**所以文件名一旦确定就不要再改** —— 改文件名等于让已经发出去的链接失效；要改标题就改 frontmatter 里的 `title`。

脚本会拒绝非 kebab-case 的 slug，也会拒绝覆盖已有文件。想顺便定标题：

```bash
npm run new hash-basics -- --title "SAS hash 对象，从头开始"
```

## 从一篇 Markdown 到一页 HTML

这件事只在**构建期**发生。`npm run build` 的时候 Astro 按顺序做四件事，做完就退场：

```
src/content/notes/*.md
   │  ①  src/content.config.ts          读集合，按 schema 校验 frontmatter
   │  ②  Markdown → HTML                代码块交给 Shiki 上色
   │  ③  src/pages/notes/[...slug].astro  getStaticPaths 为每篇生成一条路由
   │  ④  src/layouts/Note.astro          套上页头、出处条、目录抽屉
   ▼
dist/
```

| 文件（都在 `src/` 下） | 它负责什么 |
|---|---|
| `content.config.ts` | 声明只有一个集合 `notes`，并规定 frontmatter 有哪些字段、哪个必填。**文件名就是 id，id 就是 URL** |
| `pages/notes/[...slug].astro` | `getStaticPaths()` 遍历集合，为每篇笔记生成一条路径；`render(entry)` 把 Markdown 变成 HTML |
| `layouts/Note.astro` | 唯一的页面外壳。**版式住在这里和两张 CSS 里，永远不在笔记文件里** |
| `pages/index.astro` | 首页读的是同一个集合，按 `category` 分组、按 `date` 倒序。**新笔记不用手工登记** |

由此得到几条平时用得上的性质：

- **文件名 = URL**。改名会让已发布的链接失效，要换说法请改 `title`，不要改文件名。
- **frontmatter 写错在构建期就报错**。`title` 必填、`date` 会被强制解析成日期 —— 不是"上线后才发现"。
- **目录抽屉由正文的 `h2` / `h3` 在浏览器里现场生成**，所以新笔记免费获得目录，没有任何清单要维护。
- **`draft: true` 的笔记不生成页面**，也不进首页。

> 值得记住的一点：**生成出来的页面里没有 Astro 的任何东西**。实测 `dist/_astro/` 里只有两张 CSS，`.js` 文件数是 **0**，HTML 里也没有 `astro-island` 之类的标记。Astro 在这里是"生成器"不是"框架"——它把 Markdown 编译成静态 HTML 就退场，浏览器收到的和手写的 HTML 没有区别。所以它省掉的是重复劳动，而不是往页面里加东西：排版、目录、首页收录，这三件以前每篇都要重复做的事，现在都由构建完成。

## frontmatter 字段

文件顶部用真正的 YAML frontmatter，这是 Markdown 的写法，不用担心它被渲染到页面上。

```yaml
---
title: 标题
summary: 一句话摘要，显示在首页条目下方
date: 2026-09-19
category: Site notes
tags: [Astro, GitHub Pages]
lang: zh
---
```

| 字段 | 必填 | 说明 |
|---|---|---|
| `title` | 是 | 首页条目与浏览器标题 |
| `date` | 是 | `YYYY-MM-DD`，首页按它倒序排列 |
| `summary` | 否 | 缺省时首页只显示标题行 |
| `category` | 否 | 必须是既有分类之一，否则会在首页多出一个新分区 |
| `tags` | 否 | 会生成 `/tags/<tag>.html` 标签页，并进入首页的标签筛选 |
| `lang` | 否 | `zh` 或 `en`，决定标题右侧的角标 |

既有分类共六个：`Site notes`、`Statistical methods`、`SAS patterns`、`Languages and practice`、`Indexes and tools`、`Learning log`。

> 与旧笔记不同的一点：旧的手写 HTML 笔记因为**没有构建步骤**，只能在 doctype 之后放一段 HTML 注释来承载元数据，否则顶部的 `---` 会被浏览器当正文渲染出来。现在有了构建步骤，frontmatter 在构建时就被剥掉了，浏览器根本收不到它。所以这里用标准 YAML，和 Markdown 的惯例一致。

## 版式从哪来：两张样式表，各管一件事

全站样式按页面类型切成两份：

```
src/styles/base.css    站点骨架、首页、标签页        —— 每页都引
src/styles/note.css    笔记页的长文阅读版式          —— 只被 Note.astro 引
```

`base.css` 顶部的 `:root` 里是首页那套令牌（790px 正文宽、衬线标题、硬分隔线）。笔记要的是另一套：880px 正文宽、全无衬线标题、圆点列表、更松的代码块。两件事不一样，所以分开写，互不干扰。

笔记的正文由 `src/layouts/Note.astro` 套用这两张表，**所以笔记文件里一行 CSS 都不需要写**，写出来的页面自动和别人一致。

想改观感就改这两张表：首页和标签页动 `base.css`，笔记动 `note.css`。这是从「一篇笔记一份 CSS」换过来的主要收益 —— 以前改一次样式要动 N 个文件，而且改不齐。

代价也说清楚：**笔记不能再有自己独立的视觉微调**。以前每篇手写 HTML 可以各调各的间距，现在统一由 `note.css` 决定。如果某篇确实需要特殊处理，可以在 Markdown 里写内联 HTML 覆盖，但那属于例外，不要变成常态。

### 两个色相，各司其职

笔记页只用两个主色，各有固定职责，不要混用：

两个色相份量相当，但职责不重叠 —— 混用会让页面变成装饰：

<table>
  <thead><tr><th style="width:72px;">色相</th><th style="width:110px;">值</th><th>管什么</th></tr></thead>
  <tbody>
    <tr><td>靛蓝</td><td><code>#1b4f8a</code></td><td><b>结构与导航</b> —— 分类行、返回链接、章节序号、正文链接、代码块左侧竖线、代码关键字、范围框（<code>box note</code>）。一句话：你点了会「走去别处」的都属于它</td></tr>
    <tr><td>祖母绿</td><td><code>#0f7b5f</code></td><td><b>证据与结论</b> —— 结论框（<code>box takeaway</code>）、<code>[doc]</code> / <code>[lit]</code> / <code>[实践]</code> 出处标记、来源/状态标签、图号、表格三条线与表头底色、列表符号、引用块左边线、目录里正在读的那一条与「CONTENTS」上方的短横、文末收口线、「通过」pill。一句话：它会告诉你「我们发现了什么」</td></tr>
  </tbody>
</table>

页头那条第 2 像素的分隔线是两个色相**唯一**的交汇处：左半靛蓝、右半祖母绿。加新元素时先问它属于上面哪一句，再用对应的颜色。第三个颜色只允许有语义理由 —— 琥珀 `cav` 是风险、红 `bad` 是失败，仅此而已。

标题上不带任何装饰标记 —— 二级标题只有一个靛蓝的序号，层次交给字号和留白。曾经有过一根 28px 的祖母绿短横飘在标题上方，后来删掉了：它会在每一节重复一次（SAS 篇 7 次、前端篇 14 次），重复多了就变成一份大纲，而大纲的位置在左侧抽屉里。表示「你在这里」的颜色只留在抽屉里 —— 正在读的那一条是祖母绿底加左竖线。

> 记一条原则：**颜色决定不要变成排版决定**。上一轮加颜色时，所有装饰都写成 `position:absolute` 放进元素本来就有的留白里，不占版面；所以「只改颜色、不动版式」是可以验证的 —— 用 `documentElement.scrollHeight` 在改动前后各量一次，数值应当一字不差。这次删掉那根短横，把规则临时注回页面再量，页面高度三次完全相同。

### 笔记里可以用的类

这是这套版式的词汇表，写在 Markdown 里直接生效，不用自己写样式：

| 写法 | 用途 |
|---|---|
| `class="box note"` + `<span class="t">小标题</span>` | 说明框（靛蓝）：范围、约定、去标识化声明 |
| `class="box finding"` | 风险框（琥珀）：这里会出错、这里有前提 |
| `class="box takeaway"` | 结论框（祖母绿）：每节收口的那一句 |
| `class="lede"` | 紧跟 `h2` 之后的导语，自动带一条软分隔线 |
| `class="meta-row"` | 来源 / 状态那一行的键值条 |
| `class="small"` | 小一号、低对比度的辅助说明 |
| `class="num"` | 数字单元格，等宽数字不跳动 |
| `<em class="ev">[doc]</em>` | 出处标记，渲染成祖母绿标签 |
| `<pre>` 内 `class="cm"` / `"kw"` / `"mk"` | 手写代码高亮：注释 / 关键字 / 标记 |

二级标题写 `## 标题`；要带序号就写 `<h2><span class="n">1</span>标题</h2>`，序号是靛蓝的。

**目录不用维护** —— 它在页面打开时从正文的 `h2` / `h3` 生成，左侧抽屉、滚动高亮、Esc 收起、开合状态记忆全是布局层的事，一篇新笔记什么也不用做。

**以后新增的笔记一律按这套写**：颜色、间距、目录都不出现在笔记文件里，全部由 `note.css` 决定。

同一套版式还有一份**站外产出版**：`sas-pattern-note` 技能生成单文件 HTML（自带目录抽屉与同一组配色），用来在站外单独给别人一份笔记时用它。改了一边的配色，另一边也要跟着改，否则两边会漂移。

## 本地预览与发布

```bash
npm run dev      # 本地预览，改文件即时刷新
npm run build    # 产出 dist/，推之前先跑一遍
```

发布走 GitHub Actions：push 到 `main` 之后自动构建并部署到 Pages，**不需要手工推送 `dist/`**。

> 注意 Pages 的构建方式已经从 `legacy` 换成了 `workflow`。`legacy` 是 GitHub 服务端用 Jekyll 构建，而这里用的是 Astro，必须由 Actions 来跑。换过之后，仓库根目录的 `.nojekyll` 就不再关键了，但保留它没有坏处。

## 那 9 个项目站

`mmrm-guide`、`lmm-notes`、`cif-vs-km-ci`、`sas-pattern-notes`、`clinical-python-roadmap`、`learn-r-clinical`、`Proceedings`、`github-radar`、`agent_harness` 这 9 个仓库**保持独立**，各自部署在 `jinbeiwang.github.io/<仓库名>/`，地址不变。

它们在首页的「External projects」分区里列出，登记处是：

```
src/data/projects.json
```

加一个新的外部项目就在这个数组里加一条；它不是笔记，不参与按日期排序。

本项目自己新增的笔记一律进 `src/content/notes/`，**不再新开仓库**。

## 常见错误

**改了文件名**。文件名即 URL，改了既有链接就断了。要改标题改 `title`，不要改文件名。

**在笔记里写 `category` 用了不存在的值**。首页会因此多出一个分区。想新增分类，先去 `src/data/categories.json` 登记，再在笔记里使用。

**把图片放进 `src/`**。会被当成待处理的资源。图片放 `public/` 下，按 `/images/<name>.png` 引用。

**忘了跑 `npm run build` 就 push**。本地预览是宽松的，构建会真的检查 frontmatter 类型和内部链接。养成推之前跑一次的习惯。

**把「重线」写成 `1.8px`**。Chromium 会把 2px 以下的边框一律渲染成 1px —— 0.5、1、1.5、1.8 全都是 1px —— 所以 `1.8px` 的表格重线和它下面的细线一样粗，看上去完全没生效。要重线就写 `2px`。
