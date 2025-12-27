"""
Jarvis Reasoning Engine
LangChain-powered tool for complex reasoning and task execution
"""

import asyncio
import logging
from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_react_agent, AgentExecutor
from langchain.prompts import PromptTemplate
from livekit.agents import function_tool

# Tools
from Jarvis_google_search import google_search, get_current_datetime

load_dotenv()

# -----------------------------------------------------------------------------
# Logging
# -----------------------------------------------------------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# -----------------------------------------------------------------------------
# ReAct Prompt
# -----------------------------------------------------------------------------
REASONING_PROMPT = """You are Riko's reasoning engine.

You break down complex user requests and solve them step by step using tools.

Available tools:
{tools}

Tool Names: {tool_names}

Instructions:
- Think step by step
- Use tools when needed
- Give a clear final answer

Format:
Question: {input}
Thought: {agent_scratchpad}
"""

# -----------------------------------------------------------------------------
# Thinking Capability Tool (LiveKit compatible)
# -----------------------------------------------------------------------------
@function_tool(
    name="thinking_capability",
    description=(
        "Advanced reasoning engine for complex, multi-step tasks. "
        "Use when planning, researching, analyzing, or combining multiple tools."
    ),
)
async def thinking_capability(query: str) -> str:
    logger.info(f"🧠 Thinking request: {query[:80]}")

    try:
        # LLM (text-only, stable for reasoning)
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-exp",
            temperature=0.7,
        )

        prompt = PromptTemplate.from_template(REASONING_PROMPT)

        tools = [
            google_search,
            get_current_datetime,
        ]

        agent = create_react_agent(
            llm=llm,
            tools=tools,
            prompt=prompt,
        )

        executor = AgentExecutor(
            agent=agent,
            tools=tools,
            verbose=False,
            max_iterations=10,
            max_execution_time=60,
            handle_parsing_errors=True,
        )

        result = await executor.ainvoke({"input": query})
        return result.get("output", "")

    except asyncio.TimeoutError:
        logger.error("⏱️ Reasoning timeout")
        return "The task took too long. Please try a simpler request."

    except Exception as e:
        logger.exception("❌ Reasoning error")
        return f"An error occurred while processing your request: {e}"


__all__ = ["thinking_capability"]
