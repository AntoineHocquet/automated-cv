import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

model = genai.GenerativeModel(model_name="models/gemini-1.5-flash-latest")

response = model.generate_content("Translate this German sentence: Ich liebe Daten.")
print(response.text)
