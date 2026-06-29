from modules.gemini import client, MODEL_NAME
import json
import re


class EvaluationAgent:
    """
    Evaluates a candidate's interview answer across three dimensions:
    - Technical Accuracy
    - Communication Skills
    - Confidence

    Returns a structured (JSON) result for easy use in reports/UI.
    """

    def __init__(self, role, level="Entry Level"):
        self.role = role
        self.level = level

    def _build_prompt(self, question, answer):
        return f"""
You are a strict but fair professional interview evaluator.

Role being interviewed for:
{self.role}

Candidate level:
{self.level}

Interview question:
{question}

Candidate's answer:
{answer}

Evaluate the candidate's answer based on three dimensions:

1. Technical Accuracy (0-10): How correct, relevant, and complete the technical content is.
2. Communication Skills (0-10): How clearly and effectively the candidate expressed their ideas.
3. Confidence (0-10): How confident and decisive the answer sounds (based on wording, hedging, clarity — not tone of voice).

Also provide:
- A short list of strengths (max 3 bullet points)
- A short list of weaknesses (max 3 bullet points)
- One improved version of the answer (2-3 sentences max)

Return STRICTLY valid JSON in this exact format, with no extra text before or after it:

{{
  "technical_accuracy": <number>,
  "communication_skills": <number>,
  "confidence": <number>,
  "strengths": ["...", "..."],
  "weaknesses": ["...", "..."],
  "improved_answer": "..."
}}
"""

    def _extract_json(self, raw_text):
        cleaned = raw_text.strip()

        cleaned = re.sub(r"^```json", "", cleaned)
        cleaned = re.sub(r"^```", "", cleaned)
        cleaned = re.sub(r"```$", "", cleaned)
        cleaned = cleaned.strip()

        return json.loads(cleaned)

    def evaluate_answer(self, question, answer):
        prompt = self._build_prompt(question, answer)

        try:
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt
            )
            raw_text = response.text.strip()
            result = self._extract_json(raw_text)

        except json.JSONDecodeError:
            result = {
                "technical_accuracy": 0,
                "communication_skills": 0,
                "confidence": 0,
                "strengths": [],
                "weaknesses": ["Could not parse evaluation. Please try again."],
                "improved_answer": ""
            }

        except Exception as e:
            result = {
                "technical_accuracy": 0,
                "communication_skills": 0,
                "confidence": 0,
                "strengths": [],
                "weaknesses": [f"Error during evaluation: {e}"],
                "improved_answer": ""
            }

        return result