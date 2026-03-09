
import os
import requests
import json
import time
import subprocess
import base64

# --- CONFIGURATION ---
# 1. Gemini API Key (Recommended to bypass Vertex quotas)
# Get one at: https://aistudio.google.com/
GEMINI_API_KEY = "AIzaSyAlaHER_qZEWNf1Jn9Y41E82V1JSlZ43hg"

# 2. Vertex AI Configuration (Used if GEMINI_API_KEY is not provided)
PROJECT_ID = "innate-might-488304-n6"
LOCATION = "us-central1"

def get_vertex_access_token():
    try:
        result = subprocess.run(['gcloud', 'auth', 'print-access-token'], capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            print(f"Error getting gcloud token: {result.stderr}")
            return None
    except Exception as e:
        print(f"Exception getting gcloud token: {e}")
        return None

def generate_fashion_image(age, gender, occasion, weather, filename):
    prompt = f"Professional fashion photography of a {age} Korean {gender} in {occasion} wear for {weather} weather. High quality, realistic, full body shot."
    
    payload = {
        "instances": [{"prompt": prompt}],
        "parameters": {
            "sampleCount": 1,
            "aspectRatio": "1:1",
            "outputMimeType": "image/png"
        }
    }

    if GEMINI_API_KEY and GEMINI_API_KEY != "REPLACE_WITH_YOUR_GEMINI_API_KEY":
        # Using Gemini API (Google AI Studio)
        url = f"https://generativelanguage.googleapis.com/v1beta/models/imagen-4.0-generate-001:predict?key={GEMINI_API_KEY}"
        headers = {"Content-Type": "application/json"}
        print(f"Using Gemini API for {age} {gender} - {occasion}...")
    else:
        # Using Vertex AI (Google Cloud)
        token = get_vertex_access_token()
        if not token:
            print("No Gemini API Key found and gcloud authentication failed. Please provide a key or run 'gcloud auth login'.")
            return False
        url = f"https://{LOCATION}-aiplatform.googleapis.com/v1/projects/{PROJECT_ID}/locations/{LOCATION}/publishers/google/models/imagen-3.0-generate-001:predict"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        print(f"Using Vertex AI for {age} {gender} - {occasion}...")

    try:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            result = response.json()
            if 'predictions' in result and result['predictions']:
                image_b64 = result['predictions'][0]['bytesBase64Encoded']
                with open(filename, "wb") as f:
                    f.write(base64.b64decode(image_b64))
                print(f"Successfully saved to {filename}")
                return True
            else:
                # Fallback to a very simple prompt if safety filter or error occurred
                print(f"Empty response. Retrying with simple fallback prompt...")
                payload["instances"][0]["prompt"] = f"Korean {gender} fashion, high quality."
                retry_resp = requests.post(url, headers=headers, json=payload)
                if retry_resp.status_code == 200:
                    retry_result = retry_resp.json()
                    if 'predictions' in retry_result and retry_result['predictions']:
                        image_b64 = retry_result['predictions'][0]['bytesBase64Encoded']
                        with open(filename, "wb") as f:
                            f.write(base64.b64decode(image_b64))
                        print(f"Successfully saved to {filename} (via fallback)")
                        return True
                print(f"Unexpected response structure: {json.dumps(result, indent=2)}")
                return False
        else:
            print(f"Failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"Error during generation: {e}")
        return False

# Mapping of pending images
tasks = [
    ("10s", "women", "School", "Sunny", "korean_11s_women_school_sunny.png"),
    ("10s", "men", "Casual", "Hot", "korean_10s_men_casual_hot.png"),
    ("10s", "men", "Casual", "Sunny", "korean_10s_men_casual_sunny.png"),
    ("10s", "women", "Casual", "Hot", "korean_10s_women_casual_hot.png"),
    ("20s", "men", "Date", "Sunny", "korean_20s_men_date_sunny.png"),
    ("20s", "men", "Sports", "Hot", "korean_20s_men_sports_hot.png"),
    ("20s", "women", "University", "Sunny", "korean_20s_women_uni_sunny.png"),
    ("20s", "women", "Date", "Sunny", "korean_20s_women_date_sunny.png"),
    ("30s", "men", "Date", "Sunny", "korean_30s_men_date_sunny.png"),
    ("40s", "men", "Premium", "Sunny", "korean_40s_men_premium_sunny.png"),
    ("40s", "men", "Golf", "Sunny", "korean_40s_men_golf_sunny.png"),
    ("50s", "men", "Classic", "Sunny", "korean_50s_men_classic_sunny.png"),
    ("50s", "men", "Active", "Hot", "korean_50s_men_active_hot.png"),
    ("50s", "men", "Travel", "Sunny", "korean_50s_men_travel_sunny.png"),
    ("50s", "women", "Travel", "Hot", "korean_50s_women_travel_hot.png"),
    ("50s", "women", "Health", "Sunny", "korean_50s_women_health_sunny.png"),
]

if __name__ == "__main__":
    for age, gender, occ, weather, fname in tasks:
        if not os.path.exists(fname):
            generate_fashion_image(age, gender, occ, weather, fname)
            time.sleep(1) # Mild rate limiting
        else:
            print(f"Skipping {fname}, file already exists.")
