## ADDED Requirements

### Requirement: 模型管理

管理员 SHALL 能配置多模型 API Key，设置默认模型。

### Requirement: 技能管理

管理员 SHALL 能查看技能列表、上传、启用/禁用、卸载技能。

### Requirement: MCP 管理

管理员 SHALL 能添加/移除 MCP 服务器连接。

### Requirement: 用户管理

系统 SHALL 提供基础的用户 CRUD 功能。

### Requirement: Token 消耗看板

管理员 SHALL 能查看 Token 使用统计。

#### Scenario: 配置默认模型
- **WHEN** 管理员设置默认模型
- **THEN** 新会话使用该模型

#### Scenario: 查看 Token 消耗
- **WHEN** 管理员访问看板
- **THEN** 显示各用户/会话的 Token 消耗
