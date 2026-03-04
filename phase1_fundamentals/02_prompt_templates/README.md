# 02 - Prompt Templates

这一章解决的是“提示词工程的工程化问题”：把难维护的字符串拼接，变成可复用、可测试的模板。

## 本章你会掌握

- `PromptTemplate`：纯文本模板
- `ChatPromptTemplate`：多角色消息模板
- `partial()`：固定一部分变量，减少重复传参
- LCEL 管道写法：`chain = template | model`
- 如何建立自己的模板库并复用

## 文件说明

- `main.py`：7 个示例，覆盖从基础模板到 LCEL
- `examples/template_library.py`：可复用模板集合
- `examples/README.md`：模板库的单独使用说明

## 运行前准备

在仓库根目录确保有 `.env`：

```env
OPENAI_API_KEY=your_api_key
OPENAI_API_BASE=https://api.openai.com/v1
DEFAULT_MODEL=openai:gpt-4o-mini
```

`main.py` 至少需要有效的 `OPENAI_API_KEY`。

## 怎么运行

```bash
python 02_prompt_templates/main.py
python 02_prompt_templates/examples/template_library.py
```

`main.py` 每个示例之间会暂停，按 Enter 继续。

## 示例导读（`main.py`）

1. `example_1_why_templates`
对比字符串拼接和模板的维护成本。

2. `example_2_prompt_template_basics`
`PromptTemplate` 的常见创建方式与调用方式。

3. `example_3_chat_prompt_template`
构建 `system/user` 结构化消息，交给模型调用。

4. `example_4_conversation_template`
通过预置问答构建 few-shot 对话模板。

5. `example_5_message_templates`
使用 `SystemMessagePromptTemplate` / `HumanMessagePromptTemplate` 做更细粒度控制。

6. `example_6_partial_variables`
提前固定角色、受众等不常变化字段。

7. `example_7_lcel_chains`
模板与模型直接管道连接，减少手动格式化步骤。

## 什么时候用哪种模板

- 单段文本任务：优先 `PromptTemplate`
- 聊天模型多角色上下文：优先 `ChatPromptTemplate`
- 固定场景高频调用：在模板上做 `partial()`
- 多组件编排：用 LCEL 管道

## 常见问题

### 1) 变量缺失报错

模板里有 `{topic}` 就必须传 `topic`。
先打印 `template.input_variables` 排查。

### 2) 模板写得很长，后续难维护

把“角色与规则”放 `system`，把“任务数据”放 `user`，两者分开管理。

### 3) 团队里模板风格不一致

统一放到 `examples/template_library.py` 类似的位置，按分类管理。

## 建议练习

- 把你日常常用的一段提示词改写成模板
- 做一个 `partial()` 版本（固定角色）
- 再做一个 LCEL 版本，体验调用简化

## 下一章

进入 `03_messages`：把“模板输出”接入真正的多轮状态管理。
