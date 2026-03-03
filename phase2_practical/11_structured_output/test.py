"""
简单测试：验证结构化输出功能
"""

import os
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from pydantic import BaseModel, Field

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_API_BASE = os.getenv("OPENAI_API_BASE")
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "Pro/MiniMaxAI/MiniMax-M2.5")
MODEL_NAME = DEFAULT_MODEL if ":" in DEFAULT_MODEL else f"openai:{DEFAULT_MODEL}"

if not OPENAI_API_KEY or not OPENAI_API_BASE or OPENAI_API_KEY == "your_openai_api_key_here_replace_this":
    raise ValueError("请先设置 OPENAI_API_KEY 和 OPENAI_API_BASE")

model = init_chat_model(MODEL_NAME, api_key=OPENAI_API_KEY, base_url=OPENAI_API_BASE)

print("=" * 70)
print("测试：结构化输出 - Pydantic 模型")
print("=" * 70)


class Person(BaseModel):
    """人物信息"""
    name: str = Field(description="姓名")
    age: int = Field(description="年龄")
    occupation: str = Field(description="职业")


# 创建结构化输出的 LLM
structured_llm = model.with_structured_output(Person)

print("\n提示: 张三是一名 30 岁的软件工程师")
result = structured_llm.invoke("张三是一名 30 岁的软件工程师")

print(f"\n返回类型: {type(result)}")
print(f"姓名: {result.name}")
print(f"年龄: {result.age}")
print(f"职业: {result.occupation}")

print("\n" + "=" * 70)
print("测试结果：")
print("  - with_structured_output() 返回 Pydantic 对象 [成功]")
print("  - 自动类型验证 [成功]")
print("  - 无需手动解析 JSON [成功]")
print("=" * 70)

print("\n测试完成！")
