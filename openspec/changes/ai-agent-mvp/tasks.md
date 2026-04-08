## 1. 项目初始化

- [x] 1.1 创建 backend/ 和 frontend/ 目录结构
- [x] 1.2 编写 requirements.txt（fastapi, uvicorn, langchain, langchain-openai, sse-starlette）
- [ ] 1.3 初始化 Next.js 项目（npx create-next-app）
- [ ] 1.4 配置 Tailwind CSS

## 2. 后端骨架

- [x] 2.1 实现 FastAPI 主应用（main.py），包含 CORS 配置
- [x] 2.2 实现 GET /api/v1/health 健康检查端点
- [x] 2.3 创建 Tool 基类和 ToolRegistry
- [x] 2.4 实现 calculator 和 get_weather 内置工具

## 3. ReAct Agent 引擎

- [x] 3.1 实现 AsyncCallbackHandler（捕获 thought/call/answer 事件）
- [x] 3.2 创建 ReAct Agent（结合 ChatOpenAI + Tools）
- [x] 3.3 实现 ChatMessageHistory 会话历史管理
- [x] 3.4 实现 /api/v1/chat/stream SSE 端点

## 4. SSE 事件契约

- [x] 4.1 定义 SSE 事件格式（thought/call/answer）
- [x] 4.2 确保 SSE 输出与 api_spec.yaml 一致
- [x] 4.3 处理连接中断（AsyncGenerator cleanup）
- [x] 4.4 添加 CORS 中间件配置

## 5. 前端聊天界面

- [x] 5.1 创建 ChatApp 主组件（布局：消息区 + 输入框）
- [x] 5.2 实现 SSE EventSource 监听逻辑
- [x] 5.3 实现 thought 事件展示（"思考中..."卡片）
- [x] 5.4 实现 call 事件展示（工具调用标签）
- [x] 5.5 实现 answer 打字机效果 + Markdown 渲染
- [x] 5.6 实现思考流折叠/展开 UI

## 6. API 契约文档

- [x] 6.1 编写 api_spec.yaml（OpenAPI 3.0）
- [x] 6.2 定义 POST /api/v1/chat/stream 的 SSE data 结构
- [x] 6.3 定义 GET /api/v1/health 响应格式

## 7. 技能系统（基础）

- [x] 7.1 实现 GET /api/v1/skills 列表端点
- [x] 7.2 实现 POST /api/v1/skills/install 端点
- [x] 7.3 实现 DELETE /api/v1/skills/{name} 端点
- [x] 7.4 技能 JSON 配置解析器（预留接口）

## 8. MCP 集成（预留接口）

- [x] 8.1 定义 MCPClient 类接口
- [x] 8.2 实现 SSE 方式的 MCP 客户端框架
- [x] 8.3 实现 MCP 工具到本地工具的映射（预留）

## 9. 记忆系统（基础）

- [x] 9.1 定义 VectorMemory 接口
- [x] 9.2 实现 ChatMessageHistory 短期记忆
- [ ] 9.3 实现上下文注入逻辑（由 Agent 自动处理）

## 10. Admin 管理后台（基础）

- [x] 10.1 创建 Admin 页面框架
- [x] 10.2 实现模型配置界面
- [x] 10.3 实现技能管理界面
- [x] 10.4 实现 MCP 服务器配置界面
