from langchain_ollama import ChatOllama
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory
import json
from test_hindi import get_translated_text_hindi, get_translated_text_english
import re
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Ollama LLM
llm = ChatOllama(model="agriculture-qa-fast", temperature=0.5)

# Define the advisor template
advisor_template = """
You are a plant disease expert and agricultural advisor helping a farmer with their crops.

{farmer_context}

Chat History:
{chat_history}

Farmer Question: {question}

Provide helpful, practical advice based on the farmer's specific situation and the plant disease.
Focus on remedies, treatment options, and preventive measures. If organic farming is used,
prioritize organic solutions. Be specific and practical with your advice.
even if the user wants the cure, even if u are not sure , just say it as a suggestion.
If the question is not related to plant diseases, politely redirect the conversation.
"""

# Create PromptTemplate
prompt = PromptTemplate(
    input_variables=["farmer_context", "chat_history", "question"],
    template=advisor_template
)

# Set up conversation memory
memory = ConversationBufferMemory(
    memory_key="chat_history",
    input_key="question"
)

# Create LLMChain
chain = LLMChain(
    llm=llm,
    prompt=prompt,
    memory=memory
)

def bold_text(text):
    # Function to replace text within asterisks with bolded text (removing asterisks)
    return re.sub(r'\*', '', text)

# Function to run the chatbot
def run_plant_disease_chatbot(context, question, language="en"):
    # Translate context fields to English if language is Hindi
    if language == "hi" and isinstance(context, dict):
        translated_context = context.copy()
        # Fields likely to contain user-entered Hindi text
        fields_to_translate = [
            "symptoms",
            "recent_weather",
            "any_other_info",
            "previous_diseases",
            "location",
            "crops_grown",
            "crop_type"
        ]
        for field in fields_to_translate:
            if field in translated_context and translated_context[field]:
                try:
                    translated_context[field] = get_translated_text_english(translated_context[field])
                    logger.info(f"Translated context field '{field}' to English: {translated_context[field]}")
                except Exception as e:
                    logger.error(f"Failed to translate context field '{field}' to English: {str(e)}")
                    # Keep original text if translation fails
        context_str = json.dumps(translated_context, indent=2)
    else:
        # Convert context to string if it's a dict, or use as is
        context_str = json.dumps(context, indent=2) if isinstance(context, dict) else context
    
    # Translate question to English if language is Hindi
    if language == "hi":
        try:
            question = get_translated_text_english(question)
            logger.info(f"Translated Hindi question to English: {question}")
        except Exception as e:
            logger.error(f"Failed to translate question to English: {str(e)}")
            # Proceed with original question if translation fails
    
    # Run the chain with the (possibly translated) question and context
    try:
        response = chain.run(
            farmer_context=context_str,
            question=question
        )
    except Exception as e:
        logger.error(f"Error running chatbot: {str(e)}")
        response = "Sorry, I encountered an error while processing your request."
    
    # Translate response to Hindi if language is Hindi
    if language == "hi":
        try:
            response = get_translated_text_hindi(response)
            logger.info(f"Translated response to Hindi: {response}")
        except Exception as e:
            logger.error(f"Failed to translate response to Hindi: {str(e)}")
            # Return English response if translation fails
    
    return bold_text(response)

# Example usage
if __name__ == "__main__":
    farmer_context = {
        "crop_type": "टमाटर",
        "location": "मध्य घाटी, कैलिफोर्निया",
        "farming_method": "जैविक",
        "symptoms": "पीलापन और पौधों का मुरझाना, तनों पर भूरे धब्बे",
        "soil_type": "दोमट",
        "irrigation": "ड्रिप सिंचाई",
        "recent_weather": "गर्म और शुष्क, 29-35 डिग्री सेल्सियस"
    }
    question_en = "What should I do about the yellowing leaves and wilting in my tomato plants?"
    question_hi = "मेरे टमाटर के पौधों में पीले पत्तों और मुरझाने के लिए मुझे क्या करना चाहिए?"
    
    print("Expert Advice (English):")
    response = run_plant_disease_chatbot(farmer_context, question_en, language="en")
    print(response)
    
    print("\nExpert Advice (Hindi):")
    response = run_plant_disease_chatbot(farmer_context, question_hi, language="hi")
    print(response)
    
    follow_up = "Are there any organic sprays I can use?"
    print("\nFollow-up Advice (English):")
    response = run_plant_disease_chatbot(farmer_context, follow_up, language="en")
    print(response)

