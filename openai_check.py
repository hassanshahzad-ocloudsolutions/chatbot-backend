from openai import OpenAI
from app.config import OPENAI_API_KEY
client = OpenAI(api_key=OPENAI_API_KEY)

# Upload your .py file
upload = client.files.create(
    file=open("math.pdf", "rb"),
    purpose="assistants"
)

# Send messages to the model
response = client.responses.create(
    model="gpt-4o-mini",
    input=[
        {
            "role": "system",
            "content": [
                {
                    "type": "input_text",
                    "text": (
                        "You are a helpful assistant. "
                        "Always consider the full conversation history when replying. "
                        "Make sure your responses are consistent with previous messages "
                        "and maintain the context of this chat."
                    )
                }
            ]
        },
        {
            "role": "user",
            "content": [
                {"type": "input_text", "text": "Please read this file"},
                {"type": "input_file", "file_id": upload.id}
            ]
        }
    ]
)

print(response.output_text)
