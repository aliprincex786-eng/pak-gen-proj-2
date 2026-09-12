import json
import os
from urllib.parse import quote_plus
import streamlit as st
from openai import OpenAI
# ---------------------------------------------------------
# PAGE CONFIGURATION
# ---------------------------------------------------------
st.set_page_config(
    page_title="StudyFinder AI",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)
# ---------------------------------------------------------
# CUSTOM CSS
# ---------------------------------------------------------
st.markdown(
    """
    <style>
        .main {
            background-color: #f8fafc;
        }
        .hero {
            padding: 35px 20px;
            border-radius: 20px;
            background: linear-gradient(135deg, #4f46e5, #7c3aed);
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
            opacity: 0.95;
        }
        .resource-card {
            padding: 20px;
            border-radius: 15px;
            background: white;
            border: 1px solid #e5e7eb;
            margin-bottom: 15px;
            box-shadow: 0 3px 10px rgba(0,0,0,0.05);
        }
        .resource-card h3 {
            margin-top: 0;
        }
        .tag {
            display: inline-block;
            padding: 5px 10px;
            border-radius: 20px;
            background: #eef2ff;
            color: #4338ca;
            font-size: 13px;
            margin-bottom: 8px;
        }
        .footer {
            text-align: center;
            padding: 30px;
            color: #6b7280;
        }
    </style>
    """,
    unsafe_allow_html=True,
)
# ---------------------------------------------------------
# OPENROUTER CLIENT
# ---------------------------------------------------------
def get_client():
    api_key = st.secrets.get("OPENROUTER_API_KEY")
    if not api_key:
        api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        return None
    return OpenAI(
        api_key=api_key,
        base_url="https://openrouter.ai/api/v1",
    )
# ---------------------------------------------------------
# SEARCH URL HELPERS
# ---------------------------------------------------------
def youtube_search_url(query):
    return f"https://www.youtube.com/results?search_query={quote_plus(query)}"
def google_search_url(query):
    return f"https://www.google.com/search?q={quote_plus(query)}"
def course_search_url(query):
    return f"https://www.google.com/search?q={quote_plus(query + ' online course')}"
def documentation_search_url(query):
    return f"https://www.google.com/search?q={quote_plus(query + ' documentation tutorial')}"
def practice_search_url(query):
    return f"https://www.google.com/search?q={quote_plus(query + ' practice exercises')}"
# ---------------------------------------------------------
# AI RESOURCE GENERATION
# ---------------------------------------------------------
def generate_resources(topic):
    client = get_client()
    if client is None:
        st.error(
            "OPENROUTER_API_KEY is missing. Add it to Streamlit Secrets "
            "or your local environment."
        )
        return None
    system_prompt = """
You are StudyFinder AI.
Your job is to analyze a user's learning topic and create useful
resource recommendations.
Return ONLY valid JSON.
The JSON must have exactly this structure:
{
    "topic": "short topic name",
    "summary": "short explanation of what the learner should study",
    "search_queries": [
        "query 1",
        "query 2",
        "query 3",
        "query 4",
        "query 5"
    ],
    "videos": [
        {
            "title": "video search topic",
            "description": "why this video search is useful"
        }
    ],
    "websites": [
        {
            "title": "website/resource search topic",
            "description": "why this resource is useful"
        }
    ],
    "courses": [
        {
            "title": "course search topic",
            "description": "why this course is useful"
        }
    ],
    "practice": [
        {
            "title": "practice search topic",
            "description": "what the learner can practice"
        }
    ]
}
Important:
- Do not invent exact URLs.
- Do not claim that a specific course or video exists.
- Give search topics that can be converted into reliable search links.
- Prefer official documentation, reputable educational platforms,
  YouTube educational content, and practical exercises.
- Keep recommendations relevant to the user's topic.
- Use simple English.
"""
    user_prompt = f"""
The learner wants to study:
{topic}
Create a useful learning resource plan for this topic.
"""
    try:
        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": user_prompt,
                },
            ],
            temperature=0.4,
            max_tokens=3000,
        )
        content = response.choices[0].message.content.strip()
        # Remove markdown JSON fences if the model adds them.
        if content.startswith("```"):
            content = content.replace("```json", "")
            content = content.replace("```", "")
            content = content.strip()
        return json.loads(content)
    except json.JSONDecodeError:
        st.error("The AI returned an invalid response. Please try again.")
        return None
    except Exception as e:
        st.error(f"AI request failed: {e}")
        return None
# ---------------------------------------------------------
# HEADER
# ---------------------------------------------------------
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
    unsafe_allow_html=True,
)
# ---------------------------------------------------------
# SIDEBAR
# ---------------------------------------------------------
with st.sidebar:
    st.header("⚙️ Settings")
    st.info(
        """
        Enter any learning topic.
        Examples:
        - Python programming
        - Cybersecurity
        - Database management
        - Flutter development
        - Machine learning
        - C++ DSA
        """
    )
    st.divider()
    st.caption("Powered by gpt-oss-120b")
    st.caption("Built with Streamlit")
# ---------------------------------------------------------
# USER INPUT
# ---------------------------------------------------------
st.subheader("🔎 What do you want to learn?")
topic = st.text_input(
    "Learning topic",
    placeholder="Example: Learn Python from beginner to advanced",
)
search_clicked = st.button(
    "🚀 Find Learning Resources",
    type="primary",
    use_container_width=True,
)
# ---------------------------------------------------------
# GENERATE RESULTS
# ---------------------------------------------------------
if search_clicked:
    if not topic.strip():
        st.warning("Please enter a topic first.")
        st.stop()
    with st.spinner("🤖 AI is finding the best learning paths..."):
        results = generate_resources(topic)
    if results:
        st.session_state["results"] = results
        st.session_state["topic"] = topic
# ---------------------------------------------------------
# DISPLAY RESULTS
# ---------------------------------------------------------
if "results" in st.session_state:
    results = st.session_state["results"]
    st.success(
        f"Learning resources generated for: {st.session_state['topic']}"
    )
    # -----------------------------------------------------
    # SUMMARY
    # -----------------------------------------------------
    st.header("📚 Learning Overview")
    st.write(results.get("summary", ""))
    # -----------------------------------------------------
    # VIDEOS
    # -----------------------------------------------------
    st.header("🎥 Videos")
    videos = results.get("videos", [])
    if videos:
        for video in videos:
            title = video.get("title", "Learning video")
            description = video.get("description", "")
            st.markdown(
                f"""
                <div class="resource-card">
                    <span class="tag">VIDEO</span>
                    <h3>{title}</h3>
                    <p>{description}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.link_button(
                "▶️ Search YouTube",
                youtube_search_url(title),
                use_container_width=True,
            )
    else:
        st.info("No video recommendations were generated.")
    # -----------------------------------------------------
    # WEBSITES
    # -----------------------------------------------------
    st.header("🌐 Websites & Documentation")
    websites = results.get("websites", [])
    if websites:
        for website in websites:
            title = website.get("title", "Learning website")
            description = website.get("description", "")
            st.markdown(
                f"""
                <div class="resource-card">
                    <span class="tag">WEBSITE</span>
                    <h3>{title}</h3>
                    <p>{description}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
            col1, col2 = st.columns(2)
            with col1:
                st.link_button(
                    "🔎 Search Web",
                    google_search_url(title),
                    use_container_width=True,
                )
            with col2:
                st.link_button(
                    "📖 Find Documentation",
                    documentation_search_url(title),
                    use_container_width=True,
                )
    else:
        st.info("No website recommendations were generated.")
    # -----------------------------------------------------
    # COURSES
    # -----------------------------------------------------
    st.header("🎓 Courses")
    courses = results.get("courses", [])
    if courses:
        for course in courses:
            title = course.get("title", "Online course")
            description = course.get("description", "")
            st.markdown(
                f"""
                <div class="resource-card">
                    <span class="tag">COURSE</span>
                    <h3>{title}</h3>
                    <p>{description}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.link_button(
                "🎓 Search Courses",
                course_search_url(title),
                use_container_width=True,
            )
    else:
        st.info("No course recommendations were generated.")
    # -----------------------------------------------------
    # PRACTICE
    # -----------------------------------------------------
    st.header("💻 Practice Resources")
    practice = results.get("practice", [])
    if practice:
        for item in practice:
            title = item.get("title", "Practice exercises")
            description = item.get("description", "")
            st.markdown(
                f"""
                <div class="resource-card">
                    <span class="tag">PRACTICE</span>
                    <h3>{title}</h3>
                    <p>{description}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.link_button(
                "💻 Find Practice",
                practice_search_url(title),
                use_container_width=True,
            )
    else:
        st.info("No practice recommendations were generated.")
    # -----------------------------------------------------
    # SEARCH QUERIES
    # -----------------------------------------------------
    st.header("🔍 Suggested Searches")
    queries = results.get("search_queries", [])
    for query in queries:
        st.markdown(f"- `{query}`")
# ---------------------------------------------------------
# FOOTER
# ---------------------------------------------------------
st.markdown(
    """
    <div class="footer">
        🎓 StudyFinder AI • AI-powered learning resource discovery
    </div>
    """,
    unsafe_allow_html=True,
)