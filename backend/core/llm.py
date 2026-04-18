import os
import json
from typing import Dict, Any
from groq import Groq
from dotenv import load_dotenv

# Load .env from project root
base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
env_path = os.path.join(base_dir, ".env")
load_dotenv(env_path)

class LLMService:
    def __init__(self, model: str = "llama-3.3-70b-versatile"):
        self.api_key = os.getenv("GROQ_API_KEY")
        self.model = model
        self.client = Groq(api_key=self.api_key) if self.api_key else None
        self.version = "v1"
        self._embedding_model = None

    @property
    def embedding_model(self):
        if self._embedding_model is None:
            from sentence_transformers import SentenceTransformer
            self._embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        return self._embedding_model

    def get_embedding(self, text: str):
        import numpy as np
        embedding = self.embedding_model.encode(text)
        norm = np.linalg.norm(embedding)
        if norm > 0:
            embedding = embedding / norm
        return embedding.tolist()

    def extract_structured(self, text: str, schema: Dict) -> Dict[str, Any]:
        if not self.client:
            return {
                **{key: [] if isinstance(val, list) else None for key, val in schema.items()},
                "llm_version": self.version
            }

        system_prompt = (
            "You are a strict sales intelligence information extraction engine. "
            "Extract business events like funding, acquisitions, partnerships, product launches, or hiring. "
            "Return ONLY valid JSON. No explanations."
        )
        
        user_prompt = (
            f"From the text below, extract: \n"
            f"1. A list of 'companies' involved.\n"
            f"2. A 'category' (EXCLUSIVELY choose from: funding, acquisition, partnership, product_launch, hiring, or general).\n"
            f"3. A 'relevance_score' (0-100) based on signal impact.\n\n"
            f"Text: {text}\n\n"
            f"Return JSON matching this schema:\n{json.dumps(schema)}"
        )
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0
            )

            raw_output = response.choices[0].message.content
            print("RAW LLM OUTPUT:", raw_output)

            # Safe parsing
            try:
                data = json.loads(raw_output.lower())
            except:
                print("JSON parsing failed, returning fallback")
                data = {}

            result = {
                **{key: data.get(key, [] if isinstance(val, list) else None)
                   for key, val in schema.items()},
                "llm_version": self.version
            }

            return result

        except Exception as e:
            print("GROQ ERROR:", str(e))
            return {
                **{key: [] if isinstance(val, list) else None for key, val in schema.items()},
                "llm_version": self.version
            }


llm_service = LLMService()
