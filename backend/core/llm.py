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
            "You are a strict sales intelligence engine for Blostem. "
            "Blostem is a B2B infrastructure platform for Fixed Deposit (FD) distribution in India. "
            "Our target customers are Banks, NBFCs, Neobanks, Wealthtechs, and Fintechs that want to offer investment products. "
            "Extract events like funding, partnerships, or product launches that indicate a business is growing or seeking new distribution channels. "
            "Return ONLY valid JSON. No explanations."
        )
        
        user_prompt = (
            f"From the text below, extract: \n"
            f"1. A list of 'companies' involved. CRITICAL: If multiple companies are mentioned (e.g., a Fintech and its Bank partner), list ONLY the company that would be a potential customer for Blostem (the one needing FD distribution infrastructure).\n"
            f"2. A 'category' (EXCLUSIVELY choose from: funding, partnership, product_launch, expansion, regulatory, hiring, or general).\n"
            f"3. A 'relevance_score' (0-100). This is the 'Intent Score'. Calculate it based on how relevant this news is for Blostem's B2B FD sales team. Higher scores for Indian fintechs/banks launching new products or raising funds.\n\n"
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
            # Safe parsing
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
        """
        Analyze an incoming email to suggest a pipeline status update.
        """
        if not self.client:
            return {"suggested_status": current_status, "reason": "LLM offline"}

        system_prompt = (
            "You are a sales intelligence expert. "
            "Analyze the sentiment and intent of an incoming email reply to suggest a pipeline status change. "
            "Exclusively use these statuses: open, contacted, replied, closed, archived. "
            "Return JSON with 'suggested_status' and 'reason'."
        )
        
        user_prompt = (
            f"Current Deal Status: {current_status}\n"
            f"Incoming Email Body: {email_body}\n\n"
            f"Which status should this deal move to? provide a brief reason."
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
        """
        Analyze the 3 most recent logs to determine an intent/relevance score (0-100).
        """
        if not self.client or not logs:
            return 0
            
        recent_logs = logs[-3:]
        logs_text = "\n".join([f"- [{l.get('timestamp')}] {l.get('type')}: {l.get('message')}" for l in recent_logs])
        
        system_prompt = (
            "You are a sales prioritization expert for Blostem. "
            "Based on activity logs, provide a RELEVANCE SCORE 0-100. "
            "Return ONLY JSON: {'score': 0-100}."
        )
        
        user_prompt = f"Activity Logs:\n{logs_text}\n\nScore this deal's current relevance."
        
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
        """
        Generate a personalized email subject and body based on deal context.
        """
        if not self.client:
            return {"subject": "AI Draft", "body": "LLM offline. Please check GROQ_API_KEY."}

        recent_logs = logs[-3:]
        logs_text = "\n".join([f"- {l.get('message')}" for l in recent_logs])

        system_prompt = (
            "You are a world-class B2B sales copywriter for Blostem. "
            "Blostem provides FD distribution infrastructure for Banks and Fintechs in India. "
            "Generate a professional, high-conversion email outreach. "
            "The tone should be 'Problem-Solving' and 'Consultative'. "
            "If the current status is 'Unknown', infer it from the activity logs. "
            "Status Categories: Deal Opened, Outreach Initiated, Engaged, Negotiation/Evaluation, Deal Won, Deal Lost. "
            "Return ONLY JSON with 'subject' and 'body'. No preamble."
        )

        user_prompt = (
            f"Company: {company_name}\n"
            f"Current Pipeline State: {current_status}\n"
            f"Recent Activity Logs:\n{logs_text}\n\n"
            f"Generate a personalized outreach email to move this deal forward."
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

llm_service = LLMService()
