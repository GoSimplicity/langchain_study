# 06 - Agent Loop（执行循环）

这一章专门讲 Agent 在一次请求里的完整执行过程：分析问题、调用工具、接收结果、生成最终答案。

## 本章你会掌握

- 如何读取 Agent 的完整消息历史
- 如何判断是否触发了工具调用
- `stream()` 的实时输出用法
- 多步骤任务中的中间状态观测
- 如何做执行过程调试

## 文件说明

- `main.py`：6 个示例，逐步拆解执行循环
- `test.py`：最小可运行验证（包含 `invoke` 与 `stream`）

## 运行前准备

```env
OPENAI_API_KEY=your_api_key
OPENAI_API_BASE=https://api.openai.com/v1
DEFAULT_MODEL=openai:gpt-4o-mini
```

说明：

- `main.py` 和 `test.py` 都会检查 `OPENAI_API_BASE`。
- 这两个脚本会从 `04_custom_tools/tools` 导入工具，建议在仓库根目录运行命令。

## 怎么运行

```bash
python 06_agent_loop/main.py
python 06_agent_loop/test.py
```

`main.py` 示例之间会暂停，按 Enter 继续。

## 示例导读（`main.py`）

1. `example_1_understand_loop`
完整打印 `response['messages']`，看一轮调用的全链路。

2. `example_2_streaming`
使用 `agent.stream()` 实时接收输出片段。

3. `example_3_multi_step`
复杂问题下的多次工具调用。

4. `example_4_inspect_state`
在流式过程中逐步输出状态，适合调试。

5. `example_5_message_types`
逐条解释 `HumanMessage`、`AIMessage`、`ToolMessage`。

6. `example_6_best_practices`
提取最终答案、统计工具使用、异常处理的实用写法。

## 执行循环速记

典型顺序如下：

1. `HumanMessage`：用户问题
2. `AIMessage`（带 `tool_calls`）：模型决定调用工具
3. `ToolMessage`：工具返回结果
4. `AIMessage`（无 `tool_calls`）：最终回答

## 调试建议

- 调试第一步：先打印完整 `messages`
- 调试第二步：统计 `tool_calls` 次数和参数
- 调试第三步：用 `stream()` 观察卡在哪个阶段

## 常见问题

### 1) 看不懂 `stream()` 输出

`stream()` 返回的是状态增量，不一定每个 chunk 都是最终文本。要关注最新消息类型。

### 2) 最终答案提取错误

一般取 `response['messages'][-1].content`，但调试时建议先打印全部消息确认结构。

### 3) 工具调用次数异常

检查问题是否含多步任务，或 `system_prompt` 是否引导了分步求解。

## 收官检查

完成本章后，你应该能独立：

- 解释 Agent 一次调用中每条消息的作用
- 用 `stream()` 做最小实时输出
- 快速定位“没调工具”或“调错工具”的问题

这意味着 Phase 1 的核心能力已经完整闭环。
