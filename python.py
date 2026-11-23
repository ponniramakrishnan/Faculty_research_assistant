
import ollama

print("Faculty Research Assistant Started!")

response = ollama.chat(
    model="llama3.2",
    messages=[
        {
            "role": "system",
            "content": """
            You are an academic research assistant.

            Analyze the research information provided.
            Use clear academic language.
            Never invent research findings or references.
            Mention when information is insufficient.
            """
        },
        {
            "role": "user",
            "content": """
            Explain the research topic:

            Machine Learning-based URL Phishing Detection.

            Discuss:
            1. Research background
            2. Common machine learning algorithms
            3. Possible research challenges
            4. Future research directions
            """
        }
    ]
)

print("\nRESEARCH ASSISTANT RESPONSE\n")
print(response.message.content)
