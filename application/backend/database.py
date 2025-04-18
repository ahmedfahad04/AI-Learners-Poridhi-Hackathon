import io
import uuid
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.http.models import PointStruct, VectorParams, Distance
import numpy as np
import pandas as pd

class MockDatabase:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.total_records = 0

    def load_data(self):
        df = pd.read_csv(self.file_path)
        products = df.to_dict(orient='records')
        self.total_records = len(products)
        return products

    def get_products(self):
        return self.load_data()
    
    def get_product_count(self):
        client = QdrantClient(host="localhost", port=6333)
        
        try:
            # Check if collection exists
            collections = client.get_collections().collections
            collection_names = [collection.name for collection in collections]
            
            if "products" in collection_names:
                count_result = client.count(collection_name="products")
                return count_result.count
            else:
                return 0
        except Exception:
            return 0
    
    # def search_products(self, query: str):
    #     products = self.load_data()
    #     query = query.lower()
    #     return [
    #         product for product in products
    #         if query in str(product["product_name"]).lower() or 
    #            query in str(product["description"]).lower()
    #     ]
    
    def search_products(self, query: str, top_k: int = 10):
        client = QdrantClient(host="localhost", port=6333)
        model = SentenceTransformer('all-MiniLM-L6-v2')
        query_vector = model.encode(query).tolist()
        results = client.search(
            collection_name="products",
            query_vector=query_vector,
            limit=top_k
        )
        # Return all relevant fields and the confidence score
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
    
    def upload_csv_to_qdrant(self, file, collection_name="products"):
        """Uploads products from a CSV file to Qdrant using real embeddings."""

        df = pd.read_csv(file)
        model = SentenceTransformer('all-MiniLM-L6-v2')
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
        vectors = model.encode(texts).tolist()
        client = QdrantClient(host="localhost", port=6333)
        # Create (or recreate) collection with correct vector size
        client.recreate_collection(
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
        client.upsert(collection_name=collection_name, points=points)
        return len(points)
