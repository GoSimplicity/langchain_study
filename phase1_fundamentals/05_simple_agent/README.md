# 05 - Simple Agent

这一章开始进入 Agent：模型不仅回答问题，还会自动决定何时调用工具、调用哪个工具。

## 本章你会掌握

- `create_agent()` 的基本用法
- 多工具场景下的路由行为
- `system_prompt` 如何约束 Agent 风格与边界
- 如何从 `response['messages']` 读取完整执行轨迹
- 如何在多轮中传递上下文继续计算

## 文件说明

- `main.py`：6 个示例，覆盖从单工具到多轮记忆
- `test_simple.py`：最小 Agent 可用性测试

## 运行前准备

```env
OPENAI_API_KEY=your_api_key
OPENAI_API_BASE=https://api.openai.com/v1
DEFAULT_MODEL=openai:gpt-4o-mini
```

说明：

- `main.py` 强依赖 `OPENAI_API_KEY`。
- `test_simple.py` 会同时检查 `OPENAI_API_KEY` 和 `OPENAI_API_BASE`。

## 怎么运行

```bash
python 05_simple_agent/main.py
python 05_simple_agent/test_simple.py
```

`main.py` 示例之间会暂停，按 Enter 继续。

## 示例导读（`main.py`）

1. `example_1_basic_agent`
最小 Agent：单工具场景下的自动调用。

2. `example_2_multi_tool_agent`
多工具路由，按问题意图自动选工具。

3. `example_3_agent_with_system_prompt`
通过 `system_prompt` 统一输出规则和行为边界。

4. `example_4_agent_execution_details`
遍历 `response['messages']`，查看 Human/AI/Tool 每一步。

5. `example_5_multi_turn_agent`
把上一轮完整消息继续传入，完成跨轮任务。

6. `example_6_best_practices`
工具数量、容错、性能和提示词边界的工程建议。

## 如何读 Agent 返回值

`agent.invoke()` 返回一个字典，核心字段是 `messages`：

- 用户输入（`HumanMessage`）
- 可能的工具调用指令（`AIMessage` with `tool_calls`）
- 工具结果（`ToolMessage`）
- 最终回答（通常是最后一条 `AIMessage`）

常见取值方式：

```python
final_answer = response["messages"][-1].content
```

## 常见问题

### 1) Agent 不调工具

- 工具 docstring 不清晰
- 问题本身不需要外部工具
- 工具太多且职责重叠

### 2) 多轮对话“前后断层”

第二轮要带上第一轮的 `response['messages']`，而不是只传新问题。

### 3) 结果格式不稳定

在 `system_prompt` 里写明确输出格式，并让工具返回稳定字符串结构。

## 建议练习

- 给 Agent 加一个你自己的工具（例如 `convert_currency`）
- 在 `system_prompt` 中添加“回答必须两行内”约束并验证
- 打印 `response['messages']`，手动标注每条消息角色

## 下一章

进入 `06_agent_loop`：详细拆解 Agent 执行循环和流式输出过程。
