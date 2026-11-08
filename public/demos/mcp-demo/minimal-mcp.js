#!/usr/bin/env node
/**
 * 最小 MCP stdio 演示（零依赖，按 MCP 2025-06-18 规范手写，不使用 SDK）
 *
 *   node minimal-mcp.js server   → 作为 MCP server：stdin 收 JSON-RPC，stdout 回 JSON-RPC
 *   node minimal-mcp.js client   → 作为演示用 host：拉起 server 子进程，跑完整会话并打印逐条报文
 *
 * 目的：把 host / client / server 这三个抽象名词变成看得见的进程和报文。
 * 角色对照：
 *   HOST   = WorkBuddy / Claude Desktop / DSH（管模型、UI、权限弹窗、会话）；本脚本的 client 模式模拟它的一小部分
 *   CLIENT = host 内部为「每一个」server 建立的 1:1 连接对象；本脚本 client 模式里的 send()/pending
 *   SERVER = 提供 tools/resources/prompts 的独立进程；本脚本 server 模式
 *
 * 规范要点（2025-06-18 basic/transports#stdio）：
 *   - 消息是单条 JSON-RPC 请求/通知/响应
 *   - 以换行分隔，消息内不得含内嵌换行
 *   - stdout 只走协议消息；日志走 stderr
 */

'use strict';
const { spawn } = require('child_process');
const readline = require('readline');

const PROTOCOL = '2025-06-18';

/* ============================== SERVER ============================== */

// 一个刻意「确定性」的工具：核查 ADaM 数据集必需变量，纯集合运算，不含任何模型推理。
const TOOL = {
  name: 'check_required_vars',
  description:
    'Check whether an ADaM dataset contains all required variables. Returns a deterministic, machine-readable report with the exact list of missing variables.',
  inputSchema: {
    type: 'object',
    properties: {
      dataset: { type: 'string', description: 'Dataset name, e.g. ADSL / ADAE' },
      present_vars: { type: 'array', items: { type: 'string' }, description: 'Variables actually present' },
      required_vars: { type: 'array', items: { type: 'string' }, description: 'Variables required by the spec' },
    },
    required: ['dataset', 'present_vars', 'required_vars'],
  },
};

function runTool(args) {
  const present = new Set(args.present_vars || []);
  const required = args.required_vars || [];
  const missing = required.filter((v) => !present.has(v));
  return {
    dataset: args.dataset,
    checked: required.length,
    missing,
    status: missing.length === 0 ? 'PASS' : 'FAIL',
    engine: 'deterministic-code-v1.0.0', // 同一输入永远同一输出，可复核
  };
}

function ok(id, result) { return { jsonrpc: '2.0', id, result }; }

function handle(msg) {
  switch (msg.method) {
    case 'initialize':
      return ok(msg.id, {
        protocolVersion: PROTOCOL,
        capabilities: { tools: { listChanged: false } },
        serverInfo: { name: 'adam-check-demo', version: '0.1.0' },
        instructions: 'Demo MCP server: one deterministic ADaM variable checker.',
      });

    case 'notifications/initialized':
      return null; // 通知（无 id）按规范不回应

    case 'tools/list':
      return ok(msg.id, { tools: [TOOL] });

    case 'tools/call': {
      const { name, arguments: args } = msg.params;
      if (name !== TOOL.name) {
        return { jsonrpc: '2.0', id: msg.id, error: { code: -32602, message: `Unknown tool: ${name}` } };
      }
      const report = runTool(args);
      return ok(msg.id, {
        content: [{ type: 'text', text: JSON.stringify(report) }],
        isError: report.status === 'FAIL',
      });
    }

    case 'ping':
      return ok(msg.id, {});

    default:
      return { jsonrpc: '2.0', id: msg.id, error: { code: -32601, message: 'Method not found' } };
  }
}

function serve() {
  const rl = readline.createInterface({ input: process.stdin, crlfDelay: Infinity });
  rl.on('line', (line) => {
    if (!line.trim()) return;
    let msg;
    try { msg = JSON.parse(line); } catch (e) {
      process.stdout.write(JSON.stringify({ jsonrpc: '2.0', id: null, error: { code: -32700, message: 'Parse error' } }) + '\n');
      return;
    }
    const res = handle(msg);
    if (res) process.stdout.write(JSON.stringify(res) + '\n'); // 一行一条，不含内嵌换行
  });
  rl.on('close', () => process.exit(0));
}

/* ============================== CLIENT / HOST DEMO ============================== */

function demo() {
  const child = spawn(process.execPath, [__filename, 'server'], {
    stdio: ['pipe', 'pipe', 'inherit'],
  });

  const pending = new Map();
  let buf = '';
  const seq = [];
  let n = 0;
  const log = (dir, label, obj) => {
    n += 1;
    const s = `[${String(n).padStart(2, '0')}] ${dir} ${label}\n     ${JSON.stringify(obj)}`;
    seq.push(s);
    console.log(s);
  };

  child.stdout.on('data', (chunk) => {
    buf += chunk.toString('utf8');
    let i;
    while ((i = buf.indexOf('\n')) >= 0) {
      const line = buf.slice(0, i);
      buf = buf.slice(i + 1);
      if (!line.trim()) continue;
      const msg = JSON.parse(line);
      if (msg.id != null && pending.has(msg.id)) {
        const { resolve, label } = pending.get(msg.id);
        pending.delete(msg.id);
        log('S → C', label, msg);
        resolve(msg);
      }
    }
  });

  function send(method, params, label, notify = false) {
    const msg = { jsonrpc: '2.0', method };
    if (!notify) msg.id = Date.now() % 100000 + Math.floor(Math.random() * 1000);
    if (params !== undefined) msg.params = params;
    log('C → S', label, msg);
    child.stdin.write(JSON.stringify(msg) + '\n');
    if (notify) return Promise.resolve(null);
    return new Promise((resolve) => pending.set(msg.id, { resolve, label: label + ' → 响应' }));
  }

  console.log('MCP stdio 最小会话 · 真实 JSON-RPC 报文（按 2025-06-18 规范手写，零依赖）');
  console.log('HOST = 本脚本 client 模式（模拟 WorkBuddy 的一部分） | CLIENT = 下面的 send()/1:1 连接 | SERVER = 子进程');
  console.log('='.repeat(100));

  (async () => {
    // 阶段 1：初始化 —— 版本与能力协商
    const init = await send('initialize', {
      protocolVersion: PROTOCOL,
      capabilities: {},
      clientInfo: { name: 'workbuddy-demo-host', version: '1.0.0' },
    }, 'initialize（握手：版本 + 能力协商）');
    const negotiated = init.result.protocolVersion;

    // 阶段 2：通知进入操作阶段（无 id，服务端不回）
    await send('notifications/initialized', undefined, 'notifications/initialized（通知，规范上不回应）', true);

    // 阶段 3：发现工具 —— host 把这份 inputSchema 转成模型可见的 tool schema
    const listed = await send('tools/list', {}, 'tools/list（发现能力）');
    const tool = listed.result.tools[0];

    // 阶段 4：模型决定调用 → host 弹权限确认 → client 发出 tools/call
    const args = {
      dataset: 'ADSL',
      present_vars: ['USUBJID', 'AGE', 'SEX', 'RACE'],
      required_vars: ['USUBJID', 'AGE', 'TRT01P', 'TRT01PN'],
    };
    const call1 = await send('tools/call', { name: tool.name, arguments: args }, 'tools/call（执行确定性核查）');
    const call2 = await send('tools/call', { name: tool.name, arguments: args }, 'tools/call（同样输入，再执行一次）');

    const t1 = call1.result.content[0].text;
    const t2 = call2.result.content[0].text;

    console.log('='.repeat(100));
    console.log('会话结论');
    console.log('  协商协议版本          :', negotiated);
    console.log('  发现工具数            :', listed.result.tools.length, '→', tool.name);
    console.log('  工具 inputSchema 字段 :', Object.keys(tool.inputSchema.properties).join(', '));
    console.log('  首次调用结果          :', t1);
    console.log('  两次调用字节级一致    :', t1 === t2 ? '是（确定性执行）' : '否');
    console.log('  报文总数              :', n);
    console.log('='.repeat(100));
    console.log('注意：上面这些报文里没有一条包含模型推理。模型的工作只有两步：');
    console.log('  ① 读 tools/list 的 schema，决定要不要调这个工具、参数填什么；');
    console.log('  ② 读 tools/call 的返回，把它翻译成人话。');
    console.log('真正的协议交互全部由 host 内的 client 与 server 进程完成。');

    child.stdin.end();
    child.kill();
  })().catch((e) => { console.error('DEMO FAILED:', e); child.kill(); process.exitCode = 1; });
}

if (process.argv[2] === 'server') serve();
else if (process.argv[2] === 'client') demo();
else {
  console.log('用法: node minimal-mcp.js server | node minimal-mcp.js client');
}
