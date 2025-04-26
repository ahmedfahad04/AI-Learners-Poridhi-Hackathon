import io
import uuid
import logging
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.http.models import PointStruct, VectorParams, Distance
import numpy as np
import pandas as pd
import os
from keybert import KeyBERT


DB_URL = os.getenv("DATABASE_URL", "http://qdrant:6333")

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class QdrantDB:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(QdrantDB, cls).__new__(cls)
            cls._instance._init_db(*args, **kwargs)
        return cls._instance

    def _init_db(self, file_path: str = None):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.kw_model = KeyBERT()
        # self.client = QdrantClient(host=DB_HOST, port=DB_PORT)
        self.client = QdrantClient(url=os.getenv("DATABASE_URL", "http://qdrant:6333"))
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

        new_query = self.filter_queries(query)

        query_vector = self.model.encode(new_query).tolist()
        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            limit=top_k
        )

        return [
            {
                "title": match.payload.get("title"),
                "description": match.payload.get("description"),
                "category": match.payload.get("category"),
                "price": match.payload.get("price"),
                "text_for_embedding": match.payload.get("text_for_embedding"),
                "score": match.score
            }
            for match in results
        ]

    def upload_csv_to_qdrant(self, file, collection_name=None, batch_size=100):
        if collection_name is None:
            collection_name = self.collection_name
        
        logging.info(f"Starting CSV upload to collection '{collection_name}'...")
        
        try:
            df = pd.read_csv(file)
            logging.info(f"Successfully read CSV file. Total rows: {len(df)}")
        except Exception as e:
            logging.error(f"Failed to read CSV file: {e}")
            return 0

        # --- Data Cleaning ---
        # Handle potential missing values, e.g., fill NaN in price columns with 0 or a suitable default
        # df['actual_price'] = pd.to_numeric(df['actual_price'].str.replace('[₹,]', '', regex=True), errors='coerce').fillna(0)
        # df['discount_price'] = pd.to_numeric(df['discount_price'].str.replace('[₹,]', '', regex=True), errors='coerce').fillna(0)
        # df['ratings'] = pd.to_numeric(df['ratings'], errors='coerce').fillna(0)
        # df['no_of_ratings'] = pd.to_numeric(df['no_of_ratings'].str.replace(',', '', regex=True), errors='coerce').fillna(0)
        
        # Fill NaN in text fields with empty strings
        df.fillna('', inplace=True)
        logging.info("Data cleaning completed.")

        # --- Ensure Collection Exists ---
        vector_size = len(self.model.encode("test").tolist()) # Get vector size beforehand
        try:
            self.client.get_collection(collection_name=collection_name)
            logging.info(f"Collection '{collection_name}' already exists.")
        except Exception: # More specific exception handling might be needed
            logging.info(f"Collection '{collection_name}' not found. Creating...")
            try:
                self.client.recreate_collection(
                    collection_name=collection_name,
                    vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
                )
                logging.info(f"Successfully created collection '{collection_name}'.")
            except Exception as e:
                logging.error(f"Failed to create collection '{collection_name}': {e}")
                return 0 # Cannot proceed without the collection

        # --- Batch Processing ---
        total_uploaded = 0
        total_failed = 0
        for i in range(0, len(df), batch_size):
            batch_df = df.iloc[i:min(i + batch_size, len(df))]
            logging.info(f"Processing batch {i // batch_size + 1}/{ (len(df) + batch_size - 1) // batch_size } (Rows {i+1}-{min(i + batch_size, len(df))})...")

            products = []
            for _, row in batch_df.iterrows():
                # category = f"{row['main_category']} > {row['sub_category']}" if row['main_category'] and row['sub_category'] else row['main_category'] or row['sub_category'] or "Uncategorized"
                product = {
                    "id": str(uuid.uuid4()),
                    "title": row['title'],
                    "description": row['description'],
                    "category": row['category'],
                    "text_for_embedding": row['text_for_embedding'],
                }

                logging.debug(f"Product data: {product}")
                products.append(product)

            if not products:
                logging.warning(f"Batch {i // batch_size + 1} resulted in zero products to process. Skipping.")
                continue

            try:
                # Generate embeddings for the batch
                texts = [f"{p['text_for_embedding']}" for p in products]
                vectors = self.model.encode(texts).tolist()

                points = [
                    PointStruct(
                        id=p["id"],
                        vector=v,
                        payload={k: v for k, v in p.items() if k != 'id'}
                    )
                    for p, v in zip(products, vectors)
                ]

                # Upsert the batch with error handling
                self.client.upsert(collection_name=collection_name, points=points, wait=True)
                batch_uploaded_count = len(points)
                total_uploaded += batch_uploaded_count
                logging.info(f"Successfully uploaded batch {i // batch_size + 1}. Uploaded {batch_uploaded_count} points. Total uploaded so far: {total_uploaded}")

            except Exception as e:
                batch_failed_count = len(products)
                total_failed += batch_failed_count
                logging.error(f"Failed to process or upload batch {i // batch_size + 1} (Rows {i+1}-{min(i + batch_size, len(df))}): {e}. Skipping this batch.")
                # Optional: Implement retry logic here if desired

        logging.info(f"CSV upload finished. Total successfully uploaded: {total_uploaded}. Total failed: {total_failed}.")
        return total_uploaded

    def filter_queries(self, query: str, top_k: int = 3):

        keywords = self.kw_model.extract_keywords(query, keyphrase_ngram_range=(1, 1), stop_words='english')

        logging.info(f"Extracted keywords: {keywords}")

        # return top 3
        top_keys = keywords[:top_k]

        # create a f string with comma delimeter
        new_query = ', '.join([key[0] for key in top_keys])

        logging.info(f"Filtered query: {new_query}")

        return new_query

