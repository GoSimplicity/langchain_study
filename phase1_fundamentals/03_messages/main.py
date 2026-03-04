"""
03 - Message Types & Conversation Management: 消息类型与对话状态管理
"""

import os
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

# ============================================================================
# 环境配置与模型初始化
# ============================================================================

# 加载环境变量
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_API_BASE = os.getenv("OPENAI_API_BASE")
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "gpt-3.5-turbo")
MODEL_NAME = DEFAULT_MODEL if ":" in DEFAULT_MODEL else f"openai:{DEFAULT_MODEL}"

# 验证 API 密钥
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

# 全局初始化模型
model = init_chat_model(MODEL_NAME, api_key=OPENAI_API_KEY, base_url=OPENAI_API_BASE)


# ============================================================================
# 示例 1：三种核心消息类型对比
# ============================================================================
def example_1_message_types():
    """
    核心概念：SystemMessage, HumanMessage, AIMessage

    演示对象实例构建与原生字典构建的差异。在 LangChain 1.0 中，
    极其推荐使用字典格式，因为它与 OpenAI 接口原生对齐，且易于 JSON 序列化。
    """
    print("\n" + "=" * 70)
    print("示例 1：消息类型的两种构建范式对比")
    print("=" * 70)

    # 范式 1：使用 LangChain 原生对象 (强类型，但序列化略复杂)
    print("\n【范式 1：面向对象构建 (Message Objects)】")
    messages_obj = [
        SystemMessage(content="你是一个精通 Python 的技术专家。"),
        HumanMessage(content="什么是闭包 (Closure)？请用一句话解释。")
    ]
    response_obj = model.invoke(messages_obj)
    print(f"AI 回复: {response_obj.content}")

    # 范式 2：使用标准字典格式 (轻量，推荐，兼容性好)
    print("\n【范式 2：标准字典构建 (Dict Format - 生产环境推荐)】")
    messages_dict = [
        {"role": "system", "content": "你是一个精通 Python 的技术专家。"},
        {"role": "user", "content": "什么是闭包 (Closure)？请用一句话解释。"}
    ]
    response_dict = model.invoke(messages_dict)
    print(f"AI 回复: {response_dict.content}")

    print("\n💡 最佳实践：优先使用字典格式。不仅代码更紧凑，在保存至数据库或通过 API 传输时也无需额外序列化。")


# ============================================================================
# 示例 2：正确的对话状态管理
# ============================================================================
def example_2_conversation_history():
    """
    核心机制：LLM API 默认是无状态 (Stateless) 的。
    要实现“记忆”功能，客户端必须在每次调用时，将被模型生成的回复追加到历史中，
    并在下一次请求时将完整的上下文 (Context) 重新发送给模型。
    """
    print("\n" + "=" * 70)
    print("示例 2：正确的对话状态管理 (上下文传递)")
    print("=" * 70)

    # 初始化对话上下文
    conversation_context = [
        {"role": "system", "content": "你是一个简洁的助手，回答请限制在 50 字以内。"}
    ]

    # 第 1 轮对话
    print("\n【第 1 轮：建立初始信息】")
    user_msg_1 = {"role": "user", "content": "你好，我叫 Alice，我喜欢喝咖啡。"}
    conversation_context.append(user_msg_1)
    print(f"用户输入: {user_msg_1['content']}")

    response_1 = model.invoke(conversation_context)
    print(f"AI 回复: {response_1.content}")

    # 关键步骤：将 AI 的回复写入上下文历史
    conversation_context.append({"role": "assistant", "content": response_1.content})

    # 第 2 轮对话：验证记忆
    print("\n【第 2 轮：验证上下文记忆】")
    user_msg_2 = {"role": "user", "content": "如果我想送自己一份礼物，你建议送什么？基于我刚才说的喜好。"}
    conversation_context.append(user_msg_2)
    print(f"用户输入: {user_msg_2['content']}")

    response_2 = model.invoke(conversation_context)
    print(f"AI 回复: {response_2.content}")
    conversation_context.append({"role": "assistant", "content": response_2.content})

    print(f"\n💡 当前上下文窗口共维护了 {len(conversation_context)} 条消息，这就是 AI 产生“记忆”的原理。")
    """
    要明白一件事，大模型是无状态的，之所以能记住之前的对话完全是因为每次对话都把之前的历史对话全量发给了大模型
    但是大模型每一次回复都是全新的...
    """


# ============================================================================
# 示例 3：常见的无状态调用陷阱
# ============================================================================
def example_3_wrong_way():
    """
    反面教材：未维护上下文数组，导致模型产生“失忆”现象。
    """
    print("\n" + "=" * 70)
    print("示例 3：常见的无状态调用陷阱 (反面教材)")
    print("=" * 70)

    print("\n❌ 错误做法：独立发起 invoke，不传递历史消息")

    # 第一次独立调用
    response_1 = model.invoke("你好，我的主程序语言是 Golang。")
    print("用户: 你好，我的主程序语言是 Golang。")
    print(f"AI: {response_1.content}")

    # 第二次独立调用（未附带之前的上下文）
    response_2 = model.invoke("请给我推荐一个适合我的 Web 框架。")
    print("\n用户: 请给我推荐一个适合我的 Web 框架。")
    print(f"AI: {response_2.content}")

    print("\n⚠️ 观察结果：AI 并不知道你使用的是 Golang，因为后一次调用是全新的会话。")


# ============================================================================
# 示例 4：上下文滑动窗口截断机制
# ============================================================================
def example_4_optimize_history():
    """
    工程难点：随着对话进行，上下文越来越长，最终会触发大模型的 Token 限制。
    解决方案：滑动窗口 (Sliding Window) 策略，保留 System Prompt 和最近 N 轮对话。
    """
    print("\n" + "=" * 70)
    print("示例 4：上下文滑动窗口截断机制 (Token 优化)")
    print("=" * 70)

    def slide_window_history(messages, max_history_pairs=2):
        """
        截断历史消息，保留系统指令和最近的 `max_history_pairs` 轮对话。
        一轮对话 = 1 个 User 消息 + 1 个 Assistant 消息
        """
        # 提取固定在顶部的 System 消息
        system_msgs = [m for m in messages if m.get("role") == "system"]
        # 提取需要被截断的对话消息
        conversation_msgs = [m for m in messages if m.get("role") != "system"]

        # 计算最大保留的消息条数
        max_messages_to_keep = max_history_pairs * 2

        # 截取尾部消息
        recent_msgs = conversation_msgs[-max_messages_to_keep:] if len(
            conversation_msgs) > max_messages_to_keep else conversation_msgs

        # 拼接并返回：确保截断后第一条非 System 消息通常是 User (符合逻辑规范)
        return system_msgs + recent_msgs

    # 模拟一段超过 Token 限制的冗长对话
    mock_long_conversation = [
        {"role": "system", "content": "你是一个严格执行指令的 AI。"},
        {"role": "user", "content": "1+1等于几？"},
        {"role": "assistant", "content": "2"},
        {"role": "user", "content": "2+2等于几？"},
        {"role": "assistant", "content": "4"},
        {"role": "user", "content": "3+3等于几？"},
        {"role": "assistant", "content": "6"},
        {"role": "user", "content": "4+4等于几？"},
        {"role": "assistant", "content": "8"},
        {"role": "user", "content": "上面所有问题中，我问的第一个算式是什么？"},
    ]

    print(f"原始消息数组长度: {len(mock_long_conversation)}")

    # 执行截断，只保留最近 2 轮历史
    optimized_context = slide_window_history(mock_long_conversation, max_history_pairs=2)

    print(f"应用滑动窗口后的数组长度: {len(optimized_context)}")
    print("当前保留的内容结构:")
    for m in optimized_context:
        print(f"  [{m['role']}]: {m['content']}")

    # 调用模型（预期 AI 会回答不知道，因为它已经被截断了）
    response = model.invoke(optimized_context)
    print(f"\nAI 回复: {response.content}")

    print("\n💡 工程实践：生产环境中通常结合 Token 计算器（如 tiktoken）动态决定截断位置，而不是硬编码轮数。")


# ============================================================================
# 示例 5：实战 - 极简记忆聊天循环
# ============================================================================
def example_5_simple_chatbot():
    """
    实战应用：将上述概念整合，构建一个具备持续记忆能力的简易终端 Chatbot。
    """
    print("\n" + "=" * 70)
    print("示例 5：实战 - 极简记忆聊天流水线")
    print("=" * 70)

    # 1. 初始化系统上下文
    conversation_pipeline = [
        {"role": "system", "content": "你是一个幽默的朋友。你的回答通常很精炼，带点调侃。"}
    ]

    # 2. 预设用户输入流 (代替 input() 以实现自动化演示)
    mock_user_inputs = [
        "你好啊，我今天刚入职一家新公司当程序员",
        "我是写 Python 的，主要做后端",
        "考考你，我现在的心情大概是怎样的？",
        "嘿，你还记得我用什么语言开发吗？"
    ]

    # 3. 对话循环
    for i, user_text in enumerate(mock_user_inputs, 1):
        print(f"\n--- [对话轮次 {i}] ---")
        print(f"👤 用户: {user_text}")

        # 追加用户输入
        conversation_pipeline.append({"role": "user", "content": user_text})

        # 触发模型
        response = model.invoke(conversation_pipeline)
        print(f"🤖 AI: {response.content}")

        # 保存 AI 状态
        conversation_pipeline.append({"role": "assistant", "content": response.content})

    print(f"\n💡 流水线结束。最终 Context Window 载荷: {len(conversation_pipeline)} 条消息。")


# ============================================================================
# 主程序
# ============================================================================
def main():
    print("\n" + "=" * 70)
    print(" LangChain 1.0 基础教程 - 03 消息类型与对话状态管理")
    print("=" * 70)
    print(f"🔧 当前模型: {MODEL_NAME}")

    try:
        example_1_message_types()
        input("\n[按 Enter 键继续查看下一个示例...]")

        example_2_conversation_history()
        input("\n[按 Enter 键继续查看下一个示例...]")

        example_3_wrong_way()
        input("\n[按 Enter 键继续查看下一个示例...]")

        example_4_optimize_history()
        input("\n[按 Enter 键继续查看下一个示例...]")

        example_5_simple_chatbot()

        print("\n" + "=" * 70)
        print(" 🎉 本章所有示例执行完毕！")
        print("=" * 70)
        print("\n本章技能树点亮：")
        print("  ✅ 掌握原生字典格式的消息构建 (生产推荐)")
        print("  ✅ 理解大模型 API 的无状态 (Stateless) 特质")
        print("  ✅ 学会通过数组 Append 维护会话记忆 (Context Window)")
        print("  ✅ 掌握滑动窗口 (Sliding Window) 应对超长对话的截断策略")

    except KeyboardInterrupt:
        print("\n\n⚠️ 程序已被用户手动中断")
    except Exception as e:
        print(f"\n❌ 运行出错：{type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
