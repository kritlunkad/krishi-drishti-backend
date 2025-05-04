# Krishi Drishti Backend

## Overview

This backend powers the Krishi Drishti platform, providing APIs for plant disease detection, expert chatbot advice, user management, and data storage. It is built with FastAPI, SQLAlchemy, and integrates AI models for both image-based disease detection and natural language Q&A in English and Hindi.

---

## Key Features

- **Plant Disease Detection:**  
  Upload plant images to receive disease predictions and confidence scores using a deep learning model.

- **Expert Chatbot:**  
  Get context-aware, practical agricultural advice via a chatbot, with support for both English and Hindi (automatic translation).

- **User & Farmer Management:**  
  Register/login users, save farmer profiles, and associate detections and chat history with Aadhar numbers.

- **History & Analytics:**  
  Retrieve all detections and chat interactions for a farmer.

- **Database:**  
  Uses SQLite (via SQLAlchemy) for persistent storage of users, farmers, detections, and chat logs.

---

## API Endpoints

### `POST /api/register`
Register a new user.

**Request Body:**
```json
{
  "aadhar": "string",
  "password": "string"
}
```
**Response:**  
Success or error message.

---

### `POST /api/login`
Authenticate a user.

**Request Body:**
```json
{
  "aadhar": "string",
  "password": "string"
}
```
**Response:**  
Success or error message.

---

### `POST /api/farmer`
Save or update a farmer's profile/context.

**Request Body:**
```json
{
  "aadhar": "string",
  "name": "string",
  "location": "string",
  "other_fields": "..."
}
```
**Response:**  
Success or error message.

---

### `POST /api/upload`
Upload a plant image for disease detection.

**Form Data:**
- `file`: Image file (jpg/png)
- `aadhar`: User's Aadhar number

**Response:**
```json
{
  "prediction": "disease_name",
  "confidence": 0.95
}
```

---

### `POST /api/save_detection`
Save a detection result to the database.

**Request Body:**
```json
{
  "aadhar": "string",
  "prediction": "disease_name",
  "confidence": 0.95,
  "image_path": "string"
}
```
**Response:**  
Success or error message.

---

### `POST /api/chat`
Get chatbot advice (supports English and Hindi).

**Request Body:**
```json
{
  "aadhar": "string",
  "context": "string",
  "question": "string",
  "language": "en" // or "hi"
}
```
**Response:**
```json
{
  "answer": "string"
}
```

---

### `POST /api/history`
Retrieve all data for a farmer (profile, detections, chats).

**Request Body:**
```json
{
  "aadhar": "string"
}
```
**Response:**
```json
{
  "profile": { ... },
  "detections": [ ... ],
  "chats": [ ... ]
}
```

---

## File Structure

- `main.py` — FastAPI app, all API endpoints, business logic
- `models.py` — SQLAlchemy ORM models (User, Farmer, DetectionResult, ChatInteraction)
- `database.py` — Database connection and session management
- `detect.py` — Image preprocessing and disease prediction logic
- `chatbot.py` — Chatbot logic, prompt templates, translation utilities
- `test_hindi.py` — Translation helpers (English ↔ Hindi)
- `migration.sql` — Example SQL migration for detection results table

---

## Setup & Running

1. **Install Requirements:**
   - Python 3.8+
   - `pip install fastapi uvicorn sqlalchemy passlib langchain langchain_ollama`
   - (Optional) Ollama and model weights for chatbot

2. **Database:**
   - SQLite DB auto-creates on first run.
   - To migrate, use `migration.sql` as needed.

3. **Start the Server:**
   ```bash
   uvicorn main:app --reload
   ```

4. **API Usage:**
   - Use tools like Postman or a frontend to interact with endpoints.
   - For disease detection, upload an image file and provide Aadhar.
   - For chatbot, send context and question (language: "en" or "hi").

---

## Judging Notes

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