# 02 - Prompt Templates

把提示词从临时字符串变成可复用、可维护的模板。

## 核心概念

| 概念 | 用途 |
|------|------|
| `PromptTemplate` | 纯文本模板 |
| `ChatPromptTemplate` | 多角色消息模板 |
| `partial()` | 固定部分变量，减少重复传参 |
| `template \| model` | LCEL 链式调用 |

## 运行

```bash
python 02_prompt_templates/main.py
```

## 何时用哪种模板

```
单段文本任务      → PromptTemplate
聊天多角色上下文  → ChatPromptTemplate
固定场景高频调用  → partial()
多组件编排        → LCEL 管道
```

## 核心思维

```python
# ❌ 字符串拼接 - 难维护
prompt = f"你是{role}，请{task}"

# ✅ 模板化 - 结构与数据分离
template = PromptTemplate.from_template("你是{role}，请{task}")
prompt = template.format(role="老师", task="解释量子力学")
```

## Few-shot 示例

```python
template = ChatPromptTemplate.from_messages([
    ("system", "你是一个{role}"),
    ("user", "1+1=?"),
    ("assistant", "2"),       # 预设示例
    ("user", "{real_question}")  # 真实问题
])
```

## 常见问题

**变量缺失报错？** 打印 `template.input_variables` 检查

**模板太长难维护？** 把"角色"放 system，"数据"放 user

## 下一章

`03_messages` - 把模板输出接入多轮对话状态管理。
