# 03 - Messages（消息与对话状态）

这一章的核心是：模型本身不记忆，记忆来自你每次传入的 `messages`。

## 本章你会掌握

- `system / user / assistant` 三类消息职责
- 多轮对话历史的正确维护方式
- 不传历史时为什么会“失忆”
- 用滑动窗口截断历史，平衡效果与成本

## 文件说明

- `main.py`：5 个示例，从消息格式到历史优化
- `test.py`：两个基础测试（记忆测试、历史截断测试）

## 运行前准备

```env
OPENAI_API_KEY=your_api_key
OPENAI_API_BASE=https://api.openai.com/v1
DEFAULT_MODEL=openai:gpt-4o-mini
```

说明：

- `main.py` 只强依赖 `OPENAI_API_KEY`。
- `test.py` 会同时检查 `OPENAI_API_KEY` 和 `OPENAI_API_BASE`。

## 怎么运行

```bash
python 03_messages/main.py
python 03_messages/test.py
```

`main.py` 示例之间会暂停，按 Enter 继续。

## 示例导读（`main.py`）

1. `example_1_message_types`
对比消息对象和字典格式，建议生产里优先字典格式。

2. `example_2_conversation_history`
演示正确追加历史：用户消息 + AI 回复都要入栈。

3. `example_3_wrong_way`
反例：每次独立调用，不带历史，模型无法参考前文。

4. `example_4_optimize_history`
实现滑动窗口：保留 system + 最近 N 轮对话。

5. `example_5_simple_chatbot`
把上述机制组合成一个极简“带记忆”聊天流程。

## 实战规则（建议记住）

- 每轮调用前：把新 `user` 消息 append 到 `messages`
- 调用后：把 `assistant` 回复 append 回去
- 下一轮：带完整历史再次调用

## 常见问题

### 1) 第二轮开始答非所问

优先检查是否把上一轮 AI 回复写回历史。

### 2) 历史越来越长，成本飙升

加入窗口策略，只保留最近几轮；`system` 消息通常保留。

### 3) 用对象消息还是字典消息

两种都能用。若涉及存储/序列化/接口传输，字典消息更省事。

## 建议练习

- 把窗口大小从 2 轮改到 5 轮，观察回答变化
- 给 system 增加风格限制，观察是否稳定生效
- 在 `test.py` 里补一个“未保存 assistant 回复”的失败测试

## 下一章

进入 `04_custom_tools`：让模型不仅“会说”，还能“调用函数做事”。
