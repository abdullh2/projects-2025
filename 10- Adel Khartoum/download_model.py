from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

model_id_en = "facebook/bart-large-cnn"
local_dir_en = "models/bart-large-cnn"

model_id_ar = "karimraouf/mbart-arabic-summarizer"
local_dir_ar = "models/mbart-arabic-summarizer"

print("تحميل BART الإنجليزي...")
tokenizer_en = AutoTokenizer.from_pretrained(model_id_en)
model_en = AutoModelForSeq2SeqLM.from_pretrained(model_id_en)
tokenizer_en.save_pretrained(f"{local_dir_en}/tokenizer")
model_en.save_pretrained(f"{local_dir_en}/model")
print("تم حفظ bart-large-cnn في:", local_dir_en)

print("تحميل mBART العربي...")
tokenizer_ar = AutoTokenizer.from_pretrained(model_id_ar)
model_ar = AutoModelForSeq2SeqLM.from_pretrained(model_id_ar)
tokenizer_ar.save_pretrained(f"{local_dir_ar}/tokenizer")
model_ar.save_pretrained(f"{local_dir_ar}/model")
print("تم حفظ mbart-arabic-summarizer في:", local_dir_ar)
