# LangChain 1.0 基础实战

按章节组织的 LangChain 1.0 入门教程。学完 01-06 后，你能独立构建一个可调用工具、可多轮对话、可追踪执行过程的 Agent。

## 学习路线

| 章节 | 主题 | 核心能力 |
|------|------|----------|
| `01_hello_langchain` | 模型调用 | 统一接口初始化模型，理解返回结构 |
| `02_prompt_templates` | 提示词模板 | 可复用模板，告别字符串拼接 |
| `03_messages` | 消息管理 | 多轮历史维护，避免"AI 失忆" |
| `04_custom_tools` | 自定义工具 | `@tool` 装饰器暴露函数能力 |
| `05_simple_agent` | Agent 构建 | `create_agent` 自动调用工具 |
| `06_agent_loop` | 执行循环 | 读懂消息流、流式输出、调试技巧 |

## 快速开始

```bash
# 1. 创建虚拟环境
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 2. 安装依赖
pip install -U langchain python-dotenv langchain-openai

# 3. 配置环境变量（根目录新建 .env）
OPENAI_API_KEY=your_api_key
OPENAI_API_BASE=https://api.openai.com/v1
DEFAULT_MODEL=openai:gpt-4o-mini
```

## 运行顺序

```bash
python 01_hello_langchain/main.py
python 02_prompt_templates/main.py
python 03_messages/main.py
python 04_custom_tools/main.py
python 05_simple_agent/main.py
python 06_agent_loop/main.py
```

## 推荐学习方法

1. **先运行** - 每章 `main.py` 是主线，先跑通再看代码
2. **改参数实验** - 改 `system_prompt`、改工具 docstring、改历史窗口大小
3. **追踪三件事** - 输入、模型中间动作（`tool_calls`）、最终输出

## 学完后你能做什么

- 写一个带 2-3 个工具的 Agent
- 在终端打印完整执行轨迹
- 用 `stream()` 实时展示进度
- 在上下文过长时做历史截断

完成这些就可以进入下一阶段（记忆、结构化输出、复杂工作流）。
