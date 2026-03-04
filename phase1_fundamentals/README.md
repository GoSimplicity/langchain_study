# LangChain 1.0 总教程（Phase 1 Fundamentals）

这是一份基于当前项目代码和各模块 README 整理的统一学习手册，目标是让你按一条清晰路径，从 0 跑通 LangChain 1.0 的基础能力：

1. 模型调用
2. 提示词模板
3. 消息历史管理
4. 自定义工具
5. Agent 构建
6. Agent 执行循环与流式输出

---

## 1. 你会学到什么

完成本教程后，你应该可以独立做到：

- 使用 `init_chat_model` 初始化模型并调用 `invoke`
- 正确维护多轮对话历史（避免“AI 失忆”）
- 使用 `PromptTemplate` / `ChatPromptTemplate` 复用提示词
- 用 `@tool` 把 Python 函数变成可被模型调用的工具
- 使用 `create_agent` 构建可自动决策的智能体
- 用 `response["messages"]` 分析 Agent 的完整执行过程
- 用 `.stream()` 做实时输出与调试

---

## 2. 项目结构总览（以代码为准）

| 模块                    | 主题         | 关键文件                                      | 代码中的示例数 |
|-----------------------|------------|-------------------------------------------|---------|
| `01_hello_langchain`  | 第一个 LLM 调用 | `main.py`, `invoke_practice.py`           | 7       |
| `02_prompt_templates` | 提示词模板      | `main.py`, `examples/template_library.py` | 7       |
| `03_messages`         | 消息与对话管理    | `main.py`, `test.py`                      | 5       |
| `04_custom_tools`     | 自定义工具      | `main.py`, `tools/*.py`                   | 6       |
| `05_simple_agent`     | 简单 Agent   | `main.py`, `test_simple.py`               | 6       |
| `06_agent_loop`       | Agent 执行循环 | `main.py`, `test.py`                      | 6       |

说明：

- 某些 README 描述的示例数量与当前代码略有差异（例如 02 模块），本教程按当前代码行为整理。

---

## 3. 环境准备（先做这一步）

### 3.1 创建并激活虚拟环境

在项目根目录 `phase1_fundamentals` 下执行：

```bash
python -m venv venv
```

macOS / Linux:

```bash
source venv/bin/activate
```

Windows:

```bash
venv\Scripts\activate
```

### 3.2 安装依赖

```bash
pip install langchain langchain-groq python-dotenv
```

### 3.3 配置 `.env`

在项目根目录创建 `.env` 文件，建议至少包含：

```env
OPENAI_API_KEY=你的密钥
OPENAI_API_BASE=https://api.openai.com/v1
DEFAULT_MODEL=gpt-3.5-turbo
```

说明：

- `OPENAI_API_KEY`：所有模块都需要。
- `OPENAI_API_BASE`：部分脚本是“强依赖”，建议始终配置。
- `DEFAULT_MODEL`：可选。代码会做兼容处理：
    - 如果你写的是 `gpt-3.5-turbo`，会自动补成 `openai:gpt-3.5-turbo`
    - 如果你已写成 `provider:model`，就直接使用

### 3.4 哪些脚本强依赖 `OPENAI_API_BASE`

以下脚本如果缺少 `OPENAI_API_BASE` 会直接报错：

- `01_hello_langchain/invoke_practice.py`
- `03_messages/test.py`
- `05_simple_agent/test_simple.py`
- `06_agent_loop/main.py`
- `06_agent_loop/test.py`

---

## 4. 推荐学习顺序（严格按 01 -> 06）

---

### 模块 01：Hello LangChain

路径：`01_hello_langchain`

你会掌握：

- `init_chat_model` 的统一初始化方式
- `invoke` 的三种输入格式
- `AIMessage` 返回结构（`content` / `usage_metadata` / `response_metadata`）
- 基础错误处理和超时设置

先跑：

```bash
python 01_hello_langchain/main.py
python 01_hello_langchain/invoke_practice.py
```

重点观察：

- 相同问题在不同 `temperature` 下输出差异
- 传字符串 vs 传消息列表的行为差异
- 返回对象不是纯字符串，而是 `AIMessage`

常见坑：

- 只填了 `OPENAI_API_KEY`，但跑 `invoke_practice.py` 时报错：这个脚本还要求 `OPENAI_API_BASE`

---

### 模块 02：Prompt Templates

路径：`02_prompt_templates`

你会掌握：

- `PromptTemplate`（文本模板）
- `ChatPromptTemplate`（角色消息模板）
- `partial()` 部分变量预填充
- LCEL 管道语法：`chain = template | model`

先跑：

```bash
python 02_prompt_templates/main.py
python 02_prompt_templates/examples/template_library.py
```

重点观察：

- `main.py` 在每个示例之间会 `input()` 暂停，按 Enter 继续
- `template_library.py` 提供了 15 类可复用模板（翻译、代码、总结、客服、分析等）

建议实践：

- 把你常用的一类提示词抽到模板库中，避免字符串拼接

---

### 模块 03：Messages（对话状态管理）

路径：`03_messages`

你会掌握：

- `system` / `user` / `assistant` 三类消息的职责
- 为什么 LLM 是无状态的（Stateless）
- 如何通过完整历史实现“记忆”
- 滑动窗口截断历史，控制 token 成本

先跑：

```bash
python 03_messages/main.py
python 03_messages/test.py
```

重点观察：

- 正确做法：每轮都要把完整历史传回 `model.invoke(messages)`
- 错误做法：每次单独提问，模型无法记住前文

一句话记忆：

- “AI 会记住你，不是因为它有内存，而是因为你每次都把历史喂回去了。”

---

### 模块 04：Custom Tools

路径：`04_custom_tools`

你会掌握：

- `@tool` 把函数声明为工具
- docstring 和类型注解对工具路由的影响
- 单参数、多参数、可选参数（`Optional`）工具写法
- `bind_tools` 的作用：让模型产出 `tool_calls`

先跑：

```bash
python 04_custom_tools/tools/weather.py
python 04_custom_tools/tools/calculator.py
python 04_custom_tools/tools/web_search.py
python 04_custom_tools/main.py
```

重点观察：

- 工具对象有 `name` / `description` / `args` 等元数据
- `model.bind_tools([...])` 后，模型可能先返回工具调用指令，而不是最终答案
- 04 章主要是“让模型学会调用工具”，真正自动执行循环在 05/06

工具开发规范（非常重要）：

- docstring 要写清楚“做什么、参数含义、返回格式”
- 函数返回值尽量统一 `str`
- 工具内部要 `try/except`，避免异常让 Agent 死循环

---

### 模块 05：Simple Agent

路径：`05_simple_agent`

你会掌握：

- `create_agent(model=..., tools=..., system_prompt=...)`
- Agent 如何根据问题自动选择工具
- `response["messages"][-1].content` 获取最终答案
- 多轮 Agent 会话中如何传历史

先跑：

```bash
python 05_simple_agent/main.py
python 05_simple_agent/test_simple.py
```

重点观察：

- Agent 响应是完整消息轨迹，不只是单条文本
- 工具越多越容易混淆，建议控制在 2-5 个核心工具
- 系统提示词 (`system_prompt`) 可以强约束输出风格和流程

补充说明：

- `main.py` 内联定义了工具，便于开箱即用
- `test_simple.py` 从 `04_custom_tools/tools` 导入工具，便于模块复用演示

---

### 模块 06：Agent Loop（执行循环）

路径：`06_agent_loop`

你会掌握：

- ReAct 风格执行过程：思考 -> 动作 -> 观察 -> 回答
- 如何解读 `HumanMessage` / `AIMessage` / `ToolMessage`
- `invoke()` vs `stream()` 的使用场景
- 如何统计工具调用次数、查看中间状态

先跑：

```bash
python 06_agent_loop/main.py
python 06_agent_loop/test.py
```

重点观察：

- `stream()` 会逐步返回状态块（chunk）
- 最终回答依旧建议从最后一条消息中提取
- 该模块默认模型是 `Pro/MiniMaxAI/MiniMax-M2.5`，并强依赖 `OPENAI_API_BASE`

---

## 5. 每个模块的“最小通过标准”

你可以用下面标准判断自己是否真的学会：

1. 01：能解释 `invoke` 三种输入，能读取 `response.content`
2. 02：能写一个 `ChatPromptTemplate` 并用 `template | model` 调用
3. 03：能实现带历史的多轮会话和滑动窗口截断
4. 04：能写一个高质量 `@tool`（清晰 docstring + 类型注解 + 错误兜底）
5. 05：能构建 Agent 并拿到 `response["messages"][-1].content`
6. 06：能用 `stream()` 展示中间过程，并统计工具调用次数

---

## 6. 常见问题与排查清单

### 6.1 提示“未找到 OPENAI_API_KEY”

处理：

- 确认 `.env` 在项目根目录
- 确认键名是 `OPENAI_API_KEY`，不是其他拼写
- 重新激活虚拟环境再执行脚本

### 6.2 只配了 Key，部分脚本仍报错

原因：

- 某些脚本要求 `OPENAI_API_BASE` 一并存在（见本教程第 3.4 节）

处理：

- 在 `.env` 中补上 `OPENAI_API_BASE`

### 6.3 Agent 不调用工具

优先检查：

- 工具 docstring 是否过于模糊
- 用户问题是否真的需要外部工具
- 工具数量是否过多、功能描述是否重叠

### 6.4 对话“失忆”

原因：

- 你没有传完整历史消息数组

正确做法：

```python
response1 = agent.invoke({"messages": [{"role": "user", "content": "10 + 5"}]})
response2 = agent.invoke({
    "messages": response1["messages"] + [{"role": "user", "content": "再乘以3"}]
})
```

### 6.5 导入路径报错

当前项目使用的是 LangChain 1.0 风格导入：

```python
from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
from langchain_core.tools import tool
```

---

## 7. 一次性跑完整个阶段（命令清单）

在项目根目录执行：

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

提示：

- 02~06 的 `main.py` 多数包含 `input()` 分段暂停，运行时按 Enter 继续。

---

## 8. 你现在可以自己做什么

建议你做 3 个小扩展，快速把“会看示例”升级为“会做项目”：

1. 在 `04_custom_tools/tools` 新增一个真实业务工具（如数据库查询、工单检索）
2. 在 `05_simple_agent/main.py` 把新工具挂到 Agent，并写清楚 `system_prompt`
3. 在 `06_agent_loop/main.py` 增加流式日志打印，输出每一步 `tool_calls` 参数

---

## 9. 下一阶段方向（Phase 2）

根据项目总 README，后续将进入中级主题：

- 内存与状态持久化（如 checkpoint）
- 中间件与可观测性
- 结构化输出与验证重试

当你完成本阶段并能稳定跑通 01~06，进入 Phase 2 会非常顺滑。
