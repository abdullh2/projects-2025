import gradio as gr
from PIL import Image
import torch
from torchvision import models, transforms
from train_model import CaptionModel, word2idx, idx2word, device
from transformers import BlipProcessor, BlipForConditionalGeneration
# from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
from pathlib import Path

VOCAB_SIZE = len(word2idx)
EMBED_SIZE = 256
HIDDEN_SIZE = 256

transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
])

# model_name = "Helsinki-NLP/opus-mt-en-ar"
# tokenizer = AutoTokenizer.from_pretrained(model_name)
# translation_model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

# def translate_to_arabic(text):
#     encoded = tokenizer(text, return_tensors="pt")
#     generated = translation_model.generate(**encoded, max_length=200)
#     translated = tokenizer.decode(generated[0], skip_special_tokens=True)
#     return translated

cnn = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)
cnn = torch.nn.Sequential(*list(cnn.children())[:-1]).to(device)
cnn.eval()

caption_model = CaptionModel(VOCAB_SIZE, EMBED_SIZE, HIDDEN_SIZE).to(device)
BASE_DIR = Path(__file__).resolve().parent.parent
model_path = BASE_DIR / "models" / "caption_model.pth"
caption_model.load_state_dict(torch.load(model_path, map_location=device))
caption_model.eval()

blip_processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
blip_model = BlipForConditionalGeneration.from_pretrained(
    "Salesforce/blip-image-captioning-base"
).to(device)

features_tensor = torch.load(BASE_DIR / "models" / "features.pt").to(device)
with open(BASE_DIR / "models" / "filenames.txt", encoding="utf-8") as f:
    filenames = [line.strip() for line in f]

def generate_caption(image):
    blip_inputs = blip_processor(images=image, return_tensors="pt").to(device)
    with torch.no_grad():
        blip_output = blip_model.generate(**blip_inputs)
    description_blip_en = blip_processor.decode(blip_output[0], skip_special_tokens=True)
    description_blip = description_blip_en
    image_resnet = image.convert("RGB")
    tensor = transform(image_resnet).unsqueeze(0).to(device)
    with torch.no_grad():
        feature = cnn(tensor).squeeze()

    similarities = torch.nn.functional.cosine_similarity(
        feature.unsqueeze(0), features_tensor
    )
    best_idx = similarities.argmax().item()
    best_similarity = similarities[best_idx].item()

    if best_similarity > 0.96:
        inputs = torch.tensor([[word2idx["<start>"]]], device=device)
        result = []
        for _ in range(20):
            outputs = caption_model(feature.unsqueeze(0), inputs)
            _, predicted = outputs[:, -1, :].max(1)
            word = idx2word[predicted.item()]
            if word == "<end>":
                break
            result.append(word)
            inputs = torch.cat([inputs, predicted.unsqueeze(0)], dim=1)
        description_custom = " ".join(result)

        final_description = (
            f"A matching photo of the coach({filenames[best_idx]})\n\n"
            f"Description :\n{description_custom}\n\n"
            f"Public Description :\n{description_blip}"
        )
    else:
        final_description = f"Public Description :\n{description_blip}"

    return final_description

interface = gr.Interface(
    fn=generate_caption,
    inputs=gr.Image(type="pil"),
    outputs="text",
    title="Generate image description",
    description="Upload a photo, and it will produce a description using your trained model"
)

if __name__ == "__main__":
    interface.launch()
