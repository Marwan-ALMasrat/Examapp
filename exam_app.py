
def start_exam_page():
    """صفحة بداية الامتحان"""
    st.title("🎓 نظام الامتحانات")
    
    # قسم رفع ملف الأسئلة
    st.markdown("### 📂 رفع ملف الأسئلة")
    uploaded_file = st.file_uploader(
        "اختر ملف الأسئلة (JSON)", 
        type=['json'],
        help="ارفع ملف questions.json الخاص بك"
    )
    
    if uploaded_file is not None:
        try:
            # قراءة وحفظ الملف
            content = uploaded_file.read()
            questions_data = json.loads(content.decode('utf-8'))
            
            # حفظ الملف محلياً
            with open('questions.json', 'w', encoding='utf-8') as f:
                json.dump(questions_data, f, ensure_ascii=False, indent=2)
            
            st.success(f"تم رفع الملف بنجاح! عدد الأسئلة: {len(questions_data)}")
            
        except Exception as e:
            st.error(f"خطأ في قراءة الملف: {str(e)}")
    
    st.markdown("---")
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
        """تحميل الأسئلة من ملف JSON"""
        try:
            if Path(self.questions_file).exists():
                with open(self.questions_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        return data
                    elif isinstance(data, dict) and 'questions' in data:
                        return data['questions']
                    else:
                        st.error("تنسيق ملف الأسئلة غير صحيح")
                        return []
            else:
                st.error(f"ملف الأسئلة غير موجود: {self.questions_file}")
                return []
        except Exception as e:
            st.error(f"خطأ في تحميل الأسئلة: {str(e)}")
            return []
    
    def generate_exam(self, num_questions=65):
        """إنشاء امتحان عشوائي"""
        if len(self.questions) < num_questions:
            st.warning(f"عدد الأسئلة المتاحة ({len(self.questions)}) أقل من المطلوب ({num_questions})")
            return random.sample(self.questions, len(self.questions))
        return random.sample(self.questions, num_questions)
    
    def get_time_left(self, start_time, duration_minutes=90):
        """حساب الوقت المتبقي"""
        elapsed = datetime.now() - start_time
        remaining = timedelta(minutes=duration_minutes) - elapsed
        return max(remaining.total_seconds(), 0)

def init_session_state():
    """تهيئة session state"""
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
    """صفحة بداية الامتحان"""
    st.title("AWS AI Practitioner Prep Questions")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        ### معلومات الامتحان
        - **عدد الأسئلة:** 65 سؤال
        - **المدة الزمنية:** ساعة ونصف (90 دقيقة)
        - **التقييم:** تلقائي بعد الانتهاء
        """)
        
        st.markdown("---")
        
        if st.button("🚀 بدء الامتحان", use_container_width=True, type="primary"):
            exam_system = ExamSystem()
            if exam_system.questions:
                st.session_state.exam_questions = exam_system.generate_exam()
                st.session_state.exam_started = True
                st.session_state.start_time = datetime.now()
                st.session_state.current_question = 0
                st.session_state.answers = {}
                st.rerun()
            else:
                st.error("لا توجد أسئلة متاحة. تأكد من وجود ملف questions.json")

def exam_page():
    """صفحة الامتحان"""
    exam_system = ExamSystem()
    
    # التحقق من انتهاء الوقت
    time_left = exam_system.get_time_left(st.session_state.start_time)
    
    if time_left <= 0 and not st.session_state.exam_finished:
        st.session_state.exam_finished = True
        st.rerun()
    
    # شريط علوي بالمعلومات
    col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
    
    with col1:
        st.metric("السؤال الحالي", f"{st.session_state.current_question + 1}/{len(st.session_state.exam_questions)}")
    
    with col2:
        answered = len([a for a in st.session_state.answers.values() if a])
        st.metric("الأسئلة المجاب عليها", f"{answered}/{len(st.session_state.exam_questions)}")
    
    with col3:
        minutes = int(time_left // 60)
        seconds = int(time_left % 60)
        st.metric("الوقت المتبقي", f"{minutes:02d}:{seconds:02d}")
    
    with col4:
        if st.button("⏹️ إنهاء الامتحان"):
            st.session_state.exam_finished = True
            st.rerun()
    
    st.markdown("---")
    
    # عرض السؤال الحالي
    if st.session_state.current_question < len(st.session_state.exam_questions):
        question = st.session_state.exam_questions[st.session_state.current_question]
        
        # عنوان السؤال
        st.markdown(f"### السؤال {st.session_state.current_question + 1}")
        st.markdown(f"**{question['question']}**")
        
        # تحديد نوع السؤال
        question_type = question.get('question_type', 'single')
        select_count = question.get('select_count', 1)
        
        if select_count > 1:
            st.info(f"اختر {select_count} إجابات")
        
        # عرض الخيارات
        question_key = f"q_{st.session_state.current_question}"
        
        if question_type == 'single' or select_count == 1:
            # سؤال اختيار واحد - راديو بتن
            options = [f"{key}. {value}" for key, value in question['options'].items()]
            selected = st.radio(
                "اختر الإجابة الصحيحة:",
                options,
                key=f"radio_{question_key}",
                index=None
            )
            
            if selected:
                selected_key = selected[0]  # أخذ الحرف الأول
                st.session_state.answers[question_key] = [selected_key]
        
        else:
            # سؤال اختيار متعدد - checkboxes
            st.write("اختر الإجابات الصحيحة:")
            selected_options = []
            
            for key, value in question['options'].items():
                if st.checkbox(f"{key}. {value}", key=f"check_{question_key}_{key}"):
                    selected_options.append(key)
            
            st.session_state.answers[question_key] = selected_options
        
        # أزرار التنقل
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col1:
            if st.session_state.current_question > 0:
                if st.button("⬅️ السؤال السابق", use_container_width=True):
                    st.session_state.current_question -= 1
                    st.rerun()
        
        with col3:
            if st.session_state.current_question < len(st.session_state.exam_questions) - 1:
                if st.button("السؤال التالي ➡️", use_container_width=True):
                    st.session_state.current_question += 1
                    st.rerun()
            else:
                if st.button("📝 إنهاء الامتحان", use_container_width=True, type="primary"):
                    st.session_state.exam_finished = True
                    st.rerun()
        
        # شريط التقدم
        progress = (st.session_state.current_question + 1) / len(st.session_state.exam_questions)
        st.progress(progress)
        
        # خريطة الأسئلة
        st.markdown("### خريطة الأسئلة")
        
        # تقسيم الأسئلة إلى صفوف
        questions_per_row = 13
        for row in range(0, len(st.session_state.exam_questions), questions_per_row):
            cols = st.columns(min(questions_per_row, len(st.session_state.exam_questions) - row))
            
            # استبدل الجزء من السطر 231 إلى 248 بهذا الكود:

        # خريطة الأسئلة
        st.markdown("### خريطة الأسئلة")
        
        # تقسيم الأسئلة إلى صفوف
        questions_per_row = 13
        for row in range(0, len(st.session_state.exam_questions), questions_per_row):
            cols = st.columns(min(questions_per_row, len(st.session_state.exam_questions) - row))
            
            for i, col in enumerate(cols):
                q_index = row + i
                if q_index < len(st.session_state.exam_questions):
                    q_key = f"q_{q_index}"
                    
                    # تحديد لون الزر وإنشاء الزر بالطريقة الصحيحة
                    if q_index == st.session_state.current_question:
                        label = f"📍 {q_index + 1}"
                        if col.button(label, key=f"nav_{q_index}", type="primary"):
                            st.session_state.current_question = q_index
                            st.rerun()
                    elif q_key in st.session_state.answers and st.session_state.answers[q_key]:
                        label = f"✅ {q_index + 1}"
                        if col.button(label, key=f"nav_{q_index}", type="secondary"):
                            st.session_state.current_question = q_index
                            st.rerun()
                    else:
                        label = f"{q_index + 1}"
                        if col.button(label, key=f"nav_{q_index}"):
                            st.session_state.current_question = q_index
                            st.rerun()
                        

def results_page():
    """صفحة النتائج"""
    st.title("🎉 نتائج الامتحان")
    
    # حساب النتيجة
    total_questions = len(st.session_state.exam_questions)
    correct_answers = 0
    
    for i, question in enumerate(st.session_state.exam_questions):
        question_key = f"q_{i}"
        user_answer = st.session_state.answers.get(question_key, [])
        correct_answer = question['correct_answer']
        
        if set(user_answer) == set(correct_answer):
            correct_answers += 1
    
    score_percentage = (correct_answers / total_questions) * 100
    
    # عرض النتيجة الإجمالية
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("النتيجة النهائية", f"{score_percentage:.1f}%")
    
    with col2:
        st.metric("الإجابات الصحيحة", f"{correct_answers}/{total_questions}")
    
    with col3:
        st.metric("الإجابات الخاطئة", f"{total_questions - correct_answers}/{total_questions}")
    
    # تحديد مستوى الأداء
    if score_percentage >= 90:
        st.success("🏆 ممتاز! أداء رائع")
    elif score_percentage >= 80:
        st.success("🥇 جيد جداً! أداء مميز")
    elif score_percentage >= 70:
        st.info("🥈 جيد! يمكن التحسن أكثر")
    elif score_percentage >= 60:
        st.warning("🥉 مقبول! تحتاج لمزيد من الدراسة")
    else:
        st.error("📚 تحتاج لمراجعة شاملة")
    
    st.markdown("---")
    
    # عرض تفاصيل الإجابات
    if st.checkbox("عرض تفاصيل الإجابات"):
        for i, question in enumerate(st.session_state.exam_questions):
            question_key = f"q_{i}"
            user_answer = st.session_state.answers.get(question_key, [])
            correct_answer = question['correct_answer']
            is_correct = set(user_answer) == set(correct_answer)
            
            with st.expander(f"السؤال {i + 1} {'✅' if is_correct else '❌'}"):
                st.write(f"**{question['question']}**")
                
                for key, value in question['options'].items():
                    if key in correct_answer and key in user_answer:
                        st.success(f"{key}. {value} ✅ (إجابتك - صحيحة)")
                    elif key in correct_answer:
                        st.error(f"{key}. {value} ❌ (الإجابة الصحيحة - لم تختارها)")
                    elif key in user_answer:
                        st.error(f"{key}. {value} ❌ (إجابتك - خاطئة)")
                    else:
                        st.write(f"{key}. {value}")
                
                if 'explanation' in question:
                    st.info(f"**التفسير:** {question['explanation']}")
    
    # أزرار الإجراءات
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 امتحان جديد", use_container_width=True, type="primary"):
            # إعادة تعيين جميع المتغيرات
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
    
    with col2:
        if st.button("📊 تصدير النتائج", use_container_width=True):
            # إنشاء ملف JSON للنتائج
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
                label="📥 تحميل النتائج (JSON)",
                data=json.dumps(results_data, ensure_ascii=False, indent=2),
                file_name=f"exam_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )

def main():
    """الدالة الرئيسية للتطبيق"""
    init_session_state()
    
    # إضافة CSS مخصص
    st.markdown("""
    <style>
    .stButton > button {
        border-radius: 10px;
    }
    .stProgress > div > div {
        background-color: #1f77b4;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # التحكم في التنقل بين الصفحات
    if not st.session_state.exam_started:
        start_exam_page()
    elif st.session_state.exam_finished:
        results_page()
    else:
        exam_page()

if __name__ == "__main__":
    main()







# في نهاية دالة results_page()

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
        <div class="tech-icons">🐍 Python | 🤖 AI/ML 
        <a href="https://www.linkedin.com/in/marwan-al-masrat" target="_blank" class="linkedin-link">
            🔗 تواصل معي على LinkedIn
        </a>
        <p style="margin: 15px 0 0 0; font-size: 14px; color: white; opacity: 0.8;">
            ⭐ إذا أعجبك التطبيق، شاركني رأيك وتجربتك!
        </p>
    </div>
    """, unsafe_allow_html=True)

# في نهاية دالة start_exam_page() - نسخة مبسطة

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
