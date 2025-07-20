import torch
import torch.nn as nn

class CaptionModel(nn.Module):
    def __init__(self, vocab_size, embed_size, hidden_size):
        super().__init__()
        self.embed = nn.Embedding(vocab_size, embed_size)
        self.feature_proj = nn.Linear(512, embed_size)
        self.lstm = nn.LSTM(embed_size, hidden_size, batch_first=True)
        self.fc = nn.Linear(hidden_size, vocab_size)

    def forward(self, features, captions):
        projected_features = self.feature_proj(features).unsqueeze(1)
        embeddings = self.embed(captions)
        embeddings = torch.cat((projected_features, embeddings), 1)
        hiddens, _ = self.lstm(embeddings)
        outputs = self.fc(hiddens)
        return outputs
