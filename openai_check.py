from openai import OpenAI
from app.config import OPENAI_API_KEY
client = OpenAI(api_key=OPENAI_API_KEY)

# Upload your .py file
upload = client.files.create(
    file=open("requirements.txt", "rb"),
    purpose="assistants"
)

print(f"File uploaded successfully. File ID: {upload.id}")

# Send messages to the model
response = client.responses.create(
    model="gpt-4o-mini",
    input=[
        {
            "role": "system",
            "content": [
                {
                    "type": "input_text",
                    "text": "You are a helpful assistant."
                }
            ]
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "input_file",
                    "file_id": upload.id
                },
                {
                    "type": "input_text",
                    "text": "Please read and summarize this file."
                }
            ]
        }
    ]
)

print(response.output_text)
