import ollama

print("Testing the agriculture-qa-model...")

try:
    # Ask an agriculture-related question
    response = ollama.chat(model='agriculture-qa-model', 
                          messages=[
                              {'role': 'user', 'content': 'What are best practices for rice cultivation?'}
                          ])

    print("\nResponse:")
    print("-" * 80)
    print(response['message']['content'])
    print("-" * 80)

    # Try another question
    print("\nAsking another question...")
    response = ollama.chat(model='agriculture-qa-model', 
                          messages=[
                              {'role': 'user', 'content': 'How do I control pests in organic farming?'}
                          ])

    print("\nResponse:")
    print("-" * 80)
    print(response['message']['content'])
    print("-" * 80)

    print("\nModel is working correctly!")
    
except Exception as e:
    print(f"Error: {e}")
    print("\nPossible solutions:")
    print("1. Make sure Ollama is running (run 'ollama serve' in a terminal)")
    print("2. Make sure you've created and fine-tuned the model using the fix_model_creation.py script")
    print("3. Check if the model exists with 'ollama list'")
    print("4. If the model is missing, try running the fix_model_creation.py script again")