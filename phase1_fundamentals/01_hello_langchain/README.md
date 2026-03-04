# 01 - Hello LangChain

把模型调用跑通，理解 `invoke()` 的输入输出。

## 核心概念

| 概念 | 说明 |
|------|------|
| `init_chat_model()` | 统一接口初始化模型，无需关心 provider 差异 |
| `invoke()` | 同步调用，返回 `AIMessage` 对象（不是字符串） |
| 消息格式 | 字符串 / 消息对象 / 字典（生产推荐字典） |
| `temperature` | 0 = 确定性，1+ = 创造性 |

## 运行

```bash
python 01_hello_langchain/main.py
```

## 示例速览

1. **简单调用** - 一句话调用模型
2. **消息对象** - `SystemMessage` / `HumanMessage` 构建对话
3. **字典格式** - 生产推荐，便于序列化
4. **Temperature** - 对比 0.0 vs 1.2 的输出差异
5. **返回值** - `AIMessage` 结构解析
6. **错误处理** - 超时与异常兜底

## 关键理解

### 为什么多轮对话要每次传完整历史？

LLM 是**无状态**的——它不会"记住"之前的对话。每次调用都是独立的。

```python
# ❌ 错误：第二次调用不带历史
response1 = model.invoke("我叫 Alice")
response2 = model.invoke("我叫什么？")  # 模型不知道你叫 Alice

# ✅ 正确：每次都带完整历史
messages = [{"role": "user", "content": "我叫 Alice"}]
response1 = model.invoke(messages)
messages.append({"role": "assistant", "content": response1.content})
messages.append({"role": "user", "content": "我叫什么？"})
response2 = model.invoke(messages)  # 模型能正确回答
```

### `response.content` vs `response.usage_metadata`

- `content`: AI 的文本回答
- `usage_metadata`: token 消耗统计（用于成本控制）

## 下一章

`02_prompt_templates` - 把临时字符串升级成可复用模板。
