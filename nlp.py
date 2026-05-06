import spacy
import re

nlp = spacy.load("en_core_web_sm")

KNOWN_CITIES = ["hyderabad", "delhi", "mumbai", "bangalore"]

# You can expand this later
KNOWN_USERS = [
    "rahul", "amit", "sneha", "priya", "karan",
    "aarav", "siddharth", "neha", "rohan", "nikhil"
]


def extract_entities(user_query: str):
    doc = nlp(user_query)
    query_lower = user_query.lower()

    entities = {
        "city": None,
        "user_name": None,
        "start_date": None,
        "end_date": None,
        "keyword": None
    }

    # ===== spaCy extraction =====
    for ent in doc.ents:
        if ent.label_ == "GPE":
            entities["city"] = ent.text

        elif ent.label_ == "PERSON":
            entities["user_name"] = ent.text

        elif ent.label_ == "DATE":
            # simple handling (can improve later)
            if not entities["start_date"]:
                entities["start_date"] = ent.text
            else:
                entities["end_date"] = ent.text

    # ===== fallback city detection =====
    for city in KNOWN_CITIES:
        if city in query_lower:
            entities["city"] = city.capitalize()

    # ===== fallback user detection =====
    for user in KNOWN_USERS:
        if user in query_lower:
            entities["user_name"] = user.capitalize()

    # ===== keyword extraction (IMPORTANT) =====
    # for queries like: "reviews with clean"
    match = re.search(r"(clean|food|service|bad|good|dirty)", query_lower)
    if match:
        entities["keyword"] = match.group(1)

    # ===== simple date pattern =====
    date_match = re.findall(r"\d{4}-\d{2}-\d{2}", user_query)
    if len(date_match) == 2:
        entities["start_date"] = date_match[0]
        entities["end_date"] = date_match[1]

    return entities