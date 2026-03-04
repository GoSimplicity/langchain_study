# 03 - Messages: 消息类型与对话管理

## 核心要点（只讲难点）

### 1. 三种消息类型

| 角色        | 字典格式                         | 对象格式                 | 用途    |
|-----------|------------------------------|----------------------|-------|
| System    | `{"role": "system", ...}`    | `SystemMessage(...)` | 系统提示  |
| User      | `{"role": "user", ...}`      | `HumanMessage(...)`  | 用户输入  |
| Assistant | `{"role": "assistant", ...}` | `AIMessage(...)`     | AI 回复 |

**推荐：直接用字典，简洁！**

```python
# ✅ 推荐
messages = [
    {"role": "system", "content": "你是助手"},
    {"role": "user", "content": "你好"}
]

# ❌ 不推荐（太啰嗦）
from langchain_core.messages import SystemMessage, HumanMessage

messages = [
    SystemMessage(content="你是助手"),
    HumanMessage(content="你好")
]
```

---

### 2. 对话历史管理（核心难点）

#### 🔴 关键规则

> **每次调用必须传递完整的对话历史！**

#### ❌ 错误做法

```python
# 第一次
r1 = model.invoke("我叫张三")

# 第二次（没传历史）
r2 = model.invoke("我叫什么？")  # AI 不记得！
```

#### ✅ 正确做法

```python
conversation = []

# 第一次
conversation.append({"role": "user", "content": "我叫张三"})
r1 = model.invoke(conversation)

# 关键：保存 AI 回复
conversation.append({"role": "assistant", "content": r1.content})

# 第二次（传递完整历史）
conversation.append({"role": "user", "content": "我叫什么？"})
r2 = model.invoke(conversation)  # AI 记得！
```

#### 💡 对话流程

```
第 1 轮：
  [system, user] → AI回复 → 保存回复

第 2 轮：
  [system, user, assistant, user] → AI回复 → 保存回复

第 3 轮：
  [system, user, assistant, user, assistant, user] → AI回复

每次都传递所有历史！
```

---

### 3. 对话历史优化（避免太长）

#### 🔴 问题

对话历史会越来越长，消耗大量 tokens 和成本。

#### ✅ 解决方案

只保留最近 N 轮对话：

```python
def keep_recent_messages(messages, max_pairs=3):
    """
    保留最近的 N 轮对话

    max_pairs: 保留的对话轮数（每轮 = user + assistant）
    """
    # 分离 system 和对话
    system_msgs = [m for m in messages if m.get("role") == "system"]
    conversation = [m for m in messages if m.get("role") != "system"]

    # 只保留最近的
    recent = conversation[-(max_pairs * 2):]

    # 返回：system + 最近对话
    return system_msgs + recent


# 使用
optimized = keep_recent_messages(conversation, max_pairs=5)
response = model.invoke(optimized)
```

**原理：**

- 总是保留 system 消息（定义角色）
- 只保留最近 5 轮对话（10 条消息）
- 丢弃更早的历史

---

## 完整示例

### 正确的对话管理

```python
# 初始化
conversation = [
    {"role": "system", "content": "你是 Python 导师"}
]

# 第 1 轮
conversation.append({"role": "user", "content": "什么是列表？"})
r1 = model.invoke(conversation)
conversation.append({"role": "assistant", "content": r1.content})

# 第 2 轮
conversation.append({"role": "user", "content": "它和元组有什么区别？"})
r2 = model.invoke(conversation)
conversation.append({"role": "assistant", "content": r2.content})

# 第 3 轮（测试记忆）
conversation.append({"role": "user", "content": "我第一个问题问的是什么？"})
r3 = model.invoke(conversation)
# AI 会回答："你问的是什么是列表"

# 优化：只保留最近 3 轮
optimized = keep_recent_messages(conversation, max_pairs=3)
```

---

## 运行示例

```bash
cd phase1_fundamentals/03_messages
python main.py
```

---

## 常见错误

### 错误 1：忘记保存 AI 回复

```python
# ❌ 错误
conversation.append({"role": "user", "content": "问题1"})
r1 = model.invoke(conversation)
# 忘记保存 r1.content！

conversation.append({"role": "user", "content": "问题2"})
r2 = model.invoke(conversation)  # AI 不知道之前的回答
```

### 错误 2：每次重新创建列表

```python
# ❌ 错误
conversation = [{"role": "user", "content": "问题1"}]
r1 = model.invoke(conversation)

conversation = [{"role": "user", "content": "问题2"}]  # 重新创建！
r2 = model.invoke(conversation)  # 丢失了历史
```

---

## 核心总结

| 要点         | 说明             |
|------------|----------------|
| **格式**     | 用字典，不用消息对象     |
| **历史**     | 每次必须传递完整历史     |
| **保存**     | 必须保存 AI 的回复    |
| **优化**     | 只保留最近 N 轮      |
| **System** | 总是保留 system 消息 |

---

## 下一步

- **04_custom_tools** - 创建自定义工具
- **05_simple_agent** - 构建第一个 Agent
