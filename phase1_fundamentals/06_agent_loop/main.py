"""
06 - Agent 执行循环

核心理解：
- response['messages'] 记录完整执行历史
- stream() 用于实时输出和调试
"""

import os
import sys

parent_dir = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, os.path.join(parent_dir, '04_custom_tools', 'tools'))

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
from langchain_core.tools import tool

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_API_BASE = os.getenv("OPENAI_API_BASE")
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "gpt-3.5-turbo")
MODEL_NAME = DEFAULT_MODEL if ":" in DEFAULT_MODEL else f"openai:{DEFAULT_MODEL}"

if not OPENAI_API_KEY or not OPENAI_API_BASE:
    raise ValueError("请配置 OPENAI_API_KEY 和 OPENAI_API_BASE")

model = init_chat_model(MODEL_NAME, api_key=OPENAI_API_KEY, base_url=OPENAI_API_BASE)


@tool
def get_weather(city: str) -> str:
    """获取城市天气。"""
    data = {"北京": "晴天，15°C", "上海": "多云，18°C", "深圳": "阴天，22°C"}
    return data.get(city, f"暂无{city}天气")


@tool
def calculator(operation: str, a: float, b: float) -> str:
    """执行数学运算：add/subtract/multiply/divide"""
    ops = {"add": a+b, "subtract": a-b, "multiply": a*b, "divide": a/b if b else "错误"}
    return str(ops.get(operation, "不支持"))


def example_1_understand_loop():
    """理解执行循环"""
    print("\n" + "=" * 60)
    print("示例 1：执行循环详解")
    print("=" * 60)

    agent = create_agent(model=model, tools=[calculator])

    response = agent.invoke({
        "messages": [{"role": "user", "content": "25 乘以 8 等于多少？"}]
    })

    print("\n完整消息历史：")
    for i, msg in enumerate(response['messages'], 1):
        print(f"\n--- [{i}] {msg.__class__.__name__} ---")

        if hasattr(msg, 'content') and msg.content:
            print(f"内容: {msg.content}")

        if hasattr(msg, 'tool_calls') and msg.tool_calls:
            tc = msg.tool_calls[0]
            print(f"工具: {tc['name']}, 参数: {tc['args']}")

    print("""
\n执行流程：
  1. HumanMessage    → 用户问题
  2. AIMessage       → AI 决定调用工具
  3. ToolMessage     → 工具执行结果
  4. AIMessage       → 最终答案
""")


def example_2_streaming():
    """流式输出"""
    print("\n" + "=" * 60)
    print("示例 2：流式输出")
    print("=" * 60)

    agent = create_agent(model=model, tools=[get_weather])

    print("\n问题：北京天气如何？")
    print("\n流式输出：")
    print("-" * 40)

    for chunk in agent.stream({
        "messages": [{"role": "user", "content": "北京天气如何？"}]
    }):
        if 'messages' in chunk:
            msg = chunk['messages'][-1]
            if hasattr(msg, 'content') and msg.content:
                if not getattr(msg, 'tool_calls', None):
                    print(f"\n最终回答: {msg.content}")

    print("\n💡 stream() 适合实时展示进度")


def example_3_multi_step():
    """多步骤执行"""
    print("\n" + "=" * 60)
    print("示例 3：多步骤执行")
    print("=" * 60)

    agent = create_agent(
        model=model,
        tools=[calculator],
        system_prompt="你是数学助手，复杂计算分步完成。"
    )

    response = agent.invoke({
        "messages": [{"role": "user", "content": "先算 10+20，再乘以 3"}]
    })

    # 统计工具调用次数
    tool_count = sum(
        len(msg.tool_calls) for msg in response['messages']
        if hasattr(msg, 'tool_calls')
    )

    print(f"工具调用次数: {tool_count}")
    print(f"最终答案: {response['messages'][-1].content}")

    print("\n💡 Agent 可以连续多次调用工具")


def example_4_inspect_state():
    """查看中间状态"""
    print("\n" + "=" * 60)
    print("示例 4：中间状态")
    print("=" * 60)

    agent = create_agent(model=model, tools=[calculator])

    print("\n问题：100 除以 5 等于多少？")
    print("\n执行步骤：")

    step = 0
    for chunk in agent.stream({
        "messages": [{"role": "user", "content": "100 除以 5 等于多少？"}]
    }):
        step += 1
        print(f"\n步骤 {step}:")

        if 'messages' in chunk:
            msg = chunk['messages'][-1]
            print(f"  类型: {msg.__class__.__name__}")

            if hasattr(msg, 'tool_calls') and msg.tool_calls:
                print(f"  工具: {msg.tool_calls[0]['name']}")
            elif hasattr(msg, 'content') and msg.content:
                print(f"  内容: {msg.content[:50]}...")

    print("\n💡 stream 可用于调试和前端进度展示")


def example_5_message_types():
    """消息类型详解"""
    print("\n" + "=" * 60)
    print("示例 5：消息类型")
    print("=" * 60)

    agent = create_agent(model=model, tools=[get_weather])

    response = agent.invoke({
        "messages": [{"role": "user", "content": "上海天气如何？"}]
    })

    for msg in response['messages']:
        msg_type = msg.__class__.__name__

        if msg_type == "HumanMessage":
            print(f"\n[HumanMessage] 用户输入")
            print(f"  内容: {msg.content}")

        elif msg_type == "AIMessage":
            if hasattr(msg, 'tool_calls') and msg.tool_calls:
                print(f"\n[AIMessage] 决定调用工具")
                print(f"  工具: {msg.tool_calls[0]['name']}")
            else:
                print(f"\n[AIMessage] 最终回答")
                print(f"  内容: {msg.content}")

        elif msg_type == "ToolMessage":
            print(f"\n[ToolMessage] 工具结果")
            print(f"  结果: {msg.content}")


def example_6_best_practices():
    """最佳实践"""
    print("\n" + "=" * 60)
    print("示例 6：最佳实践")
    print("=" * 60)

    print("""
实用代码模式：

1. 获取最终答案
   final = response['messages'][-1].content

2. 检查是否用工具
   has_tools = any(hasattr(m, 'tool_calls') and m.tool_calls
                   for m in response['messages'])

3. 收集使用的工具
   tools = [tc['name'] for m in response['messages']
            if hasattr(m, 'tool_calls')
            for tc in m.tool_calls]

4. stream 用于实时展示
5. invoke 包裹 try-except
""")

    # 实际示例
    agent = create_agent(model=model, tools=[calculator])

    try:
        response = agent.invoke({
            "messages": [{"role": "user", "content": "5 加 3"}]
        })

        final = response['messages'][-1].content
        print(f"最终答案: {final}")

        tools = [
            tc['name'] for m in response['messages']
            if hasattr(m, 'tool_calls')
            for tc in m.tool_calls
        ]
        print(f"使用工具: {tools}")

    except Exception as e:
        print(f"错误: {e}")


def main():
    print("\n" + "=" * 60)
    print(" LangChain 1.0 - Agent 执行循环")
    print("=" * 60)

    try:
        example_1_understand_loop()
        input("\n按 Enter 继续...")
        example_2_streaming()
        input("\n按 Enter 继续...")
        example_3_multi_step()
        input("\n按 Enter 继续...")
        example_4_inspect_state()
        input("\n按 Enter 继续...")
        example_5_message_types()
        input("\n按 Enter 继续...")
        example_6_best_practices()

        print("\n" + "=" * 60)
        print(" 🎉 Phase 1 完成！")
        print("=" * 60)
        print("""
核心要点：
  ✅ Agent 循环：问题 → 工具调用 → 结果 → 答案
  ✅ messages 记录完整历史
  ✅ stream() 实时输出
  ✅ 调试时先打印 messages
""")

    except KeyboardInterrupt:
        print("\n\n程序已中断")
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
