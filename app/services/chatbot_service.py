
from langchain_unstructured import UnstructuredLoader
import requests
from dotenv import load_dotenv
import os
import json
from openai import OpenAI
from abc import ABC, abstractmethod
from app.config import (OLLAMA_API_URL, OLLAMA_MODEL,OLLAMA_TEMPERATURE,OPENAI_API_KEY, OPENAI_MODEL, OPENAI_TEMPERATURE)
from sqlalchemy.orm import Session
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
import os
import uuid
import shutil
from tempfile import gettempdir



load_dotenv()

class Provider(ABC):
    @abstractmethod
    def generate_response(self,db:Session,chat_id:int,prompt:str)->str:
        pass 
    
    @abstractmethod
    def generate_title(self,prompt:str)->str:
        pass 

class Ollama(Provider):

    def generate_response(self,db:Session,chat_id:int,prompt: str):
        """
        Sends the user prompt to Ollama Llama 3.2 local server and returns the response.
        Make sure Ollama is running locally on default port 11434.
        """
        url = OLLAMA_API_URL # type: ignore
        payload = {
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "max_tokens": 5000,       # optional, adjust as needed
            "temperature": OLLAMA_TEMPERATURE    # optional, creativity of response
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
        
    def generate_title(self,prompt: str):
        """
        Sends the user prompt to Ollama Llama 3.2 local server and returns the response.
        Make sure Ollama is running locally on default port 11434.
        """
        url = OLLAMA_API_URL # type: ignore
        payload = {
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "max_tokens": 5000,       # optional, adjust as needed
            "temperature": OLLAMA_TEMPERATURE    # optional, creativity of response
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

class OpenAi(Provider):
    def generate_response(self,db:Session,chat_id:int, prompt: str):
        from app.services.chat_service import fetch_messages_by_chat_service
        api_key = OPENAI_API_KEY
        model = OPENAI_MODEL
        temperature = float(OPENAI_TEMPERATURE)
        client = OpenAI(api_key=api_key)
        messages_list_for_context = [{"role": "system",
                                     "content": ("You are a helpful assistant. Always consider the full conversation history "
                                                "when replying. Make sure your responses are consistent with previous messages "
                                                "and maintain the context of this chat.")}] + \
        [{"role": m.role, "content": m.content} for m in fetch_messages_by_chat_service(db, chat_id)]

        try:
            response = client.chat.completions.create(
                model=model,
                messages=messages_list_for_context,
                max_tokens=500,
                temperature=temperature,
            )


            return response.choices[0].message.content.strip()

        except Exception as e:
            return f"OpenAI API error: {str(e)}"
        
    def generate_title(self,prompt: str): 
        api_key = OPENAI_API_KEY
        model = OPENAI_MODEL 
        temperature = float(OPENAI_TEMPERATURE) 
        client = OpenAI(api_key=api_key) 
        try: 
            response = client.chat.completions.create(
                model=model, 
                messages=[ {"role": "system", "content": "You are a helpful assistant."},
                                        {"role": "user", "content": prompt}, ],
                max_tokens=500,
                temperature=temperature,) 
            return response.choices[0].message.content.strip()
        except Exception as e: 
            return f"OpenAI API error: {str(e)}"


class LangChain(Provider):
     def generate_response(self, db: Session, chat_id: int, prompt: str, file):
        from app.services.chat_service import fetch_messages_by_chat_service
        # Initialize the LangChain Chat Model
        chat = ChatOpenAI(
            openai_api_key=OPENAI_API_KEY,
            model_name=OPENAI_MODEL,
            temperature=float(OPENAI_TEMPERATURE),
            max_tokens=500
        )

        # Fetch previous messages for context
        messages_from_db = fetch_messages_by_chat_service(db, chat_id)

        # Build the message list for LangChain
        messages = [
            SystemMessage(content=(
                "You are a helpful assistant. Always consider the full conversation history "
                "when replying. Make sure your responses are consistent with previous messages "
                "and maintain the context of this chat."
            ))
        ]

        for m in messages_from_db:
            role = m.role.lower()
            if role == "user":
                messages.append(HumanMessage(content=m.content or ""))
            elif role == "assistant":
                messages.append(AIMessage(content=m.content or ""))
        
        #Add the current user prompt
        messages.append(HumanMessage(content=[
            {"type": "file", "file_url": {"url": "https://example.com/image.jpg"}}
        ]))

         # Process the uploaded file if provided
        # if file:
        #     # Create unique temporary path
        #     tmp_dir = os.path.join(gettempdir(), "chatbot_files")
        #     os.makedirs(tmp_dir, exist_ok=True)
        #     unique_filename = f"{chat_id}_{uuid.uuid4().hex}_{file.filename}"
        #     tmp_path = os.path.join(tmp_dir, unique_filename)

        #     #storing file to the tmp folder
        #     with open(tmp_path, "wb") as f:
        #         shutil.copyfileobj(file.file, f)

        #     try:
        #         # Load file content
        #         loader = UnstructuredLoader(tmp_path)
        #         docs = loader.load()
        #         file_text = "\n".join([doc.page_content for doc in docs])

        #         # Add file content as part of the user's prompt
        #         if file_text:
        #             messages.append(HumanMessage(content=f"File content:\n{file_text}"))
        #     finally:
        #         # Cleanup temporary file
        #         if os.path.exists(tmp_path):
        #             os.remove(tmp_path)
    
        try:
            response = chat.invoke(messages)
            return response.content.strip()

        except Exception as e:
            return f"LangChain API error: {str(e)}"

     def generate_title(self, prompt: str):
        try:
            llm = ChatOpenAI(
                api_key=OPENAI_API_KEY,
                model=OPENAI_MODEL,
                temperature=float(OPENAI_TEMPERATURE),
                max_tokens=500,
            )

            response = llm.invoke([
                SystemMessage(content="You are a helpful assistant."),
                HumanMessage(content=prompt)
            ])

            return response.content.strip()

        except Exception as e:
            return f"LangChain error: {str(e)}"