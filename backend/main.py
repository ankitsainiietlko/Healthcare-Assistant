import requests
import os
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import google.generativeai as genai
import openai
import traceback
import re

# ✅ Load environment variables
from dotenv import load_dotenv
load_dotenv()

app = FastAPI()

# ✅ Add a root endpoint to prevent 404 Not Found errors
@app.get("/")
def home():
    return {"message": "FastAPI Backend is Running Successfully!"}

# ✅ Enable CORS for frontend connection (Fixed issue)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://healthcare-assistant-nine.vercel.app"],  # Your Vercel frontend URL
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# ✅ Fetch API keys
gemini_api_key = os.getenv("GEMINI_API_KEY")
openai.api_key = os.getenv("OPENAI_API_KEY")
google_places_api_key = os.getenv("GOOGLE_PLACES_API_KEY")
ipinfo_api_key = os.getenv("IPINFO_API_KEY")

if not gemini_api_key:
    raise RuntimeError("❌ No Gemini API key found! Please set GEMINI_API_KEY in .env")

genai.configure(api_key=gemini_api_key)

class ChatRequest(BaseModel):
    prompt: str
    latitude: float = None  # Optional user latitude
    longitude: float = None  # Optional user longitude

# ✅ Function to detect user location automatically (fallback method)
def detect_user_location():
    try:
        response = requests.get(f"https://ipinfo.io/json?token={ipinfo_api_key}")
        data = response.json()
        return data.get("city", "Unknown Location")
    except Exception as e:
        print("❌ Error detecting location:", e)
        return "Unknown Location"

# ✅ Function to find doctors using Google Places API
def find_doctor_nearby(specialty: str, location: str):
    """
    ✅ Fetches doctor details using Google Places API with improved accuracy.
    ✅ Includes full address, rating, and open status.
    """
    url = "https://maps.googleapis.com/maps/api/place/textsearch/json"

    params = {
        "query": f"{specialty} doctor in {location}",
        "key": google_places_api_key,
        "type": "doctor",
        "radius": 15000  # ✅ Searches within 15km radius
    }

    response = requests.get(url, params=params)
    data = response.json()

    if "error_message" in data:
        return f"❌ Google API Error: {data['error_message']}"

    if "results" in data and len(data["results"]) > 0:
        doctors = []
        for result in data["results"][:5]:  # ✅ Limit to 5 results
            doctor_info = {
                "name": result.get("name", "Unknown Doctor"),
                "address": result.get("formatted_address", "Address not available"),
                "rating": result.get("rating", "No rating available"),
                "open_now": result.get("opening_hours", {}).get("open_now", "Unknown")
            }
            doctors.append(doctor_info)

        return doctors  # ✅ Return doctor details

    return "❌ No doctors found. Try a different specialty or location."

@app.post("/chat/")
def chat_with_ai(request: ChatRequest):
    """
    ✅ FIXED: AI now introduces itself with a custom name.
    ✅ Ensures correct responses for both general and medical queries.
    ✅ Uses Google Places API for doctor search.
    """
    try:
        formatted_prompt = request.prompt.lower().strip()

        # ✅ Custom AI name
        AI_NAME = "MediBot"  # Change this to any name you prefer

        # ✅ Custom response for "What is your name?"
        if formatted_prompt in ["what is your name", "who are you"]:
            return {"response": f"My name is {AI_NAME}, your AI healthcare assistant. 😊 How can I help you today?"}

        # ✅ Handle general greetings
        greetings = ["hi", "hello", "hey", "how are you"]
        if any(greet in formatted_prompt for greet in greetings):
            return {"response": f"Hello! 😊 I'm {AI_NAME}. How can I assist you today?"}

        # ✅ Detect doctor search queries
        if re.search(r"(find|search|locate).*(doctor|neurologist|cardiologist|dermatologist|specialist)", formatted_prompt):
            specialty_match = re.search(r"find\s+(a|an)?\s*([\w\s]+)\s*(doctor|specialist)?", formatted_prompt)
            specialty = specialty_match.group(2).strip() if specialty_match else "doctor"

            # ✅ Extract location (fixing issue with "Delhi" not being detected)
            location_match = re.search(r"in\s+([a-zA-Z\s]+)$", formatted_prompt)
            if location_match:
                location = location_match.group(1).strip()
            elif "delhi" in formatted_prompt:
                location = "Delhi"
            elif not request.latitude or not request.longitude:
                location = detect_user_location()
            else:
                location = f"{request.latitude},{request.longitude}"

            # ✅ Fetch doctors from Google Places API
            doctors = find_doctor_nearby(specialty, location)

            if isinstance(doctors, list) and len(doctors) > 0:
                response_text = "\n\n".join([f"🔹 **{doc['name']}**\n📍 {doc['address']}\n⭐ Rating: {doc['rating']}" for doc in doctors])
            else:
                response_text = f"❌ No {specialty} found in {location}. Try another location."

        else:
            # ✅ Use AI for general questions
            model = genai.GenerativeModel("gemini-pro")
            response_text = model.generate_content(request.prompt).text

        return {"response": response_text}

    except Exception as e:
        print(f"❌ ERROR: {e}")
        return {"response": "❌ Error processing your request. Please try again later."}
