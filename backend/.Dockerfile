FROM python:3.11-slim

WORKDIR /app

# 确保 requirements.txt 存在于构建上下文中
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

