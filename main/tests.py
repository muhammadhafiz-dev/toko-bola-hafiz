from django.test import TestCase, Client
from .models import Product
from django.test import LiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from django.contrib.auth.models import User

#untuk mengetes apakah semua fungsi berjalan lancar
class MainTest(TestCase):
    def test_main_url_is_exist(self):
        response = Client().get('')
        self.assertEqual(response.status_code, 200)

    def test_main_using_main_template(self):
        response = Client().get('')
        self.assertTemplateUsed(response, 'main.html')

    def test_nonexistent_page(self):
        response = Client().get('/burhan_always_exists/')
        self.assertEqual(response.status_code, 404)

    def test_product_creation(self):
        product = Product.objects.create(
          name="BURHAN FC MENANG",
          description="BURHAN FC 1-0 PANDA BC",
          category="match",
          product_views=1001,
          is_featured=True
        )
        self.assertTrue(product.is_product_hot)
        self.assertEqual(product.category, "match")
        self.assertTrue(product.is_featured)
        
    def test_product_default_values(self):
        product = Product.objects.create(
          name="Test Product",
          description="Test description"
        )
        self.assertEqual(product.category, "update")
        self.assertEqual(product.product_views, 0)
        self.assertFalse(product.is_featured)
        self.assertFalse(product.is_product_hot)
        
    def test_increment_views(self):
        product = Product.objects.create(
          name="Test Product",
          description="Test description"
        )
        initial_views = product.product_views
        product.increment_views()
        self.assertEqual(product.product_views, initial_views + 1)
        
    def test_is_product_hot_threshold(self):
        # Test product with exactly 20 views (should not be hot)
        product_20 = Product.objects.create(
          name="Product with 20 views",
          description="Test description",
          product_views=20
        )
        self.assertFalse(product_20.is_product_hot)
        
        # Test product with 21 views (should be hot)
        product_21 = Product.objects.create(
          name="Product with 21 views", 
          description="Test description",
          product_views=21
        )
        self.assertTrue(product_21.is_product_hot)

class TokoBolaHafizFunctionalTest(LiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Create single browser instance for all tests
        cls.browser = webdriver.Chrome()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        # Close browser after all tests complete
        cls.browser.quit()

    def setUp(self):
        # Create user for testing
        self.test_user = User.objects.create_user(
            username='testadmin',
            password='testpassword'
        )

    def tearDown(self):
        # Clean up browser state between tests
        self.browser.delete_all_cookies()
        self.browser.execute_script("window.localStorage.clear();")
        self.browser.execute_script("window.sessionStorage.clear();")
        # Navigate to blank page to reset state
        self.browser.get("about:blank")

    def login_user(self):
        """Helper method to login user"""
        self.browser.get(f"{self.live_server_url}/login/")
        username_input = self.browser.find_element(By.NAME, "username")
        password_input = self.browser.find_element(By.NAME, "password")
        username_input.send_keys("testadmin")
        password_input.send_keys("testpassword")
        password_input.submit()

    def test_login_page(self):
        # Test login functionality
        self.login_user()

        # Check if login is successful
        wait = WebDriverWait(self.browser, 120)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "h1")))
        h1_element = self.browser.find_element(By.TAG_NAME, "h1")
        self.assertEqual(h1_element.text, "Toko Bola Hafiz")

        logout_link = self.browser.find_element(By.PARTIAL_LINK_TEXT, "Logout")
        self.assertTrue(logout_link.is_displayed())

    def test_register_page(self):
        # Test register functionality
        self.browser.get(f"{self.live_server_url}/register/")

        # Check if register page opens
        h1_element = self.browser.find_element(By.TAG_NAME, "h1")
        self.assertEqual(h1_element.text, "Register")

        # Fill register form
        username_input = self.browser.find_element(By.NAME, "username")
        password1_input = self.browser.find_element(By.NAME, "password1")
        password2_input = self.browser.find_element(By.NAME, "password2")

        username_input.send_keys("newuser")
        password1_input.send_keys("complexpass123")
        password2_input.send_keys("complexpass123")
        password2_input.submit()

        # Check redirect to login page
        wait = WebDriverWait(self.browser, 120)
        wait.until(EC.text_to_be_present_in_element((By.TAG_NAME, "h1"), "Login"))
        login_h1 = self.browser.find_element(By.TAG_NAME, "h1")
        self.assertEqual(login_h1.text, "Login")

    def test_create_product(self):
        # Test create product functionality (requires login)
        self.login_user()

        # Go to create product page
        add_button = self.browser.find_element(By.PARTIAL_LINK_TEXT, "Add Product")
        add_button.click()

        # Fill form
        name_input = self.browser.find_element(By.NAME, "name")
        description_input = self.browser.find_element(By.NAME, "description")
        category_select = self.browser.find_element(By.NAME, "category")
        thumbnail_input = self.browser.find_element(By.NAME, "thumbnail")
        is_featured_checkbox = self.browser.find_element(By.NAME, "is_featured")

        name_input.send_keys("Test Product Name")
        description_input.send_keys("Test product description for selenium testing")
        thumbnail_input.send_keys("https://example.com/image.jpg")

        # Set category (select 'match' from dropdown)

        select = Select(category_select)
        select.select_by_value("match")

        # Check is_featured checkbox
        is_featured_checkbox.click()

        # Submit form
        name_input.submit()

        # Check if returned to main page and product appears
        wait = WebDriverWait(self.browser, 120)
        wait.until(EC.text_to_be_present_in_element((By.TAG_NAME, "h1"), "Football Product"))
        h1_element = self.browser.find_element(By.TAG_NAME, "h1")
        self.assertEqual(h1_element.text, "Football Product")

        # Check if product name appears on page
        wait.until(EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, "Test Product Name")))
        product_name = self.browser.find_element(By.PARTIAL_LINK_TEXT, "Test Product Name")
        self.assertTrue(product_name.is_displayed())

    def test_product_detail(self):
        # Test product detail page

        # Login first because of @login_required decorator
        self.login_user()

        # Create product for testing
        product = Product.objects.create(
            name="Detail Test Product",
            description="Description for detail testing",
            user=self.test_user
        )

        # Open product detail page
        self.browser.get(f"{self.live_server_url}/product/{product.id}/")

        # Check if detail page opens correctly
        self.assertIn("Detail Test Product", self.browser.page_source)
        self.assertIn("Description for detail testing", self.browser.page_source)

    def test_logout(self):
        # Test logout functionality
        self.login_user()

        # Click logout button - text is inside button, not link
        logout_button = self.browser.find_element(By.XPATH, "//button[contains(text(), 'Logout')]")
        logout_button.click()

        # Check if redirected to login page
        wait = WebDriverWait(self.browser, 120)
        wait.until(EC.text_to_be_present_in_element((By.TAG_NAME, "h1"), "Login"))
        h1_element = self.browser.find_element(By.TAG_NAME, "h1")
        self.assertEqual(h1_element.text, "Login")

    def test_filter_main_page(self):
        # Test filter functionality on main page
        #         
        # Create product for testing
        Product.objects.create(
            name="My Test Product",
            description="My product description",
            user=self.test_user
        )
        Product.objects.create(
            name="Other User Product", 
            description="Other description",
            user=self.test_user  # Same user for simplicity
        )

        self.login_user()

        # Test filter "All Articles"
        wait = WebDriverWait(self.browser, 120)
        wait.until(EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, "All Articles")))
        all_button = self.browser.find_element(By.PARTIAL_LINK_TEXT, "All Articles")
        all_button.click()
        self.assertIn("My Test Product", self.browser.page_source)
        self.assertIn("Other User Product", self.browser.page_source)

        # Test filter "My Articles"  
        my_button = self.browser.find_element(By.PARTIAL_LINK_TEXT, "My Articles")
        my_button.click()
        self.assertIn("My Test Product", self.browser.page_source)

#field price, category, thumbnail belum dibuat ujicoba testingnya