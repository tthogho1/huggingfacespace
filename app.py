import os
from typing import List, Dict, Any
from fastapi import FastAPI, Form, File, UploadFile
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from dotenv import load_dotenv
from vector_search import vector_search
from embedding import Embedding

# .envファイルから環境変数を読み込む
load_dotenv()

# FastAPIアプリケーションを作成
app = FastAPI()

# グローバルなEmbeddingインスタンスを作成（モジュール読み込み時に一度だけ初期化）
embedding = Embedding()

# 環境変数から画像サーバーのURLを取得
IMAGE_SERVER = os.environ.get("IMAGE_SERVER", "https://default-image-server.com/")


class SearchWebcamRequest(BaseModel):
    query: str
    count: str


class SearchWebcamByUrlRequest(BaseModel):
    imageUrl: str
    count: str


@app.post("/api/searchWebcamFromAtlas")
async def search_webcam_from_atlas_endpoint(request: SearchWebcamRequest):
    """
    テキストクエリでWebカメラを検索するAPIエンドポイント

    Args:
        request: query と count を含む SearchWebcamRequest オブジェクト

    Returns:
        検索結果のPhotoリスト
    """
    try:
        query_dict = {"query": request.query, "count": request.count}
        photos = await search_by_text_from_atlas(query_dict, IMAGE_SERVER)
        return JSONResponse(content=photos)
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.post("/api/searchWebcamByImage")
async def search_webcam_by_image_endpoint(
    count: str = Form(...), image: UploadFile = File(...)
):
    """
    画像でWebカメラを検索するAPIエンドポイント

    Args:
        count: 取得する結果の数
        image: アップロードされた画像ファイル

    Returns:
        検索結果のPhotoリスト
    """
    try:
        # 画像をバイナリデータとして読み込む
        image_bytes = await image.read()
        photos = await search_by_image_from_atlas(image_bytes, count, IMAGE_SERVER)
        return JSONResponse(content=photos)
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.post("/api/searchWebcamByURL")
async def search_webcam_by_url_endpoint(request: SearchWebcamByUrlRequest):
    """
    画像URLでWebカメラを検索するAPIエンドポイント

    Args:
        request: imageUrl と count を含む SearchWebcamByUrlRequest オブジェクト

    Returns:
        検索結果のPhotoリスト
    """
    try:
        query_dict = {"imageUrl": request.imageUrl, "count": request.count}
        photos = await search_by_url_from_atlas(query_dict, IMAGE_SERVER)
        return JSONResponse(content=photos)
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


async def search_by_text_from_atlas(
    query: Dict[str, str], image_server: str
) -> List[Dict[str, Any]]:
    query_vector = await embedding.get_text_embedding(query["query"])
    result = await vector_search(query_vector, query["count"])

    photos = []
    for match in result:
        try:
            photo = {
                "id": match["webcam"]["webcamid"],
                "score": match["score"],
                "created_at": "",
                "width": 200,
                "height": 112,
                "description": match["webcam"]["title"],
                "urls": {
                    "small": image_server + str(match["webcam"]["webcamid"]) + ".jpg",
                },
                "links": {
                    "html": match["webcam"]["player"]["day"],
                },
                "location": {
                    "country": match["webcam"]["location"]["country"],
                    "latitude": match["webcam"]["location"]["latitude"],
                    "longitude": match["webcam"]["location"]["longitude"],
                },
            }
            photos.append(photo)
        except Exception as error:
            print("Error:", error)
            raise
    return photos


async def search_by_image_from_atlas(
    blob_image: bytes, count: str, image_server: str
) -> List[Dict[str, Any]]:
    """
    画像から類似画像を検索する

    Args:
        blob_image: 画像のバイナリデータ
        count: 取得する結果の数（文字列）
        image_server: 画像サーバーのURL

    Returns:
        検索結果のPhotoリスト
    """
    blob_vector = await embedding.get_blob_img_embedding(blob_image)
    result = await vector_search(blob_vector, count)

    photos = []
    for match in result:
        try:
            photo = {
                "id": match["webcam"]["webcamid"],
                "score": match["score"],
                "created_at": "",
                "width": 200,
                "height": 112,
                "description": match["webcam"]["title"],
                "urls": {
                    "small": image_server + str(match["webcam"]["webcamid"]) + ".jpg",
                },
                "links": {
                    "html": match["webcam"]["player"]["day"],
                },
                "location": {
                    "country": match["webcam"]["location"]["country"],
                    "latitude": match["webcam"]["location"]["latitude"],
                    "longitude": match["webcam"]["location"]["longitude"],
                },
            }
            photos.append(photo)
        except Exception as error:
            print("Error:", error)
            raise

    return photos


async def search_by_url_from_atlas(
    query: Dict[str, str], image_server: str
) -> List[Dict[str, Any]]:
    """
    画像URLから類似画像を検索する

    Args:
        query: imageUrlとcountを含む辞書
        image_server: 画像サーバーのURL

    Returns:
        検索結果のPhotoリスト
    """
    print(f"imageUrl: {query['imageUrl']}")
    print(f"count: {query['count']}")

    image_vector = await embedding.get_image_embedding(query["imageUrl"])
    result = await vector_search(image_vector, query["count"])

    photos = []
    for match in result:
        try:
            photo = {
                "id": match["webcam"]["webcamid"],
                "score": match["score"],
                "created_at": "",
                "width": 200,
                "height": 112,
                "description": match["webcam"]["title"],
                "urls": {
                    "small": image_server + str(match["webcam"]["webcamid"]) + ".jpg",
                },
                "links": {
                    "html": match["webcam"]["player"]["day"],
                },
                "location": {
                    "country": match["webcam"]["location"]["country"],
                    "latitude": match["webcam"]["location"]["latitude"],
                    "longitude": match["webcam"]["location"]["longitude"],
                },
            }
            photos.append(photo)
        except Exception as error:
            print("Error:", error)
            error_msg = f"Failed to map result to Photo: {str(error)}"
            raise Exception(error_msg)

    return photos
