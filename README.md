---
title: Webcam Search API
emoji: 📸
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
license: mit
---

# Webcam Search API

画像とテキストを使って Web カメラを検索する API です。CLIP モデルを使用してベクトル検索を実行します。

## 機能

- **テキスト検索**: テキストクエリから Web カメラを検索
- **画像アップロード検索**: アップロードした画像から類似 Web カメラを検索
- **URL 画像検索**: 画像 URL から類似 Web カメラを検索

## API エンドポイント

### POST /api/searchWebcamFromAtlas

テキストクエリで検索

**Parameters:**

- `query`: 検索テキスト
- `count`: 取得件数

### POST /api/searchWebcamByImage

画像ファイルをアップロードして検索

**Parameters:**

- `image`: 画像ファイル
- `count`: 取得件数

### POST /api/searchWebcamByURL

画像 URL から検索

**Parameters:**

- `imageUrl`: 画像の URL
- `count`: 取得件数

## 環境変数

以下の環境変数を Hugging Face Spaces の設定で追加してください：

- `MODEL_ID`: 使用する CLIP モデル ID（例: `openai/clip-vit-base-patch32`）
- `MONGODB_URL`: MongoDB の接続 URL
- `DATABASE_NAME`: データベース名
- `IMAGE_SERVER`: 画像サーバーの URL

## ドキュメント

API ドキュメントは `/docs` で確認できます。
