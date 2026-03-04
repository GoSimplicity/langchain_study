"""
04 - Custom Tools: 自定义工具与 Function Calling
"""

# 标准库：读取环境变量。
import os
# 标准库：判断平台并处理编码输出。
import sys
# 类型工具：用于可选参数声明。
from typing import Optional

# Windows 终端下，确保中文输出不乱码。
if sys.platform == 'win32':
    import io
    # 重包 stdout，强制 utf-8。
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    # 重包 stderr，强制 utf-8。
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 加载 .env。
from dotenv import load_dotenv
# 初始化模型。
from langchain.chat_models import init_chat_model
# tool 装饰器：把函数包装成 Tool 对象。
from langchain_core.tools import tool

# ============================= 学习说明 =============================
# 这一章请重点关注两个点：
# 1) docstring 会被模型读取，用于决定“何时调用工具”。
# 2) bind_tools 后 response.tool_calls 只是调用指令，还没执行工具。
# ==================================================================

# ============================================================================
# 环境配置与模型初始化
# ============================================================================

# 从 .env 加载配置。
load_dotenv()
# 读取 API key。
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# 读取 base_url。
OPENAI_API_BASE = os.getenv("OPENAI_API_BASE")
# 读取默认模型。
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "gpt-3.5-turbo")
# 补全 provider 前缀。
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

# 初始化全局模型对象。
model = init_chat_model(MODEL_NAME, api_key=OPENAI_API_KEY, base_url=OPENAI_API_BASE)


# ============================================================================
# 工具定义区
# ============================================================================
# 说明：真实项目建议把工具拆到独立目录，这里为了教学集中展示。

@tool
def get_weather(city: str) -> str:
    """
    获取指定城市的当前天气情况。

    参数:
        city: 城市名称，如 "北京", "上海"
    """
    # 模拟天气数据。
    mock_weather_db = {
        "北京": "晴朗，气温 22°C，微风",
        "上海": "多云，气温 26°C，湿度 80%"
    }
    # 按城市查找，查不到返回兜底信息。
    return mock_weather_db.get(city, f"无法获取 {city} 的天气数据。")


@tool
def calculator(operation: str, a: float, b: float) -> str:
    """
    执行基础的数学运算。

    参数:
        operation: 运算类型，支持 add/subtract/multiply/divide
        a: 第一个操作数
        b: 第二个操作数
    """
    try:
        # 分支执行不同运算。
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
        # 避免抛异常中断 Agent，返回字符串错误给模型阅读。
        return f"计算错误: {str(e)}"


@tool
def web_search(query: str, num_results: Optional[int] = 3) -> str:
    """
    在互联网上搜索指定关键词。

    参数:
        query: 搜索关键词
        num_results: 返回结果数量，默认 3
    """
    # 这里返回模拟结果文本。
    return f"检索 '{query}' 成功。共返回了 {num_results} 条模拟结果..."


# ============================================================================
# 示例 1：创建第一个工具
# ============================================================================
def example_1_simple_tool():
    """演示 @tool 最小用法。"""
    print("\n" + "=" * 70)
    print("示例 1：创建第一个工具 (@tool)")
    print("=" * 70)

    # 在函数定义上加 @tool，即可自动产出 Tool 对象。
    @tool
    def get_current_time() -> str:
        """获取当前系统时间，返回格式为 YYYY-MM-DD HH:MM:SS"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 打印工具元数据。
    print("\n[工具元数据 (Metadata)]")
    print(f"名称 (name): {get_current_time.name}")
    print(f"描述 (description): {get_current_time.description}")
    print(f"参数架构 (args schema): {get_current_time.args}")

    # 直接调用工具（本地测试常用）。
    result = get_current_time.invoke({})
    print(f"\n[直接调用结果]: {result}")

    print("\n💡 关键机制：")
    print("  1. @tool 自动提取函数签名 + docstring")
    print("  2. 模型主要依靠 docstring 做工具路由")


# ============================================================================
# 示例 2：带参数的工具
# ============================================================================
def example_2_tool_with_params():
    """演示单参数工具 schema 与调用。"""
    print("\n" + "=" * 70)
    print("示例 2：带参数的工具 (Schema 约束)")
    print("=" * 70)

    # 打印天气工具元数据。
    print("\n[天气工具元数据]")
    print(f"名称: {get_weather.name}")
    print(f"描述: {get_weather.description}")
    print(f"预期参数 (Schema): {get_weather.args}")

    print("\n[执行测试]")
    # 传入北京测试。
    result1 = get_weather.invoke({"city": "北京"})
    print(f"输入 '北京' -> {result1}")

    # 传入未收录城市测试兜底。
    result2 = get_weather.invoke({"city": "深圳"})
    print(f"输入 '深圳' -> {result2}")


# ============================================================================
# 示例 3：多参数工具
# ============================================================================
def example_3_multiple_params():
    """演示多参数工具调用。"""
    print("\n" + "=" * 70)
    print("示例 3：多参数工具 (Calculator)")
    print("=" * 70)

    # 打印计算器 schema。
    print("\n[计算器工具信息]")
    print(f"预期参数 (Schema): {calculator.args}")

    print("\n[执行测试]")
    # 准备多组输入。
    tests = [
        {"operation": "add", "a": 10, "b": 5},
        {"operation": "multiply", "a": 7, "b": 8},
        {"operation": "divide", "a": 20, "b": 4}
    ]

    # 循环测试每组参数。
    for test in tests:
        result = calculator.invoke(test)
        print(f"  入参 {test} -> 结果: {result}")


# ============================================================================
# 示例 4：可选参数工具
# ============================================================================
def example_4_optional_params():
    """演示 Optional 参数与默认值。"""
    print("\n" + "=" * 70)
    print("示例 4：可选参数解析 (Optional Params)")
    print("=" * 70)

    # 打印 search 工具参数 schema。
    print("\n[搜索工具预期参数]")
    print(f"{web_search.args}")

    # 不传 num_results，走默认值。
    print("\n[仅传递必填参数 (触发默认值)]")
    result1 = web_search.invoke({"query": "LangChain 1.0 特性"})
    print(f"输出: {result1}")

    # 显式覆盖默认值。
    print("\n[显式覆盖默认参数]")
    result2 = web_search.invoke({"query": "Python 异步编程", "num_results": 5})
    print(f"输出: {result2}")


# ============================================================================
# 示例 5：工具绑定到模型（核心预览）
# ============================================================================
def example_5_bind_tools():
    """
    演示 bind_tools 后模型如何生成 tool_calls 指令。
    """
    print("\n" + "=" * 70)
    print("示例 5：将工具绑定至模型 (Function Calling 预览)")
    print("=" * 70)

    # 把可用工具列表绑定到模型。
    model_with_tools = model.bind_tools([get_weather, calculator])

    print("✅ 工具已成功注入模型层。当前可用能力：[get_weather, calculator]")

    # 发一个明显需要天气工具的问题。
    prompt = "北京今天天气怎么样？"
    print(f"\n👤 用户提问: {prompt}")

    # 调用绑定了工具的模型。
    response = model_with_tools.invoke(prompt)

    # 如果模型决定调用工具，会在 tool_calls 里给出指令。
    if response.tool_calls:
        print("\n🛠️ 模型决策：需要调用工具！")
        for tool_call in response.tool_calls:
            print(f"  - 命中工具: {tool_call['name']}")
            print(f"  - 提取参数: {tool_call['args']}")
    else:
        # 否则就是直接文本回答。
        print("\n🤖 模型决策：直接回复 (未使用工具)")
        print(f"  - 回复内容: {response.content}")

    print("\n💡 提示：当前只是生成了 tool_calls 指令，工具尚未自动执行。")


# ============================================================================
# 示例 6：工具开发的最佳实践
# ============================================================================
def example_6_best_practices():
    """输出工具开发实践建议。"""
    print("\n" + "=" * 70)
    print("示例 6：自定义工具开发最佳实践 (Best Practices)")
    print("=" * 70)

    print("""
✅ 生产环境高质量工具建议：

1. Docstring 清晰：说明用途、参数格式、返回格式
2. 类型注解完整：参数与返回值都标注类型
3. 返回类型稳定：优先返回 str（或 JSON 字符串）
4. 工具内做异常兜底：不要让异常直接中断主流程
5. 单一职责：一个工具只做一件事
    """)


# ============================================================================
# 主程序
# ============================================================================
def main():
    """按顺序运行本章示例。"""
    # 打印标题。
    print("\n" + "=" * 70)
    print(" LangChain 1.0 基础教程 - 04 自定义工具 (@tool)")
    print("=" * 70)

    try:
        # 示例 1：最小工具。
        example_1_simple_tool()
        input("\n[按 Enter 键继续查看下一个示例...]")

        # 示例 2：单参数。
        example_2_tool_with_params()
        input("\n[按 Enter 键继续查看下一个示例...]")

        # 示例 3：多参数。
        example_3_multiple_params()
        input("\n[按 Enter 键继续查看下一个示例...]")

        # 示例 4：可选参数。
        example_4_optional_params()
        input("\n[按 Enter 键继续查看下一个示例...]")

        # 示例 5：绑定工具。
        example_5_bind_tools()
        input("\n[按 Enter 键继续查看下一个示例...]")

        # 示例 6：最佳实践。
        example_6_best_practices()

        # 结束信息。
        print("\n" + "=" * 70)
        print(" 🎉 本章所有示例执行完毕！")
        print("=" * 70)
        print("\n本章技能树点亮：")
        print("  ✅ @tool 装饰器")
        print("  ✅ 工具 schema 与 docstring")
        print("  ✅ Optional 参数")
        print("  ✅ tool_calls 结构")

    except KeyboardInterrupt:
        # 用户中断。
        print("\n\n⚠️ 程序已被用户手动中断")
    except Exception as e:
        # 打印详细异常。
        print(f"\n❌ 运行出错：{type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()


# 直接运行时执行主流程。
if __name__ == "__main__":
    main()
