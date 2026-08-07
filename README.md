# FarmMind

AI-Powered Farm Decision Optimization Platform

## Overview

FarmMind is an AI-powered decision support platform that assists farmers throughout the crop lifecycle by combining crop knowledge, weather intelligence, disease analysis, and multi-criteria decision optimization. The system currently supports **Rice** and **Tomato** crops.

## Features

- Persistent Farm Memory
- Crop Workflow Engine
- Context Fusion Engine
- Weather Intelligence
- Disease Analysis Integration
- Decision Optimization (AHP + TOPSIS)
- Explainable AI Recommendations
- Post-Harvest Intelligence
- React Dashboard

## Tech Stack

### Backend
- FastAPI
- SQLAlchemy
- PostgreSQL
- Python

### Frontend
- React
- HTML/CSS
- JavaScript

### AI / Machine Learning
- YOLO11
- Random Forest
- XGBoost
- AHP
- TOPSIS

## Project Structure

```
FarmMind/
│
├── backend/
├── frontend/
├── README.md
├── requirements.txt
└── .gitignore
```

## Installation

### Backend

```bash
cd backend
pip install -r requirements.txt
python run.py
```

### Frontend

```bash
cd frontend
npm install
npm start
```

## Supported Crops

- Rice
- Tomato

---

Developed as a research project at **PES University**.