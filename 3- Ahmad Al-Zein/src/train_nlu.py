# train_nlu.py
import spacy
import json
import random
from spacy.tokens import DocBin
from spacy.training import Example
import os # تم الإضافة

# --- الخطوة 0: تفعيل دعم الـ GPU ---
# تأكد من تثبيت المكتبات الصحيحة: pip install -U spacy[cuda11x] cupy
# قم بإلغاء التعليق عن السطر التالي لتفعيل الـ GPU
# spacy.require_gpu() 
# print("GPU Activated:", spacy.prefer_gpu())


def load_data(file_path):
    """تحميل البيانات من ملف JSON وتحويلها لصيغة spaCy"""
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    training_data = []
    for intent_data in data['intents']:
        intent_name = intent_data['intent']
        for text in intent_data['texts']:
            entities = []
            for entity in intent_data['entities']:
                if entity['text'] in text:
                    start = text.find(entity['text'])
                    end = start + len(entity['text'])
                    entities.append((start, end, entity['label']))
            
            # إضافة القصد إلى فئات النص
            cats = {i['intent']: 0 for i in data['intents']}
            cats[intent_name] = 1
            
            training_data.append({"text": text, "entities": entities, "cats": cats})
            
    return training_data

def train_spacy(data, iterations=20, model_name="nlu_model_ar"):
    """تدريب نموذج spaCy وحفظه"""
    # إنشاء نموذج فارغ باللغة العربية
    nlp = spacy.blank("ar")

    # إضافة مصنف النص (Text Classifier) إلى الـ pipeline
    if "textcat" not in nlp.pipe_names:
        textcat = nlp.add_pipe("textcat", last=True)
    else:
        textcat = nlp.get_pipe("textcat")

    # إضافة الكيانات (NER) إلى الـ pipeline
    if "ner" not in nlp.pipe_names:
        ner = nlp.add_pipe("ner", last=True)
    else:
        ner = nlp.get_pipe("ner")

    # إضافة أسماء المقاصد (intents) والكيانات (entities) إلى المكونات
    all_intents = {cat for item in data for cat in item['cats']}
    for intent in all_intents:
        textcat.add_label(intent)
        
    all_labels = {ent[2] for item in data for ent in item['entities']}
    for label in all_labels:
        ner.add_label(label)

    # بدء التدريب
    optimizer = nlp.begin_training()
    print("--- بدء التدريب ---")
    for itn in range(iterations):
        random.shuffle(data)
        losses = {}
        for item in data:
            doc = nlp.make_doc(item['text'])
            example = Example.from_dict(doc, {"entities": item['entities'], "cats": item['cats']})
            nlp.update([example], drop=0.35, losses=losses, sgd=optimizer)
        print(f"التكرار {itn + 1}/{iterations}, الخسارة: {losses}")

    # حفظ النموذج المدرب إلى مجلد
    # تم تحديث المسار ليشير إلى مجلد nlu_model_ar داخل مجلد data
    model_output_path = os.path.join(os.path.dirname(__file__), '..', 'data', model_name)
    nlp.to_disk(model_output_path)
    print(f"\n--- تم حفظ النموذج بنجاح في مجلد '{model_output_path}' ---")


if __name__ == "__main__":
    # 1. تحميل بيانات التدريب
    # تم تحديث المسار ليشير إلى training_data.json في مجلد data
    training_data = load_data(os.path.join(os.path.dirname(__file__), '..', 'data', 'training_data.json'))
    
    # 2. بدء عملية التدريب
    train_spacy(training_data)