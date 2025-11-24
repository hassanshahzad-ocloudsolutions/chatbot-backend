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
from PyPDF2 import PdfFileReader

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
                messages.append(HumanMessage(content=m.content))
            elif role == "assistant":
                messages.append(AIMessage(content=m.content))
        
        # Add the current user prompt
        messages.append(HumanMessage(content=prompt))

         # Process the uploaded file if provided
        file_text = ""
        if file:
            filename = file.filename.lower()
            if filename.endswith(".txt"):
                file_text = file.file.read().decode("utf-8")
            elif filename.endswith(".pdf"):
                reader = PdfReader(file.file)
                file_text = "\n".join([page.extract_text() or "" for page in reader.pages])

            elif filename.endswith(".xlsx"):
                from openpyxl import load_workbook
                wb = load_workbook(file.file, data_only=True)  # data_only=True to get values, not formulas
                file_text_list = []
                for sheet in wb.worksheets:
                    for row in sheet.iter_rows(values_only=True):
                    # join cells in the row with tabs or commas
                        row_text = "\t".join([str(cell) if cell is not None else "" for cell in row])
                        file_text_list.append(row_text)
                file_text = "\n".join(file_text_list)
            
            messages.append(HumanMessage(content=f"[File: {file.filename}]\n{file_text}"))

        try:
            # Generate response
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