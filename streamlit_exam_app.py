import streamlit as st
import json
import random
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any
import pandas as pd

# إعداد الصفحة
st.set_page_config(
    page_title="نظام الامتحانات الذكي",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS مخصص لتحسين التصميم
st.markdown("""
<style>
.main-header {
    background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    padding: 1rem;
    border-radius: 10px;
    color: white;
    text-align: center;
    margin-bottom: 2rem;
}

.question-container {
    background: #f8f9fa;
    padding: 1.5rem;
    border-radius: 10px;
    border-left: 5px solid #667eea;
    margin: 1rem 0;
}

.option-container {
    background: white;
    padding: 1rem;
    border-radius: 8px;
    margin: 0.5rem 0;
    border: 2px solid #e9ecef;
    transition: all 0.3s ease;
}

.selected-option {
    border-color: #667eea !important;
    background-color: #f8f9ff !important;
}

.timer-container {
    background: #dc3545;
    color: white;
    padding: 1rem;
    border-radius: 10px;
    text-align: center;
    font-size: 1.5rem;
    font-weight: bold;
    margin-bottom: 1rem;
}

.timer-warning {
    background: #ffc107 !important;
    color: black !important;
}

.stats-container {
    background: #e9ecef;
    padding: 1rem;
    border-radius: 8px;
    margin: 1rem 0;
}

.result-correct {
    color: #28a745;
    font-weight: bold;
}

.result-incorrect {
    color: #dc3545;
    font-weight: bold;
}

.progress-bar {
    margin: 1rem 0;
}
</style>
""", unsafe_allow_html=True)

# تهيئة session state
def initialize_session_state():
    """تهيئة متغيرات الجلسة"""
    if 'questions' not in st.session_state:
        st.session_state.questions = []
    if 'current_exam' not in st.session_state:
        st.session_state.current_exam = []
    if 'current_question' not in st.session_state:
        st.session_state.current_question = 0
    if 'user_answers' not in st.session_state:
        st.session_state.user_answers = {}
    if 'exam_started' not in st.session_state:
        st.session_state.exam_started = False
    if 'exam_finished' not in st.session_state:
        st.session_state.exam_finished = False
    if 'start_time' not in st.session_state:
        st.session_state.start_time = None
    if 'exam_duration' not in st.session_state:
        st.session_state.exam_duration = 90  # 90 دقيقة
    if 'show_results' not in st.session_state:
        st.session_state.show_results = False

def load_questions():
    """تحميل الأسئلة من ملف JSON"""
    try:
        with open('questions_data.json', 'r', encoding='utf-8') as f:
            st.session_state.questions = json.load(f)
        return True
    except FileNotFoundError:
        st.error("لم يتم العثور على ملف الأسئلة. يرجى التأكد من وجود ملف questions_data.json")
        return False
    except json.JSONDecodeError:
        st.error("خطأ في قراءة ملف الأسئلة. يرجى التأكد من صحة تنسيق الملف")
        return False

def generate_exam(num_questions: int = 65):
    """إنشاء امتحان جديد"""
    if len(st.session_state.questions) < num_questions:
        num_questions = len(st.session_state.questions)
        st.warning(f"تم تقليل عدد الأسئلة إلى {num_questions} (العدد المتاح)")
    
    st.session_state.current_exam = random.sample(st.session_state.questions, num_questions)
    st.session_state.current_question = 0
    st.session_state.user_answers = {}
    st.session_state.exam_started = True
    st.session_state.exam_finished = False
    st.session_state.start_time = datetime.now()
    st.session_state.show_results = False

def get_remaining_time():
    """حساب الوقت المتبقي"""
    if not st.session_state.start_time:
        return st.session_state.exam_duration * 60
    
    elapsed = datetime.now() - st.session_state.start_time
    remaining = st.session_state.exam_duration * 60 - elapsed.total_seconds()
    return max(0, remaining)

def format_time(seconds):
    """تنسيق الوقت"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)
    
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    else:
        return f"{minutes:02d}:{seconds:02d}"

def display_question(question_data, question_index):
    """عرض السؤال"""
    st.markdown(f"""
    <div class="question-container">
        <h3>السؤال {question_index + 1} من {len(st.session_state.current_exam)}</h3>
        <p><strong>الفئة:</strong> {question_data['category']}</p>
        <div style="font-size: 1.1rem; margin: 1rem 0;">
            {question_data['question']}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # عرض شريط التقدم
    progress = (question_index + 1) / len(st.session_state.current_exam)
    st.progress(progress)
    
    # عرض الخيارات
    question_key = f"q_{question_data['id']}"
    
    if question_data['question_type'] == 'single':
        # سؤال اختيار واحد - استخدام radio buttons
        selected_option = st.radio(
            f"اختر إجابة واحدة:",
            options=list(range(len(question_data['options']))),
            format_func=lambda x: f"{chr(65 + x)}. {question_data['options'][x]}",
            key=question_key,
            index=st.session_state.user_answers.get(question_key, [None])[0] if question_key in st.session_state.user_answers else None
        )
        
        if selected_option is not None:
            st.session_state.user_answers[question_key] = [selected_option]
    
    else:
        # سؤال اختيار متعدد - استخدام checkboxes
        st.write(f"اختر {question_data['select_count']} إجابات:")
        
        selected_options = []
        for i, option in enumerate(question_data['options']):
            is_selected = st.checkbox(
                f"{chr(65 + i)}. {option}",
                key=f"{question_key}_{i}",
                value=i in st.session_state.user_answers.get(question_key, [])
            )
            if is_selected:
                selected_options.append(i)
        
        st.session_state.user_answers[question_key] = selected_options
        
        # تحقق من عدد الإجابات المحددة
        if len(selected_options) > question_data['select_count']:
            st.warning(f"يرجى اختيار {question_data['select_count']} إجابات فقط")
        elif len(selected_options) < question_data['select_count'] and len(selected_options) > 0:
            st.info(f"يرجى اختيار {question_data['select_count'] - len(selected_options)} إجابة إضافية")

def calculate_score():
    """حساب النتيجة"""
    correct_answers = 0
    total_questions = len(st.session_state.current_exam)
    
    results = []
    
    for question in st.session_state.current_exam:
        question_key = f"q_{question['id']}"
        user_answer = st.session_state.user_answers.get(question_key, [])
        
        # تحويل الإجابات الصحيحة إلى أرقام
        correct_indices = []
        for ans in question['correct_answer']:
            if ans in 'ABCDE':
                correct_indices.append(ord(ans) - ord('A'))
        
        correct_indices.sort()
        user_answer_sorted = sorted(user_answer) if user_answer else []
        
        is_correct = user_answer_sorted == correct_indices
        if is_correct:
            correct_answers += 1
        
        results.append({
            'question': question,
            'user_answer': user_answer,
            'correct_answer': correct_indices,
            'is_correct': is_correct
        })
    
    score_percentage = (correct_answers / total_questions) * 100 if total_questions > 0 else 0
    
    return {
        'correct_answers': correct_answers,
        'total_questions': total_questions,
        'score_percentage': score_percentage,
        'results': results
    }

def display_results():
    """عرض النتائج"""
    score_data = calculate_score()
    
    st.markdown('<div class="main-header"><h1>🎉 نتائج الامتحان 🎉</h1></div>', unsafe_allow_html=True)
    
    # عرض النتيجة الإجمالية
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "النتيجة",
            f"{score_data['score_percentage']:.1f}%",
            f"{score_data['correct_answers']}/{score_data['total_questions']}"
        )
    
    with col2:
        st.metric(
            "الإجابات الصحيحة",
            score_data['correct_answers'],
            f"من أصل {score_data['total_questions']}"
        )
    
    with col3:
        elapsed_time = datetime.now() - st.session_state.start_time
        st.metric(
            "الوقت المستغرق",
            format_time(elapsed_time.total_seconds()),
            f"من أصل {st.session_state.exam_duration} دقيقة"
        )
    
    # تقييم الأداء
    if score_data['score_percentage'] >= 90:
        st.success("🌟 ممتاز! أداء رائع")
    elif score_data['score_percentage'] >= 80:
        st.success("👍 جيد جداً! أداء جيد")
    elif score_data['score_percentage'] >= 70:
        st.warning("👌 جيد، يمكن تحسينه")
    elif score_data['score_percentage'] >= 60:
        st.warning("⚠️ مقبول، يحتاج مراجعة")
    else:
        st.error("📚 يحتاج دراسة أكثر")
    
    # عرض تفاصيل الأسئلة
    st.subheader("مراجعة الأسئلة")
    
    for i, result in enumerate(score_data['results']):
        question = result['question']
        user_answer = result['user_answer']
        correct_answer = result['correct_answer']
        is_correct = result['is_correct']
        
        # رأس السؤال
        if is_correct:
            st.markdown(f"### ✅ السؤال {i + 1} - صحيح")
        else:
            st.markdown(f"### ❌ السؤال {i + 1} - خطأ")
        
        # نص السؤال
        st.write(f"**{question['question']}**")
        
        # عرض الخيارات مع تمييز الإجابات
        for j, option in enumerate(question['options']):
            option_letter = chr(65 + j)
            
            if j in correct_answer and j in user_answer:
                # إجابة صحيحة ومختارة
                st.markdown(f"🟢 **{option_letter}. {option}** (إجابتك - صحيحة)")
            elif j in correct_answer:
                # إجابة صحيحة غير مختارة
                st.markdown(f"🟢 **{option_letter}. {option}** (الإجابة الصحيحة)")
            elif j in user_answer:
                # إجابة خاطئة مختارة
                st.markdown(f"🔴 {option_letter}. {option} (إجابتك - خاطئة)")
            else:
                # خيار عادي
                st.write(f"{option_letter}. {option}")
        
        # عرض التوضيح إذا كان متوفراً
        if question.get('explanation'):
            with st.expander("💡 التوضيح"):
                st.write(question['explanation'])
        
        st.divider()

def main():
    """الدالة الرئيسية للتطبيق"""
    initialize_session_state()
    
    # العنوان الرئيسي
    st.markdown('<div class="main-header"><h1>📝 نظام الامتحانات الذكي</h1></div>', unsafe_allow_html=True)
    
    # الشريط الجانبي
    with st.sidebar:
        st.header("⚙️ إعدادات الامتحان")
        
        if not st.session_state.exam_started:
            # تحميل الأسئلة
            if st.button("📂 تحميل الأسئلة"):
                if load_questions():
                    st.success(f"تم تحميل {len(st.session_state.questions)} سؤال")
            
            if st.session_state.questions:
                st.write(f"**عدد الأسئلة المتاحة:** {len(st.session_state.questions)}")
                
                # إعدادات الامتحان
                exam_questions = st.number_input(
                    "عدد أسئلة الامتحان",
                    min_value=10,
                    max_value=min(150, len(st.session_state.questions)),
                    value=min(65, len(st.session_state.questions))
                )
                
                st.session_state.exam_duration = st.number_input(
                    "مدة الامتحان (بالدقائق)",
                    min_value=30,
                    max_value=180,
                    value=90
                )
                
                if st.button("🚀 بدء الامتحان"):
                    generate_exam(exam_questions)
                    st.rerun()
        
        else:
            # معلومات الامتحان الحالي
            st.write(f"**عدد الأسئلة:** {len(st.session_state.current_exam)}")
            st.write(f"**السؤال الحالي:** {st.session_state.current_question + 1}")
            st.write(f"**الأسئلة المجابة:** {len(st.session_state.user_answers)}")
            
            # إنهاء الامتحان
            if st.button("🏁 إنهاء الامتحان", type="primary"):
                st.session_state.exam_finished = True
                st.session_state.show_results = True
                st.rerun()
            
            if st.button("🔄 إعادة تعيين"):
                for key in ['exam_started', 'exam_finished', 'current_exam', 'user_answers', 'current_question', 'start_time', 'show_results']:
                    if key in st.session_state:
                        del st.session_state[key]
                st.rerun()
    
    # المحتوى الرئيسي
    if not st.session_state.questions and not st.session_state.exam_started:
        st.info("👈 يرجى تحميل الأسئلة من الشريط الجانبي لبدء الامتحان")
        
        # نصائح للاستخدام
        with st.expander("📖 كيفية الاستخدام"):
            st.markdown("""
            1. **تحضير ملف الأسئلة:**
               - تأكد من وجود ملف `questions_data.json` في نفس مجلد التطبيق
               - يمكنك استخدام البرنامج المخصص لاستخراج الأسئلة من PDF
            
            2. **بدء الامتحان:**
               - اضغط على "تحميل الأسئلة" في الشريط الجانبي
               - اختر عدد الأسئلة ومدة الامتحان
               - اضغط على "بدء الامتحان"
            
            3. **أثناء الامتحان:**
               - أجب على الأسئلة بالتسلسل
               - للأسئلة متعددة الإجابات، حدد العدد المطلوب
               - راقب العداد الزمني في أعلى الصفحة
            
            4. **بعد الامتحان:**
               - اضغط على "إنهاء الامتحان" لرؤية النتائج
               - ستظهر النتيجة مع مراجعة مفصلة لكل سؤال
            """)
    
    elif st.session_state.exam_finished or st.session_state.show_results:
        display_results()
    
    elif st.session_state.exam_started and st.session_state.current_exam:
        # عرض العداد الزمني
        remaining_time = get_remaining_time()
        
        if remaining_time <= 0:
            st.error("⏰ انتهى الوقت!")
            st.session_state.exam_finished = True
            st.session_state.show_results = True
            st.rerun()
        
        # تحديد لون العداد بناءً على الوقت المتبقي