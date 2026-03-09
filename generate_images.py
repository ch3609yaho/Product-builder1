
import os
import requests
import json
import time
import subprocess
import base64

# Vertex AI Configuration
PROJECT_ID = "innate-might-488304-n6"
LOCATION = "us-central1"

def get_access_token():
    try:
        # Try to get token from gcloud
        result = subprocess.run(['gcloud', 'auth', 'print-access-token'], capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            print(f"Error getting token: {result.stderr}")
            return None
    except Exception as e:
        print(f"Exception getting token: {e}")
        return None

def generate_fashion_image(age, gender, occasion, weather, filename, token):
    url = f"https://{LOCATION}-aiplatform.googleapis.com/v1/projects/{PROJECT_ID}/locations/{LOCATION}/publishers/google/models/imagen-3.0-generate-001:predict"
    
    prompt = f"Full body fashion portrait of a stylish {age} Korean {gender} wearing a {occasion} outfit suitable for {weather} weather. Head to toe visible, professional lighting, portrait orientation, 9:16 aspect ratio, cinematic quality, high resolution."
    
    payload = {
        "instances": [
            {
                "prompt": prompt
            }
        ],
        "parameters": {
            "sampleCount": 1,
            "aspectRatio": "9:16",
            "outputMimeType": "image/png"
        }
    }
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    print(f"Generating image for {age} {gender} - {occasion} ({weather})...")
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            result = response.json()
            image_b64 = result['predictions'][0]['bytesBase64Encoded']
            
            with open(filename, "wb") as f:
                f.write(base64.b64decode(image_b64))
            print(f"Successfully saved to {filename}")
            return True
        else:
            print(f"Failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"Error: {e}")
        return False

# Mapping of what needs to be generated
tasks = [
    ("20s", "women", "Sports", "Hot", "korean_20s_women_sports_hot.png"),
    ("20s", "men", "University", "Hot", "korean_20s_men_uni_hot.png"),
    ("30s", "men", "Social", "Sunny", "korean_30s_men_social_sunny.png"),
    ("40s", "women", "Premium", "Sunny", "korean_40s_women_premium_sunny.png"),
    ("40s", "men", "Leisure", "Chilly", "korean_40s_men_leisure_chilly.png"),
    ("50s", "men", "Classic", "Sunny", "korean_50s_men_classic_sunny.png"),
    ("50s", "women", "Travel", "Hot", "korean_50s_women_travel_hot.png"),
    ("50s", "women", "Health", "Sunny", "korean_50s_women_health_sunny.png"),
]

if __name__ == "__main__":
    token = get_access_token()
    if token:
        for age, gender, occ, weather, fname in tasks:
            generate_fashion_image(age, gender, occ, weather, fname, token)
            time.sleep(2) # Avoid rate limiting
    else:
        print("Could not obtain access token. Please run 'gcloud auth login' and try again.")
