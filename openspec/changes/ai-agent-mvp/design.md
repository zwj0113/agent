## Context

当前状态：项目从零开始，需要构建一个完整的 AI Agent 系统。

约束：
- Python 3.10+ 后端 + React/Next.js 前端
- 使用 FastAPI 提供 REST/WebSocket/SSE 接口
- LangChain/LangGraph 作为 Agent 编排引擎
- PostgreSQL + Qdrant 作为数据存储

利益相关方：前端开发者、后端开发者、终端用户、管理员

## Goals / Non-Goals

**Goals:**
- 构建可流式输出的 AI Chat API（SSE 协议）
- 实现 ReAct Agent 引擎，支持工具调用
- 搭建基础前端聊天界面
- 实现工具注册与执行系统
- 具备简单的内存会话记忆

**Non-Goals:**
- 生产级 Docker 沙箱（第一阶段使用简易实现）
- 完整的 Admin 管理后台（后续迭代）
- MCP 完整协议实现（概念验证阶段）
- 向量数据库集成（后续迭代）

## Decisions

### 1. SSE vs WebSocket
**决策**：第一阶段使用 SSE
**理由**：SSE 实现简单，单向流适合当前的流式输出需求。WebSocket 可在需要双向通信时扩展。
**替代方案**：WebSocket — 更复杂但支持双向通信

### 2. ReAct Agent 实现
**决策**：使用 langchain 的 ReAct Agent，结合 ChatOpenAI
**理由**：langchain 已封装完整，切换成本低
**替代方案**：手写 Agent 循环 — 更可控但工作量大

### 3. SSE 事件类型设计
**决策**：定义 `thought`/`call`/`answer` 三种事件
```
event: message
data: {"type":"thought","content":"..."}
event: message
data: {"type":"call","tool":"get_weather","args":{"city":"Beijing"}}
event: message
data: {"type":"answer","content":"..."}
```

### 4. 工具封装标准
**决策**：所有工具继承 `BaseTool`，统一接口
```python
class WeatherTool(BaseTool):
    name: str = "get_weather"
    description: str = "Get weather for a city"
    def _run(self, city: str) -> str: ...
```

### 5. 会话历史存储
**决策**：第一阶段使用 in-memory `ChatMessageHistory`
**理由**：简化 MVP，持久化后续通过 SQLAlchemy 实现

## Risks / Trade-offs

| 风险 | 缓解措施 |
|------|----------|
| LLM 输出不含结构化 thought | Prompt engineering 引导 JSON 格式输出 |
| SSE 连接中断处理 | 添加心跳 + 异常捕获 |
| 工具执行安全 | 第二阶段加入 Docker 沙箱 |
| 前端流式渲染性能 | 使用 React 虚拟列表 |

## Open Questions

1. 记忆系统的向量化何时触发？（每消息/会话结束/手动）
2. MCP Stdio vs SSE 如何选择？
3. 多租户 vs 单租户架构？
4. Token 计费精确度要求？
