import streamlit as st
import json
import random
from datetime import datetime, timedelta
from pathlib import Path

# إعداد الصفحة
st.set_page_config(
    page_title="AWS AI Practitioner Prep Questions",
    page_icon="📝",
    layout="wide"
)

class ExamSystem:
    def __init__(self, questions_file="questions.json"):
        self.questions_file = questions_file
        self.questions = self.load_questions()
        
    def load_questions(self):
        """Load questions from JSON file"""
        try:
            if Path(self.questions_file).exists():
                with open(self.questions_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        return data
                    elif isinstance(data, dict) and 'questions' in data:
                        return data['questions']
                    else:
                        st.error("Invalid questions file format")
                        return []
            else:
                st.error(f"Questions file not found: {self.questions_file}")
                return []
        except Exception as e:
            st.error(f"Error loading questions: {str(e)}")
            return []
    
    def generate_exam(self, num_questions=65):
        """Generate random exam"""
        if len(self.questions) < num_questions:
            st.warning(f"Available questions ({len(self.questions)}) less than required ({num_questions})")
            return random.sample(self.questions, len(self.questions))
        return random.sample(self.questions, num_questions)
    
    def get_time_left(self, start_time, duration_minutes=90):
        """Calculate remaining time"""
        elapsed = datetime.now() - start_time
        remaining = timedelta(minutes=duration_minutes) - elapsed
        return max(remaining.total_seconds(), 0)

def init_session_state():
    """Initialize session state"""
    if 'exam_started' not in st.session_state:
        st.session_state.exam_started = False
    if 'current_question' not in st.session_state:
        st.session_state.current_question = 0
    if 'answers' not in st.session_state:
        st.session_state.answers = {}
    if 'exam_questions' not in st.session_state:
        st.session_state.exam_questions = []
    if 'start_time' not in st.session_state:
        st.session_state.start_time = None
    if 'exam_finished' not in st.session_state:
        st.session_state.exam_finished = False

def start_exam_page():
    """Exam start page"""
    st.title("🎓 Exam System")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        ### معلومات الامتحان
        - **عدد الأسئلة:** 65 سؤال
        - **المدة الزمنية:** ساعة ونصف (90 دقيقة)
        - **التقييم:** تلقائي بعد الانتهاء
        """)
        
        st.markdown("---")
        
        if st.button("🚀 Start Exam", use_container_width=True, type="primary"):
            exam_system = ExamSystem()
            if exam_system.questions:
                st.session_state.exam_questions = exam_system.generate_exam()
                st.session_state.exam_started = True
                st.session_state.start_time = datetime.now()
                st.session_state.current_question = 0
                st.session_state.answers = {}
                st.rerun()
            else:
                st.error("No questions available. Make sure questions.json file exists")

    # Footer المطور - تصميم متقدم
    st.markdown("---")
    st.markdown("""
    <style>
    .developer-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 25px;
        border-radius: 15px;
        text-align: center;
        box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3);
        margin: 30px 0;
        animation: fadeInUp 1s ease-out;
    }
    
    .developer-name {
        font-size: 24px;
        font-weight: bold;
        color: #FFD700;
        margin: 10px 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .developer-title {
        font-size: 16px;
        color: white;
        margin: 8px 0;
        opacity: 0.9;
    }
    
    .linkedin-link {
        display: inline-block;
        background: rgba(255, 255, 255, 0.2);
        padding: 8px 20px;
        border-radius: 25px;
        color: #FFD700;
        text-decoration: none;
        font-weight: bold;
        margin: 15px 0;
        transition: all 0.3s ease;
        backdrop-filter: blur(10px);
    }
    
    .linkedin-link:hover {
        background: rgba(255, 215, 0, 0.2);
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }
    
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
    
    .tech-icons {
        font-size: 18px;
        margin: 10px 0;
        color: white;
    }
    </style>
    
    <div class="developer-card">
        <h4 style="margin: 0; color: white;">🚀 تم تطوير هذا التطبيق بواسطة</h4>
        <div class="developer-name">Marwan Al-Masrrat</div>
        <div class="developer-title">💻 Full Stack Developer & AI Enthusiast</div>
        <div class="tech-icons">🐍 Python | ⚛️ React | 🤖 AI/ML | ☁️ Cloud</div>
        <a href="https://www.linkedin.com/in/marwan-al-masrat" target="_blank" class="linkedin-link">
            🔗 تواصل معي على LinkedIn
        </a>
        <p style="margin: 15px 0 0 0; font-size: 14px; color: white; opacity: 0.8;">
            ⭐ إذا أعجبك التطبيق، شاركني رأيك وتجربتك!
        </p>
    </div>
    """, unsafe_allow_html=True)

# --- بقية الدوال (exam_page, results_page, main) تبقى كما هي مع التحقق من ال indentation --- #

def main():
    """Main application function"""
    init_session_state()
    
    # Add custom CSS
    st.markdown("""
    <style>
    .stButton > button {
        border-radius: 10px;
    }
    
    /* Mobile improvements */
    @media (max-width: 768px) {
        .question-grid {
            grid-template-columns: repeat(5, 1fr) !important;
        }
        .question-btn {
            width: 45px !important;
            height: 45px !important;
            font-size: 12px !important;
        }
    }
    
    @media (max-width: 480px) {
        .question-grid {
            grid-template-columns: repeat(4, 1fr) !important;
        }
        .question-btn {
            width: 40px !important;
            height: 40px !important;
            font-size: 11px !important;
        }
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Navigate between pages
    if not st.session_state.exam_started:
        start_exam_page()
    elif st.session_state.exam_finished:
        from pathlib import Path
        results_page()
    else:
        exam_page()

if __name__ == "__main__":
    main()
