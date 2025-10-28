# Python 3.10 官方精簡版映像檔作為基底映像檔
FROM python:3.10-slim

# 設定環境變數
ENV PYTHONDONTWRITEBYTECODE=1 \
  PYTHONUNBUFFERED=1 \
  PIP_NO_CACHE_DIR=1 \
  HF_HOME=/home/app/.cache/huggingface \
  PORT=8501

# 安裝系統相依套件  
RUN apt-get update && apt-get install -y --no-install-recommends \
  curl \
  && rm -rf /var/lib/apt/lists/*

# 建立非 root 使用者
RUN useradd -m app
WORKDIR /app

# 複製並安裝 Python 相依套件
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 複製應用程式程式碼
COPY . .

# 設定目錄權限並切換使用者
RUN chown -R app:app /app
USER app

# 開放應用程式Port
EXPOSE 8501

# 設定健康檢查
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD curl -f http://localhost:${PORT}/_stcore/health || exit 1

# 啟動應用程式
CMD ["streamlit", "run", "src/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
