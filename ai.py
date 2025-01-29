from groq import Groq
import os
from openai import OpenAI

client = Groq(api_key=os.environ.get("GROQ_API_KEY"),)

def get_insights_by_llm(avg_stats, past_runs):
    inp_message = f"""Act as a helpful running coach. 
Present insights and key data points from the athlete's past 4 weeks of running activity in under 100 words. Sugggest a general focus for upcoming week, and suggested acticvities for next 2 days. 
Avoid mentioning obvious statistics from summary. Do not use first person voice.
Encourage, motivate, and applaud the athlete. 
The workout history includes various runs like long runs, tempo runs, easy runs, recovery runs, intervals, and trail run, with additional details for some activities such as lap times, average pace, and total elevation gain. Based on the recent workouts/intervals/long runs or races in last 5 workouts suggest upcoming weeks focus. Workouts are numbered by a descending order of date. Take a comprehensive approah in suggesting the workouts considering the athlete's past runs where depending on recent workouts you should suggest easy runs/ tempo runs/ intervals/ long runs/ hill workouts or a recovery run.  
If past runs are not available, then only suggest a general focus for the upcoming week and activities for the next 2 days. Use at most 3/4 emojis to make the message more engaging only if necessary.
Here is the athlete's workout history.
4 week rolling summary: {avg_stats}
Previous 4 weeks running history: {past_runs}"""
    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": "You are a helpful running coach who always encourages the athlete and give insights on data."
            },
            {
                "role": "user",
                "content": inp_message
            },
        ],
        temperature=1,
        max_completion_tokens=3130,
        top_p=1,
        stream=True,
        stop=None,
    )

    output = ""
    for chunk in completion:
        output += chunk.choices[0].delta.content or ""
        
    return output


def analyse_past_3m_runs(activities, athlete_baseline):
    inp_message = f"""Act as a helpful and professiona running coach and data analyst.
    You are presented with the workout history of an athlete for the past 3 months. 
    The athlete's past 3 months activities include various runs like long runs, tempo runs, easy runs, recovery runs, intervals, and trail run, with additional details for some activities such as lap times, average pace, and total elevation gain.
    Analyse the athlete's past 3 months of running activity and provide a summarised version of athlete's past 3 months running history. The summary should be detailed such that based on this data further workout plans can be generated. DO NOT PROVIDE ANY SUGGSTIONS yet.
    Past 3 months running history is as follows: {activities}
    """
    
    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": "You are a helpful running coach who always encourages the athlete and give insights on data."
            },
            {
                "role": "user",
                "content": inp_message
            },
        ],
        temperature=1,
        max_completion_tokens=3130,
        top_p=1,
        stream=True,
        stop=None,
    )

    output = ""
    for chunk in completion:
        output += chunk.choices[0].delta.content or ""
        
    return output
    
    
def get_response_from_groq(inp_message):
    completion = client.chat.completions.create(
        # model="llama-3.3-70b-versatile",
        # model = "llama3-70b-8192",
        model ="deepseek-r1-distill-llama-70b",
        # model="llama3-8b-8192",
        messages=[
            {
                "role": "system",
                "content": "You are a helpful and professional running coach."
            },
            {
                "role": "user",
                "content": inp_message
            },
        ],
        temperature=1,
        max_completion_tokens=3130,
        top_p=1,
        stream=True,
        stop=None,
    )

    output = ""
    for chunk in completion:
        output += chunk.choices[0].delta.content or ""

    output = extract_after_think(output)
    return output

def extract_after_think(text):
    tag = "</think>"
    index = text.find(tag)
    if index != -1:
        return text[index + len(tag):].strip()
    return text  # Return None if </think> is not found

def get_response_from_deepseek(inp_message):
    client = OpenAI(api_key=os.environ.get("DEEPSEEK_API_KEY"), base_url="https://api.deepseek.com")

    messages = [{"role": "user", "content": f"{inp_message}"}]
    response = client.chat.completions.create(
        model="deepseek-reasoner",
        messages=messages
    )

    return response.choices[0].message.content, response.choices[0].message.reasoning_content
