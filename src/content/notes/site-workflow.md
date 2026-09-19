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

新增一篇笔记 = **新建一个 Markdown 文件**，然后 push。首页的条目、分类分组、标签页全部自动生成，不需要碰任何别的地方。

```
src/content/notes/<kebab-case-slug>.md
```

文件名就是 URL。上面的文件对应 `https://jinbeiwang.github.io/notes/<slug>.html`，**所以文件名一旦确定就不要再改** —— 改文件名等于让已经发出去的链接失效。

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

## 版式从哪来：为什么不用自己写 CSS

全站样式只有一份：

```
src/styles/base.css
```

它定义了配色、字号、行高、代码块、表格、图注。笔记的正文由 `src/layouts/Note.astro` 套用这些样式，**所以笔记文件里一行 CSS 都不需要写**，写出来的页面自动和别人一致。

改配色就在 `base.css` 顶部的 `:root` 里改一个变量，整个站（含首页、标签页）一起变。这是从「一篇笔记一份 CSS」换过来的主要收益：以前改一次样式要动 N 个文件，而且改不齐。

代价也说清楚：**笔记不能再有自己独立的视觉微调**。以前每篇手写 HTML 可以各调各的间距，现在统一由 `base.css` 决定。如果某篇确实需要特殊处理，可以在 Markdown 里写内联 HTML 覆盖，但那属于例外，不要变成常态。

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
