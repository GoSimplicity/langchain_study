"""
02 - Prompt Templates: 提示词模板

核心思维：把提示词当作可复用组件，而不是临时字符串。
"""

import os
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_API_BASE = os.getenv("OPENAI_API_BASE")
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "gpt-3.5-turbo")
MODEL_NAME = DEFAULT_MODEL if ":" in DEFAULT_MODEL else f"openai:{DEFAULT_MODEL}"

if not OPENAI_API_KEY:
    raise ValueError("请在 .env 中配置 OPENAI_API_KEY")

model = init_chat_model(MODEL_NAME, api_key=OPENAI_API_KEY, base_url=OPENAI_API_BASE)


def example_1_why_templates():
    """对比：字符串拼接 vs 模板"""
    print("\n" + "=" * 60)
    print("示例 1：为什么需要提示词模板？")
    print("=" * 60)

    topic = "Python"
    difficulty = "初学者"

    # 方式 1：字符串拼接（不推荐）
    print("\n【方式 1：字符串拼接】")
    prompt_str = f"你是一个{difficulty}级别的编程导师。请用简单易懂的语言解释{topic}。"
    print(f"提示词：{prompt_str}")
    response = model.invoke(prompt_str)
    print(f"AI 回复：{response.content[:100]}...\n")

    # 方式 2：模板化（推荐）
    print("【方式 2：PromptTemplate】")
    template = PromptTemplate.from_template(
        "你是一个{difficulty}级别的编程导师。请用简单易懂的语言解释{topic}。"
    )
    print(f"模板：{template.template}")
    print(f"变量：{template.input_variables}")

    prompt = template.format(difficulty=difficulty, topic=topic)
    print(f"生成的提示词：{prompt}")
    response = model.invoke(prompt)
    print(f"AI 回复：{response.content[:100]}...\n")

    print("💡 优势：可复用、可维护、可验证、可组合")


def example_2_prompt_template_basics():
    """PromptTemplate 基础用法"""
    print("\n" + "=" * 60)
    print("示例 2：PromptTemplate 基础")
    print("=" * 60)

    # 方法 1：from_template（最常用）
    print("\n【方法 1：from_template】")
    template = PromptTemplate.from_template("将以下文本翻译成{language}：\n{text}")
    prompt = template.format(language="法语", text="Hello, how are you?")
    print(f"生成的提示词：\n{prompt}\n")

    # 方法 2：显式声明变量
    print("【方法 2：显式指定变量】")
    template2 = PromptTemplate(
        input_variables=["product", "feature"],
        template="为{product}写一句广告语，重点突出{feature}特点。"
    )
    prompt2 = template2.format(product="智能手表", feature="超长续航")
    print(f"生成的提示词：{prompt2}")


def example_3_chat_prompt_template():
    """ChatPromptTemplate - 聊天消息模板"""
    print("\n" + "=" * 60)
    print("示例 3：ChatPromptTemplate")
    print("=" * 60)

    # 元组写法（推荐）
    chat_template = ChatPromptTemplate.from_messages([
        ("system", "你是一个{role}，擅长{expertise}。"),
        ("user", "请帮我{task}")
    ])

    print(f"模板变量：{chat_template.input_variables}")

    messages = chat_template.format_messages(
        role="Python 导师",
        expertise="用简单方式解释复杂概念",
        task="解释什么是列表推导式"
    )

    print("\n生成的消息：")
    for msg in messages:
        print(f"  [{msg.type.capitalize()}]: {msg.content}")

    response = model.invoke(messages)
    print(f"\nAI 回复：{response.content[:150]}...")


def example_4_conversation_template():
    """多轮对话模板（Few-shot）"""
    print("\n" + "=" * 60)
    print("示例 4：Few-shot 对话模板")
    print("=" * 60)

    template = ChatPromptTemplate.from_messages([
        ("system", "你是一个{role}。{instruction}"),
        ("user", "{question1}"),
        ("assistant", "{answer1}"),  # 预设示例
        ("user", "{question2}")      # 当前问题
    ])

    messages = template.format_messages(
        role="Python 专家",
        instruction="回答要简洁、准确",
        question1="什么是列表？",
        answer1="列表是 Python 中的有序可变集合，用方括号 [] 表示。",
        question2="它和元组有什么区别？"
    )

    print("完整对话流：")
    for i, msg in enumerate(messages, 1):
        print(f"  {i}. [{msg.type}] {msg.content[:50]}...")

    response = model.invoke(messages)
    print(f"\nAI 回复：{response.content}")


def example_5_partial_variables():
    """部分变量填充"""
    print("\n" + "=" * 60)
    print("示例 5：Partial Variables")
    print("=" * 60)

    template = ChatPromptTemplate.from_messages([
        ("system", "你是一个{role}，目标读者是{audience}。"),
        ("user", "请{task}")
    ])

    print(f"原始模板变量：{template.input_variables}")

    # 预填充 role 和 audience
    partial = template.partial(role="科技博客作者", audience="前端程序员")
    print(f"部分填充后：{partial.input_variables}")

    # 多次调用只需传 task
    messages1 = partial.format_messages(task="写一篇 Vue3 组合式 API 的文章开头")
    response1 = model.invoke(messages1)
    print(f"\n文章 1：{response1.content[:100]}...")

    messages2 = partial.format_messages(task="写一篇 TypeScript 泛型的文章开头")
    response2 = model.invoke(messages2)
    print(f"文章 2：{response2.content[:100]}...")


def example_6_lcel_chains():
    """LCEL 链式调用"""
    print("\n" + "=" * 60)
    print("示例 6：LCEL 链式调用")
    print("=" * 60)

    template = ChatPromptTemplate.from_messages([
        ("system", "你是一个{role}"),
        ("user", "{input}")
    ])

    # 管道操作符连接模板和模型
    chain = template | model

    print("链结构：[Template] -> | -> [Model]")

    response = chain.invoke({
        "role": "脱口秀演员",
        "input": "用一句话解释什么是 Bug"
    })

    print(f"\nAI 回复：{response.content}")


def main():
    print("\n" + "=" * 60)
    print(" LangChain 1.0 - 02 提示词模板")
    print("=" * 60)

    try:
        example_1_why_templates()
        input("\n[按 Enter 继续...]")
        example_2_prompt_template_basics()
        input("\n[按 Enter 继续...]")
        example_3_chat_prompt_template()
        input("\n[按 Enter 继续...]")
        example_4_conversation_template()
        input("\n[按 Enter 继续...]")
        example_5_partial_variables()
        input("\n[按 Enter 继续...]")
        example_6_lcel_chains()

        print("\n" + "=" * 60)
        print(" 🎉 完成！")
        print("=" * 60)
        print("\n技能点亮：")
        print("  ✅ PromptTemplate")
        print("  ✅ ChatPromptTemplate")
        print("  ✅ Few-shot 模板")
        print("  ✅ Partial Variables")
        print("  ✅ LCEL 链式调用")

    except KeyboardInterrupt:
        print("\n\n程序已中断")
    except Exception as e:
        print(f"\n❌ 错误：{e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
