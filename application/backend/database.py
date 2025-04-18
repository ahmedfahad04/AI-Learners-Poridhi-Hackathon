import io
import uuid
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.http.models import PointStruct, VectorParams, Distance
import numpy as np
import pandas as pd

class QdrantDB:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(QdrantDB, cls).__new__(cls)
            cls._instance._init_db(*args, **kwargs)
        return cls._instance

    def _init_db(self, file_path: str = None):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.client = QdrantClient(host="localhost", port=6333)
        self.collection_name = "products"
        self.total_records = 0

    def get_products(self):
        return self.client.count(collection_name=self.collection_name)

    def get_product_count(self):
        try:
            collections = self.client.get_collections().collections
            collection_names = [collection.name for collection in collections]
            if self.collection_name in collection_names:
                count_result = self.client.count(collection_name=self.collection_name)
                return count_result.count
            else:
                return 0
        except Exception:
            return 0

    def search_products(self, query: str, top_k: int = 10):
        query_vector = self.model.encode(query).tolist()
        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            limit=top_k
        )
        return [
            {
                "name": match.payload.get("name"),
                "description": match.payload.get("description"),
                "category": match.payload.get("category"),
                "price": match.payload.get("price"),
                "score": match.score
            }
            for match in results
        ]

    def upload_csv_to_qdrant(self, file, collection_name=None):
        if collection_name is None:
            collection_name = self.collection_name
        df = pd.read_csv(file)
        products = []
        for _, row in df.iterrows():
            product = {
                "id": str(uuid.uuid4()),
                "name": row['product_name'],
                "description": row['description'],
                "category": row['category'],
                "price": row['price'],
            }
            products.append(product)
        texts = [f"{p['name']} - {p['description']} - {p['price']}$" for p in products]
        vectors = self.model.encode(texts).tolist()
        # Only create collection if it doesn't exist
        collections = self.client.get_collections().collections
        collection_names = [collection.name for collection in collections]
        if collection_name not in collection_names:
            self.client.recreate_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(size=len(vectors[0]), distance=Distance.COSINE),
            )
        points = [
            PointStruct(
                id=p["id"],
                vector=v,
                payload={
                    "name": p["name"],
                    "description": p["description"],
                    "category": p["category"],
                    "price": p["price"]
                }
            )
            for p, v in zip(products, vectors)
        ]
        self.client.upsert(collection_name=collection_name, points=points)
        return len(points)
