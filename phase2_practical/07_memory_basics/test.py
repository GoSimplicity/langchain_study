"""
简单测试：验证内存功能
"""

import os
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_API_BASE = os.getenv("OPENAI_API_BASE")
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "Pro/MiniMaxAI/MiniMax-M2.5")
MODEL_NAME = DEFAULT_MODEL if ":" in DEFAULT_MODEL else f"openai:{DEFAULT_MODEL}"

if not OPENAI_API_KEY or not OPENAI_API_BASE or OPENAI_API_KEY == "your_openai_api_key_here_replace_this":
    raise ValueError("请先设置 OPENAI_API_KEY 和 OPENAI_API_BASE")

model = init_chat_model("groq:llama-3.3-70b-versatile", api_key=OPENAI_API_KEY, base_url=OPENAI_API_BASE)

print("=" * 70)
print("测试：InMemorySaver 内存功能")
print("=" * 70)

# 创建带内存的 Agent
agent = create_agent(
    model=model,
    tools=[],
    checkpointer=InMemorySaver()
)

config = {"configurable": {"thread_id": "test_session"}}

print("\n第一轮对话：")
print("用户: 我叫张三")
response1 = agent.invoke(
    {"messages": [{"role": "user", "content": "我叫张三"}]},
    config=config
)
print(f"Agent: {response1['messages'][-1].content}")

print("\n第二轮对话：")
print("用户: 我叫什么？")
response2 = agent.invoke(
    {"messages": [{"role": "user", "content": "我叫什么？"}]},
    config=config
)
print(f"Agent: {response2['messages'][-1].content}")

print("\n" + "=" * 70)
print("内存状态：")
print(f"  总消息数: {len(response2['messages'])}")
print(f"  thread_id: {config['configurable']['thread_id']}")
print("=" * 70)

if "张三" in response2['messages'][-1].content:
    print("\n测试成功！Agent 记住了名字。")
else:
    print("\n警告：Agent 可能没有正确记住")

print("\n测试完成！")
