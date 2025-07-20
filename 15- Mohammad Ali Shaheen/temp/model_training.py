from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import GaussianNB, MultinomialNB, BernoulliNB
from sklearn.metrics import accuracy_score, precision_score, f1_score, confusion_matrix
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
import pickle

# تدريب النماذج
def train_model(data, model_type='MultinomialNB'):
    # تحويل النصوص إلى تمثيل رقمي باستخدام CountVectorizer
    cv = CountVectorizer()
    x = cv.fit_transform(data['New_Text']).toarray()
    y = data.Target.values

    # تقسيم البيانات إلى تدريب واختبار
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=40)

    if model_type == 'GaussianNB':
        model = GaussianNB()
    elif model_type == 'MultinomialNB':
        model = MultinomialNB()
    else:
        model = BernoulliNB()

    model.fit(x_train, y_train)
    pred = model.predict(x_test)

    accuracy = accuracy_score(pred, y_test)
    precision = precision_score(pred, y_test)
    f1 = f1_score(pred, y_test)
    cm = confusion_matrix(pred, y_test)

    print(f"Accuracy: {accuracy}, Precision: {precision}, F1 Score: {f1}")
    print("Confusion Matrix:")
    print(cm)

    # حفظ النموذج بعد تدريبه
    with open(f'{model_type.lower()}_model.pkl', 'wb') as file:
        pickle.dump(model, file)
    
    # حفظ CountVectorizer
    with open('count_vectorizer.pkl', 'wb') as file:
        pickle.dump(cv, file)

    print(f"Model and CountVectorizer saved as {model_type.lower()}_model.pkl")

    return model, cv
