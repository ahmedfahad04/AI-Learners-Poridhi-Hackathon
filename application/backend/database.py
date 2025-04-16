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
        products = self.load_data()
        return len(products)
    
    def search_products(self, query: str):
        products = self.load_data()
        query = query.lower()
        return [
            product for product in products
            if query in str(product["product_name"]).lower() or 
               query in str(product["description"]).lower()
        ]
