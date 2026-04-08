## ADDED Requirements

### Requirement: ReAct Agent 核心

系统 SHALL 使用 LangChain 的 ReAct Agent 架构，结合 ChatOpenAI 实现。

### Requirement: AsyncCallbackHandler

系统 SHALL 实现自定义 `AsyncCallbackHandler`，捕获：
- LLM 新 token（用于 thought 事件）
- 工具开始执行（用于 call 事件）
- LLM 最终输出（用于 answer 事件）

### Requirement: 内置工具

Agent SHALL 至少内置以下工具之一用于演示：
- `calculator`：简单数学计算
- `get_weather`：获取城市天气（模拟数据）

### Requirement: 会话历史

系统 SHALL 使用 LangChain 的 `ChatMessageHistory` 在内存中存储会话历史。

#### Scenario: Agent 处理用户问题
- **WHEN** 用户发送 "What's 2+2?"
- **THEN** Agent 调用 calculator 工具，返回 "4"

#### Scenario: Agent 无法回答
- **WHEN** 用户发送超出能力的问题
- **THEN** Agent 返回友好的不知道回答
