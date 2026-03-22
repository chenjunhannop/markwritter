# LiteLLM 集成实施计划（修订版）

## 需求规格

| 配置项 | 要求 |
|--------|------|
| 默认模型 | qwen3.5-plus |
| 缓存方式 | 内存缓存 (in-memory) |
| 配置方式 | YAML 配置文件 |
| 步骤粒度 | 更细化的执行步骤 |

---

## Phase 1: 基础依赖与配置 (2小时)

### Step 1.1: 添加依赖
**文件**: `pyproject.toml`
```
[project]
dependencies = [
    "typer>=0.9.0",
    "pydantic>=2.0.0",
    "pyyaml>=6.0",
    "litellm>=1.0.0",  # 新增
]
```

### Step 1.2: 创建配置模型
**文件**: `markwritter/models.py` (新增)
- `class LLMConfig(BaseModel)` - LLM 配置模型
- `class CacheConfig(BaseModel)` - 缓存配置模型
- `class GlobalConfig(BaseModel)` - 全局配置根模型

### Step 1.3: 创建配置文件
**文件**: `config.yaml` (新建)
```yaml
llm:
  default_model: "qwen/qwen3.5-plus"
  timeout: 30
  max_retries: 2

cache:
  enabled: true
  ttl_seconds: 3600
  max_size: 1000
```

### Step 1.4: 实现配置加载器
**文件**: `markwritter/config.py` (新建)
- `load_config()` - 加载 YAML 配置
- `get_config()` - 获取全局配置单例
- `ConfigError` - 配置错误异常

---

## Phase 2: LLM 客户端实现 (3小时)

### Step 2.1: 创建内存缓存
**文件**: `markwritter/llm_client.py` (部分)
```python
class MemoryCache:
    """Simple in-memory cache with TTL"""
    def __init__(self, max_size: int, ttl_seconds: int)
    def get(self, key: str) -> Optional[str]
    def set(self, key: str, value: str)
    def _cleanup_expired()
```

### Step 2.2: 创建 LLM 客户端核心
**文件**: `markwritter/llm_client.py` (部分)
```python
class LLMClient:
    """LiteLLM wrapper with caching and error handling"""
    def __init__(self, config: LLMConfig, cache: Optional[MemoryCache])
    async def complete(self, prompt: str, model: Optional[str]) -> str
    def complete_sync(self, prompt: str, model: Optional[str]) -> str
    def _generate_cache_key(prompt: str, model: str) -> str
```

### Step 2.3: 实现错误处理与重试
**文件**: `markwritter/llm_client.py` (部分)
- `LLMError` / `LLMTimeoutError` / `LLMRateLimitError`
- 指数退避重试逻辑
- 优雅降级处理

### Step 2.4: 创建客户端工厂
**文件**: `markwritter/llm_client.py` (部分)
- `create_llm_client()` - 从配置创建客户端实例
- 支持环境变量 API key 注入

---

## Phase 3: Prompt 模板设计 (2小时)

### Step 3.1: 设计 Skill 选择 Prompt
**文件**: `markwritter/parser.py` (部分)
```python
SKILL_SELECTION_PROMPT = """
You are an intent parser for a skill-based AI framework.

Available skills:
{skill_descriptions}

User input: {user_input}

Analyze the user's intent and select the best matching skill.
Respond in JSON format:
{
  "skill_name": "<selected_skill_name>",
  "confidence": 0.0-1.0,
  "reasoning": "<why this skill>",
  "extracted_params": {"param_name": "value"}
}
"""
```

### Step 3.2: 实现 Prompt 渲染器
**文件**: `markwritter/parser.py` (部分)
- `render_skill_selection_prompt(skills, user_input)` - 渲染选择 prompt
- `render_param_extraction_prompt(skill, user_input)` - 渲染参数提取 prompt

### Step 3.3: 创建响应模型
**文件**: `markwritter/models.py` (新增)
```python
class LLMIntentResponse(BaseModel):
    skill_name: str
    confidence: float
    reasoning: str
    extracted_params: dict[str, Any]
```

---

## Phase 4: Parser 重构 (3小时)

### Step 4.1: 提取关键词解析器
**文件**: `markwritter/parser.py` (重构)
```python
class KeywordParser:
    """Original keyword-based parser as fallback"""
    def parse(self, user_input: str, skills: list[SkillDefinition]) -> ParseIntent
    def _extract_params_from_input(...) -> dict
```

### Step 4.2: 实现 LLM 解析器
**文件**: `markwritter/parser.py` (新增)
```python
class LLMParser:
    """LLM-based intent parser"""
    def __init__(self, llm_client: LLMClient, confidence_threshold: float = 0.7)
    async def parse(self, user_input: str, skills: list[SkillDefinition]) -> ParseIntent
    def _parse_llm_response(self, response: str) -> LLMIntentResponse
```

### Step 4.3: 实现混合解析器
**文件**: `markwritter/parser.py` (重构)
```python
class InputParser:
    """Hybrid parser: LLM primary, keyword fallback"""
    def __init__(self, llm_parser: LLMParser, keyword_parser: KeywordParser)
    async def parse(self, user_input: str, skills: list[SkillDefinition]) -> ParseIntent
    def parse_sync(self, user_input: str, skills: list[SkillDefinition]) -> ParseIntent
```

### Step 4.4: 添加置信度阈值处理
**文件**: `markwritter/parser.py` (部分)
- 低于阈值时使用关键词回退
- 记录 LLM 解析与关键词解析的差异

---

## Phase 5: 框架集成 (2小时)

### Step 5.1: 修改 Framework 初始化
**文件**: `markwritter/core.py` (修改)
- 注入 LLMClient 到 Framework
- 根据配置选择解析器模式

### Step 5.2: 实现异步流程支持
**文件**: `markwritter/core.py` (修改)
- `async def process_input_async()` - 异步处理
- 保持 `process_input()` 同步兼容

### Step 5.3: 更新 CLI 入口
**文件**: `markwritter/cli.py` (修改)
- 配置加载初始化
- 支持 `--config` 参数指定配置文件

### Step 5.4: 环境变量支持
**文件**: `markwritter/config.py` (部分)
- `MARKWRITTER_CONFIG_PATH` - 配置文件路径
- `DASHSCOPE_API_KEY` - Qwen API key

---

## Phase 6: 测试与验证 (2小时)

### Step 6.1: LLM 客户端单元测试
**文件**: `tests/test_llm_client.py` (新建)
- Mock LiteLLM 调用
- 缓存命中/未命中测试
- 错误重试测试

### Step 6.2: Parser 集成测试
**文件**: `tests/test_parser.py` (修改)
- LLM 解析器测试
- 混合策略测试
- 回退逻辑测试

### Step 6.3: 配置加载测试
**文件**: `tests/test_config.py` (新建)
- YAML 解析测试
- 环境变量覆盖测试
- 配置验证测试

### Step 6.4: 端到端测试
**文件**: `tests/test_integration.py` (新建)
- 完整流程: 输入 → LLM 解析 → Skill 执行

---

## 文件变更清单

| 文件 | 操作 | 说明 |
|------|------|------|
| `pyproject.toml` | 修改 | 添加 litellm 依赖 |
| `config.yaml` | 新建 | 框架配置文件 |
| `markwritter/models.py` | 修改 | 添加配置和 LLM 响应模型 |
| `markwritter/config.py` | 新建 | 配置加载器 |
| `markwritter/llm_client.py` | 新建 | LLM 客户端 + 内存缓存 |
| `markwritter/parser.py` | 重构 | 混合解析策略 |
| `markwritter/core.py` | 修改 | 集成 LLM 客户端 |
| `markwritter/cli.py` | 修改 | 配置初始化 |
| `tests/test_llm_client.py` | 新建 | LLM 客户端测试 |
| `tests/test_config.py` | 新建 | 配置测试 |
| `tests/test_parser.py` | 修改 | 扩展解析器测试 |
| `tests/test_integration.py` | 新建 | 端到端测试 |

**总计**: 6 个阶段, 23 个步骤, 14 个文件, ~14 小时

---

## 配置示例

### config.yaml
```yaml
llm:
  default_model: "qwen/qwen3.5-plus"
  timeout: 30
  max_retries: 2
  temperature: 0.1

cache:
  enabled: true
  ttl_seconds: 3600
  max_size: 1000

parser:
  confidence_threshold: 0.7
  use_llm: true
```

### 环境变量
```bash
export DASHSCOPE_API_KEY="your-qwen-api-key"
export MARKWRITTER_CONFIG_PATH="./config.yaml"
```
