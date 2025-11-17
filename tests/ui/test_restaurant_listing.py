import pytest
import allure
from selenium import webdriver
from pages.restaurant_listing_page import RestaurantListingPage
from pages.food_menu_page import FoodMenuPage


@allure.feature('Restaurant Listing')
class TestRestaurantListing:
    
    @pytest.fixture
    def driver(self):
        """Set up browser before each test and tear down after"""
        options = webdriver.ChromeOptions()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        driver = webdriver.Chrome(options=options)
        driver.maximize_window()
        driver.implicitly_wait(10)
        yield driver
        driver.quit()
    
    @allure.story('Page Load')
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Verify restaurant listing page loads successfully")
    def test_restaurant_listing_page_loads(self, driver):
        """Test 1: Verify restaurant listing page loads successfully"""
        with allure.step("Open restaurant listing page"):
            page = RestaurantListingPage(driver)
            page.open()
        
        with allure.step("Verify page is loaded"):
            assert page.is_loaded(), "Page should contain Harper's"
        
        with allure.step("Count restaurants displayed"):
            restaurant_count = page.get_restaurant_count()
            allure.attach(str(restaurant_count), name="Restaurant Count", attachment_type=allure.attachment_type.TEXT)
            assert restaurant_count >= 1, "Should display at least 1 restaurant"
        
        print(f"✅ Page loaded successfully, displaying {restaurant_count} restaurants")
    
    @allure.story('Restaurant Information')
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Verify restaurant card displays correct information")
    def test_restaurant_has_correct_info(self, driver):
        """Test 2: Verify restaurant card displays correct information"""
        with allure.step("Open restaurant listing page"):
            page = RestaurantListingPage(driver)
            page.open()
        
        with allure.step("Verify restaurant name"):
            restaurant_name = page.get_first_restaurant_name()
            allure.attach(restaurant_name, name="Restaurant Name", attachment_type=allure.attachment_type.TEXT)
            assert restaurant_name == "Harper's Kitchen"
        
        with allure.step("Verify Order Now button exists"):
            assert page.has_order_button(), "Should have Order Now button"
        
        print("✅ Restaurant information displayed correctly")
    
    @allure.story('Navigation')
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Verify clicking Order Now button navigates to menu page")
    def test_click_order_now_navigates_to_menu(self, driver):
        """Test 3: Verify clicking Order Now button navigates to menu page"""
        listing_page = RestaurantListingPage(driver)
        menu_page = FoodMenuPage(driver)
        
        with allure.step("Open restaurant listing page"):
            listing_page.open()
        
        with allure.step("Click first Order Now button"):
            listing_page.click_first_order_button()
        
        with allure.step("Verify navigation to menu page"):
            assert menu_page.is_on_menu_page(), "Should navigate to menu page"
            assert menu_page.has_food_menu_title(), "Should display Food Menu title"
            
            # Attach current URL for verification
            current_url = listing_page.driver.current_url
            allure.attach(current_url, name="Current URL", attachment_type=allure.attachment_type.TEXT)
        
        print("✅ Successfully navigated to menu page")