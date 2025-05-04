# Krishi Drishti Backend

## Overview

**Krishi Drishti** is an AI-powered backend system designed to assist farmers, agricultural experts, and enthusiasts with accurate, detailed, and context-aware responses about agriculture, farming, and crop management. The backend leverages large language models (LLMs) and custom fine-tuning to deliver domain-specific expertise.

---

## Features

- **Domain-Specialized AI Assistant:**  
  Provides expert advice on crop rotation, soil management, sustainable farming, pest control, irrigation, harvesting, livestock, agricultural economics, and equipment.

- **Custom Model Creation:**  
  Uses [Ollama](https://ollama.com/) to create and manage LLMs tailored for agriculture, with options for minimal system prompt or embedded example-based fine-tuning.

- **Flexible Fine-Tuning Approaches:**  
  - **Minimal Model:** Fastest setup using a strong system prompt.
  - **Example-Embedded Model:** Incorporates real Q&A examples for improved contextual accuracy.

- **Automated Model Management:**  
  Scripts handle model creation, updating, and removal seamlessly.

- **AI Workflow with LangChain:**  
  We have used LangChain with Ollama to create an AI workflow that takes context from forms filled out by farmers and uses our fine-tuned Llama 3.2 1B model (`agriculture-qa-fast`). This allows the chatbot to answer questions with more relevance and personalization based on the farmer's context.

- **Interactive Farm Mapping with Three.js:**  
  We provide a very easy-to-use interface built with Three.js for farmers to create rough maps of their farm areas. Farmers can mark the crops they have planted, comment on diseases observed in particular areas, and save this information for offline use. This mapping tool is lightweight, intuitive, and requires minimal computational resources, making it accessible even on low-end devices.

---

## Models Used

- **Chatbot Model:**  
  We used the open-source Llama 3.2 (1B parameter) model, fine-tuned using the Hugging Face KisanVani dataset. The KisanVani dataset is specifically focused on Indian agriculture, so we used it to ensure the model's responses are highly relevant for Indian farmers. The resulting model is named `agriculture-qa-fast` and is integrated into our chatbot to answer farmers' queries.

- **Plant Disease Detection:**  
  For image-based disease detection, we used the Hugging Face model [`linkanjarad/mobilenet_v2_1.0_224-plant-disease-identification`](https://huggingface.co/linkanjarad/mobilenet_v2_1.0_224-plant-disease-identification), a pre-trained MobileNetV2 model. This model is lightweight and works efficiently offline, making it ideal for resource-constrained environments.

- **Translation:**  
  For English↔Hindi translation, we used Argos Translate and exposed FastAPI endpoints for translation.

---

## How It Works

1. **Minimal Model Creation:**  
   - Generates a `Modelfile.fast` with a detailed system prompt.
   - Creates a model (`agriculture-qa-fast`) using Ollama for rapid deployment.

2. **Example-Embedded Model:**  
   - Extracts sample Q&A pairs from your dataset.
   - Generates a `Modelfile.examples` embedding these examples.
   - Builds a more context-aware model (`agriculture-qa-examples`).

3. **Model Management:**  
   - Existing models with the same name are automatically removed before creation.
   - All model operations are handled via Python scripts and Ollama CLI.

---

## API Endpoints

FastAPI endpoints were created for interfacing with all models and translation utilities.  
All endpoints are open source and designed for easy integration and offline use.

- `/api/register` — Register a new user
- `/api/login` — Authenticate a user
- `/api/farmer` — Save or update a farmer's profile/context
- `/api/upload` — Upload a plant image for disease detection
- `/api/save_detection` — Save a detection result to the database
- `/api/chat` — Get chatbot advice (supports English and Hindi)
- `/api/history` — Retrieve all data for a farmer (profile, detections, chats)
- `/api/translate` — Translate text between English and Hindi

**Note:**  
- The `/api/translate` endpoint runs on port **8100**.  
- All other backend endpoints run on port **8000**.

---

## File Structure

- `finetune.py` — Main script for generating Modelfiles and managing models.
- `Modelfile.fast` — Minimal model configuration (auto-generated).
- `Modelfile.examples` — Example-embedded model configuration (auto-generated).
- `main.py` — FastAPI app, all API endpoints, business logic.
- `models.py` — SQLAlchemy ORM models (User, Farmer, DetectionResult, ChatInteraction).
- `database.py` — Database connection and session management.
- `detect.py` — Image preprocessing and disease prediction logic.
- `chatbot.py` — Chatbot logic, prompt templates, translation utilities.
- `test_hindi.py` — Translation helpers (English ↔ Hindi).
- `migration.sql` — Example SQL migration for detection results table.
- `README.md` — Project documentation.

---

## Setup & Usage

1. **Install Requirements:**
   - Python 3.8+
   - `pip install fastapi uvicorn sqlalchemy passlib langchain langchain_ollama argostranslate`
   - (Optional) Ollama and model weights for chatbot

2. **Database:**
   - SQLite DB auto-creates on first run.
   - To migrate, use `migration.sql` as needed.

3. **Start the Server:**
   - For backend APIs (excluding translation):  
     ```bash
     uvicorn main:app --reload --port 8000
     ```
   - For translation API:  
     ```bash
     uvicorn test_hindi:app --reload --port 8100
     ```

4. **API Usage:**
   - Use tools like Postman or a frontend to interact with endpoints.
   - For disease detection, upload an image file and provide Aadhar.
   - For chatbot, send context and question (language: "en" or "hi").
   - For translation, use the `/api/translate` endpoint on port 8100.

---

## Judging Notes

- **Open Source Stack:**  
  All models and libraries used are open source.

- **Offline & Lightweight:**  
  The main goal was to use models that can run offline, with minimal computational overhead, making them suitable for resource-constrained devices.

- **Demonstration for Edge Devices:**  
  This project is specifically designed to demonstrate how a fine-tuned Llama 3.2 1B model (for chatbot), LangChain (for AI workflow and context handling), and a MobileNetV2-based disease detection model (`linkanjarad/mobilenet_v2_1.0_224-plant-disease-identification`) can work efficiently in resource-constrained and offline situations.  
  Farmers can use the system even without internet connectivity and with minimal computing resources.

- **Easy Farm Mapping:**  
  The Three.js-based mapping interface allows farmers to easily create and save maps of their farm, mark crops, comment on diseases, and use this information offline. This interface is highly intuitive and lightweight, ensuring accessibility on low-end devices.

- **Multilingual:**  
  All chatbot endpoints support both English and Hindi (auto-translation).

- **Traceability:**  
  All detections and chats are linked to Aadhar for easy history retrieval.

- **Extensible:**  
  Add new models, endpoints, or database fields as needed.

---

## Contact

For questions or demo requests, please contact the project team.

---

**Thank you for evaluating Krishi Drishti!**