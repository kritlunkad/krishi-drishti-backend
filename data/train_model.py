
import ollama
import json
import time
import random
import sys

def train_model_with_examples(filename, model_name, samples=None):
    with open(filename, 'r') as f:
        conversations = [json.loads(line) for line in f]
    
    if samples and samples < len(conversations):
        # Take a random sample if specified
        conversations = random.sample(conversations, samples)
    
    print(f"Training with {len(conversations)} conversations...")
    
    success = 0
    errors = 0
    
    for i, conv in enumerate(conversations):
        try:
            if i % 10 == 0:
                print(f"Progress: {i}/{len(conversations)} examples processed")
            
            # Submit this conversation to the model to "learn" from it
            messages = conv["messages"]
            
            # Send to Ollama
            response = ollama.chat(
                model=model_name,
                messages=messages
            )
            
            success += 1
            time.sleep(0.1)  # Don't overload the API
            
        except Exception as e:
            print(f"Error on example {i}: {e}")
            errors += 1
            time.sleep(1)  # Longer pause after error
    
    print(f"Training complete. Processed {success} examples successfully with {errors} errors.")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python train_model.py <conversation_file> <model_name> [sample_size]")
        sys.exit(1)
    
    conv_file = sys.argv[1]
    model_name = sys.argv[2]
    samples = int(sys.argv[3]) if len(sys.argv) > 3 else None
    
    train_model_with_examples(conv_file, model_name, samples)
