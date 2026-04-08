## ADDED Requirements

### Requirement: SSE 流式聊天端点

系统 SHALL 提供 `POST /api/v1/chat/stream` 端点，接收 JSON body `{"message": "...", "session_id": "..."}` 并返回 Server-Sent Events 流。

### Requirement: SSE 事件类型

流 SHALL 包含以下三种事件类型：

- `thought`：Agent 思考过程，格式 `{"type": "thought", "content": "..."}`
- `call`：工具调用，格式 `{"type": "call", "tool": "tool_name", "args": {...}}`
- `answer`：最终文本回答，格式 `{"type": "answer", "content": "..."}`

### Requirement: 健康检查端点

系统 SHALL 提供 `GET /api/v1/health` 端点，返回 JSON `{"status": "ok"}`。

### Requirement: CORS 支持

API SHALL 配置 CORS，允许前端（默认 `http://localhost:3000`）跨域访问。

### Requirement: 连接中断处理

当客户端断开连接时，服务器 SHALL 正确终止 SSE 流，不抛出未处理异常。

#### Scenario: 正常聊天请求
- **WHEN** 用户发送 POST /api/v1/chat/stream
- **THEN** 服务器返回 SSE 流，包含 thought/call/answer 事件

#### Scenario: 健康检查
- **WHEN** 客户端 GET /api/v1/health
- **THEN** 返回 200 和 {"status": "ok"}

#### Scenario: 客户端提前断开
- **WHEN** 客户端在 SSE 流进行中断开
- **THEN** 服务器正确清理资源，不报错
