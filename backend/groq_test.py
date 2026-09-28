import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY is missing from .env")


client = Groq(api_key=GROQ_API_KEY)


response = client.chat.completions.create(
    model="openai/gpt-oss-20b",
    messages=[
        {
            "role": "system",
            "content": "You are an expert Site Reliability Engineer."
        },
        {
            "role": "user",
            "content": """
            A Payment API has 4.5 second latency,
            35% HTTP 500 errors, and 100% database
            connection utilization.

            What should an SRE investigate first?
            """
        }
    ],
)


print("========== GROQ TEST ==========\n")
print(response.choices[0].message.content)