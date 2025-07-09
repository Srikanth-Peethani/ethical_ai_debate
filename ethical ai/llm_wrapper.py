# llm_wrapper.py
import ollama
from functools import lru_cache
import json

class LLMWrapper:
    def __init__(self, model: str = 'phi3:instruct'):
        self.model = model
        self._warmup_model()

    def _warmup_model(self):
        """Pre-load model to reduce first-response latency"""
        try:
            ollama.generate(model=self.model, prompt='ping')
        except Exception as e:
            raise RuntimeError(f"Failed to load model {self.model}: {e}")

    @lru_cache(maxsize=100)
    def generate(self, prompt: str, max_tokens: int = 150) -> str:
        """Cached generation with optimized parameters"""
        try:
            response = ollama.chat(
                model=self.model,
                messages=[{'role': 'user', 'content': prompt}],
                options={
                    'temperature': 0.4,
                    'num_predict': max_tokens,
                    'num_ctx': 1024,
                    'repeat_penalty': 1.1
                }
            )
            return response['message']['content'].strip()
        except Exception as e:
            return f"API Error: {str(e)}"