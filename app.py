import streamlit as st
import PyPDF2
import docx
import pandas as pd
import io
import openai

st.set_page_config(page_title="AI MCQ Generator", layout="wide")
st.title("📚 مولد أسئلة اختيار من متعدد")

# ---- إدخال مفتاح OpenAI ----
client = OpenAI(api_key="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")
#api_key = st.text_input("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")

# ---- اختيار نوع الإدخال ----
input_type = st.radio("اختر نوع الإدخال:", ["TXT (نص يدوي)", "PDF / DOCX (ملف)"])

text = ""
file_ready = False

if input_type == "TXT (نص يدوي)":
    text = st.text_area("اكتب النص هنا:", height=300)
    if text.strip():
        file_ready = True
else:
    uploaded_file = st.file_uploader("اختر ملف PDF أو DOCX", type=["pdf", "docx"])
    if uploaded_file:
        file_ready = True
        # استخراج النص من الملف
        if uploaded_file.name.lower().endswith(".pdf"):
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        elif uploaded_file.name.lower().endswith(".docx"):
            doc = docx.Document(uploaded_file)
            text = "\n".join([p.text for p in doc.paragraphs])

# ---- عرض النص للمعاينة ----
if text:
    st.subheader("📄 النص المستخرج / المدخل:")
    st.text_area("Preview:", text, height=200)

# ---- إعداد توليد الأسئلة ----
num_q = st.number_input("عدد الأسئلة المطلوبة:", min_value=1, max_value=50, value=5)

# ---- زر توليد الأسئلة ----
if file_ready:
    if st.button("🧠 توليد الأسئلة"):
        st.spinner("جاري إنشاء الأسئلة...")
        try:
            openai.api_key = api_key
            prompt = f"""
            قم بتحويل النص التالي إلى {num_q} أسئلة اختيار من متعدد باللغة العربية.
            - لكل سؤال 4 خيارات (أ، ب، ج، د).
            - إجابة صحيحة واحدة فقط لكل سؤال.
            النص:
            {text}
            """
            response = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=1500
            )
            mcq_text = response.choices[0].message.content

            st.success("تم إنشاء الأسئلة ✅")
            st.subheader("📝 الأسئلة الناتجة:")
            st.code(mcq_text, language="text")

            # حفظ Excel
            df = pd.DataFrame({"Questions": mcq_text.split("\n\n")})
            excel_buf = io.BytesIO()
            df.to_excel(excel_buf, index=False)
            excel_buf.seek(0)
            st.download_button("⬇ تحميل Excel", excel_buf, file_name="mcq_questions.xlsx")
            st.download_button("⬇ تحميل TXT", mcq_text, file_name="mcq_questions.txt")

        except Exception as e:
            st.error(f"حدث خطأ أثناء الاتصال بـ OpenAI: {e}")
else:
    st.info("اختر نوع إدخال صالح ثم أضف نص أو ملف لتفعيل الزر.")
