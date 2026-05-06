from db import run_query
from e5_intent import predict_intent_e5
from nlp import extract_entities

def format_output(result, mode="text"):
    if not result:
        return "No results found."

    # Handle error response
    if isinstance(result, dict) and "error" in result:
        return f"Error: {result['error']}"

    # If result is list of dicts
    if isinstance(result, list) and isinstance(result[0], dict):

        if mode == "json":
            return result

        elif mode == "table":
            from tabulate import tabulate
            return tabulate(result, headers="keys", tablefmt="grid")

        else:
            output = []
            for row in result:
                line = ", ".join(f"{k}: {v}" for k, v in row.items())
                output.append(line)
            return "\n".join(output)

    return str(result)


# ===== LOOP =====

while True:
    user_query = input("\nAsk your question (type 'exit' to quit): ").lower().strip()

    if user_query in ["exit", "quit"]:
        print("Exiting...")
        break

    # Step 1: Intent
    intent, confidence = predict_intent_e5(user_query)

    print("Intent:", intent, "| Confidence:", round(confidence, 2))

    # Step 2: Extract entities
    entities = extract_entities(user_query)
    print("Entities:", entities)

    # Step 3: Handle low confidence (DON’T EXIT)
    if confidence < 0.5:
        print("⚠️ Low confidence, trying best guess...")

    # Step 4: Validate (DON’T EXIT)
    if intent == "bookings_by_city" and not entities.get("city"):
        print("⚠️ Missing city, showing all bookings instead.")

    elif intent == "bookings_by_user" and not entities.get("user_name"):
        print("⚠️ Missing user, showing all bookings instead.")

    # Step 5: Run query safely
    try:
        result = run_query(intent, entities)
    except Exception as e:
        print("Error executing query:", e)
        continue

    # Step 6: Output
    print("\nResult:\n")
    print(format_output(result, mode="text"))