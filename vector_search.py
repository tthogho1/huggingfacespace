from typing import List, Dict, Any
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os

# .envファイルから環境変数を読み込む
load_dotenv()

# MongoDBの接続情報を.envから取得
MONGODB_URL = os.environ.get("MONGODB_URL")
DATABASE_NAME = os.environ.get("DATABASE_NAME")


async def connect_to_database():
    """MongoDBに接続する"""
    client = AsyncIOMotorClient(MONGODB_URL)
    database = client[DATABASE_NAME]
    return database


async def vector_search(
    query_vector: List[float], count_s: str
) -> List[Dict[str, Any]]:
    """
    ベクトル検索を実行する

    Args:
        query_vector: クエリベクトル
        count_s: 取得する結果の数（文字列）

    Returns:
        検索結果のリスト
    """
    try:
        database = await connect_to_database()
        collection = database["webcam"]

        count = int(count_s)

        # アグリゲーションパイプラインの実行
        pipeline = [
            {
                "$vectorSearch": {
                    "index": "imgembindex",
                    "path": "embedding",
                    "queryVector": query_vector,
                    "numCandidates": 100,
                    "limit": count,
                }
            },
            {
                "$project": {
                    "score": {"$meta": "vectorSearchScore"},
                    "webcam.webcamid": 1,
                    "webcam.title": 1,
                    "webcam.location.country": 1,
                    "webcam.location.latitude": 1,
                    "webcam.location.longitude": 1,
                    "webcam.player.day": 1,
                }
            },
        ]

        result = await collection.aggregate(pipeline).to_list(length=None)
        return result
    except Exception as error:
        print("Error:", error)
        raise
