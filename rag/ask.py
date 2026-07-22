from pathlib import Path
from dotenv import load_dotenv
from groq import Groq
from search import search

parts = []

question = "where does the chunks changed to vectors?"
result = search(question , k=5)
print("Retrieved chunks and scores:")
for score, chunk in result:
    print(f"{round(score, 3)} {chunk['file']}")
print("---")
context = ""
for score, chunk in result:
    context += f"File: {chunk['file']}(lines{chunk['start_line']}-{chunk['end_line']}):\n\n"
    context += chunk['text'] + "\n\n"

prompt = f"""Here is a codebase. Answer using ONLY this code. Cite
  the file you used.

  CODE:
  {context}

  QUESTION: {question}"""
load_dotenv()
client = Groq()
try:
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role":"user", "content": prompt}
        ],
    )
    print(response.choices[0].message.content)
    print(response.usage)
    print(f"Total characters: {len(context):,}")
except Exception as e:
    print(f"Error: {e}")
