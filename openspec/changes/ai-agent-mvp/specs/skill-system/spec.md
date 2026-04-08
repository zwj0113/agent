## ADDED Requirements

### Requirement: 技能元数据

技能 SHALL 由 JSON 配置定义，包含：`name`, `description`, `tools`（工具列表）。

### Requirement: 技能列表 API

系统 SHALL 提供 `GET /api/v1/skills` 返回已注册技能列表。

### Requirement: 技能安装/卸载

系统 SHALL 提供 `POST /api/v1/skills/install` 和 `DELETE /api/v1/skills/{name}` 接口。

#### Scenario: 上传新技能
- **WHEN** 管理员上传技能 JSON 配置
- **THEN** 技能被解析并注册到工具注册表

#### Scenario: 卸载技能
- **WHEN** 管理员删除技能
- **THEN** 相关工具从注册表移除
