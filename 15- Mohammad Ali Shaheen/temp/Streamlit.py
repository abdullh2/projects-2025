import streamlit as st
import pickle
from nltk.tokenize import word_tokenize
import nltk
import string
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

# تحميل النموذج المحفوظ و CountVectorizer
with open('multinomial_nb_model.pkl', 'rb') as model_file:
    loaded_model = pickle.load(model_file)

with open('count_vectorizer.pkl', 'rb') as cv_file:
    loaded_cv = pickle.load(cv_file)

# تحميل مكتبات أخرى
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')

# معالجة النصوص
stop = stopwords.words("English")
ps = WordNetLemmatizer()
punc = string.punctuation

def Process(text):
    text = text.lower()
    token = word_tokenize(text)
    process_tokens = []
    for word in token:
        if word not in punc and word not in stop:
            process_tokens.append(word)
    
    stemmed_tokens = []
    for word in process_tokens:
        stemmed_tokens.append(ps.lemmatize(word, pos="v"))
        
    return " ".join(stemmed_tokens)

# دالة التنبؤ بالنموذج
def predict_message(message, model, vectorizer=loaded_cv):
    processed_message = Process(message)
    message_vectorized = vectorizer.transform([processed_message]).toarray()
    prediction = model.predict(message_vectorized)
    return "Spam" if prediction == 0 else "Ham"

# واجهة Streamlit
st.title("نموذج تصنيف الرسائل المزعجة (Spam Detection Model)")

# مكان لإضافة صورة تعبّر عن السبام
st.image(r"Spam-Emails.png", caption="")

# مربع نص لإدخال الرسالة
message = st.text_area("أدخل الرسالة:", "")

# سايدر لعرض شرح عن رسائل السبام
st.sidebar.title("معلومات حول رسائل السبام")
st.sidebar.write("""
    رسائل السبام هي رسائل غير مرغوب فيها يتم إرسالها بشكل جماعي من قبل المهاجمين أو الشركات
    للترويج لمنتجات أو خدمات دون موافقة المرسل إليهم. يمكن أن تكون رسائل السبام ضارة لأنها قد تحتوي
    على روابط مريبة تؤدي إلى مواقع احتيالية أو تعرض جهازك للبرمجيات الخبيثة.
    
    **أضرار رسائل السبام**:
    - تعرض خصوصيتك للخطر.
    - نشر الفيروسات والبرمجيات الخبيثة.
    - إهدار وقتك ومواردك.
    - تأثير سلبي على تجربتك في الإنترنت.
""")

# زر "تحقق من الرسالة"
if st.button('تحقق من الرسالة'):
    if message:
        prediction_result = predict_message(message, loaded_model)
        st.write(f"الرسالة هي: **{prediction_result}**")
    else:
        st.write("من فضلك أدخل رسالة للتحقق منها.")
