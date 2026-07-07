from dotenv import load_dotenv
from load_repo import load_repo
from groq import Groq

load_dotenv()

client = Groq()

try:
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role":"system", "content": "you tell them about ethiopain orthodox church very detailed"},{"role":"user", "content": "hey how is your day."}

        ],)
    print(response.choices[0].message.content)
    print(response.usage)
    
except Exception as e:
    print(f"Error: {e}")