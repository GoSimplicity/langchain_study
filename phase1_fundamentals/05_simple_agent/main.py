"""
05 - Simple Agent: 赋予大模型行动力
"""

import os
import sys
from typing import Optional

# Windows 终端编码支持
if sys.platform == 'win32':
    import io

    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.tools import tool
from langchain.agents import create_agent

# ============================================================================
# 环境配置与模型初始化
# ============================================================================

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_API_BASE = os.getenv("OPENAI_API_BASE")
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "gpt-3.5-turbo")
MODEL_NAME = DEFAULT_MODEL if ":" in DEFAULT_MODEL else f"openai:{DEFAULT_MODEL}"

if not OPENAI_API_KEY or OPENAI_API_KEY == "your_openai_api_key_here_replace_this":
    raise ValueError(
        "\n" + "=" * 70 + "\n"
                          "❌ 错误：未找到有效的 OPENAI_API_KEY 环境变量！\n"
                          "=" * 70 + "\n"
                                     "请在 .env 文件中填入你的配置\n"
                                     "=" * 70
    )

if not OPENAI_API_BASE and not OPENAI_API_KEY.startswith("sk-"):
    print("\n⚠️  警告：你的 OPENAI_API_KEY 格式可能不正确，请确保配置了正确的密钥或 BASE_URL\n")

# 全局初始化模型
model = init_chat_model(MODEL_NAME, api_key=OPENAI_API_KEY, base_url=OPENAI_API_BASE)


# ============================================================================
# 工具定义区 (内联以保证开箱即用)
# ============================================================================

@tool
def get_weather(city: str) -> str:
    """获取指定城市的当前天气情况。"""
    mock_weather_db = {
        "北京": "晴朗，气温 22°C，适合户外活动",
        "上海": "多云，气温 26°C，湿度较高"
    }
    return mock_weather_db.get(city, f"暂无 {city} 的天气数据。")


@tool
def calculator(operation: str, a: float, b: float) -> str:
    """执行基础的数学运算。支持: 'add', 'subtract', 'multiply', 'divide'。"""
    try:
        if operation == "add":
            return str(a + b)
        elif operation == "subtract":
            return str(a - b)
        elif operation == "multiply":
            return str(a * b)
        elif operation == "divide":
            return str(a / b)
        else:
            return f"不支持的运算: {operation}"
    except Exception as e:
        return f"计算出错: {str(e)}"


@tool
def web_search(query: str, num_results: Optional[int] = 3) -> str:
    """在互联网上搜索指定关键词。"""
    return f"检索 '{query}' 成功。共返回了 {num_results} 条模拟搜索结果。"


# ============================================================================
# 示例 1：创建第一个 Agent
# ============================================================================
def example_1_basic_agent():
    """
    核心概念：基础智能体的构建
    通过 `create_agent` 注入模型与工具，智能体会自动接管决策流。
    """
    print("\n" + "=" * 70)
    print("示例 1：创建第一个智能体 (Agent)")
    print("=" * 70)

    # 构建 Agent 状态图
    agent = create_agent(
        model=model,
        tools=[get_weather]  # 当前只挂载一个天气工具
    )

    print("✅ Agent 构建成功！挂载工具：[get_weather]")

    # 场景 A：需要触发工具的提问
    print("\n[测试 A：需要调用工具的提问]")
    response_a = agent.invoke({
        "messages": [{"role": "user", "content": "北京今天天气怎么样？"}]
    })
    # Agent 返回的是包含完整对话历史的字典，最终回复在最后一条消息中
    print(f"🤖 Agent 最终回复：{response_a['messages'][-1].content}")

    # 场景 B：无需触发工具的闲聊提问
    print("\n[测试 B：常规对话提问 (无需工具)]")
    response_b = agent.invoke({
        "messages": [{"role": "user", "content": "你好，请简单介绍一下你自己。限制 20 个字以内。"}]
    })
    print(f"🤖 Agent 最终回复：{response_b['messages'][-1].content}")

    print("\n💡 核心机制：")
    print("  - Agent 具备『路由思维』。需要外部数据时，它会暂停生成去调用工具；")
    print("  - 不需要时，它会直接以普通 LLM 的身份作答。")


# ============================================================================
# 示例 2：多工具 Agent 的意图识别
# ============================================================================
def example_2_multi_tool_agent():
    """
    演示 Agent 在拥有多个工具时，如何根据上下文精准路由 (Tool Routing)。
    """
    print("\n" + "=" * 70)
    print("示例 2：多工具 Agent 的意图识别")
    print("=" * 70)

    agent = create_agent(
        model=model,
        tools=[get_weather, calculator, web_search]
    )

    print("✅ 配置工具集：[get_weather, calculator, web_search]")

    # 测试不同垂直领域的提问
    tests = [
        "上海的天气适合出门吗？",  # 预期命中 get_weather
        "请帮我算一下 15.5 乘以 23 等于多少？",  # 预期命中 calculator
    ]

    for i, question in enumerate(tests, 1):
        print(f"\n--- [测试用例 {i}] ---")
        print(f"👤 用户：{question}")

        response = agent.invoke({
            "messages": [{"role": "user", "content": question}]
        })

        print(f"🤖 Agent：{response['messages'][-1].content}")

    print("\n💡 技术要点：工具越多，对大模型的指令遵循能力要求越高。必须保证工具的 Docstring 绝对清晰。")


# ============================================================================
# 示例 3：利用系统提示词塑造 Agent 行为
# ============================================================================
def example_3_agent_with_system_prompt():
    """
    使用 `system_prompt` 全局修饰 Agent 的行为。
    """
    print("\n" + "=" * 70)
    print("示例 3：利用系统提示词塑造 Agent 行为")
    print("=" * 70)

    # 创建带系统设定 (Persona) 的 Agent
    custom_persona = """你是一个严谨的科学助手。
工作守则：
1. 回答要极其简练。
2. 在提供计算结果或天气结果后，必须在结尾加上 "[数据已核实]" 的字样。
3. 坚决不要产生废话。
"""

    agent = create_agent(
        model=model,
        tools=[get_weather, calculator],
        system_prompt=custom_persona  # 全局提示词修饰器
    )

    print(f"已注入系统守则：\n{custom_persona}")

    prompt = "北京天气如何？顺便算一下 100 加 50。"
    print(f"\n👤 用户：{prompt}")

    response = agent.invoke({
        "messages": [{"role": "user", "content": prompt}]
    })

    print(f"\n🤖 Agent 最终回复：\n{response['messages'][-1].content}")


# ============================================================================
# 示例 4：透视 Agent 的底层执行状态机
# ============================================================================
def example_4_agent_execution_details():
    """
    揭示 ReAct 框架 (Reasoning and Acting) 的完整工作流。
    展示消息列表中每一种消息类型的流转过程。
    """
    print("\n" + "=" * 70)
    print("示例 4：透视 Agent 的底层执行状态机 (State Graph)")
    print("=" * 70)

    agent = create_agent(model=model, tools=[calculator])
    prompt = "25 乘以 8 等于多少？"

    print(f"用户提问: {prompt}")
    print("\n[开始拦截执行图历史...]\n")

    response = agent.invoke({
        "messages": [{"role": "user", "content": prompt}]
    })

    # 遍历状态图生成的全部上下文消息
    for i, msg in enumerate(response['messages'], 1):
        msg_type = msg.__class__.__name__
        print(f"--- 节点 {i} | 类型: {msg_type} ---")

        # 1. 如果是用户消息或普通 AI 回复
        if hasattr(msg, 'content') and msg.content:
            print(f"📜 载荷: {msg.content}")

        # 2. 如果 AI 决定调用工具 (发起 tool_calls)
        if hasattr(msg, 'tool_calls') and msg.tool_calls:
            print("🛠️ 动作指令 (Action): 触发工具调用")
            for tc in msg.tool_calls:
                print(f"   => 目标: {tc['name']} | 参数: {tc['args']}")

        # 3. 如果是工具的执行结果返回
        if msg_type == "ToolMessage":
            print(f"⚙️ 运行结果 (Observation): {msg.content}")

        print("")

    print("💡 状态流转总结 (ReAct Loop)：")
    print("  1. HumanMessage -> 用户抛出意图")
    print("  2. AIMessage (带 tool_calls) -> LLM 推理并下达调用指令")
    print("  3. ToolMessage -> 宿主环境执行 Python 函数并回传结果")
    print("  4. AIMessage -> LLM 基于工具结果总结最终文本")


# ============================================================================
# 示例 5：维持多轮对话记忆的 Agent
# ============================================================================
def example_5_multi_turn_agent():
    """
    向 Agent 传递连续的状态数组，实现带长程记忆的工具调用。
    """
    print("\n" + "=" * 70)
    print("示例 5：维持多轮对话记忆的 Agent")
    print("=" * 70)

    agent = create_agent(model=model, tools=[calculator])

    # [第 1 轮对话]
    print("--- [第 1 轮] ---")
    print("👤 用户：10 加 5 等于多少？")

    response1 = agent.invoke({
        "messages": [{"role": "user", "content": "10 加 5 等于多少？"}]
    })
    print(f"🤖 Agent：{response1['messages'][-1].content}")

    # [第 2 轮对话：继承上下文]
    print("\n--- [第 2 轮] ---")
    print("👤 用户：把刚才的结果再乘以 3 呢？")

    # 将第一轮产生的完整消息流 (包含所有 ToolMessage) 加上新的问题传入
    context_history = response1['messages'] + [{"role": "user", "content": "把刚才的结果再乘以 3 呢？"}]

    response2 = agent.invoke({
        "messages": context_history
    })
    print(f"🤖 Agent：{response2['messages'][-1].content}")

    print("\n💡 技术要点：与基础模型的历史管理相同，只需将完整的 `messages` 数组全量传入状态机。")


# ============================================================================
# 示例 6：生产环境最佳实践
# ============================================================================
def example_6_best_practices():
    """工程经验总结"""
    print("\n" + "=" * 70)
    print("示例 6：Agent 工程化最佳实践")
    print("=" * 70)

    print("""
✅ 构建健壮 Agent 的军规：

1. 警惕工具贪婪 (Tool Greed)：
   - 不要一次性给 Agent 挂载过多的工具（建议 < 5 个核心工具）。
   - 工具过多会导致 LLM 上下文急剧膨胀，且容易引发路由幻觉（选错工具）。

2. 防御性系统提示词 (System Prompt)：
   - 清晰定义其边界："你是一个搜索助手。如果无法通过工具找到答案，请直接回复不知道，不要瞎编。"

3. 容错与异常穿透：
   - 如果工具函数抛出 Exception，大模型往往会陷入死循环尝试。
   - 务必在 @tool 内部使用 try-except，并返回字符串错误码供大模型阅读。

4. 性能考量：
   - 每次 Tool Call 都意味着完整消耗了一次 API 请求。
   - 在生产环境中，推荐配合流式输出 (Streaming) 或图节点事件追踪，以优化用户等待体验。
    """)


# ============================================================================
# 主程序
# ============================================================================
def main():
    print("\n" + "=" * 70)
    print(" LangChain 1.0 基础教程 - 05 构建智能体 (Agent)")
    print("=" * 70)
    print(f"🔧 当前加载引擎: {MODEL_NAME}")

    try:
        example_1_basic_agent()
        input("\n[按 Enter 键继续查看下一个示例...]")

        example_2_multi_tool_agent()
        input("\n[按 Enter 键继续查看下一个示例...]")

        example_3_agent_with_system_prompt()
        input("\n[按 Enter 键继续查看下一个示例...]")

        example_4_agent_execution_details()
        input("\n[按 Enter 键继续查看下一个示例...]")

        example_5_multi_turn_agent()
        input("\n[按 Enter 键继续查看下一个示例...]")

        example_6_best_practices()

        print("\n" + "=" * 70)
        print(" 🎉 本章所有示例执行完毕！")
        print("=" * 70)
        print("\n本章技能树点亮：")
        print("  ✅ 掌握基于 API 架构的 `create_agent` 使用方法")
        print("  ✅ 理解智能体自动决策并调用工具的机制")
        print("  ✅ 透视 ReAct 循环流 (Human -> AI Action -> Observation -> AI Answer)")
        print("  ✅ 掌握利用 `system_prompt` 注入系统人格")
        print("  ✅ 实现具有多轮上下文记忆的动态工具流水线")

    except KeyboardInterrupt:
        print("\n\n⚠️ 程序已被用户手动中断")
    except Exception as e:
        print(f"\n❌ 运行出错：{type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
