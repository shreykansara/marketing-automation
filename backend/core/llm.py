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
            "You are a deterministic information extraction engine for Blostem. "
            "Blostem focuses ONLY on Banks, NBFCs, Fintechs, Neobanks, and Wealthtech platforms in India. "
            "Your job is to extract ONLY high-signal intelligence from noisy news text.\n\n"
            "STRICT RULES:\n"
            "1. Extract ONLY companies central to the event (ignore media, PR, irrelevant mentions).\n"
            "2. Normalize company names (e.g., 'HDFC Bank Ltd.' → 'HDFC Bank').\n"
            "3. Category MUST be one of: funding, partnership, product_launch, expansion, regulatory, hiring, general.\n"
            "4. Relevance scoring:\n"
            "   - 80–100: Indian fintech/banking infra activity\n"
            "   - 40–79: indirect/global fintech relevance\n"
            "   - 0–39: non-finance companies\n"
            "   - If no relevant financial entity → score MUST be 0\n"
            "5. Never hallucinate. If unsure, return empty values.\n"
            "6. Output STRICT JSON only. No explanation."
        )
        
        user_prompt = (
            f"Extract structured intelligence from the following news.\n\n"
            f"TEXT:\n\"\"\"\n{text}\n\"\"\"\n\n"
            f"OUTPUT SCHEMA:\n{json.dumps(schema)}\n\n"
            f"Return ONLY valid JSON."
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
            try:
                data = json.loads(raw_output.lower())
            except:
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

    def analyze_deal_status(self, email_body: str, current_status: str) -> Dict[str, Any]:
        if not self.client:
            return {"suggested_status": current_status, "reason": "LLM offline"}

        system_prompt = (
            "You are a B2B sales pipeline intelligence engine for Blostem.\n\n"
            "Allowed statuses:\n"
            "- open\n- contacted\n- replied\n- closed\n- archived\n\n"
            "DECISION RULES:\n"
            "- Engagement (questions, interest, scheduling) → replied\n"
            "- Neutral acknowledgment → replied\n"
            "- Not interested → archived\n"
            "- Purchase/demo confirmation → closed\n"
            "- No response → keep as contacted\n\n"
            "Do NOT assume optimism. Base ONLY on explicit intent.\n\n"
            "Return JSON with 'suggested_status' and 'reason'."
        )
        
        user_prompt = (
            f"Current Deal Status: {current_status}\n"
            f"Incoming Email Body: {email_body}\n\n"
            f"Determine the correct status update."
        )

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            print(f"[ERROR] LLM analysis failed: {e}")
            return {"suggested_status": current_status, "reason": str(e)}

    def score_deal_logs(self, logs: list) -> int:
        if not self.client or not logs:
            return 0
            
        recent_logs = logs[-3:]
        logs_text = "\n".join([f"- [{l.get('timestamp')}] {l.get('type')}: {l.get('message')}" for l in recent_logs])
        
        system_prompt = (
            "You are a deal prioritization engine for Blostem.\n\n"
            "Score based on BUYING INTENT:\n"
            "80–100: strong intent (demo, follow-ups, product questions)\n"
            "50–79: moderate engagement\n"
            "20–49: weak signals\n"
            "0–19: no activity or negative\n\n"
            "Recency > volume. Penalize inactivity.\n\n"
            "Return ONLY JSON: {\"score\": number}"
        )
        
        user_prompt = f"Activity Logs:\n{logs_text}\n\nScore this deal."

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0
            )
            data = json.loads(response.choices[0].message.content)
            return int(data.get("score", 0))
        except Exception as e:
            print(f"[ERROR] LLM log scoring failed: {e}")
            return 0

    def generate_outreach_email(self, logs: list, current_status: str, company_name: str) -> Dict[str, str]:
        if not self.client:
            return {"subject": "AI Draft", "body": "LLM offline. Please check GROQ_API_KEY."}

        recent_logs = logs[-3:]
        logs_text = "\n".join([f"- {l.get('message')}" for l in recent_logs])

        system_prompt = (
            "You are a top-tier fintech B2B sales copywriter for Blostem.\n\n"
            "Blostem provides FD distribution infra and Banking APIs.\n\n"
            "WRITING RULES:\n"
            "1. Personalize using context\n"
            "2. No fluff or generic openings\n"
            "3. Strong hook + clear value + soft CTA\n"
            "4. Tone: confident, concise, intelligent\n"
            "5. Length: 80–150 words\n\n"
            "Return JSON with 'subject' and 'body'."
        )

        user_prompt = (
            f"Company: {company_name}\n"
            f"Stage: {current_status}\n"
            f"Context Logs:\n{logs_text}\n\n"
            f"Write a high-conversion outreach email."
        )

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.7
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            print(f"[ERROR] LLM email generation failed: {e}")
            return {"subject": "Follow up: Blostem", "body": f"Error generating email: {str(e)}"}

    def generate_email_log_suggestion(self, subject: str, body: str) -> str:
        if not self.client:
            return "Email interaction captured."

        system_prompt = (
            "You are a CRM logging assistant.\n\n"
            "Summarize into ONE precise sentence capturing action or outcome.\n\n"
            "Rules:\n"
            "- Max 20 words\n"
            "- No fluff\n"
            "- Plain text only"
        )

        user_prompt = f"Subject: {subject}\nBody: {body}\n\nSummarize."

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"[ERROR] LLM log generation failed: {e}")
            return f"Processed email: {subject}"

llm_service = LLMService()