"""
04 - Custom Tools: 自定义工具与 Function Calling
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
# 工具定义区 (Tools Definition)
# ============================================================================
# 💡 最佳实践：在实际工程中，建议将这些工具抽取到独立的 tools/ 目录下。
# 为了演示脚本的开箱即用，我们在此处直接定义它们。

@tool
def get_weather(city: str) -> str:
    """
    获取指定城市的当前天气情况。

    参数:
        city: 城市名称，如 "北京", "上海"
    """
    # 这里模拟调用真实的天气 API
    mock_weather_db = {
        "北京": "晴朗，气温 22°C，微风",
        "上海": "多云，气温 26°C，湿度 80%"
    }
    return mock_weather_db.get(city, f"无法获取 {city} 的天气数据。")


@tool
def calculator(operation: str, a: float, b: float) -> str:
    """
    执行基础的数学运算。

    参数:
        operation: 运算类型。支持的值包括 "add"(加), "subtract"(减), "multiply"(乘), "divide"(除)
        a: 第一个操作数
        b: 第二个操作数
    """
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
            return f"不支持的运算类型: {operation}"
    except Exception as e:
        return f"计算错误: {str(e)}"


@tool
def web_search(query: str, num_results: Optional[int] = 3) -> str:
    """
    在互联网上搜索指定关键词。

    参数:
        query: 搜索关键词
        num_results: 返回的搜索结果数量，默认为 3
    """
    return f"检索 '{query}' 成功。共返回了 {num_results} 条模拟结果..."


# ============================================================================
# 示例 1：创建第一个工具
# ============================================================================
def example_1_simple_tool():
    """
    核心概念：使用 @tool 装饰器

    将一个普通的 Python 函数转换为 LangChain Tool 对象。
    """
    print("\n" + "=" * 70)
    print("示例 1：创建第一个工具 (@tool)")
    print("=" * 70)

    @tool
    def get_current_time() -> str:
        """获取当前系统时间，返回格式为 YYYY-MM-DD HH:MM:SS"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    print("\n[工具元数据 (Metadata)]")
    print(f"名称 (name): {get_current_time.name}")
    print(f"描述 (description): {get_current_time.description}")
    print(f"参数架构 (args schema): {get_current_time.args}")

    # 调用工具
    result = get_current_time.invoke({})
    print(f"\n[直接调用结果]: {result}")

    print("\n💡 关键机制：")
    print("  1. @tool 装饰器自动提取函数签名 (Signature) 和文档字符串 (Docstring)。")
    print("  2. Docstring 是重中之重！大模型依赖它来进行工具路由 (Tool Routing)。")


# ============================================================================
# 示例 2：带参数的工具
# ============================================================================
def example_2_tool_with_params():
    """
    演示：参数的提取与执行
    """
    print("\n" + "=" * 70)
    print("示例 2：带参数的工具 (Schema 约束)")
    print("=" * 70)

    print("\n[天气工具元数据]")
    print(f"名称: {get_weather.name}")
    print(f"描述: {get_weather.description}")
    print(f"预期参数 (Schema): {get_weather.args}")

    # 以字典形式传入参数
    print("\n[执行测试]")
    result1 = get_weather.invoke({"city": "北京"})
    print(f"输入 '北京' -> {result1}")

    result2 = get_weather.invoke({"city": "深圳"})
    print(f"输入 '深圳' -> {result2}")


# ============================================================================
# 示例 3：多参数工具
# ============================================================================
def example_3_multiple_params():
    """
    演示：复杂计算器的多参数映射
    """
    print("\n" + "=" * 70)
    print("示例 3：多参数工具 (Calculator)")
    print("=" * 70)

    print("\n[计算器工具信息]")
    print(f"预期参数 (Schema): {calculator.args}")

    print("\n[执行测试]")
    tests = [
        {"operation": "add", "a": 10, "b": 5},
        {"operation": "multiply", "a": 7, "b": 8},
        {"operation": "divide", "a": 20, "b": 4}
    ]

    for test in tests:
        result = calculator.invoke(test)
        print(f"  入参 {test} -> 结果: {result}")


# ============================================================================
# 示例 4：可选参数工具
# ============================================================================
def example_4_optional_params():
    """
    演示：Type Hints (类型提示) 中的 Optional 关键字使用
    """
    print("\n" + "=" * 70)
    print("示例 4：可选参数解析 (Optional Params)")
    print("=" * 70)

    print("\n[搜索工具预期参数]")
    print(f"{web_search.args}")

    print("\n[仅传递必填参数 (触发默认值)]")
    result1 = web_search.invoke({"query": "LangChain 1.0 特性"})
    print(f"输出: {result1}")

    print("\n[显式覆盖默认参数]")
    result2 = web_search.invoke({"query": "Python 异步编程", "num_results": 5})
    print(f"输出: {result2}")


# ============================================================================
# 示例 5：工具绑定到模型（核心预览）
# ============================================================================
def example_5_bind_tools():
    """
    核心操作：将工具架构 (Schema) 注入到 LLM 中。
    让模型知道它"拥有"哪些能力。
    """
    print("\n" + "=" * 70)
    print("示例 5：将工具绑定至模型 (Function Calling 预览)")
    print("=" * 70)

    # 通过 bind_tools 将工具集合注入给模型
    model_with_tools = model.bind_tools([get_weather, calculator])

    print("✅ 工具已成功注入模型层。当前可用能力：[get_weather, calculator]")

    # 向模型提问，触发工具路由
    prompt = "北京今天天气怎么样？"
    print(f"\n👤 用户提问: {prompt}")

    response = model_with_tools.invoke(prompt)

    # 检查模型是否决定调用工具
    if response.tool_calls:
        print(f"\n🛠️ 模型决策：需要调用工具！")
        for tool_call in response.tool_calls:
            print(f"  - 命中工具: {tool_call['name']}")
            print(f"  - 提取参数: {tool_call['args']}")
    else:
        print(f"\n🤖 模型决策：直接回复 (未使用工具)")
        print(f"  - 回复内容: {response.content}")

    print("\n💡 提示：目前模型只是『生成了调用工具的指令(tool_calls)』，工具本身还未被真正执行。")
    print("   如何自动执行工具并将结果返还给模型？我们将在下一章 Agent 中解决。")


# ============================================================================
# 示例 6：工具开发的最佳实践
# ============================================================================
def example_6_best_practices():
    """
    工程经验总结
    """
    print("\n" + "=" * 70)
    print("示例 6：自定义工具开发最佳实践 (Best Practices)")
    print("=" * 70)

    print("""
✅ 生产环境的高质量工具应具备以下特质：

1. 极致清晰的 Docstring：
   - 模型不看代码逻辑，只看 docstring。
   - 清楚写明：做什么、参数什么格式、返回值什么格式。

2. 严格的类型提示 (Type Hints)：
   - 使用 str, int, float, bool。
   - 允许为空的参数使用 Optional[T]。

3. 稳定的返回类型：
   - 强烈建议统一返回 `str`。
   - 复杂数据结构（如 List/Dict）应使用 json.dumps() 序列化为字符串返回。

4. 防御性编程 (错误兜底)：
   - 工具内部必须有 try-except。
   - 不要抛出异常让主程序崩溃，而是返回友好的错误字符串（如 "搜索失败，API超时"），
     这样模型能"阅读"到错误，并尝试换种方式或向用户道歉。

5. 遵循单一职责原则 (SRP)：
   - 一个工具只做一件事。不要设计包含巨大 if-else 逻辑的万能工具。
    """)


# ============================================================================
# 主程序
# ============================================================================
def main():
    print("\n" + "=" * 70)
    print(" LangChain 1.0 基础教程 - 04 自定义工具 (@tool)")
    print("=" * 70)

    try:
        example_1_simple_tool()
        input("\n[按 Enter 键继续查看下一个示例...]")

        example_2_tool_with_params()
        input("\n[按 Enter 键继续查看下一个示例...]")

        example_3_multiple_params()
        input("\n[按 Enter 键继续查看下一个示例...]")

        example_4_optional_params()
        input("\n[按 Enter 键继续查看下一个示例...]")

        example_5_bind_tools()
        input("\n[按 Enter 键继续查看下一个示例...]")

        example_6_best_practices()

        print("\n" + "=" * 70)
        print(" 🎉 本章所有示例执行完毕！")
        print("=" * 70)
        print("\n本章技能树点亮：")
        print("  ✅ 掌握 @tool 装饰器的使用方法")
        print("  ✅ 理解 Docstring 和 Type Hints 对大模型路由的决定性作用")
        print("  ✅ 掌握可选参数与多参数的解析逻辑")
        print("  ✅ 体验模型底层的 tool_calls (Function Calling) 结构")
        print("\n下一章预告：")
        print("  - 05_simple_agent: 赋予模型执行力，构建能够自动调用工具的 Agent！")

    except KeyboardInterrupt:
        print("\n\n⚠️ 程序已被用户手动中断")
    except Exception as e:
        print(f"\n❌ 运行出错：{type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
