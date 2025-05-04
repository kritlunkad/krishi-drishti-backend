from sqlalchemy import Column, Integer, String, Float, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    aadhar = Column(String, unique=True, index=True)
    password = Column(String)

class Farmer(Base):
    __tablename__ = "farmers"
    id = Column(Integer, primary_key=True, index=True)
    aadhar = Column(String, unique=True, index=True)
    name = Column(String, nullable=True)
    location = Column(String, nullable=True)
    crops_grown = Column(String, nullable=True)
    soil_type = Column(String, nullable=True)
    irrigation_system = Column(String, nullable=True)
    farm_size = Column(String, nullable=True)
    previous_diseases = Column(Text, nullable=True)
    organic_farming = Column(String, nullable=True)
    extra_farm_type = Column(String, nullable=True)
    current_weather = Column(String, nullable=True)
    any_other_info = Column(Text, nullable=True)

class DetectionResult(Base):
    __tablename__ = "detection_results"
    id = Column(Integer, primary_key=True, index=True)
    aadhar = Column(String, index=True)
    disease = Column(String)
    confidence = Column(Float)

class ChatInteraction(Base):
    __tablename__ = "chat_interactions"
    id = Column(Integer, primary_key=True, index=True)
    aadhar = Column(String, index=True)
    question = Column(Text)
    answer = Column(Text)