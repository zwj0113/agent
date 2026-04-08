## Why

企业需要构建一个通用的 AI Agent 系统，能够像 Claude Code 一样实时展示 AI 的思考与执行过程，支持流式输出、动态工具扩展和长期记忆。当前缺乏开源、可定制的解决方案来满足这类需求。

## What Changes

- **AI Agent 核心引擎**：基于 LangChain/LangGraph 的 ReAct Agent，支持流式 SSE 输出（thought/call/answer 三种事件类型）
- **工具系统**：内置 Bash（Docker 沙箱）、Python REPL、网页搜索工具，支持动态注册和调用
- **技能系统**：支持用户通过 Admin 页面上传、安装、卸载自定义技能（Python 脚本或 JSON 配置）
- **MCP 支持**：符合 Model Context Protocol 标准的服务器连接（SSE/Stdio 通信）
- **记忆系统**：会话级短期记忆（in-memory）+ 向量化长期记忆（Qdrant/Milvus）
- **前端界面**：类 Claude.ai 的聊天界面，支持 Markdown，实时展示思考流和工具调用流
- **管理后台**：模型管理、技能管理、MCP 管理、用户管理、Token 消耗看板

## Capabilities

### New Capabilities

- `流式-chat-api`：SSE 流式聊天接口，定义 thought/call/answer 事件契约
- `react-agent-engine`：基于 LangChain 的 ReAct Agent 核心引擎
- `tool-registry`：动态工具注册与执行系统
- `skill-system`：自定义技能的上传、安装、卸载管理
- `mcp-integration`：MCP 协议客户端，支持连接外部 MCP 服务器
- `memory-system`：短期会话记忆 + 向量长期记忆系统
- `chat-frontend`：Next.js 实现的聊天界面
- `admin-dashboard`：管理员控制台

### Modified Capabilities

- （无）

## Impact

- **后端**：FastAPI + LangChain，新增 SSE 流式端点、工具执行沙箱、向量数据库集成
- **前端**：Next.js + Tailwind CSS，新增聊天界面组件、Admin 页面
- **数据库**：PostgreSQL（关系型元数据）+ Qdrant（向量记忆）
- **依赖**：langchain、langchain-openai、fastapi、sqlalchemy、qdrant-client
