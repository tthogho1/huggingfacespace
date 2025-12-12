import os
from typing import List, Optional
from transformers import (
    CLIPVisionModelWithProjection,
    CLIPTextModelWithProjection,
    AutoTokenizer,
    AutoProcessor,
)
from PIL import Image
import numpy as np
import requests
from io import BytesIO


class Embedding:
    def __init__(self):
        self.model: Optional[CLIPVisionModelWithProjection] = None
        self.tokenizer: Optional[AutoTokenizer] = None
        self.text_model: Optional[CLIPTextModelWithProjection] = None
        self.image_processor: Optional[AutoProcessor] = None
        self._initialize_models()

    def _initialize_models(self):
        """モデルを初期化する"""
        model_id = os.environ.get("MODEL_ID")
        print(f"start initialize model {model_id}")

        self.model = CLIPVisionModelWithProjection.from_pretrained(model_id)
        self.tokenizer = AutoTokenizer.from_pretrained(model_id)
        self.text_model = CLIPTextModelWithProjection.from_pretrained(model_id)
        self.image_processor = AutoProcessor.from_pretrained(model_id, use_fast=True)

        print(f"end initialize model {model_id}")

    async def get_text_embedding(self, text: str) -> List[float]:
        """
        テキストから埋め込みベクトルを取得する

        Args:
            text: 入力テキスト

        Returns:
            埋め込みベクトル
        """
        if self.tokenizer is None or self.text_model is None:
            raise ValueError("Model not initialized")

        text_inputs = self.tokenizer(
            text, padding=True, truncation=True, return_tensors="pt"
        )
        outputs = self.text_model(**text_inputs)
        text_embeds = outputs.text_embeds

        return text_embeds.detach().numpy().flatten().tolist()

    async def get_image_embedding(self, url: str) -> List[float]:
        """
        URL画像から埋め込みベクトルを取得する

        Args:
            url: 画像URL

        Returns:
            埋め込みベクトル
        """
        if not self.image_processor or not self.model:
            raise ValueError("Model not initialized")

        # URLから画像を読み込む
        response = requests.get(url)
        image = Image.open(BytesIO(response.content))

        inputs = self.image_processor(images=image, return_tensors="pt")
        outputs = self.model(**inputs)
        image_embeds = outputs.image_embeds

        return image_embeds.detach().numpy().flatten().tolist()

    async def get_blob_img_embedding(self, image_bytes: bytes) -> List[float]:
        """
        バイナリデータから埋め込みベクトルを取得する

        Args:
            image_bytes: 画像のバイナリデータ

        Returns:
            埋め込みベクトル
        """
        if not self.image_processor or not self.model:
            raise ValueError("Model not initialized")

        # バイナリデータから画像を読み込む
        image = Image.open(BytesIO(image_bytes))

        inputs = self.image_processor(images=image, return_tensors="pt")
        outputs = self.model(**inputs)
        image_embeds = outputs.image_embeds

        return image_embeds.detach().numpy().flatten().tolist()
