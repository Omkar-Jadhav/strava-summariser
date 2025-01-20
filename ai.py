from groq import Groq
import os

client = Groq(api_key=os.environ.get("GROQ_API_KEY"),)
completion = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[
        {
            "role": "system",
            "content": "You are a helpful running coach who always encourages the athlete and give insights on data."
        },
        {
            "role": "user",
            "content": "This is the average running data of the athlete over past 4 weeks.\nFour-Week Rolling Run Summary\nTotal runs: : 26\nTotal distance: : 289.85 Km\nAverage distance: : 11.15 Km/run\nAverage pace: : 05:50 min/Km\nTotal elevation gain:: 1271.30 m\nTotal moving time: : 28:15:34\nTotal elapsed time: : 28:44:13\nThe stats for this activity was -\ntotal distance - 42.6Km\navg pace - 5:20 min/km\ntotal time - 3hr 48min\n\nProvide insights and data points from it, do not mention the obvious statistics. Encourage the athlete. Suggest a general focus for upcoming week.\n"
        },
    ],
    temperature=1,
    max_completion_tokens=3130,
    top_p=1,
    stream=True,
    stop=None,
)

for chunk in completion:
    print(chunk.choices[0].delta.content or "", end="")
