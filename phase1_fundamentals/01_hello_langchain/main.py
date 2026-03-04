"""
01 - Hello LangChain: 第一个 LLM 调用

核心概念：
- init_chat_model: 统一接口初始化模型（无需关心不同 provider）
- invoke: 触发一次同步调用
- 返回 AIMessage 对象，不是纯字符串
"""

import os
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, SystemMessage

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_API_BASE = os.getenv("OPENAI_API_BASE")
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "gpt-3.5-turbo")
MODEL_NAME = DEFAULT_MODEL if ":" in DEFAULT_MODEL else f"openai:{DEFAULT_MODEL}"

if not OPENAI_API_KEY:
    raise ValueError(
        "❌ 未找到 OPENAI_API_KEY！\n"
        "请在 .env 中配置：\n"
        "  OPENAI_API_KEY=sk-your_actual_key_here\n"
        "  OPENAI_API_BASE=https://api.openai.com/v1"
    )


def example_1_simple_invoke():
    """最简单的 LLM 调用"""
    print("\n" + "=" * 60)
    print("示例 1：最简单的 LLM 调用")
    print("=" * 60)

    model = init_chat_model(MODEL_NAME, api_key=OPENAI_API_KEY, base_url=OPENAI_API_BASE)

    user_input = "你好！请用一句话介绍什么是量子纠缠。"
    print(f"用户输入: {user_input}")

    response = model.invoke(user_input)

    print(f"AI 回复: {response.content}")
    print(f"\n💡 返回类型: {type(response).__name__}（不是字符串！）")


def example_2_messages():
    """使用消息对象构建对话"""
    print("\n" + "=" * 60)
    print("示例 2：消息对象构建对话")
    print("=" * 60)

    model = init_chat_model(MODEL_NAME, api_key=OPENAI_API_KEY, base_url=OPENAI_API_BASE)

    messages = [
        SystemMessage(content="你是一个友好的 Python 编程助手，擅长用简单易懂的方式解释概念。回答尽量简短。"),
        HumanMessage(content="什么是 Python 装饰器？"),
    ]

    print("系统提示:", messages[0].content[:50] + "...")
    print("用户问题:", messages[1].content)

    response = model.invoke(messages)
    print(f"\nAI 回复:\n{response.content}")

    # 关键：把 AI 回复追加到历史
    messages.append(response)
    messages.append(HumanMessage(content="能给我一个简单的代码例子吗？"))

    print("\n" + "-" * 60)
    print("继续对话（必须传入完整历史）...")
    print("用户追问:", messages[-1].content)

    response2 = model.invoke(messages)
    print(f"\nAI 回复:\n{response2.content}")


def example_3_dict_messages():
    """字典格式消息（生产环境推荐）"""
    print("\n" + "=" * 60)
    print("示例 3：字典格式消息（生产推荐）")
    print("=" * 60)

    model = init_chat_model(MODEL_NAME, api_key=OPENAI_API_KEY, base_url=OPENAI_API_BASE)

    messages = [
        {"role": "system", "content": "你是一个专业的数学老师。"},
        {"role": "user", "content": "什么是斐波那契数列？用一句话解释。"},
    ]

    print("消息列表:")
    for msg in messages:
        print(f"  [{msg['role']}]: {msg['content']}")

    response = model.invoke(messages)
    print(f"\nAI 回复:\n{response.content}")


def example_4_model_parameters():
    """Temperature 参数对比"""
    print("\n" + "=" * 60)
    print("示例 4：Temperature 参数对比")
    print("=" * 60)

    prompt = "写一个关于春天的四字成语。"
    print(f"提示词: {prompt}")

    # 低温度：稳定、一致
    model_deterministic = init_chat_model(
        MODEL_NAME, api_key=OPENAI_API_KEY, base_url=OPENAI_API_BASE,
        temperature=0.0, max_tokens=200,
    )

    print("\n[temperature=0.0 - 严谨模式]")
    for i in range(2):
        response = model_deterministic.invoke(prompt)
        print(f"  第 {i + 1} 次: {response.content}")

    # 高温度：发散、创造
    model_creative = init_chat_model(
        MODEL_NAME, api_key=OPENAI_API_KEY, base_url=OPENAI_API_BASE,
        temperature=1.2, max_tokens=200,
    )

    print("\n[temperature=1.2 - 创造模式]")
    for i in range(2):
        response = model_creative.invoke(prompt)
        print(f"  第 {i + 1} 次: {response.content}")


def example_5_response_structure():
    """理解返回值结构"""
    print("\n" + "=" * 60)
    print("示例 5：返回值结构解析")
    print("=" * 60)

    model = init_chat_model(MODEL_NAME, api_key=OPENAI_API_KEY, base_url=OPENAI_API_BASE)
    response = model.invoke("用一句话解释为什么天空是蓝色的。")

    print("1. 核心内容 (content):")
    print(f"   {response.content}\n")

    print("2. Token 消耗 (usage_metadata):")
    if response.usage_metadata:
        usage = response.usage_metadata
        print(f"   输入: {usage.get('input_tokens', 'N/A')} | 输出: {usage.get('output_tokens', 'N/A')} | 总计: {usage.get('total_tokens', 'N/A')}")

    print(f"\n3. 消息 ID: {response.id}")


def example_6_error_handling():
    """错误处理最佳实践"""
    print("\n" + "=" * 60)
    print("示例 6：错误处理")
    print("=" * 60)

    try:
        model = init_chat_model(
            MODEL_NAME,
            api_key=OPENAI_API_KEY,
            base_url=OPENAI_API_BASE,
            timeout=10,
        )
        response = model.invoke("测试连接。")
        print(f"✅ 成功！回复: {response.content}")

    except ValueError as e:
        print(f"❌ 配置错误: {e}")
    except ConnectionError as e:
        print(f"❌ 网络错误（检查 base_url 或代理）: {e}")
    except Exception as e:
        print(f"❌ 异常: {type(e).__name__}: {e}")


def main():
    print("\n" + "=" * 60)
    print(" LangChain 1.0 基础教程 - 第一个 LLM 调用")
    print("=" * 60)
    print(f"🔧 模型: {MODEL_NAME}")

    try:
        example_1_simple_invoke()
        example_2_messages()
        example_3_dict_messages()
        example_4_model_parameters()
        example_5_response_structure()
        example_6_error_handling()

        print("\n" + "=" * 60)
        print(" 🎉 所有示例运行完成！")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ 运行出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
