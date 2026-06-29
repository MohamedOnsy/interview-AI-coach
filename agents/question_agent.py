from modules.gemini import client, MODEL_NAME
import random


class QuestionAgent:
    """
    Dynamically generates interview questions using Gemini.
    Works with ANY role typed by the user — no hardcoded role list.
    """

    def __init__(self,
                 role,
                 total_questions=5,
                 level="Entry Level",
                 personality="Friendly"):

        self.role = role
        self.level = level
        self.personality = personality

        self.total_questions = total_questions
        self.current_question = 0

        self.history = []

    def _build_first_prompt(self):
        angles = [
            "start with a question about the candidate's general experience",
            "start with a practical scenario-based question",
            "start with a question testing fundamental knowledge",
            "start with a question about a real project they might have worked on",
        ]
        chosen_angle = random.choice(angles)

        return f"""
You are a real, professional human interviewer conducting a live interview
for the role of: {self.role}

You are NOT reading from a script. Generate a fresh, natural question as if this is a real conversation.

Personality style:
{self.personality}

Candidate level:
{self.level}

Guidance for this question:
{chosen_angle}

Rules:
- Base the question on the skills, knowledge, and responsibilities typically required for the role "{self.role}", even if you have to infer them yourself
- Do not greet the candidate
- Do not explain or justify the question
- Do not number it
- Make it sound like something a real interviewer would say out loud

Return ONLY the question text, nothing else.
"""

    def generate_first_question(self):
        prompt = self._build_first_prompt()

        try:
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt
            )
            question = response.text.strip()
        except Exception as e:
            question = f"Error generating question: {e}"

        return question

    def add_to_history(self, question, answer):
        self.history.append({
            "question": question,
            "answer": answer
        })

    def increment_question_count(self):
        self.current_question += 1

    def interview_finished(self):
        return self.current_question >= self.total_questions