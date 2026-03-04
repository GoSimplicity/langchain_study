# 05 - Simple Agent

Agent = 模型 + 工具 + 自动执行循环

模型不仅回答问题，还会自动决定何时调用工具、调用哪个工具。

## 核心概念

| 概念 | 说明 |
|------|------|
| `create_agent()` | 创建 Agent |
| 工具路由 | Agent 根据问题自动选工具 |
| `system_prompt` | 约束 Agent 行为和边界 |
| `response['messages']` | 完整执行轨迹 |

## 运行

```bash
python 05_simple_agent/main.py
```

## Agent 执行流程（ReAct）

```
用户问题
    ↓
模型分析：需要调用工具吗？
    ↓ 是
选择工具 + 生成参数
    ↓
执行工具 → 获取结果
    ↓
模型基于结果生成答案
```

## 读取 Agent 返回值

```python
response = agent.invoke({"messages": [...]})

# 最终答案
final = response["messages"][-1].content

# 检查是否用了工具
has_tools = any(
    hasattr(m, 'tool_calls') and m.tool_calls
    for m in response['messages']
)
```

## 多轮对话

```python
# 第 1 轮
response1 = agent.invoke({"messages": [user_msg1]})

# 第 2 轮：带上第 1 轮完整历史
context = response1['messages'] + [user_msg2]
response2 = agent.invoke({"messages": context})
```

## 常见问题

**不调工具？** docstring 不清晰 / 问题不需要工具 / 工具职责重叠

**多轮断层？** 没带上上一轮的 `response['messages']`

**格式不稳定？** 在 `system_prompt` 里明确输出格式

## 下一章

`06_agent_loop` - 深入执行循环和流式输出。
