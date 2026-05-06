import json
import torch
from transformers import BertTokenizer, BertForSequenceClassification
from sklearn.preprocessing import LabelEncoder
from torch.utils.data import Dataset, DataLoader

# Load data
with open("intents.json") as f:
    data = json.load(f)

texts = [item["text"] for item in data]
labels = [item["label"] for item in data]

# Encode labels
le = LabelEncoder()
labels_encoded = le.fit_transform(labels)

# Tokenizer
tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")

class IntentDataset(Dataset):
    def __init__(self, texts, labels):
        self.encodings = tokenizer(texts, truncation=True, padding=True)
        self.labels = labels

    def __getitem__(self, idx):
        item = {key: torch.tensor(val[idx]) for key, val in self.encodings.items()}
        item["labels"] = torch.tensor(self.labels[idx])
        return item

    def __len__(self):
        return len(self.labels)

dataset = IntentDataset(texts, labels_encoded)
loader = DataLoader(dataset, batch_size=8, shuffle=True)

# Model
model = BertForSequenceClassification.from_pretrained(
    "bert-base-uncased",
    num_labels=len(le.classes_)
)

optimizer = torch.optim.AdamW(model.parameters(), lr=2e-5)

# Training loop
model.train()
for epoch in range(8):
    for batch in loader:
        outputs = model(**batch)
        loss = outputs.loss

        loss.backward()
        optimizer.step()
        optimizer.zero_grad()

    print(f"Epoch {epoch} done")

# Save model
model.save_pretrained("model")
tokenizer.save_pretrained("model")

# Save label encoder
import pickle
with open("model/label_encoder.pkl", "wb") as f:
    pickle.dump(le, f)