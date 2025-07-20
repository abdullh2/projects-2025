from fastapi import FastAPI
from pydantic import BaseModel
from transformers import pipeline
from arabert.preprocess import ArabertPreprocessor
from langdetect import detect

app = FastAPI()

arabert_prep = ArabertPreprocessor(model_name="araelectra-base-discriminator")
arabic_pipeline = pipeline(
    "question-answering",
    model="ZeyadAhmed/AraElectra-Arabic-SQuADv2-QA",
    tokenizer="ZeyadAhmed/AraElectra-Arabic-SQuADv2-QA"
)

english_pipeline = pipeline(
    "question-answering",
    model="distilbert-base-uncased-distilled-squad",
    tokenizer="distilbert-base-uncased-distilled-squad"
)

class QARequest(BaseModel):
    context: str
    question: str

@app.post("/qa")
def answer_qa(request: QARequest):
    try:
        # نكتشف اللغة من السؤال أو السياق (حسب الأفضلية)
        detected_lang = detect(request.question + " " + request.context)

        if detected_lang == "ar":
            context_processed = arabert_prep.preprocess(request.context)
            question_processed = arabert_prep.preprocess(request.question)
            result = arabic_pipeline({
                "context": context_processed,
                "question": question_processed
            })
        elif detected_lang == "en":
            result = english_pipeline({
                "context": request.context,
                "question": request.question
            })
        else:
            return {"error": f"Unsupported language: {detected_lang}"}

        return {"answer": result}

    except Exception as e:
        return {"error": str(e)}
