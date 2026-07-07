from pathlib import Path
from dotenv import load_dotenv
from groq import Groq

parts = []

for path in Path(".").rglob("*.py"):
    try:
        code = path.read_text(encoding="utf-8")
    except Exception:
        continue
        
    header = f"# FILE: {path}\n"
    parts.append(header + code)
big_string = "\n\n".join(parts)


question = "what is this project?"
prompt = f"""Here is a codebase. Answer using ONLY this code. Cite
  the file you used.

  CODE:
  {big_string}

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
    print(f"Total characters: {len(big_string):,}")
except Exception as e:
    print(f"Error: {e}")