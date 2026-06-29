from modules.gemini import client, MODEL_NAME
import json
import re


class ReportAgent:
    """
    Aggregates all per-question evaluations from the interview
    into one final summary report:
    - Average scores (Technical, Communication, Confidence)
    - Overall strengths & weaknesses
    - Suggested improvements
    """

    def __init__(self, role, candidate_name="Candidate", level="Entry Level"):
        self.role = role
        self.candidate_name = candidate_name
        self.level = level

    def _calculate_averages(self, evaluations):
        if not evaluations:
            return {
                "technical_accuracy": 0,
                "communication_skills": 0,
                "confidence": 0
            }

        total_technical = sum(e.get("technical_accuracy", 0) for e in evaluations)
        total_communication = sum(e.get("communication_skills", 0) for e in evaluations)
        total_confidence = sum(e.get("confidence", 0) for e in evaluations)

        count = len(evaluations)

        return {
            "technical_accuracy": round(total_technical / count, 1),
            "communication_skills": round(total_communication / count, 1),
            "confidence": round(total_confidence / count, 1)
        }

    def _collect_points(self, evaluations, key):
        points = []
        for e in evaluations:
            points.extend(e.get(key, []))
        return points

    def _build_prompt(self, averages, all_strengths, all_weaknesses, history):
        formatted_history = ""
        for i, item in enumerate(history, start=1):
            formatted_history += f"Q{i}: {item['question']}\nA{i}: {item['answer']}\n\n"

        return f"""
You are a senior hiring manager writing a final interview summary report.

Candidate name:
{self.candidate_name}

Role:
{self.role}

Candidate level:
{self.level}

Average scores from the interview:
- Technical Accuracy: {averages['technical_accuracy']}/10
- Communication Skills: {averages['communication_skills']}/10
- Confidence: {averages['confidence']}/10

Collected strengths noted across all answers:
{all_strengths}

Collected weaknesses noted across all answers:
{all_weaknesses}

Full interview transcript:
{formatted_history}

Task:
Write a final hiring summary based on everything above.

Return STRICTLY valid JSON in this exact format, with no extra text before or after it:

{{
  "overall_score": <number out of 10>,
  "summary": "2-3 sentence overall impression of the candidate",
  "top_strengths": ["...", "...", "..."],
  "top_weaknesses": ["...", "...", "..."],
  "suggested_improvements": ["...", "...", "..."],
  "hiring_recommendation": "Strong Hire / Hire / Borderline / No Hire"
}}
"""

    def _extract_json(self, raw_text):
        cleaned = raw_text.strip()
        cleaned = re.sub(r"^```json", "", cleaned)
        cleaned = re.sub(r"^```", "", cleaned)
        cleaned = re.sub(r"```$", "", cleaned)
        cleaned = cleaned.strip()
        return json.loads(cleaned)

    def generate_final_report(self, evaluations, history):
        averages = self._calculate_averages(evaluations)
        all_strengths = self._collect_points(evaluations, "strengths")
        all_weaknesses = self._collect_points(evaluations, "weaknesses")

        prompt = self._build_prompt(averages, all_strengths, all_weaknesses, history)

        try:
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt
            )
            raw_text = response.text.strip()
            ai_summary = self._extract_json(raw_text)

        except json.JSONDecodeError:
            ai_summary = {
                "overall_score": 0,
                "summary": "Could not generate summary. Please try again.",
                "top_strengths": [],
                "top_weaknesses": [],
                "suggested_improvements": [],
                "hiring_recommendation": "N/A"
            }

        except Exception as e:
            ai_summary = {
                "overall_score": 0,
                "summary": f"Error generating report: {e}",
                "top_strengths": [],
                "top_weaknesses": [],
                "suggested_improvements": [],
                "hiring_recommendation": "N/A"
            }

        final_report = {
            "candidate_name": self.candidate_name,
            "role": self.role,
            "level": self.level,
            "scores": averages,
            **ai_summary
        }

        return final_report