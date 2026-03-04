"""
06 - Agent 执行循环
"""

# 标准库：环境变量和路径处理。
import os
# 标准库：修改 import 搜索路径。
import sys

# 计算项目根目录路径。
parent_dir = os.path.dirname(os.path.dirname(__file__))
# 把 04_custom_tools/tools 加入模块搜索路径，便于复用工具。
sys.path.insert(0, os.path.join(parent_dir, '04_custom_tools', 'tools'))

# 加载 .env。
from dotenv import load_dotenv
# 模型初始化接口。
from langchain.chat_models import init_chat_model
# Agent 创建函数。
from langchain.agents import create_agent
from langchain_core.tools import tool

# ============================= 学习说明 =============================
# 这一章请重点看 response['messages'] 与 stream() chunk。
# 最终答案很重要，但中间步骤更能解释 Agent 为什么这么做。
# ==================================================================

# 加载环境变量。
load_dotenv()
# 读取 key。
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# 读取 base_url。
OPENAI_API_BASE = os.getenv("OPENAI_API_BASE")
# 读取默认模型。
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "Pro/MiniMaxAI/MiniMax-M2.5")
# 自动补 provider 前缀。
MODEL_NAME = DEFAULT_MODEL if ":" in DEFAULT_MODEL else f"openai:{DEFAULT_MODEL}"

# 校验必要配置。
if not OPENAI_API_KEY or not OPENAI_API_BASE or OPENAI_API_KEY == "your_openai_api_key_here_replace_this":
    raise ValueError("请先设置 OPENAI_API_KEY 和 OPENAI_API_BASE")

# 初始化模型。
model = init_chat_model(MODEL_NAME, api_key=OPENAI_API_KEY, base_url=OPENAI_API_BASE)


@tool
def get_weather(city: str) -> str:
    """
    获取指定城市的天气信息

    参数:
        city: 城市名称，如"北京"、"上海"

    返回:
        天气信息字符串
    """
    # 模拟天气数据（实际应用中应调用真实API）
    weather_data = {
        "北京": "晴天，温度 15°C，空气质量良好",
        "上海": "多云，温度 18°C，有轻微雾霾",
        "深圳": "阴天，温度 22°C，可能有小雨",
        "成都": "小雨，温度 12°C，湿度较高"
    }

    return weather_data.get(city, f"抱歉，暂时没有{city}的天气数据")


@tool
def calculator(operation: str, a: float, b: float) -> str:
    """
    执行基本的数学计算

    参数:
        operation: 运算类型，支持 "add"(加), "subtract"(减), "multiply"(乘), "divide"(除)
        a: 第一个数字
        b: 第二个数字

    返回:
        计算结果字符串
    """
    operations = {
        "add": lambda x, y: x + y,
        "subtract": lambda x, y: x - y,
        "multiply": lambda x, y: x * y,
        "divide": lambda x, y: x / y if y != 0 else "错误：除数不能为零"
    }

    if operation not in operations:
        return f"不支持的运算类型：{operation}。支持的类型：add, subtract, multiply, divide"

    try:
        result = operations[operation](a, b)
        return f"{a} {operation} {b} = {result}"
    except Exception as e:
        return f"计算错误：{e}"


# ============================================================================
# 示例 1：理解执行循环 - 查看完整消息历史
# ============================================================================
def example_1_understand_loop():
    """
    查看一次调用中的完整消息链。
    """
    print("\n" + "=" * 70)
    print("示例 1：Agent 执行循环详解")
    print("=" * 70)

    # 创建只带 calculator 的 Agent，方便聚焦单一工具。
    agent = create_agent(
        model=model,
        tools=[calculator]
    )

    print("\n问题：25 乘以 8 等于多少？")
    # 发起调用。
    response = agent.invoke({
        "messages": [{"role": "user", "content": "25 乘以 8 等于多少？"}]
    })

    print("\n完整消息历史：")
    # 遍历每条消息。
    for i, msg in enumerate(response['messages'], 1):
        print(f"\n{'=' * 60}")
        print(f"消息 {i}: {msg.__class__.__name__}")
        print(f"{'=' * 60}")

        # 若消息有文本内容则打印。
        if hasattr(msg, 'content') and msg.content:
            print(f"内容: {msg.content}")

        # 若消息里有 tool_calls，打印调用指令详情。
        if hasattr(msg, 'tool_calls') and msg.tool_calls:
            print("工具调用:")
            for tc in msg.tool_calls:
                print(f"  - 工具: {tc['name']}")
                print(f"  - 参数: {tc['args']}")

        # ToolMessage 通常会带 name（工具名）。
        if hasattr(msg, 'name'):
            print(f"工具名: {msg.name}")

    print("\n\n执行流程：")
    print("""
    1. HumanMessage    → 用户问题
    2. AIMessage       → AI 决定调用工具（包含 tool_calls）
    3. ToolMessage     → 工具执行结果
    4. AIMessage       → AI 基于结果生成最终答案
    """)

    print("\n关键点：")
    print("  - Agent 自动完成循环")
    print("  - 所有步骤都在 messages 里")
    print("  - 最后一条消息通常是最终答案")


# ============================================================================
# 示例 2：流式输出（Streaming）
# ============================================================================
def example_2_streaming():
    """
    实时观察 Agent 输出。
    """
    print("\n" + "=" * 70)
    print("示例 2：流式输出")
    print("=" * 70)

    # 创建 Agent（挂载计算器与天气工具）。
    agent = create_agent(
        model=model,
        tools=[calculator, get_weather]
    )

    print("\n问题：北京天气如何？")
    print("\n流式输出（实时显示）：")
    print("-" * 70)

    # stream 返回生成器，每次迭代是一个 chunk（状态增量）。
    for chunk in agent.stream({
        "messages": [{"role": "user", "content": "北京天气如何？"}]
    }):
        # chunk 可能不含 messages，先判断。
        if 'messages' in chunk:
            # 取当前 chunk 的最新消息。
            latest_msg = chunk['messages'][-1]

            # 过滤掉“工具调用指令消息”，只展示最终文本回答。
            if hasattr(latest_msg, 'content') and latest_msg.content:
                if not hasattr(latest_msg, 'tool_calls') or not latest_msg.tool_calls:
                    print(f"\n最终回答: {latest_msg.content}")

    print("\n关键点：")
    print("  - stream() 适合实时进度展示")
    print("  - chunk 是增量状态，不一定每条都是最终答案")


# ============================================================================
# 示例 3：多步骤执行
# ============================================================================
def example_3_multi_step():
    """
    演示复杂问题可能触发多次工具调用。
    """
    print("\n" + "=" * 70)
    print("示例 3：多步骤执行")
    print("=" * 70)

    # 创建 Agent 并加系统提示，鼓励分步求解。
    agent = create_agent(
        model=model,
        tools=[calculator],
        system_prompt="你是一个数学助手。当遇到复杂计算时，分步骤计算。"
    )

    print("\n问题：先算 10 加 20，然后把结果乘以 3")
    # 调用 Agent。
    response = agent.invoke({
        "messages": [{"role": "user", "content": "先算 10 加 20，然后把结果乘以 3"}]
    })

    # 统计工具调用次数。
    tool_calls_count = 0
    for msg in response['messages']:
        if hasattr(msg, 'tool_calls') and msg.tool_calls:
            tool_calls_count += len(msg.tool_calls)

    print(f"\n工具调用次数: {tool_calls_count}")
    print(f"最终答案: {response['messages'][-1].content}")

    print("\n关键点：")
    print("  - Agent 可以连续多次调用工具")
    print("  - 前一步结果会影响后一步")


# ============================================================================
# 示例 4：查看中间状态
# ============================================================================
def example_4_inspect_state():
    """
    使用 stream 观察每一步的状态变化。
    """
    print("\n" + "=" * 70)
    print("示例 4：查看中间状态")
    print("=" * 70)

    # 创建 Agent。
    agent = create_agent(
        model=model,
        tools=[calculator]
    )

    print("\n问题：100 除以 5 等于多少？")
    print("\n执行步骤：")

    # 步骤计数器。
    step = 0
    # 流式接收执行状态。
    for chunk in agent.stream({
        "messages": [{"role": "user", "content": "100 除以 5 等于多少？"}]
    }):
        step += 1
        print(f"\n步骤 {step}:")

        if 'messages' in chunk:
            latest = chunk['messages'][-1]
            msg_type = latest.__class__.__name__
            print(f"  类型: {msg_type}")

            # 如果是工具调用消息，打印工具名。
            if hasattr(latest, 'tool_calls') and latest.tool_calls:
                print(f"  工具调用: {latest.tool_calls[0]['name']}")
            # 如果是普通内容消息，打印内容预览。
            elif hasattr(latest, 'content') and latest.content:
                print(f"  内容: {latest.content[:50]}...")

    print("\n关键点：")
    print("  - stream 可用于调试 Agent 执行过程")
    print("  - 也适合做前端进度展示")


# ============================================================================
# 示例 5：理解消息类型
# ============================================================================
def example_5_message_types():
    """
    逐条解释执行链中不同消息类型的含义。
    """
    print("\n" + "=" * 70)
    print("示例 5：消息类型详解")
    print("=" * 70)

    # 创建天气 Agent。
    agent = create_agent(
        model=model,
        tools=[get_weather]
    )

    # 发起调用。
    response = agent.invoke({
        "messages": [{"role": "user", "content": "上海天气如何？"}]
    })

    print("\n消息类型分析：")
    for msg in response['messages']:
        msg_type = msg.__class__.__name__

        # 用户消息。
        if msg_type == "HumanMessage":
            print("\n[HumanMessage] 用户输入")
            print(f"  内容: {msg.content}")

        # AI 消息（可能是工具调用，也可能是最终答案）。
        elif msg_type == "AIMessage":
            if hasattr(msg, 'tool_calls') and msg.tool_calls:
                print("\n[AIMessage] AI 决定调用工具")
                print(f"  工具: {msg.tool_calls[0]['name']}")
                print(f"  参数: {msg.tool_calls[0]['args']}")
            else:
                print("\n[AIMessage] AI 的最终回答")
                print(f"  内容: {msg.content}")

        # 工具结果消息。
        elif msg_type == "ToolMessage":
            print("\n[ToolMessage] 工具执行结果")
            print(f"  工具: {msg.name}")
            print(f"  结果: {msg.content}")

    print("\n\n消息类型总结：")
    print("""
    HumanMessage  → 用户输入
    AIMessage     → AI 输出（可能含 tool_calls）
    ToolMessage   → 工具执行结果
    SystemMessage → 系统指令（通过 system_prompt）
    """)


# ============================================================================
# 示例 6：执行循环最佳实践
# ============================================================================
def example_6_best_practices():
    """
    给出执行循环调试与生产实践。
    """
    print("\n" + "=" * 70)
    print("示例 6：执行循环最佳实践")
    print("=" * 70)

    print("""
最佳实践：

1. 获取最终答案
   final_answer = response['messages'][-1].content

2. 检查是否使用工具
   has_tool_calls = any(hasattr(msg, 'tool_calls') and msg.tool_calls for msg in response['messages'])

3. 使用 stream 提升用户体验
4. 调试时打印完整 messages
5. 对 agent.invoke 包裹 try-except
    """)

    print("\n实际示例：")
    # 创建 Agent。
    agent = create_agent(model=model, tools=[calculator])

    try:
        # 发起简单调用。
        response = agent.invoke({
            "messages": [{"role": "user", "content": "5 加 3"}]
        })

        # 获取最终答案。
        final_answer = response['messages'][-1].content
        print(f"最终答案: {final_answer}")

        # 收集工具调用名。
        used_tools = [
            msg.tool_calls[0]['name']
            for msg in response['messages']
            if hasattr(msg, 'tool_calls') and msg.tool_calls
        ]
        print(f"使用的工具: {used_tools}")

    except Exception as e:
        # 打印异常。
        print(f"错误: {e}")


# ============================================================================
# 主程序
# ============================================================================
def main():
    """按顺序运行本章所有示例。"""
    # 打印标题。
    print("\n" + "=" * 70)
    print(" LangChain 1.0 - Agent 执行循环")
    print("=" * 70)

    try:
        # 示例 1：完整消息链。
        example_1_understand_loop()
        input("\n按 Enter 继续...")

        # 示例 2：流式输出。
        example_2_streaming()
        input("\n按 Enter 继续...")

        # 示例 3：多步骤工具调用。
        example_3_multi_step()
        input("\n按 Enter 继续...")

        # 示例 4：中间状态调试。
        example_4_inspect_state()
        input("\n按 Enter 继续...")

        # 示例 5：消息类型分析。
        example_5_message_types()
        input("\n按 Enter 继续...")

        # 示例 6：最佳实践。
        example_6_best_practices()

        # 打印结束信息。
        print("\n" + "=" * 70)
        print(" 完成！")
        print("=" * 70)
        print("\n核心要点：")
        print("  Agent 执行循环：问题 → 工具调用 → 结果 → 答案")
        print("  messages 记录完整历史")
        print("  stream() 用于实时输出")

    except KeyboardInterrupt:
        # 用户中断。
        print("\n\n程序中断")
    except Exception as e:
        # 输出详细异常。
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()


# 直接运行文件时执行 main。
if __name__ == "__main__":
    main()
