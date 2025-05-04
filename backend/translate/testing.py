import requests

BASE_URL = "http://127.0.0.1:8100"

def call_hindi(text, from_code="en"):
    payload = {"text": text, "from_code": from_code, "to_code": "hi"}
    response = requests.post(f"{BASE_URL}/hindi", json=payload)
    try:
        print("Hindi:", response.json())
    except ValueError:
        print("Hindi response not JSON:", response.text)

def call_tamil(text, from_code="en"):
    payload = {"text": text, "from_code": from_code, "to_code": "ta"}
    response = requests.post(f"{BASE_URL}/tamil", json=payload)
    try:
        print("Tamil:", response.json())
    except ValueError:
        print("Tamil response not JSON:", response.text)

def call_telugu(text, from_code="en"):
    payload = {"text": text, "from_code": from_code, "to_code": "te"}
    response = requests.post(f"{BASE_URL}/telugu", json=payload)
    try:
        print("Telugu:", response.json())
    except ValueError:
        print("Telugu response not JSON:", response.text)

def call_kannada(text, from_code="en"):
    payload = {"text": text, "from_code": from_code, "to_code": "kn"}
    response = requests.post(f"{BASE_URL}/kannada", json=payload)
    try:
        print("Kannada:", response.json())
    except ValueError:
        print("Kannada response not JSON:", response.text)

if __name__ == "__main__":
    sample_text = "Irrigation is the process of supplying water to plants."
    call_hindi(sample_text)
    call_tamil(sample_text)
    call_telugu(sample_text)
    call_kannada(sample_text)