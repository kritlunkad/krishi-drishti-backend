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

## File Structure

- finetune.py  
  Main script for generating Modelfiles and managing models.

- `Modelfile.fast`  
  Minimal model configuration (auto-generated).

- `Modelfile.examples`  
  Example-embedded model configuration (auto-generated).

- README.md  
  Project documentation.

---

## Setup & Usage

1. **Install Requirements:**
   - Python 3.8+
   - [Ollama](https://ollama.com/) installed and running

2. **Prepare Your Data:**
   - Place your Q&A data in a JSONL file (one JSON object per line with `prompt` and `response` fields).

3. **Run Fine-Tuning Script:**
   ```bash
   python data/finetune.py --data path/to/your/data.jsonl
   ```

4. **Interact with the Model:**
   - Use Ollama or integrate with your frontend to query the custom model.

---

## Judging Notes

- **Speed:**  
  Judges can test both the minimal and example-embedded models for response quality and speed.

- **Customization:**  
  The system is easily extensible—swap in your own data or system prompts for different domains.

- **Reliability:**  
  Automated error handling ensures smooth model creation and updates.

---

## Contact

For questions or demo requests, please contact the project team.

---

**Thank you for evaluating Krishi Drishti!**