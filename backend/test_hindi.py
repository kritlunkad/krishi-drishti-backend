import requests
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_translated_text_hindi(text, from_code="en", to_code="hi"):
    url = "http://localhost:8100/hindi"
    payload = {
        "text": text,
        "from_code": from_code,
        "to_code": to_code
    }
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json().get("translated_text", text)
    except requests.exceptions.ConnectionError as e:
        logger.error(f"Failed to connect to translation service at {url}: {str(e)}")
        return text
    except requests.exceptions.RequestException as e:
        logger.error(f"Error during Hindi translation request: {str(e)}")
        return text

def get_translated_text_english(text, from_code="hi", to_code="en"):
    url = "http://localhost:8100/english"
    payload = {
        "text": text,
        "from_code": from_code,
        "to_code": to_code
    }
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json().get("translated_text", text)
    except requests.exceptions.ConnectionError as e:
        logger.error(f"Failed to connect to translation service at {url}: {str(e)}")
        return text
    except requests.exceptions.RequestException as e:
        logger.error(f"Error during English translation request: {str(e)}")
        return text

if __name__ == "__main__":
    text = "Irrigation is vital for crop production."
    translated = get_translated_text_hindi(text)
    print(f"English to Hindi: {translated}")

    translated = get_translated_text_english(translated)
    print(f"Hindi to English: {translated}")
    