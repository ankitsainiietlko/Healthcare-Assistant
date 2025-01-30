from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import google.generativeai as genai
import openai
import os
from dotenv import load_dotenv
import traceback
import re

# ✅ Load environment variables
load_dotenv()

app = FastAPI()

# ✅ Enable CORS for frontend connection
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # ✅ Allow frontend requests
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Fetch API keys
gemini_api_key = os.getenv("GEMINI_API_KEY")
openai.api_key = os.getenv("OPENAI_API_KEY")  # ✅ GPT-4 API Key

if not gemini_api_key:
    raise RuntimeError("❌ No Gemini API key found! Please set GEMINI_API_KEY in .env")

genai.configure(api_key=gemini_api_key)

class ChatRequest(BaseModel):
    prompt: str

# ✅ Memory to store past chat messages
conversation_memory = []

def format_input(prompt_text):
    """ ✅ Automatically format input for better AI responses. """
    prompt_text = str(prompt_text).strip()

    if not prompt_text:
        return "Hello! How can I assist you today?"

    # ✅ Detect numbers and add context
    if prompt_text.isdigit():
        return f"What can you tell me about the number {prompt_text}?"

    # ✅ Detect dates and add context
    date_pattern = r"^\d{1,2}[/.-]\d{1,2}[/.-]\d{4}$"
    if re.match(date_pattern, prompt_text):
        return f"What is special about the date {prompt_text}?"

    # ✅ Detect names (two capitalized words) and add context
    words = prompt_text.split()
    if len(words) == 2 and all(w[0].isupper() for w in words):
        return f"Who is {prompt_text}? Can you provide more details?"

    return prompt_text  # ✅ Return original if no special formatting needed

def generate_gpt4_response(user_input):
    """
    ✅ Uses OpenAI GPT-4 for advanced reasoning.
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": user_input}]
        )
        return response["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"❌ GPT-4 Error: {traceback.format_exc()}")
        return "I'm sorry, but I couldn't process your request."

@app.post("/chat/")
def chat_with_ai(request: ChatRequest):
    """
    ✅ Handles all types of inputs and improves AI responses with memory.
    """
    try:
        formatted_prompt = format_input(request.prompt)  # ✅ Smart AI prompting
        conversation_memory.append(f"User: {request.prompt}")

        # ✅ Keep only the last 5 messages to avoid excessive memory use
        if len(conversation_memory) > 5:
            conversation_memory.pop(0)

        conversation_history = "\n".join(conversation_memory)

        final_prompt = f"""
        You are a highly intelligent healthcare assistant. You provide 
        detailed, accurate answers related to health. You also answer general 
        questions to the best of your ability. Here is the conversation so far:

        {conversation_history}

        Now answer this question:
        {formatted_prompt}
        """

        # ✅ Use GPT-4 for advanced topics, Gemini for general chat
        if "explain" in request.prompt.lower() or "how does" in request.prompt.lower():
            response_text = generate_gpt4_response(final_prompt)
        else:
            model = genai.GenerativeModel("gemini-pro")
            response_text = model.generate_content(final_prompt).text

        conversation_memory.append(f"AI: {response_text}")  # ✅ Store AI response

        return {"response": response_text}

    except Exception as e:
        print(f"❌ AI Error: {traceback.format_exc()}")
        return {"response": "I'm sorry, but I couldn't process your request. Please try again."}