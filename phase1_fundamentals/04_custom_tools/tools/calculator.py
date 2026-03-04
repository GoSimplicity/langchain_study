"""自定义工具：计算器"""

from langchain_core.tools import tool


@tool
def calculator(operation: str, a: float, b: float) -> str:
    """
    执行基本的数学计算。

    参数:
        operation: 运算类型 - add/subtract/multiply/divide
        a: 第一个数字
        b: 第二个数字

    返回:
        计算结果字符串
    """
    ops = {
        "add": lambda x, y: x + y,
        "subtract": lambda x, y: x - y,
        "multiply": lambda x, y: x * y,
        "divide": lambda x, y: x / y if y != 0 else "错误：除数不能为零"
    }

    if operation not in ops:
        return f"不支持的运算：{operation}"

    try:
        result = ops[operation](a, b)
        return f"{a} {operation} {b} = {result}"
    except Exception as e:
        return f"计算错误：{e}"


if __name__ == "__main__":
    print("测试计算器：")
    print(f"  {calculator.invoke({'operation': 'add', 'a': 10, 'b': 5})}")
    print(f"  {calculator.invoke({'operation': 'multiply', 'a': 7, 'b': 8})}")
