"""
05 - Simple Agent: 赋予大模型行动力
"""

# 标准库：读取环境变量。
import os
# 标准库：平台与编码处理。
import sys
# 类型工具：可选参数注解。
from typing import Optional

# Windows 下修正终端编码，避免中文输出乱码。
if sys.platform == 'win32':
    import io
    # 设置 stdout 为 utf-8。
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    # 设置 stderr 为 utf-8。
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 加载 .env。
from dotenv import load_dotenv
# 模型初始化。
from langchain.chat_models import init_chat_model
# 工具装饰器。
from langchain_core.tools import tool
# Agent 创建函数。
from langchain.agents import create_agent

# ============================= 学习说明 =============================
# 本章请重点关注：
# - Agent 在何时触发工具
# - response['messages'] 中每条消息代表什么
# ==================================================================

# ============================================================================
# 环境配置与模型初始化
# ============================================================================

# 加载环境变量。
load_dotenv()
# 读取 key。
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# 读取 base_url。
OPENAI_API_BASE = os.getenv("OPENAI_API_BASE")
# 读取默认模型。
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "gpt-3.5-turbo")
# 自动补 provider 前缀。
MODEL_NAME = DEFAULT_MODEL if ":" in DEFAULT_MODEL else f"openai:{DEFAULT_MODEL}"

# 校验 key。
if not OPENAI_API_KEY or OPENAI_API_KEY == "your_openai_api_key_here_replace_this":
    raise ValueError(
        "\n" + "=" * 70 + "\n"
        "❌ 错误：未找到有效的 OPENAI_API_KEY 环境变量！\n"
        "=" * 70 + "\n"
        "请在 .env 文件中填入你的配置\n"
        "=" * 70
    )

# 对可疑 key 给出提醒。
if not OPENAI_API_BASE and not OPENAI_API_KEY.startswith("sk-"):
    print("\n⚠️  警告：你的 OPENAI_API_KEY 格式可能不正确，请确保配置了正确的密钥或 BASE_URL\n")

# 初始化全局模型。
model = init_chat_model(MODEL_NAME, api_key=OPENAI_API_KEY, base_url=OPENAI_API_BASE)


# ============================================================================
# 工具定义区
# ============================================================================

@tool
def get_weather(city: str) -> str:
    """获取指定城市的当前天气情况。"""
    # 模拟天气数据。
    mock_weather_db = {
        "北京": "晴朗，气温 22°C，适合户外活动",
        "上海": "多云，气温 26°C，湿度较高"
    }
    # 按城市返回天气或兜底文案。
    return mock_weather_db.get(city, f"暂无 {city} 的天气数据。")


@tool
def calculator(operation: str, a: float, b: float) -> str:
    """执行基础数学运算。支持 add/subtract/multiply/divide。"""
    try:
        # 运算分支。
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
        # 异常转字符串返回，避免崩溃。
        return f"计算出错: {str(e)}"


@tool
def web_search(query: str, num_results: Optional[int] = 3) -> str:
    """在互联网上搜索指定关键词（模拟）。"""
    return f"检索 '{query}' 成功。共返回了 {num_results} 条模拟搜索结果。"


# ============================================================================
# 示例 1：创建第一个 Agent
# ============================================================================
def example_1_basic_agent():
    """最小 Agent：单工具场景。"""
    print("\n" + "=" * 70)
    print("示例 1：创建第一个智能体 (Agent)")
    print("=" * 70)

    # 创建 Agent，并挂载天气工具。
    agent = create_agent(
        model=model,
        tools=[get_weather]
    )

    print("✅ Agent 构建成功！挂载工具：[get_weather]")

    # 场景 A：明显需要工具的问题。
    print("\n[测试 A：需要调用工具的提问]")
    response_a = agent.invoke({
        "messages": [{"role": "user", "content": "北京今天天气怎么样？"}]
    })
    print(f"🤖 Agent 最终回复：{response_a['messages'][-1].content}")

    # 场景 B：一般问候，可能不需要工具。
    print("\n[测试 B：常规对话提问 (无需工具)]")
    response_b = agent.invoke({
        "messages": [{"role": "user", "content": "你好，请简单介绍一下你自己。限制 20 个字以内。"}]
    })
    print(f"🤖 Agent 最终回复：{response_b['messages'][-1].content}")

    print("\n💡 机制说明：")
    print("  - 需要外部能力时，Agent 会走工具调用路径")
    print("  - 不需要时，Agent 会直接文本回答")


# ============================================================================
# 示例 2：多工具 Agent 的意图识别
# ============================================================================
def example_2_multi_tool_agent():
    """多工具路由示例。"""
    print("\n" + "=" * 70)
    print("示例 2：多工具 Agent 的意图识别")
    print("=" * 70)

    # 创建多工具 Agent。
    agent = create_agent(
        model=model,
        tools=[get_weather, calculator, web_search]
    )

    print("✅ 配置工具集：[get_weather, calculator, web_search]")

    # 准备不同类型问题。
    tests = [
        "上海的天气适合出门吗？",
        "请帮我算一下 15.5 乘以 23 等于多少？",
    ]

    # 逐个问题测试路由效果。
    for i, question in enumerate(tests, 1):
        print(f"\n--- [测试用例 {i}] ---")
        print(f"👤 用户：{question}")

        response = agent.invoke({
            "messages": [{"role": "user", "content": question}]
        })

        print(f"🤖 Agent：{response['messages'][-1].content}")

    print("\n💡 工具越多，docstring 越要清晰，避免路由混淆。")


# ============================================================================
# 示例 3：利用系统提示词塑造 Agent 行为
# ============================================================================
def example_3_agent_with_system_prompt():
    """演示 system_prompt 对 Agent 风格和规则的约束。"""
    print("\n" + "=" * 70)
    print("示例 3：利用系统提示词塑造 Agent 行为")
    print("=" * 70)

    # 自定义 Agent 行为守则。
    custom_persona = """你是一个严谨的科学助手。
工作守则：
1. 回答要极其简练。
2. 在提供计算结果或天气结果后，必须在结尾加上 "[数据已核实]" 的字样。
3. 坚决不要产生废话。
"""

    # 创建带系统提示词的 Agent。
    agent = create_agent(
        model=model,
        tools=[get_weather, calculator],
        system_prompt=custom_persona
    )

    print(f"已注入系统守则：\n{custom_persona}")

    # 提问一个可能触发多个工具的问题。
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
    """打印完整消息链，理解 ReAct 流程。"""
    print("\n" + "=" * 70)
    print("示例 4：透视 Agent 的底层执行状态机 (State Graph)")
    print("=" * 70)

    # 创建仅带计算器工具的 Agent。
    agent = create_agent(model=model, tools=[calculator])
    # 准备问题。
    prompt = "25 乘以 8 等于多少？"

    print(f"用户提问: {prompt}")
    print("\n[开始拦截执行图历史...]\n")

    # 调用 Agent。
    response = agent.invoke({
        "messages": [{"role": "user", "content": prompt}]
    })

    # 遍历完整历史消息。
    for i, msg in enumerate(response['messages'], 1):
        # 获取消息类型名称。
        msg_type = msg.__class__.__name__
        print(f"--- 节点 {i} | 类型: {msg_type} ---")

        # 如果消息有文本内容就打印。
        if hasattr(msg, 'content') and msg.content:
            print(f"📜 载荷: {msg.content}")

        # 如果消息包含 tool_calls，说明此时模型在下达工具调用指令。
        if hasattr(msg, 'tool_calls') and msg.tool_calls:
            print("🛠️ 动作指令 (Action): 触发工具调用")
            for tc in msg.tool_calls:
                print(f"   => 目标: {tc['name']} | 参数: {tc['args']}")

        # 如果是 ToolMessage，说明工具执行结果已返回。
        if msg_type == "ToolMessage":
            print(f"⚙️ 运行结果 (Observation): {msg.content}")

        print("")

    print("💡 状态流转总结 (ReAct Loop)：")
    print("  1. HumanMessage -> 用户意图")
    print("  2. AIMessage(tool_calls) -> 下达工具指令")
    print("  3. ToolMessage -> 工具执行结果")
    print("  4. AIMessage -> 基于结果产出最终答案")


# ============================================================================
# 示例 5：维持多轮对话记忆的 Agent
# ============================================================================
def example_5_multi_turn_agent():
    """演示跨轮上下文继承。"""
    print("\n" + "=" * 70)
    print("示例 5：维持多轮对话记忆的 Agent")
    print("=" * 70)

    # 创建 Agent。
    agent = create_agent(model=model, tools=[calculator])

    # 第 1 轮。
    print("--- [第 1 轮] ---")
    print("👤 用户：10 加 5 等于多少？")

    response1 = agent.invoke({
        "messages": [{"role": "user", "content": "10 加 5 等于多少？"}]
    })
    print(f"🤖 Agent：{response1['messages'][-1].content}")

    # 第 2 轮。
    print("\n--- [第 2 轮] ---")
    print("👤 用户：把刚才的结果再乘以 3 呢？")

    # 把第一轮完整历史 + 第二轮问题一起传入。
    context_history = response1['messages'] + [{"role": "user", "content": "把刚才的结果再乘以 3 呢？"}]

    response2 = agent.invoke({
        "messages": context_history
    })
    print(f"🤖 Agent：{response2['messages'][-1].content}")

    print("\n💡 要点：多轮 Agent 与多轮模型调用一样，都依赖完整 messages 历史。")


# ============================================================================
# 示例 6：生产环境最佳实践
# ============================================================================
def example_6_best_practices():
    """打印 Agent 工程实践建议。"""
    print("\n" + "=" * 70)
    print("示例 6：Agent 工程化最佳实践")
    print("=" * 70)

    print("""
✅ 构建健壮 Agent 的建议：

1. 控制工具数量：建议先保持在 2~5 个核心工具
2. system_prompt 明确边界：找不到答案就说不知道
3. 工具内做异常兜底：避免死循环重试
4. 关注性能：每次工具调用都可能产生额外时延和成本
    """)


# ============================================================================
# 主程序
# ============================================================================
def main():
    """按顺序运行本章所有示例。"""
    # 打印标题与模型信息。
    print("\n" + "=" * 70)
    print(" LangChain 1.0 基础教程 - 05 构建智能体 (Agent)")
    print("=" * 70)
    print(f"🔧 当前加载引擎: {MODEL_NAME}")

    try:
        # 示例 1：最小 Agent。
        example_1_basic_agent()
        input("\n[按 Enter 键继续查看下一个示例...]")

        # 示例 2：多工具路由。
        example_2_multi_tool_agent()
        input("\n[按 Enter 键继续查看下一个示例...]")

        # 示例 3：系统提示词控制行为。
        example_3_agent_with_system_prompt()
        input("\n[按 Enter 键继续查看下一个示例...]")

        # 示例 4：执行轨迹透视。
        example_4_agent_execution_details()
        input("\n[按 Enter 键继续查看下一个示例...]")

        # 示例 5：多轮记忆。
        example_5_multi_turn_agent()
        input("\n[按 Enter 键继续查看下一个示例...]")

        # 示例 6：工程实践总结。
        example_6_best_practices()

        # 打印完成信息。
        print("\n" + "=" * 70)
        print(" 🎉 本章所有示例执行完毕！")
        print("=" * 70)
        print("\n本章技能树点亮：")
        print("  ✅ create_agent")
        print("  ✅ 自动工具路由")
        print("  ✅ ReAct 循环认知")
        print("  ✅ system_prompt 约束")
        print("  ✅ 多轮上下文传递")

    except KeyboardInterrupt:
        # 用户中断处理。
        print("\n\n⚠️ 程序已被用户手动中断")
    except Exception as e:
        # 打印详细异常。
        print(f"\n❌ 运行出错：{type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()


# 直接运行文件时执行 main。
if __name__ == "__main__":
    main()
