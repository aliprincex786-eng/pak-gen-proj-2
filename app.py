import os
import streamlit as st
from google import genai


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="StudyFinder AI",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown(
    """
    <style>

    .stApp {
        background: linear-gradient(
            135deg,
            #f8fafc 0%,
            #eef2ff 100%
        );
    }

    .hero {
        text-align: center;
        padding: 45px 20px 30px 20px;
    }

    .hero h1 {
        font-size: 52px;
        font-weight: 800;
        color: #111827;
        margin-bottom: 10px;
    }

    .hero h1 span {
        color: #6366f1;
    }

    .hero p {
        font-size: 19px;
        color: #6b7280;
        max-width: 760px;
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
    """,
    unsafe_allow_html=True
)


# =========================================================
# GEMINI CLIENT
# =========================================================

def get_gemini_client():

    api_key = None

    # Streamlit Cloud Secrets
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
    except Exception:
        pass

    # Local environment variable
    if not api_key:
        api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        return None

    return genai.Client(api_key=api_key)


# =========================================================
# GEMINI STUDY RESOURCE GENERATOR
# =========================================================

def generate_study_resources(topic, level, resource_count):

    client = get_gemini_client()

    if client is None:
        raise ValueError(
            "Gemini API key is missing. "
            "Please add GEMINI_API_KEY to Streamlit Secrets."
        )

    prompt = f"""
You are an expert educational resource curator.

A student wants to learn:

TOPIC:
{topic}

STUDENT LEVEL:
{level}

Your job is to create a useful learning guide for this topic.

Provide:

1. A short introduction to the topic.
2. A beginner-friendly learning roadmap.
3. Important concepts the student should learn.
4. Relevant educational videos.
5. Relevant educational websites.
6. Articles and documentation.
7. Free learning resources whenever possible.
8. A recommended learning order.

IMPORTANT RULES:

- Search the web for real resources.
- DO NOT invent URLs.
- Only recommend resources that actually exist.
- Prefer reputable educational websites.
- Prefer official documentation when available.
- Prefer high-quality educational videos.
- Resources must be directly related to the requested topic.
- Explain why each recommended resource is useful.
- Keep the explanation easy to understand.
- Do not recommend pirated or illegal resources.

Number of resources requested:
{resource_count}

Return the final answer using clean Markdown.

Organize the answer using headings such as:

## 📚 Topic Overview

## 🗺️ Learning Roadmap

## 🎥 Video Resources

## 🌐 Websites & Articles

## 📖 Documentation

## ⭐ Recommended Learning Order
"""

    # =====================================================
    # NEW GEMINI INTERACTIONS API
    # =====================================================

    interaction = client.interactions.create(
        model="gemini-3.6-flash",
        input=prompt,
        tools=[
            {
                "type": "google_search"
            }
        ]
    )

    return interaction.output_text


# =========================================================
# AI TUTOR
# =========================================================

def ask_tutor(topic, question):

    client = get_gemini_client()

    if client is None:
        raise ValueError(
            "Gemini API key is missing."
        )

    prompt = f"""
You are an expert AI tutor.

The student is learning:

{topic}

The student's question is:

{question}

Explain the answer in simple language.

Requirements:

- Start with a simple explanation.
- Give an example when useful.
- Explain difficult terms.
- Use bullet points when appropriate.
- Correct misconceptions politely.
- Keep the answer educational.
- Use Markdown formatting.
"""

    interaction = client.interactions.create(
        model="gemini-3.6-flash",
        input=prompt
    )

    return interaction.output_text


# =========================================================
# QUIZ GENERATOR
# =========================================================

def generate_quiz(topic):

    client = get_gemini_client()

    if client is None:
        raise ValueError(
            "Gemini API key is missing."
        )

    prompt = f"""
Create a 5-question multiple-choice quiz about:

{topic}

Requirements:

- Create exactly 5 questions.
- Each question must have 4 options.
- Only one option should be correct.
- Include the correct answer.
- Include a short explanation.
- Questions should test understanding rather than memorization.
- Keep the difficulty appropriate for a beginner.
- Return the quiz using Markdown.
"""

    interaction = client.interactions.create(
        model="gemini-3.6-flash",
        input=prompt
    )

    return interaction.output_text


# =========================================================
# HERO SECTION
# =========================================================

st.markdown(
    """
    <div class="hero">

        <h1>
            Study<span>Finder</span> AI 🎓
        </h1>

        <p>
            Enter any course or topic and discover
            relevant videos, websites, documentation,
            articles and learning resources with AI.
        </p>

    </div>
    """,
    unsafe_allow_html=True
)


# =========================================================
# SEARCH BOX
# =========================================================

st.markdown(
    '<div class="topic-box">',
    unsafe_allow_html=True
)

topic = st.text_input(
    "🔎 What do you want to learn?",
    placeholder="Example: Python for Data Science"
)

col1, col2, col3 = st.columns(3)


with col1:

    level = st.selectbox(
        "🎓 Student Level",
        [
            "Beginner",
            "Intermediate",
            "Advanced"
        ]
    )


with col2:

    resource_count = st.slider(
        "📚 Number of Resources",
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


st.markdown(
    "</div>",
    unsafe_allow_html=True
)


# =========================================================
# SESSION STATE
# =========================================================

if "results" not in st.session_state:
    st.session_state.results = None

if "topic" not in st.session_state:
    st.session_state.topic = ""


# =========================================================
# SEARCH / GENERATE RESOURCES
# =========================================================

if search_button:

    if not topic.strip():

        st.warning(
            "⚠️ Please enter a course or topic first."
        )

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
                    f"❌ Something went wrong:\n\n{str(e)}"
                )


# =========================================================
# DISPLAY SEARCH RESULTS
# =========================================================

if st.session_state.results:

    st.markdown(
        '<div class="section-title">'
        '📚 Learning Resources'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        st.session_state.results
    )


    # =====================================================
    # AI TUTOR
    # =====================================================

    st.divider()

    st.markdown(
        '<div class="section-title">'
        '🤖 AI Tutor'
        '</div>',
        unsafe_allow_html=True
    )

    st.write(
        "Didn't understand something? Ask the AI tutor."
    )

    tutor_question = st.text_input(
        "💬 Ask your question",
        placeholder=(
            "Example: Explain arrays like I am a beginner."
        )
    )

    if st.button(
        "💡 Ask AI Tutor",
        type="secondary"
    ):

        if not tutor_question.strip():

            st.warning(
                "Please enter a question."
            )

        else:

            with st.spinner(
                "🤖 AI Tutor is thinking..."
            ):

                try:

                    answer = ask_tutor(
                        st.session_state.topic,
                        tutor_question
                    )

                    st.markdown(
                        "### 🤖 AI Tutor Answer"
                    )

                    st.markdown(answer)

                except Exception as e:

                    st.error(
                        f"❌ {str(e)}"
                    )


    # =====================================================
    # QUIZ
    # =====================================================

    st.divider()

    st.markdown(
        '<div class="section-title">'
        '🧠 Test Your Knowledge'
        '</div>',
        unsafe_allow_html=True
    )

    st.write(
        "Generate a quick quiz to test your understanding."
    )

    if st.button(
        "🎯 Generate Quiz"
    ):

        with st.spinner(
            "🧠 Creating your quiz..."
        ):

            try:

                quiz = generate_quiz(
                    st.session_state.topic
                )

                st.markdown(
                    "### 📝 Your Quiz"
                )

                st.markdown(quiz)

            except Exception as e:

                st.error(
                    f"❌ {str(e)}"
                )


# =========================================================
# FOOTER
# =========================================================

st.markdown(
    """
    <div class="footer">

        <p>
            🎓 <strong>StudyFinder AI</strong>
        </p>

        <p>
            Learn smarter. Discover better resources.
        </p>

        <p>
            Powered by Gemini AI
        </p>

    </div>
    """,
    unsafe_allow_html=True
)
