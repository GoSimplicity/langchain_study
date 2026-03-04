# 04 - Custom Tools（自定义工具）

这一章把普通 Python 函数变成模型可调用的工具，是从“聊天”走向“执行”的关键一步。

## 本章你会掌握

- 用 `@tool` 定义工具
- 如何写高质量 docstring 与类型注解
- 单参数、多参数、可选参数工具写法
- `bind_tools()` 的作用与边界（只生成调用指令，不自动执行）

## 文件说明

- `main.py`：6 个示例，完整演示工具定义与绑定
- `tools/weather.py`：天气工具示例
- `tools/calculator.py`：计算工具示例
- `tools/web_search.py`：可选参数工具示例

## 运行前准备

```env
OPENAI_API_KEY=your_api_key
OPENAI_API_BASE=https://api.openai.com/v1
DEFAULT_MODEL=openai:gpt-4o-mini
```

`main.py` 强依赖 `OPENAI_API_KEY`。

## 怎么运行

```bash
python 04_custom_tools/tools/weather.py
python 04_custom_tools/tools/calculator.py
python 04_custom_tools/tools/web_search.py
python 04_custom_tools/main.py
```

`main.py` 示例之间会暂停，按 Enter 继续。

## 示例导读（`main.py`）

1. `example_1_simple_tool`
最小工具定义与元数据查看（name/description/args）。

2. `example_2_tool_with_params`
单参数工具调用和参数 schema 观察。

3. `example_3_multiple_params`
多参数映射到工具调用。

4. `example_4_optional_params`
`Optional` 参数与默认值行为。

5. `example_5_bind_tools`
把工具绑定给模型，观察 `response.tool_calls`。

6. `example_6_best_practices`
工具开发的工程约定总结。

## 关键理解：`bind_tools` 和 Agent 的区别

- `model.bind_tools([...])`：模型知道“可以调用哪些工具”，会产出 `tool_calls`。
- 它不会自动执行 Python 函数并回填结果。
- 自动执行循环要到下一章 `create_agent` 才完整出现。

## 工具编写建议

- 函数名见名知意
- docstring 写清：用途、参数格式、返回格式
- 返回值尽量稳定为字符串
- 工具内部做好异常兜底，避免直接抛出未处理异常

## 常见问题

### 1) 模型总是选错工具

通常是工具描述过于相似或过于抽象。把 docstring 写到“可区分”。

### 2) 工具能跑，但模型不调

先检查问题是否真的需要该工具，再检查 docstring 是否包含足够关键词。

### 3) 绑定后为什么没看到最终答案

因为你当前看到的是工具调用指令阶段，不是完整 Agent 循环。

## 下一章

进入 `05_simple_agent`：构建可自动决策和执行工具的 Agent。
