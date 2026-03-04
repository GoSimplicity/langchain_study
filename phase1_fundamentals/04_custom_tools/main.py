"""
04 - Custom Tools: 自定义工具与 Function Calling

核心理解：
1. docstring 会被模型读取，用于决定"何时调用工具"
2. bind_tools 后 response.tool_calls 只是调用指令，还没执行工具
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
    """
    获取指定城市的当前天气。

    参数:
        city: 城市名称，如 "北京", "上海"
    """
    mock_data = {
        "北京": "晴朗，22°C，微风",
        "上海": "多云，26°C，湿度 80%"
    }
    return mock_data.get(city, f"无法获取 {city} 的天气")


@tool
def calculator(operation: str, a: float, b: float) -> str:
    """
    执行基础数学运算。

    参数:
        operation: 运算类型 - add/subtract/multiply/divide
        a: 第一个数
        b: 第二个数
    """
    try:
        ops = {
            "add": a + b,
            "subtract": a - b,
            "multiply": a * b,
            "divide": a / b if b != 0 else "错误：除数不能为零"
        }
        return str(ops.get(operation, f"不支持的运算: {operation}"))
    except Exception as e:
        return f"计算错误: {e}"


@tool
def web_search(query: str, num_results: Optional[int] = 3) -> str:
    """
    搜索互联网。

    参数:
        query: 搜索关键词
        num_results: 返回结果数，默认 3
    """
    return f"搜索 '{query}' 完成，返回 {num_results} 条结果"


# ============================================================================
# 示例
# ============================================================================

def example_1_simple_tool():
    """最小工具定义"""
    print("\n" + "=" * 60)
    print("示例 1：@tool 最小用法")
    print("=" * 60)

    @tool
    def get_current_time() -> str:
        """获取当前系统时间，格式 YYYY-MM-DD HH:MM:SS"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    print("\n[工具元数据]")
    print(f"名称: {get_current_time.name}")
    print(f"描述: {get_current_time.description}")
    print(f"参数: {get_current_time.args}")

    result = get_current_time.invoke({})
    print(f"\n[直接调用]: {result}")

    print("\n💡 @tool 自动提取函数签名 + docstring")


def example_2_tool_with_params():
    """带参数的工具"""
    print("\n" + "=" * 60)
    print("示例 2：带参数的工具")
    print("=" * 60)

    print(f"\n天气工具参数: {get_weather.args}")

    print("\n[测试调用]")
    print(f"  北京 → {get_weather.invoke({'city': '北京'})}")
    print(f"  深圳 → {get_weather.invoke({'city': '深圳'})}")


def example_3_multiple_params():
    """多参数工具"""
    print("\n" + "=" * 60)
    print("示例 3：多参数工具")
    print("=" * 60)

    print(f"\n计算器参数: {calculator.args}")

    tests = [
        {"operation": "add", "a": 10, "b": 5},
        {"operation": "multiply", "a": 7, "b": 8},
        {"operation": "divide", "a": 20, "b": 4}
    ]

    print("\n[测试调用]")
    for t in tests:
        print(f"  {t} → {calculator.invoke(t)}")


def example_4_optional_params():
    """可选参数"""
    print("\n" + "=" * 60)
    print("示例 4：可选参数")
    print("=" * 60)

    print(f"\n搜索工具参数: {web_search.args}")

    print("\n[仅传必填参数]")
    print(f"  {web_search.invoke({'query': 'LangChain'})}")

    print("\n[覆盖默认值]")
    print(f"  {web_search.invoke({'query': 'Python', 'num_results': 5})}")


def example_5_bind_tools():
    """绑定工具到模型"""
    print("\n" + "=" * 60)
    print("示例 5：bind_tools - Function Calling")
    print("=" * 60)

    model_with_tools = model.bind_tools([get_weather, calculator])
    print("✅ 工具已绑定: [get_weather, calculator]")

    prompt = "北京今天天气怎么样？"
    print(f"\n用户: {prompt}")

    response = model_with_tools.invoke(prompt)

    if response.tool_calls:
        print("\n🛠️ 模型决定调用工具:")
        for tc in response.tool_calls:
            print(f"  工具: {tc['name']}")
            print(f"  参数: {tc['args']}")
    else:
        print(f"\n🤖 直接回复: {response.content}")

    print("\n💡 此时只是生成了调用指令，工具尚未执行")


def example_6_best_practices():
    """最佳实践"""
    print("\n" + "=" * 60)
    print("示例 6：工具开发最佳实践")
    print("=" * 60)

    print("""
✅ 高质量工具建议：

1. Docstring 清晰：用途、参数格式、返回格式
2. 类型注解完整：参数与返回值都标注
3. 返回类型稳定：优先 str 或 JSON 字符串
4. 内部异常兜底：不要让异常中断 Agent
5. 单一职责：一个工具只做一件事
""")


def main():
    print("\n" + "=" * 60)
    print(" LangChain 1.0 - 04 自定义工具")
    print("=" * 60)

    try:
        example_1_simple_tool()
        input("\n[按 Enter 继续...]")
        example_2_tool_with_params()
        input("\n[按 Enter 继续...]")
        example_3_multiple_params()
        input("\n[按 Enter 继续...]")
        example_4_optional_params()
        input("\n[按 Enter 继续...]")
        example_5_bind_tools()
        input("\n[按 Enter 继续...]")
        example_6_best_practices()

        print("\n" + "=" * 60)
        print(" 🎉 完成！")
        print("=" * 60)
        print("\n技能点亮：")
        print("  ✅ @tool 装饰器")
        print("  ✅ 参数 schema")
        print("  ✅ Optional 参数")
        print("  ✅ bind_tools")

    except KeyboardInterrupt:
        print("\n\n程序已中断")
    except Exception as e:
        print(f"\n❌ 错误：{e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
