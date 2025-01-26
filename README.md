# Dental Products Scraper

## Project Overview
This project implements an advanced web scraping system designed to monitor dental product prices from DentalStall.com. Using modern asynchronous programming techniques and robust design patterns, the scraper efficiently collects product information while respecting website policies and handling errors gracefully.

## Key Features
The scraper incorporates several sophisticated features to ensure reliable and efficient operation:

### Resilient Scraping
The system uses aiohttp for asynchronous HTTP requests and implements comprehensive error handling with automatic retries. When encountering network issues or rate limits, the scraper will pause and retry with exponential backoff, ensuring reliable data collection even under challenging conditions.

### Efficient Caching
A Redis-based caching system efficiently tracks product prices, reducing unnecessary storage operations. The cache stores product prices with a one-hour expiration time, and only products with price changes trigger storage updates. This approach significantly reduces system load and improves performance.

### Multiple Storage Options
The system implements a flexible storage strategy pattern, currently supporting JSON file storage with the ability to easily add new storage backends. The storage system includes robust validation and error handling to ensure data integrity.

### Smart Notification System
Two notification channels are implemented:
- Console notifications for immediate feedback during development
- Email notifications using async SMTP for production monitoring
Both channels use a common interface, making it easy to add new notification methods.

## Technical Architecture

### Core Components

#### Scraper Module
```python
class DentalStallScraper(ScraperStrategy):
    """Handles the core scraping logic with features like:
    - Custom headers and user agent management
    - Rate limiting and retry logic
    - Image downloading and storage
    - Robust HTML parsing"""
```

The scraper includes sophisticated features like:
- Automatic handling of compressed responses
- Customizable request headers
- Intelligent pagination handling
- Concurrent page processing
- Product image downloading with validation

#### Caching System
```python
class RedisCache:
    """Redis-based caching system that:
    - Maintains connection pool
    - Handles authentication
    - Implements retry logic
    - Provides atomic operations"""
```

The cache system efficiently tracks product prices and reduces database load by:
- Storing prices with TTL (Time To Live)
- Handling connection issues gracefully
- Providing atomic operations for price updates

#### Notification System
```python
class NotificationStrategy(ABC):
    """Abstract base for notification systems
    Implementations include:
    - Console notifications
    - Email notifications via SMTP"""
```

The notification system provides real-time updates about:
- Scraping progress and completion
- Error conditions and retries
- Price change detection
- System status updates

## Setup and Installation

1. Clone the repository:
```bash
git clone [repository-url]
cd dental-scraper
```

2. Set up the Python virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your settings:
# SMTP_SERVER=smtp.gmail.com
# SMTP_PORT=587
# EMAIL_SENDER=your-email@gmail.com
# EMAIL_PASSWORD=your-app-password
# EMAIL_RECIPIENT=recipient@email.com
# API_TOKEN=your-secure-token
```

4. Start Redis server:
```bash
redis-server
```

5. Run the application:
```bash
uvicorn app.main:app --reload
```

## API Endpoints

### Health Check
```http
GET /health
```
Returns service health status.

### Trigger Scraping
```http
POST /scrape
Headers: X-Token: your-api-token
Query Parameters:
  - page_limit (optional): Number of pages to scrape
  - proxy (optional): Proxy server to use
```

### Get Products
```http
GET /products
Headers: X-Token: your-api-token
```
Returns all scraped products.

## Error Handling and Logging
The system implements comprehensive error handling and logging:
- Detailed logging of scraping operations
- Error tracking with stack traces
- Automatic retry mechanisms
- Rate limit handling
- Connection error recovery

## Best Practices Implemented
The project follows several software engineering best practices:

### Design Patterns
- Strategy Pattern for scraping, storage, and notifications
- Dependency Injection for flexible component integration
- Factory Pattern for component creation

### Code Organization
- Clear separation of concerns
- Interface-based design
- Comprehensive type hints
- Detailed documentation

### Error Handling
- Graceful degradation
- Automatic retry mechanisms
- Comprehensive logging
- User-friendly error messages

## Future Enhancements
Potential improvements for future versions:

- Advanced proxy rotation system
- Additional storage backends (MongoDB, PostgreSQL)
- More notification channels (Slack, Discord)
- Dashboard for monitoring scraping operations
- Machine learning for price trend analysis

## Contributing
Contributions are welcome! Please read our contributing guidelines and submit pull requests for any enhancements.

## License
This project is licensed under the MIT License - see the LICENSE file for details.