"""
INTERVAI – AI Interview Coach with Voice (TTS & STT)
Modern SaaS UI Design with Auto-play Audio
"""

import streamlit as st
import time
import base64
from PIL import Image
import json

# Agents
from agents.question_agent import QuestionAgent
from agents.followup_agent import FollowupAgent
from agents.evaluation_agent import EvaluationAgent
from agents.report_agent import ReportAgent

# Speech modules
from speech.tts import text_to_speech
from speech.stt import speech_to_text

# Page config
st.set_page_config(
    page_title="INTERVAI - AI Interview Coach",
    page_icon="🎤",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================
# CUSTOM CSS - Modern SaaS Design
# ============================================
def load_css():
    """Load custom CSS for modern UI"""
    css = """
    <style>
        /* Import Google Fonts */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
        
        /* Global Reset */
        * {
            font-family: 'Inter', sans-serif !important;
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        /* Hide default Streamlit elements */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        .stApp {
            background: linear-gradient(135deg, #0a0a0f 0%, #1a1a2e 50%, #16213e 100%);
            background-attachment: fixed;
        }
        
        /* Main container */
        .main {
            padding: 2rem;
            max-width: 1200px;
            margin: 0 auto;
        }
        
        /* Glassmorphism Card */
        .glass-card {
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 24px;
            padding: 2rem;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
            transition: all 0.3s ease;
            animation: fadeInUp 0.5s ease;
        }
        
        .glass-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 12px 48px rgba(0, 0, 0, 0.4);
            border-color: rgba(255, 255, 255, 0.15);
        }
        
        /* Gradient Text */
        .gradient-text {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            font-weight: 800;
        }
        
        /* Modern Button */
        .btn-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 12px 36px;
            border-radius: 50px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
            position: relative;
            overflow: hidden;
            width: 100%;
        }
        
        .btn-primary:hover {
            transform: scale(1.05);
            box-shadow: 0 8px 30px rgba(102, 126, 234, 0.6);
        }
        
        .btn-primary:active {
            transform: scale(0.95);
        }
        
        .btn-primary::before {
            content: '';
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
            transform: scale(0);
            transition: transform 0.5s ease;
        }
        
        .btn-primary:hover::before {
            transform: scale(1);
        }
        
        /* Feature Cards */
        .feature-card {
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid rgba(255, 255, 255, 0.06);
            border-radius: 20px;
            padding: 2rem;
            text-align: center;
            transition: all 0.3s ease;
            animation: fadeInUp 0.6s ease;
        }
        
        .feature-card:hover {
            background: rgba(255, 255, 255, 0.06);
            transform: translateY(-10px);
            border-color: rgba(102, 126, 234, 0.3);
            box-shadow: 0 8px 32px rgba(102, 126, 234, 0.1);
        }
        
        .feature-icon {
            font-size: 3rem;
            margin-bottom: 1rem;
        }
        
        /* Progress Bar */
        .custom-progress {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 50px;
            height: 8px;
            overflow: hidden;
            margin: 1rem 0;
        }
        
        .custom-progress-bar {
            height: 100%;
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            border-radius: 50px;
            transition: width 0.5s ease;
        }
        
        /* Score Cards */
        .score-card {
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid rgba(255, 255, 255, 0.06);
            border-radius: 16px;
            padding: 1.5rem;
            text-align: center;
            transition: all 0.3s ease;
        }
        
        .score-card:hover {
            background: rgba(255, 255, 255, 0.06);
            transform: scale(1.02);
        }
        
        .score-value {
            font-size: 2.5rem;
            font-weight: 700;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .score-label {
            color: #a0aec0;
            font-size: 0.9rem;
            margin-top: 0.5rem;
        }
        
        /* Progress Circle */
        .progress-circle {
            width: 150px;
            height: 150px;
            border-radius: 50%;
            background: conic-gradient(
                #667eea var(--progress, 0%),
                rgba(255, 255, 255, 0.1) var(--progress, 0%)
            );
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto;
            position: relative;
        }
        
        .progress-circle-inner {
            width: 120px;
            height: 120px;
            border-radius: 50%;
            background: #1a1a2e;
            display: flex;
            align-items: center;
            justify-content: center;
            flex-direction: column;
        }
        
        /* Animations */
        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        @keyframes pulse {
            0% {
                transform: scale(1);
                opacity: 1;
            }
            50% {
                transform: scale(1.1);
                opacity: 0.7;
            }
            100% {
                transform: scale(1);
                opacity: 1;
            }
        }
        
        @keyframes glow {
            0% {
                box-shadow: 0 0 20px rgba(102, 126, 234, 0.2);
            }
            50% {
                box-shadow: 0 0 40px rgba(102, 126, 234, 0.6);
            }
            100% {
                box-shadow: 0 0 20px rgba(102, 126, 234, 0.2);
            }
        }
        
        .pulse-animation {
            animation: pulse 1.5s ease-in-out infinite;
        }
        
        .glow-animation {
            animation: glow 2s ease-in-out infinite;
        }
        
        /* Recording indicator */
        .recording-indicator {
            display: inline-flex;
            align-items: center;
            gap: 10px;
            padding: 8px 16px;
            background: rgba(239, 68, 68, 0.2);
            border-radius: 50px;
            border: 1px solid rgba(239, 68, 68, 0.3);
            color: #ef4444;
        }
        
        .recording-dot {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background: #ef4444;
            animation: pulse 1s ease-in-out infinite;
        }
        
        /* Typography */
        h1, h2, h3, h4, h5, h6 {
            color: white;
            font-weight: 700;
        }
        
        p, .stText, .stCaption {
            color: #a0aec0;
        }
        
        /* Input fields */
        .stTextInput > div > div > input,
        .stSelectbox > div > div,
        .stTextArea > div > div > textarea {
            background: rgba(255, 255, 255, 0.05) !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            border-radius: 12px !important;
            color: white !important;
            padding: 12px 16px !important;
            transition: all 0.3s ease !important;
        }
        
        .stTextInput > div > div > input:focus,
        .stSelectbox > div > div:focus,
        .stTextArea > div > div > textarea:focus {
            border-color: #667eea !important;
            box-shadow: 0 0 20px rgba(102, 126, 234, 0.1) !important;
        }
        
        .stSelectbox > div > div {
            background: rgba(255, 255, 255, 0.05) !important;
        }
        
        /* Custom scrollbar */
        ::-webkit-scrollbar {
            width: 8px;
        }
        
        ::-webkit-scrollbar-track {
            background: rgba(255, 255, 255, 0.05);
            border-radius: 10px;
        }
        
        ::-webkit-scrollbar-thumb {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 10px;
        }
        
        /* Responsive */
        @media (max-width: 768px) {
            .glass-card {
                padding: 1.5rem;
            }
            .score-value {
                font-size: 2rem;
            }
        }
        
        /* Spinner override */
        .stSpinner > div {
            border-color: #667eea !important;
        }
        
        /* Audio player styling - make it more subtle */
        .stAudio {
            background: transparent !important;
        }
        
        .stAudio audio {
            width: 100% !important;
        }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

# Load CSS
load_css()

# ============================================
# LANGUAGE SETUP
# ============================================
if "lang" not in st.session_state:
    st.session_state.lang = "en"

LANG = {
    "en": {
        "title": "INTERVAI",
        "subtitle": "Your AI-Powered Interview Coach",
        "description": "Practice realistic AI interviews, receive instant feedback, improve your communication skills, and prepare for your dream job.",
        "features": [
            {"icon": "🎤", "title": "Voice Interview", "desc": "Speak naturally and get real-time feedback"},
            {"icon": "🧠", "title": "AI Evaluation", "desc": "Instant analysis of your responses"},
            {"icon": "📊", "title": "Performance Dashboard", "desc": "Track your progress over time"}
        ],
        "start_btn": "Start Interview 🚀",
        "candidate_name": "👤 Candidate Name",
        "role": "💼 Role",
        "role_placeholder": "e.g. AI Engineer",
        "level": "📊 Level",
        "levels": ["Beginner","Entry Level","Mid Level","Senior Level"],
        "personality": "🎭 Interviewer Personality",
        "personalities": ["Friendly","Formal","Strict", "Casual"],
        "num_questions": "📝 Number of Questions",
        "setup_title": "Interview Setup",
        "setup_subtitle": "Configure your interview experience",
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
        "new_interview": "🔄 Start New Interview",
        "listen_btn": "🔊 Listen to Question",
        "record_btn": "🎤 Record Answer",
        "retry": "🔄 Retry",
        "ai_speaking": "AI Speaking...",
        "recording": "Recording...",
        "click_record": "Click the microphone to start recording",
        "problem_solving": "Problem Solving",
        "knowledge": "Knowledge",
        "audio_playing": "🔊 Audio Playing...",
    },
    "ar": {
        "title": "INTERVAI",
        "subtitle": "مدرب المقابلات بالذكاء الاصطناعي",
        "description": "تدرب على مقابلات العمل الواقعية، احصل على تغذية راجعة فورية، حسن مهارات التواصل، واستعد لوظيفة أحلامك.",
        "features": [
            {"icon": "🎤", "title": "مقابلة صوتية", "desc": "تحدث بشكل طبيعي واحصل على تغذية راجعة فورية"},
            {"icon": "🧠", "title": "تقييم بالذكاء الاصطناعي", "desc": "تحليل فوري لإجاباتك"},
            {"icon": "📊", "title": "لوحة الأداء", "desc": "تتبع تقدمك مع مرور الوقت"}
        ],
        "start_btn": "ابدأ المقابلة 🚀",
        "candidate_name": "👤 اسم المرشح",
        "role": "💼 الوظيفة",
        "role_placeholder": "مثال: مهندس ذكاء اصطناعي",
        "level": "📊 المستوى",
        "levels": ["مبتدئ", "مستوى متوسط", "مستوى متقدم", "خبير"],
        "personality": "🎭 شخصية المحاور",
        "personalities": ["ودود", "رسمي", "صارم", "عفوي"],
        "num_questions": "📝 عدد الأسئلة",
        "setup_title": "إعدادات المقابلة",
        "setup_subtitle": "خصص تجربة المقابلة الخاصة بك",
        "generating_first": "جاري توليد أول سؤال…",
        "question_label": "سؤال",
        "of": "من",
        "your_answer": "إجابتك",
        "submit_answer": "إرسال الإجابة ✅",
        "answer_warning": "اكتب أو سجّل إجابة أولاً",
        "evaluating": "جاري تقييم إجابتك…",
        "quick_eval": "📊 تقييم سريع",
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
        "new_interview": "🔄 بدء مقابلة جديدة",
        "listen_btn": "🔊 استمع للسؤال",
        "record_btn": "🎤 سجّل الإجابة",
        "retry": "🔄 حاول مجدداً",
        "ai_speaking": "الذكاء الاصطناعي يتحدث...",
        "recording": "جاري التسجيل...",
        "click_record": "اضغط على الميكروفون لبدء التسجيل",
        "problem_solving": "حل المشكلات",
        "knowledge": "المعرفة",
        "audio_playing": "🔊 جاري تشغيل الصوت...",
    },
}

# Language selector
lang_choice = st.sidebar.radio(
    "🌐",
    options=["en", "ar"],
    format_func=lambda x: "English" if x == "en" else "العربية",
    horizontal=True,
    index=0 if st.session_state.lang == "en" else 1,
    key="lang_selector"
)
st.session_state.lang = lang_choice
T = LANG[st.session_state.lang]

# ============================================
# SESSION STATE INIT
# ============================================
if "stage" not in st.session_state:
    st.session_state.stage = "landing"
    st.session_state.question_agent = None
    st.session_state.followup_agent = None
    st.session_state.evaluation_agent = None
    st.session_state.current_question = ""
    st.session_state.evaluations = []
    st.session_state.final_report = None
    st.session_state.error = None
    st.session_state.audio_played = False
    st.session_state.audio_data = None  # Store generated audio data

# ============================================
# HELPER FUNCTIONS
# ============================================
def play_audio(audio_bytes, autoplay=True):
    """Play audio with Streamlit's audio component"""
    if audio_bytes:
        # Use st.audio with autoplay
        st.audio(
            audio_bytes,
            format="audio/mp3",
            autoplay=autoplay
        )

def generate_and_play_audio(text, personality, lang="en"):
    """Generate TTS audio and return bytes"""
    try:
        audio_bytes = text_to_speech(
            text=text,
            personality=personality,
            lang=lang
        )
        return audio_bytes
    except Exception as e:
        st.warning(f"Could not generate audio: {e}")
        return None

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

def render_metric_card(label, value, max_value=10, color="#667eea"):
    """Render a modern metric card with progress bar"""
    percentage = (value / max_value) * 100
    return f"""
    <div class="score-card">
        <div style="font-size: 0.9rem; color: #a0aec0; margin-bottom: 0.5rem;">{label}</div>
        <div class="score-value">{value}/10</div>
        <div class="custom-progress" style="margin: 0.5rem 0;">
            <div class="custom-progress-bar" style="width: {percentage}%; background: {color};"></div>
        </div>
    </div>
    """

def auto_play_question():
    """Auto-generate and play audio for current question"""
    if st.session_state.current_question:
        # Generate audio only if not already generated for this question
        question_key = f"audio_{st.session_state.question_agent.current_question}"
        
        if question_key not in st.session_state:
            tts_lang = "ar" if st.session_state.lang == "ar" else "en"
            audio_bytes = generate_and_play_audio(
                text=st.session_state.current_question,
                personality=st.session_state.personality,
                lang=tts_lang
            )
            if audio_bytes:
                st.session_state[question_key] = audio_bytes
                st.session_state.audio_data = audio_bytes
                # Play audio
                play_audio(audio_bytes, autoplay=True)
                return True
        else:
            # Play stored audio
            play_audio(st.session_state[question_key], autoplay=True)
            return True
    return False

# ============================================
# STAGE 0: LANDING PAGE
# ============================================
if st.session_state.stage == "landing":
    # Main container
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("<div style='padding: 2rem 0;'>", unsafe_allow_html=True)
        
        # Logo
        st.markdown("""
            <div style="text-align: center; margin-bottom: 2rem;">
                <h1 style="font-size: 4rem; margin-bottom: 0.5rem;">
                    <span class="gradient-text">INTERVAI</span>
                </h1>
                <p style="font-size: 1.2rem; color: #a0aec0;">{}</p>
            </div>
        """.format(T["subtitle"]), unsafe_allow_html=True)
        
        # Description
        st.markdown("""
            <div style="text-align: center; margin-bottom: 3rem; padding: 0 2rem;">
                <p style="font-size: 1.1rem; line-height: 1.8; color: #cbd5e0;">{}</p>
            </div>
        """.format(T["description"]), unsafe_allow_html=True)
        
        # Features
        cols = st.columns(3)
        for idx, feature in enumerate(T["features"]):
            with cols[idx]:
                st.markdown(f"""
                    <div class="feature-card" style="animation-delay: {idx * 0.2}s;">
                        <div class="feature-icon">{feature['icon']}</div>
                        <h4 style="color: white; margin-bottom: 0.5rem;">{feature['title']}</h4>
                        <p style="color: #a0aec0; font-size: 0.9rem;">{feature['desc']}</p>
                    </div>
                """, unsafe_allow_html=True)
        
        # Start button
        st.markdown("<div style='text-align: center; margin-top: 3rem;'>", unsafe_allow_html=True)
        
        if st.button(T["start_btn"], key="start_interview", use_container_width=False):
            st.session_state.stage = "setup"
            st.rerun()
        
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

# ============================================
# STAGE 1: SETUP
# ============================================
elif st.session_state.stage == "setup":
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
            <div class="glass-card" style="margin: 2rem 0;">
                <h2 style="text-align: center; margin-bottom: 0.5rem;">{}</h2>
                <p style="text-align: center; color: #a0aec0; margin-bottom: 2rem;">{}</p>
        """.format(T["setup_title"], T["setup_subtitle"]), unsafe_allow_html=True)
        
        with st.form("setup_form", clear_on_submit=False):
            candidate_name = st.text_input(
                T["candidate_name"],
                value="Candidate",
                key="setup_name"
            )
            
            role = st.text_input(
                T["role"],
                placeholder=T["role_placeholder"],
                key="setup_role"
            )
            
            level = st.selectbox(
                T["level"],
                T["levels"],
                key="setup_level"
            )
            
            personality = st.selectbox(
                T["personality"],
                T["personalities"],
                key="setup_personality"
            )
            
            total_questions = st.slider(
                T["num_questions"],
                min_value=2,
                max_value=10,
                value=3,
                key="setup_questions"
            )
            
            st.markdown("<div style='margin-top: 1.5rem;'>", unsafe_allow_html=True)
            submitted = st.form_submit_button(
                T["start_btn"],
                use_container_width=True,
                type="primary"
            )
            st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
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
                with st.spinner("Initializing interview..."):
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

# ============================================
# STAGE 2: INTERVIEW
# ============================================
elif st.session_state.stage == "interview":
    qa = st.session_state.question_agent
    progress = qa.current_question
    total = qa.total_questions
    
    # Top bar with progress
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        st.markdown(f"""
            <div style="display: flex; align-items: center; gap: 1rem;">
                <span style="font-size: 1.2rem;">🎤</span>
                <div>
                    <div style="color: #a0aec0; font-size: 0.8rem;">{T['role_label']}</div>
                    <div style="color: white; font-weight: 600;">{st.session_state.role}</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        progress_percent = (progress / total) * 100
        st.markdown(f"""
            <div style="margin: 0.5rem 0;">
                <div style="display: flex; justify-content: space-between; color: #a0aec0; font-size: 0.8rem;">
                    <span>{T['question_label']} {progress + 1} {T['of']} {total}</span>
                    <span>{int(progress_percent)}%</span>
                </div>
                <div class="custom-progress">
                    <div class="custom-progress-bar" style="width: {progress_percent}%;"></div>
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
            <div style="text-align: right; color: #a0aec0; font-size: 0.8rem;">
                <div>{T['personality']}</div>
                <div style="color: white; font-weight: 600;">{st.session_state.personality}</div>
            </div>
        """, unsafe_allow_html=True)
    
    # Main question card
    col1, col2, col3 = st.columns([1, 3, 1])
    
    with col2:
        st.markdown("""
            <div class="glass-card" style="margin: 1rem 0;">
        """, unsafe_allow_html=True)
        
        # AI Avatar and question
        col_q1, col_q2 = st.columns([1, 5])
        
        with col_q1:
            st.markdown("""
                <div style="font-size: 3rem; text-align: center;">🤖</div>
            """, unsafe_allow_html=True)
        
        with col_q2:
            st.markdown(f"""
                <div style="color: #a0aec0; font-size: 0.8rem; margin-bottom: 0.5rem;">{T['ai_speaking']}</div>
                <div style="color: white; font-size: 1.1rem; line-height: 1.6;">{st.session_state.current_question}</div>
            """, unsafe_allow_html=True)
            
            # Auto-play audio - this will run automatically when page loads
            audio_placeholder = st.empty()
            
            # Generate and play audio automatically
            with st.spinner("🔊 Generating audio..."):
                tts_lang = "ar" if st.session_state.lang == "ar" else "en"
                audio_bytes = generate_and_play_audio(
                    text=st.session_state.current_question,
                    personality=st.session_state.personality,
                    lang=tts_lang
                )
                if audio_bytes:
                    # Store in session state for this question
                    question_key = f"audio_{progress}"
                    st.session_state[question_key] = audio_bytes
                    # Play audio
                    with audio_placeholder.container():
                        st.audio(audio_bytes, format="audio/mp3", autoplay=True)
                        # Show playing indicator
                        st.markdown(f"""
                            <div style="display: flex; align-items: center; gap: 0.5rem; margin-top: 0.5rem;">
                                <span style="color: #667eea;">🔊</span>
                                <span style="color: #a0aec0; font-size: 0.8rem;">{T['audio_playing']}</span>
                            </div>
                        """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Answer section
        st.markdown("""
            <div class="glass-card" style="margin: 1rem 0;">
                <h4 style="margin-bottom: 1rem;">{}</h4>
        """.format(T["your_answer"]), unsafe_allow_html=True)
        
        answer_key = f"answer_{progress}"
        if answer_key not in st.session_state:
            st.session_state[answer_key] = ""
        
        # Voice recording
        audio_input_key = f"audio_input_{progress}"
        audio_data = st.audio_input(
            T["record_btn"],
            key=audio_input_key,
            help="Click to record your answer (max 5 minutes)"
        )
        
        if audio_data is not None:
            audio_bytes = audio_data.getvalue()
            stt_lang = "ar" if st.session_state.lang == "ar" else "en"
            with st.spinner("Transcribing your speech…"):
                transcribed = speech_to_text(audio_bytes, language=stt_lang)
            if transcribed:
                st.session_state[answer_key] = transcribed
                st.success("✅ Audio transcribed successfully!")
            else:
                st.warning("Could not transcribe audio. Please type your answer.")
        
        # Text area
        answer = st.text_area(
            "Type your answer here...",
            value=st.session_state[answer_key],
            key=answer_key,
            height=150,
            label_visibility="collapsed"
        )
        
        # Submit button
        col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
        with col_btn2:
            submit_answer = st.button(
                T["submit_answer"],
                use_container_width=True,
                type="primary"
            )
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Handle submit
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
            
            # Show evaluation in modern cards
            with st.expander(T["quick_eval"], expanded=True):
                evals = evaluation
                
                # Score cards
                cols = st.columns(3)
                metrics = [
                    (T["technical"], evals.get('technical_accuracy', 0), "#667eea"),
                    (T["communication"], evals.get('communication_skills', 0), "#48bb78"),
                    (T["confidence"], evals.get('confidence', 0), "#ed8936")
                ]
                
                for idx, (label, value, color) in enumerate(metrics):
                    with cols[idx]:
                        st.markdown(render_metric_card(label, value, 10, color), unsafe_allow_html=True)
                
                # Strengths and weaknesses
                col_s1, col_s2 = st.columns(2)
                
                with col_s1:
                    st.markdown("""
                        <div class="glass-card" style="padding: 1rem; background: rgba(72, 187, 120, 0.1); border-color: rgba(72, 187, 120, 0.2);">
                            <h5 style="color: #48bb78; margin-bottom: 0.5rem;">✅ {}</h5>
                            <ul style="color: #a0aec0; list-style: none; padding: 0;">
                    """.format(T["strengths"]), unsafe_allow_html=True)
                    
                    for s in evaluation.get("strengths", []):
                        st.markdown(f"<li style='padding: 0.3rem 0;'>• {s}</li>", unsafe_allow_html=True)
                    
                    st.markdown("</ul></div>", unsafe_allow_html=True)
                
                with col_s2:
                    st.markdown("""
                        <div class="glass-card" style="padding: 1rem; background: rgba(239, 68, 68, 0.1); border-color: rgba(239, 68, 68, 0.2);">
                            <h5 style="color: #ef4444; margin-bottom: 0.5rem;">⚠️ {}</h5>
                            <ul style="color: #a0aec0; list-style: none; padding: 0;">
                    """.format(T["weaknesses"]), unsafe_allow_html=True)
                    
                    for w in evaluation.get("weaknesses", []):
                        st.markdown(f"<li style='padding: 0.3rem 0;'>• {w}</li>", unsafe_allow_html=True)
                    
                    st.markdown("</ul></div>", unsafe_allow_html=True)
                
                # Improved answer
                st.markdown("""
                    <div class="glass-card" style="padding: 1rem; margin-top: 1rem; background: rgba(102, 126, 234, 0.05);">
                        <h5 style="color: #667eea; margin-bottom: 0.5rem;">💡 {}</h5>
                        <p style="color: #cbd5e0;">{}</p>
                    </div>
                """.format(T["improved_answer"], evaluation.get("improved_answer", "")), unsafe_allow_html=True)
            
            # Check if interview is finished
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

# ============================================
# STAGE 3: REPORT
# ============================================
elif st.session_state.stage == "report":
    # Generate report if not exists
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
    
    # Header
    st.markdown("""
        <div style="text-align: center; margin-bottom: 2rem;">
            <h1 style="font-size: 2.5rem;">{}</h1>
            <p style="color: #a0aec0; font-size: 1.1rem;">{} • {} • {}</p>
        </div>
    """.format(
        T["final_report"],
        report['candidate_name'],
        report['role'],
        report['level']
    ), unsafe_allow_html=True)
    
    # Overall Score with circular gauge
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col2:
        overall_score = report.get('overall_score', 0)
        percentage = (overall_score / 10) * 100
        
        st.markdown(f"""
            <div style="text-align: center;">
                <div class="progress-circle" style="--progress: {percentage}%;">
                    <div class="progress-circle-inner">
                        <div style="font-size: 2.5rem; font-weight: 700; color: white;">{overall_score}</div>
                        <div style="color: #a0aec0; font-size: 0.8rem;">/ 10</div>
                    </div>
                </div>
                <h4 style="margin-top: 1rem;">{T['overall_score']}</h4>
            </div>
        """, unsafe_allow_html=True)
    
    # Score cards
    st.markdown("<div style='margin: 2rem 0;'>", unsafe_allow_html=True)
    cols = st.columns(4)
    metrics = [
        (T["technical"], report['scores']['technical_accuracy'], "#667eea"),
        (T["communication"], report['scores']['communication_skills'], "#48bb78"),
        (T["confidence"], report['scores']['confidence'], "#ed8936"),
        (T["problem_solving"], report['scores'].get('problem_solving', 7), "#9f7aea")
    ]
    
    for idx, (label, value, color) in enumerate(metrics):
        with cols[idx]:
            st.markdown(render_metric_card(label, value, 10, color), unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Hiring Recommendation
    st.markdown(f"""
        <div class="glass-card" style="text-align: center; margin: 1rem 0; background: rgba(102, 126, 234, 0.05);">
            <h3 style="margin-bottom: 0.5rem;">{T['hiring_rec']}</h3>
            <div style="font-size: 1.5rem; font-weight: 700; color: #667eea;">{report.get('hiring_recommendation', 'N/A')}</div>
        </div>
    """, unsafe_allow_html=True)
    
    # Two column layout for strengths/weaknesses
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
            <div class="glass-card" style="background: rgba(72, 187, 120, 0.05); border-color: rgba(72, 187, 120, 0.2);">
                <h4 style="color: #48bb78; margin-bottom: 1rem;">✅ {}</h4>
        """.format(T["top_strengths"]), unsafe_allow_html=True)
        
        for s in report.get("top_strengths", []):
            st.markdown(f"<div style='padding: 0.5rem; border-bottom: 1px solid rgba(255,255,255,0.05);'>• {s}</div>", unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
            <div class="glass-card" style="background: rgba(239, 68, 68, 0.05); border-color: rgba(239, 68, 68, 0.2);">
                <h4 style="color: #ef4444; margin-bottom: 1rem;">⚠️ {}</h4>
        """.format(T["top_weaknesses"]), unsafe_allow_html=True)
        
        for w in report.get("top_weaknesses", []):
            st.markdown(f"<div style='padding: 0.5rem; border-bottom: 1px solid rgba(255,255,255,0.05);'>• {w}</div>", unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Summary
    st.markdown("""
        <div class="glass-card" style="margin: 1rem 0;">
            <h4 style="margin-bottom: 1rem;">{}</h4>
            <p style="color: #cbd5e0; line-height: 1.8;">{}</p>
        </div>
    """.format(T["summary"], report.get("summary", "")), unsafe_allow_html=True)
    
    # Suggestions
    st.markdown("""
        <div class="glass-card" style="margin: 1rem 0; background: rgba(102, 126, 234, 0.03);">
            <h4 style="color: #667eea; margin-bottom: 1rem;">💡 {}</h4>
    """.format(T["suggestions"]), unsafe_allow_html=True)
    
    for imp in report.get("suggested_improvements", []):
        st.markdown(f"<div style='padding: 0.5rem; border-bottom: 1px solid rgba(255,255,255,0.05);'>• {imp}</div>", unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # New Interview button
    st.markdown("<div style='text-align: center; margin-top: 2rem;'>", unsafe_allow_html=True)
    if st.button(T["new_interview"], use_container_width=False, type="primary"):
        for key in list(st.session_state.keys()):
            if key not in ["lang", "lang_selector"]:
                del st.session_state[key]
        st.session_state.stage = "landing"
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)