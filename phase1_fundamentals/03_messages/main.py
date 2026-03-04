"""
03 - Messages: 消息类型与对话状态管理

核心理解：模型本身不记忆，记忆来自你每次传入的 messages。
"""

import os
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_API_BASE = os.getenv("OPENAI_API_BASE")
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "gpt-3.5-turbo")
MODEL_NAME = DEFAULT_MODEL if ":" in DEFAULT_MODEL else f"openai:{DEFAULT_MODEL}"

if not OPENAI_API_KEY:
    raise ValueError("请在 .env 中配置 OPENAI_API_KEY")

model = init_chat_model(MODEL_NAME, api_key=OPENAI_API_KEY, base_url=OPENAI_API_BASE)


def example_1_message_types():
    """消息类型对比：对象 vs 字典"""
    print("\n" + "=" * 60)
    print("示例 1：消息类型的两种写法")
    print("=" * 60)

    # 对象格式
    print("\n【对象格式】")
    messages_obj = [
        SystemMessage(content="你是一个 Python 技术专家。"),
        HumanMessage(content="什么是闭包？请用一句话解释。")
    ]
    response_obj = model.invoke(messages_obj)
    print(f"AI 回复: {response_obj.content}")

    # 字典格式（生产推荐）
    print("\n【字典格式 - 生产推荐】")
    messages_dict = [
        {"role": "system", "content": "你是一个 Python 技术专家。"},
        {"role": "user", "content": "什么是闭包？请用一句话解释。"}
    ]
    response_dict = model.invoke(messages_dict)
    print(f"AI 回复: {response_dict.content}")

    print("\n💡 字典格式更易序列化和跨服务传输")


def example_2_conversation_history():
    """正确维护对话历史"""
    print("\n" + "=" * 60)
    print("示例 2：正确维护对话历史")
    print("=" * 60)

    conversation = [
        {"role": "system", "content": "你是一个简洁的助手，回答限制在 50 字以内。"}
    ]

    # 第 1 轮
    print("\n【第 1 轮】")
    conversation.append({"role": "user", "content": "你好，我叫 Alice，我喜欢喝咖啡。"})
    print(f"用户: {conversation[-1]['content']}")

    response_1 = model.invoke(conversation)
    print(f"AI: {response_1.content}")

    # 关键：把 AI 回复写回历史
    conversation.append({"role": "assistant", "content": response_1.content})

    # 第 2 轮
    print("\n【第 2 轮】")
    conversation.append({"role": "user", "content": "我想要一份礼物建议，基于我的喜好。"})
    print(f"用户: {conversation[-1]['content']}")

    response_2 = model.invoke(conversation)
    print(f"AI: {response_2.content}")

    conversation.append({"role": "assistant", "content": response_2.content})

    print(f"\n💡 当前上下文：{len(conversation)} 条消息")


def example_3_wrong_way():
    """反面教材：无状态调用"""
    print("\n" + "=" * 60)
    print("示例 3：反面教材 - 无状态调用")
    print("=" * 60)

    print("\n❌ 错误做法：每次独立调用，不带历史")

    response_1 = model.invoke("你好，我的主程序语言是 Golang。")
    print("用户: 你好，我的主程序语言是 Golang。")
    print(f"AI: {response_1.content}")

    response_2 = model.invoke("请给我推荐一个适合我的 Web 框架。")
    print("\n用户: 请给我推荐一个适合我的 Web 框架。")
    print(f"AI: {response_2.content}")

    print("\n⚠️ 模型不知道你提过 Golang，因为第二次调用没有历史")


def example_4_sliding_window():
    """滑动窗口截断历史"""
    print("\n" + "=" * 60)
    print("示例 4：滑动窗口截断")
    print("=" * 60)

    def slide_window(messages, max_pairs=2):
        """保留 system + 最近 N 轮对话"""
        system = [m for m in messages if m.get("role") == "system"]
        others = [m for m in messages if m.get("role") != "system"]
        recent = others[-(max_pairs * 2):] if len(others) > max_pairs * 2 else others
        return system + recent

    long_conversation = [
        {"role": "system", "content": "你是一个 AI。"},
        {"role": "user", "content": "1+1=?"},
        {"role": "assistant", "content": "2"},
        {"role": "user", "content": "2+2=?"},
        {"role": "assistant", "content": "4"},
        {"role": "user", "content": "3+3=?"},
        {"role": "assistant", "content": "6"},
        {"role": "user", "content": "我问的第一个算式是什么？"},
    ]

    print(f"原始消息：{len(long_conversation)} 条")

    optimized = slide_window(long_conversation, max_pairs=2)
    print(f"截断后：{len(optimized)} 条")

    print("保留内容：")
    for m in optimized:
        print(f"  [{m['role']}]: {m['content']}")

    response = model.invoke(optimized)
    print(f"\nAI 回复: {response.content}")


def example_5_simple_chatbot():
    """极简聊天流水线"""
    print("\n" + "=" * 60)
    print("示例 5：极简聊天流水线")
    print("=" * 60)

    conversation = [
        {"role": "system", "content": "你是一个幽默的朋友，回答精炼带点调侃。"}
    ]

    questions = [
        "你好，我今天刚入职当程序员",
        "我是写 Python 的，主要做后端",
        "猜猜我现在的心情？",
        "你还记得我用什么语言吗？"
    ]

    for i, question in enumerate(questions, 1):
        print(f"\n--- [轮次 {i}] ---")
        print(f"👤 用户: {question}")

        conversation.append({"role": "user", "content": question})
        response = model.invoke(conversation)
        print(f"🤖 AI: {response.content}")
        conversation.append({"role": "assistant", "content": response.content})

    print(f"\n💡 最终历史：{len(conversation)} 条消息")


def main():
    print("\n" + "=" * 60)
    print(" LangChain 1.0 - 03 消息与对话状态")
    print("=" * 60)
    print(f"🔧 模型: {MODEL_NAME}")

    try:
        example_1_message_types()
        input("\n[按 Enter 继续...]")
        example_2_conversation_history()
        input("\n[按 Enter 继续...]")
        example_3_wrong_way()
        input("\n[按 Enter 继续...]")
        example_4_sliding_window()
        input("\n[按 Enter 继续...]")
        example_5_simple_chatbot()

        print("\n" + "=" * 60)
        print(" 🎉 完成！")
        print("=" * 60)
        print("\n技能点亮：")
        print("  ✅ 消息格式与角色")
        print("  ✅ 无状态本质")
        print("  ✅ 历史维护")
        print("  ✅ 滑动窗口")

    except KeyboardInterrupt:
        print("\n\n程序已中断")
    except Exception as e:
        print(f"\n❌ 错误：{e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
