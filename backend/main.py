from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi import FastAPI, Depends, HTTPException,File, UploadFile, Form
from sqlalchemy.orm import Session
from database import SessionLocal, User
import os
from pathlib import Path
from datetime import datetime
from fastapi.staticfiles import StaticFiles
from src.split_video_by_squat import split_video_by_squat  # 确保路径正确
from src.process_and_analyze_video import process_and_analyze_video

app = FastAPI()

# 添加 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源的跨域请求（生产环境建议替换为前端的域名，例如 ["http://localhost:5173"]）
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有 HTTP 方法（如 POST、OPTIONS、GET 等）
    allow_headers=["*"],  # 允许所有请求头
)


# 数据模型
class RegisterRequest(BaseModel):
    username: str
    password: str

# 获取数据库会话
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/register")
async def register_user(data: RegisterRequest, db: Session = Depends(get_db)):
    # 检查用户名是否已存在
    existing_user = db.query(User).filter(User.username == data.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")

    # 创建新用户
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
    # 从数据库中查找用户
    user = db.query(User).filter(User.username == data.username).first()
    if not user or user.password != data.password:
        raise HTTPException(status_code=400, detail="Invalid username or password")

    return {"message": "Login successful"}


# 设置上传目录
UPLOAD_ROOT_DIR = os.path.join(os.getcwd(), "uploads")
Path(UPLOAD_ROOT_DIR).mkdir(parents=True, exist_ok=True)

# 挂载静态文件目录
app.mount("/uploads", StaticFiles(directory=UPLOAD_ROOT_DIR), name="uploads")

@app.post("/upload")
async def upload_video(username: str = Form(...), file: UploadFile = File(...)):
    # 生成时间戳并创建用户目录
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    user_dir = os.path.join(UPLOAD_ROOT_DIR, username, timestamp)
    Path(user_dir).mkdir(parents=True, exist_ok=True)

    # 保存上传文件
    file_path = os.path.join(user_dir, file.filename)
    with open(file_path, "wb") as f:
        f.write(await file.read())

    # 生成相对路径
    relative_file_path = os.path.relpath(file_path, UPLOAD_ROOT_DIR)  # 获取相对路径
    relative_file_path = relative_file_path.replace(os.sep, "/")  # 转换为 URL 格式

    return {
        "message": f"Video uploaded successfullyff to {user_dir}",
        "filename": file.filename,
        "file_path": f"uploads/{relative_file_path}",  # 确保返回相对路径
        "timestamp": timestamp
    }

# 分析深蹲视频接口
@app.post("/analyze_squat_segments")
async def analyze_squat_segments(username: str = Form(...), filename: str = Form(...), timestamp: str = Form(...)):
    # 构造文件路径
    user_dir = os.path.join(UPLOAD_ROOT_DIR, username, timestamp)
    file_path = os.path.join(user_dir, filename)
    output_dir = os.path.join(user_dir, "segments")

    if not os.path.exists(file_path):
        return {"message": "File not found", "error": True}

    try:
        # 调用分割逻辑
        # segment_files = split_video_by_squat(file_path, output_dir)
        segment_files = process_and_analyze_video(file_path,output_dir)

        # 返回分割视频的路径列表
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
    获取用户上传的历史记录
    :param username: 用户名（通过表单提交）
    :return: 用户上传视频的历史记录
    """
    # 检查用户目录是否存在
    user_dir = os.path.join(UPLOAD_ROOT_DIR, username)
    if not os.path.exists(user_dir):
        return {"message": "No history found for this user.", "videos": []}

    # 遍历用户目录，获取所有视频文件信息
    history = []
    for root, dirs, files in os.walk(user_dir):
        for file in files:
            if file.endswith((".mp4", ".avi", ".mkv")):  # 支持的视频格式
                relative_path = os.path.relpath(os.path.join(root, file), UPLOAD_ROOT_DIR)
                history.append({
                    "filename": file,
                    "path": f"uploads/{relative_path}",
                    "timestamp": os.path.basename(root),  # 时间戳来自目录名
                })

    return {"message": "History retrieved successfully.", "videos": history}


