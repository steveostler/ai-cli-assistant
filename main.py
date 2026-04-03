import os
from openai import OpenAI
from dotenv import load_dotenv
from datetime import datetime
import json

# Load environment variables from .env file (for API key)
load_dotenv()

# Create OpenAI client using API key from environment
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def ask_ai(prompt):
    """
    Sends a prompt to the AI API and returns structured response data.
    Handles missing fields and API errors safely.
    """
    try:
        # Send request to AI model
        response = client.responses.create(model="gpt-4.1-mini", input=prompt)
        # Convert response object to dictionary for easier access
        data = response.model_dump()
        outputs = data.get("output", [])

        # Handle case where no output is returned
        if not outputs:
            return {
                "text": "No response received",
                "model": data.get("model", "Unknown"),
                "role": "unknown",
            }

        # Extract first output item
        first_item = outputs[0]
        content_blocks = first_item.get("content", [])

        # Extract text safely
        text = "No content available"
        if content_blocks:
            text = content_blocks[0].get("text", "No text found")

        return {
            "text": text,
            "model": data.get("model", "Unknown"),
            "role": first_item.get("role", "unknown"),
        }

    except Exception as e:
        # Return structured error instead of crashing
        return {"text": f"Error: {e}", "model": "unknown", "role": "error"}


def load_logs(log_file):
    """
    Loads log file safely.
    Ensures returned data is always a list (even if file is empty or malformed).
    """
    if not os.path.exists(log_file):
        return []

    with open(log_file, "r") as f:
        try:
            logs = json.load(f)

            # Ensure logs is always a list
            if isinstance(logs, dict):
                return [logs]
            if isinstance(logs, list):
                return logs
            return []

        except json.JSONDecodeError:
            return []


def search_logs(logs, keyword):
    """
    Searches stored logs for prompts containing a keyword.
    Returns matching entries.
    """
    matches = []

    for entry in logs:
        prompt = entry.get("prompt", "")
        if keyword.lower() in prompt.lower():
            matches.append(entry)

    return matches

def print_last_conversations(logs, count=3):
    """
    Displays the last N conversations from the logs.
    Includes timestamp, prompt, response, model, and role.
    """
    if not logs:
        print("No previous conversations today.\n")
        return

    print(f"\nLast {count} conversations:")
    print("-" * 30)

    for entry in logs[-count:]:
        print(f"Time:     {entry.get('timestamp', 'Unknown')}")
        print(f"Model:    {entry.get('model', 'Unknown')}")
        print(f"Role:     {entry.get('role', 'Unknown')}")
        print(f"Prompt:   {entry.get('prompt', '')}")
        print(f"Response: {entry.get('response', '')}")
        print("-" * 30)

    print()


# --- Log setup ---
# Create a date-based filename (one log file per day)
today = datetime.now().strftime("%Y_%m_%d")
log_file = f"chatlog_{today}.json"

# Load existing logs
logs = load_logs(log_file)

print_last_conversations(logs, 5)

#  ---Main loop---

while True:
    prompt = input("Ask a question (or type 'exit'): ")

    # Prevent empty input
    if not prompt.strip():
        print("Please enter a question.")
        continue

    # Exit condition   
    if prompt.lower() == "exit":
        print("Goodbye!")
        break

    # Handle search command (does not call AI)
    if prompt.lower().startswith("search "):
        keyword = prompt[7:].strip()

        if not keyword:
            print("Please enter a keyword to search for.")
            continue

        matches = search_logs(logs, keyword)

        if matches:
            print(f"\nFound {len(matches)} matching prompt(s):")
            print("-" * 30)
            for entry in matches:
                print(f"Time:     {entry.get('timestamp', 'Unknown')}")
                print(f"Prompt:   {entry.get('prompt', '')}")
                print(f"Response: {entry.get('response', '')}")
                print("-" * 30)
            print()
        else:
            print(f"No prompts found containing '{keyword}'.\n")

        continue

    # Call AI and get response
    result = ask_ai(prompt)
    timestamp = datetime.now().strftime("%H:%M:%S")

    # Display output to user
    print("-" * 30)
    print(f"Time:     {timestamp}")
    print(f"Model:    {result['model']}")
    print(f"Role:     {result['role']}")
    print(f"Prompt:   {prompt}")
    print(f"Response: {result['text']}")
    print("-" * 30)
    print()

    # Create log entry
    conversation = {
        "timestamp": timestamp,
        "role": result["role"],
        "model": result["model"],
        "prompt": prompt,
        "response": result["text"],
    }

    # Add new conversation to logs
    logs.append(conversation)

    # Save updated logs to file
    with open(log_file, "w") as f:
        json.dump(logs, f, indent=4)

    # Show total entries for today
    print(f"Log entries saved today: {len(logs)}")
    print()
