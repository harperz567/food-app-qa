"""Configuration file for test environment settings"""


class Config:
    """Test configuration settings"""
    
    # Base URLs
    BASE_URL = "http://localhost:4200"
    RESTAURANT_LISTING_URL = f"{BASE_URL}/restaurant-listing"
    
    # API endpoints
    API_BASE_URL = "http://localhost"
    ORDER_SERVICE_PORT = 8082
    USER_SERVICE_PORT = 9093
    RESTAURANT_SERVICE_PORT = 8083
    PAYMENT_SERVICE_PORT = 9095
    FOOD_CATALOG_SERVICE_PORT = 8084
    
    # Service URLs (for API testing)
    ORDER_SERVICE_URL = f"{API_BASE_URL}:{ORDER_SERVICE_PORT}"
    USER_SERVICE_URL = f"{API_BASE_URL}:{USER_SERVICE_PORT}"
    RESTAURANT_SERVICE_URL = f"{API_BASE_URL}:{RESTAURANT_SERVICE_PORT}"
    PAYMENT_SERVICE_URL = f"{API_BASE_URL}:{PAYMENT_SERVICE_PORT}"
    FOOD_CATALOG_SERVICE_URL = f"{API_BASE_URL}:{FOOD_CATALOG_SERVICE_PORT}"
    
    # Timeouts
    DEFAULT_TIMEOUT = 10
    LONG_TIMEOUT = 30
    
    # Browser settings
    HEADLESS = False  # Set to True to run tests without opening browser
    MAXIMIZE_WINDOW = True