# 实施计划: 后端代码质量修复

> 创建日期: 2026-03-25
> 状态: 待确认

## 概述

本计划旨在解决后端代码审查中发现的架构、规范和代码质量问题。修复分为 4 个阶段，优先处理高严重程度问题，确保向后兼容性和增量可交付性。

## 需求

- 修复 RESTful API 规范违规
- 消除代码重复（异常类、模型定义）
- 集成 ProviderRegistry 到 LLMClient
- 统一 API 版本前缀
- 完善服务层架构
- 清理未使用的依赖和代码
- 改进全局状态管理以便于测试

## 架构变更

| 文件 | 变更描述 |
|------|----------|
| `markwritter/exceptions.py` | 新增：集中定义所有自定义异常类 |
| `markwritter/query/models.py` | 新增：查询相关的数据模型 |
| `markwritter/api/services/` | 扩展：添加 NoteService, LLMService |
| `markwritter/api/routes/record.py` | 重构：RESTful 端点 + 依赖注入 |
| `markwritter/api/routes/__init__.py` | 更新：导出所有路由模块 |
| `markwritter/llm_client.py` | 增强：ProviderRegistry 集成初始化 |
| `markwritter/provider_registry.py` | 修复：移除空 TYPE_CHECKING 块 |
| `pyproject.toml` | 清理：移除未使用依赖 |

---

## 阶段 1: 核心基础修复 (高优先级)

**目标**: 解决代码重复和依赖问题，建立统一基础

### 1.1 创建统一异常模块

- **文件**: `markwritter/exceptions.py`
- **操作**: 创建新文件，集中定义所有自定义异常
- **内容**:
  ```python
  class MarkwritterError(Exception):
      """Base exception for all Markwritter errors."""
      pass

  class VaultError(MarkwritterError):
      """Base exception for vault operations."""
      pass

  class InvalidVaultError(VaultError):
      """Raised when vault path is invalid."""
      pass

  class NoteNotFoundError(VaultError):
      """Raised when a note cannot be found."""
      pass

  class NodeNotFoundError(MarkwritterError):
      """Raised when a graph node cannot be found."""
      pass

  class LLMError(MarkwritterError):
      """LLM API error."""
      pass
  ```
- **风险**: 低

### 1.2 更新异常导入

- **文件**: `markwritter/explore/graph.py`, `markwritter/obsidian/vault.py`
- **操作**: 删除重复定义，从 `exceptions.py` 导入
- **风险**: 低

### 1.3 统一 SearchResult 模型

- **文件**: 创建 `markwritter/query/models.py`
- **操作**: 将 `SearchResult`, `HighlightResult` 等模型集中定义
- **更新**: `markwritter/query/search.py`, `markwritter/api/routes/search.py`
- **风险**: 低

### 1.4 清理未使用依赖

- **文件**: `pyproject.toml`
- **操作**: 移除 `python-frontmatter` 和 `watchdog`
- **风险**: 低

---

## 阶段 2: API 规范化 (高优先级)

**目标**: 修复 RESTful 规范违规，统一 API 版本前缀

### 2.1 RESTful 端点重构

- **文件**: `markwritter/api/routes/record.py`
- **变更**:

| 原端点 | 新端点 |
|--------|--------|
| POST /create | POST /notes |
| PUT /update | PUT /notes/{note_path} |

- **向后兼容**: 添加废弃警告的旧端点别名
- **风险**: 中 - 需前端配合

### 2.2 统一 API 版本前缀

- **文件**: `markwritter/api/app.py`
- **操作**: 为 skills, chat, logs 路由添加 `/api/v1` 前缀
- **风险**: 中

### 2.3 完善路由导出

- **文件**: `markwritter/api/routes/__init__.py`
- **操作**: 添加 `query`, `record`, `explore` 导出
- **风险**: 低

---

## 阶段 3: 架构改进 (中优先级)

**目标**: 集成 ProviderRegistry，完善服务层，改进状态管理

### 3.1 ProviderRegistry 集成

- **文件**: `markwritter/llm_client.py`
- **操作**: 在 `__init__` 中自动创建 ProviderRegistry
- **风险**: 低

### 3.2 修复空 TYPE_CHECKING 块

- **文件**: `markwritter/provider_registry.py`
- **操作**: 删除或填充 TYPE_CHECKING 块
- **风险**: 低

### 3.3 创建服务层

- **新建**: `markwritter/api/services/note_service.py`
- **新建**: `markwritter/api/services/llm_service.py`
- **风险**: 中

### 3.4 依赖注入替代全局状态

- **文件**: `markwritter/api/routes/record.py`
- **操作**: 使用 FastAPI `Depends()` 替代全局变量
- **风险**: 中

### 3.5 修复同步/异步混用

- **文件**: `markwritter/executor.py`
- **操作**: 添加警告或使用 `nest_asyncio`
- **风险**: 中

---

## 阶段 4: 代码清理 (低优先级)

**目标**: 清理未使用代码，完善文档

### 4.1 处理未使用的 SkillRunRequest

- **文件**: `markwritter/api/models/skill.py`
- **操作**: 验证并决定使用或删除

### 4.2 完善占位符实现

- **文件**: `markwritter/api/routes/notes.py`, `markwritter/api/routes/search.py`
- **操作**: 集成服务层实现真实功能

### 4.3 评估 framework_bridge 必要性

- **文件**: `markwritter/api/services/framework_bridge.py`
- **操作**: 评估是否合并到其他服务

---

## 测试策略

### 单元测试

| 模块 | 测试文件 |
|------|----------|
| exceptions | `tests/test_exceptions.py` |
| NoteService | `tests/api/services/test_note_service.py` |
| LLMService | `tests/api/services/test_llm_service.py` |
| RESTful 端点 | `tests/api/routes/test_record.py` |

### 集成测试

| 场景 | 测试文件 |
|------|----------|
| API 版本一致性 | `tests/api/test_api_versioning.py` |
| 依赖注入 | `tests/api/test_dependency_injection.py` |
| ProviderRegistry | `tests/test_provider_registry_integration.py` |

---

## 风险与缓解措施

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| RESTful 端点变更导致前端调用失败 | 高 | 提供废弃端点别名 + 迁移指南 |
| API 版本前缀变更影响现有客户端 | 中 | 支持双路径过渡期 |
| 服务层重构引入回归 | 中 | 完善单元测试 + 分阶段迁移 |
| asyncio.run() 在异步上下文失败 | 中 | 添加运行时检测 |

---

## 成功标准

- [ ] 所有自定义异常定义在 `exceptions.py` 中
- [ ] 无重复的类定义
- [ ] `pyproject.toml` 中无未使用的依赖
- [ ] 所有 API 端点符合 RESTful 规范
- [ ] 所有 API 端点使用统一的 `/api/v1` 前缀
- [ ] `ProviderRegistry` 已集成到 `LLMClient`
- [ ] 服务层包含 `NoteService` 和 `LLMService`
- [ ] 测试覆盖率 > 80%

---

## 预估复杂度

| 阶段 | 文件数 | 预估工时 | 复杂度 |
|------|--------|----------|--------|
| 阶段 1 | 5 | 4-6 小时 | 低 |
| 阶段 2 | 3 | 3-4 小时 | 中 |
| 阶段 3 | 5 | 8-12 小时 | 高 |
| 阶段 4 | 3 | 4-6 小时 | 中 |

**总计**: 约 19-28 小时，建议分 3-4 个迭代完成

---

## 实施顺序建议

1. **迭代 1**: 阶段 1（基础修复，无破坏性变更）
2. **迭代 2**: 阶段 2 + 阶段 3.1-3.2（API 规范化 + Registry 集成）
3. **迭代 3**: 阶段 3.3-3.5（服务层 + 依赖注入）
4. **迭代 4**: 阶段 4（代码清理 + 测试补充）