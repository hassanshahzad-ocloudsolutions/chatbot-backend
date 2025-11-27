
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
from fastapi import UploadFile
import base64

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
    def generate_response(self, db: Session, chat_id: int, prompt: str, file: UploadFile):
        from app.services.chat_service import fetch_messages_by_chat_service, get_latest_message_service
        api_key = OPENAI_API_KEY
        model = OPENAI_MODEL
        temperature = float(OPENAI_TEMPERATURE)

        client = OpenAI(api_key=api_key)

        #client.audio.transcriptions.create

        # Build initial messages from chat history
        messages = [{"role": "system",
                    "content": [{"type": "input_text", "text":"You are a helpful assistant. Always consider the full conversation history "
                                                              "when replying. Make sure your responses are consistent with previous messages "
                                                              "and maintain the context of this chat."}]}]

        for m in fetch_messages_by_chat_service(db, chat_id):
            if m.content:
                # Determine type based on role because assistant messages or content is of output_text type.
                content_type = "input_text" if m.role == "user" else "output_text"
                messages.append({
                    "role": m.role,
                    "content": [{"type": content_type, "text": (m.content or "")+ (f"\n\n[Audio]: {m.audio_content}" if m.audio_content else "")}]
                })

        documents_extension = [
        ".art", ".bat", ".brf", ".c", ".cls", ".css",
        ".diff", ".eml", ".es", ".h", ".hs", ".htm", ".html", ".ics", ".ifb", ".java",
        ".js", ".json", ".ksh", ".ltx", ".mail", ".markdown", ".md", ".mht", ".mhtml",
        ".mjs", ".nws", ".patch", ".pdf", ".pl", ".pm", ".pot", ".py", ".scala", ".sh", ".shtml",
        ".srt", ".sty", ".tex", ".text", ".txt", ".vcf", ".vtt", ".xml", ".yaml", ".yml"
        ]

        audio_extensions = [".mp3", ".wav", ".m4a", ".webm", ".ogg"]

        image_extensions = [".png",".jpeg","jpg", "webp"]

        # Append user prompt
        user_message = {"type": "input_text", "text": prompt or ""}

        # If file is provided
        if file:
            tmp_dir = os.path.join(gettempdir(), "chatbot_files")
            os.makedirs(tmp_dir, exist_ok=True)
            unique_filename = f"{chat_id}_{uuid.uuid4().hex}_{file.filename}"
            tmp_path = os.path.join(tmp_dir, unique_filename)

            # Save file temporarily
            with open(tmp_path, "wb") as f:
                shutil.copyfileobj(file.file, f)

            try:
                if (file.filename.endswith(tuple(documents_extension))):
                # Upload to OpenAI
                    with open(tmp_path, "rb") as f:
                        upload = client.files.create(file=f, purpose="assistants")
                    # Add file message
                    file_message = {"type": "input_file", "file_id": upload.id}
                    messages.append({"role": "user", "content": f'file name {file.filename} {[user_message, file_message]}'})
                
                #if user attaches mp3 file ie this is not recored voice note one
                elif (file.filename.endswith(tuple(audio_extensions))):
                    with open(tmp_path, "rb") as audio_file:
                        transcription = client.audio.transcriptions.create(
                            model="whisper-1",
                            file=audio_file
                        )
                    latest_msg = get_latest_message_service(db, chat_id)

                    if latest_msg:
                        latest_msg.audio_content = transcription.text
                        db.commit()
                        db.refresh(latest_msg)
                    messages.append({"role": "user", "content": f'file name {file.filename} {[user_message, transcription.text]}'})

                elif(file.filename.endswith(tuple(image_extensions))):
                    with open(tmp_path, "rb") as image_file:
                        base64_image = base64.b64encode(image_file.read()).decode("utf-8")
                    
                    extension = file.filename.split('.')[-1]
                    image_message =  {"type": "input_image", "image_url": f"data:image/{extension};base64,{base64_image}"}
                    messages.append({"role": "user", "content": f'file name {file.filename} {[user_message, image_message]}'})

                else:
                    raise ValueError(f"Unsupported file format: {file.filename}")
            finally:
                # Cleanup temporary file
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)
        else:
            messages.append({"role": "user","content":[user_message]})

        # Generate response
        try:

            response = client.responses.create(
                model=model,
                input=messages,
                temperature=temperature
            )
            return response.output_text

        except Exception as e:
            raise e

    async def transcribe_audio(self, file):
        client = OpenAI(api_key=OPENAI_API_KEY)

    # Save temporary file
        tmp_dir = os.path.join(gettempdir(), "chatbot_files")
        os.makedirs(tmp_dir, exist_ok=True)
        unique_filename = f"{uuid.uuid4().hex}_{file.filename}"
        tmp_path = os.path.join(tmp_dir, unique_filename)

        with open(tmp_path, "wb") as f:
            f.write(await file.read())

        try:
            # Transcribe using Whisper
            with open(tmp_path, "rb") as audio_file:
                transcription = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file
                )
            transcription_text = transcription.text
        
        finally:
        # Clean up temp file
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
        return transcription_text
        

    
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
        # messages.append(HumanMessage(content=[
        #     {"type": "file", "file_url": {"url": "https://raw.githubusercontent.com/khuzaima-ocs/railway-incidents/refs/heads/main/rail_incidents.csv"}}
        # ]))

         # Process the uploaded file if provided
        if file:
            # Create unique temporary path
            tmp_dir = os.path.join(gettempdir(), "chatbot_files")
            os.makedirs(tmp_dir, exist_ok=True)
            unique_filename = f"{chat_id}_{uuid.uuid4().hex}_{file.filename}"
            tmp_path = os.path.join(tmp_dir, unique_filename)

            #storing file to the tmp folder
            with open(tmp_path, "wb") as f:
                shutil.copyfileobj(file.file, f)

            try:
                # Load file content
                loader = UnstructuredLoader(tmp_path)
                docs = loader.load()
                file_text = "\n".join([doc.page_content for doc in docs])

                # Add file content as part of the user's prompt
                if file_text:
                    messages.append(HumanMessage(content=f"File content:\n{file_text}"))
            finally:
                # Cleanup temporary file
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)
    
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