from langchain_openai import ChatOpenAI
from langchain.agents import initialize_agent, AgentType
from langchain.memory import ConversationBufferMemory
from app.services.tools.llm_tools import all_tools
import os

# Load OpenAI API key from environment
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Initialize LLM
llm = ChatOpenAI(
    model_name="gpt-4",
    temperature=0.7,
    openai_api_key=OPENAI_API_KEY
)

# Initialize memory
memory = ConversationBufferMemory(return_messages=True)

# Initialize agent with tools, LLM, and memory
agent = initialize_agent(
    tools=all_tools,
    llm=llm,
    agent=AgentType.OPENAI_FUNCTIONS,
    memory=memory,
    verbose=True
)

def chat_with_agent(user_message: str) -> str:
    """
    Run the agent with the user message and return the response.
    """
    try:
        response = agent.invoke({"input": user_message})
        return response["output"] if isinstance(response, dict) and "output" in response else str(response)
    except Exception as e:
        return f"Error: {str(e)}" 