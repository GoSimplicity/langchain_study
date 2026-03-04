# 04 - Custom Tools

把普通 Python 函数变成模型可调用的工具——从"聊天"走向"执行"的关键一步。

## 核心概念

| 概念 | 说明 |
|------|------|
| `@tool` | 装饰器，把函数包装成 Tool 对象 |
| docstring | 模型用它决定"何时调用" |
| `bind_tools()` | 把工具绑定给模型 |
| `tool_calls` | 模型生成的调用指令（不是执行结果） |

## 运行

```bash
python 04_custom_tools/main.py
```

## 工具定义模板

```python
@tool
def my_tool(param: str) -> str:
    """
    一句话描述工具用途。

    参数:
        param: 参数说明
    """
    # 实现逻辑
    return "结果"
```

## 关键理解：bind_tools vs Agent

```
bind_tools()  → 模型知道"可以调哪些工具"，产出 tool_calls
             → 但不会自动执行函数

Agent        → 自动执行循环：
               1. 模型决定调用工具
               2. 执行工具
               3. 把结果返回模型
               4. 模型生成最终答案
```

## 工具编写建议

```python
# ✅ 好的工具
@tool
def get_weather(city: str) -> str:
    """获取指定城市的天气信息。参数: city - 城市名称"""
    return weather_data.get(city, "暂无数据")

# ❌ 差的工具
@tool
def do_something(data):  # 无类型注解
    pass  # 无 docstring
```

## 常见问题

**模型总选错工具？** docstring 太相似或太抽象

**工具能跑但不调？** 检查问题是否真需要工具，docstring 是否含关键词

**绑定了没答案？** 你看到的是 tool_calls 指令，不是完整 Agent 循环

## 下一章

`05_simple_agent` - 构建可自动决策和执行工具的 Agent。
