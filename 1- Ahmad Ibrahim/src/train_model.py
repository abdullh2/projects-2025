import torch
import torch.nn as nn
from torchvision import models, transforms
from pathlib import Path

from models.caption_model import CaptionModel
from utils.data_utils import load_captions, extract_feature

BASE_DIR = Path(__file__).resolve().parent.parent
IMAGE_DIR = BASE_DIR / "data" / "images"
CAPTION_FILE = BASE_DIR / "data" / "captions.txt"
MODEL_DIR = BASE_DIR / "models"
MODEL_DIR.mkdir(parents=True, exist_ok=True)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# تحميل التعليقات وبناء القاموس
vocab, captions_dict = load_captions(CAPTION_FILE)
word2idx = {w: i for i, w in enumerate(vocab)}
idx2word = {i: w for w, i in word2idx.items()}

VOCAB_SIZE = len(vocab)
EMBED_SIZE = 256
HIDDEN_SIZE = 256
NUM_EPOCHS = 100

transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
])

cnn = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)
cnn = nn.Sequential(*list(cnn.children())[:-1]).to(device)
cnn.eval()

features_list = []
captions_list = []

# استخراج الميزات والتعليقات
for fname, tokens in captions_dict.items():
    feature = extract_feature(cnn, IMAGE_DIR / fname, transform, device)
    features_list.append(feature)
    caption_idx = [word2idx["<start>"]] + [word2idx[t] for t in tokens] + [word2idx["<end>"]]
    captions_list.append(torch.tensor(caption_idx, dtype=torch.long))

model = CaptionModel(VOCAB_SIZE, EMBED_SIZE, HIDDEN_SIZE).to(device)
criterion = nn.CrossEntropyLoss(ignore_index=word2idx["<pad>"])
optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

# التدريب
for epoch in range(NUM_EPOCHS):
    total_loss = 0
    for feature, caption in zip(features_list, captions_list):
        feature = feature.unsqueeze(0)
        inputs = caption[:-1].unsqueeze(0)
        targets = caption[1:].unsqueeze(0)

        outputs = model(feature, inputs)
        outputs = outputs[:, 1:, :].reshape(-1, VOCAB_SIZE)
        targets = targets.reshape(-1)

        loss = criterion(outputs, targets)

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        total_loss += loss.item()

    if (epoch + 1) % 10 == 0:
        torch.save(model.state_dict(), MODEL_DIR / f"caption_model_epoch{epoch+1}.pth")
        print(f" تم حفظ Checkpoint في epoch {epoch+1}")

    print(f"Epoch [{epoch+1}/{NUM_EPOCHS}], Loss: {total_loss:.4f}")

# حفظ الميزات للأستخدام لاحقًا
features_tensor = torch.stack(features_list)
torch.save(features_tensor, MODEL_DIR / "features.pt")

filenames = list(captions_dict.keys())
with open(MODEL_DIR / "filenames.txt", "w", encoding="utf-8") as f:
    for name in filenames:
        f.write(str(name) + "\n")

torch.save(model.state_dict(), MODEL_DIR / "caption_model.pth")
print(" The finished form has been saved!")
