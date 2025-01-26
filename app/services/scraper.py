# app/services/scraper.py
from abc import ABC, abstractmethod
from bs4 import BeautifulSoup
import aiohttp
from aiohttp import ClientSession, TCPConnector, ClientTimeout
from bs4 import BeautifulSoup
import asyncio
from decimal import Decimal
import os
from typing import List, Optional
from ..schemas.product import Product
from ..core.config import settings
import logging
import brotli

class ScraperStrategy(ABC):
    """Abstract base class for scraping strategies"""
    
    @abstractmethod
    async def scrape(self, page_limit: Optional[int] = None, proxy: Optional[str] = None) -> List[Product]:
        pass

class DentalStallScraper(ScraperStrategy):
    """Concrete implementation for scraping DentalStall website"""

    def __init__(self):
        self.timeout = ClientTimeout(total=30, connect=10)
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache'
        }

    

    async def fetch_page(self, session: ClientSession, url: str, retry_count: int = 0) -> Optional[str]:
        """Enhanced fetch_page method with better error handling"""
        try:
            async with session.get(url, timeout=self.timeout, allow_redirects=True) as response:
                logging.debug(f"Fetching URL: {url}, Status: {response.status}")

                if response.status == 200:
                    content = await response.text()
                    if not content.strip():
                        logging.error(f"Empty response received from {url}")
                        return None
                    return content
                else:
                    logging.error(f"HTTP {response.status} for URL: {url}")
                    
                    if retry_count < settings.DEFAULT_RETRY_ATTEMPTS:
                        wait_time = settings.RETRY_DELAY * (retry_count + 1)
                        logging.warning(f"Retrying {url} after {wait_time} seconds...")
                        await asyncio.sleep(wait_time)
                        return await self.fetch_page(session, url, retry_count + 1)
                    raise Exception(f"Failed to fetch {url} after {retry_count} retries")

        except asyncio.TimeoutError:
            logging.error(f"Timeout fetching {url}")
            if retry_count < settings.DEFAULT_RETRY_ATTEMPTS:
                await asyncio.sleep(settings.RETRY_DELAY)
                return await self.fetch_page(session, url, retry_count + 1)
            raise

        except Exception as e:
            logging.error(f"Error fetching {url}: {str(e)}")
            if retry_count < settings.DEFAULT_RETRY_ATTEMPTS:
                await asyncio.sleep(settings.RETRY_DELAY)
                return await self.fetch_page(session, url, retry_count + 1)
            raise


    async def download_image(self, session: ClientSession, image_url: str, product_title: str) -> str:
        """
        Downloads and saves a product image with proper error handling and validation.
        Returns the path where the image was saved.
        """
        try:
            safe_title = "".join(c for c in product_title if c.isalnum() or c in (' ', '-', '_'))
            safe_title = safe_title[:50].strip()
            filename = f"{safe_title}.jpg"
            
            os.makedirs(settings.IMAGE_STORAGE_PATH, exist_ok=True)
            filepath = os.path.join(settings.IMAGE_STORAGE_PATH, filename)
            
            # Download image with timeout
            async with session.get(image_url, timeout=30) as response:
                if response.status != 200:
                    logging.error(f"Failed to download image for {product_title}: HTTP {response.status}")
                    return ""
                    
                # Read and save image content
                image_data = await response.read()
                if not image_data:
                    logging.error(f"No image data received for {product_title}")
                    return ""
                    
                with open(filepath, 'wb') as f:
                    f.write(image_data)
                    
                logging.debug(f"Successfully saved image for {product_title} to {filepath}")
                return filepath
                
        except Exception as e:
            logging.error(f"Error downloading image for {product_title}: {str(e)}")
            return ""

    async def scrape(self, page_limit: Optional[int] = None, proxy: Optional[str] = None) -> List[Product]:
        """
        Main scraping method that coordinates the entire scraping process.
        This method manages the session, handles pagination, and collects all products.
        """
        all_products = []

        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Referer': 'https://dentalstall.com/',
            'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1'
        }

        cookie_jar = aiohttp.CookieJar(unsafe=True)

        try:
            async with aiohttp.ClientSession(
                headers=self.headers,
                cookie_jar=cookie_jar,
                connector=aiohttp.TCPConnector(ssl=False)
            ) as session:
                html = await self.fetch_page(session, settings.BASE_URL)
                soup = BeautifulSoup(html, 'html.parser')

                logging.debug(f"Fetched page content: {html[:500]}")

                
                total_pages = self.get_total_pages(soup)
                if page_limit:
                    total_pages = min(total_pages, page_limit)
                
                logging.info(f"Starting scrape of {total_pages} pages")
                
                tasks = []
                for page in range(1, total_pages + 1):
                    url = f"{settings.BASE_URL}page/{page}/"
                    tasks.append(self.scrape_page(session, url))
                
                page_results = await asyncio.gather(*tasks, return_exceptions=True)
                
                for result in page_results:
                    if isinstance(result, Exception):
                        logging.error(f"Error scraping page: {str(result)}")
                        continue
                    all_products.extend(result)
                
                logging.info(f"Successfully scraped {len(all_products)} products total")
                return all_products

        except Exception as e:
            logging.error(f"Error in scraping process: {str(e)}")
            raise

    async def scrape_page(self, session: ClientSession, url: str) -> List[Product]:
        """
        Scrapes a single page of products from DentalStall.
        The site uses WooCommerce with a custom theme structure.
        """
        products_on_page = []
        
        try:
            html = await self.fetch_page(session, url)
            soup = BeautifulSoup(html, 'html.parser')
            
            product_elements = soup.find_all('li', class_='product')
            logging.info(f"Found {len(product_elements)} product elements on {url}")
            
            for element in product_elements:
                try:
                    title_container = element.find('h2', class_='woo-loop-product__title')
                    if title_container and title_container.a:
                        title = title_container.a.text.strip()
                    else:
                        continue
                    
                    price_container = element.find('div', class_='mf-product-price-box')
                    if not price_container:
                        continue
                        
                    price_element = (
                        price_container.find('ins', recursive=True) or 
                        price_container.find('span', class_='woocommerce-Price-amount', recursive=True)
                    )
                    
                    if not price_element:
                        continue
                    
                    amount_element = price_element.find('bdi')
                    if not amount_element:
                        continue
                        
                    price_text = amount_element.text.strip()
                    price = Decimal(
                        price_text.replace('₹', '')
                        .replace(',', '')
                        .replace('/-', '')
                        .strip()
                    )
                    
                    img_container = element.find('div', class_='mf-product-thumbnail')
                    if not img_container:
                        continue
                        
                    img_element = img_container.find('img')
                    if not img_element:
                        continue
                    
                    image_url = (
                        img_element.get('data-lazy-src') or 
                        img_element.get('src')
                    )
                    
                    if not image_url or image_url.endswith('svg+xml'):
                        continue
                    
                    image_path = await self.download_image(session, image_url, title)
                    if not image_path:
                        continue
                    
                    product = Product(
                        product_title=title,
                        product_price=price,
                        path_to_image=image_path
                    )
                    
                    products_on_page.append(product)
                    logging.info(f"Successfully processed product: {title} - ₹{price}")
                    
                except Exception as e:
                    logging.error(f"Error processing product: {str(e)}", exc_info=True)
                    continue
            
            return products_on_page
            
        except Exception as e:
            logging.error(f"Error scraping page {url}: {str(e)}", exc_info=True)
            return products_on_page

    def get_total_pages(self, soup: BeautifulSoup) -> int:
        """
        Extract total number of pages from the pagination.
        The website shows pagination like: 1, 2, 3, 4, ..., 117, 118, 119
        """
        try:
            pagination = soup.find('ul', class_='page-numbers')
            if not pagination:
                logging.warning("No pagination found, defaulting to 1 page")
                return 1

            page_numbers = pagination.find_all('a', class_='page-numbers')
            
            if not page_numbers:
                return 1

            max_page = 1
            for page in page_numbers:
                if 'next' in page.get('class', []):
                    continue
                    
                try:
                    page_num = int(page.text.strip())
                    max_page = max(max_page, page_num)
                except ValueError:
                    continue

            logging.info(f"Total pages found: {max_page}")
            return max_page

        except Exception as e:
            logging.error(f"Error determining total pages: {str(e)}")
            return 1