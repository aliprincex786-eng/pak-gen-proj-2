import os
import requests
import streamlit as st


# ============================================================
# PAGE CONFIGURATION
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
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    /* ================================
       MAIN APPLICATION
       ================================ */

    .stApp {
        background: #f7f9fc;
    }

    .block-container {
        max-width: 1200px;
        padding-top: 1.5rem;
        padding-bottom: 3rem;
    }


    /* ================================
       TOP HEADER
       ================================ */

    .top-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 5px 0 25px 0;
    }

    .brand {
        font-size: 28px;
        font-weight: 800;
        color: #111827;
    }

    .brand-icon {
        display: inline-block;
        background: #2563eb;
        color: white;
        padding: 7px 10px;
        border-radius: 10px;
        margin-right: 8px;
    }

    .tagline {
        color: #6b7280;
        font-size: 14px;
    }


    /* ================================
       HERO SECTION
       ================================ */

    .hero {
        background: linear-gradient(
            135deg,
            #1e3a8a 0%,
            #2563eb 50%,
            #4f46e5 100%
        );

        border-radius: 24px;
        padding: 55px 30px;
        text-align: center;
        color: white;

        margin: 10px 0 35px 0;

        box-shadow:
            0 18px 40px rgba(37, 99, 235, 0.25);
    }

    .hero-content {
        max-width: 850px;
        margin: auto;
    }

    .hero-icon {
        font-size: 55px;
        line-height: 1;
        margin-bottom: 12px;
    }

    .hero-title {
        font-size: 48px;
        font-weight: 800;
        line-height: 1.15;
        margin-bottom: 16px;
        color: white;
    }

    .hero-description {
        font-size: 18px;
        line-height: 1.7;
        max-width: 720px;
        margin: 0 auto 28px auto;
        color: white;
        opacity: 0.96;
    }

    .hero-badges {
        display: flex;
        justify-content: center;
        flex-wrap: wrap;
        gap: 10px;
    }

    .hero-badge {
        background: rgba(255, 255, 255, 0.15);
        border: 1px solid rgba(255, 255, 255, 0.25);
        padding: 8px 15px;
        border-radius: 25px;
        font-size: 14px;
        color: white;
    }


    /* ================================
       SEARCH AREA
       ================================ */

    .search-heading {
        font-size: 28px;
        font-weight: 800;
        color: #111827;
        margin-bottom: 5px;
    }

    .search-description {
        color: #6b7280;
        font-size: 15px;
        margin-bottom: 12px;
    }


    /* ================================
       FEATURE CARDS
       ================================ */

    .feature-card {
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 18px;
        padding: 22px;
        min-height: 155px;

        box-shadow:
            0 6px 18px rgba(0, 0, 0, 0.04);
    }

    .feature-icon {
        font-size: 30px;
        margin-bottom: 8px;
    }

    .feature-title {
        font-size: 17px;
        font-weight: 750;
        color: #111827;
    }

    .feature-text {
        color: #6b7280;
        font-size: 13px;
        line-height: 1.5;
        margin-top: 6px;
    }


    /* ================================
       RESULTS
       ================================ */

    .result-header {
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 18px;
        padding: 22px;
        margin-top: 30px;
        margin-bottom: 20px;

        box-shadow:
            0 6px 18px rgba(0, 0, 0, 0.04);
    }

    .result-title {
        font-size: 25px;
        font-weight: 800;
        color: #111827;
    }

    .result-description {
        color: #6b7280;
        margin-top: 5px;
    }


    /* ================================
       SIDEBAR
       ================================ */

    section[data-testid="stSidebar"] {
        background: #ffffff;
    }


    /* ================================
       FOOTER
       ================================ */

    .footer {
        text-align: center;
        color: #9ca3af;
        font-size: 13px;
        padding: 30px 10px 10px 10px;
    }


    /* ================================
       MOBILE RESPONSIVE
       ================================ */

    @media (max-width: 768px) {

        .hero {
            padding: 40px 20px;
        }

        .hero-title {
            font-size: 36px;
        }

        .hero-description {
            font-size: 16px;
        }

        .tagline {
            display: none;
        }
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# GET GROQ API KEY
# ============================================================

def get_groq_api_key():

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
    max_tokens=3500
):

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
                    "You are StudyFinder AI, an expert "
                    "educational assistant. "
                    "Help students discover useful learning "
                    "resources and understand academic topics. "
                    "Use simple English. "
                    "Be accurate and practical. "
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

        # -----------------------------
        # RATE LIMIT
        # -----------------------------

        if response.status_code == 429:

            return None, (
                "⚠️ Groq rate limit reached.\n\n"
                "Please wait a few seconds and try again."
            )

        # -----------------------------
        # AUTHENTICATION ERROR
        # -----------------------------

        if response.status_code in [401, 403]:

            return None, (
                "❌ Groq API key is invalid or "
                "does not have permission to use the API."
            )

        # -----------------------------
        # OTHER API ERROR
        # -----------------------------

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

        # -----------------------------
        # SUCCESS
        # -----------------------------

        data = response.json()

        answer = data["choices"][0]["message"]["content"]

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
# GENERATE STUDY RESOURCES
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

Return a clean Markdown study guide.

Use these sections:

# 📚 Study Guide

## 🎯 Topic Overview

Explain the topic in simple language.

## 🛣️ Learning Roadmap

Give 5 logical steps for learning this topic.

## 🎥 Video Resources

Recommend {resource_count} useful video topics.

IMPORTANT:
Do NOT invent individual YouTube video URLs.

Instead provide YouTube SEARCH URLs.

Example:

https://www.youtube.com/results?search_query=Newton+Laws

For every video include:

### 🎥 Video Recommendation

**Topic:** ...

**Why watch it:** ...

**YouTube Search:** [Search YouTube](URL)

## 🌐 Websites

Recommend useful educational websites.

For every website include:

**Website:** ...

**Why it is useful:** ...

**URL:** ...

Prefer reputable sources such as:

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

Recommend useful courses and tutorials.

## 🧪 Practice

Give 3 practical exercises.

## ⭐ Best Starting Point

Tell the student which resource they should use first.

IMPORTANT:
- Never invent URLs.
- Use simple English.
- Keep the guide practical.
- Make it useful for students.
"""


    return call_groq(
        prompt,
        temperature=0.3,
        max_tokens=3500
    )


# ============================================================
# AI TUTOR
# ============================================================

def ask_tutor(
    topic,
    question
):

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
3. Give a real-world example.
4. Correct misunderstandings.
5. Keep the answer focused.
6. If programming is involved, provide code examples.
7. Use headings and bullet points.
"""


    return call_groq(
        prompt,
        temperature=0.4,
        max_tokens=2200
    )


# ============================================================
# QUIZ GENERATOR
# ============================================================

def generate_quiz(topic):

    prompt = f"""
Create a 5-question multiple-choice quiz.

TOPIC:
{topic}

For each question use:

## Question 1

Question text

A. Option

B. Option

C. Option

D. Option

**Correct Answer:** B

**Explanation:** Explain the answer.

Create exactly 5 questions.

Make the questions educational and suitable
for a student learning this topic.
"""


    return call_groq(
        prompt,
        temperature=0.5,
        max_tokens=2500
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
# HERO
# ============================================================

st.markdown(
    """
    <div class="hero">

        <div class="hero-content">

            <div class="hero-icon">
                🎓
            </div>

            <div class="hero-title">
                StudyFinder AI
            </div>

            <div class="hero-description">
                Describe what you want to learn and discover
                videos, websites, courses, tutorials and
                practice resources — all in one place.
            </div>

            <div class="hero-badges">

                <span class="hero-badge">
                    🎥 Videos
                </span>

                <span class="hero-badge">
                    🌐 Websites
                </span>

                <span class="hero-badge">
                    📖 Courses
                </span>

                <span class="hero-badge">
                    🤖 AI Tutor
                </span>

                <span class="hero-badge">
                    🧠 Quiz
                </span>

            </div>

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

    st.write(
        "Customize your learning experience."
    )

    student_level = st.selectbox(
        "📚 Student Level",
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

    st.markdown("### 💡 How It Works")

    st.markdown(
        """
        **1.** 🔎 Enter a topic

        **2.** 🤖 AI analyzes it

        **3.** 📚 Resources are generated

        **4.** 💬 Ask the AI Tutor

        **5.** 🧠 Take a quiz
        """
    )

    st.divider()

    st.markdown("### 🚀 Powered By")

    st.caption(
        "Groq API"
    )

    st.caption(
        "openai/gpt-oss-120b"
    )


# ============================================================
# SEARCH SECTION
# ============================================================

st.markdown(
    """
    <div class="search-heading">
        🔎 What do you want to learn?
    </div>

    <div class="search-description">
        Enter a course, subject, programming language,
        technology or any topic.
    </div>
    """,
    unsafe_allow_html=True
)


topic = st.text_input(
    "Topic",
    placeholder=(
        "Example: Newton Laws, Python, Cybersecurity, "
        "Machine Learning..."
    ),
    label_visibility="collapsed"
)


# ============================================================
# SEARCH BUTTON
# ============================================================

search_clicked = st.button(
    "🚀 Find My Study Resources",
    use_container_width=True,
    type="primary"
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
            "🤖 gpt-oss-120b is creating "
            "your personalized study guide..."
        ):

            result, error = generate_resources(
                topic.strip(),
                student_level,
                resource_count
            )

        if error:

            st.error(error)

        else:

            # Save result
            st.session_state["topic"] = topic.strip()

            st.session_state["resources"] = result


# ============================================================
# FEATURE CARDS
# ============================================================

if "resources" not in st.session_state:

    st.markdown(
        "### 🌟 Everything You Need to Learn"
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.markdown(
            """
            <div class="feature-card">

                <div class="feature-icon">
                    🎥
                </div>

                <div class="feature-title">
                    Video Learning
                </div>

                <div class="feature-text">
                    Discover useful YouTube
                    learning resources for your topic.
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:

        st.markdown(
            """
            <div class="feature-card">

                <div class="feature-icon">
                    🌐
                </div>

                <div class="feature-title">
                    Educational Websites
                </div>

                <div class="feature-text">
                    Find trusted websites,
                    documentation and tutorials.
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )

    with col3:

        st.markdown(
            """
            <div class="feature-card">

                <div class="feature-icon">
                    📖
                </div>

                <div class="feature-title">
                    Courses & Tutorials
                </div>

                <div class="feature-text">
                    Find courses and tutorials
                    that match your learning level.
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )

    with col4:

        st.markdown(
            """
            <div class="feature-card">

                <div class="feature-icon">
                    🤖
                </div>

                <div class="feature-title">
                    AI Tutor
                </div>

                <div class="feature-text">
                    Ask questions and receive
                    personalized explanations.
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )


# ============================================================
# DISPLAY RESULTS
# ============================================================

if "resources" in st.session_state:

    st.markdown(
        """
        <div class="result-header">

            <div class="result-title">
                📚 Your Personalized Study Guide
            </div>

            <div class="result-description">
                Resources selected for your learning topic.
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )

    # Display only once
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
        f"Ask anything about "
        f"**{st.session_state['topic']}**."
    )

    tutor_question = st.text_area(
        "Your question",
        placeholder=(
            "Example: Explain Newton's First Law "
            "with a real-world example."
        ),
        label_visibility="collapsed"
    )

    if st.button(
        "💬 Ask AI Tutor",
        use_container_width=True
    ):

        if not tutor_question.strip():

            st.warning(
                "⚠️ Please enter your question."
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

    st.write(
        "Check how well you understand the topic."
    )

    if st.button(
        "📝 Generate 5-Question Quiz",
        use_container_width=True
    ):

        with st.spinner(
            "🧠 Creating your quiz..."
        ):

            quiz, error = generate_quiz(
                st.session_state["topic"]
            )

        if error:

            st.error(error)

        else:

            st.markdown(
                "### 📝 Your Quiz"
            )

            st.markdown(quiz)


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.markdown(
    """
    <div class="footer">

        🎓 <b>StudyFinder AI</b>

        <br><br>

        Learn smarter • Discover better resources •
        Practice with AI

        <br>

        Powered by Groq + gpt-oss-120b

    </div>
    """,
    unsafe_allow_html=True
)
