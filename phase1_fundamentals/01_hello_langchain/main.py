"""
01 - Hello LangChain: 第一个 LLM 调用
"""

import os
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, SystemMessage

# ============================================================================
# 环境配置
# ============================================================================

# 加载环境变量
load_dotenv()

# 读取配置项
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_API_BASE = os.getenv("OPENAI_API_BASE")
# 默认使用通用大模型名称，如果没有带 provider，则自动加上 openai:
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "gpt-3.5-turbo")
MODEL_NAME = DEFAULT_MODEL if ":" in DEFAULT_MODEL else f"openai:{DEFAULT_MODEL}"

# 验证 API 密钥是否存在
if not OPENAI_API_KEY:
    raise ValueError(
        "\n" + "=" * 70 + "\n"
        "❌ 错误：未找到 OPENAI_API_KEY 环境变量！\n"
        "=" * 70 + "\n"
        "请按照以下步骤设置环境变量：\n\n"
        "1️⃣ 访问提供商控制台获取 API 密钥\n"
        "2️⃣ 复制 .env.example 为 .env\n"
        "3️⃣ 在 .env 文件中填入你的配置：\n"
        "   OPENAI_API_KEY=sk-your_actual_key_here\n"
        "   OPENAI_API_BASE=https://api.openai.com/v1  # (可选) 如果使用中转或私有部署\n"
        "4️⃣ 重新运行程序\n"
        "=" * 70
    )

# 仅在未配置自定义 BASE_URL 时，才强校验 sk- 前缀 (因为很多第三方平台的 key 不是 sk- 开头)
if not OPENAI_API_BASE and not OPENAI_API_KEY.startswith("sk-"):
    print("\n⚠️  警告：你的 OPENAI_API_KEY 格式可能不正确")
    print("   官方 OpenAI API 密钥通常以 'sk-' 开头")
    print("   如果你使用的是第三方转发服务，请确保在 .env 中配置了 OPENAI_API_BASE\n")


# ============================================================================
# 示例 1：最简单的 LLM 调用
# ============================================================================
def example_1_simple_invoke():
    """
    示例1：最简单的模型调用

    核心概念：
    - init_chat_model: 用于初始化聊天模型的统一接口
    - invoke: 同步调用模型的方法
    """
    print("\n" + "=" * 70)
    print("示例 1：最简单的 LLM 调用 (纯文本输入)")
    print("=" * 70)

    # 初始化模型
    # 格式：init_chat_model("提供商:模型名称")
    model = init_chat_model(
        MODEL_NAME,
        api_key=OPENAI_API_KEY,
        base_url=OPENAI_API_BASE,
    )

    # 使用字符串直接调用模型
    user_input = "你好！请用一句话介绍什么是量子纠缠。"
    print(f"用户输入: {user_input}")

    response = model.invoke(user_input)

    print(f"AI 回复: {response.content}")
    print(f"\n返回对象类型: {type(response).__name__}")


# ============================================================================
# 示例 2：使用消息列表进行对话
# ============================================================================
def example_2_messages():
    """
    示例2：使用消息对象列表

    核心概念：
    - SystemMessage: 系统消息，用于设定 AI 的行为和角色
    - HumanMessage: 用户消息
    - AIMessage: AI 的回复消息

    消息列表允许你构建多轮对话历史
    """
    print("\n" + "=" * 70)
    print("示例 2：使用显式消息对象构建对话")
    print("=" * 70)

    model = init_chat_model(
        MODEL_NAME,
        api_key=OPENAI_API_KEY,
        base_url=OPENAI_API_BASE,
    )

    # 构建消息列表
    messages = [
        SystemMessage(content="你是一个友好的 Python 编程助手，擅长用简单易懂的方式解释编程概念。回答尽量简短。"),
        HumanMessage(content="什么是 Python 装饰器？"),
    ]

    print("系统提示:", messages[0].content)
    print("用户问题:", messages[1].content)

    # 调用模型
    response = model.invoke(messages)
    print(f"\nAI 回复:\n{response.content}")

    # 继续对话：将 AI 的回复添加到对话历史
    messages.append(response)  # AIMessage
    messages.append(HumanMessage(content="能给我一个简单的代码例子吗？"))

    print("\n" + "-" * 70)
    print("继续对话...")
    print("用户问题:", messages[-1].content)

    response2 = model.invoke(messages)
    print(f"\nAI 回复:\n{response2.content}")


# ============================================================================
# 示例 3：使用字典格式的消息
# ============================================================================
def example_3_dict_messages():
    """
    示例3：使用字典格式的消息

    LangChain 1.0 推荐的字典格式，兼容性好，易于 JSON 序列化：
    {"role": "system"/"user"/"assistant", "content": "消息内容"}
    """
    print("\n" + "=" * 70)
    print("示例 3：使用字典格式的消息（生产推荐）")
    print("=" * 70)

    model = init_chat_model(
        MODEL_NAME,
        api_key=OPENAI_API_KEY,
        base_url=OPENAI_API_BASE,
    )

    # 使用字典格式构建消息
    messages = [
        {"role": "system", "content": "你是一个专业的数学老师。"},
        {"role": "user", "content": "什么是斐波那契数列？用一句话解释。"},
    ]

    print("消息列表:")
    for msg in messages:
        print(f"  {msg['role']}: {msg['content']}")

    response = model.invoke(messages)
    print(f"\nAI 回复:\n{response.content}")


# ============================================================================
# 示例 4：配置模型参数
# ============================================================================
def example_4_model_parameters():
    """
    示例4：配置模型参数

    init_chat_model 支持的常用参数：
    - temperature: 控制输出的随机性（0.0-2.0）
      * 0.0: 最严谨、确定性
      * 1.0: 默认值，平衡创造性和一致性
    - max_tokens: 限制单次生成消息的最大长度
    """
    print("\n" + "=" * 70)
    print("示例 4：配置模型参数 (Temperature 控制)")
    print("=" * 70)

    # 创建一个温度较低的模型（更严谨确定）
    model_deterministic = init_chat_model(
        MODEL_NAME,
        api_key=OPENAI_API_KEY,
        base_url=OPENAI_API_BASE,
        temperature=0.0,
        max_tokens=200
    )

    prompt = "写一个关于春天的四字成语。"

    print(f"提示词: {prompt}")
    print("\n[使用 temperature=0.0 (严谨/确定性输出)]")

    # 调用两次，观察输出的一致性
    for i in range(2):
        response = model_deterministic.invoke(prompt)
        print(f"  第 {i + 1} 次: {response.content}")

    print("\n" + "-" * 70)

    # 创建一个温度较高的模型（更随机/发散）
    model_creative = init_chat_model(
        MODEL_NAME,
        api_key=OPENAI_API_KEY,
        base_url=OPENAI_API_BASE,
        temperature=1.2,
        max_tokens=200
    )

    print("\n[使用 temperature=1.2 (发散/创造性输出)]")

    # 调用两次，观察输出的差异
    for i in range(2):
        response = model_creative.invoke(prompt)
        print(f"  第 {i + 1} 次: {response.content}")


# ============================================================================
# 示例 5：理解 invoke 方法的返回值
# ============================================================================
def example_5_response_structure():
    """
    示例5：深入理解 invoke 返回值

    invoke 方法返回一个 AIMessage 对象，LangChain 1.0 标准化了其属性：
    - content: 模型的文本回复
    - response_metadata: 原始提供商响应元数据
    - usage_metadata: 标准化的 Token 使用量统计
    - id: 消息 ID
    """
    print("\n" + "=" * 70)
    print("示例 5：invoke 返回值结构解析 (AIMessage)")
    print("=" * 70)

    model = init_chat_model(
        MODEL_NAME,
        api_key=OPENAI_API_KEY,
        base_url=OPENAI_API_BASE,
    )

    response = model.invoke("用一句话解释为什么天空是蓝色的。")

    print("1. 核心内容 (content):")
    print(f"   {response.content}\n")

    print("2. 消耗统计 (usage_metadata) - LangChain 1.0 特性:")
    if response.usage_metadata:
        usage = response.usage_metadata
        print(f"   输入 tokens: {usage.get('input_tokens', 'N/A')}")
        print(f"   输出 tokens: {usage.get('output_tokens', 'N/A')}")
        print(f"   总计 tokens: {usage.get('total_tokens', 'N/A')}\n")
    else:
        print("   当前模型暂未返回标准 token 统计数据\n")

    print("3. 原始响应元数据 (response_metadata):")
    for key, value in response.response_metadata.items():
        print(f"   {key}: {value}")

    print(f"\n4. 消息 ID: {response.id}")


# ============================================================================
# 示例 6：错误处理
# ============================================================================
def example_6_error_handling():
    """
    示例6：正确的错误处理
    """
    print("\n" + "=" * 70)
    print("示例 6：网络与 API 错误处理最佳实践")
    print("=" * 70)

    try:
        model = init_chat_model(
            MODEL_NAME,
            api_key=OPENAI_API_KEY,
            base_url=OPENAI_API_BASE,
            timeout=10  # 设置 10 秒超时
        )

        response = model.invoke("测试连接是否正常。")
        print(f"✅ 成功调用模型！回复: {response.content}")

    except ValueError as e:
        print(f"❌ 配置错误: {e}")
    except ConnectionError as e:
        print(f"❌ 网络错误 (请检查 base_url 或代理): {e}")
    except Exception as e:
        # OpenAI 接口常见错误：AuthenticationError, RateLimitError 等
        print(f"❌ 发生异常: {type(e).__name__}: {e}")


# ============================================================================
# 示例 7：多模型对比
# ============================================================================
def example_7_multiple_models():
    """
    示例7：多模型一键切换

    体现 LangChain 解耦架构的优势：只需更改字符串标识。
    """
    print("\n" + "=" * 70)
    print("示例 7：对比不同模型的切换")
    print("=" * 70)

    # 尝试调用默认模型和一个基础模型
    models_to_test = [
        MODEL_NAME,
        MODEL_NAME  # 假设环境中支持这个经典名称的路由
    ]

    prompt = "你是谁？请简短回答。"
    print(f"提示词: {prompt}\n")

    for model_name in models_to_test:
        try:
            print(f"正在使用模型: [{model_name}]")
            print("-" * 50)

            model = init_chat_model(
                model_name,
                api_key=OPENAI_API_KEY,
                base_url=OPENAI_API_BASE,
                temperature=0.5
            )

            response = model.invoke(prompt)
            print(f"回复: {response.content}\n")

        except Exception as e:
            print(f"⚠️ 模型 {model_name} 调用失败 (可能当前 API Key 无权限访问该模型): {type(e).__name__}\n")


# ============================================================================
# 主程序
# ============================================================================
def main():
    """
    主程序：按顺序运行所有示例
    """
    print("\n" + "=" * 70)
    print(" LangChain 1.0 基础教程 - 第一个 LLM 调用")
    print("=" * 70)
    print(f"🔧 当前加载的模型标识: {MODEL_NAME}")
    if OPENAI_API_BASE:
        print(f"🌐 自定义 API 节点: {OPENAI_API_BASE}")

    try:
        example_1_simple_invoke()
        example_2_messages()
        example_3_dict_messages()
        example_4_model_parameters()
        example_5_response_structure()
        example_6_error_handling()
        example_7_multiple_models()

        print("\n" + "=" * 70)
        print(" 🎉 所有示例运行完成！")
        print("=" * 70)

    except Exception as e:
        print(f"\n❌ 运行过程中发生未捕获异常: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()