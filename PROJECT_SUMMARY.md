# AI Agent 项目总结

## 项目概述

一个类似 Claude Code 的通用 AI Agent 系统，能够实时展示 AI 的思考与执行过程，支持流式输出、动态工具扩展和会话记忆。

---

## 1. 已实现的具体功能

### 1.1 后端功能

| 功能 | 状态 | 说明 |
|------|------|------|
| FastAPI 主应用 | ✅ | CORS 配置、健康检查端点 |
| SSE 流式聊天接口 | ✅ | `/api/v1/chat/stream` 端点 |
| ReAct Agent 引擎 | ✅ | 基于 MiniMax API 的 ReAct 循环 |
| 工具注册系统 | ✅ | `ToolRegistry` 动态工具管理 |
| 内置工具 | ✅ | Calculator、Weather、DiskUsage、Bash |
| 聊天会话记忆 | ✅ | `ChatSession` 会话历史管理 |
| 技能系统 API | ✅ | GET/POST/DELETE `/api/v1/skills` |
| MCP 客户端框架 | ✅ | 预留接口 |
| 向量记忆接口 | ✅ | 预留 `VectorMemory` 接口 |

### 1.2 前端功能

| 功能 | 状态 | 说明 |
|------|------|------|
| 聊天界面 | ✅ | `ChatApp` 主组件 |
| SSE EventSource 监听 | ✅ | 实时接收流式事件 |
| 思考内容展示 | ✅ | 💭 标签显示推理过程 |
| 工具调用展示 | ✅ | 🔧 标签显示工具调用 |
| Markdown 渲染 | ✅ | `react-markdown` + `remark-gfm` |
| 流式打字效果 | ✅ | 实时显示 AI 输出 |
| Admin 管理后台 | ✅ | 模型配置、技能管理页面 |

---

## 2. 各功能具体实现方式

### 2.1 ReAct Agent 引擎

**文件**: `backend/agents/react.py`

**核心实现**:
```
while iteration < max_iterations:
    1. 调用 LLM (MiniMax API) 获取响应
    2. 提取思考内容 (thought) - Action: 之前的推理
    3. 解析 Action/Action Input 格式
    4. 执行工具调用 (tool.invoke)
    5. 将工具结果反馈给 LLM 继续推理
    6. 无 Action 时返回最终答案 (answer)
```

**关键类**:
- `ReActAgent`: 主 Agent 类，支持 `invoke()` 和 `invoke_streaming()`
- `AgentCallbacks`: 线程安全的事件收集器
- `_call_llm_streaming()`: 流式调用 MiniMax API

**流式处理**:
```python
for chunk in self._call_llm_streaming(messages):
    full_content += chunk
    # 实时检测 Action: 块并提取思考内容
    if not found_action:
        action_match = re.search(r'Action:\s*(\w+)', full_content, re.IGNORECASE)
        if action_match:
            thought_part = full_content[:action_match.start()].strip()
            yield {"type": "thought", "content": thought_part}
```

### 2.2 SSE 流式输出

**文件**: `backend/main.py`

**端点**: `POST /api/v1/chat/stream`

**事件类型**:
```json
{"type": "thought", "content": "推理内容..."}
{"type": "call", "tool": "bash", "args": {"input": "echo hello"}, "result": "hello"}
{"type": "answer", "content": "最终答案..."}
{"type": "error", "content": "错误信息"}
```

**实现方式**:
- 使用 `EventSourceResponse` 实现 SSE
- 后台线程运行 Agent，避免阻塞
- `queue.Queue` 在线程间传递事件
- 前端 `EventSource` 监听并实时渲染

### 2.3 工具系统

**文件**: `backend/tools/`

| 工具 | 类 | 功能 |
|------|-----|------|
| Calculator | `CalculatorTool` | 数学表达式计算 |
| Weather | `WeatherTool` | 模拟天气查询 |
| DiskUsage | `DiskUsageTool` | 磁盘使用查询 |
| Bash | `BashTool` | Shell 命令执行 |

**工具调用格式** (Agent 输出):
```
Action: tool_name
Action Input: the_input_value
```

### 2.4 前端聊天界面

**文件**: `frontend/components/ChatApp.tsx`

**状态管理**:
```typescript
const [messages, setMessages] = useState<Message[]>([])
const [isStreaming, setIsStreaming] = useState(false)
const [currentEvents, setCurrentEvents] = useState<StreamEvent[]>([])
```

**SSE 监听**:
```typescript
const response = await fetch('http://localhost:8000/api/v1/chat/stream', {
    method: 'POST',
    body: JSON.stringify({ message: input, session_id: sessionId })
})
const reader = response.body?.getReader()
// 处理流式数据...
```

---

## 3. 实现过程中遇到的问题及优化

### 3.1 聊天历史上下文丢失

**问题**: 用户发送新消息时，Agent 无法记住之前的对话内容

**原因**: `get_messages_for_context()` 方法存在但未传递给 Agent

**解决**: 在 `main.py` 中调用 `chat_session.get_messages_for_context()` 并传给 Agent

### 3.2 工具执行后 LLM 停止推理

**问题**: Agent 执行一个工具后不再继续调用 LLM

**原因**: 系统提示词不够明确，LLM 不知道工具执行后要继续

**解决**: 修改提示词，增加 "After getting the tool result, CONTINUE your reasoning" 规则

### 3.3 思考内容不显示

**问题**: 前端只显示工具调用，不显示 LLM 的思考推理过程

**原因**: `_extract_thought()` 方法只提取 Action: 之前的原始文本，包含 `<think>...</think>` 标签

**解决**:
1. 新增 `clean_thinking_tags()` 函数移除 `<think>...</think>` 标签
2. 在 `invoke_streaming()` 中提取思考内容并单独发送 `thought` 事件

### 3.4 最终答案包含 <think> 标签

**问题**: 返回的 answer 内容中仍然包含 `<think>...</think>` 标签

**解决**: 在生成 answer 事件前调用 `clean_thinking_tags()` 清理内容

### 3.5 思考内容提取不完整

**问题**: 当 LLM 返回多个工具调用时，只有第一个的思考内容被正确提取

**原因**: 流式处理中，找到 Action: 块后立即设置 `found_action = True`，后续内容不再检查

**解决**: 重新设计流式处理逻辑，每个 LLM 响应独立处理thought提取

### 3.6 文件编码问题

**问题**: 编辑器处理中文注释时导致 `<think>` 标签被错误解析

**解决**: 使用 Python 脚本直接写入文件，避免编辑器编码问题

### 3.7 MiniMax API 流式响应处理

**问题**: 流式 API 返回的 SSE 格式解析

**解决**: 处理 `data: [DONE]` 终止标记，正确解析 `delta.content` 字段

---

## 4. 未实现的功能

| 功能 | 优先级 | 说明 |
|------|--------|------|
| Next.js 项目初始化 | 中 | 需要手动 `npx create-next-app` |
| Tailwind CSS 配置 | 中 | 需要手动配置 |
| 上下文注入逻辑 | 中 | 由 Agent 自动处理（已部分实现） |
| 向量长期记忆 | 低 | 预留接口，需要 Qdrant/Milvus |
| 真实天气 API | 低 | 当前为模拟数据 |
| Docker 沙箱执行 | 低 | BashTool 目前直接执行命令 |

---

## 5. 需要优化的功能

### 5.1 前端流式渲染

**当前**: 事件累积后批量更新 UI

**问题**: 与后端流式输出不同步

**优化方向**: 使用 `fetch` + `ReadableStream` 实现真正的实时渲染

### 5.2 思考内容显示优化

**当前**: 思考内容可能只显示 markdown 代码块标记 "```"

**原因**: LLM 格式化为 `thought\n\`\`\`\nAction:...`

**优化方向**: 清理思考内容中的 markdown 格式标记

### 5.3 多工具调用场景

**当前**: 多个连续工具调用时，thought 事件可能丢失

**优化方向**: 确保每个 LLM 响应周期都有正确的 thought 事件

### 5.4 错误处理

**当前**: API 超时或错误时返回通用错误信息

**优化方向**: 细化错误类型，提供更友好的错误提示

### 5.5 会话持久化

**当前**: 会话数据存储在内存中，服务器重启丢失

**优化方向**: 接入数据库持久化存储

---

## 6. 项目总体架构

### 6.1 技术栈

| 层级 | 技术 | 说明 |
|------|------|------|
| 后端框架 | FastAPI | ASGI 接口 |
| LLM | MiniMax-M2.7 | OpenAI 兼容 API |
| 工具框架 | LangChain | BaseTool 抽象 |
| 流式通信 | SSE (sse-starlette) | 服务端推送 |
| 前端框架 | Next.js 14 | React 18 |
| 样式 | Tailwind CSS | 原子化 CSS |
| Markdown | react-markdown | 渲染支持 |

### 6.2 目录结构

```
D:/Desktop/me/agent/
├── backend/
│   ├── main.py                    # FastAPI 主应用
│   ├── agents/
│   │   └── react.py               # ReAct Agent 引擎
│   ├── tools/
│   │   ├── registry.py            # 工具注册表
│   │   ├── builtin.py             # 内置工具 (Calculator, Weather, DiskUsage)
│   │   └── shell.py               # BashTool
│   ├── memory/
│   │   ├── history.py             # ChatSession 会话管理
│   │   └── vector.py              # 向量记忆接口
│   ├── api/
│   │   └── __init__.py
│   ├── mcp/
│   │   └── client.py              # MCP 客户端框架
│   ├── requirements.txt
│   ├── .env
│   └── server.log
├── frontend/
│   ├── app/
│   │   ├── layout.tsx             # 根布局
│   │   ├── page.tsx                # 首页
│   │   ├── globals.css             # 全局样式
│   │   └── admin/
│   │       └── page.tsx            # 管理后台
│   ├── components/
│   │   └── ChatApp.tsx             # 聊天主组件
│   ├── package.json
│   ├── tailwind.config.js
│   ├── tsconfig.json
│   └── next.config.js
├── openspec/
│   └── changes/
│       └── ai-agent-mvp/          # OpenSpec 提案
│           ├── proposal.md
│           ├── design.md
│           ├── tasks.md
│           └── specs/
│               ├── 流式-chat-api/
│               ├── react-agent-engine/
│               ├── tool-registry/
│               ├── skill-system/
│               ├── mcp-integration/
│               ├── memory-system/
│               ├── chat-frontend/
│               └── admin-dashboard/
├── CLAUDE.md                      # Claude Code 项目指令
├── 需求.txt
└── 步骤.txt
```

### 6.3 API 端点

| 端点 | 方法 | 功能 |
|------|------|------|
| `/api/v1/health` | GET | 健康检查 |
| `/api/v1/chat/stream` | POST | SSE 流式聊天 |
| `/api/v1/skills` | GET | 列出可用技能 |
| `/api/v1/skills/install` | POST | 安装技能 |
| `/api/v1/skills/{name}` | DELETE | 卸载技能 |

### 6.4 数据流

```
用户输入
    ↓
Frontend (ChatApp.tsx)
    ↓ HTTP POST + SSE
Backend (main.py)
    ↓
ReAct Agent (agents/react.py)
    ↓ 循环调用
MiniMax API ←→ 工具执行
    ↓
事件收集 (AgentCallbacks)
    ↓ SSE stream
Frontend
    ↓
实时渲染 (💭 思考 / 🔧 工具 / 答案)
```

---

## 7. 配置信息

### 7.1 环境变量 (`backend/.env`)

```bash
MINIMAX_API_KEY=sk-cp-...     # MiniMax API 密钥
MINIMAX_BASE_URL=https://api.minimaxi.com
MINIMAX_MODEL=MiniMax-M2.7
```

### 7.2 启动命令

**后端**:
```bash
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000
```

**前端**:
```bash
cd frontend
npm run dev
```

---

## 8. 下一步计划

1. **完善前端流式渲染** - 实现真正的实时 UI 更新
2. **优化思考内容提取** - 清理 markdown 格式，完整显示推理过程
3. **添加数据库持久化** - PostgreSQL 存储会话历史
4. **实现真实工具** - 搜索、文件操作、代码执行等
5. **MCP 协议集成** - 连接外部 MCP 服务器
6. **向量记忆系统** - 接入 Qdrant 实现长期记忆
