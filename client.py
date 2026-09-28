import os
import asyncio
from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent

load_dotenv()

MCP_SERVERS = {
    "file-service": {
        "url": "http://localhost:8000/mcp",
        "transport": "streamable_http",
    },
    "calculator-service": {
        "url": "http://localhost:8001/mcp",
        "transport": "streamable_http",
    },
}

SYSTEM_PROMPT = """You are an inventory assistant.
You can ONLY help with:
- Viewing, adding, updating, and deleting inventory items (using the CSV tools)
- Math calculations (using the calculator tools)

Rules:
- Always use the tools to get data. Never guess inventory values.
- If a question is outside these topics (for example exchange rates, news, weather,
  or general knowledge), reply exactly:
  "Sorry, I can only help with inventory and calculations."
- Never make up numbers or real-time information."""


async def run_chat():
    api_key = os.getenv("GEMINI_API_KEY")

    client = MultiServerMCPClient(MCP_SERVERS)

    tools = await client.get_tools()

    model = ChatGoogleGenerativeAI(model="gemini-3.8-flash", temperature=0, google_api_key=api_key)
    agent = create_agent(model, tools, system_prompt=SYSTEM_PROMPT)

    while True:
        user_text = input("You: ").strip()

        result = await agent.ainvoke({"messages": [{"role": "user", "content": user_text}]})

        assistant_text = result["messages"][-1].text
        print(f"AI: {assistant_text}\n")


if __name__ == "__main__":
    asyncio.run(run_chat())