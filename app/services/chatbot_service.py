import requests
from dotenv import load_dotenv
import os
import json
from abc import ABC, abstractmethod

load_dotenv()

class Provider(ABC):
    @abstractmethod
    def generate_response(self,promp:str)->str:
        pass 

class Ollama(Provider):

   
    def generate_response(self,prompt: str):
        """
        Sends the user prompt to Ollama Llama 3.2 local server and returns the response.
        Make sure Ollama is running locally on default port 11434.
        """
        url = os.getenv("OLLAMA_API_URL") # type: ignore
        payload = {
            "model": os.getenv("OLLAMA_MODEL"),
            "prompt": prompt,
            "max_tokens": 5000,       # optional, adjust as needed
            "temperature": os.getenv("OLLAMA_TEMPERATURE")     # optional, creativity of response
        }

        try:
            response = requests.post(url, json=payload, stream=True)
            response.raise_for_status()

            #ollama generate response in splits so combine the response
            full_response = ""
            for line in response.iter_lines():
                if line:
                    try:
                        data = json.loads(line.decode("utf-8"))
                        # Accumulate partial responses
                        if "response" in data:
                            full_response += data["response"]
                    except json.JSONDecodeError:
                        # Skip malformed lines
                        continue

            return full_response.strip()

        except requests.RequestException as e:
            return f"Ollama API error: {str(e)}"

