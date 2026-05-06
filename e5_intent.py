from sentence_transformers import SentenceTransformer, util
import json

model = SentenceTransformer("intfloat/e5-small-v2")

with open("intents.json") as f:
    data = json.load(f)

texts = ["query: " + item["text"] for item in data]
labels = [item["label"] for item in data]

embeddings = model.encode(texts, convert_to_tensor=True)


def predict_intent_e5(user_query: str):
    query_embedding = model.encode("query: " + user_query, convert_to_tensor=True)

    scores = util.cos_sim(query_embedding, embeddings)[0]

    best_idx = scores.argmax().item()

    return labels[best_idx], scores[best_idx].item()