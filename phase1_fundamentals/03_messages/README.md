# 03 - Messages

核心概念：**模型本身不记忆，记忆来自你每次传入的 `messages`。**

## 核心概念

| 消息角色 | 用途 |
|----------|------|
| `system` | 定义 AI 角色和行为规则 |
| `user` | 用户输入 |
| `assistant` | AI 回复（追加回历史实现记忆） |

## 运行

```bash
python 03_messages/main.py
```

## 多轮对话的黄金法则

```python
# 每轮调用
conversation.append({"role": "user", "content": "新问题"})
response = model.invoke(conversation)

# 关键：把 AI 回复写回历史
conversation.append({"role": "assistant", "content": response.content})
```

## 为什么会"失忆"？

```python
# ❌ 每次独立调用 = 无状态
response1 = model.invoke("我叫 Alice")
response2 = model.invoke("我叫什么？")  # 模型不知道

# ✅ 每次带完整历史 = 有记忆
messages = [{"role": "user", "content": "我叫 Alice"}]
response1 = model.invoke(messages)
messages.append({"role": "assistant", "content": response1.content})
messages.append({"role": "user", "content": "我叫什么？"})
response2 = model.invoke(messages)  # 模型知道你叫 Alice
```

## 历史太长怎么办？

滑动窗口：保留 `system` + 最近 N 轮

```python
def slide_window(messages, max_pairs=2):
    system = [m for m in messages if m["role"] == "system"]
    others = [m for m in messages if m["role"] != "system"]
    return system + others[-(max_pairs * 2):]
```

## 常见问题

**第二轮答非所问？** 检查是否把上一轮 AI 回复写回历史

**成本飙升？** 加滑动窗口，或用 token 计算动态截断

**对象还是字典？** 都能用于存储/序列化，字典更轻量

## 下一章

`04_custom_tools` - 让模型不仅"会说"，还能"调用函数做事"。
