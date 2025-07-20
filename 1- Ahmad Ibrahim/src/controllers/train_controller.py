import torch

def train_model(
    model,
    features_list,
    captions_list,
    word2idx,
    num_epochs,
    save_dir,
    device
):
    VOCAB_SIZE = len(word2idx)
    criterion = torch.nn.CrossEntropyLoss(ignore_index=word2idx["<pad>"])
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

    for epoch in range(num_epochs):
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
            torch.save(model.state_dict(), save_dir / f"caption_model_epoch{epoch+1}.pth")
            print(f" تم حفظ Checkpoint في epoch {epoch+1}")

        print(f"Epoch [{epoch+1}/{num_epochs}], Loss: {total_loss:.4f}")

    torch.save(model.state_dict(), save_dir / "caption_model.pth")
    print(" تم حفظ النموذج النهائي!")

    return model
