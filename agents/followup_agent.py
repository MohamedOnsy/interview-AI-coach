from modules.gemini import client, MODEL_NAME
import random


class FollowupAgent:
    """
    Dynamically generates follow-up interview questions based on
    the candidate's previous answer and the full interview history.
    Works with ANY role — no hardcoded questions.
    """

    def __init__(self,
                 role,
                 personality="Friendly",
                 level="Entry Level"):

        self.role = role
        self.personality = personality
        self.level = level

    def _format_history(self, history):
        if not history:
            return "No previous questions yet."

        formatted = ""
        for i, item in enumerate(history, start=1):
            formatted += f"Q{i}: {item['question']}\nA{i}: {item['answer']}\n\n"

        return formatted.strip()

    def _build_followup_prompt(self, history, last_answer):
        angles = [
            "dig deeper into a technical detail the candidate mentioned",
            "challenge the candidate with a related scenario based on their answer",
            "ask them to clarify or justify something they said",
            "explore a skill or tool they mentioned in more depth",
            "ask about a real example or project related to their answer",
        ]
        chosen_angle = random.choice(angles)

        formatted_history = self._format_history(history)

        return f"""
You are a real, professional human interviewer conducting a live interview
for the role of: {self.role}

You are NOT reading from a script. This is a live, natural conversation.

Personality style:
{self.personality}

Candidate level:
{self.level}

Interview history so far:
{formatted_history}

Candidate's most recent answer:
{last_answer}

Guidance for the next question:
{chosen_angle}

Rules:
- The next question MUST be a direct, natural reaction to the candidate's most recent answer
- Do not repeat or rephrase any previous question
- Do not greet the candidate
- Do not explain or justify the question
- Do not number it
- Make it sound like something a real interviewer would say out loud in the moment

Return ONLY the question text, nothing else.
"""

    def generate_followup_question(self, history, last_answer):
        prompt = self._build_followup_prompt(history, last_answer)

        try:
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt
            )
            question = response.text.strip()
        except Exception as e:
            question = f"Error generating follow-up question: {e}"

        return question