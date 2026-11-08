#!/usr/bin/env node
/**
 * 三种传输的「信封」对照实验（Node 内置模块，零依赖，全程 127.0.0.1，零外发）
 *
 *   node http-transport-demo.js
 *
 * 用同一批 JSON-RPC 消息，分别走：
 *   ① HTTP POST —— 每条消息一趟独立的请求/响应往返，打印真实 HTTP 报文
 *   ② SSE      —— 一次 GET 建立长连接，服务端在同一条连接上连推 3 条事件
 *   ③ stdio    —— 仅做数字对照，实际报文见 mcp-session.log（不产生任何网络请求）
 *
 * 目的：让「发起一次 HTTP 调用是什么意思」变成看得见的请求行、请求头、请求体和状态行。
 */

'use strict';
const http = require('http');

const MESSAGES = [
  { jsonrpc: '2.0', id: 1, method: 'initialize', params: { protocolVersion: '2025-06-18', capabilities: {}, clientInfo: { name: 'transport-demo', version: '1.0.0' } } },
  { jsonrpc: '2.0', id: 2, method: 'tools/list', params: {} },
  { jsonrpc: '2.0', id: 3, method: 'tools/call', params: { name: 'check_required_vars', arguments: { dataset: 'ADSL' } } },
];

const SSE_EVENTS = [
  { jsonrpc: '2.0', method: 'notifications/progress', params: { progress: 1, total: 3, message: 'reading dataset' } },
  { jsonrpc: '2.0', method: 'notifications/progress', params: { progress: 2, total: 3, message: 'checking variables' } },
  { jsonrpc: '2.0', method: 'notifications/message', params: { level: 'info', data: 'done' } },
];

let postCount = 0;

function post(port, payload) {
  return new Promise((resolve, reject) => {
    const body = JSON.stringify(payload);
    const req = http.request({
      host: '127.0.0.1', port, method: 'POST', path: '/mcp',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json, text/event-stream',
        'Authorization': 'Bearer ***DEMO_KEY***',
        'Mcp-Session-Id': 'demo-session-1',
        'Content-Length': Buffer.byteLength(body),
      },
    }, (res) => {
      let data = '';
      res.on('data', (c) => { data += c; });
      res.on('end', () => resolve({ status: res.statusCode, contentType: res.headers['content-type'], body: data }));
    });
    req.on('error', reject);
    req.end(body);
  });
}

function sseGet(port) {
  return new Promise((resolve, reject) => {
    const req = http.request({
      host: '127.0.0.1', port, method: 'GET', path: '/mcp',
      headers: { Accept: 'text/event-stream' },
    }, (res) => {
      console.log(`     响应行   : HTTP/1.1 ${res.statusCode} ${res.statusMessage}`);
      console.log(`     Content-Type: ${res.headers['content-type']}   ← 注意：不是 application/json，连接不关闭`);
      let buf = '';
      res.setEncoding('utf8');
      res.on('data', (chunk) => {
        buf += chunk;
        let i;
        while ((i = buf.indexOf('\n\n')) >= 0) {
          const frame = buf.slice(0, i);
          buf = buf.slice(i + 2);
          const dataLine = frame.split('\n').find((l) => l.startsWith('data: '));
          console.log(`     ↓ 收到一条事件: ${dataLine ? dataLine.slice(6) : frame}`);
        }
      });
      res.on('end', () => { console.log('     连接关闭（服务端推完了）'); resolve(); });
    });
    req.on('error', reject);
    req.end();
  });
}

const server = http.createServer((req, res) => {
  let raw = '';
  req.on('data', (c) => { raw += c; });
  req.on('end', () => {
    if (req.method === 'POST' && req.url === '/mcp') {
      postCount += 1;
      const msg = JSON.parse(raw);
      const reply = {
        jsonrpc: '2.0', id: msg.id,
        result: msg.method === 'tools/list' ? { tools: [] } : { ok: true, echo: msg.method },
      };
      const out = JSON.stringify(reply);

      console.log(`\n[HTTP 第 ${postCount} 次调用]  ← 一条 JSON-RPC = 一趟完整往返`);
      console.log(`  请求行     : ${req.method} ${req.url} HTTP/1.1`);
      console.log(`  Host       : ${req.headers.host}`);
      console.log(`  Content-Type: ${req.headers['content-type']}`);
      console.log(`  Authorization: ${req.headers.authorization}   ← 每趟都要重新带`);
      console.log(`  Mcp-Session-Id: ${req.headers['mcp-session-id']}   ← HTTP 本身无状态，靠头维持逻辑会话`);
      console.log(`  Content-Length: ${req.headers['content-length']} 字节`);
      console.log(`  请求体     : ${raw}`);
      console.log(`  响应行     : HTTP/1.1 200 OK`);
      console.log(`  响应体     : ${out}`);
      console.log(`  —— 本趟结束，TCP 连接可复用但「这一问一答」已完成；下条消息要重新 POST ——`);

      res.writeHead(200, {
        'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(out),
        'Mcp-Session-Id': 'demo-session-1',
      });
      res.end(out);
      return;
    }

    if (req.method === 'GET' && req.url === '/mcp') {
      res.writeHead(200, {
        'Content-Type': 'text/event-stream',
        'Cache-Control': 'no-cache',
        Connection: 'keep-alive',
      });
      let n = 0;
      const timer = setInterval(() => {
        n += 1;
        res.write(`id: ${n}\nevent: message\ndata: ${JSON.stringify(SSE_EVENTS[n - 1])}\n\n`);
        if (n === SSE_EVENTS.length) { clearInterval(timer); res.end(); }
      }, 60);
      return;
    }

    res.writeHead(404); res.end();
  });
});

console.log('三种传输的「信封」对照 · 全部在本机 127.0.0.1 完成，无任何外部请求');
console.log('='.repeat(100));
console.log('【0】先记住一句话：JSON-RPC 是信纸，传输是信封。下面所有请求体，内容和 mcp-session.log 里的是同一类 JSON。');

server.listen(0, '127.0.0.1', async () => {
  const port = server.address().port;
  console.log(`\n本机临时端口: ${port}（只绑 127.0.0.1，符合 MCP 规范对本地 HTTP 的安全要求）`);

  console.log('\n' + '='.repeat(100));
  console.log('【1】HTTP：每条 JSON-RPC 消息 = 一次独立的 POST 往返');
  for (const msg of MESSAGES) await post(port, msg);

  console.log('\n' + '='.repeat(100));
  console.log('【2】SSE：只发一次 GET，服务端在同一条连接上连续推 3 条事件');
  console.log('  请求行     : GET /mcp HTTP/1.1');
  console.log('  Accept     : text/event-stream');
  await sseGet(port);
  console.log('  （客户端若要说话，得另外发 POST —— SSE 是单向：服务器 → 客户端）');

  console.log('\n' + '='.repeat(100));
  console.log('【3】对照结论');
  console.log(`  STDIO : 9 条 JSON-RPC = 0 次网络往返；同一根管道里的 9 行文本，见 mcp-session.log`);
  console.log(`  HTTP  : ${MESSAGES.length} 条 JSON-RPC = ${postCount} 次 POST 往返；每次重带全套 header`);
  console.log(`  SSE   : 1 次 GET 建连 + 同一条连接上推 ${SSE_EVENTS.length} 条事件；请求数不随事件数增长`);
  console.log('  三者信纸完全相同，差别只在「怎么送」：本地管道 / 一问一答 / 挂着的单向流。');
  console.log('='.repeat(100));

  server.close();
});
