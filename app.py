import os
import re
import json
import html
import streamlit as st
from google import genai

# ---------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------

st.set_page_config(
    page_title="StudyFinder AI",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ---------------------------------------------------------
# CUSTOM CSS
# ---------------------------------------------------------

st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #f8fafc 0%, #eef2ff 100%);
    }

    .hero {
        text-align: center;
        padding: 45px 20px 25px 20px;
    }

    .hero h1 {
        font-size: 52px;
        font-weight: 800;
        margin-bottom: 10px;
        color: #111827;
    }

    .hero h1 span {
        color: #6366f1;
    }

    .hero p {
        font-size: 19px;
        color: #6b7280;
        max-width: 750px;
        margin: auto;
    }

    .topic-box {
        background: white;
        border-radius: 18px;
        padding: 25px;
        box-shadow: 0 8px 30px rgba(0,0,0,0.06);
        margin-bottom: 25px;
    }

    .section-title {
        font-size: 28px;
        font-weight: 750;
        color: #111827;
        margin-top: 25px;
        margin-bottom: 15px;
    }

    .resource-card {
        background: white;
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 15px;
        border: 1px solid #e5e7eb;
        box-shadow: 0 5px 18px rgba(0,0,0,0.04);
    }

    .resource-card h3 {
        margin-top: 0;
        color: #111827;
    }

    .resource-type {
        display: inline-block;
        background: #eef2ff;
        color: #4f46e5;
        padding: 5px 10px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 700;
        margin-bottom: 8px;
    }

    .roadmap-card {
        background: white;
        padding: 18px;
        border-radius: 14px;
        border-left: 5px solid #6366f1;
        margin-bottom: 12px;
    }

    .footer {
        text-align: center;
        color: #6b7280;
        padding: 40px 10px 20px 10px;
    }

    div.stButton > button {
        border-radius: 10px;
        font-weight: 700;
    }
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------
# GEMINI CLIENT
# ---------------------------------------------------------

def get_gemini_client():
    """
    Supports:
    1. Streamlit Cloud secrets
    2. Local environment variable
    """

    api_key = None

    try:
        api_key = st.secrets["GEMINI_API_KEY"]
    except Exception:
        api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        return None

    return genai.Client(api_key=api_key)


# ---------------------------------------------------------
# GEMINI CALL
# ---------------------------------------------------------

def generate_study_resources(topic, level, resource_count):
    client = get_gemini_client()

    if client is None:
        raise ValueError(
            "Gemini API key is missing. Add GEMINI_API_KEY to "
            "Streamlit Secrets or your environment variables."
        )

    prompt = f"""
You are an expert educational resource curator.

The student wants to learn:

TOPIC:
{topic}

STUDENT LEVEL:
{level}

Find useful, legitimate, educational resources for this topic.

Return a structured response containing:

1. A short explanation of the topic.
2. A beginner-friendly learning roadmap.
3. Recommended educational resources.
4. YouTube/video resources.
5. Websites/articles/documentation.
6. Free resources whenever possible.
7. A suggested learning order.

IMPORTANT:
- Use real web resources.
- Do not invent URLs.
- Prefer reputable educational sources.
- Prefer official documentation, universities,
  recognized educational websites, and high-quality
  educational YouTube channels.
- Explain why each resource is useful.
- Keep recommendations relevant to the exact topic.
- Do not recommend unsafe, illegal, pirated, or misleading content.

Return the final answer in clear Markdown.

Maximum resources:
{resource_count}
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config={
            "tools": [{"google_search": {}}]
        }
    )

    return response.text


# ---------------------------------------------------------
# AI TUTOR
# ---------------------------------------------------------

def ask_tutor(topic, question):
    client = get_gemini_client()

    if client is None:
        raise ValueError(
            "Gemini API key is missing. Configure GEMINI_API_KEY first."
        )

    prompt = f"""
You are an AI tutor.

The student is studying:
{topic}

Student question:
{question}

Explain the answer in simple language.

Requirements:
- Start with a simple explanation.
- Give an example when useful.
- Avoid unnecessary complexity.
- If the question contains a misconception,
  politely correct it.
- Use Markdown formatting.
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    return response.text


# ---------------------------------------------------------
# QUIZ GENERATOR
# ---------------------------------------------------------

def generate_quiz(topic):
    client = get_gemini_client()

    if client is None:
        raise ValueError("Gemini API key is missing.")

    prompt = f"""
Create a 5-question multiple-choice quiz about:

{topic}

Rules:
- Questions should test understanding.
- 4 options per question.
- Exactly one correct answer.
- Include the correct answer after each question.
- Include a short explanation.

Return Markdown.
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    return response.text


# ---------------------------------------------------------
# HEADER
# ---------------------------------------------------------

st.markdown("""
<div class="hero">
    <h1>Study<span>Finder</span> AI 🎓</h1>
    <p>
        Enter any course or topic and let AI discover
        the best videos, websites, documentation and
        learning resources for you.
    </p>
</div>
""", unsafe_allow_html=True)


# ---------------------------------------------------------
# INPUT
# ---------------------------------------------------------

st.markdown('<div class="topic-box">', unsafe_allow_html=True)

topic = st.text_input(
    "🔎 What do you want to learn?",
    placeholder="Example: Python for Data Science",
    label_visibility="visible"
)

col1, col2, col3 = st.columns(3)

with col1:
    level = st.selectbox(
        "Student Level",
        [
            "Beginner",
            "Intermediate",
            "Advanced"
        ]
    )

with col2:
    resource_count = st.slider(
        "Number of resources",
        min_value=5,
        max_value=15,
        value=8
    )

with col3:
    st.write("")
    st.write("")
    search_button = st.button(
        "🚀 Find Learning Resources",
        type="primary",
        use_container_width=True
    )

st.markdown("</div>", unsafe_allow_html=True)


# ---------------------------------------------------------
# SESSION STATE
# ---------------------------------------------------------

if "results" not in st.session_state:
    st.session_state.results = None

if "topic" not in st.session_state:
    st.session_state.topic = ""


# ---------------------------------------------------------
# SEARCH
# ---------------------------------------------------------

if search_button:

    if not topic.strip():
        st.warning("Please enter a course or topic first.")
    else:

        with st.spinner(
            "🤖 AI is researching learning resources..."
        ):
            try:
                result = generate_study_resources(
                    topic=topic.strip(),
                    level=level,
                    resource_count=resource_count
                )

                st.session_state.results = result
                st.session_state.topic = topic.strip()

            except Exception as e:
                st.error(
                    f"Something went wrong:\n\n{str(e)}"
                )


# ---------------------------------------------------------
# DISPLAY RESULTS
# ---------------------------------------------------------

if st.session_state.results:

    st.markdown(
        f'<div class="section-title">📚 Learning Resources for '
        f'{html.escape(st.session_state.topic)}</div>',
        unsafe_allow_html=True
    )

    st.markdown(st.session_state.results)

    st.divider()

    # -----------------------------------------------------
    # AI TUTOR
    # -----------------------------------------------------

    st.markdown(
        '<div class="section-title">🤖 AI Tutor</div>',
        unsafe_allow_html=True
    )

    tutor_question = st.text_input(
        "Ask anything about this topic:",
        placeholder="Explain this topic like I am a beginner..."
    )

    if st.button("💡 Ask AI Tutor"):

        if not tutor_question.strip():
            st.warning("Please enter a question.")
        else:

            with st.spinner("AI Tutor is thinking..."):

                try:
                    answer = ask_tutor(
                        st.session_state.topic,
                        tutor_question
                    )

                    st.markdown("### 🤖 AI Tutor Answer")
                    st.markdown(answer)

                except Exception as e:
                    st.error(str(e))

    # -----------------------------------------------------
    # QUIZ
    # -----------------------------------------------------

    st.divider()

    st.markdown(
        '<div class="section-title">🧠 Test Your Knowledge</div>',
        unsafe_allow_html=True
    )

    if st.button("🎯 Generate Quiz"):

        with st.spinner("Creating your quiz..."):

            try:
                quiz = generate_quiz(
                    st.session_state.topic
                )

                st.markdown(quiz)

            except Exception as e:
                st.error(str(e))


# ---------------------------------------------------------
# FOOTER
# ---------------------------------------------------------

st.markdown("""
<div class="footer">
    <p>🎓 StudyFinder AI</p>
    <p>
        Learn smarter. Discover better resources.
        Powered by Gemini.
    </p>
</div>
""", unsafe_allow_html=True)
