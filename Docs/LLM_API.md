# Oriflow LLM API

本文件记录项目中提供的轻量化 LLM 客户端封装，便于 TUI、节点插件或脚本直接调用。

文件：`LLM/client.py`；包：`LLM`。

导出对象
- `LLMClient(backend='openai', api_key=None, endpoint=None)`：主要客户端类。
  - `generate(prompt, model='gpt-3.5-turbo', max_tokens=256, **kwargs) -> str`：同步调用，返回生成的文本。
  - `generate_async(prompt, model='gpt-3.5-turbo', max_tokens=256, **kwargs) -> str`：异步调用，返回生成文本。
- `create_client(backend='openai', api_key=None, endpoint=None)`：工厂函数。
- 另外 `LLM` 包重导出了 `Workflow.llm_config` 中的 `set_llm_api`, `get_llm_api`, `clear_llm_api`，用于全局凭证管理。

使用示例（同步）

```python
from LLM import create_client, set_llm_api

# 可选：设置全局凭证（会被 LLMClient 自动读取）
set_llm_api(api_key="sk-...")

client = create_client(backend="openai")
text = client.generate("请用中文总结下面文本：...", model="gpt-3.5-turbo", max_tokens=200)
print(text)
```

使用示例（异步）

```python
import asyncio
from LLM import create_client

async def main():
    client = create_client(backend="openai")
    resp = await client.generate_async("Tell me a short poem.")
    print(resp)

asyncio.run(main())
```

离线/测试模式
- 可以使用 `create_client(backend='mock')` 在无网络或无 `openai` 包时获得可预测的字符串返回，便于 TUI 或单元测试。

注意
- 1) 目前对 `openai` 的调用使用同步客户端并通过 `asyncio.to_thread` 提供异步包装。
- 2) `LLM` 模块不会自动安装或管理 `openai` 依赖；请在 `requirements.txt` 中添加 `openai`（若需要）或在运行环境中手动安装。
