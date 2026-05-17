import os
import re
from abc import ABC, abstractmethod
from google import genai
from google.genai import types

class LLMAdapter(ABC):
    @abstractmethod
    def generate_code(self, prompt: str) -> str:
        pass

class GeminiAdapter(LLMAdapter):
    def __init__(self, model_name: str = "gemini-2.5-flash"):
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is not set.")
        
        self.client = genai.Client(api_key=api_key)
        self.model_name = model_name

    def generate_code(self, prompt: str) -> str:
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt,
        )
        return self._extract_python_code(response.text)

    def _extract_python_code(self, response_text: str) -> str:
        # Extract code from markdown blocks if present
        match = re.search(r"```python\n(.*?)\n```", response_text, re.DOTALL)
        if match:
            return match.group(1).strip()
        # Fallback if no markdown blocks are found
        return response_text.strip()
