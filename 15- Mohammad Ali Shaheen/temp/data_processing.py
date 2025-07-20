import pandas as pd
import nltk
import string
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

# تحميل مكتبة NLTK والبيانات المطلوبة
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')

# تحميل البيانات
def load_data(file_path='spam.csv'):
    data = pd.read_csv(file_path, encoding='latin1')
    return data

# معالجة النصوص
def clean_data(data):
    data = data.drop(columns=['Unnamed: 2', 'Unnamed: 3', 'Unnamed: 4'])
    data = data.rename(columns={'v1': 'Target', 'v2': 'Text'})
    data = data.drop_duplicates(keep='first')

    data['Target'].replace({'ham': 1, 'spam': 0}, inplace=True)

    return data


# تنظيف النصوص
def process_text(text):
    punc = string.punctuation
    stop = stopwords.words("english")
    ps = WordNetLemmatizer()
    
    text = text.lower()
    token = nltk.word_tokenize(text)
    process_tokens = [word for word in token if word not in punc and word not in stop]
    
    stemmed_tokens = [ps.lemmatize(word, pos="v") for word in process_tokens]
    
    return " ".join(stemmed_tokens)

def preprocess_data(data):
    data['New_Text'] = data['Text'].apply(process_text)
    return data
