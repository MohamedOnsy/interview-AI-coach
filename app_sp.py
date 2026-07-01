"""
INTERVAI – AI Interview Coach with Voice (TTS & STT)

Uses Streamlit's audio_input (no pyaudio required) and speech_recognition for transcription.
All Gemini API calls are wrapped with retry logic to handle temporary overloads.
"""

import streamlit as st
import time
from agents.question_agent import QuestionAgent
from agents.followup_agent import FollowupAgent
from agents.evaluation_agent import EvaluationAgent
from agents.report_agent import ReportAgent

# logo importing 
from PIL import Image

logo = Image.open("ui/logo.png")

# Speech modules
from speech.tts import text_to_speech
from speech.stt import speech_to_text

st.set_page_config(page_title="INTERVAI", page_icon="🎤", layout="centered")

# ----- Language setup -----
if "lang" not in st.session_state:
    st.session_state.lang = "en"

LANG = {
    "en": {
        "title": "🎤 INTERVAI",
        "caption": "Voice‑enabled AI interview coach – speak your answers",
        "candidate_name": "Candidate Name",
        "role": "Role",
        "role_placeholder": "e.g. AI Engineer",
        "level": "Level",
        "levels": ["Beginner", "Entry Level", "Mid Level", "Senior Level"],
        "personality": "Interviewer Personality",
        "personalities": ["Friendly", "Formal", "Strict", "Casual"],
        "num_questions": "Number of Questions",
        "start_btn": "Start Interview 🚀",
        "role_error": "You must enter a Role first",
        "generating_first": "Generating first question…",
        "question_label": "Question",
        "of": "of",
        "your_answer": "Your Answer",
        "submit_answer": "Submit Answer ✅",
        "answer_warning": "Please write or record an answer first",
        "evaluating": "Evaluating your answer…",
        "quick_eval": "📊 Quick Evaluation",
        "technical": "Technical Accuracy",
        "communication": "Communication Skills",
        "confidence": "Confidence",
        "strengths": "Strengths",
        "weaknesses": "Weaknesses",
        "improved_answer": "Improved Answer",
        "generating_next": "Generating next question…",
        "preparing_report": "Preparing final report…",
        "final_report": "📋 Final Report",
        "candidate": "Candidate",
        "role_label": "Role",
        "level_label": "Level",
        "overall_score": "Overall Score",
        "hiring_rec": "Hiring Recommendation",
        "summary": "📝 Summary",
        "top_strengths": "✅ Top Strengths",
        "top_weaknesses": "⚠️ Areas to Improve",
        "suggestions": "💡 Suggested Improvements",
        "new_interview": "🔁 New Interview",
        "listen_btn": "🔊 Listen to Question",
        "record_btn": "🎤 Record Answer",
        "retry": "🔄 Retry",
    },
    "ar": {
        "title": "🎤 مدرب المقابلات بالذكاء الاصطناعي",
        "caption": "نسخة تجريبية (مع الصوت) – تحدث بإجاباتك",
        "candidate_name": "اسم المرشح",
        "role": "الوظيفة (Role)",
        "role_placeholder": "مثال: AI Engineer",
        "level": "المستوى",
        "levels": ["مبتدئ", "Entry Level", "Mid Level", "Senior Level"],
        "personality": "شخصية المُحاور",
        "personalities": ["Friendly", "Formal", "Strict", "Casual"],
        "num_questions": "عدد الأسئلة",
        "start_btn": "ابدأ الإنترفيو 🚀",
        "role_error": "لازم تكتب الـ Role الأول",
        "generating_first": "جاري توليد أول سؤال…",
        "question_label": "سؤال",
        "of": "من",
        "your_answer": "إجابتك",
        "submit_answer": "إرسال الإجابة ✅",
        "answer_warning": "اكتب أو سجّل إجابة أولاً",
        "evaluating": "جاري تقييم إجابتك…",
        "quick_eval": "📊 تقييم سريع للإجابة دي",
        "technical": "الدقة التقنية",
        "communication": "مهارات التواصل",
        "confidence": "الثقة",
        "strengths": "نقاط القوة",
        "weaknesses": "نقاط الضعف",
        "improved_answer": "إجابة محسّنة",
        "generating_next": "جاري توليد السؤال التالي…",
        "preparing_report": "جاري إعداد التقرير النهائي…",
        "final_report": "📋 التقرير النهائي",
        "candidate": "المرشح",
        "role_label": "الوظيفة",
        "level_label": "المستوى",
        "overall_score": "النتيجة الإجمالية",
        "hiring_rec": "توصية التوظيف",
        "summary": "📝 الملخص",
        "top_strengths": "✅ أقوى النقاط",
        "top_weaknesses": "⚠️ نقاط تحتاج تحسين",
        "suggestions": "💡 اقتراحات للتحسين",
        "new_interview": "🔁 إنترفيو جديد",
        "listen_btn": "🔊 استمع للسؤال",
        "record_btn": "🎤 سجّل الإجابة",
        "retry": "🔄 حاول مجدداً",
    },
}

lang_choice = st.radio(
    "🌐 Language / اللغة",
    options=["en", "ar"],
    format_func=lambda x: "English" if x == "en" else "العربية",
    horizontal=True,
    index=0 if st.session_state.lang == "en" else 1,
    key="lang_selector"
)
st.session_state.lang = lang_choice
T = LANG[st.session_state.lang]

# ----- Session state init -----
if "stage" not in st.session_state:
    st.session_state.stage = "setup"
    st.session_state.question_agent = None
    st.session_state.followup_agent = None
    st.session_state.evaluation_agent = None
    st.session_state.current_question = ""
    st.session_state.evaluations = []
    st.session_state.final_report = None
    st.session_state.error = None

# ----- Helper to play audio -----
def play_audio(audio_bytes, autoplay=True):
    if audio_bytes:
        st.audio(audio_bytes, format="audio/mp3", autoplay=autoplay)

# ----- Helper: call an agent method with retry -----
def call_with_retry(func, *args, max_retries=2, **kwargs):
    for attempt in range(max_retries + 1):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            if "503" in str(e) or "UNAVAILABLE" in str(e):
                if attempt < max_retries:
                    wait = 2 ** attempt
                    time.sleep(wait)
                    continue
                else:
                    raise
            else:
                raise
    return None

# ----- STAGE 1: Setup -----
if st.session_state.stage == "setup":
    st.title(T["title"])
    st.caption(T["caption"])
    with st.form("setup_form"):
        candidate_name = st.text_input(T["candidate_name"], value="Candidate")
        role = st.text_input(T["role"], placeholder=T["role_placeholder"])
        level = st.selectbox(T["level"], T["levels"])
        personality = st.selectbox(T["personality"], T["personalities"])
        total_questions = st.slider(T["num_questions"], min_value=2, max_value=10, value=3)
        submitted = st.form_submit_button(T["start_btn"])

    if submitted:
        if not role.strip():
            st.error(T["role_error"])
        else:
            level_for_agents = level
            if level in ["Beginner", "مبتدئ"]:
                level_for_agents = "Beginner (very simple, foundational questions only)"
            st.session_state.candidate_name = candidate_name
            st.session_state.role = role
            st.session_state.level = level_for_agents
            st.session_state.personality = personality

            try:
                st.session_state.question_agent = QuestionAgent(
                    role=role,
                    total_questions=total_questions,
                    level=level_for_agents,
                    personality=personality,
                    language=st.session_state.lang
                )
                st.session_state.followup_agent = FollowupAgent(
                    role=role,
                    personality=personality,
                    level=level_for_agents
                )
                st.session_state.evaluation_agent = EvaluationAgent(
                    role=role,
                    level=level_for_agents
                )
            except Exception as e:
                st.error(f"Failed to initialise agents: {e}")
                st.stop()

            try:
                with st.spinner(T["generating_first"]):
                    first_question = call_with_retry(
                        st.session_state.question_agent.generate_first_question
                    )
            except Exception as e:
                st.error(f"⚠️ Could not generate question: {e}")
                st.info("This is usually a temporary overload of the Gemini API. Please try again.")
                if st.button(T["retry"]):
                    st.rerun()
                st.stop()

            st.session_state.current_question = first_question
            st.session_state.stage = "interview"
            st.rerun()

# ----- STAGE 2: Interview -----
elif st.session_state.stage == "interview":
    qa = st.session_state.question_agent
    progress = qa.current_question
    total = qa.total_questions

    st.progress(progress / total if total else 0)
    st.subheader(f"{T['question_label']} {progress + 1} {T['of']} {total}")
    st.info(st.session_state.current_question)

    # Listen button
    col_listen, _ = st.columns([1, 5])
    with col_listen:
        if st.button(T["listen_btn"], use_container_width=True):
            tts_lang = "ar" if st.session_state.lang == "ar" else "en"
            audio_bytes = text_to_speech(st.session_state.current_question, lang=tts_lang)
            if audio_bytes:
                play_audio(audio_bytes, autoplay=True)

    # ----- Answer input (voice first, then text) -----
    answer_key = f"answer_{progress}"
    if answer_key not in st.session_state:
        st.session_state[answer_key] = ""

    # --- Process audio input BEFORE the text area ---
    audio_input_key = f"audio_input_{progress}"
    audio_data = st.audio_input(
        T["record_btn"],
        key=audio_input_key,
        help="Click to record your answer (max 5 minutes)"
    )

    if audio_data is not None:
        audio_bytes = audio_data.getvalue()
        stt_lang = "ar-EG" if st.session_state.lang == "ar" else "en-US"
        with st.spinner("Transcribing your speech…"):
            transcribed = speech_to_text(audio_bytes, language=stt_lang)
        if transcribed:
            # Update session state BEFORE the text area is rendered
            st.session_state[answer_key] = transcribed
        else:
            st.warning("Could not transcribe audio. Please type your answer.")

    # --- Now render the text area (will show the updated value if any) ---
    answer = st.text_area(
        T["your_answer"],
        value=st.session_state[answer_key],
        key=answer_key,
        height=150
    )

    # ----- Submit -----
    col1, col2 = st.columns(2)
    with col1:
        submit_answer = st.button(T["submit_answer"], use_container_width=True)

    if submit_answer:
        current_answer = st.session_state.get(answer_key, "")
        if not current_answer.strip():
            st.warning(T["answer_warning"])
        else:
            try:
                with st.spinner(T["evaluating"]):
                    evaluation = call_with_retry(
                        st.session_state.evaluation_agent.evaluate_answer,
                        question=st.session_state.current_question,
                        answer=current_answer
                    )
            except Exception as e:
                st.error(f"⚠️ Evaluation failed: {e}")
                if st.button(T["retry"]):
                    st.rerun()
                st.stop()

            st.session_state.evaluations.append(evaluation)
            qa.add_to_history(st.session_state.current_question, current_answer)
            qa.increment_question_count()

            with st.expander(T["quick_eval"], expanded=True):
                st.write(f"**{T['technical']}:** {evaluation.get('technical_accuracy')}/10")
                st.write(f"**{T['communication']}:** {evaluation.get('communication_skills')}/10")
                st.write(f"**{T['confidence']}:** {evaluation.get('confidence')}/10")
                st.write(f"**{T['strengths']}:**", evaluation.get("strengths", []))
                st.write(f"**{T['weaknesses']}:**", evaluation.get("weaknesses", []))
                st.write(f"**{T['improved_answer']}:**", evaluation.get("improved_answer", ""))

            if qa.interview_finished():
                st.session_state.stage = "report"
                st.rerun()
            else:
                try:
                    with st.spinner(T["generating_next"]):
                        next_question = call_with_retry(
                            st.session_state.followup_agent.generate_followup_question,
                            history=qa.history,
                            last_answer=current_answer
                        )
                except Exception as e:
                    st.error(f"⚠️ Could not generate next question: {e}")
                    if st.button(T["retry"]):
                        st.rerun()
                    st.stop()

                st.session_state.current_question = next_question
                if answer_key in st.session_state:
                    del st.session_state[answer_key]
                st.rerun()

# ----- STAGE 3: Report -----
elif st.session_state.stage == "report":
    if st.session_state.final_report is None:
        try:
            with st.spinner(T["preparing_report"]):
                report_agent = ReportAgent(
                    role=st.session_state.role,
                    candidate_name=st.session_state.candidate_name,
                    level=st.session_state.level
                )
                st.session_state.final_report = call_with_retry(
                    report_agent.generate_final_report,
                    evaluations=st.session_state.evaluations,
                    history=st.session_state.question_agent.history
                )
        except Exception as e:
            st.error(f"⚠️ Failed to generate report: {e}")
            if st.button(T["retry"]):
                st.rerun()
            st.stop()

    report = st.session_state.final_report
    st.header(T["final_report"])
    st.subheader(f"{T['candidate']}: {report['candidate_name']}")
    st.caption(f"{T['role_label']}: {report['role']} | {T['level_label']}: {report['level']}")

    col1, col2, col3 = st.columns(3)
    col1.metric(T["technical"], f"{report['scores']['technical_accuracy']}/10")
    col2.metric(T["communication"], f"{report['scores']['communication_skills']}/10")
    col3.metric(T["confidence"], f"{report['scores']['confidence']}/10")
    st.metric(T["overall_score"], f"{report.get('overall_score', 0)}/10")
    st.write(f"**{T['hiring_rec']}:** {report.get('hiring_recommendation', 'N/A')}")

    st.markdown(f"### {T['summary']}")
    st.write(report.get("summary", ""))
    st.markdown(f"### {T['top_strengths']}")
    for s in report.get("top_strengths", []):
        st.write(f"- {s}")
    st.markdown(f"### {T['top_weaknesses']}")
    for w in report.get("top_weaknesses", []):
        st.write(f"- {w}")
    st.markdown(f"### {T['suggestions']}")
    for imp in report.get("suggested_improvements", []):
        st.write(f"- {imp}")

    st.divider()
    if st.button(T["new_interview"]):
        for key in list(st.session_state.keys()):
            if key != "lang":
                del st.session_state[key]
        st.rerun()