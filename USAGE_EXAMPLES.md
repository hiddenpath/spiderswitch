# Spiderswitch MCP Server - 使用示例

 spiderswitch MCP 服务器现在支持 `require_api_key` 参数，可以只列出本地有 API key 的提供商的大模型。

## 新功能：过滤无 API key 的模型

`list_models` 工具新增了 `require_api_key` 参数：

### 参数说明

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `filter_provider` | string | null | 按 provider 过滤（如 'openai', 'anthropic'） |
| `filter_capability` | string | null | 按能力过滤（'streaming', 'tools', 'vision', 'embeddings', 'audio'） |
| `require_api_key` | boolean | false | **新增**：如果为 true，只返回已配置 API key 的 provider 的模型 |

### 使用示例

#### 示例 1：列出所有模型
```python
await mcp_client.call_tool("list_models", {})
```

#### 示例 2：只列出有 API key 的模型
```python
await mcp_client.call_tool("list_models", {"require_api_key": True})
```

#### 示例 3：组合过滤
```python
await mcp_client.call_tool(
    "list_models",
    {
        "filter_provider": "openai",
        "filter_capability": "vision",
        "require_api_key": True
    }
)
```

### 返回结果说明

```json
{
  "count": 3,
  "models": [...],
  "filtered": {
    "require_api_key": true,
    "provider": "openai",
    "capability": "vision"
  }
}
```

- `count`: 过滤后的模型数量
- `models`: 模型列表，每个模型包含 `api_key_status` 字段
- `filtered`: 过滤条件记录

### API Key 检测

服务器会自动检测以下环境变量中的 API key：

| Provider | 环境变量 |
|----------|----------|
| openai | `OPENAI_API_KEY` |
| anthropic | `ANTHROPIC_API_KEY` |
| google | `GOOGLE_API_KEY`, `GEMINI_API_KEY` |
| deepseek | `DEEPSEEK_API_KEY` |
| cohere | `COHERE_API_KEY` |
| mistral | `MISTRAL_API_KEY` |

## 完整测试示例

```python
import asyncio
import json
import subprocess
import sys

async def test_spiderswitch():
    """测试 spiderswitch MCP 服务器"""
    
    # 启动服务器（设置 API key）
    env = {
        "AI_PROTOCOL_PATH": "/path/to/ai-protocol",
        "OPENAI_API_KEY": "sk-your-key",
        "DEEPSEEK_API_KEY": "sk-your-key"
    }
    
    process = await asyncio.create_subprocess_exec(
        "python3", "-m", "spiderswitch.server",
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env
    )
    
    # ... MCP 客户端通信代码 ...
    
    # 列出所有模型
    all_models = await list_models(client)  # JSON 响应
    
    print(f"总模型数: {all_models['count']}")
    
    # 只列出有 API key 的模型
    ready_models = await list_models(client, require_api_key=True)
    
    print(f"有 API key 的模型数: {ready_models['count']}")
    print(f"过滤掉: {all_models['count'] - ready_models['count']} 个模型")
```

## 部署到 MCP 配置

在 MCP 客户端配置中：

```json
{
  "mcpServers": {
    "spiderswitch": {
      "command": "python3",
      "args": ["-m", "spiderswitch.server"],
      "env": {
        "AI_PROTOCOL_PATH": "/home/alex/ai-protocol",
        "OPENAI_API_KEY": "sk-your-openai-key",
        "DEEPSEEK_API_KEY": "sk-your-deepseek-key"
      }
    }
  }
}
```

注意事项：
1. 在 MCP 客户端启动时设置环境变量
2. 只配置你有权限使用的 provider 的 API key
3. 服务器会自动检测可用的 API key，无需手动配置

## 性能优化建议

使用 `require_api_key` 参数可以：
1. 减少返回的模型数量（通常从 188 个减少到 10-50 个）
2. 加快响应速度
3. 降低网络传输量
4. 提高模型选择的精确度

适合以下场景：
- 只关心可以立即使用的模型
- 需要快速刷新模型列表
- 在网络受限环境中使用
