from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch
from langdetect import detect
from concurrent.futures import ThreadPoolExecutor

MODEL_EN_PATH = "models/bart-large-cnn"
MODEL_AR_PATH = "models/mbart-arabic-summarizer"

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"الجهاز المستخدم: {device}")

print("تحميل النموذج الإنجليزي (FP16)...")
tokenizer_en = AutoTokenizer.from_pretrained(f"{MODEL_EN_PATH}/tokenizer")
model_en = AutoModelForSeq2SeqLM.from_pretrained(
    f"{MODEL_EN_PATH}/model",
    torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32
).to(device)
model_en.eval()

print("تحميل النموذج العربي (FP16)...")
tokenizer_ar = AutoTokenizer.from_pretrained(f"{MODEL_AR_PATH}/tokenizer")
model_ar = AutoModelForSeq2SeqLM.from_pretrained(
    f"{MODEL_AR_PATH}/model",
    torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32
).to(device)
model_ar.eval()

print("النماذج جاهزة للتلخيص")


def summarize_single_chunk(text: str, max_input_length=1024, max_summary_length=150) -> str:
    """
    """
    lang = detect(text)
    tokenizer = tokenizer_ar if lang == 'ar' else tokenizer_en
    model = model_ar if lang == 'ar' else model_en

    inputs = tokenizer(text, max_length=max_input_length, truncation=True, return_tensors="pt").to(device)

    with torch.no_grad():
        summary_ids = model.generate(
            inputs["input_ids"],
            max_length=max_summary_length,
            min_length=30,
            length_penalty=1.0,
            num_beams=2,
            early_stopping=True
        )

    return tokenizer.decode(summary_ids[0], skip_special_tokens=True)


def chunk_text(text, max_words=800):

    words = text.split()
    return [' '.join(words[i:i + max_words]) for i in range(0, len(words), max_words)]


def summarize_long_text(text: str, max_input_length=1024, max_summary_length=150) -> str:

    chunks = chunk_text(text)

    with ThreadPoolExecutor() as executor:
        summaries = list(executor.map(
            lambda chunk: summarize_single_chunk(chunk, max_input_length, max_summary_length),
            chunks
        ))

    return " ".join(summaries)
