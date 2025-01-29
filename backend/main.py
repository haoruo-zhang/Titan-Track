from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi import FastAPI, Depends, HTTPException, File, UploadFile, Form
from sqlalchemy.orm import Session
from database import SessionLocal, User
import os
from pathlib import Path
from datetime import datetime
from fastapi.staticfiles import StaticFiles
from src.split_video_by_squat import split_video_by_squat  # Ensure the path is correct
from src.process_and_analyze_video import process_and_analyze_video

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for CORS requests (replace with frontend domain in production, e.g., ["http://localhost:5173"])
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (e.g., POST, OPTIONS, GET, etc.)
    allow_headers=["*"],  # Allow all request headers
)

# Data model
class RegisterRequest(BaseModel):
    username: str
    password: str

# Get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/register")
async def register_user(data: RegisterRequest, db: Session = Depends(get_db)):
    # Check if the username already exists
    existing_user = db.query(User).filter(User.username == data.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")

    # Create a new user
    new_user = User(username=data.username, password=data.password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "Registration successful"}

class LoginRequest(BaseModel):
    username: str
    password: str

@app.post("/login")
async def login_user(data: LoginRequest, db: Session = Depends(get_db)):
    # Look up the user in the database
    user = db.query(User).filter(User.username == data.username).first()
    if not user or user.password != data.password:
        raise HTTPException(status_code=400, detail="Invalid username or password")

    return {"message": "Login successful"}

# Set upload directory
UPLOAD_ROOT_DIR = os.path.join(os.getcwd(), "uploads")
Path(UPLOAD_ROOT_DIR).mkdir(parents=True, exist_ok=True)

# Mount static file directory
app.mount("/uploads", StaticFiles(directory=UPLOAD_ROOT_DIR), name="uploads")

@app.post("/upload")
async def upload_video(username: str = Form(...), file: UploadFile = File(...)):
    # Generate a timestamp and create the user directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    user_dir = os.path.join(UPLOAD_ROOT_DIR, username, timestamp)
    Path(user_dir).mkdir(parents=True, exist_ok=True)

    # Save the uploaded file
    file_path = os.path.join(user_dir, file.filename)
    with open(file_path, "wb") as f:
        f.write(await file.read())

    # Generate relative path
    relative_file_path = os.path.relpath(file_path, UPLOAD_ROOT_DIR)  # Get relative path
    relative_file_path = relative_file_path.replace(os.sep, "/")  # Convert to URL format

    return {
        "message": f"Video uploaded successfully to {user_dir}",
        "filename": file.filename,
        "file_path": f"uploads/{relative_file_path}",  # Ensure the response returns a relative path
        "timestamp": timestamp
    }

# Analyze squat video segments API
@app.post("/analyze_squat_segments")
async def analyze_squat_segments(username: str = Form(...), filename: str = Form(...), timestamp: str = Form(...)):
    # Construct file path
    user_dir = os.path.join(UPLOAD_ROOT_DIR, username, timestamp)
    file_path = os.path.join(user_dir, filename)
    output_dir = os.path.join(user_dir, "segments")

    if not os.path.exists(file_path):
        return {"message": "File not found", "error": True}

    try:
        # Call the segmentation logic
        segment_files = process_and_analyze_video(file_path, output_dir)

        # Return the list of segmented video paths
        return {
            "message": "Squat segments analyzed successfully",
            "segments": [f"uploads/{username}/{timestamp}/segments/{os.path.basename(f)}" for f in segment_files]
        }
    except Exception as e:
        return {"message": "Analysis failed", "error": str(e)}

UPLOAD_ROOT_DIR = os.path.join(os.getcwd(), "uploads")

@app.post("/history")
async def get_user_history(username: str = Form(...)):
    """
    Retrieve the upload history of a user
    :param username: The username (submitted via form)
    :return: A history of uploaded videos by the user
    """
    # Check if the user directory exists
    user_dir = os.path.join(UPLOAD_ROOT_DIR, username)
    if not os.path.exists(user_dir):
        return {"message": "No history found for this user.", "videos": []}

    # Traverse the user directory and get all video file information
    history = []
    for root, dirs, files in os.walk(user_dir):
        for file in files:
            if file.endswith((".mp4", ".avi", ".mkv")):  # Supported video formats
                relative_path = os.path.relpath(os.path.join(root, file), UPLOAD_ROOT_DIR)
                history.append({
                    "filename": file,
                    "path": f"uploads/{relative_path}",
                    "timestamp": os.path.basename(root),  # Timestamp is derived from the directory name
                })

    return {"message": "History retrieved successfully.", "videos": history}
