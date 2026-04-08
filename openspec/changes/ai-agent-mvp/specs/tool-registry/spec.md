## ADDED Requirements

### Requirement: 工具基类

所有工具 SHALL 继承 LangChain 的 `BaseTool`，实现标准接口：
- `name`: 工具唯一名称
- `description`: 工具描述（用于 Agent 理解何时调用）
- `_run()`: 同步执行方法

### Requirement: 工具注册

工具 SHALL 通过 `ToolRegistry` 类统一注册和管理，支持 `registry.register(tool)` 和 `registry.get_tool(name)`。

### Requirement: 工具执行隔离

工具执行 SHALL 捕获 stdout/stderr，并返回结构化结果。

#### Scenario: 注册新工具
- **WHEN** 调用 registry.register(my_tool)
- **THEN** 工具被添加到可用工具列表

#### Scenario: 执行工具
- **WHEN** Agent 调用 tool_name 并传入参数
- **THEN** 工具执行并返回结果
