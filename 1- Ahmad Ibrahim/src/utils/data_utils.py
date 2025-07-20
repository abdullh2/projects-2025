from PIL import Image
import torch

def load_captions(caption_file):
    vocab = ["<pad>", "<start>", "<end>"]
    captions_dict = {}
    with open(caption_file, encoding="utf-8") as f:
        for line in f:
            fname, caption = line.strip().split("|")
            tokens = caption.strip().split()
            vocab.extend(tokens)
            captions_dict[fname] = tokens
    vocab = list(set(vocab))
    return vocab, captions_dict

def extract_feature(cnn, image_path, transform, device):
    img = Image.open(image_path).convert("RGB")
    tensor = transform(img).unsqueeze(0).to(device)
    with torch.no_grad():
        feature = cnn(tensor).squeeze()
    return feature
