# app/main.py
from fastapi import FastAPI, HTTPException, Depends, Header
from typing import Optional, Dict
from .services.scraping_service import ScrapingService
from .core.config import settings
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Initialize FastAPI application
app = FastAPI(
    title="Dental Products Scraper",
    description="API for scraping dental products from DentalStall",
    version="1.0.0"
)

# Authentication dependency
async def verify_token(x_token: str = Header(...)):
    """Verify the API token provided in headers"""
    if x_token != settings.API_TOKEN:
        raise HTTPException(
            status_code=401,
            detail="Invalid API token"
        )
    return x_token

@app.get("/health")
async def health_check():
    """Simple health check endpoint"""
    return {
        "status": "healthy",
        "service": "dental-scraper"
    }

@app.post("/scrape")
async def scrape_products(
    page_limit: Optional[int] = None,
    proxy: Optional[str] = None,
    _: str = Depends(verify_token)
):
    """
    Trigger the scraping process
    
    Parameters:
    - page_limit: Optional limit on number of pages to scrape
    - proxy: Optional proxy server to use for requests
    """
    try:
        service = ScrapingService()
        stats = await service.run_scraping(page_limit, proxy)
        return {
            "status": "success",
            "message": "Scraping completed successfully",
            "stats": stats
        }
    except Exception as e:
        logging.error(f"Scraping failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Scraping failed: {str(e)}"
        )

@app.get("/products")
async def get_products(_: str = Depends(verify_token)):
    """Retrieve all scraped products"""
    try:
        service = ScrapingService()
        products = await service.get_stored_products()
        return {
            "status": "success",
            "count": len(products),
            "products": products
        }
    except Exception as e:
        logging.error(f"Failed to retrieve products: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve products: {str(e)}"
        )