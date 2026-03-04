"""自定义工具：天气查询"""

from langchain_core.tools import tool


@tool
def get_weather(city: str) -> str:
    """
    获取指定城市的天气信息。

    参数:
        city: 城市名称，如"北京"、"上海"

    返回:
        天气信息字符串
    """
    weather_data = {
        "北京": "晴天，15°C，空气质量良好",
        "上海": "多云，18°C，有轻微雾霾",
        "深圳": "阴天，22°C，可能有小雨",
        "成都": "小雨，12°C，湿度较高"
    }
    return weather_data.get(city, f"暂无{city}的天气数据")


if __name__ == "__main__":
    print("测试天气工具：")
    print(f"  北京 → {get_weather.invoke({'city': '北京'})}")
    print(f"  上海 → {get_weather.invoke({'city': '上海'})}")
