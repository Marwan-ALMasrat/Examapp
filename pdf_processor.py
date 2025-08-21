import json
import re
import random
from typing import List, Dict, Any

def process_questions_from_text(pdf_text: str) -> List[Dict[str, Any]]:
    """
    معالجة النص المستخرج من ملف PDF وتحويله إلى قائمة منظمة من الأسئلة
    """
    questions = []
    
    # تقسيم النص إلى أسئلة منفصلة
    question_blocks = re.split(r'Question:\s*(\d+)', pdf_text)[1:]  # إزالة النص قبل أول سؤال
    
    # معالجة كل زوج (رقم السؤال، محتوى السؤال)
    for i in range(0, len(question_blocks), 2):
        if i + 1 < len(question_blocks):
            question_num = question_blocks[i]
            question_content = question_blocks[i + 1]
            
            # استخراج السؤال والخيارات والإجابة
            question_data = extract_question_data(question_num, question_content)
            if question_data:
                questions.append(question_data)
    
    return questions

def extract_question_data(question_num: str, content: str) -> Dict[str, Any]:
    """
    استخراج بيانات السؤال الواحد
    """
    try:
        # تنظيف النص
        content = content.strip()
        
        # استخراج نوع السؤال (category)
        category_match = re.search(r'\[(.*?)\]', content)
        category = category_match.group(1) if category_match else "General"
        
        # استخراج نص السؤال
        question_text = extract_question_text(content)
        if not question_text:
            return None
            
        # استخراج الخيارات
        options = extract_options(content)
        if not options:
            return None
            
        # استخراج الإجابة الصحيحة
        correct_answer = extract_correct_answer(content)
        if not correct_answer:
            return None
            
        # تحديد نوع السؤال (إجابة واحدة أم متعددة)
        question_type, select_count = determine_question_type(question_text, content)
        
        # استخراج التوضيح
        explanation = extract_explanation(content)
        
        return {
            "id": int(question_num),
            "category": category,
            "question": question_text.strip(),
            "options": options,
            "correct_answer": correct_answer,
            "question_type": question_type,
            "select_count": select_count,
            "explanation": explanation
        }
        
    except Exception as e:
        print(f"خطأ في معالجة السؤال رقم {question_num}: {e}")
        return None

def extract_question_text(content: str) -> str:
    """
    استخراج نص السؤال
    """
    # البحث عن النص بين category وأول خيار (A.)
    pattern = r'\](.*?)(?=A\.)'
    match = re.search(pattern, content, re.DOTALL)
    
    if match:
        question_text = match.group(1).strip()
        # تنظيف النص من العلامات غير المرغوبة
        question_text = re.sub(r'^[^\w]*', '', question_text)
        return question_text
    return ""

def extract_options(content: str) -> List[str]:
    """
    استخراج خيارات السؤال
    """
    options = []
    
    # البحث عن الخيارات A, B, C, D
    option_pattern = r'([A-E])\.\s*(.*?)(?=[A-E]\.|Answer:|$)'
    matches = re.findall(option_pattern, content, re.DOTALL)
    
    for letter, option_text in matches:
        # تنظيف النص
        option_text = re.sub(r'\n+', ' ', option_text).strip()
        option_text = re.sub(r'\s+', ' ', option_text)
        if option_text and not option_text.startswith('Answer:'):
            options.append(option_text)
    
    return options

def extract_correct_answer(content: str) -> List[str]:
    """
    استخراج الإجابة الصحيحة
    """
    # البحث عن السطر الذي يحتوي على "Answer:"
    answer_match = re.search(r'Answer:\s*([A-E,\s]+)', content)
    
    if answer_match:
        answer_text = answer_match.group(1).strip()
        # تقسيم الإجابات المتعددة
        answers = [ans.strip() for ans in re.split(r'[,\s]+', answer_text) if ans.strip()]
        return [ans for ans in answers if ans in 'ABCDE']
    
    return []

def determine_question_type(question_text: str, content: str) -> tuple:
    """
    تحديد نوع السؤال وعدد الإجابات المطلوبة
    """
    # البحث عن مؤشرات الأسئلة متعددة الإجابات
    select_patterns = [
        r'select\s+two',
        r'select\s+three',
        r'select\s+(\d+)',
        r'\(select\s+two\)',
        r'\(select\s+three\)',
        r'choose\s+two',
        r'choose\s+three'
    ]
    
    full_text = question_text + " " + content
    full_text = full_text.lower()
    
    for pattern in select_patterns:
        match = re.search(pattern, full_text)
        if match:
            if 'two' in match.group():
                return "multiple", 2
            elif 'three' in match.group():
                return "multiple", 3
            elif match.group(1) and match.group(1).isdigit():
                return "multiple", int(match.group(1))
    
    return "single", 1

def extract_explanation(content: str) -> str:
    """
    استخراج التوضيح إذا وجد
    """
    # البحث عن النص بعد "Explanation:"
    explanation_match = re.search(r'Explanation:\s*(.*?)(?=Question:|AWS\s+AI\s+Practitioner|$)', content, re.DOTALL)
    
    if explanation_match:
        explanation = explanation_match.group(1).strip()
        # تنظيف النص
        explanation = re.sub(r'\n+', ' ', explanation)
        explanation = re.sub(r'\s+', ' ', explanation)
        return explanation
    
    return ""

def save_questions_to_json(questions: List[Dict], filename: str = "questions_data.json"):
    """
    حفظ الأسئلة في ملف JSON
    """
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(questions, f, ensure_ascii=False, indent=2)
    print(f"تم حفظ {len(questions)} سؤال في ملف {filename}")

def generate_random_exam(questions: List[Dict], num_questions: int = 65) -> List[Dict]:
    """
    توليد امتحان عشوائي من الأسئلة
    """
    if len(questions) < num_questions:
        print(f"تحذير: عدد الأسئلة المتاحة ({len(questions)}) أقل من المطلوب ({num_questions})")
        return random.sample(questions, len(questions))
    
    return random.sample(questions, num_questions)

# استخدام البرنامج مع النص المستخرج من PDF
def main():
    # هنا يمكنك وضع النص المستخرج من ملف PDF
    # أو قراءته من ملف نصي
    
    # مثال لقراءة النص من ملف
    try:
        with open('pdf_content.txt', 'r', encoding='utf-8') as f:
            pdf_text = f.read()
    except FileNotFoundError:
        print("يرجى وضع محتوى PDF في ملف pdf_content.txt")
        return
    
    # معالجة الأسئلة
    questions = process_questions_from_text(pdf_text)
    
    if questions:
        # حفظ الأسئلة
        save_questions_to_json(questions)
        
        # عرض إحصائيات
        print(f"\nتمت معالجة {len(questions)} سؤال:")
        single_choice = len([q for q in questions if q['question_type'] == 'single'])
        multiple_choice = len([q for q in questions if q['question_type'] == 'multiple'])
        print(f"- أسئلة اختيار واحد: {single_choice}")
        print(f"- أسئلة اختيار متعدد: {multiple_choice}")
        
        # إنشاء امتحان تجريبي
        exam = generate_random_exam(questions, 65)
        save_questions_to_json(exam, "sample_exam.json")
        print(f"\nتم إنشاء امتحان تجريبي بـ {len(exam)} سؤال")
    else:
        print("لم يتم العثور على أسئلة صالحة في النص")

if __name__ == "__main__":
    main()
