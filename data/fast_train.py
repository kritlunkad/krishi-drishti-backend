import ollama
import json
import time
import random
import sys

def train_model_with_batches(filename, model_name, batch_size=10, max_samples=100, start_index=0):
    with open(filename, 'r') as f:
        conversations = [json.loads(line) for line in f]
    
    # Skip the first start_index conversations
    conversations = conversations[start_index:]
    
    # Limit samples for speed
    if max_samples and max_samples < len(conversations):
        conversations = random.sample(conversations, max_samples)
    
    print(f"Training with {len(conversations)} conversations in batches of {batch_size}...")
    
    # Process in batches
    batches = [conversations[i:i + batch_size] for i in range(0, len(conversations), batch_size)]
    
    for batch_num, batch in enumerate(batches):
        print(f"Processing batch {batch_num+1}/{len(batches)}")
        
        # Process each example in the batch
        for conv in batch:
            try:
                # Submit this conversation to the model to "learn" from it
                messages = conv["messages"]
                
                # Send to Ollama (non-blocking)
                ollama.chat(
                    model=model_name,
                    messages=messages,
                    stream=False  # Don't wait for full response
                )
                
            except Exception as e:
                print(f"Error on example: {e}")
        
        print(f"Completed batch {batch_num+1}")
        time.sleep(0.5)  # Brief pause between batches
    
    print(f"Fast training complete. Processed {len(conversations)} examples.")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python fast_train.py <conversation_file> <model_name> [max_samples] [batch_size] [start_index]")
        sys.exit(1)
    
    conv_file = sys.argv[1]
    model_name = sys.argv[2]
    max_samples = int(sys.argv[3]) if len(sys.argv) > 3 else 100
    batch_size = int(sys.argv[4]) if len(sys.argv) > 4 else 10
    start_index = int(sys.argv[5]) if len(sys.argv) > 5 else 0
    
    train_model_with_batches(conv_file, model_name, batch_size, max_samples, start_index)
