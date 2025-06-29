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
system_prompt = (
    "You are an assistant that always chooses the right tool for the user's request. "
    "If the user is making a decision, choosing between options, or comparing alternatives, always use the decision_matrix tool. "
    "If the user mentions weight and height, always calculate BMI using the bmi_calculator tool. "
    "If the user asks for motivation, inspiration, or a wise thought, always provide a quote using the motivational_quote tool. "
    "If the user asks for specific information about coaching, always use the knowledge_base_search (Retrieval) tool. "
    "If the user does not provide weights or scores for the decision matrix, handle them automatically. "
    "Never ask the user for weights or scores if they are missing; just proceed with the calculation. "
    "Always return the result as a table with numbers and a short explanation for decisions."
)

agent = initialize_agent(
    tools=all_tools,
    llm=llm,
    agent=AgentType.OPENAI_FUNCTIONS,
    memory=memory,
    verbose=True,
    system_prompt=system_prompt
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