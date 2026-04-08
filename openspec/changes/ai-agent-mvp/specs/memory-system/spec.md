## ADDED Requirements

### Requirement: 短期会话记忆

系统 SHALL 使用 `ChatMessageHistory` 在内存中存储当前会话的消息历史。

### Requirement: 记忆注入

每轮对话 SHALL 将历史消息作为上下文传递给 Agent。

### Requirement: 向量数据库接口（预留）

系统 SHALL 定义 `VectorMemory` 接口，支持后续集成 Qdrant/Milvus。

#### Scenario: 记忆保存
- **WHEN** 用户发送消息
- **THEN** 消息被保存到会话历史

#### Scenario: 记忆检索
- **WHEN** Agent 需要上下文
- **THEN** 历史消息被注入到 prompt
