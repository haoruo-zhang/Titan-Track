from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 数据库 URL
DATABASE_URL = "sqlite:///./users.db"

# 创建数据库引擎
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# 声明基类
Base = declarative_base()

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 用户模型
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)

# 创建所有表
Base.metadata.create_all(bind=engine)
