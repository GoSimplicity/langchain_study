"""
03 - Message Types & Conversation Management: 消息类型与对话状态管理
"""

# 标准库：读取环境变量。
import os

# .env 加载工具。
from dotenv import load_dotenv
# 模型初始化接口。
from langchain.chat_models import init_chat_model
# 消息对象类（用于演示对象格式）。
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

# ============================= 学习说明 =============================
# 本章请重点看“conversation 列表是如何增量维护的”。
# 这比具体提示词内容更重要。
# ==================================================================

# ============================================================================
# 环境配置与模型初始化
# ============================================================================

# 读取 .env 文件。
load_dotenv()

# 读取 API key。
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# 读取 API base。
OPENAI_API_BASE = os.getenv("OPENAI_API_BASE")
# 读取默认模型。
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "gpt-3.5-turbo")
# 自动补全 provider 前缀。
MODEL_NAME = DEFAULT_MODEL if ":" in DEFAULT_MODEL else f"openai:{DEFAULT_MODEL}"

# 检查 key 是否有效。
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

# key 格式可疑且未配置 base_url 时给提醒。
if not OPENAI_API_BASE and not OPENAI_API_KEY.startswith("sk-"):
    print("\n⚠️  警告：你的 OPENAI_API_KEY 格式可能不正确，请确保配置了正确的密钥或 BASE_URL\n")

# 初始化全局模型，所有示例共享。
model = init_chat_model(MODEL_NAME, api_key=OPENAI_API_KEY, base_url=OPENAI_API_BASE)


# ============================================================================
# 示例 1：三种核心消息类型对比
# ============================================================================
def example_1_message_types():
    """
    核心概念：SystemMessage, HumanMessage, AIMessage

    目标：对比对象格式和字典格式。
    """
    print("\n" + "=" * 70)
    print("示例 1：消息类型的两种构建范式对比")
    print("=" * 70)

    # ---------- 范式 1：对象格式 ----------
    print("\n【范式 1：面向对象构建 (Message Objects)】")
    # 创建对象消息列表。
    messages_obj = [
        SystemMessage(content="你是一个精通 Python 的技术专家。"),
        HumanMessage(content="什么是闭包 (Closure)？请用一句话解释。")
    ]
    # 调用模型。
    response_obj = model.invoke(messages_obj)
    print(f"AI 回复: {response_obj.content}")

    # ---------- 范式 2：字典格式 ----------
    print("\n【范式 2：标准字典构建 (Dict Format - 生产环境推荐)】")
    # 创建字典消息列表。
    messages_dict = [
        {"role": "system", "content": "你是一个精通 Python 的技术专家。"},
        {"role": "user", "content": "什么是闭包 (Closure)？请用一句话解释。"}
    ]
    # 调用模型。
    response_dict = model.invoke(messages_dict)
    print(f"AI 回复: {response_dict.content}")

    print("\n💡 最佳实践：优先字典格式，序列化和跨服务传输更轻量。")


# ============================================================================
# 示例 2：正确的对话状态管理
# ============================================================================
def example_2_conversation_history():
    """
    展示“正确维护历史”的标准流程。
    """
    print("\n" + "=" * 70)
    print("示例 2：正确的对话状态管理 (上下文传递)")
    print("=" * 70)

    # 初始化上下文列表，先放 system。
    conversation_context = [
        {"role": "system", "content": "你是一个简洁的助手，回答请限制在 50 字以内。"}
    ]

    # 第 1 轮：用户输入。
    print("\n【第 1 轮：建立初始信息】")
    user_msg_1 = {"role": "user", "content": "你好，我叫 Alice，我喜欢喝咖啡。"}
    conversation_context.append(user_msg_1)
    print(f"用户输入: {user_msg_1['content']}")

    # 把完整上下文发给模型。
    response_1 = model.invoke(conversation_context)
    print(f"AI 回复: {response_1.content}")

    # 把 AI 回复写回历史（关键步骤）。
    conversation_context.append({"role": "assistant", "content": response_1.content})

    # 第 2 轮：基于前文继续追问。
    print("\n【第 2 轮：验证上下文记忆】")
    user_msg_2 = {"role": "user", "content": "如果我想送自己一份礼物，你建议送什么？基于我刚才说的喜好。"}
    conversation_context.append(user_msg_2)
    print(f"用户输入: {user_msg_2['content']}")

    # 再次调用（携带完整历史）。
    response_2 = model.invoke(conversation_context)
    print(f"AI 回复: {response_2.content}")

    # 继续把 AI 回复写回历史，形成可持续会话。
    conversation_context.append({"role": "assistant", "content": response_2.content})

    # 打印历史长度，帮助理解“记忆”来源。
    print(f"\n💡 当前上下文窗口共维护了 {len(conversation_context)} 条消息。")


# ============================================================================
# 示例 3：常见的无状态调用陷阱
# ============================================================================
def example_3_wrong_way():
    """
    反例：每次独立 invoke，不传历史。
    """
    print("\n" + "=" * 70)
    print("示例 3：常见的无状态调用陷阱 (反面教材)")
    print("=" * 70)

    print("\n❌ 错误做法：独立发起 invoke，不传递历史消息")

    # 第一次调用（独立上下文）。
    response_1 = model.invoke("你好，我的主程序语言是 Golang。")
    print("用户: 你好，我的主程序语言是 Golang。")
    print(f"AI: {response_1.content}")

    # 第二次调用（仍是独立上下文）。
    response_2 = model.invoke("请给我推荐一个适合我的 Web 框架。")
    print("\n用户: 请给我推荐一个适合我的 Web 框架。")
    print(f"AI: {response_2.content}")

    print("\n⚠️ 观察：第二次调用没有第一轮历史，模型不知道你提过 Golang。")


# ============================================================================
# 示例 4：上下文滑动窗口截断机制
# ============================================================================
def example_4_optimize_history():
    """
    展示滑动窗口策略：保留 system + 最近 N 轮。
    """
    print("\n" + "=" * 70)
    print("示例 4：上下文滑动窗口截断机制 (Token 优化)")
    print("=" * 70)

    # 定义一个历史截断函数。
    def slide_window_history(messages, max_history_pairs=2):
        """
        保留 system 消息 + 最近 max_history_pairs 轮。
        一轮 = user + assistant（2 条消息）
        """
        # 先分离 system。
        system_msgs = [m for m in messages if m.get("role") == "system"]
        # 再拿到普通对话消息。
        conversation_msgs = [m for m in messages if m.get("role") != "system"]

        # 计算最多保留多少条普通消息。
        max_messages_to_keep = max_history_pairs * 2

        # 从尾部截取最近消息。
        recent_msgs = conversation_msgs[-max_messages_to_keep:] if len(conversation_msgs) > max_messages_to_keep else conversation_msgs

        # 拼回新历史并返回。
        return system_msgs + recent_msgs

    # 构造一段较长消息历史。
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

    # 打印截断前长度。
    print(f"原始消息数组长度: {len(mock_long_conversation)}")

    # 执行截断，仅保留最近 2 轮。
    optimized_context = slide_window_history(mock_long_conversation, max_history_pairs=2)

    # 打印截断后长度。
    print(f"应用滑动窗口后的数组长度: {len(optimized_context)}")
    print("当前保留的内容结构:")
    for m in optimized_context:
        print(f"  [{m['role']}]: {m['content']}")

    # 用截断后的上下文调用模型。
    response = model.invoke(optimized_context)
    print(f"\nAI 回复: {response.content}")

    print("\n💡 生产环境通常结合 token 计算动态截断，而非固定轮数。")


# ============================================================================
# 示例 5：实战 - 极简记忆聊天循环
# ============================================================================
def example_5_simple_chatbot():
    """
    把“历史维护”落地到一个可执行的简易聊天流程。
    """
    print("\n" + "=" * 70)
    print("示例 5：实战 - 极简记忆聊天流水线")
    print("=" * 70)

    # 初始化系统消息。
    conversation_pipeline = [
        {"role": "system", "content": "你是一个幽默的朋友。你的回答通常很精炼，带点调侃。"}
    ]

    # 预置四条用户输入（便于非交互演示）。
    mock_user_inputs = [
        "你好啊，我今天刚入职一家新公司当程序员",
        "我是写 Python 的，主要做后端",
        "考考你，我现在的心情大概是怎样的？",
        "嘿，你还记得我用什么语言开发吗？"
    ]

    # 遍历每条输入，模拟多轮对话。
    for i, user_text in enumerate(mock_user_inputs, 1):
        print(f"\n--- [对话轮次 {i}] ---")
        print(f"👤 用户: {user_text}")

        # 追加当前轮用户消息。
        conversation_pipeline.append({"role": "user", "content": user_text})

        # 调用模型（携带完整历史）。
        response = model.invoke(conversation_pipeline)
        print(f"🤖 AI: {response.content}")

        # 保存 AI 回复。
        conversation_pipeline.append({"role": "assistant", "content": response.content})

    # 打印最终历史长度。
    print(f"\n💡 流水线结束。最终 Context Window 载荷: {len(conversation_pipeline)} 条消息。")


# ============================================================================
# 主程序
# ============================================================================
def main():
    """按顺序运行本章所有示例。"""
    # 打印章节标题。
    print("\n" + "=" * 70)
    print(" LangChain 1.0 基础教程 - 03 消息类型与对话状态管理")
    print("=" * 70)
    # 打印当前模型。
    print(f"🔧 当前模型: {MODEL_NAME}")

    try:
        # 示例 1：消息格式对比。
        example_1_message_types()
        input("\n[按 Enter 键继续查看下一个示例...]")

        # 示例 2：正确历史维护。
        example_2_conversation_history()
        input("\n[按 Enter 键继续查看下一个示例...]")

        # 示例 3：错误反例。
        example_3_wrong_way()
        input("\n[按 Enter 键继续查看下一个示例...]")

        # 示例 4：历史截断。
        example_4_optimize_history()
        input("\n[按 Enter 键继续查看下一个示例...]")

        # 示例 5：综合实战。
        example_5_simple_chatbot()

        # 打印完成信息。
        print("\n" + "=" * 70)
        print(" 🎉 本章所有示例执行完毕！")
        print("=" * 70)
        print("\n本章技能树点亮：")
        print("  ✅ 消息格式与角色职责")
        print("  ✅ Stateless 本质")
        print("  ✅ 上下文历史维护")
        print("  ✅ 滑动窗口优化")

    except KeyboardInterrupt:
        # 用户主动中断。
        print("\n\n⚠️ 程序已被用户手动中断")
    except Exception as e:
        # 打印详细异常。
        print(f"\n❌ 运行出错：{type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()


# 直接运行脚本时进入 main。
if __name__ == "__main__":
    main()
