import logging
from datetime import datetime, timezone
from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.messages import SystemMessage, BaseMessage
from langchain_core.tools import tool
from langchain_ollama import ChatOllama

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@tool
def get_current_time() -> dict:
    """Return the current UTC time in ISO-8601 format.
    Example → {"utc": "2025-05-21T06:42:00Z"}"""
    current_time = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    return {"utc": current_time}

class State(TypedDict):
    messages: list[BaseMessage]

model = ChatOllama(
    model="qwen3:30b-a3b",
    base_url="http://localhost:11434"
).bind_tools([get_current_time])

async def chatbot(state: State):
    system_prompt = SystemMessage(
        content="You are a helpful AI assistant. You have access to a tool named 'get_current_time'. "
                "When the user asks for the current time, you MUST use the 'get_current_time' tool to provide the answer. "
                "For other questions, respond politely."
    )
    
    messages_with_prompt = [system_prompt] + state["messages"]

    response = await model.ainvoke(messages_with_prompt)

    if hasattr(response, 'content') and isinstance(response.content, str):
        response.content = response.content.split("</think>")[-1].strip()

    return {"messages": [response]}

builder = StateGraph(State)

builder.add_node("chatbot", chatbot)
builder.add_node("tools", ToolNode([get_current_time]))

builder.add_edge(START, "chatbot")
builder.add_conditional_edges(
    "chatbot",
    tools_condition,
    {
        "tools": "tools",
        END: END,
    }
)
builder.add_edge("tools", "chatbot")

graph = builder.compile()

__all__ = ["graph"]