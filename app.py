import streamlit as st

from agents.question_agent import QuestionAgent
from agents.followup_agent import FollowupAgent
from agents.evaluation_agent import EvaluationAgent
from agents.report_agent import ReportAgent


st.set_page_config(page_title="AI Interview Coach", page_icon="🎤", layout="centered")

st.title("🎤 AI Interview Coach")
st.caption("نسخة تجريبية (نصية) لتجربة كل الـ Agents قبل إضافة الصوت")


# ---------- Session State Initialization ----------
if "stage" not in st.session_state:
    st.session_state.stage = "setup"          # setup -> interview -> report
    st.session_state.question_agent = None
    st.session_state.followup_agent = None
    st.session_state.evaluation_agent = None
    st.session_state.current_question = ""
    st.session_state.evaluations = []          # كل تقييمات الأسئلة
    st.session_state.final_report = None


# ---------- Stage 1: Setup ----------
if st.session_state.stage == "setup":

    with st.form("setup_form"):
        candidate_name = st.text_input("اسم المرشح", value="Candidate")
        role = st.text_input("الوظيفة (Role)", placeholder="مثال: AI Engineer")
        level = st.selectbox("المستوى", ["Entry Level", "Mid Level", "Senior Level"])
        personality = st.selectbox("شخصية المُحاور", ["Friendly", "Formal", "Strict", "Casual"])
        total_questions = st.slider("عدد الأسئلة", min_value=2, max_value=10, value=3)

        submitted = st.form_submit_button("ابدأ الإنترفيو 🚀")

    if submitted:
        if not role.strip():
            st.error("لازم تكتب الـ Role الأول")
        else:
            st.session_state.candidate_name = candidate_name
            st.session_state.role = role
            st.session_state.level = level
            st.session_state.personality = personality

            st.session_state.question_agent = QuestionAgent(
                role=role,
                total_questions=total_questions,
                level=level,
                personality=personality
            )
            st.session_state.followup_agent = FollowupAgent(
                role=role,
                personality=personality,
                level=level
            )
            st.session_state.evaluation_agent = EvaluationAgent(
                role=role,
                level=level
            )

            with st.spinner("جاري توليد أول سؤال..."):
                first_question = st.session_state.question_agent.generate_first_question()

            st.session_state.current_question = first_question
            st.session_state.stage = "interview"
            st.rerun()


# ---------- Stage 2: Interview Loop ----------
elif st.session_state.stage == "interview":

    qa = st.session_state.question_agent
    progress = qa.current_question
    total = qa.total_questions

    st.progress(progress / total if total else 0)
    st.subheader(f"سؤال {progress + 1} من {total}")

    st.info(st.session_state.current_question)

    answer = st.text_area("إجابتك", key=f"answer_{progress}", height=150)

    col1, col2 = st.columns(2)

    with col1:
        submit_answer = st.button("إرسال الإجابة ✅", use_container_width=True)

    if submit_answer:
        if not answer.strip():
            st.warning("اكتب إجابة الأول")
        else:
            with st.spinner("جاري تقييم إجابتك..."):
                evaluation = st.session_state.evaluation_agent.evaluate_answer(
                    question=st.session_state.current_question,
                    answer=answer
                )

            st.session_state.evaluations.append(evaluation)
            qa.add_to_history(st.session_state.current_question, answer)
            qa.increment_question_count()

            with st.expander("📊 تقييم سريع للإجابة دي"):
                st.write(f"**Technical Accuracy:** {evaluation.get('technical_accuracy')}/10")
                st.write(f"**Communication Skills:** {evaluation.get('communication_skills')}/10")
                st.write(f"**Confidence:** {evaluation.get('confidence')}/10")
                st.write("**Strengths:**", evaluation.get("strengths", []))
                st.write("**Weaknesses:**", evaluation.get("weaknesses", []))
                st.write("**Improved Answer:**", evaluation.get("improved_answer", ""))

            if qa.interview_finished():
                st.session_state.stage = "report"
                st.rerun()
            else:
                with st.spinner("جاري توليد السؤال التالي..."):
                    next_question = st.session_state.followup_agent.generate_followup_question(
                        history=qa.history,
                        last_answer=answer
                    )

                st.session_state.current_question = next_question
                st.rerun()


# ---------- Stage 3: Final Report ----------
elif st.session_state.stage == "report":

    if st.session_state.final_report is None:
        with st.spinner("جاري إعداد التقرير النهائي..."):
            report_agent = ReportAgent(
                role=st.session_state.role,
                candidate_name=st.session_state.candidate_name,
                level=st.session_state.level
            )

            st.session_state.final_report = report_agent.generate_final_report(
                evaluations=st.session_state.evaluations,
                history=st.session_state.question_agent.history
            )

    report = st.session_state.final_report

    st.header("📋 التقرير النهائي")

    st.subheader(f"المرشح: {report['candidate_name']}")
    st.caption(f"الوظيفة: {report['role']} | المستوى: {report['level']}")

    col1, col2, col3 = st.columns(3)
    col1.metric("Technical", f"{report['scores']['technical_accuracy']}/10")
    col2.metric("Communication", f"{report['scores']['communication_skills']}/10")
    col3.metric("Confidence", f"{report['scores']['confidence']}/10")

    st.metric("Overall Score", f"{report.get('overall_score', 0)}/10")
    st.write(f"**Hiring Recommendation:** {report.get('hiring_recommendation', 'N/A')}")

    st.markdown("### 📝 الملخص")
    st.write(report.get("summary", ""))

    st.markdown("### ✅ أقوى النقاط")
    for s in report.get("top_strengths", []):
        st.write(f"- {s}")

    st.markdown("### ⚠️ نقاط تحتاج تحسين")
    for w in report.get("top_weaknesses", []):
        st.write(f"- {w}")

    st.markdown("### 💡 اقتراحات للتحسين")
    for imp in report.get("suggested_improvements", []):
        st.write(f"- {imp}")

    st.divider()
    if st.button("🔁 إنترفيو جديد"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()