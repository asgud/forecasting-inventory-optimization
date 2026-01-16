import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ============================================
# OPENROUTER CLIENT SETUP
# ============================================
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY")
)

# Model
MODEL = "mistralai/devstral-2512:free"

# ============================================
# LOAD KNOWLEDGE BASE
# ============================================
def load_knowledge_base():
    """Load project context from knowledge_base.txt"""
    try:
        with open("knowledge_base.txt", "r") as f:
            return f.read()
    except FileNotFoundError:
        return "Knowledge base not found."

# ============================================
# SYSTEM PROMPT
# ============================================
def get_system_prompt():
    """Create system prompt with project knowledge"""
    
    knowledge = load_knowledge_base()
    
    system_prompt = f"""You are a helpful AI assistant specialized in Supply Chain Management. You assist users with a Supply Chain Forecasting & Inventory Optimization project.

YOUR CAPABILITIES:
1. Answer questions about the specific project (using the knowledge base below)
2. Explain general supply chain and data science concepts (using your own knowledge)
3. Help users understand forecasting, inventory management, and analytics

IMPORTANT INSTRUCTIONS:
- If the question is about THIS PROJECT (e.g., "What was your MAPE?", "Which products did you analyze?") → Use the PROJECT KNOWLEDGE BASE below
- If the question is a GENERAL CONCEPT (e.g., "What is forecasting?", "What is safety stock?", "What is ABC analysis?") → Use your general knowledge to explain, then relate to this project if relevant
- ALWAYS provide a helpful answer. Never say "no matches found" or "I cannot find this"
- Keep answers concise (2-4 paragraphs max)
- Use bullet points for lists
- NEVER use LaTeX formatting for formulas. Write formulas in plain text like: Safety Stock = Z × Std Dev × √(Lead Time)

PROJECT KNOWLEDGE BASE:
{knowledge}

Remember: You are a knowledgeable supply chain assistant. For general concepts, use your training knowledge. For project-specific details, use the knowledge base above."""
    
    return system_prompt

# ============================================
# CHAT FUNCTION
# ============================================
def chat(user_message, conversation_history=None):
    """
    Send message to LLM and get response
    
    Args:
        user_message: User's question
        conversation_history: List of previous messages (for memory)
    
    Returns:
        assistant_response: AI's response
        updated_history: Updated conversation history
    """
    
    if conversation_history is None:
        conversation_history = []
    
    messages = [
        {"role": "system", "content": get_system_prompt()}
    ]
    
    messages.extend(conversation_history)
    messages.append({"role": "user", "content": user_message})
    
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            max_tokens=1000,
            temperature=0.7
        )
        
        assistant_response = response.choices[0].message.content
        
        conversation_history.append({"role": "user", "content": user_message})
        conversation_history.append({"role": "assistant", "content": assistant_response})
        
        return assistant_response, conversation_history
    
    except Exception as e:
        error_message = f"Error: {str(e)}"
        return error_message, conversation_history