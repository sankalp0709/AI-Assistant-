import os
from typing import Optional
import openai
import groq
import google.generativeai as genai
try:
    from mistralai import MistralClient
except ImportError:
    MistralClient = None

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
import hashlib

class LLMBridge:
    def __init__(self):
        # Initialize clients only if API keys are available
        openai_key = os.getenv("OPENAI_API_KEY")
        self.openai_client = openai.OpenAI(api_key=openai_key) if openai_key else None

        groq_key = os.getenv("GROQ_API_KEY")
        self.groq_client = groq.Groq(api_key=groq_key) if groq_key else None

        google_key = os.getenv("GOOGLE_API_KEY")
        if google_key:
            genai.configure(api_key=google_key)
            self.google_available = True
        else:
            self.google_available = False

        mistral_key = os.getenv("MISTRAL_API_KEY")
        self.mistral_client = MistralClient(api_key=mistral_key) if MistralClient and mistral_key else None

        # Initialize local model for UniGuru
        self.cache = {}
        try:
            self.tokenizer = AutoTokenizer.from_pretrained('microsoft/DialoGPT-small')
            self.model = AutoModelForCausalLM.from_pretrained('microsoft/DialoGPT-small')
            self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
            self.model.to(self.device)
            self.local_available = True
        except Exception as e:
            print(f"Failed to load local UniGuru model: {e}")
            self.local_available = False

    async def call_llm(self, model: str, prompt: str) -> str:
        # Validate prompt
        if not isinstance(prompt, str) or not prompt.strip():
            raise ValueError("Invalid prompt: must be a non-empty string")

        prompt = prompt.strip()

        if model == "chatgpt":
            if self.openai_client:
                try:
                    response = self.openai_client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[{"role": "user", "content": prompt}]
                    )
                    return response.choices[0].message.content
                except Exception as e:
                    return f"ChatGPT error: {e}"
            else:
                return f"ChatGPT not available: {prompt}"
        elif model == "groq":
            if self.groq_client:
                try:
                    response = self.groq_client.chat.completions.create(
                        model="llama2-70b-4096",
                        messages=[{"role": "user", "content": prompt}]
                    )
                    return response.choices[0].message.content
                except Exception as e:
                    return f"Groq error: {e}"
            else:
                return f"Groq not available: {prompt}"
        elif model == "gemini":
            if self.google_available:
                try:
                    model = genai.GenerativeModel('gemini-pro')
                    response = model.generate_content(prompt)
                    return response.text
                except Exception as e:
                    return f"Gemini error: {e}"
            else:
                return f"Gemini not available: {prompt}"
        elif model == "mistral":
            if self.mistral_client:
                try:
                    response = self.mistral_client.chat(
                        model="mistral-medium",
                        messages=[{"role": "user", "content": prompt}]
                    )
                    return response.choices[0].message.content
                except Exception as e:
                    return f"Mistral error: {e}"
            else:
                return f"Mistral not available: {prompt}"
        elif model == "uniguru":
            if not self.local_available:
                return f"UniGuru not available: {prompt}"

            # Check cache
            prompt_hash = hashlib.sha256(prompt.encode()).hexdigest()
            if prompt_hash in self.cache:
                return self.cache[prompt_hash]

            try:
                # Validate prompt
                if not prompt or not isinstance(prompt, str):
                    raise ValueError("Invalid prompt: must be a non-empty string")

                # Tokenize and generate
                inputs = self.tokenizer.encode(prompt + self.tokenizer.eos_token, return_tensors='pt').to(self.device)
                with torch.no_grad():
                    outputs = self.model.generate(
                        inputs,
                        max_length=inputs.shape[1] + 50,  # Generate up to 50 new tokens
                        pad_token_id=self.tokenizer.eos_token_id,
                        do_sample=True,
                        top_p=0.9,
                        temperature=0.7
                    )
                response = self.tokenizer.decode(outputs[0][inputs.shape[1]:], skip_special_tokens=True).strip()

                # Cache the response
                self.cache[prompt_hash] = response
                return response

            except ValueError as e:
                return f"UniGuru prompt error: {e}"
            except torch.cuda.OutOfMemoryError:
                return "UniGuru GPU memory error: try with CPU or smaller model"
            except Exception as e:
                return f"UniGuru inference error: {e}"
        else:
            raise ValueError(f"Unsupported model: {model}")

llm_bridge = LLMBridge()