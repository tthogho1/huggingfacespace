FROM python:3.11-slim

# 作業ディレクトリを設定
WORKDIR /app

# システムパッケージの更新と必要なパッケージのインストール
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 依存関係ファイルをコピー
COPY requirements.txt .

# Pythonパッケージのインストール
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションファイルをコピー
COPY app.py .
COPY embedding.py .
COPY vector_search.py .
COPY .env .

# Hugging Face Spacesのデフォルトポート7860を公開
EXPOSE 7860

# アプリケーションを起動
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860"]
