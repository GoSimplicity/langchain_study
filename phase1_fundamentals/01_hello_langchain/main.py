"""
01 - Hello LangChain: 第一个 LLM 调用
"""

# 标准库：读取环境变量。
import os

# 第三方库：把 .env 文件中的键值加载到进程环境变量里。
from dotenv import load_dotenv
# LangChain 统一模型初始化入口（聊天模型）。
from langchain.chat_models import init_chat_model
# LangChain 消息对象类型（用于结构化对话）。
from langchain_core.messages import HumanMessage, SystemMessage

# ============================= 学习说明 =============================
# 你会看到同一个模型调用在不同输入格式下的行为：
# - 纯字符串
# - 消息对象列表
# - 字典消息列表（生产常用）
# 同时还会看到 response 元数据与错误处理方式。
# ==================================================================

# ============================================================================
# 环境配置
# ============================================================================

# 读取 .env 文件，等价于把 .env 中的键值 export 到当前进程。
load_dotenv()

# 从环境中读取 API key。
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# 从环境中读取可选的 base_url（网关/代理/私有部署常用）。
OPENAI_API_BASE = os.getenv("OPENAI_API_BASE")
# 读取默认模型；如果没配就用 gpt-3.5-turbo。
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "gpt-3.5-turbo")
# 兼容写法：
# - 若 DEFAULT_MODEL 已是 provider:model，直接使用。
# - 若只是 model 名，则自动补 openai: 前缀。
MODEL_NAME = DEFAULT_MODEL if ":" in DEFAULT_MODEL else f"openai:{DEFAULT_MODEL}"

# 检查最关键配置：没有 key 就无法调用模型。
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

# 如果没有配置 OPENAI_API_BASE，且 key 也不像官方 sk- 前缀，则给出警告。
# 注意这里只是“警告”，不是“报错”。
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
    - init_chat_model: 初始化模型实例
    - invoke: 触发一次同步调用
    """
    # 打印分隔线，帮助你在终端里区分示例输出。
    print("\n" + "=" * 70)
    print("示例 1：最简单的 LLM 调用 (纯文本输入)")
    print("=" * 70)

    # 初始化模型对象。
    # 这里用统一接口，不需要关心不同 provider 的具体 SDK 细节。
    model = init_chat_model(
        MODEL_NAME,
        api_key=OPENAI_API_KEY,
        base_url=OPENAI_API_BASE,
    )

    # 准备一个简单问题（纯字符串输入）。
    user_input = "你好！请用一句话介绍什么是量子纠缠。"
    # 打印用户输入，方便对照输出。
    print(f"用户输入: {user_input}")

    # 发起调用，返回的是 AIMessage 对象，不是纯字符串。
    response = model.invoke(user_input)

    # 读取主要文本内容。
    print(f"AI 回复: {response.content}")
    # 打印返回类型，建立“response 是对象”的意识。
    print(f"\n返回对象类型: {type(response).__name__}")


# ============================================================================
# 示例 2：使用消息列表进行对话
# ============================================================================
def example_2_messages():
    """
    示例2：使用消息对象列表

    你会看到：
    - SystemMessage 用于定义角色/行为
    - HumanMessage 表示用户输入
    - 把 AI 回复 append 回历史后，模型可继续上下文对话
    """
    print("\n" + "=" * 70)
    print("示例 2：使用显式消息对象构建对话")
    print("=" * 70)

    # 初始化模型。
    model = init_chat_model(
        MODEL_NAME,
        api_key=OPENAI_API_KEY,
        base_url=OPENAI_API_BASE,
    )

    # 构建初始消息历史（系统 + 用户）。
    messages = [
        SystemMessage(content="你是一个友好的 Python 编程助手，擅长用简单易懂的方式解释编程概念。回答尽量简短。"),
        HumanMessage(content="什么是 Python 装饰器？"),
    ]

    # 打印当前上下文。
    print("系统提示:", messages[0].content)
    print("用户问题:", messages[1].content)

    # 把完整消息历史交给模型。
    response = model.invoke(messages)
    print(f"\nAI 回复:\n{response.content}")

    # 把 AI 回复写回历史（这一步是多轮对话关键）。
    messages.append(response)
    # 追加第二轮用户问题。
    messages.append(HumanMessage(content="能给我一个简单的代码例子吗？"))

    print("\n" + "-" * 70)
    print("继续对话...")
    print("用户问题:", messages[-1].content)

    # 再次传入“完整历史”，模型才能感知上下文。
    response2 = model.invoke(messages)
    print(f"\nAI 回复:\n{response2.content}")


# ============================================================================
# 示例 3：使用字典格式的消息
# ============================================================================
def example_3_dict_messages():
    """
    示例3：使用字典格式的消息

    字典格式最常见：
    {"role": "system|user|assistant", "content": "..."}
    便于序列化、存储和跨服务传递。
    """
    print("\n" + "=" * 70)
    print("示例 3：使用字典格式的消息（生产推荐）")
    print("=" * 70)

    # 初始化模型。
    model = init_chat_model(
        MODEL_NAME,
        api_key=OPENAI_API_KEY,
        base_url=OPENAI_API_BASE,
    )

    # 用字典形式组织消息。
    messages = [
        {"role": "system", "content": "你是一个专业的数学老师。"},
        {"role": "user", "content": "什么是斐波那契数列？用一句话解释。"},
    ]

    # 打印消息列表内容，方便对照。
    print("消息列表:")
    for msg in messages:
        print(f"  {msg['role']}: {msg['content']}")

    # 直接调用。
    response = model.invoke(messages)
    print(f"\nAI 回复:\n{response.content}")


# ============================================================================
# 示例 4：配置模型参数
# ============================================================================
def example_4_model_parameters():
    """
    示例4：配置模型参数

    关注两个常用参数：
    - temperature：控制随机性
    - max_tokens：限制输出长度
    """
    print("\n" + "=" * 70)
    print("示例 4：配置模型参数 (Temperature 控制)")
    print("=" * 70)

    # 创建低温模型：更稳定、更一致。
    model_deterministic = init_chat_model(
        MODEL_NAME,
        api_key=OPENAI_API_KEY,
        base_url=OPENAI_API_BASE,
        temperature=0.0,
        max_tokens=200,
    )

    # 固定同一提示词用于对比。
    prompt = "写一个关于春天的四字成语。"

    print(f"提示词: {prompt}")
    print("\n[使用 temperature=0.0 (严谨/确定性输出)]")

    # 连续调用两次，观察是否趋于一致。
    for i in range(2):
        response = model_deterministic.invoke(prompt)
        print(f"  第 {i + 1} 次: {response.content}")

    print("\n" + "-" * 70)

    # 创建高温模型：更发散、更有变化。
    model_creative = init_chat_model(
        MODEL_NAME,
        api_key=OPENAI_API_KEY,
        base_url=OPENAI_API_BASE,
        temperature=1.2,
        max_tokens=200,
    )

    print("\n[使用 temperature=1.2 (发散/创造性输出)]")

    # 再调用两次，对比输出差异。
    for i in range(2):
        response = model_creative.invoke(prompt)
        print(f"  第 {i + 1} 次: {response.content}")


# ============================================================================
# 示例 5：理解 invoke 方法的返回值
# ============================================================================
def example_5_response_structure():
    """
    示例5：深入理解 invoke 返回值

    invoke 返回 AIMessage，常看字段：
    - content
    - usage_metadata
    - response_metadata
    - id
    """
    print("\n" + "=" * 70)
    print("示例 5：invoke 返回值结构解析 (AIMessage)")
    print("=" * 70)

    # 初始化模型。
    model = init_chat_model(
        MODEL_NAME,
        api_key=OPENAI_API_KEY,
        base_url=OPENAI_API_BASE,
    )

    # 发起一次调用。
    response = model.invoke("用一句话解释为什么天空是蓝色的。")

    # 读取主要文本内容。
    print("1. 核心内容 (content):")
    print(f"   {response.content}\n")

    # 读取标准化 token 统计（若 provider 返回）。
    print("2. 消耗统计 (usage_metadata) - LangChain 1.0 特性:")
    if response.usage_metadata:
        usage = response.usage_metadata
        print(f"   输入 tokens: {usage.get('input_tokens', 'N/A')}")
        print(f"   输出 tokens: {usage.get('output_tokens', 'N/A')}")
        print(f"   总计 tokens: {usage.get('total_tokens', 'N/A')}\n")
    else:
        print("   当前模型暂未返回标准 token 统计数据\n")

    # 打印原始响应元数据（不同 provider 字段会不同）。
    print("3. 原始响应元数据 (response_metadata):")
    for key, value in response.response_metadata.items():
        print(f"   {key}: {value}")

    # 打印消息 ID，用于日志追踪或调试。
    print(f"\n4. 消息 ID: {response.id}")


# ============================================================================
# 示例 6：错误处理
# ============================================================================
def example_6_error_handling():
    """
    示例6：正确的错误处理

    目标：给出可用于生产的最小错误处理骨架。
    """
    print("\n" + "=" * 70)
    print("示例 6：网络与 API 错误处理最佳实践")
    print("=" * 70)

    try:
        # 初始化模型，并设置 timeout 防止无限等待。
        model = init_chat_model(
            MODEL_NAME,
            api_key=OPENAI_API_KEY,
            base_url=OPENAI_API_BASE,
            timeout=10,
        )

        # 简单探活调用。
        response = model.invoke("测试连接是否正常。")
        print(f"✅ 成功调用模型！回复: {response.content}")

    except ValueError as e:
        # 配置错误（比如 key 缺失）。
        print(f"❌ 配置错误: {e}")
    except ConnectionError as e:
        # 网络层错误（网关不可达、代理异常等）。
        print(f"❌ 网络错误 (请检查 base_url 或代理): {e}")
    except Exception as e:
        # 兜底异常（鉴权失败、限流等也可能落这里）。
        print(f"❌ 发生异常: {type(e).__name__}: {e}")


# ============================================================================
# 示例 7：多模型对比
# ============================================================================
def example_7_multiple_models():
    """
    示例7：多模型一键切换

    重点：只改模型标识字符串，调用接口保持不变。
    """
    print("\n" + "=" * 70)
    print("示例 7：对比不同模型的切换")
    print("=" * 70)

    # 这里保留两个位置，便于你自行替换成不同模型做对比。
    models_to_test = [
        MODEL_NAME,
        MODEL_NAME,
    ]

    # 固定提示词，避免变量干扰对比。
    prompt = "你是谁？请简短回答。"
    print(f"提示词: {prompt}\n")

    # 逐个模型测试。
    for model_name in models_to_test:
        try:
            print(f"正在使用模型: [{model_name}]")
            print("-" * 50)

            # 初始化当前模型。
            model = init_chat_model(
                model_name,
                api_key=OPENAI_API_KEY,
                base_url=OPENAI_API_BASE,
                temperature=0.5,
            )

            # 调用并输出结果。
            response = model.invoke(prompt)
            print(f"回复: {response.content}\n")

        except Exception as e:
            # 某些模型可能无权限或名称无效，打印并继续下一个。
            print(f"⚠️ 模型 {model_name} 调用失败 (可能当前 API Key 无权限访问该模型): {type(e).__name__}\n")


# ============================================================================
# 主程序
# ============================================================================
def main():
    """
    主程序：按顺序运行所有示例

    推荐学习顺序：
    1) 简单调用 -> 2) 消息格式 -> 3) 参数控制 -> 4) 返回值解析 -> 5) 异常处理
    """
    # 打印章节标题。
    print("\n" + "=" * 70)
    print(" LangChain 1.0 基础教程 - 第一个 LLM 调用")
    print("=" * 70)
    # 打印当前模型标识。
    print(f"🔧 当前加载的模型标识: {MODEL_NAME}")
    # 如果存在 base_url，也打印出来便于排查网络路径。
    if OPENAI_API_BASE:
        print(f"🌐 自定义 API 节点: {OPENAI_API_BASE}")

    try:
        # 示例 1：最小可用调用。
        example_1_simple_invoke()
        # 示例 2：消息对象多轮。
        example_2_messages()
        # 示例 3：字典消息格式。
        example_3_dict_messages()
        # 示例 4：参数对比。
        example_4_model_parameters()
        # 示例 5：返回值结构。
        example_5_response_structure()
        # 示例 6：错误处理。
        example_6_error_handling()
        # 示例 7：模型切换。
        example_7_multiple_models()

        # 打印完成提示。
        print("\n" + "=" * 70)
        print(" 🎉 所有示例运行完成！")
        print("=" * 70)

    except Exception as e:
        # 打印未捕获异常（学习阶段建议保留完整栈）。
        print(f"\n❌ 运行过程中发生未捕获异常: {e}")
        import traceback
        traceback.print_exc()


# 只有在直接运行本文件时才执行 main。
if __name__ == "__main__":
    main()
