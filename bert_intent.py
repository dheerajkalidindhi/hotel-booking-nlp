import torch
import pickle
from transformers import BertTokenizer, BertForSequenceClassification

# Load model
model = BertForSequenceClassification.from_pretrained("./model")
tokenizer = BertTokenizer.from_pretrained("./model")
# Load label encoder
with open("model/label_encoder.pkl", "rb") as f:
    le = pickle.load(f)

model.eval()


def predict_intent(text: str):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True)

    with torch.no_grad():
        outputs = model(**inputs)

    logits = outputs.logits
    probs = torch.softmax(logits, dim=1)

    confidence, predicted_class_id = torch.max(probs, dim=1)

    confidence = confidence.item()
    intent = le.inverse_transform([predicted_class_id.item()])[0]

    return intent, confidence