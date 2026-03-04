"""
02 - Prompt Templates: 提示词模板
"""

# 标准库：读取环境变量。
import os

# 从 .env 加载配置。
from dotenv import load_dotenv
# LangChain 统一模型初始化接口。
from langchain.chat_models import init_chat_model
# PromptTemplate: 纯文本模板。
# ChatPromptTemplate: 聊天消息模板。
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
# 这两个类用于更细粒度构造 system/human 消息模板。
from langchain_core.prompts import (
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)

# ============================= 学习说明 =============================
# 这一章最关键的工程思维：
# "把提示词当作可复用组件，而不是临时字符串。"
# ==================================================================

# ============================================================================
# 环境配置与模型初始化
# ============================================================================

# 把 .env 中的配置加载到当前进程环境。
load_dotenv()

# 读取 API key。
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# 读取可选 base_url。
OPENAI_API_BASE = os.getenv("OPENAI_API_BASE")
# 读取默认模型。
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "gpt-3.5-turbo")
# 若模型没写 provider 前缀，则自动补 openai:。
MODEL_NAME = DEFAULT_MODEL if ":" in DEFAULT_MODEL else f"openai:{DEFAULT_MODEL}"

# 校验 key 是否有效（示例中常见的占位符也判定为无效）。
if not OPENAI_API_KEY or OPENAI_API_KEY == "your_openai_api_key_here_replace_this":
    raise ValueError(
        "\n" + "=" * 70 + "\n"
        "❌ 错误：未找到有效的 OPENAI_API_KEY 环境变量！\n"
        "=" * 70 + "\n"
        "请在 .env 文件中填入你的配置：\n"
        "   OPENAI_API_KEY=sk-your_actual_key_here\n"
        "   OPENAI_API_BASE=https://api.openai.com/v1  # (可选) 如果使用中转或私有部署\n"
        "=" * 70
    )

# 如果 key 格式看起来不标准且没配 base_url，则给警告。
if not OPENAI_API_BASE and not OPENAI_API_KEY.startswith("sk-"):
    print("\n⚠️  警告：你的 OPENAI_API_KEY 格式可能不正确，请确保配置了正确的密钥或 BASE_URL\n")

# 全局初始化模型。
# 这样每个示例不必重复创建模型，聚焦在“模板”本身。
model = init_chat_model(MODEL_NAME, api_key=OPENAI_API_KEY, base_url=OPENAI_API_BASE)


# ============================================================================
# 示例 1：为什么需要提示词模板？
# ============================================================================
def example_1_why_templates():
    """
    对比：字符串拼接 vs 模板

    学习目标：理解模板在可维护性、复用性上的优势。
    """
    print("\n" + "=" * 70)
    print("示例 1：为什么需要提示词模板？")
    print("=" * 70)

    # --------------------------- 方式1：字符串拼接 ---------------------------
    print("\n【方式 1：字符串拼接（不推荐）】")
    print("-" * 70)

    # 准备变量。
    topic = "Python"
    difficulty = "初学者"

    # 直接拼接字符串。
    # 问题：提示词结构和业务变量混在一起，后期维护成本高。
    prompt_str = f"你是一个{difficulty}级别的编程导师。请用简单易懂的语言解释{topic}。"
    print(f"提示词：{prompt_str}")

    # 调用模型。
    response = model.invoke(prompt_str)
    print(f"AI 回复：{response.content[:100]}...\n")

    # --------------------------- 方式2：模板化 ---------------------------
    print("【方式 2：使用 PromptTemplate（推荐）】")
    print("-" * 70)

    # 把“结构”抽成模板，把“数据”留到调用时注入。
    template = PromptTemplate.from_template(
        "你是一个{difficulty}级别的编程导师。请用简单易懂的语言解释{topic}。"
    )

    # 打印模板内容。
    print(f"模板：{template.template}")
    # 打印模板自动识别出的变量名。
    print(f"变量：{template.input_variables}")

    # 格式化模板，注入具体变量。
    prompt = template.format(difficulty=difficulty, topic=topic)
    print(f"生成的提示词：{prompt}")

    # 调用模型。
    response = model.invoke(prompt)
    print(f"AI 回复：{response.content[:100]}...\n")

    # 打印模板化优势总结。
    print("💡 优势：")
    print("  1. 可复用 - 同一个模板可以用于不同输入")
    print("  2. 可维护 - 模板和数据分离")
    print("  3. 可验证 - 变量缺失会被及时发现")
    print("  4. 可组合 - 易与链式调用结合")


# ============================================================================
# 示例 2：PromptTemplate 基础用法
# ============================================================================
def example_2_prompt_template_basics():
    """
    PromptTemplate 用于生成“纯文本提示词”。
    """
    print("\n" + "=" * 70)
    print("示例 2：PromptTemplate 基础用法")
    print("=" * 70)

    # 方法 1：from_template（最常用）。
    print("\n【方法 1：from_template（推荐）】")
    template1 = PromptTemplate.from_template(
        "将以下文本翻译成{language}：\n{text}"
    )

    # 把变量注入模板。
    prompt1 = template1.format(language="法语", text="Hello, how are you?")
    print(f"生成的提示词：\n{prompt1}\n")

    # 调用模型并打印结果。
    response1 = model.invoke(prompt1)
    print(f"AI 回复：{response1.content}\n")

    # 方法 2：显式声明 input_variables。
    print("【方法 2：显式指定变量】")
    template2 = PromptTemplate(
        input_variables=["product", "feature"],
        template="为{product}写一句广告语，重点突出{feature}特点。"
    )

    # 格式化并调用。
    prompt2 = template2.format(product="智能手表", feature="超长续航")
    print(f"生成的提示词：\n{prompt2}\n")

    response2 = model.invoke(prompt2)
    print(f"AI 回复：{response2.content}\n")

    # 方法 3：invoke 返回 PromptValue。
    print("【方法 3：使用 invoke（返回 PromptValue）】")
    template3 = PromptTemplate.from_template(
        "写一首关于{theme}的{style}风格的诗，不超过4行。"
    )

    # invoke 输入字典，输出对象里含 text 字段。
    prompt_value = template3.invoke({"theme": "春天", "style": "现代"})
    print(f"生成的提示词：\n{prompt_value.text}\n")


# ============================================================================
# 示例 3：ChatPromptTemplate - 聊天消息模板
# ============================================================================
def example_3_chat_prompt_template():
    """
    ChatPromptTemplate 用于构建结构化消息（system/user/assistant）。
    """
    print("\n" + "=" * 70)
    print("示例 3：ChatPromptTemplate - 聊天消息模板")
    print("=" * 70)

    # 方法 1：元组写法（最常用）。
    print("\n【方法 1：元组格式（推荐）】")

    # 定义一个 system + user 的模板结构。
    chat_template = ChatPromptTemplate.from_messages([
        ("system", "你是一个{role}，擅长{expertise}。"),
        ("user", "请帮我{task}")
    ])

    # 查看模板需要哪些变量。
    print(f"模板提取的变量：{chat_template.input_variables}")

    # 注入变量，得到消息对象列表。
    messages = chat_template.format_messages(
        role="Python 导师",
        expertise="用简单方式解释复杂概念",
        task="解释什么是列表推导式"
    )

    # 打印消息列表，观察角色内容。
    print("\n生成的消息对象：")
    for msg in messages:
        print(f"  [{msg.type.capitalize()}]: {msg.content}")

    # 把消息列表直接传给模型。
    response = model.invoke(messages)
    print(f"\nAI 回复：{response.content[:150]}...\n")

    # 方法 2：简单模板。
    print("【方法 2：简化模板】")

    simple_template = ChatPromptTemplate.from_messages([
        ("system", "你是一个友好的助手"),
        ("user", "{question}")
    ])

    # 注入问题变量。
    messages = simple_template.format_messages(question="什么是机器学习？")
    # 调用并输出。
    response = model.invoke(messages)
    print(f"AI 回复：{response.content[:100]}...\n")


# ============================================================================
# 示例 4：多轮对话模板
# ============================================================================
def example_4_conversation_template():
    """
    用模板预设 few-shot 对话历史。
    """
    print("\n" + "=" * 70)
    print("示例 4：多轮对话预设模板 (Few-shot 演示)")
    print("=" * 70)

    # 构建包含 system / user / assistant / user 的模板。
    template = ChatPromptTemplate.from_messages([
        ("system", "你是一个{role}。{instruction}"),
        ("user", "{question1}"),
        ("assistant", "{answer1}"),
        ("user", "{question2}")
    ])

    print("模板结构设计：")
    print("  1. System: 设定角色和行为")
    print("  2. User: few-shot 问题")
    print("  3. Assistant: few-shot 回答")
    print("  4. User: 当前真实问题\n")

    # 注入变量，形成完整消息。
    messages = template.format_messages(
        role="Python 专家",
        instruction="回答要简洁、准确，不废话",
        question1="什么是列表？",
        answer1="列表是 Python 中的有序可变集合，用方括号 [] 表示。",
        question2="它和元组有什么区别？"
    )

    print("生成的完整对话流：")
    for i, msg in enumerate(messages, 1):
        content_preview = msg.content[:60] + "..." if len(msg.content) > 60 else msg.content
        print(f"  {i}. [{msg.type}] {content_preview}")

    # 调用模型并输出。
    response = model.invoke(messages)
    print(f"\nAI 回复：{response.content}\n")


# ============================================================================
# 示例 5：使用 MessagePromptTemplate（高级）
# ============================================================================
def example_5_message_templates():
    """
    更细粒度构建：先造 system 模板，再造 human 模板，再组合。
    """
    print("\n" + "=" * 70)
    print("示例 5：MessagePromptTemplate 类（高级）")
    print("=" * 70)

    # 创建 system 模板对象。
    system_template = SystemMessagePromptTemplate.from_template(
        "你是一个{profession}，你的特长是{specialty}。"
    )

    # 创建 human 模板对象。
    human_template = HumanMessagePromptTemplate.from_template(
        "关于{topic}，我想知道{question}"
    )

    # 把两个模板对象组合成聊天模板。
    chat_template = ChatPromptTemplate.from_messages([
        system_template,
        human_template
    ])

    print("当前模板由以下组件拼接而成：")
    print("  1. SystemMessagePromptTemplate")
    print("  2. HumanMessagePromptTemplate")
    print(f"\n自动汇总变量：{chat_template.input_variables}\n")

    # 注入变量。
    messages = chat_template.format_messages(
        profession="数据科学家",
        specialty="用数据讲故事",
        topic="数据可视化",
        question="如何选择合适的图表类型？"
    )

    # 调用模型。
    response = model.invoke(messages)
    print(f"AI 回复：{response.content[:200]}...\n")


# ============================================================================
# 示例 6：部分变量填充（Partial Variables）
# ============================================================================
def example_6_partial_variables():
    """
    partial 的作用：固定高频不变参数，减少每次调用传参。
    """
    print("\n" + "=" * 70)
    print("示例 6：部分变量填充（Partial Variables）")
    print("=" * 70)

    # 原始模板：需要 role、audience、task 三个变量。
    original_template = ChatPromptTemplate.from_messages([
        ("system", "你是一个{role}，你的目标读者是{audience}。"),
        ("user", "请{task}")
    ])

    print(f"原始模板需要变量：{original_template.input_variables}\n")

    # 预填充 role 和 audience。
    partially_filled = original_template.partial(
        role="科技博客作者",
        audience="前端程序员"
    )

    print(f"部分填充后，仅需提供：{partially_filled.input_variables}\n")

    # 第一次调用：只传 task。
    messages1 = partially_filled.format_messages(
        task="写一篇关于 Vue3 组合式 API 的文章开头"
    )

    response1 = model.invoke(messages1)
    print(f"文章 1：{response1.content[:150]}...\n")

    # 第二次调用：复用同一 partial 模板，换 task 即可。
    messages2 = partially_filled.format_messages(
        task="写一篇关于 TypeScript 泛型的文章开头"
    )

    response2 = model.invoke(messages2)
    print(f"文章 2：{response2.content[:150]}...\n")


# ============================================================================
# 示例 7：与 LCEL 链式调用（预览）
# ============================================================================
def example_7_lcel_chains():
    """
    LCEL 管道：template | model
    作用：把格式化与调用串起来，减少样板代码。
    """
    print("\n" + "=" * 70)
    print("示例 7：LCEL 链式调用（预览）")
    print("=" * 70)

    # 定义一个聊天模板。
    template = ChatPromptTemplate.from_messages([
        ("system", "你是一个{role}"),
        ("user", "{input}")
    ])

    # 通过 | 运算符把“模板输出”直接接到“模型输入”。
    chain = template | model

    print("链的组成：")
    print("  [模板 (Template)] -> | -> [模型 (LLM)]\n")

    # 调用链时直接传模板变量，无需手写 format_messages。
    response = chain.invoke({
        "role": "脱口秀演员",
        "input": "用一句话解释什么是 Bug"
    })

    # 输出最终内容。
    print(f"AI 回复：{response.content}\n")

    print("💡 链式调用的核心优势：")
    print("  1. 声明式写法，代码更简洁")
    print("  2. 组件可复用，便于扩展")
    print("  3. 后续可继续接输出解析器")


# ============================================================================
# 主程序
# ============================================================================
def main():
    """按顺序执行所有示例。"""
    # 打印章节标题。
    print("\n" + "=" * 70)
    print(" LangChain 1.0 基础教程 - 02 提示词模板")
    print("=" * 70)

    try:
        # 示例 1：为什么要模板。
        example_1_why_templates()
        input("\n[按 Enter 键继续查看下一个示例...]")

        # 示例 2：PromptTemplate 基础。
        example_2_prompt_template_basics()
        input("\n[按 Enter 键继续查看下一个示例...]")

        # 示例 3：ChatPromptTemplate。
        example_3_chat_prompt_template()
        input("\n[按 Enter 键继续查看下一个示例...]")

        # 示例 4：few-shot 对话模板。
        example_4_conversation_template()
        input("\n[按 Enter 键继续查看下一个示例...]")

        # 示例 5：MessagePromptTemplate 组合。
        example_5_message_templates()
        input("\n[按 Enter 键继续查看下一个示例...]")

        # 示例 6：partial 用法。
        example_6_partial_variables()
        input("\n[按 Enter 键继续查看下一个示例...]")

        # 示例 7：LCEL 管道。
        example_7_lcel_chains()

        # 打印完成提示。
        print("\n" + "=" * 70)
        print(" 🎉 所有示例运行完成！")
        print("=" * 70)
        print("\n本章技能树点亮：")
        print("  ✅ PromptTemplate 纯文本模板")
        print("  ✅ ChatPromptTemplate 角色消息模板")
        print("  ✅ Few-shot 模板预设")
        print("  ✅ Partial Variables")
        print("  ✅ LCEL 链式调用")

    except KeyboardInterrupt:
        # 用户中断时友好退出。
        print("\n\n⚠️ 程序已被用户手动中断")
    except Exception as e:
        # 打印详细异常信息。
        print(f"\n❌ 运行出错：{type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()


# 直接运行时执行主程序。
if __name__ == "__main__":
    main()
