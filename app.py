import os
import json
import re
import requests
import streamlit as st


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="StudyFinder AI",
    page_icon="🎓",
    layout="wide"
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    .main {
        background-color: #f8fafc;
    }

    .hero {
        padding: 35px 20px;
        border-radius: 20px;
        background: linear-gradient(135deg, #0f172a, #1e3a8a);
        color: white;
        text-align: center;
        margin-bottom: 30px;
    }

    .hero h1 {
        font-size: 42px;
        margin-bottom: 10px;
    }

    .hero p {
        font-size: 18px;
        opacity: 0.9;
    }

    .resource-card {
        padding: 20px;
        border-radius: 15px;
        background-color: white;
        border: 1px solid #e2e8f0;
        margin-bottom: 15px;
        box-shadow: 0px 4px 12px rgba(0,0,0,0.05);
    }

    .resource-card h3 {
        margin-top: 0;
    }

    .badge {
        display: inline-block;
        padding: 5px 10px;
        border-radius: 20px;
        background-color: #dbeafe;
        color: #1e40af;
        font-size: 13px;
        margin-bottom: 8px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# API CONFIGURATION
# ============================================================

def get_api_key():
    """
    Get API key from Streamlit secrets first,
    then environment variables.
    """

    try:
        if "MODEL_API_KEY" in st.secrets:
            return st.secrets["MODEL_API_KEY"]
    except Exception:
        pass

    return os.getenv("MODEL_API_KEY")


def get_api_url():
    """
    OpenAI-compatible endpoint.

    Replace this with the endpoint supplied by
    your gpt-oss-120b hosting provider.
    """

    try:
        if "MODEL_API_URL" in st.secrets:
            return st.secrets["MODEL_API_URL"]
    except Exception:
        pass

    return os.getenv(
        "MODEL_API_URL",
        "https://api.example.com/v1/chat/completions"
    )


MODEL_NAME = "gpt-oss-120b"


# ============================================================
# CALL MODEL
# ============================================================

def call_model(prompt, temperature=0.3):

    api_key = get_api_key()
    api_url = get_api_url()

    if not api_key:
        return None, (
            "API key is missing. Add MODEL_API_KEY to your "
            "Streamlit Secrets."
        )

    if "example.com" in api_url:
        return None, (
            "MODEL_API_URL is not configured. Add the real "
            "OpenAI-compatible endpoint for your gpt-oss-120b provider."
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
                    "You are StudyFinder AI, an educational research "
                    "assistant. Give accurate, useful and student-friendly "
                    "answers. Never invent URLs."
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": temperature
    }

    try:

        response = requests.post(
            api_url,
            headers=headers,
            json=payload,
            timeout=90
        )

        if response.status_code != 200:

            try:
                error_data = response.json()
                error_message = error_data.get(
                    "error",
                    response.text
                )
            except Exception:
                error_message = response.text

            return None, (
                f"Model API error ({response.status_code}): "
                f"{error_message}"
            )

        data = response.json()

        answer = data["choices"][0]["message"]["content"]

        return answer, None

    except requests.exceptions.Timeout:

        return None, (
            "The AI server took too long to respond. "
            "Please try again."
        )

    except requests.exceptions.RequestException as e:

        return None, f"Connection error: {str(e)}"

    except Exception as e:

        return None, f"Unexpected error: {str(e)}"


# ============================================================
# STUDY RESOURCE GENERATOR
# ============================================================

def generate_resources(topic, level, resource_count):

    prompt = f"""
Create a study-resource guide for this topic:

TOPIC:
{topic}

STUDENT LEVEL:
{level}

The student wants approximately {resource_count} useful resources.

Return the answer in Markdown.

Organize it into:

# 📚 Study Guide

## 1. Topic Overview
Explain the topic in simple language.

## 2. Recommended Learning Path
Give 4-6 steps in the order the student should learn them.

## 3. 🎥 Videos
Give useful YouTube search links rather than inventing
specific video URLs.

For each video recommendation provide:
- Title/topic
- What the student will learn
- YouTube search link

Use this format:

[Search YouTube](https://www.youtube.com/results?search_query=...)

## 4. 🌐 Websites
Recommend useful educational websites.

For each:
- Website name
- Why it is useful
- Official URL

Only provide URLs you are confident about.

## 5. 📖 Courses / Articles
Recommend useful courses, tutorials or articles.

## 6. 🧠 Practice
Give 3 practical exercises.

## 7. ⭐ Best Starting Resource
Choose the single best starting point for this student.

IMPORTANT:
- Do not invent URLs.
- Prefer reputable educational sources.
- Keep the explanation practical.
- Do not overwhelm the student.
"""

    return call_model(prompt)


# ============================================================
# AI TUTOR
# ============================================================

def ask_tutor(topic, question):

    prompt = f"""
You are an AI tutor.

The student's topic is:

{topic}

Student question:

{question}

Answer like a helpful university tutor.

Requirements:
- Explain step by step.
- Use simple English.
- Give an example where useful.
- Correct misconceptions.
- Do not make the answer unnecessarily long.
"""

    return call_model(prompt, temperature=0.4)


# ============================================================
# QUIZ GENERATOR
# ============================================================

def generate_quiz(topic):

    prompt = f"""
Create a short quiz about:

{topic}

Create exactly 5 multiple-choice questions.

For every question provide:

Question:
A)
B)
C)
D)

Correct Answer:
Explanation:

Keep the difficulty suitable for a student learning this topic.
"""

    return call_model(prompt, temperature=0.5)


# ============================================================
# HERO
# ============================================================

st.markdown(
    """
    <div class="hero">
        <h1>🎓 StudyFinder AI</h1>
        <p>
            Describe what you want to learn and discover
            videos, websites, courses and practice resources.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.header("⚙️ Study Settings")

    student_level = st.selectbox(
        "Student Level",
        [
            "Beginner",
            "Intermediate",
            "Advanced",
            "University Student"
        ]
    )

    resource_count = st.slider(
        "Number of resources",
        min_value=3,
        max_value=10,
        value=5
    )

    st.divider()

    st.markdown(
        """
        ### 💡 How it works

        **1.** Enter a topic

        **2.** AI analyzes it

        **3.** Study resources are generated

        **4.** Ask the AI tutor

        **5.** Test yourself with a quiz
        """
    )


# ============================================================
# TOPIC INPUT
# ============================================================

st.subheader("🔎 What do you want to learn?")

topic = st.text_input(
    "Enter a course, subject or topic",
    placeholder="Example: Data Structures and Algorithms"
)


search_clicked = st.button(
    "🚀 Find Study Resources",
    use_container_width=True,
    type="primary"
)


# ============================================================
# SEARCH
# ============================================================

if search_clicked:

    if not topic.strip():

        st.warning("Please enter a topic first.")

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

            st.success("Study resources generated!")

            st.markdown(result)


# ============================================================
# AI TUTOR
# ============================================================

if "topic" in st.session_state:

    st.divider()

    st.header("🤖 AI Tutor")

    tutor_question = st.text_area(
        "Ask anything about your topic",
        placeholder=(
            "Example: Explain linked lists with a real-world example."
        )
    )

    if st.button(
        "Ask AI Tutor",
        use_container_width=True
    ):

        if not tutor_question.strip():

            st.warning("Please enter a question.")

        else:

            with st.spinner("AI Tutor is thinking..."):

                answer, error = ask_tutor(
                    st.session_state["topic"],
                    tutor_question
                )

            if error:

                st.error(error)

            else:

                st.markdown("### 💬 Tutor Answer")

                st.markdown(answer)


# ============================================================
# QUIZ
# ============================================================

if "topic" in st.session_state:

    st.divider()

    st.header("🧠 Test Your Knowledge")

    if st.button(
        "Generate 5-Question Quiz",
        use_container_width=True
    ):

        with st.spinner("Creating your quiz..."):

            quiz, error = generate_quiz(
                st.session_state["topic"]
            )

        if error:

            st.error(error)

        else:

            st.markdown(quiz)


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "🎓 StudyFinder AI • Powered by Streamlit + gpt-oss-120b"
)
