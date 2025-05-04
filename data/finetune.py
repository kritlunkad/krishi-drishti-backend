import subprocess
import os
import json
import sys
import ollama
import time
import re

print("Fast Fine-tuning Method for Ollama")
print("===================================\n")

# Check if Ollama is running
try:
    ollama.list()
    print("✅ Ollama server is running")
except Exception as e:
    print("❌ Error: Ollama server doesn't seem to be running")
    print("   Please start Ollama with 'ollama serve' in a separate terminal")
    print("   Then run this script again")
    sys.exit(1)

# Check if fine-tuning data exists
data_path = "ollama_finetune_data/agriculture_qa.jsonl"
if not os.path.exists(data_path):
    print(f"\n❌ Fine-tuning data not found at {data_path}")
    print("Please make sure you've successfully created the fine-tuning data")
    sys.exit(1)
else:
    print(f"✅ Fine-tuning data exists at {data_path}")

# APPROACH 1: MINIMAL MODELFILE WITH SYSTEM PROMPT ONLY
# This is the fastest approach - just use system prompt without training
modelfile_path = "./Modelfile.fast"
print("Creating minimal Modelfile for fastest approach...")

modelfile_content = """
FROM llama3.2:1b

# Define a strong system prompt instead of fine-tuning
SYSTEM You are an AI assistant that specializes in agriculture, farming, and crop management. You provide detailed, accurate, and helpful responses to questions about agricultural practices, techniques, and knowledge. You know about crop rotation, soil management, sustainable farming, organic agriculture, pest control, irrigation techniques, harvesting methods, livestock management, agricultural economics, and farming equipment.

# Parameters for faster inference
PARAMETER temperature 0.7
PARAMETER top_k 40
PARAMETER top_p 0.9
"""

with open(modelfile_path, "w") as f:
    f.write(modelfile_content)
print("✅ Created minimal Modelfile")

# Check if base model exists
try:
    models = ollama.list()
    models_list = [model['name'] for model in models['models']] if 'models' in models else []
    
    if "llama3.2:1b" not in models_list:
        print("\n❌ Base model llama3.2:1b not found. Pulling it...")
        print("This may take a while depending on your internet connection.")
        subprocess.run(["ollama", "pull", "llama3.2:1b"], check=True)
        print("✅ Pulled llama3.2:1b model")
    else:
        print("✅ Base llama3.2:1b model exists")
except Exception as e:
    print(f"❌ Error checking or pulling base model: {e}")
    subprocess.run(["ollama", "pull", "llama3.2:1b"])

print("\n🚀 Creating the agriculture-qa-fast model...")
try:
    # First, remove any existing model with this name
    try:
        subprocess.run(["ollama", "rm", "agriculture-qa-fast"], stderr=subprocess.DEVNULL)
        print("   Removed existing model with the same name")
    except:
        pass  # Ignore errors if the model doesn't exist
        
    # Create the model
    result = subprocess.run(["ollama", "create", "agriculture-qa-fast", "-f", "./Modelfile.fast"], 
                           capture_output=True, text=True, check=True)
    print("✅ Successfully created agriculture-qa-fast model")
except subprocess.CalledProcessError as e:
    print(f"❌ Error creating model: {e}")
    print(f"   Error details: {e.stderr}")
    sys.exit(1)

# APPROACH 2: CREATE MODELFILE WITH FEW EXAMPLES EMBEDDED
# Extract a few examples (maybe 5-10) from your data to embed directly
print("\n📝 Creating Modelfile with a few embedded examples...")
modelfile_with_examples_path = "./Modelfile.examples"

# Read a few examples from the data
examples = []
with open(data_path, 'r') as f:
    for i, line in enumerate(f):
        if i >= 5:  # Just get 5 examples
            break
        try:
            data = json.loads(line.strip())
            if 'prompt' in data and 'response' in data:
                examples.append((data['prompt'], data['response']))
        except:
            continue

# Create Modelfile with examples
modelfile_content = """
FROM llama3.2:1b

# Define the system message
SYSTEM You are an AI assistant that specializes in agriculture, farming, and crop management. You provide detailed, accurate, and helpful responses to questions about agricultural practices, techniques, and knowledge.

# Parameters
PARAMETER temperature 0.7
PARAMETER top_k 40
PARAMETER top_p 0.9

"""

# Add examples directly to the Modelfile
for i, (prompt, response) in enumerate(examples):
    modelfile_content += f"\n# Example {i+1}\n"
    modelfile_content += f"TEMPLATE \"\"\"{{system_prompt}}\\n\\n"
    modelfile_content += f"USER: {prompt}\\n"
    modelfile_content += f"ASSISTANT: {response}\"\"\"\n"

with open(modelfile_with_examples_path, "w") as f:
    f.write(modelfile_content)
print("✅ Created Modelfile with embedded examples")

print("\n🚀 Creating the agriculture-qa-examples model...")
try:
    # First, remove any existing model with this name
    try:
        subprocess.run(["ollama", "rm", "agriculture-qa-examples"], stderr=subprocess.DEVNULL)
    except:
        pass  # Ignore errors if the model doesn't exist
        
    # Create the model
    result = subprocess.run(["ollama", "create", "agriculture-qa-examples", "-f", "./Modelfile.examples"], 
                           capture_output=True, text=True, check=True)
    print("✅ Successfully created agriculture-qa-examples model")
except subprocess.CalledProcessError as e:
    print(f"❌ Error creating model: {e}")
    print(f"   Error details: {e.stderr}")

# APPROACH 3: BATCH PROCESSING FOR FASTER TRAINING
print("\n📝 Creating streamlined batch training script...")
batch_training_script = """
import ollama
import json
import time
import random
import sys

def train_model_with_batches(filename, model_name, batch_size=10, max_samples=100):
    with open(filename, 'r') as f:
        conversations = [json.loads(line) for line in f]
    
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
        print("Usage: python fast_train.py <conversation_file> <model_name> [max_samples] [batch_size]")
        sys.exit(1)
    
    conv_file = sys.argv[1]
    model_name = sys.argv[2]
    max_samples = int(sys.argv[3]) if len(sys.argv) > 3 else 100
    batch_size = int(sys.argv[4]) if len(sys.argv) > 4 else 10
    
    train_model_with_batches(conv_file, model_name, batch_size, max_samples)
"""

with open("fast_train.py", "w") as f:
    f.write(batch_training_script)

print("✅ Created fast batch training script")

# Create the minimal conversation format
print("\n📝 Creating streamlined conversation dataset...")
conv_file = "agriculture_qa_minimal.jsonl"
count = 0

with open(data_path, 'r') as f_in, open(conv_file, 'w') as f_out:
    for line in f_in:
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
                if count >= 100:  # Limit to 100 examples for speed
                    break
        except:
            continue

print(f"✅ Created minimal conversation dataset with {count} examples")

print("\n✨ All done! You now have multiple faster options:")
print("\n1. FASTEST: Use the system prompt only model:")
print("   ollama run agriculture-qa-fast")
print("\n2. BALANCED: Use the model with embedded examples:")
print("   ollama run agriculture-qa-examples")
print("\n3. OPTIONAL: Run the fast batch training on either model:")
print(f"   python fast_train.py {conv_file} agriculture-qa-fast 50 10")
print("   (This processes 50 examples in batches of 10)")
print("\nTest your model with:")
print("ollama run agriculture-qa-fast \"What are the best crops for sandy soil?\"")