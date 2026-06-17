import openai
import os
from dotenv import load_dotenv

load_dotenv()

client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_briefing(month: str, rising: list, falling: list) -> str:
    rising_text = "\n".join([
        f"- {r[0]}, {r[1]}: average price £{r[2]:,.0f}, up {r[3]}% month-on-month ({r[4]} transactions)"
        for r in rising
    ])
    falling_text = "\n".join([
        f"- {f[0]}, {f[1]}: average price £{f[2]:,.0f}, down {f[3]}% month-on-month ({f[4]} transactions)"
        for f in falling
    ])

    prompt = f"""You are a UK property market analyst writing a monthly briefing.

Month: {month}

Top 3 rising areas:
{rising_text}

Top 3 falling areas:
{falling_text}

Write a concise, professional market briefing (3-4 short paragraphs) covering:
1. What's happening in the rising areas and possible drivers
2. What's happening in the falling areas and possible drivers
3. Any caveat worth noting if a sample size looks small

Keep it factual and avoid speculation beyond what the data supports."""

    response = client.chat.completions.create(
        model="gpt-4o",
        max_tokens=600,
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content