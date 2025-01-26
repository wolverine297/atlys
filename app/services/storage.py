# app/services/storage.py
from abc import ABC, abstractmethod
import json
import logging
import os
from typing import List
from ..schemas.product import Product
from ..core.config import settings

class StorageStrategy(ABC):
    """Abstract base class for storage strategies"""
    
    @abstractmethod
    async def save_products(self, products: List[Product]) -> None:
        """Save products to storage"""
        pass

    @abstractmethod
    async def load_products(self) -> List[Product]:
        """Load products from storage"""
        pass

class JsonFileStorage(StorageStrategy):
    """Concrete implementation for JSON file storage"""
    
    def __init__(self, file_path: str = settings.LOCAL_STORAGE_PATH):
        self.file_path = file_path
        # Create directory if it doesn't exist
        directory = os.path.dirname(file_path)
        if not os.path.exists(directory):
            logging.info(f"Directory {directory} not found. Creating it now.")
            os.makedirs(directory, exist_ok=True)
        
        if not os.path.exists(self.file_path):
            logging.info(f"Storage file not found. Creating a new file at {self.file_path}.")
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump([], f, indent=2, ensure_ascii=False)


    async def save_products(self, products: List[Product]) -> None:
        """Save products to JSON file"""
        try:
            if not products:
                raise ValueError("No products to save")
            
            logging.debug(f"Saving {len(products)} products to {self.file_path}")

            products_data = [product.model_dump() for product in products]
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(products_data, f, indent=2, ensure_ascii=False)
        except ValueError as ve:
            raise Exception(f"Validation Error: {str(ve)}")
        except Exception as e:
            raise Exception(f"Error saving products to JSON: {str(e)}")



    async def load_products(self) -> List[Product]:
        """Load products from JSON file with validation"""
        try:
            if not os.path.exists(self.file_path):
                logging.warning("Storage file not found.")
                return []
            
            with open(self.file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                logging.debug(f"JSON content: {content[:500]}")

                try:
                    data = json.loads(content)
                except json.JSONDecodeError as e:
                    logging.error("Malformed JSON. Please check the file content.")
                    raise Exception(f"Error loading products from JSON: {e}")
                
                valid_products = []
                for idx, product_data in enumerate(data):
                    try:
                        valid_products.append(Product(**product_data))
                    except Exception as e:
                        logging.warning(
                            f"Skipping invalid product entry at index {idx}: {product_data} - Error: {e}"
                        )
                
                return valid_products
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            raise Exception(f"Error loading products from JSON: {str(e)}")

