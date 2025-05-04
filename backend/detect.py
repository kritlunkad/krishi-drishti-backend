import argparse
from PIL import Image
import torch
import torch.nn.functional as F
from transformers import AutoImageProcessor, AutoModelForImageClassification
import os
from test_hindi import get_translated_text_hindi

def load_model_and_processor(model_name):
    """Load the model and processor from Hugging Face."""
    try:
        processor = AutoImageProcessor.from_pretrained(model_name)
        model = AutoModelForImageClassification.from_pretrained(model_name)
        return processor, model
    except Exception as e:
        print(f"Error loading model or processor: {e}")
        return None, None

def preprocess_image(image_path, processor):
    """Preprocess the input image."""
    try:
        # Open and convert image to RGB
        image = Image.open(image_path).convert("RGB")
        # Process image (resize to 224x224 and normalize)
        inputs = processor(images=image, return_tensors="pt")
        return inputs
    except Exception as e:
        print(f"Error processing image: {e}")
        return None

def predict_disease(image_path, processor, model, language="en"):
    """Run inference and return the predicted disease class and confidence."""
    inputs = preprocess_image(image_path, processor)
    if inputs is None:
        return None, None
    
    # Run model inference
    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits
        # Apply softmax to get probabilities
        probs = F.softmax(logits, dim=-1)
        predicted_class_idx = probs.argmax(-1).item()
        confidence = probs[0, predicted_class_idx].item()
        predicted_class = model.config.id2label[predicted_class_idx]
        
        # Apply Hindi translation only if language is 'hi'
        if language == "hi":
            predicted_class = get_translated_text_hindi(predicted_class)
            confidence_str = get_translated_text_hindi(f"{confidence:.2%}")
        else:
            confidence_str = f"{confidence:.2%}"
        
        return predicted_class, confidence

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Classify plant disease from an image using MobileNet V2.")
    parser.add_argument("--image", type=str, help="Path to the input image")
    parser.add_argument("--language", type=str, default="en", help="Language for output (en or hi)")
    args = parser.parse_args()

    # Model name
    model_name = "linkanjarad/mobilenet_v2_1.0_224-plant-disease-identification"

    # Load model and processor
    processor, model = load_model_and_processor(model_name)
    if processor is None or model is None:
        print("Failed to load model. Exiting.")
        return

    # Get image path
    if args.image:
        image_path = args.image
    else:
        image_path = input("Enter the path to the image: ")

    # Verify image path
    if not os.path.exists(image_path):
        print(f"Image file {image_path} does not exist.")
        return

    # Predict disease
    predicted_class, confidence = predict_disease(image_path, processor, model, args.language)
    if predicted_class and confidence is not None:
        print(f"Predicted plant disease: {predicted_class}")
        print(f"Confidence level: {confidence}")
    else:
        print("Failed to predict disease.")

if __name__ == "__main__":
    main()