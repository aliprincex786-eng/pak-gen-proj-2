import os
import requests
import streamlit as st


# ============================================================
# PAGE CONFIGURATION
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
        padding: 40px 25px;
        border-radius: 22px;
        background: linear-gradient(
            135deg,
            #0f172a,
            #1d4ed8
        );
        color: white;
        text-align: center;
        margin-bottom: 30px;
    }

    .hero h1 {
        font-size: 44px;
        font-weight: 800;
        margin-bottom: 10px;
    }

    .hero p {
        font-size: 18px;
        opacity: 0.9;
    }

    .info-card {
        padding: 20px;
        border-radius: 16px;
        background: white;
        border: 1px solid #e2e8f0;
        margin-bottom: 15px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# GROQ CONFIGURATION
# ============================================================

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

MODEL_NAME = "openai/gpt-oss-120b"


def get_groq_api_key():
    """
    Gets the Groq API key from Streamlit Secrets
    or from an environment variable.
    """

    try:
        if "GROQ_API_KEY" in st.secrets:
            return st.secrets["GROQ_API_KEY"]
    except Exception:
        pass

    return os.getenv("GROQ_API_KEY")


# ============================================================
# GROQ API FUNCTION
# ============================================================

def call_groq(
    prompt,
    temperature=0.3,
    max_tokens=2500
):
    """
    Sends a request to Groq using the
    OpenAI-compatible Chat Completions API.
    """

    api_key = get_groq_api_key()

    if not api_key:

        return None, (
            "❌ GROQ_API_KEY is missing.\n\n"
            "Please add your Groq API key to "
            "Streamlit Secrets."
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
                    "You are StudyFinder AI, an intelligent "
                    "educational assistant. "
                    "Your job is to help students discover "
                    "useful learning resources and understand "
                    "academic topics. "
                    "Always be accurate, practical and easy "
                    "to understand. "
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

        # ----------------------------------------------------
        # RATE LIMIT
        # ----------------------------------------------------

        if response.status_code == 429:

            return None, (
                "⚠️ Groq rate limit reached.\n\n"
                "Please wait a few seconds and try again."
            )

        # ----------------------------------------------------
        # INVALID API KEY
        # ----------------------------------------------------

        if response.status_code in [401, 403]:

            return None, (
                "❌ Your Groq API key is invalid or "
                "does not have permission to use this API."
            )

        # ----------------------------------------------------
        # OTHER API ERROR
        # ----------------------------------------------------

        if response.status_code != 200:

            try:
                error_data = response.json()

                error_message = (
                    error_data
                    .get("error", {})
                    .get("message", response.text)
                )

            except Exception:

                error_message = response.text

            return None, (
                f"❌ Groq API Error "
                f"({response.status_code}):\n\n"
                f"{error_message}"
            )

        # ----------------------------------------------------
        # SUCCESS
        # ----------------------------------------------------

        data = response.json()

        answer = (
            data["choices"][0]["message"]["content"]
        )

        return answer, None

    except requests.exceptions.Timeout:

        return None, (
            "⏱️ Groq took too long to respond. "
            "Please try again."
        )

    except requests.exceptions.ConnectionError:

        return None, (
            "🌐 Could not connect to Groq. "
            "Please check your internet connection."
        )

    except requests.exceptions.RequestException as e:

        return None, (
            f"❌ Network error:\n\n{str(e)}"
        )

    except Exception as e:

        return None, (
            f"❌ Unexpected error:\n\n{str(e)}"
        )


# ============================================================
# RESOURCE GENERATOR
# ============================================================

def generate_resources(
    topic,
    level,
    resource_count
):

    prompt = f"""
Create a personalized study guide.

TOPIC:
{topic}

STUDENT LEVEL:
{level}

NUMBER OF RESOURCES:
{resource_count}

Return the answer using Markdown.

Use this exact structure:

# 📚 Study Guide

## 🎯 Topic Overview

Explain the topic in simple language.

## 🛣️ Recommended Learning Path

Create a step-by-step learning path.

## 🎥 Video Resources

Recommend useful video topics.

IMPORTANT:
Do NOT invent individual video URLs.

Instead create YouTube search links like:

https://www.youtube.com/results?search_query=YOUR+SEARCH+QUERY

For every video recommendation include:

### Video X
**Topic:** ...
**Why watch it:** ...
**YouTube Search:** ...

## 🌐 Websites

Recommend useful educational websites.

For every website provide:

**Website:** ...
**Purpose:** ...
**URL:** ...

Only provide URLs you are confident are real.

Prefer reputable educational resources such as:

- MDN
- W3Schools
- GeeksforGeeks
- freeCodeCamp
- Khan Academy
- Coursera
- edX
- MIT OpenCourseWare
- official documentation

## 📖 Courses & Tutorials

Recommend useful courses or tutorials.

## 🧪 Practice

Give 3 practical exercises.

## ⭐ Best Starting Point

Tell the student which resource they should start with and why.

IMPORTANT:
- Do not invent URLs.
- Keep the answer practical.
- Use simple English.
- Do not overwhelm the student.
"""

    return call_groq(
        prompt,
        temperature=0.3,
        max_tokens=3500
    )


# ============================================================
# AI TUTOR
# ============================================================

def ask_tutor(topic, question):

    prompt = f"""
You are an expert university tutor.

CURRENT TOPIC:
{topic}

STUDENT QUESTION:
{question}

Answer the student clearly.

Requirements:

1. Explain step-by-step.
2. Use simple English.
3. Give an example.
4. Correct misunderstandings.
5. Keep the answer focused.
6. Use code examples when the topic is programming.
7. Use Markdown headings and bullet points.
"""

    return call_groq(
        prompt,
        temperature=0.4,
        max_tokens=2000
    )


# ============================================================
# QUIZ GENERATOR
# ============================================================

def generate_quiz(topic):

    prompt = f"""
Create a quiz for a student studying:

{topic}

Create exactly 5 multiple-choice questions.

Use this format:

## Question 1

Question text

A. Option
B. Option
C. Option
D. Option

**Correct Answer:** B

**Explanation:** Explain why.

Repeat this for all 5 questions.

Make the questions educational rather than trivial.
"""

    return call_groq(
        prompt,
        temperature=0.5,
        max_tokens=2500
    )


# ============================================================
# HERO SECTION
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

        **3.** Resources are generated

        **4.** Ask the AI Tutor

        **5.** Generate a quiz
        """
    )

    st.divider()

    st.caption(
        "Powered by Groq + gpt-oss-120b"
    )


# ============================================================
# TOPIC INPUT
# ============================================================

st.subheader("🔎 What do you want to learn?")

topic = st.text_input(
    "Enter a course, subject or topic",
    placeholder=(
        "Example: Python Data Structures"
    )
)


# ============================================================
# SEARCH BUTTON
# ============================================================

if st.button(
    "🚀 Find Study Resources",
    use_container_width=True,
    type="primary"
):

    if not topic.strip():

        st.warning(
            "⚠️ Please enter a topic first."
        )

    else:

        with st.spinner(
            "🤖 gpt-oss-120b is creating "
            "your study guide..."
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
                "✅ Study resources generated!"
            )

            st.markdown(result)


# ============================================================
# DISPLAY SAVED RESOURCES
# ============================================================

if "resources" in st.session_state:

    if not st.session_state.get(
        "resources_displayed",
        False
    ):

        st.session_state[
            "resources_displayed"
        ] = True


# ============================================================
# AI TUTOR
# ============================================================

if "topic" in st.session_state:

    st.divider()

    st.header("🤖 AI Tutor")

    tutor_question = st.text_area(
        "Ask a question about your topic",
        placeholder=(
            "Example: Explain linked lists "
            "with a real-world example."
        )
    )

    if st.button(
        "💬 Ask AI Tutor",
        use_container_width=True
    ):

        if not tutor_question.strip():

            st.warning(
                "Please enter a question."
            )

        else:

            with st.spinner(
                "🤖 AI Tutor is thinking..."
            ):

                answer, error = ask_tutor(
                    st.session_state["topic"],
                    tutor_question
                )

            if error:

                st.error(error)

            else:

                st.markdown(
                    "### 💡 Tutor Answer"
                )

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

        with st.spinner(
            "🤖 Creating your quiz..."
        ):

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
    "🎓 StudyFinder AI | "
    "Streamlit + Groq + gpt-oss-120b"
)
