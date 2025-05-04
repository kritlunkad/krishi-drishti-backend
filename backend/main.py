from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session
from database import SessionLocal, engine
import models
from detect import load_model_and_processor, preprocess_image, predict_disease
from chatbot import run_plant_disease_chatbot
from passlib.context import CryptContext
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Create database tables
models.Base.metadata.create_all(bind=engine)

# Pydantic models
class FarmerContext(BaseModel):
    crop_type: Optional[str] = ""
    location: Optional[str] = ""
    farming_method: Optional[str] = ""
    symptoms: Optional[str] = ""
    soil_type: Optional[str] = ""
    irrigation: Optional[str] = ""
    recent_weather: Optional[str] = ""
    aadhar: Optional[str] = None
    name: Optional[str] = None
    crops_grown: Optional[str] = None
    farm_size: Optional[str] = None
    previous_diseases: Optional[str] = None
    extra_farm_type: Optional[str] = None
    any_other_info: Optional[str] = None

class ChatQuery(BaseModel):
    context: FarmerContext
    question: str
    language: Optional[str] = "en"

class ChatHistoryRequest(BaseModel):
    aadhar: str
    language: Optional[str] = "en"

class LoginRequest(BaseModel):
    aadhar: str
    password: str

class RegisterRequest(BaseModel):
    aadhar: str
    password: str

class SaveDetectionRequest(BaseModel):
    aadhar: str
    disease: str
    confidence: float

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Password hashing and verification
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

@app.post("/api/login")
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.aadhar == request.aadhar).first()
    if not user or not verify_password(request.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid Aadhar or password")
    return {"message": "Login successful", "aadhar": user.aadhar}

@app.post("/api/register")
async def register(request: RegisterRequest, db: Session = Depends(get_db)):
    existing_user = db.query(models.User).filter(models.User.aadhar == request.aadhar).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Aadhar already registered")
    hashed_password = hash_password(request.password)
    db_user = models.User(aadhar=request.aadhar, password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return {"message": "Registration successful", "aadhar": db_user.aadhar}

@app.post("/api/farmer")
async def save_farmer(context: FarmerContext, db: Session = Depends(get_db)):
    existing_farmer = db.query(models.Farmer).filter(models.Farmer.aadhar == context.aadhar).first()
    if existing_farmer:
        return {"message": "Farmer already exists", "aadhar": context.aadhar}
    db_farmer = models.Farmer(
        aadhar=context.aadhar,
        name=context.name,
        location=context.location,
        crops_grown=context.crops_grown,
        soil_type=context.soil_type,
        irrigation_system=context.irrigation,
        farm_size=context.farm_size,
        previous_diseases=context.previous_diseases,
        organic_farming=context.farming_method,
        extra_farm_type=context.extra_farm_type,
        current_weather=context.recent_weather,
        any_other_info=context.any_other_info
    )
    db.add(db_farmer)
    db.commit()
    db.refresh(db_farmer)
    return {"message": "Farmer info saved", "aadhar": context.aadhar}

@app.post("/api/upload")
async def upload_image(
    file: UploadFile = File(...),
    aadhar: str = Form(None),
    language: str = Form("en"),
    db: Session = Depends(get_db)
):
    if not file.filename.lower().endswith(('.png', '.jpg', '.jpeg')):
        raise HTTPException(status_code=400, detail="Invalid image format. Use PNG, JPG, or JPEG.")
    file_path = f"temp_{file.filename}"
    with open(file_path, "wb") as f:
        f.write(await file.read())
    model_name = "linkanjarad/mobilenet_v2_1.0_224-plant-disease-identification"
    processor, model = load_model_and_processor(model_name)
    if processor is None or model is None:
        os.remove(file_path)
        raise HTTPException(status_code=500, detail="Failed to load model.")
    predicted_class, confidence = predict_disease(file_path, processor, model, language)
    os.remove(file_path)
    if predicted_class is None:
        raise HTTPException(status_code=500, detail="Failed to predict disease.")
    return {
        "disease": predicted_class,
        "confidence": float(confidence),
        "aadhar": aadhar
    }

@app.post("/api/save_detection")
async def save_detection(request: SaveDetectionRequest, db: Session = Depends(get_db)):
    logger.info(f"Received save_detection request: {request.dict()}")
    try:
        if not request.aadhar or not request.disease or not isinstance(request.confidence, float):
            raise HTTPException(
                status_code=422,
                detail="Invalid input: aadhar and disease must be non-empty strings, confidence must be a float"
            )
        db_detection = models.DetectionResult(
            aadhar=request.aadhar,
            disease=request.disease,
            confidence=request.confidence
        )
        db.add(db_detection)
        db.commit()
        db.refresh(db_detection)
        logger.info(f"Detection saved for aadhar: {request.aadhar}")
        return {
            "message": "Detection saved",
            "aadhar": request.aadhar,
            "disease": request.disease,
            "confidence": request.confidence
        }
    except Exception as e:
        logger.error(f"Error saving detection: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to save detection: {str(e)}")

@app.post("/api/chat")
async def chat_query(query: ChatQuery, db: Session = Depends(get_db)):
    try:
        response = run_plant_disease_chatbot(query.context.dict(), query.question, query.language)
        db_chat = models.ChatInteraction(
            aadhar=query.context.aadhar,
            question=query.question,
            answer=response
        )
        db.add(db_chat)
        db.commit()
        db.refresh(db_chat)
        return {
            "question": query.question,
            "answer": response,
            "aadhar": query.context.aadhar
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chatbot error: {str(e)}")

@app.post("/api/history")
async def get_history(request: ChatHistoryRequest, db: Session = Depends(get_db)):
    logger.info(f"Fetching history for aadhar: {request.aadhar}")
    farmer = db.query(models.Farmer).filter(models.Farmer.aadhar == request.aadhar).first()
    detections = db.query(models.DetectionResult).filter(models.DetectionResult.aadhar == request.aadhar).all()
    chats = db.query(models.ChatInteraction).filter(models.ChatInteraction.aadhar == request.aadhar).all()
    return {
        "farmer": farmer.__dict__ if farmer else None,
        "detections": [d.__dict__ for d in detections],
        "chats": [c.__dict__ for c in chats]
    }