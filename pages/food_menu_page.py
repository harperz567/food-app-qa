from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class FoodMenuPage:
    """Page object for food menu page"""
    
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)
        
        # Page elements
        self.food_menu_title = (By.XPATH, "//h2[contains(text(), 'Food Menu')]")
    
    def is_on_menu_page(self):
        """Verify if currently on menu page"""
        return "/food-catalog/" in self.driver.current_url
    
    def has_food_menu_title(self):
        """Verify if Food Menu title exists"""
        try:
            self.wait.until(
                EC.presence_of_element_located(self.food_menu_title)
            )
            return True
        except:
            return False