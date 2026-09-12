import os
import requests
import streamlit as st


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="StudyFinder AI",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# GROQ CONFIGURATION
# ============================================================

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL_NAME = "openai/gpt-oss-120b"


# ============================================================
# GET API KEY
# ============================================================

def get_groq_api_key():

    try:
        if "GROQ_API_KEY" in st.secrets:
            return st.secrets["GROQ_API_KEY"]
    except Exception:
        pass

    return os.getenv("GROQ_API_KEY")


# ============================================================
# GLOBAL CSS
# ============================================================

st.markdown(
    """
    <style>

    /* Main background */
    .stApp {
        background: #f7f9fc;
    }

    /* Remove default top spacing */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1200px;
    }

    /* Header */
    .top-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 10px 0 25px 0;
    }

    .brand {
        font-size: 27px;
        font-weight: 800;
        color: #111827;
    }

    .brand-icon {
        background: #2563eb;
        color: white;
        padding: 8px 11px;
        border-radius: 10px;
        margin-right: 8px;
    }

    .tagline {
        color: #6b7280;
        font-size: 14px;
    }

    /* Hero */
    .hero {
        background: linear-gradient(
            135deg,
            #1d4ed8 0%,
            #2563eb 50%,
            #4f46e5 100%
        );
        padding: 55px 35px;
        border-radius: 24px;
        text-align: center;
        color: white;
        margin-bottom: 30px;
        box-shadow: 0 15px 35px rgba(37, 99, 235, 0.20);
    }

    .hero-title {
        font-size: 46px;
        font-weight: 800;
        margin-bottom: 12px;
    }

    .hero-text {
        font-size: 18px;
        opacity: 0.95;
        max-width: 700px;
        margin: auto;
        line-height: 1.6;
    }

    /* Search box */
    .search-title {
        font-size: 25px;
        font-weight: 750;
        color: #111827;
        margin-bottom: 5px;
    }

    .search-subtitle {
        color: #6b7280;
        margin-bottom: 15px;
    }

    /* Feature cards */
    .feature-card {
        background: white;
        padding: 22px;
        border-radius: 17px;
        border: 1px solid #e5e7eb;
        height: 150px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.03);
    }

    .feature-icon {
        font-size: 30px;
        margin-bottom: 8px;
    }

    .feature-title {
        font-size: 17px;
        font-weight: 700;
        color: #111827;
    }

    .feature-text {
        font-size: 13px;
        color: #6b7280;
        margin-top: 5px;
    }

    /* Result container */
    .result-header {
        background: white;
        border: 1px solid #e5e7eb;
        padding: 20px;
        border-radius: 16px;
        margin-top: 30px;
    }

    /* Footer */
    .footer {
        text-align: center;
        color: #9ca3af;
        padding: 25px;
        font-size: 13px;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: white;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# TOP HEADER
# ============================================================

st.markdown(
    """
    <div class="top-header">

        <div>
            <span class="brand-icon">🎓</span>
            <span class="brand">StudyFinder AI</span>
        </div>

        <div class="tagline">
            Your AI-powered learning companion
        </div>

    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# HERO SECTION
# ============================================================

st.markdown(
    """
    <div class="hero">

        <div class="hero-title">
            Learn Anything. Smarter. 🚀
        </div>

        <div class="hero-text">
            Enter any subject or topic and let AI create
            a personalized study guide with videos,
            websites, courses, tutorials and practice.
        </div>

    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown("## ⚙️ Study Settings")

    st.markdown(
        "Customize your learning experience."
    )

    student_level = st.selectbox(
        "📚 Your Level",
        [
            "Beginner",
            "Intermediate",
            "Advanced",
            "University Student"
        ]
    )

    resource_count = st.slider(
        "🔗 Number of Resources",
        min_value=3,
        max_value=10,
        value=5
    )

    st.divider()

    st.markdown("### ✨ Features")

    st.markdown(
        """
        🎥 **Video Resources**

        🌐 **Educational Websites**

        📖 **Courses & Tutorials**

        🤖 **AI Tutor**

        🧠 **Practice Quiz**
        """
    )

    st.divider()

    st.caption(
        "Powered by Groq"
    )

    st.caption(
        "Model: gpt-oss-120b"
    )


# ============================================================
# SEARCH SECTION
# ============================================================

st.markdown(
    '<div class="search-title">🔎 What do you want to learn?</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="search-subtitle">'
    'Enter a course, subject, programming language, '
    'technology or any topic.'
    '</div>',
    unsafe_allow_html=True
)


topic = st.text_input(
    "Topic",
    placeholder=(
        "Example: Python Data Structures, "
        "Machine Learning, Cybersecurity..."
    ),
    label_visibility="collapsed"
)


search_clicked = st.button(
    "🚀 Find My Study Resources",
    type="primary",
    use_container_width=True
)


# ============================================================
# GROQ API
# ============================================================

def call_groq(
    prompt,
    temperature=0.3,
    max_tokens=3500
):

    api_key = get_groq_api_key()

    if not api_key:

        return None, (
            "GROQ_API_KEY is missing. "
            "Add it to Streamlit Secrets."
        )

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": MODEL_NAME,

        "messages": [
            {
                "role": "system",
                "content": (
                    "You are StudyFinder AI, an expert "
                    "educational assistant. "
                    "Help students find useful learning "
                    "resources and understand academic topics. "
                    "Never invent URLs."
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ],

        "temperature": temperature,
        "max_tokens": max_tokens
    }

    try:

        response = requests.post(
            GROQ_API_URL,
            headers=headers,
            json=payload,
            timeout=90
        )

        if response.status_code == 429:

            return None, (
                "Groq rate limit reached. "
                "Please wait a few seconds and try again."
            )

        if response.status_code in [401, 403]:

            return None, (
                "Invalid Groq API key. "
                "Please check your Streamlit Secrets."
            )

        if response.status_code != 200:

            try:

                error_data = response.json()

                message = (
                    error_data
                    .get("error", {})
                    .get("message", response.text)
                )

            except Exception:

                message = response.text

            return None, (
                f"Groq API Error ({response.status_code}): "
                f"{message}"
            )

        data = response.json()

        answer = data["choices"][0]["message"]["content"]

        return answer, None

    except requests.exceptions.Timeout:

        return None, (
            "The AI server took too long to respond."
        )

    except requests.exceptions.ConnectionError:

        return None, (
            "Could not connect to Groq."
        )

    except Exception as e:

        return None, str(e)


# ============================================================
# RESOURCE GENERATOR
# ============================================================

def generate_resources(
    topic,
    level,
    resource_count
):

    prompt = f"""
Create a personalized study guide for:

Topic: {topic}

Student Level: {level}

Resources requested: {resource_count}

Return a clean Markdown response.

Use exactly these sections:

# 📚 Study Guide

## 🎯 Topic Overview

Explain the topic simply.

## 🛣️ Learning Roadmap

Give 5 logical learning steps.

## 🎥 Video Resources

Give {resource_count} useful video recommendations.

DO NOT invent YouTube video URLs.

Instead use YouTube search URLs:

https://www.youtube.com/results?search_query=

For example:

[Search YouTube](https://www.youtube.com/results?search_query=Python+data+structures)

## 🌐 Websites

Recommend useful educational websites.

Give the website name, purpose and official URL.

Use reputable resources such as:

- MDN
- W3Schools
- freeCodeCamp
- Khan Academy
- GeeksforGeeks
- Coursera
- edX
- MIT OpenCourseWare
- Official documentation

## 📖 Courses & Tutorials

Recommend useful courses or tutorials.

## 🧪 Practice

Give 3 exercises.

## ⭐ Best Starting Point

Tell the student what they should study first.

IMPORTANT:
Do not invent URLs.
Use simple English.
Make the recommendations useful for students.
"""

    return call_groq(
        prompt,
        temperature=0.3,
        max_tokens=3500
    )


# ============================================================
# SEARCH ACTION
# ============================================================

if search_clicked:

    if not topic.strip():

        st.warning(
            "⚠️ Please enter a topic first."
        )

    else:

        with st.spinner(
            "🤖 AI is creating your personalized study guide..."
        ):

            result, error = generate_resources(
                topic.strip(),
                student_level,
                resource_count
            )

        if error:

            st.error(error)

        else:

            st.session_state["topic"] = topic.strip()
            st.session_state["resources"] = result

            st.success(
                "🎉 Your study resources are ready!"
            )


# ============================================================
# FEATURE CARDS
# ============================================================

if "resources" not in st.session_state:

    st.markdown("### 🌟 Everything You Need to Learn")

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.markdown(
            """
            <div class="feature-card">

                <div class="feature-icon">🎥</div>

                <div class="feature-title">
                    Video Learning
                </div>

                <div class="feature-text">
                    Discover useful videos
                    for your topic.
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:

        st.markdown(
            """
            <div class="feature-card">

                <div class="feature-icon">🌐</div>

                <div class="feature-title">
                    Best Websites
                </div>

                <div class="feature-text">
                    Find trusted educational
                    websites and documentation.
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )

    with col3:

        st.markdown(
            """
            <div class="feature-card">

                <div class="feature-icon">📖</div>

                <div class="feature-title">
                    Courses
                </div>

                <div class="feature-text">
                    Discover courses and
                    tutorials to learn faster.
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )

    with col4:

        st.markdown(
            """
            <div class="feature-card">

                <div class="feature-icon">🤖</div>

                <div class="feature-title">
                    AI Tutor
                </div>

                <div class="feature-text">
                    Ask questions and get
                    personalized explanations.
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )


# ============================================================
# RESULTS
# ============================================================

if "resources" in st.session_state:

    st.markdown(
        """
        <div class="result-header">

            <h2>📚 Your Personalized Study Guide</h2>

            <p>
                AI-generated resources based on your topic.
            </p>

        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        st.session_state["resources"]
    )


# ============================================================
# AI TUTOR
# ============================================================

if "topic" in st.session_state:

    st.divider()

    st.header("🤖 AI Tutor")

    st.write(
        f"Ask anything about **{st.session_state['topic']}**."
    )

    question = st.text_area(
        "Your question",
        placeholder=(
            "Example: Explain this topic with a "
            "real-world example."
        ),
        label_visibility="collapsed"
    )

    if st.button(
        "💬 Ask AI Tutor",
        use_container_width=True
    ):

        if not question.strip():

            st.warning(
                "Please enter your question."
            )

        else:

            tutor_prompt = f"""
You are an expert tutor.

Topic:
{st.session_state['topic']}

Student question:
{question}

Explain the answer clearly.

Use:
- Simple English
- Step-by-step explanation
- Examples
- Practical explanation
"""

            with st.spinner(
                "🤖 AI Tutor is thinking..."
            ):

                answer, error = call_groq(
                    tutor_prompt,
                    temperature=0.4,
                    max_tokens=2000
                )

            if error:

                st.error(error)

            else:

                st.markdown("### 💡 Tutor Answer")

                st.markdown(answer)


# ============================================================
# QUIZ
# ============================================================

if "topic" in st.session_state:

    st.divider()

    st.header("🧠 Test Your Knowledge")

    if st.button(
        "📝 Generate 5-Question Quiz",
        use_container_width=True
    ):

        quiz_prompt = f"""
Create a 5-question multiple-choice quiz about:

{st.session_state['topic']}

For every question provide:

Question

A. Option
B. Option
C. Option
D. Option

Correct Answer

Explanation

Make it suitable for a student.
"""

        with st.spinner(
            "🧠 Creating your quiz..."
        ):

            quiz, error = call_groq(
                quiz_prompt,
                temperature=0.5,
                max_tokens=2500
            )

        if error:

            st.error(error)

        else:

            st.markdown("### 📝 Your Quiz")

            st.markdown(quiz)


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
    <div class="footer">

        🎓 <b>StudyFinder AI</b>

        <br>

        Learn smarter • Discover better resources •
        Powered by gpt-oss-120b

    </div>
    """,
    unsafe_allow_html=True
)
