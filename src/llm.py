from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def summarize_abstract(abstract_text: str) -> str:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that summarizes scientific abstracts."},
            {"role": "user", "content": f"Summarize this abstract in one sentence: {abstract_text}"}
        ]
    )
    return response.choices[0].message.content

def analyze_abstract(abstract_text: str) -> str:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that analyzes scientific abstracts."},
            {"role": "user", "content": f"Analyze this abstract and provide key findings, methodology, and potential implications: {abstract_text}"}
        ]
    )
    return response.choices[0].message.content