# 06 - Agent Loop

深入理解 Agent 执行循环：分析问题、调用工具、接收结果、生成答案。

## 核心概念

| 概念 | 说明 |
|------|------|
| `response['messages']` | 完整执行历史 |
| `stream()` | 实时输出，调试利器 |
| `tool_calls` | 工具调用指令 |
| 消息类型 | Human/AI/Tool/System |

## 运行

```bash
python 06_agent_loop/main.py
```

## 执行循环速记

```
1. HumanMessage      → 用户问题
2. AIMessage(tool_calls) → 决定调用工具
3. ToolMessage       → 工具执行结果
4. AIMessage         → 最终答案
```

## 实用代码模式

```python
# 最终答案
final = response['messages'][-1].content

# 是否用了工具
has_tools = any(
    hasattr(m, 'tool_calls') and m.tool_calls
    for m in response['messages']
)

# 收集工具名
tools = [
    tc['name'] for m in response['messages']
    if hasattr(m, 'tool_calls')
    for tc in m.tool_calls
]
```

## 调试三步

1. 打印完整 `messages`
2. 统计 `tool_calls` 次数和参数
3. 用 `stream()` 看卡在哪个阶段

## 常见问题

**stream 输出看不懂？** chunk 是状态增量，关注最新消息类型

**答案提取错误？** 先打印全部消息确认结构

**工具调用异常？** 检查问题是否多步，或 system_prompt 是否引导分步

## Phase 1 收官

完成本章后，你应该能：

- 解释 Agent 一次调用中每条消息的作用
- 用 `stream()` 做实时输出
- 快速定位"没调工具"或"调错工具"的问题

这意味着 Phase 1 核心能力已完整闭环。
