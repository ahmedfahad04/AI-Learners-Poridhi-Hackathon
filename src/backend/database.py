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

        # Handle potential missing values, e.g., fill NaN in price columns with 0 or a suitable default
        df['actual_price'] = pd.to_numeric(df['actual_price'].str.replace('[₹,]', '', regex=True), errors='coerce').fillna(0)
        df['discount_price'] = pd.to_numeric(df['discount_price'].str.replace('[₹,]', '', regex=True), errors='coerce').fillna(0)
        df['ratings'] = pd.to_numeric(df['ratings'], errors='coerce').fillna(0)
        df['no_of_ratings'] = pd.to_numeric(df['no_of_ratings'].str.replace(',', '', regex=True), errors='coerce').fillna(0)
       
        # Fill NaN in text fields with empty strings
        df.fillna('', inplace=True)

        products = []
        for _, row in df.iterrows():
            # Combine categories, handle potential missing ones
            category = f"{row['main_category']} > {row['sub_category']}" if row['main_category'] and row['sub_category'] else row['main_category'] or row['sub_category'] or "Uncategorized"

            product = {
                "id": str(uuid.uuid4()), # Generate new UUID for each product
                "name": row['name'],
                "description": row['name'], # Using name as description for now
                "category": category,
                "actual_price": float(row['actual_price']),
                "discount_price": float(row['discount_price']),
                "image": row['image'],
                "link": row['link'],
                "ratings": float(row['ratings']),
                "no_of_ratings": int(row['no_of_ratings'])
            }
            products.append(product)

        # Generate text for embeddings using relevant fields
        texts = [f"Name: {p['name']}, Category: {p['category']}, Price: {p['actual_price']}" for p in products]
        vectors = self.model.encode(texts).tolist()

        # Only create collection if it doesn't exist
        try:
            self.client.get_collection(collection_name=collection_name)
        except Exception: # More specific exception handling might be needed depending on qdrant_client version
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
                    "actual_price": p["actual_price"],
                    "discount_price": p["discount_price"],
                    "image": p["image"],
                    "link": p["link"],
                    "ratings": p["ratings"],
                    "no_of_ratings": p["no_of_ratings"]
                    # Add other relevant fields from the new CSV structure to the payload if needed
                }
            )
            for p, v in zip(products, vectors)
        ]
        self.client.upsert(collection_name=collection_name, points=points, wait=True) # Added wait=True for confirmation
        return len(points)
