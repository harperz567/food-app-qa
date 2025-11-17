from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class RestaurantListingPage:
    """Page object for restaurant listing page"""
    
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)
        
        # Page element locators (centralized in one place)
        self.order_now_button = (By.XPATH, "//button[contains(text(), 'Order Now')]")
        self.restaurant_name = (By.XPATH, "//h3[contains(text(), \"Harper's Kitchen\")]")
        self.page_title = (By.XPATH, "//*[contains(text(), \"Harper's\")]")
    
    def open(self):
        """Navigate to restaurant listing page"""
        self.driver.get("http://localhost:4200/restaurant-listing")
    
    def is_loaded(self):
        """Verify if page is loaded successfully"""
        return "Harper's" in self.driver.page_source
    
    def get_restaurant_count(self):
        """Get the number of restaurants displayed on the page"""
        buttons = self.wait.until(
            EC.presence_of_all_elements_located(self.order_now_button)
        )
        return len(buttons)
    
    def get_first_restaurant_name(self):
        """Get the name of the first restaurant"""
        element = self.wait.until(
            EC.presence_of_element_located(self.restaurant_name)
        )
        return element.text
    
    def click_first_order_button(self):
        """Click the first Order Now button"""
        button = self.wait.until(
            EC.element_to_be_clickable(self.order_now_button)
        )
        button.click()
    
    def has_order_button(self):
        """Check if Order Now button exists"""
        try:
            self.driver.find_element(*self.order_now_button)
            return True
        except:
            return False