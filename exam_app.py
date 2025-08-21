import streamlit as st
import json
import random
from datetime import datetime, timedelta
import time
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

    # Footer بسيط للصفحة الرئيسية
    st.markdown("""
    <div style='text-align: center; margin-top: 40px; padding: 20px; 
                border-top: 2px solid #e0e0e0;'>
        <div style='color: #666; font-size: 14px; margin-bottom: 8px;'>
            💻 Developed with ❤️ by <strong style='color: #667eea;'>Marwan Al-Masrrat</strong>
        </div>
        <a href='https://www.linkedin.com/in/marwan-al-masrat' target='_blank' 
           style='color: #0077B5; text-decoration: none; font-size: 13px;'>
           🔗 Connect on LinkedIn
        </a>
    </div>
    """, unsafe_allow_html=True)

def exam_page():
    """Exam page"""
    exam_system = ExamSystem()
    
    # Check if time is up
    time_left = exam_system.get_time_left(st.session_state.start_time)
    
    if time_left <= 0 and not st.session_state.exam_finished:
        st.session_state.exam_finished = True
        st.rerun()
    
    # Top information bar
    col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
    
    with col1:
        st.metric("Current Question", f"{st.session_state.current_question + 1}/{len(st.session_state.exam_questions)}")
    
    with col2:
        answered = len([a for a in st.session_state.answers.values() if a])
        st.metric("Answered Questions", f"{answered}/{len(st.session_state.exam_questions)}")
    
    with col3:
        minutes = int(time_left // 60)
        seconds = int(time_left % 60)
        st.metric("Time Remaining", f"{minutes:02d}:{seconds:02d}")
    
    with col4:
        if st.button("⏹️ End Exam"):
            st.session_state.exam_finished = True
            st.rerun()
    
    st.markdown("---")
    
    # Display current question
    if st.session_state.current_question < len(st.session_state.exam_questions):
        question = st.session_state.exam_questions[st.session_state.current_question]
        
        # Question title
        st.markdown(f"### Question {st.session_state.current_question + 1}")
        st.markdown(f"**{question['question']}**")
        
        # Determine question type
        question_type = question.get('question_type', 'single')
        select_count = question.get('select_count', 1)
        
        if select_count > 1:
            st.info(f"Select {select_count} answers")
        
        # Display options
        question_key = f"q_{st.session_state.current_question}"
        
        if question_type == 'single' or select_count == 1:
            # Single choice question - radio buttons
            options = [f"{key}. {value}" for key, value in question['options'].items()]
            selected = st.radio(
                "Choose the correct answer:",
                options,
                key=f"radio_{question_key}",
                index=None
            )
            
            if selected:
                selected_key = selected[0]  # Take first character
                st.session_state.answers[question_key] = [selected_key]
        
        else:
            # Multiple choice question - checkboxes
            st.write("Select the correct answers:")
            selected_options = []
            
            for key, value in question['options'].items():
                if st.checkbox(f"{key}. {value}", key=f"check_{question_key}_{key}"):
                    selected_options.append(key)
            
            st.session_state.answers[question_key] = selected_options
        
        st.markdown("---")
        
        # Navigation buttons
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col1:
            if st.session_state.current_question > 0:
                if st.button("⬅️ Previous Question", use_container_width=True):
                    st.session_state.current_question -= 1
                    st.rerun()
        
        with col3:
            if st.session_state.current_question < len(st.session_state.exam_questions) - 1:
                if st.button("Next Question ➡️", use_container_width=True):
                    st.session_state.current_question += 1
                    st.rerun()
            else:
                if st.button("📝 Finish Exam", use_container_width=True, type="primary"):
                    st.session_state.exam_finished = True
                    st.rerun()
        
        st.markdown("---")
        
        # Enhanced questions map for mobile phones
        st.markdown("### Questions Map")
        
        # Custom CSS for responsive questions grid
        st.markdown("""
        <style>
        .questions-container {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            justify-content: flex-start;
            align-items: flex-start;
            margin: 15px 0;
            padding: 10px;
            background: rgba(0,0,0,0.02);
            border-radius: 10px;
        }
        
        .question-number {
            min-width: 45px;
            height: 45px;
            border-radius: 8px;
            font-size: 14px;
            font-weight: bold;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.2s ease;
            border: 2px solid transparent;
            text-decoration: none;
            margin: 2px;
        }
        
        .question-number:hover {
            transform: scale(1.1);
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        }
        
        .question-answered {
            background-color: #007bff !important;
            color: white !important;
        }
        
        .question-unanswered {
            background-color: #dc3545 !important;
            color: white !important;
        }
        
        .question-current {
            background-color: #28a745 !important;
            color: white !important;
            border: 3px solid #155724 !important;
        }
        
        /* Mobile responsive */
        @media (max-width: 768px) {
            .questions-container {
                gap: 6px;
            }
            .question-number {
                min-width: 40px;
                height: 40px;
                font-size: 13px;
            }
        }
        
        @media (max-width: 480px) {
            .questions-container {
                gap: 5px;
            }
            .question-number {
                min-width: 38px;
                height: 38px;
                font-size: 12px;
            }
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Create HTML for questions grid
        questions_html = '<div class="questions-container">'
        
        for i in range(len(st.session_state.exam_questions)):
            q_key = f"q_{i}"
            
            # Determine CSS class
            if i == st.session_state.current_question:
                css_class = "question-current"
            elif q_key in st.session_state.answers and st.session_state.answers[q_key]:
                css_class = "question-answered"
            else:
                css_class = "question-unanswered"
            
            questions_html += f'<div class="question-number {css_class}" onclick="window.parent.postMessage({{type: \'streamlit:setComponentValue\', value: {i}}}, \'*\')">{i + 1}</div>'
        
        questions_html += '</div>'
        
        st.markdown(questions_html, unsafe_allow_html=True)
        
        # Alternative: Streamlit buttons as backup (hidden but functional)
        st.markdown('<div style="display: none;">', unsafe_allow_html=True)
        
        # Create buttons in rows for navigation
        questions_per_row = 13
        for row_start in range(0, len(st.session_state.exam_questions), questions_per_row):
            cols = st.columns(min(questions_per_row, len(st.session_state.exam_questions) - row_start))
            
            for i, col in enumerate(cols):
                q_index = row_start + i
                if q_index < len(st.session_state.exam_questions):
                    q_key = f"q_{q_index}"
                    
                    # Create clickable button with proper type handling
                    if q_index == st.session_state.current_question:
                        # Current question button (green)
                        if col.button(
                            str(q_index + 1), 
                            key=f"nav_btn_{q_index}",
                            type="primary"
                        ):
                            st.session_state.current_question = q_index
                            st.rerun()
                    elif q_key in st.session_state.answers and st.session_state.answers[q_key]:
                        # Answered question button (blue)
                        if col.button(
                            str(q_index + 1), 
                            key=f"nav_btn_{q_index}",
                            type="secondary"
                        ):
                            st.session_state.current_question = q_index
                            st.rerun()
                    else:
                        # Unanswered question button (red)
                        if col.button(
                            str(q_index + 1), 
                            key=f"nav_btn_{q_index}"
                        ):
                            st.session_state.current_question = q_index
                            st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)

def results_page():
    """Results page"""
    st.title("🎉 Exam Results")
    
    # Calculate score
    total_questions = len(st.session_state.exam_questions)
    correct_answers = 0
    
    for i, question in enumerate(st.session_state.exam_questions):
        question_key = f"q_{i}"
        user_answer = st.session_state.answers.get(question_key, [])
        correct_answer = question['correct_answer']
        
        if set(user_answer) == set(correct_answer):
            correct_answers += 1
    
    score_percentage = (correct_answers / total_questions) * 100
    
    # Display overall score
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Final Score", f"{score_percentage:.1f}%")
    
    with col2:
        st.metric("Correct Answers", f"{correct_answers}/{total_questions}")
    
    with col3:
        st.metric("Wrong Answers", f"{total_questions - correct_answers}/{total_questions}")
    
    # Determine performance level
    if score_percentage >= 90:
        st.success("🏆 Excellent! Outstanding performance")
    elif score_percentage >= 80:
        st.success("🥇 Very Good! Great performance")
    elif score_percentage >= 70:
        st.info("🥈 Good! Room for improvement")
    elif score_percentage >= 60:
        st.warning("🥉 Acceptable! Need more study")
    else:
        st.error("📚 Need comprehensive review")
    
    st.markdown("---")
    
    # Display answer details
    if st.checkbox("Show Answer Details"):
        for i, question in enumerate(st.session_state.exam_questions):
            question_key = f"q_{i}"
            user_answer = st.session_state.answers.get(question_key, [])
            correct_answer = question['correct_answer']
            is_correct = set(user_answer) == set(correct_answer)
            
            with st.expander(f"Question {i + 1} {'✅' if is_correct else '❌'}"):
                st.write(f"**{question['question']}**")
                
                for key, value in question['options'].items():
                    if key in correct_answer and key in user_answer:
                        st.success(f"{key}. {value} ✅ (Your answer - Correct)")
                    elif key in correct_answer:
                        st.error(f"{key}. {value} ❌ (Correct answer - You didn't choose)")
                    elif key in user_answer:
                        st.error(f"{key}. {value} ❌ (Your answer - Wrong)")
                    else:
                        st.write(f"{key}. {value}")
                
                if 'explanation' in question:
                    st.info(f"**Explanation:** {question['explanation']}")
    
    # Action buttons
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 New Exam", use_container_width=True, type="primary"):
            # Reset all variables
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
    
    with col2:
        if st.button("📊 Export Results", use_container_width=True):
            # Create JSON file for results
            results_data = {
                "exam_date": datetime.now().isoformat(),
                "total_questions": total_questions,
                "correct_answers": correct_answers,
                "score_percentage": score_percentage,
                "time_taken": str(datetime.now() - st.session_state.start_time),
                "detailed_answers": []
            }
            
            for i, question in enumerate(st.session_state.exam_questions):
                question_key = f"q_{i}"
                user_answer = st.session_state.answers.get(question_key, [])
                correct_answer = question['correct_answer']
                
                results_data["detailed_answers"].append({
                    "question_id": question.get('id', i),
                    "question": question['question'],
                    "user_answer": user_answer,
                    "correct_answer": correct_answer,
                    "is_correct": set(user_answer) == set(correct_answer)
                })
            
            st.download_button(
                label="📥 Download Results (JSON)",
                data=json.dumps(results_data, ensure_ascii=False, indent=2),
                file_name=f"exam_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )

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
        results_page()
    else:
        exam_page()

if __name__ == "__main__":
    main()
