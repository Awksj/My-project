import streamlit as st
import PyPDF2
import docx
import pandas as pd
from openai import OpenAI
import io

client = OpenAI(api_key="ضع مفتاحك هنا")

def extract_text(file):
    if file.name.endswith(".pdf"):
        pdf_reader = PyPDF2.PdfReader(file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text
    elif file.name.endswith(".docx"):
        doc = docx.Document(file)
        return "\n".join([para.text for para in doc.paragraphs])
    elif file.name.endswith(".txt"):
        return file.read().decode("utf-8")
    else:
        return None

def generate_questions(text, question_count):
    prompt = f"""
    أنت أداة لإنشاء أسئلة امتحانات من النص التالي:

    النص:
    {text}

    المطلوب:
    أنشئ {question_count} أسئلة اختيار من متعدد.
    كل سؤال يحتوي:
    - سؤال واحد
    - 4 خيارات (A,B,C,D)
    - إجابة صحيحة واحدة
    - حدد الإجابة الصحيحة بعد كل سؤال بهذا الشكل:
      Correct Answer: A

    صيغة الإخراج تكون منظمة كالتالي:

    Q1: .....
    A) ....
    B) ....
    C) ....
    D) ....
    Correct Answer: A
    """

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

st.title("📚 AI Exam Generator")
st.subheader("توليد أسئلة اختيار من متعدد تلقائياً")

file = st.file_uploader("ارفع ملف PDF / DOCX / TXT", type=["pdf", "docx", "txt"])
question_count = st.number_input("عدد الأسئلة المطلوبة", min_value=1, max_value=50, value=5)

if file and st.button("توليد الأسئلة ✅"):
    with st.spinner("جاري استخراج النص وتحليل الملف..."):
        text = extract_text(file)

    if text:
        st.success("تم استخراج النص ✅")

        with st.spinner("جاري إنشاء الأسئلة بالذكاء الاصطناعي..."):
            questions = generate_questions(text, question_count)

        st.write("### ✅ الأسئلة الناتجة")
        st.text(questions)

        data = {"Questions": [questions]}
        df = pd.DataFrame(data)

        st.download_button("📄 تحميل كـ TXT", questions, file_name="questions.txt")

        excel_buffer = io.BytesIO()
        df.to_excel(excel_buffer, index=False)
        st.download_button("📊 تحميل Excel", excel_buffer, file_name="questions.xlsx")
    else:
        st.error("❌ نوع الملف غير مدعوم أو فشل استخراج النص")
