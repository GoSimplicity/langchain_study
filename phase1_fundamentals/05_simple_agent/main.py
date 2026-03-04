"""
05 - Simple Agent: 赋予大模型行动力

Agent = 模型 + 工具 + 自动执行循环
"""

import os
import sys
from typing import Optional

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.tools import tool
from langchain.agents import create_agent

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_API_BASE = os.getenv("OPENAI_API_BASE")
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "gpt-3.5-turbo")
MODEL_NAME = DEFAULT_MODEL if ":" in DEFAULT_MODEL else f"openai:{DEFAULT_MODEL}"

if not OPENAI_API_KEY:
    raise ValueError("请在 .env 中配置 OPENAI_API_KEY")

model = init_chat_model(MODEL_NAME, api_key=OPENAI_API_KEY, base_url=OPENAI_API_BASE)


# ============================================================================
# 工具定义
# ============================================================================

@tool
def get_weather(city: str) -> str:
    """获取指定城市的天气。"""
    data = {"北京": "晴朗，22°C", "上海": "多云，26°C"}
    return data.get(city, f"暂无 {city} 天气")


@tool
def calculator(operation: str, a: float, b: float) -> str:
    """执行数学运算：add/subtract/multiply/divide"""
    ops = {"add": a+b, "subtract": a-b, "multiply": a*b, "divide": a/b if b else "错误"}
    return str(ops.get(operation, "不支持"))


@tool
def web_search(query: str, num_results: Optional[int] = 3) -> str:
    """搜索互联网。"""
    return f"搜索 '{query}'，返回 {num_results} 条结果"


# ============================================================================
# 示例
# ============================================================================

def example_1_basic_agent():
    """最小 Agent"""
    print("\n" + "=" * 60)
    print("示例 1：创建第一个 Agent")
    print("=" * 60)

    agent = create_agent(model=model, tools=[get_weather])
    print("✅ Agent 创建成功，工具: [get_weather]")

    # 需要工具的问题
    print("\n[需要工具的提问]")
    response = agent.invoke({
        "messages": [{"role": "user", "content": "北京天气如何？"}]
    })
    print(f"🤖 Agent: {response['messages'][-1].content}")

    # 不需要工具的问题
    print("\n[不需要工具的提问]")
    response = agent.invoke({
        "messages": [{"role": "user", "content": "你好，介绍一下自己，20字内"}]
    })
    print(f"🤖 Agent: {response['messages'][-1].content}")


def example_2_multi_tool():
    """多工具路由"""
    print("\n" + "=" * 60)
    print("示例 2：多工具 Agent")
    print("=" * 60)

    agent = create_agent(model=model, tools=[get_weather, calculator])
    print("✅ 工具: [get_weather, calculator]")

    questions = [
        "上海天气适合出门吗？",
        "15.5 乘以 23 等于多少？",
    ]

    for q in questions:
        print(f"\n👤 用户: {q}")
        response = agent.invoke({"messages": [{"role": "user", "content": q}]})
        print(f"🤖 Agent: {response['messages'][-1].content}")

    print("\n💡 工具越多，docstring 越要清晰")


def example_3_system_prompt():
    """系统提示词塑造行为"""
    print("\n" + "=" * 60)
    print("示例 3：系统提示词控制")
    print("=" * 60)

    system_prompt = """你是一个严谨的科学助手。
规则：
1. 回答极简
2. 数据结果后加 "[已核实]"
3. 不废话
"""

    agent = create_agent(
        model=model,
        tools=[get_weather, calculator],
        system_prompt=system_prompt
    )

    print(f"系统提示: {system_prompt[:50]}...")

    prompt = "北京天气？顺便算 100+50"
    print(f"\n👤 用户: {prompt}")

    response = agent.invoke({"messages": [{"role": "user", "content": prompt}]})
    print(f"\n🤖 Agent:\n{response['messages'][-1].content}")


def example_4_execution_trace():
    """透视执行过程"""
    print("\n" + "=" * 60)
    print("示例 4：执行轨迹")
    print("=" * 60)

    agent = create_agent(model=model, tools=[calculator])

    response = agent.invoke({
        "messages": [{"role": "user", "content": "25 乘以 8 等于多少？"}]
    })

    print("完整消息链：")
    for i, msg in enumerate(response['messages'], 1):
        msg_type = msg.__class__.__name__
        print(f"\n--- [{i}] {msg_type} ---")

        if hasattr(msg, 'content') and msg.content:
            print(f"内容: {msg.content[:60]}..." if len(str(msg.content)) > 60 else f"内容: {msg.content}")

        if hasattr(msg, 'tool_calls') and msg.tool_calls:
            tc = msg.tool_calls[0]
            print(f"工具: {tc['name']}, 参数: {tc['args']}")

    print("\n💡 流程: HumanMessage → AIMessage(决策) → ToolMessage(执行) → AIMessage(答案)")


def example_5_multi_turn():
    """多轮对话"""
    print("\n" + "=" * 60)
    print("示例 5：多轮对话")
    print("=" * 60)

    agent = create_agent(model=model, tools=[calculator])

    # 第 1 轮
    print("--- [第 1 轮] ---")
    print("👤 用户: 10 加 5 等于多少？")
    response1 = agent.invoke({
        "messages": [{"role": "user", "content": "10 加 5 等于多少？"}]
    })
    print(f"🤖 Agent: {response1['messages'][-1].content}")

    # 第 2 轮：带上第 1 轮历史
    print("\n--- [第 2 轮] ---")
    print("👤 用户: 把刚才的结果乘以 3？")
    context = response1['messages'] + [{"role": "user", "content": "把刚才的结果乘以 3？"}]
    response2 = agent.invoke({"messages": context})
    print(f"🤖 Agent: {response2['messages'][-1].content}")

    print("\n💡 多轮 Agent 和多轮模型一样，都依赖完整历史")


def example_6_best_practices():
    """最佳实践"""
    print("\n" + "=" * 60)
    print("示例 6：最佳实践")
    print("=" * 60)

    print("""
✅ Agent 工程化建议：

1. 控制工具数量：2~5 个核心工具
2. system_prompt 明确边界：找不到就说不知道
3. 工具内异常兜底：避免死循环
4. 关注性能：每次工具调用都有时延和成本
""")


def main():
    print("\n" + "=" * 60)
    print(" LangChain 1.0 - 05 构建智能体")
    print("=" * 60)
    print(f"🔧 模型: {MODEL_NAME}")

    try:
        example_1_basic_agent()
        input("\n[按 Enter 继续...]")
        example_2_multi_tool()
        input("\n[按 Enter 继续...]")
        example_3_system_prompt()
        input("\n[按 Enter 继续...]")
        example_4_execution_trace()
        input("\n[按 Enter 继续...]")
        example_5_multi_turn()
        input("\n[按 Enter 继续...]")
        example_6_best_practices()

        print("\n" + "=" * 60)
        print(" 🎉 完成！")
        print("=" * 60)
        print("\n技能点亮：")
        print("  ✅ create_agent")
        print("  ✅ 工具路由")
        print("  ✅ ReAct 循环")
        print("  ✅ system_prompt")
        print("  ✅ 多轮上下文")

    except KeyboardInterrupt:
        print("\n\n程序已中断")
    except Exception as e:
        print(f"\n❌ 错误：{e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
