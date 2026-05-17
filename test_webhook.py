import requests
import json
import time

def simulate_webhook():
    url = "http://127.0.0.1:8000/webhook"
    
    # Simulated GitHub push event payload
    payload = {
        "ref": "refs/heads/main",
        "modified_file": "sample.cbl",
        "pusher": {
            "name": "legacy-dev"
        }
    }
    
    headers = {"Content-Type": "application/json"}
    
    print(f"Sending mock GitHub Push event to {url}...")
    try:
        start_time = time.time()
        response = requests.post(url, json=payload, headers=headers)
        end_time = time.time()
        
        print(f"Response ({end_time - start_time:.2f}s): {response.status_code}")
        print(json.dumps(response.json(), indent=2))
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the bot server. Make sure it is running via `uvicorn bot:app`.")

if __name__ == "__main__":
    simulate_webhook()
