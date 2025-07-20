

# import pandas as pd
# import numpy as np
# import matplotlib.pyplot as plt
# import seaborn as sns
# import nltk

# # تحميل مكتبة NLTK والبيانات المطلوبة
# nltk.download('punkt_tab')
# nltk.download('wordnet')

# nltk.download('stopwords')


# # تحميل البيانات المطلوبة

# nltk.download('punkt')


# # الآن استخدم stopwords بعد تحميل البيانات
# from nltk.corpus import stopwords
# # stop = stopwords.words("english")

# import warnings
# warnings.filterwarnings('ignore')

# # قراءة البيانات
# data = pd.read_csv(r'spam.csv', encoding='latin1')

# # إظهار عينة من البيانات
# # data.head()
# # data.tail()
# data.sample(10)

# # معالجة البيانات المفقودة والبيانات المتكررة
# data.duplicated().sum()
# data.isna().sum()

# # تنظيف البيانات
# data = data.drop(columns=['Unnamed: 2', 'Unnamed: 3', 'Unnamed: 4'])
# data = data.rename(columns={'v1': 'Target', 'v2': 'Text'})
# data = data.drop_duplicates(keep='first')
# data.duplicated().sum()

# data.isnull().sum()
# data['Target'].replace({'ham': 1, 'spam': 0}, inplace=True)

# # رسم توزيع البيانات
# data.Target.value_counts().plot.pie(autopct='%.1f%%')

# # إضافة ميزات عدد الأحرف والكلمات والجمل
# data['Num_Char'] = data['Text'].apply(len)
# data['Word_Num'] = data['Text'].apply(lambda x: len(nltk.word_tokenize(x)))
# data['Sent_num'] = data['Text'].apply(lambda x: len(nltk.sent_tokenize(x)))

# df = data[['Target', 'Num_Char', 'Word_Num', 'Sent_num']]
# cor = df.corr()
# sns.heatmap(cor, annot=True, linewidth=1)

# # معالجة النصوص
# import string
# punc = string.punctuation
# from nltk.corpus import stopwords
# stop = stopwords.words("english")
# from nltk.stem import WordNetLemmatizer
# ps = WordNetLemmatizer()

# def Process(text):
#     text = text.lower()
#     token = nltk.word_tokenize(text)
#     process_tokens = []
#     for word in token:
#         if word not in punc and word not in stop:
#             process_tokens.append(word)
    
#     stemmed_tokens = []
#     for word in process_tokens:
#         stemmed_tokens.append(ps.lemmatize(word, pos="v"))
        
#     return " ".join(stemmed_tokens)

# # تطبيق المعالجة على النصوص
# data['New_Text'] = data['Text'].apply(Process)

# # تقسيم البيانات إلى تدريب واختبار
# from sklearn.model_selection import train_test_split
# from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer

# cv = CountVectorizer()
# tf = TfidfVectorizer()

# # تحويل النصوص إلى تمثيل رقمي باستخدام CountVectorizer
# x = cv.fit_transform(data['New_Text']).toarray()
# y = data.Target.values
# x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=40)

# # استيراد النماذج

# from sklearn.naive_bayes import GaussianNB, MultinomialNB, BernoulliNB
# from sklearn.metrics import accuracy_score, precision_score, f1_score, confusion_matrix

# gnb = GaussianNB()
# mnb = MultinomialNB()
# bnb = BernoulliNB()

# model_names = ['GaussianNB', 'MultinomialNB', 'BernoulliNB']
# score = []
# preci = []
# f1 = []

# def model(mo):
#     mo.fit(x_train, y_train)
#     pred = mo.predict(x_test)
#     score.append(accuracy_score(pred, y_test))
#     preci.append(precision_score(pred, y_test))
#     f1.append(f1_score(pred, y_test))
#     print(confusion_matrix(pred, y_test))

# # تدريب النماذج
# print(model(gnb))
# print(model(mnb))
# print(model(bnb))

# # عرض النتائج
# ndf = pd.DataFrame({'Models_name': model_names, 'Accuracy': score, 'Precision': preci, 'f1': f1})
# print(ndf)

# print("/n")
# print("/n")
# print("/n")
# print("/n")
# import pickle

# # حفظ النموذج بعد تدريبه
# with open('multinomial_nb_model.pkl', 'wb') as file:
#     pickle.dump(mnb, file)

# # حفظ CountVectorizer
# with open('count_vectorizer.pkl', 'wb') as file:
#     pickle.dump(cv, file)

# print("saving best model and CountVectorizer done")







# # للتشغيل من الكونسول 

# # دالة التنبؤ بالنموذج
# # دالة التنبؤ بالنموذج مع إضافة شرط للخروج
# def predict_message(model, message, vectorizer=cv):
#     # تطبيق المعالجة على الرسالة
#     processed_message = Process(message)
    
#     # تحويل النص المدخل إلى تمثيل رقمي باستخدام CountVectorizer أو TfidfVectorizer
#     message_vectorized = vectorizer.transform([processed_message]).toarray()

#     # التنبؤ باستخدام النموذج
#     prediction = model.predict(message_vectorized)
    
#     # إعادة التنبؤ
#     return "Spam" if prediction == 0 else "Ham"

# # اختبار إرسال رسالة لتوقع نوعها بشكل مستمر حتى يتم إدخال "exit"
# while True:
#     message = input("ENTER YOUR MESAGE OR ((( EXIT TO END ))): ")
    
#     if message.lower() == 'exit':
#         print("!!....END....!!")
#         break
    
#     selected_model = mnb  # اختر النموذج الذي تريد اختباره (ممكن تغييره إلى gnb أو bnb)

#     prediction_result = predict_message(selected_model, message)
#     print(f"THE MESSAGE IS : {prediction_result}")






















import pandas as pd
from data_processing import load_data, clean_data, preprocess_data , process_text
from model_training import train_model
import pickle

# تحميل البيانات وتحضيرها
data = load_data('spam.csv')
data = clean_data(data)
data = preprocess_data(data)

# تدريب النموذج
model, cv = train_model(data, model_type='MultinomialNB')

# # دالة التنبؤ بالنموذج
# def predict_message(model, message, vectorizer=cv):
#     # تطبيق المعالجة على الرسالة
#     processed_message = process_text(message)
    
#     # تحويل النص المدخل إلى تمثيل رقمي باستخدام CountVectorizer
#     message_vectorized = vectorizer.transform([processed_message]).toarray()

#     # التنبؤ باستخدام النموذج
#     prediction = model.predict(message_vectorized)
    
#     return "Spam" if prediction == 0 else "Ham"

# # اختبار إرسال رسالة لتوقع نوعها بشكل مستمر حتى يتم إدخال "exit"
# while True:
#     message = input("ENTER YOUR MESSAGE OR ((( EXIT TO END ))): ")
    
#     if message.lower() == 'exit':
#         print("!!....END....!!")
#         break
    
#     prediction_result = predict_message(model, message)
#     print(f"THE MESSAGE IS : {prediction_result}")
