#!/usr/bin/env node
/**
 * Publish the weekly clinical-programming digests to GitHub Pages.
 *
 *   npm run weekly
 *   npm run weekly -- --src "G:/test/github/notes/weekly-digest"
 *
 * The digests live OUTSIDE this repo, in notes/weekly-digest/. This script is
 * the only bridge between the two:
 *
 *   notes/weekly-digest/YYYY-MM-DD-clinical-programming-weekly.html
 *     -> public/weekly/<same name>
 *     -> https://jinbeiwang.github.io/weekly/<same name>
 *
 * It also rebuilds public/weekly.html, an index of every published issue.
 * Everything under public/ is copied verbatim by `astro build` (see
 * astro.config.mjs), so these pages never go through markdown/Shiki.
 *
 * Idempotent: re-running with no new issues changes no file bytes. It never
 * deletes an issue that is missing from the source directory — removing a
 * published page is a deliberate decision, not a side effect of a local cleanup.
 */
import { readdirSync, readFileSync, writeFileSync, existsSync, mkdirSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const OUT_DIR = resolve(ROOT, 'public/weekly');
const INDEX = resolve(ROOT, 'public/weekly.html');

const args = process.argv.slice(2);
let SRC = resolve(ROOT, '../../notes/weekly-digest');
for (let i = 0; i < args.length; i++) {
  if (args[i] === '--src' || args[i] === '-s') SRC = resolve(args[++i] ?? SRC);
}

// The file name is the URL. Only dated digests qualify; the index and the
// markdown/JSON companions in the source directory are deliberately not published.
const NAME = /^(\d{4}-\d{2}-\d{2})-clinical-programming-weekly\.html$/;

if (!existsSync(SRC)) {
  console.error(`error: source directory not found: ${SRC}`);
  console.error('       pass --src <dir> to point at notes/weekly-digest/');
  process.exit(1);
}

mkdirSync(OUT_DIR, { recursive: true });

// 1. copy any issue that is new or has changed
const sources = readdirSync(SRC).filter((f) => NAME.test(f)).sort();
let written = 0;
for (const f of sources) {
  const from = resolve(SRC, f);
  const to = resolve(OUT_DIR, f);
  const bytes = readFileSync(from);
  const current = existsSync(to) ? readFileSync(to) : null;
  if (!current || !current.equals(bytes)) {
    writeFileSync(to, bytes);
    written++;
    console.log(`  ${current ? 'updated' : 'added  '}  public/weekly/${f}`);
  }
}

// 2. rebuild the index from what is actually published, newest first
const issues = readdirSync(OUT_DIR).filter((f) => NAME.test(f)).sort().reverse();

function windowFor(iso) {
  const [y, m, d] = iso.split('-').map(Number);
  const end = new Date(y, m - 1, d);          // local, not UTC
  const start = new Date(y, m - 1, d - 6);
  const fmt = (t) => `${t.getFullYear()}-${String(t.getMonth() + 1).padStart(2, '0')}-${String(t.getDate()).padStart(2, '0')}`;
  return `${fmt(start)} — ${fmt(end)}`;
}

function esc(s) {
  return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

const rows = issues.map((f) => {
  const iso = f.match(NAME)[1];
  return `      <li><a href="/weekly/${esc(f)}"><span class="d">${iso}</span>`
    + `<span class="w">覆盖 ${windowFor(iso)}</span>`
    + `<span class="go">阅读本期 &rarr;</span></a></li>`;
}).join('\n');

const html = `<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>临床统计编程 · 每周简报</title>
<meta name="description" content="面向临床统计编程的每周信息简报：制药监管、方法学、统计编程、CDISC 与 AI。">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<style>
:root{
  --paper:#fbfaf7; --card:#ffffff; --ink:#17181a; --muted:#5f6368;
  --line:#e2e0d9; --line-soft:#eeece6;
  --accent:#1b4f8a; --ev:#0f7b5f;
  --maxw:880px;
}
*{box-sizing:border-box}
body{
  margin:0; background:var(--paper); color:var(--ink);
  font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Microsoft YaHei",sans-serif;
  font-size:15.5px; line-height:1.78;
}
.wrap{max-width:var(--maxw); margin:0 auto; padding:0 28px 80px}
header.mast{padding:56px 0 26px; border-bottom:1px solid var(--line)}
.kicker{font-size:11.5px; letter-spacing:.16em; text-transform:uppercase; color:var(--accent); font-weight:700}
h1{font-family:Georgia,"Songti SC","SimSun",serif; font-weight:600; font-size:32px; line-height:1.3; margin:14px 0 10px}
.sub{color:var(--muted); font-size:13.5px; margin:0}
.byline{
  margin-top:22px; padding-top:14px; font-size:12.5px; color:var(--muted);
  background-image:linear-gradient(90deg,var(--accent) 0 50%,var(--ev) 50% 100%);
  background-repeat:no-repeat; background-size:100% 2px; background-position:0 0;
}
.byline a{color:var(--accent); text-decoration:none; border-bottom:1px solid #c9d9ec}
section{margin-top:40px}
h2{font-family:Georgia,"Songti SC","SimSun",serif; font-size:21px; font-weight:600; margin:0 0 18px; padding-top:18px; border-top:1px solid var(--line)}
.note{color:var(--muted); font-size:13px; margin:0 0 18px}
.issues{list-style:none; padding:0; margin:0}
.issues li{margin:0 0 10px; background:var(--card); border:1px solid var(--line); border-radius:2px}
.issues a{display:flex; flex-wrap:wrap; align-items:baseline; gap:6px 16px; padding:16px 20px; text-decoration:none; color:inherit}
.issues a:hover{border-left:3px solid var(--ev); padding-left:18px}
.issues .d{color:var(--accent); font-weight:600; font-size:15px}
.issues .w{color:var(--muted); font-size:13px}
.issues .go{margin-left:auto; color:var(--ev); font-size:13px; white-space:nowrap}
.empty{color:var(--muted); background:#fff; border:1px solid var(--line); padding:16px 20px; font-size:14px}
footer{margin-top:52px; padding-top:18px; border-top:1px solid var(--line); font-size:12px; color:var(--muted)}
footer p{margin:0 0 6px}
footer a{color:var(--accent); text-decoration:none}
@media(max-width:640px){
  .wrap{padding:0 18px 60px} h1{font-size:26px}
  .issues a{flex-direction:column; gap:2px} .issues .go{margin-left:0}
}
</style>
</head>
<body>
<div class="wrap">

<header class="mast">
  <div class="kicker">Clinical Programming Weekly · Jinbei</div>
  <h1>临床统计编程 · 每周简报</h1>
  <p class="sub">每期覆盖过去 7 天（含运行当日）｜制药与监管 · 方法学 · 统计编程 · CDISC · AI</p>
  <div class="byline">共 <strong>${issues.length}</strong> 期　·　每周一更新　·　<a href="/">返回主站</a></div>
</header>

<section>
  <h2>已发布期次</h2>
  <p class="note">事实与推测分开、口径与存疑逐条列明；涉及监管决定与标准版本时，请以监管机构 / 标准组织的一手文件为准。</p>
${issues.length ? `  <ul class="issues">\n${rows}\n  </ul>` : '  <p class="empty">尚无已发布期次。</p>'}
</section>

<footer>
  <p>本页只汇编公开来源的摘要与链接，不含原文全文；摘要由 AI 概括，事实以原文为准。</p>
  <p>每期页面为静态 HTML，无脚本、无追踪，任何设备浏览器可直接打开。</p>
</footer>

</div>
</body>
</html>
`;

const previous = existsSync(INDEX) ? readFileSync(INDEX, 'utf8') : null;
if (previous !== html) {
  writeFileSync(INDEX, html, 'utf8');
  console.log('  rebuilt  public/weekly.html');
}

console.log('');
console.log(`sources   ${sources.length} issue(s) in ${SRC}`);
console.log(`published ${issues.length} issue(s) in public/weekly/  (${written} file(s) written)`);
console.log('index     /weekly.html  ->  https://jinbeiwang.github.io/weekly.html');
for (const f of issues) console.log(`issue     https://jinbeiwang.github.io/weekly/${f}`);
console.log('');
console.log('next: npm run build && git add -A && git commit -m "..." && git push');
