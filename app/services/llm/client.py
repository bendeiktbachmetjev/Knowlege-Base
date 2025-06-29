import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain

# Print current working directory
print("Current working directory:", os.getcwd())

# Always load .env from the current working directory
DOTENV_PATH = os.path.join(os.getcwd(), '.env')
print("Loading .env from:", DOTENV_PATH)
load_dotenv(DOTENV_PATH)

# Print contents of .env
try:
    with open(DOTENV_PATH, 'r') as f:
        print(".env contents:\n", f.read())
except Exception as e:
    print("Could not read .env:", e)

# Print all OPENAI-related env vars
for k, v in os.environ.items():
    if "OPENAI" in k:
        print(f"{k}={v}")

# Use only OPENAI_API_KEY
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
print("OPENAI_API_KEY used:", OPENAI_API_KEY)

# Initialize ChatOpenAI model (GPT-4)
chat_model = ChatOpenAI(
    model_name="gpt-4",
    temperature=0.7,
    openai_api_key=OPENAI_API_KEY
)

# Initialize Conversation Memory
memory = ConversationBufferMemory(return_messages=True)

# Initialize ConversationChain with memory
conversation_chain = ConversationChain(
    llm=chat_model,
    memory=memory,
    verbose=True
)

def generate_response(prompt: str) -> str:
    """
    Generate a response from GPT-4 using LangChain ChatOpenAI.
    Args:
        prompt (str): The user prompt to send to the model.
    Returns:
        str: The model's response as a string.
    """
    try:
        messages = [HumanMessage(content=prompt)]
        response = chat_model(messages)
        return response.content
    except Exception as e:
        # Return error message for debugging
        return f"Error: {str(e)}"

def generate_response_with_memory(prompt: str) -> str:
    """
    Generate a response from GPT-4 using LangChain ConversationChain with memory.
    Args:
        prompt (str): The user prompt to send to the model.
    Returns:
        str: The model's response as a string, with conversational memory.
    """
    try:
        response = conversation_chain.predict(input=prompt)
        return response
    except Exception as e:
        # Return error message for debugging
        return f"Error: {str(e)}" 