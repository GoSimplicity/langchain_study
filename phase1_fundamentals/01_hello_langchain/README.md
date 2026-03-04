# 01 - Hello LangChain

这一章的目标很直接：先把模型调用跑通，并且真正看懂 `invoke()` 的输入和输出。

## 本章你会掌握

- 用 `init_chat_model` 初始化聊天模型
- 使用三种 `invoke` 输入格式（字符串、字典消息、消息对象）
- 读取 `AIMessage` 的关键字段：`content`、`response_metadata`、`usage_metadata`
- 做基础错误处理和超时控制

## 文件说明

- `main.py`：7 个示例，覆盖初始化、消息格式、参数、返回值、错误处理
- `invoke_practice.py`：6 个练习，偏动手实验和结果观察

## 运行前准备

在仓库根目录确保有 `.env`：

```env
OPENAI_API_KEY=your_api_key
OPENAI_API_BASE=https://api.openai.com/v1
DEFAULT_MODEL=openai:gpt-4o-mini
```

说明：

- `main.py` 强依赖 `OPENAI_API_KEY`。
- `invoke_practice.py` 会同时检查 `OPENAI_API_KEY` 和 `OPENAI_API_BASE`。

## 怎么运行

推荐在仓库根目录执行：

```bash
python 01_hello_langchain/main.py
python 01_hello_langchain/invoke_practice.py
```

`invoke_practice.py` 在练习之间会暂停，按 Enter 继续。

## 示例导读（`main.py`）

1. `example_1_simple_invoke`
一句话调用模型，确认最小链路可用。

2. `example_2_messages`
使用 `SystemMessage` / `HumanMessage` 组织上下文，并继续追加多轮。

3. `example_3_dict_messages`
使用字典格式消息（生产里更常见，便于序列化）。

4. `example_4_model_parameters`
对比不同 `temperature` 带来的输出差异。

5. `example_5_response_structure`
拆解 `AIMessage` 返回结构，关注 token 与模型元信息。

6. `example_6_error_handling`
示范超时和异常兜底写法。

7. `example_7_multiple_models`
演示模型标识切换（重点在接口统一，不在某个具体模型）。

## 练习导读（`invoke_practice.py`）

1. 三种输入格式对比
2. 同一问题在不同 system prompt 下的风格差异
3. 正确维护对话历史
4. 不传历史导致“失忆”的反例
5. 返回值字段解读与 token 观察
6. 小型聊天机器人演示（非交互式）

## 学习检查点

跑完本章后，确认你能回答这些问题：

- 什么情况下用字符串调用，什么情况下用消息列表调用？
- 为什么多轮对话要每次传完整历史？
- `response['messages'][-1]` 和 `response.content` 分别在哪些对象上可用？

## 常见问题

### 1) 报 `未找到 OPENAI_API_KEY`

- 确认 `.env` 在仓库根目录
- 确认 key 不是占位符

### 2) `invoke_practice.py` 启动就退出

这个脚本会检查 `OPENAI_API_BASE`，请补齐该环境变量。

### 3) 只拿到字符串，不知道 token 用量

优先看 `response.usage_metadata` 或 `response.response_metadata`，不同模型返回字段可能有差异。

## 下一章

进入 `02_prompt_templates`：把“临时字符串提示词”升级成可维护、可复用的模板。
