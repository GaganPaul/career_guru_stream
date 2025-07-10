# Imports
import streamlit as st
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
import docx2txt
import pdfplumber
import os
import firebase_admin
from firebase_admin import credentials, firestore, auth
from streamlit_option_menu import option_menu
import time
import json


# Firebase Initialization
if not firebase_admin._apps:
    # For local development
    if os.path.exists("serviceAccountKey.json"):
        cred = credentials.Certificate("serviceAccountKey.json")
    else:
        # For production (Render.com)
        firebase_config = {
            "type": os.environ.get("FIREBASE_TYPE"),
            "project_id": os.environ.get("FIREBASE_PROJECT_ID"),
            "private_key_id": os.environ.get("FIREBASE_PRIVATE_KEY_ID"),
            "private_key": os.environ.get("FIREBASE_PRIVATE_KEY").replace('\\n', '\n'),
            "client_email": os.environ.get("FIREBASE_CLIENT_EMAIL"),
            "client_id": os.environ.get("FIREBASE_CLIENT_ID"),
            "auth_uri": os.environ.get("FIREBASE_AUTH_URI"),
            "token_uri": os.environ.get("FIREBASE_TOKEN_URI"),
            "auth_provider_x509_cert_url": os.environ.get("FIREBASE_AUTH_PROVIDER_X509_CERT_URL"),
            "client_x509_cert_url": os.environ.get("FIREBASE_CLIENT_X509_CERT_URL")
        }
        cred = credentials.Certificate(firebase_config)

    firebase_admin.initialize_app(cred)
db = firestore.client()

# Modern Theme Configuration
st.set_page_config(
    page_title="Career Guru",
    layout="wide",
    initial_sidebar_state="collapsed",
    page_icon="🚀"
)

# Enhanced Modern CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    :root {
        --primary-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        --secondary-gradient: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        --accent-gradient: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        --dark-bg: #0a0a0a;
        --card-bg: rgba(255, 255, 255, 0.05);
        --border-color: rgba(255, 255, 255, 0.1);
        --text-primary: #ffffff;
        --text-secondary: rgba(255, 255, 255, 0.7);
        --shadow-light: 0 8px 32px rgba(0, 0, 0, 0.3);
        --shadow-heavy: 0 20px 60px rgba(0, 0, 0, 0.4);
    }

    * {
        font-family: 'Inter', sans-serif;
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }

    .main {
        background: radial-gradient(ellipse at top, #1a1a2e 0%, #0a0a0a 100%);
        min-height: 100vh;
        color: var(--text-primary);
    }

    .block-container {
        padding: 1rem;
        max-width: 1400px;
    }

    /* Landing Page Styles */
    .hero-section {
        background: var(--primary-gradient);
        padding: 2rem 1rem;
        border-radius: 24px;
        text-align: center;
        margin: 2rem auto; /* Center the section horizontally */
        position: relative;
        overflow: hidden;
        box-shadow: var(--shadow-heavy);
        max-width: 900px; /* Optional, control width */
    }

    .hero-section::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 1000"><polygon fill="rgba(255,255,255,0.1)" points="0,0 1000,300 1000,1000 0,700"/></svg>');
        pointer-events: none;
    }

    .hero-content {
    max-width: 700px;
    margin: 0 auto; /* Center content inside the hero section */
}

    .hero-title {
        font-size: 4rem;
        font-weight: 800;
        margin-bottom: 1rem;
        background: linear-gradient(45deg, #fff, #f0f0f0);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0 4px 20px rgba(0,0,0,0.5);
        line-height: 1.1;
    }

    .hero-subtitle {
        font-size: 1.5rem;
        font-weight: 400;
        opacity: 0.9;
        margin-bottom: 2rem;
        max-width: 600px;
        margin-left: auto;
        margin-right: auto;
    }

    .cta-button {
        background: var(--accent-gradient);
        color: white;
        padding: 1rem 2.5rem;
        border-radius: 50px;
        text-decoration: none;
        font-weight: 600;
        font-size: 1.1rem;
        transition: all 0.3s ease;
        display: inline-block;
        border: none;
        cursor: pointer;
        box-shadow: 0 4px 20px rgba(79, 172, 254, 0.3);
    }

    .cta-button:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 30px rgba(79, 172, 254, 0.4);
    }

    /* Feature Cards */
    .features-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: 2rem;
        margin: 2rem 0;
    }

    .feature-card {
        background: var(--card-bg);
        backdrop-filter: blur(20px);
        border-radius: 20px;
        padding: 2.5rem;
        border: 1px solid var(--border-color);
        transition: all 0.4s ease;
        text-align: center;
        position: relative;
        overflow: hidden;
    }

    .feature-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: var(--primary-gradient);
        transform: scaleX(0);
        transition: transform 0.3s ease;
    }

    .feature-card:hover::before {
        transform: scaleX(1);
    }

    .feature-card:hover {
        transform: translateY(-10px);
        box-shadow: var(--shadow-heavy);
        border-color: rgba(255, 255, 255, 0.2);
    }

    .feature-icon {
        font-size: 3rem;
        margin-bottom: 1.5rem;
        display: block;
    }

    .feature-title {
        font-size: 1.5rem;
        font-weight: 600;
        margin-bottom: 1rem;
        color: var(--text-primary);
    }

    .feature-description {
        color: var(--text-secondary);
        line-height: 1.6;
        font-size: 1rem;
    }

    /* Auth Pages */
    .auth-container {
        max-width: 450px;
        margin: 0 auto;
        padding: 3rem;
        background: var(--card-bg);
        backdrop-filter: blur(20px);
        border-radius: 24px;
        border: 1px solid var(--border-color);
        box-shadow: var(--shadow-heavy);
    }

    .auth-header {
        text-align: center;
        margin-bottom: 2rem;
    }

    .auth-title {
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        background: var(--primary-gradient);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .auth-subtitle {
        color: var(--text-secondary);
        font-size: 1.1rem;
    }

    /* Input Styles */
    .stTextInput > div > div > input {
        background: rgba(255, 255, 255, 0.05);
        border: 2px solid var(--border-color);
        border-radius: 16px;
        color: var(--text-primary);
        padding: 1rem 1.5rem;
        font-size: 1rem;
        transition: all 0.3s ease;
        backdrop-filter: blur(10px);
    }

    .stTextInput > div > div > input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.2);
        background: rgba(255, 255, 255, 0.08);
    }

    .stTextInput > div > div > input::placeholder {
        color: rgba(255, 255, 255, 0.4);
    }

    /* Button Styles */
    .stButton > button {
        background: var(--primary-gradient);
        color: white;
        border: none;
        border-radius: 16px;
        padding: 1rem 2rem;
        font-size: 1.1rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 20px rgba(102, 126, 234, 0.3);
        width: 100%;
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 30px rgba(102, 126, 234, 0.4);
    }

    /* Navigation */
    .nav-back {
        display: flex;
        align-items: center;
        color: var(--text-secondary);
        text-decoration: none;
        font-weight: 500;
        margin-bottom: 2rem;
        transition: color 0.3s ease;
    }

    .nav-back:hover {
        color: var(--text-primary);
    }

    /* Chat Interface */
    .chat-container {
        background: var(--card-bg);
        border-radius: 16px;
        padding: 1.5rem;
        margin: 1rem 0;
        border: 1px solid var(--border-color);
        backdrop-filter: blur(20px);
    }

    .message {
        padding: 1rem 1.5rem;
        border-radius: 20px;
        margin: 0.5rem 0;
        max-width: 80%;
        word-wrap: break-word;
    }

    .user-message {
        background: var(--primary-gradient);
        color: white;
        margin-left: auto;
        border-bottom-right-radius: 8px;
    }

    .ai-message {
        background: rgba(255, 255, 255, 0.1);
        color: var(--text-primary);
        border-bottom-left-radius: 8px;
    }

    /* Sidebar */
    .sidebar .sidebar-content {
        background: var(--dark-bg);
        border-right: 1px solid var(--border-color);
    }

    /* File Upload */
    .stFileUploader {
        background: var(--card-bg);
        border-radius: 16px;
        padding: 2rem;
        border: 2px dashed var(--border-color);
        text-align: center;
        backdrop-filter: blur(20px);
    }

    /* Loading Animation */
    .loading-spinner {
        display: inline-block;
        width: 20px;
        height: 20px;
        border: 3px solid rgba(255, 255, 255, 0.3);
        border-radius: 50%;
        border-top-color: #667eea;
        animation: spin 1s ease-in-out infinite;
    }

    @keyframes spin {
        to { transform: rotate(360deg); }
    }

    /* Success/Error Messages */
    .stSuccess, .stError {
        border-radius: 12px;
        padding: 1rem;
        margin: 1rem 0;
    }

    /* Responsive Design */
    @media (max-width: 768px) {
        .hero-title {
            font-size: 2.5rem;
        }

        .hero-subtitle {
            font-size: 1.2rem;
        }

        .auth-container {
            padding: 2rem;
            margin: 1rem;
        }

        .features-grid {
            grid-template-columns: 1fr;
        }

        .feature-card {
            padding: 2rem;
        }
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

    .fade-in-up {
        animation: fadeInUp 0.8s ease-out;
    }

    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateX(-20px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }

    .slide-in {
        animation: slideIn 0.6s ease-out;
    }
</style>
""", unsafe_allow_html=True)

# Session State Initialization
if "page" not in st.session_state:
    st.session_state.page = "landing"
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user" not in st.session_state:
    st.session_state.user = None


# Authentication Functions
def register_user(email, password):
    try:
        user = auth.create_user(email=email, password=password)
        db.collection("users").document(user.uid).set({
            "email": email,
            "chat_history": [],
            "created_at": firestore.SERVER_TIMESTAMP
        })
        return True, "🎉 Account created successfully! Welcome to Career Guru!"
    except Exception as e:
        return False, f"Registration failed: {str(e)}"


def login_user(email, password):
    try:
        users = db.collection("users").where("email", "==", email).stream()
        for user in users:
            st.session_state.authenticated = True
            st.session_state.user = user.id
            st.session_state.page = "dashboard"
            return True, "Welcome back! Login successful."
        return False, "Invalid credentials. Please check your email and password."
    except Exception as e:
        return False, f"Login failed: {str(e)}"


# Navigation Functions
def go_to_page(page_name):
    st.session_state.page = page_name
    st.rerun()


def logout():
    st.session_state.authenticated = False
    st.session_state.user = None
    st.session_state.page = "landing"
    st.rerun()


# PAGE ROUTING
if st.session_state.page == "landing":
    # LANDING PAGE
    st.markdown("""
    <div class="hero-section fade-in-up">
        <div class="hero-content">
            <h1 class="hero-title">🚀 Career Guru</h1>
            <h4 class="hero-subtitle" style="text-align: center; margin: 0 auto 2rem auto; max-width: 600px;">
                Transform your career journey with AI-powered guidance and personalized coaching
            </h4>
            <div style="margin-top: 2rem; text-align: center;">
                <a href="#login-section" style="text-decoration: none;">
                    <button class="cta-button" style="
                        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
                        color: white;
                        padding: 1.2rem 4rem;
                        border-radius: 50px;
                        font-weight: 600;
                        font-size: 1.3rem;
                        border: none;
                        cursor: pointer;
                        box-shadow: 0 6px 25px rgba(79, 172, 254, 0.4);
                        display: inline-block;
                    ">
                        Get Started Today
                    </button>
                </a>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Features Section
    st.markdown('<div class="features-grid fade-in-up">', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div class="feature-card">
            <span class="feature-icon">🎯</span>
            <h3 class="feature-title">AI Mock Interviews</h3>
            <p class="feature-description">Practice with intelligent AI that adapts to your role and provides real-time feedback</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="feature-card">
            <span class="feature-icon">🔍</span>
            <h3 class="feature-title">Career Intelligence</h3>
            <p class="feature-description">Explore career paths with data-driven insights and personalized recommendations</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="feature-card">
            <span class="feature-icon">📊</span>
            <h3 class="feature-title">Resume Optimization</h3>
            <p class="feature-description">Get expert-level resume analysis and ATS optimization suggestions</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # CTA Section
    st.markdown('<div style="text-align: center; margin: 4rem 0;">', unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1, 1])
    st.markdown('<div id="login-section"></div>', unsafe_allow_html=True)
    with col1:
        if st.button("🔐 Login", use_container_width=True):
            go_to_page("login")

    with col2:
        if st.button("🚀 Sign Up", use_container_width=True):
            go_to_page("register")

    with col3:
        if st.button("ℹ️ Learn More", use_container_width=True):
            go_to_page("about")

    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.page == "login":
    # LOGIN PAGE
    st.markdown("""
    <div class="slide-in">
        <div style="margin-bottom: 2rem;">
            <a href="#" class="nav-back" onclick="window.location.reload()">← Back to Home</a>
        </div>
        <div class="auth-container">
            <div class="auth-header">
                <h1 class="auth-title">Welcome Back</h1>
                <p class="auth-subtitle">Sign in to continue your career journey</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Back button
    if st.button("← Back to Home"):
        go_to_page("landing")

    # Login Form
    with st.form("login_form"):
        email = st.text_input("📧 Email Address", placeholder="Enter your email")
        password = st.text_input("🔒 Password", type="password", placeholder="Enter your password")

        col1, col2 = st.columns(2)

        with col1:
            login_btn = st.form_submit_button("🚀 Sign In", use_container_width=True)

        with col2:
            if st.form_submit_button("📝 Create Account", use_container_width=True):
                go_to_page("register")

    if login_btn:
        if email and password:
            with st.spinner("Signing you in..."):
                success, msg = login_user(email, password)
                if success:
                    st.success(msg)
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error(msg)
        else:
            st.error("Please fill in all fields!")

elif st.session_state.page == "register":
    # REGISTER PAGE
    st.markdown("""
    <div class="slide-in">
        <div style="margin-bottom: 2rem;">
            <a href="#" class="nav-back" onclick="window.location.reload()">← Back to Home</a>
        </div>
        <div class="auth-container">
            <div class="auth-header">
                <h1 class="auth-title">Join Career Guru</h1>
                <p class="auth-subtitle">Create your account and start your journey</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Back button
    if st.button("← Back to Home"):
        go_to_page("landing")

    # Register Form
    with st.form("register_form"):
        email = st.text_input("📧 Email Address", placeholder="Enter your email")
        password = st.text_input("🔒 Password", type="password", placeholder="Create a password")
        confirm_password = st.text_input("🔒 Confirm Password", type="password", placeholder="Confirm your password")

        col1, col2 = st.columns(2)

        with col1:
            register_btn = st.form_submit_button("🎉 Create Account", use_container_width=True)

        with col2:
            if st.form_submit_button("🔐 Already have account?", use_container_width=True):
                go_to_page("login")

    if register_btn:
        if email and password and confirm_password:
            if password == confirm_password:
                if len(password) >= 6:
                    with st.spinner("Creating your account..."):
                        success, msg = register_user(email, password)
                        if success:
                            st.success(msg)
                            time.sleep(2)
                            go_to_page("login")
                        else:
                            st.error(msg)
                else:
                    st.error("Password must be at least 6 characters long!")
            else:
                st.error("Passwords don't match!")
        else:
            st.error("Please fill in all fields!")
#ABOUT PAGE
elif st.session_state.page == "about":
    st.markdown('<div style="margin-top: 40px;"></div>', unsafe_allow_html=True)
    if st.button("← Back to Home"):
        go_to_page("landing")

    # About Page with Streamlit components instead of raw HTML
    st.markdown("# About Career Guru")
    st.markdown("### Your intelligent career companion")

    st.markdown("---")

    # Introduction
    st.markdown("""
    **Career Guru** is your intelligent career companion, helping professionals with AI-powered career guidance and personalized support.
    """)

    # What We Offer
    st.markdown("## 🚀 What We Offer")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        **🎤 AI Mock Interviews**  
        Tailored mock interview sessions with real-time AI feedback

        **🧠 Career Intelligence**  
        Discover paths based on skills, goals, and job market trends
        """)

    with col2:
        st.markdown("""
        **📄 Resume Optimization**  
        ATS-friendly, industry-standard formatting and suggestions

        **💼 Coaching**  
        Smart tips to grow in your role and transition with confidence
        """)

    # Mission
    st.markdown("## 🎯 Our Mission")
    st.markdown("""
    We aim to democratize high-quality career coaching using artificial intelligence—making it accessible, affordable, and personalized for every learner and job-seeker.
    """)

    # Why Choose Us
    st.markdown("## 💡 Why Choose Us?")
    st.markdown("""
    - Easy-to-use, voice-first and mobile-friendly interface
    - Built with advanced LLMs and personalized models
    - Works across industries and languages
    - Continuously improving based on your feedback
    """)

    # Call to action
    st.success(
        "💼 Whether you're a student, job seeker, or working professional, Career Guru is here to elevate your career journey with modern tools that actually make a difference.")

    # Feature highlights
    st.markdown("---")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        ### 🎯 Smart AI
        Advanced language models trained on career expertise
        """)

    with col2:
        st.markdown("""
        ### 🚀 Fast Results
        Get instant feedback and actionable insights
        """)

    with col3:
        st.markdown("""
        ### 🔒 Secure
        Your data is protected with enterprise-grade security
        """)

elif st.session_state.authenticated:
    # DASHBOARD - Main Application

    # Initialize LLM
    GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
    if not GROQ_API_KEY:
        st.error("🔑 Please add your GROQ_API_KEY ")
        st.stop()

    llm = ChatGroq(api_key=GROQ_API_KEY, model="llama3-8b-8192", temperature=0.7)

    # Sidebar Navigation
    with st.sidebar:
        st.markdown("### 🚀 Career Guru")
        st.markdown("---")

        selected = option_menu(
            menu_title=None,
            options=["Mock Interview", "Career Explorer", "Resume Analyzer", "Logout"],
            icons=["mic-fill", "search", "file-earmark-text-fill", "box-arrow-left"],
            menu_icon="list",
            default_index=0,
            styles={
                "container": {"padding": "0!important", "background-color": "transparent"},
                "icon": {"color": "#667eea", "font-size": "18px"},
                "nav-link": {
                    "font-size": "16px",
                    "text-align": "left",
                    "margin": "0px",
                    "color": "white",
                    "background-color": "transparent",
                    "border-radius": "12px",
                    "padding": "12px 16px",
                },
                "nav-link-selected": {"background-color": "#667eea"},
            }
        )

    # Handle Logout
    if selected == "Logout":
        logout()

    # Mock Interview
    if selected == "Mock Interview":
        st.markdown("""
        <div class="chat-container">
            <h2>🎯 AI Mock Interview Coach</h2>
            <p>Practice your interview skills with our intelligent AI coach</p>
        </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns(2)

        with col1:
            role = st.text_input("🎯 Job Role", placeholder="e.g., Software Engineer")

        with col2:
            company = st.text_input("🏢 Company Type", placeholder="e.g., Tech Startup")

        question = st.text_area("💬 Your Question or Topic", placeholder="What would you like to practice?")

        if st.button("🚀 Get Coaching", use_container_width=True):
            if role and question:
                with st.spinner("🤖 AI Coach is thinking..."):
                    template = PromptTemplate(
                        input_variables=["role", "company", "question"],
                        template="""You are an expert interview coach with 15+ years of experience. 
                        The user is preparing for a {role} position at a {company} company.

                        User's question/topic: {question}

                        Provide helpful, specific, and actionable advice. Include:
                        1. Direct answer to their question
                        2. Common interview questions for this role
                        3. Key points to emphasize
                        4. Potential follow-up questions

                        Keep it conversational and encouraging."""
                    )
                    prompt = template.format(role=role, company=company or "typical", question=question)
                    response = llm.invoke(prompt).content

                    st.markdown(f"""
                    <div class="chat-container">
                        <div class="message user-message">
                            <strong>You:</strong> {question}
                        </div>
                        <div class="message ai-message">
                            <strong>🤖 AI Coach:</strong><br>{response}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.error("Please fill in the job role and your question!")

    # Career Explorer
    elif selected == "Career Explorer":
        st.markdown("""
        <div class="chat-container">
            <h2>🔍 Career Intelligence Hub</h2>
            <p>Explore career paths and get personalized guidance</p>
        </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns(2)

        with col1:
            career_interest = st.text_input("🎯 Career Interest", placeholder="e.g., Data Science, UX Design")

        with col2:
            experience_level = st.selectbox("📊 Experience Level",
                                            ["Entry Level", "Mid Level", "Senior Level", "Executive"])

        query = st.text_area("❓ Your Question", placeholder="What would you like to know about this career?")

        if st.button("🔍 Explore Career", use_container_width=True):
            if career_interest and query:
                with st.spinner("🔍 Gathering career insights..."):
                    prompt = f"""You are a career counselor and industry expert. 
                    The user is interested in {career_interest} at {experience_level} level.

                    User's question: {query}

                    Provide comprehensive guidance including:
                    1. Role overview and responsibilities
                    2. Required skills and qualifications
                    3. Career progression paths
                    4. Industry trends and salary insights
                    5. Actionable next steps

                    Be specific and provide practical advice."""

                    result = llm.invoke(prompt).content

                    st.markdown(f"""
                    <div class="chat-container">
                        <div class="message user-message">
                            <strong>You:</strong> {query}
                        </div>
                        <div class="message ai-message">
                            <strong>🔍 Career Intelligence:</strong><br>{result}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.error("Please fill in your career interest and question!")

    # Resume Analyzer
    elif selected == "Resume Analyzer":
        st.markdown("""
        <div class="chat-container">
            <h2>📊 Resume Analyzer</h2>
            <p>Get expert-level resume analysis and optimization tips</p>
        </div>
        """, unsafe_allow_html=True)

        uploaded_file = st.file_uploader(
            "📎 Upload Your Resume",
            type=["pdf", "docx"],
            help="Supported formats: PDF, DOCX (Max 10MB)"
        )

        if uploaded_file:
            with st.spinner("📖 Analyzing your resume..."):
                try:
                    text = ""
                    ext = uploaded_file.name.split('.')[-1].lower()

                    if ext == "pdf":
                        with pdfplumber.open(uploaded_file) as pdf:
                            for page in pdf.pages:
                                text += page.extract_text() or ""
                    elif ext == "docx":
                        text = docx2txt.process(uploaded_file)

                    if text:
                        resume_prompt = f"""You are a senior HR professional and resume expert with 10+ years of experience.
                        Analyze this resume and provide comprehensive feedback:

                        Resume Content:
                        {text}

                        Provide detailed analysis covering:
                        1. **Overall Impression** - First impression and key strengths
                        2. **Structure & Format** - Layout, organization, readability
                        3. **Content Quality** - Achievements, quantifiable results, relevance
                        4. **ATS Optimization** - Keywords, formatting for applicant tracking systems
                        5. **Areas for Improvement** - Specific suggestions with examples
                        6. **Industry Alignment** - How well it fits target roles
                        7. **Action Items** - 3-5 immediate steps to improve

                        Be specific, constructive, and actionable. Use a professional but encouraging tone."""

                        feedback = llm.invoke(resume_prompt).content

                        st.markdown(f"""
                        <div class="chat-container">
                            <h3>📊 Resume Analysis Report</h3>
                            <div class="message ai-message">
                                <strong>📈 Expert Analysis:</strong><br>{feedback}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                        # Download feedback option
                        st.download_button(
                            label="📥 Download Analysis Report",
                            data=feedback,
                            file_name="resume_analysis_report.txt",
                            mime="text/plain",
                            use_container_width=True
                        )

                        # Save to user history
                        try:
                            db.collection("users").document(st.session_state.user).update({
                                "resume_analyses": firestore.ArrayUnion([{
                                    "filename": uploaded_file.name,
                                    "analysis": feedback[:500] + "...",  # Store summary
                                    "timestamp": firestore.SERVER_TIMESTAMP
                                }])
                            })
                        except:
                            pass  # Continue if database update fails

                    else:
                        st.error("❌ Could not extract text from the file. Please try a different format.")

                except Exception as e:
                    st.error(f"❌ Error processing file: {str(e)}")

        else:
            st.markdown("""
            <div class="chat-container">
                <div style="text-align: center; padding: 2rem;">
                    <h3>🎯 Resume Analysis Features</h3>
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1.5rem; margin-top: 2rem;">
                        <div style="background: rgba(255,255,255,0.05); padding: 1.5rem; border-radius: 12px;">
                            <h4>📝 Content Review</h4>
                            <p>Detailed analysis of your experience, skills, and achievements</p>
                        </div>
                        <div style="background: rgba(255,255,255,0.05); padding: 1.5rem; border-radius: 12px;">
                            <h4>🤖 ATS Optimization</h4>
                            <p>Ensure your resume passes applicant tracking systems</p>
                        </div>
                        <div style="background: rgba(255,255,255,0.05); padding: 1.5rem; border-radius: 12px;">
                            <h4>🎯 Industry Alignment</h4>
                            <p>Match your resume to industry standards and expectations</p>
                        </div>
                        <div style="background: rgba(255,255,255,0.05); padding: 1.5rem; border-radius: 12px;">
                            <h4>📊 Actionable Insights</h4>
                            <p>Get specific recommendations for immediate improvements</p>
                        </div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

else:
    # Fallback - redirect to landing
    go_to_page("landing")