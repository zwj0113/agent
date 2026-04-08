## ADDED Requirements

### Requirement: 聊天界面布局

前端 SHALL 实现类 Claude.ai 的聊天界面，包含：
- 消息历史区域（左侧或主区域）
- 底部输入框
- 响应式设计

### Requirement: Markdown 支持

消息 SHALL 支持 Markdown 渲染，包括代码块。

### Requirement: SSE 事件处理

前端 SHALL 使用 EventSource 或 fetch 监听 `/api/v1/chat/stream`，处理三类事件：
- `thought`：显示"思考中..."半透明卡片
- `call`：显示"正在调用工具 [名称]"标签
- `answer`：使用打字机效果实时渲染

### Requirement: 思考流展示

回复过程中 SHALL 有可折叠/展开的 UI 显示"思考流"和"工具调用流"。

#### Scenario: 发送消息并接收流
- **WHEN** 用户发送消息
- **THEN** 界面实时显示 thought/call/answer 事件

#### Scenario: Markdown 渲染
- **WHEN** 收到包含代码的消息
- **THEN** 代码块被正确语法高亮显示
