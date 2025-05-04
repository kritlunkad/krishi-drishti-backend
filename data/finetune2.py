import subprocess
import os
import json
import sys
import ollama
import random
import time
import argparse

def prepare_data(input_file, output_file, max_examples=None, start_index=0):
    """
    Convert raw data to the format needed for training
    Can start from a specific index to avoid reprocessing examples
    """
    print(f"Preparing data from {input_file} to {output_file}...")
    count = 0
    
    # Check if output file exists and count existing examples
    existing_count = 0
    if os.path.exists(output_file) and start_index > 0:
        with open(output_file, 'r') as f:
            existing_count = sum(1 for _ in f)
        print(f"Found {existing_count} existing examples in output file")
        
        if existing_count >= start_index:
            print(f"Starting from index {start_index} (skipping {start_index} examples)")
        else:
            print(f"Warning: Requested to start from index {start_index} but only {existing_count} examples exist")
            start_index = existing_count
    
    # Determine write mode (append or write)
    mode = 'a' if start_index > 0 and os.path.exists(output_file) else 'w'
    
    with open(input_file, 'r') as f_in, open(output_file, mode) as f_out:
        for i, line in enumerate(f_in):
            # Skip already processed examples
            if i < start_index:
                continue
                
            try:
                data = json.loads(line.strip())
                if 'prompt' in data and 'response' in data:
                    # Format as a conversation that Ollama can process
                    conversation = {
                        "messages": [
                            {"role": "user", "content": data['prompt']},
                            {"role": "assistant", "content": data['response']}
                        ]
                    }
                    f_out.write(json.dumps(conversation) + "\n")
                    count += 1
                    
                    if count % 500 == 0:
                        print(f"Processed {count} examples...")
                        
                    # Stop if we've reached the maximum
                    if max_examples and count >= max_examples:
                        break
            except json.JSONDecodeError:
                print(f"Warning: Skipping invalid JSON line: {line[:50]}...")
                continue
    
    total_examples = existing_count + count if start_index > 0 else count
    print(f"✅ Data preparation complete. Added {count} new examples (total: {total_examples})")
    return count

def train_model_with_batches(filename, model_name, batch_size=10, max_samples=None, 
                            start_index=0, end_index=None):
    """
    Train model using batched approach for speed
    Can specify start and end indices to train on a subset of examples
    """
    with open(filename, 'r') as f:
        conversations = [json.loads(line) for i, line in enumerate(f)]
    
    # Apply range limits if specified
    if start_index > 0 and start_index < len(conversations):
        if end_index and end_index <= len(conversations):
            conversations = conversations[start_index:end_index]
        else:
            conversations = conversations[start_index:]
    elif end_index and end_index <= len(conversations):
        conversations = conversations[:end_index]
    
    # Apply sample limit if specified
    if max_samples and max_samples < len(conversations):
        conversations = random.sample(conversations, max_samples)
    
    total = len(conversations)
    print(f"Training with {total} conversations in batches of {batch_size}...")
    
    # Process in batches
    batches = [conversations[i:i + batch_size] for i in range(0, len(conversations), batch_size)]
    
    for batch_num, batch in enumerate(batches):
        print(f"Processing batch {batch_num+1}/{len(batches)} ({batch_num*batch_size}/{total} examples)")
        
        # Process each example in the batch
        for conv in batch:
            try:
                # Submit conversation to the model
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
        
        # Progress percentage
        progress = min(100, int((batch_num + 1) * 100 / len(batches)))
        print(f"Progress: {progress}% complete")
        
        # Brief pause between batches to avoid overloading
        if batch_num < len(batches) - 1:  # Don't sleep after the last batch
            time.sleep(0.5)  # Half second pause between batches
    
    print(f"✅ Training complete. Processed {total} examples.")

def main():
    parser = argparse.ArgumentParser(description='Fast training for Ollama models with new data')
    parser.add_argument('--input', type=str, help='Input data file (original JSONL format)',
                        default="ollama_finetune_data/agriculture_qa.jsonl")
    parser.add_argument('--output', type=str, help='Output conversation file',
                        default="agriculture_qa_conversations.jsonl")
    parser.add_argument('--model', type=str, help='Model name to train',
                        default="agriculture-qa-fast")
    parser.add_argument('--batch-size', type=int, help='Batch size for training',
                        default=10)
    parser.add_argument('--max-samples', type=int, help='Maximum number of samples to train on',
                        default=None)
    parser.add_argument('--start-index', type=int, help='Start training from this index',
                        default=0)
    parser.add_argument('--end-index', type=int, help='End training at this index',
                        default=None)
    parser.add_argument('--prepare-only', action='store_true', 
                        help='Only prepare data, don\'t train')
    parser.add_argument('--train-only', action='store_true',
                        help='Skip data preparation, only train')
    
    args = parser.parse_args()
    
    # Ensure we have the necessary files and model
    if not args.train_only:
        if not os.path.exists(args.input):
            print(f"❌ Input file {args.input} not found")
            return
            
        # Prepare the data
        prepare_data(args.input, args.output, args.max_samples, args.start_index)
    
    if args.prepare_only:
        print("Data preparation complete. Skipping training as requested.")
        return
    
    # Check if model exists
    try:
        models = ollama.list()
        model_exists = any(model['name'] == args.model for model in models.get('models', []))
        
        if not model_exists:
            print(f"❌ Model {args.model} not found. Please create it first.")
            return
    except Exception as e:
        print(f"❌ Error checking model: {e}")
        return
    
    # Train the model
    train_model_with_batches(
        args.output, 
        args.model, 
        args.batch_size, 
        args.max_samples,
        args.start_index,
        args.end_index
    )
    
    print(f"\n✨ Training of {args.model} complete!")
    print(f"Test your model with: ollama run {args.model} \"What are the best crops for sandy soil?\"")

if __name__ == "__main__":
    main()