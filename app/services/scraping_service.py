# app/services/scraping_service.py
import logging
from typing import Dict, List, Optional
from .scraper import ScraperStrategy, DentalStallScraper
from .storage import StorageStrategy, JsonFileStorage
from .notifier import EmailNotifier, NotificationStrategy, ConsoleNotifier
from ..cache.redis_cache import RedisCache
from ..schemas.product import Product
from decimal import Decimal

class ScrapingService:
    """Main service class that orchestrates scraping, storage, and notification"""
    
    def __init__(
        self,
        scraper: ScraperStrategy = DentalStallScraper(),
        storage: StorageStrategy = JsonFileStorage(),
        conoleNotifier: NotificationStrategy = ConsoleNotifier(),
        emailNotifier: NotificationStrategy = EmailNotifier(),
        cache: RedisCache = RedisCache()
    ):
        self.scraper = scraper
        self.storage = storage
        self.conoleNotifier = conoleNotifier
        self.emailNotifier = emailNotifier
        self.cache = cache

    async def process_scraped_products(
        self,
        products: List[Product]
    ) -> Dict[str, int]:
        """Process scraped products and update storage if needed"""
        stats = {"total": len(products), "updated": 0}
        
        existing_products = await self.storage.load_products()
        existing_dict = {p.product_title: p for p in existing_products}

        print(products,"products")
        
        products_to_update = []
        for product in products:
            print(f"Scraped product: {product.product_title} - {product.product_price}")
            cached_price = await self.cache.get_product_price(product.product_title)
            print(f"Cached price for {product.product_title}: {cached_price}")


            if cached_price is None or cached_price != float(product.product_price):
                products_to_update.append(product)
                await self.cache.set_product_price(
                    product.product_title,
                    float(product.product_price)
                )
                stats["updated"] += 1


        if products_to_update:
            await self.storage.save_products(products_to_update)

        return stats

    async def run_scraping(
        self,
        page_limit: Optional[int] = None,
        proxy: Optional[str] = None
    ) -> None:
        """Run the complete scraping process"""
        try:
            # Scrape products
            products = await self.scraper.scrape(page_limit, proxy)
            
            stats = await self.process_scraped_products(products)
            
            message = (
                f"Scraping completed successfully!\n"
                f"Total products scraped: {stats['total']}\n"
                f"Products updated: {stats['updated']}"
            )
            await self.conoleNotifier.notify(message)
            await self.emailNotifier.notify("Scraping completed successfully!")
            
        except Exception as e:
            error_message = f"Scraping failed: {str(e)}"
            await self.conoleNotifier.notify(error_message)
            raise