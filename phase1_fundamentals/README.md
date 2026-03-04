# LangChain 1.0 基础实战（Phase 1）

这个仓库是一套按章节组织的 LangChain 1.0 入门实战。
目标不是“看完概念”，而是按顺序跑完 01-06 后，能自己写出一个可调用工具、可多轮对话、可查看执行过程的 Agent。

## 适合谁

- 第一次接触 LangChain，想从代码出发理解核心机制
- 已经会调用 LLM API，但不熟悉 `PromptTemplate`、`@tool`、`create_agent`
- 想把“模型调用”升级为“可执行任务的智能体”

## 学习路线

| 章节 | 主题 | 你会拿到的能力 |
| --- | --- | --- |
| `01_hello_langchain` | 模型调用与 `invoke` | 会用统一接口初始化模型，理解返回结构 |
| `02_prompt_templates` | 提示词模板 | 会写可复用模板，避免字符串拼接 |
| `03_messages` | 消息与对话状态 | 会管理多轮历史，避免“AI 失忆” |
| `04_custom_tools` | 自定义工具 | 会用 `@tool` 暴露函数能力 |
| `05_simple_agent` | Agent 构建 | 会用 `create_agent` 自动调用工具 |
| `06_agent_loop` | Agent 执行循环 | 会读懂消息流、查看中间步骤、流式输出 |

## 快速开始

### 1. 创建虚拟环境

```bash
python -m venv .venv
source .venv/bin/activate
```

Windows:

```bash
.venv\Scripts\activate
```

### 2. 安装依赖

```bash
pip install -U langchain python-dotenv
```

如果你使用特定模型提供方，请按需安装对应集成包（例如 `langchain-openai`、`langchain-groq`）。

### 3. 配置 `.env`

在仓库根目录新建 `.env`：

```env
OPENAI_API_KEY=your_api_key
OPENAI_API_BASE=https://api.openai.com/v1
DEFAULT_MODEL=openai:gpt-4o-mini
```

说明：

- `OPENAI_API_KEY`：所有章节都需要。
- `OPENAI_API_BASE`：建议始终配置；部分脚本会强校验。
- `DEFAULT_MODEL`：建议显式写成 `provider:model` 格式，避免不同脚本默认值不一致。

## 运行顺序（建议严格按顺序）

```bash
python 01_hello_langchain/main.py
python 01_hello_langchain/invoke_practice.py

python 02_prompt_templates/main.py
python 02_prompt_templates/examples/template_library.py

python 03_messages/main.py
python 03_messages/test.py

python 04_custom_tools/tools/weather.py
python 04_custom_tools/tools/calculator.py
python 04_custom_tools/tools/web_search.py
python 04_custom_tools/main.py

python 05_simple_agent/main.py
python 05_simple_agent/test_simple.py

python 06_agent_loop/main.py
python 06_agent_loop/test.py
```

## 哪些脚本强依赖 `OPENAI_API_BASE`

以下脚本在启动时会检查 `OPENAI_API_BASE`，未配置会直接退出：

- `01_hello_langchain/invoke_practice.py`
- `03_messages/test.py`
- `05_simple_agent/test_simple.py`
- `06_agent_loop/main.py`
- `06_agent_loop/test.py`

## 推荐学习方法

- 先运行 `main.py`：理解章节主线。
- 再运行 `test*.py` 或 `examples/*.py`：做最小验证。
- 每章至少做一次“改参数实验”：比如改 `system_prompt`、改工具 docstring、改历史窗口大小。
- 记录三件事：输入、模型中间动作（如 `tool_calls`）、最终输出。

## 常见问题

### 1) 模型初始化报错

优先检查三项：

- `.env` 是否在仓库根目录
- `OPENAI_API_KEY` 是否有效
- `DEFAULT_MODEL` 是否写成你当前 provider 支持的模型

### 2) Agent 不调用工具

通常是工具描述不够清晰：

- `@tool` 的 docstring 里写清“做什么、参数格式、返回格式”
- 避免多个工具职责重叠

### 3) 多轮对话记不住上下文

- 每次调用都要带完整 `messages`
- 必须把上一轮 `assistant` 回复写回历史

## 学完这个阶段后

你应该可以独立完成这些任务：

- 写一个带 2-3 个工具的 Agent
- 在终端打印完整执行轨迹（Human/AI/Tool 消息）
- 用 `stream()` 实时展示进度
- 在上下文过长时做历史截断

如果这些都能稳定做到，就可以进入下一阶段（记忆、结构化输出、复杂工作流）。
