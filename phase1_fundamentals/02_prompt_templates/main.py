"""
02 - Prompt Templates: 提示词模板
"""

import os
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from langchain_core.prompts import (
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)

# ============================================================================
# 环境配置与模型初始化
# ============================================================================

# 加载环境变量
load_dotenv()

# 读取配置项
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_API_BASE = os.getenv("OPENAI_API_BASE")
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "gpt-3.5-turbo")
MODEL_NAME = DEFAULT_MODEL if ":" in DEFAULT_MODEL else f"openai:{DEFAULT_MODEL}"

# 验证 API 密钥是否存在
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

if not OPENAI_API_BASE and not OPENAI_API_KEY.startswith("sk-"):
    print("\n⚠️  警告：你的 OPENAI_API_KEY 格式可能不正确，请确保配置了正确的密钥或 BASE_URL\n")

# 全局初始化模型 (因为本章节重点在于模板，无需在每个示例中重复配置模型参数)
model = init_chat_model(MODEL_NAME, api_key=OPENAI_API_KEY, base_url=OPENAI_API_BASE)


# ============================================================================
# 示例 1：为什么需要提示词模板？
# ============================================================================
def example_1_why_templates():
    """
    示例1：对比字符串拼接 vs 模板

    问题：字符串拼接容易出错、难维护、不可复用
    解决：使用提示词模板 (Prompt Templates)
    """
    print("\n" + "=" * 70)
    print("示例 1：为什么需要提示词模板？")
    print("=" * 70)

    # ❌ 不推荐：使用字符串拼接
    print("\n【方式 1：字符串拼接（不推荐）】")
    print("-" * 70)

    topic = "Python"
    difficulty = "初学者"

    # 难以维护，容易出错
    prompt_str = f"你是一个{difficulty}级别的编程导师。请用简单易懂的语言解释{topic}。"
    print(f"提示词：{prompt_str}")

    response = model.invoke(prompt_str)
    print(f"AI 回复：{response.content[:100]}...\n")

    # ✅ 推荐：使用 PromptTemplate
    print("【方式 2：使用 PromptTemplate（推荐）】")
    print("-" * 70)

    # 创建可复用的模板
    template = PromptTemplate.from_template(
        "你是一个{difficulty}级别的编程导师。请用简单易懂的语言解释{topic}。"
    )

    print(f"模板：{template.template}")
    print(f"变量：{template.input_variables}")

    # 使用模板生成提示词
    prompt = template.format(difficulty=difficulty, topic=topic)
    print(f"生成的提示词：{prompt}")

    response = model.invoke(prompt)
    print(f"AI 回复：{response.content[:100]}...\n")

    print("💡 优势：")
    print("  1. 可复用 - 同一个模板可以用于不同的输入")
    print("  2. 可维护 - 模板和数据分离，易于统一修改")
    print("  3. 类型安全 - 自动验证传入变量是否完整")
    print("  4. 易于集成 - 可以无缝接入 LangChain 的链式调用")


# ============================================================================
# 示例 2：PromptTemplate 基础用法
# ============================================================================
def example_2_prompt_template_basics():
    """
    示例2：PromptTemplate 的基本用法

    PromptTemplate 主要用于生成纯文本(String)格式的提示词。
    适合简单指令、补全任务或单次问答。
    """
    print("\n" + "=" * 70)
    print("示例 2：PromptTemplate 基础用法")
    print("=" * 70)

    # 方法 1：使用 from_template（最简单推荐）
    print("\n【方法 1：from_template（推荐）】")
    template1 = PromptTemplate.from_template(
        "将以下文本翻译成{language}：\n{text}"
    )

    prompt1 = template1.format(language="法语", text="Hello, how are you?")
    print(f"生成的提示词：\n{prompt1}\n")

    response1 = model.invoke(prompt1)
    print(f"AI 回复：{response1.content}\n")

    # 方法 2：显式指定变量（更严格，适合需要提前声明接口的场景）
    print("【方法 2：显式指定变量】")
    template2 = PromptTemplate(
        input_variables=["product", "feature"],
        template="为{product}写一句广告语，重点突出{feature}特点。"
    )

    prompt2 = template2.format(product="智能手表", feature="超长续航")
    print(f"生成的提示词：\n{prompt2}\n")

    response2 = model.invoke(prompt2)
    print(f"AI 回复：{response2.content}\n")

    # 方法 3：使用 invoke（直接生成 StringPromptValue 对象）
    print("【方法 3：使用 invoke（更方便）】")
    template3 = PromptTemplate.from_template(
        "写一首关于{theme}的{style}风格的诗，不超过4行。"
    )

    # invoke 直接返回格式化后的 PromptValue 对象
    prompt_value = template3.invoke({"theme": "春天", "style": "现代"})
    print(f"生成的提示词：\n{prompt_value.text}\n")


# ============================================================================
# 示例 3：ChatPromptTemplate - 聊天消息模板
# ============================================================================
def example_3_chat_prompt_template():
    """
    示例3：ChatPromptTemplate 的基本用法

    ChatPromptTemplate 用于构建结构化的聊天消息列表(Messages)。
    完美契合现代 LLM 的 System、User、Assistant 角色分离架构。
    """
    print("\n" + "=" * 70)
    print("示例 3：ChatPromptTemplate - 聊天消息模板")
    print("=" * 70)

    # 方法 1：使用元组格式（最简单，强烈推荐）
    print("\n【方法 1：元组格式（推荐）】")

    chat_template = ChatPromptTemplate.from_messages([
        ("system", "你是一个{role}，擅长{expertise}。"),
        ("user", "请帮我{task}")
    ])

    print(f"模板提取的变量：{chat_template.input_variables}")

    # 格式化模板
    messages = chat_template.format_messages(
        role="Python 导师",
        expertise="用简单的方式解释复杂概念",
        task="解释什么是列表推导式"
    )

    print("\n生成的消息对象：")
    for msg in messages:
        print(f"  [{msg.type.capitalize()}]: {msg.content}")

    response = model.invoke(messages)
    print(f"\nAI 回复：{response.content[:150]}...\n")

    # 方法 2：使用字符串简写（最简洁）
    print("【方法 2：单字符串自动转 User Message】")

    simple_template = ChatPromptTemplate.from_messages([
        ("system", "你是一个友好的助手"),
        ("user", "{question}")
    ])

    messages = simple_template.format_messages(question="什么是机器学习？")
    response = model.invoke(messages)
    print(f"AI 回复：{response.content[:100]}...\n")


# ============================================================================
# 示例 4：多轮对话模板
# ============================================================================
def example_4_conversation_template():
    """
    示例4：构建多轮对话的模板

    可以预设系统提示、Few-shot(少样本)历史和当前问题
    """
    print("\n" + "=" * 70)
    print("示例 4：多轮对话预设模板 (Few-shot 演示)")
    print("=" * 70)

    # 创建包含对话历史的模板
    template = ChatPromptTemplate.from_messages([
        ("system", "你是一个{role}。{instruction}"),
        ("user", "{question1}"),
        ("assistant", "{answer1}"),
        ("user", "{question2}")
    ])

    print("模板结构设计：")
    print("  1. System: 设定角色和行为指令")
    print("  2. User: 模拟的第一个问题 (Few-shot)")
    print("  3. Assistant: 模拟的第一个回答 (Few-shot)")
    print("  4. User: 用户的真实提问（基于上下文）\n")

    # 填充模板
    messages = template.format_messages(
        role="Python 专家",
        instruction="回答要简洁、准确，不废话",
        question1="什么是列表？",
        answer1="列表是 Python 中的有序可变集合，用方括号 [] 表示。",
        question2="它和元组有什么区别？"  # 基于上下文的问题
    )

    print("生成的完整对话流：")
    for i, msg in enumerate(messages, 1):
        content_preview = msg.content[:60] + "..." if len(msg.content) > 60 else msg.content
        print(f"  {i}. [{msg.type}] {content_preview}")

    response = model.invoke(messages)
    print(f"\nAI 回复：{response.content}\n")


# ============================================================================
# 示例 5：使用 MessagePromptTemplate（高级）
# ============================================================================
def example_5_message_templates():
    """
    示例5：使用具体的 MessagePromptTemplate 类

    这是 `from_messages` 底层实际使用的类，适用于需要对特定消息层级
    进行极细粒度控制或对象组装的场景。
    """
    print("\n" + "=" * 70)
    print("示例 5：MessagePromptTemplate 类（面向对象高级用法）")
    print("=" * 70)

    # 分别创建不同类型的消息模板对象
    system_template = SystemMessagePromptTemplate.from_template(
        "你是一个{profession}，你的特长是{specialty}。"
    )

    human_template = HumanMessagePromptTemplate.from_template(
        "关于{topic}，我想知道{question}"
    )

    # 组合成完整的 ChatPromptTemplate
    chat_template = ChatPromptTemplate.from_messages([
        system_template,
        human_template
    ])

    print("当前模板由以下组件拼接而成：")
    print(f"  1. SystemMessagePromptTemplate")
    print(f"  2. HumanMessagePromptTemplate")
    print(f"\n自动汇总的全部变量：{chat_template.input_variables}\n")

    # 使用模板
    messages = chat_template.format_messages(
        profession="数据科学家",
        specialty="用数据讲故事",
        topic="数据可视化",
        question="如何选择合适的图表类型？"
    )

    response = model.invoke(messages)
    print(f"AI 回复：{response.content[:200]}...\n")


# ============================================================================
# 示例 6：部分变量填充（Partial Variables）
# ============================================================================
def example_6_partial_variables():
    """
    示例6：部分变量 - 预填充某些变量

    适用场景：
    - 某些变量在初始化时就已经确定（如当前时间、固定角色等）
    - 避免每次调用都传递重复的参数
    """
    print("\n" + "=" * 70)
    print("示例 6：部分变量填充（Partial Variables）")
    print("=" * 70)

    # 创建原始模板
    original_template = ChatPromptTemplate.from_messages([
        ("system", "你是一个{role}，你的目标读者是{audience}。"),
        ("user", "请{task}")
    ])

    print(f"原始模板需要变量：{original_template.input_variables}\n")

    # 柯里化：部分填充固定 role 和 audience
    partially_filled = original_template.partial(
        role="科技博客作者",
        audience="前端程序员"
    )

    print(f"部分填充后，仅需提供：{partially_filled.input_variables}\n")

    # 调用 1：现在只需要提供 task
    messages1 = partially_filled.format_messages(
        task="写一篇关于 Vue3 组合式 API 的文章开头"
    )

    response1 = model.invoke(messages1)
    print(f"文章 1：{response1.content[:150]}...\n")

    # 调用 2：复用预填充模板，执行不同 task
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
    示例7：模板 + 模型的链式调用

    LangChain 表达式语言 (LCEL) 使得组件组合变得极其自然。
    """
    print("\n" + "=" * 70)
    print("示例 7：LCEL 链式调用（预览）")
    print("=" * 70)

    # 创建模板
    template = ChatPromptTemplate.from_messages([
        ("system", "你是一个{role}"),
        ("user", "{input}")
    ])

    # 使用 | 运算符创建处理链 (Pipeline)
    chain = template | model

    print("链的组成：")
    print("  [模板 (Template)] -> | -> [模型 (LLM)]\n")

    # 直接调用链 (无需手动调用 template.format_messages)
    response = chain.invoke({
        "role": "脱口秀演员",
        "input": "用一句话解释什么是 Bug"
    })

    print(f"AI 回复：{response.content}\n")

    print("💡 链式调用的核心优势：")
    print("  1. 声明式语法，代码极致简洁")
    print("  2. 组件即插即用，天然支持异步与流式输出 (Streaming)")
    print("  3. 易于扩展（比如继续用 | 连接输出解析器）")
    print("  （详细 LCEL 语法将在后续高级模块深入学习）")


# ============================================================================
# 主程序
# ============================================================================
def main():
    """运行所有示例"""
    print("\n" + "=" * 70)
    print(" LangChain 1.0 基础教程 - 02 提示词模板")
    print("=" * 70)

    try:
        example_1_why_templates()
        input("\n[按 Enter 键继续查看下一个示例...]")

        example_2_prompt_template_basics()
        input("\n[按 Enter 键继续查看下一个示例...]")

        example_3_chat_prompt_template()
        input("\n[按 Enter 键继续查看下一个示例...]")

        example_4_conversation_template()
        input("\n[按 Enter 键继续查看下一个示例...]")

        example_5_message_templates()
        input("\n[按 Enter 键继续查看下一个示例...]")

        example_6_partial_variables()
        input("\n[按 Enter 键继续查看下一个示例...]")

        example_7_lcel_chains()

        print("\n" + "=" * 70)
        print(" 🎉 所有示例运行完成！")
        print("=" * 70)
        print("\n本章技能树点亮：")
        print("  ✅ 掌握 PromptTemplate 纯文本模板")
        print("  ✅ 精通 ChatPromptTemplate 角色消息模板")
        print("  ✅ 掌握多轮对话 (Few-shot) 的模板预设")
        print("  ✅ 学会 Partial Variables 部分变量填充")
        print("  ✅ 体验 LCEL 链式调用的丝滑语法")
        print("\n下一步探索：")
        print("  - 03_messages: 深入理解消息类型")
        print("  - 04_output_parsers: 解析模型输出结构化数据")

    except KeyboardInterrupt:
        print("\n\n⚠️ 程序已被用户手动中断")
    except Exception as e:
        print(f"\n❌ 运行出错：{type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
