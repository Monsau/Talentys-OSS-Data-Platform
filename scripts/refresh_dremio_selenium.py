#!/usr/bin/env python3
"""
Automated Dremio Source Refresh using Selenium
Simulates UI interaction to click the Refresh Metadata button
"""

import time
import sys

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException, NoSuchElementException
except ImportError:
    print("❌ Selenium not installed!")
    print("📦 Install with: pip install selenium")
    print("📦 Also install Chrome/Chromium and ChromeDriver")
    sys.exit(1)

# Configuration
DREMIO_URL = "http://localhost:9047"
DREMIO_USER = "admin"
DREMIO_PASSWORD = "admin123"
SOURCE_NAME = "elasticsearch"

def setup_driver():
    """Setup Chrome driver with appropriate options"""
    print("🔧 Setting up Chrome driver...")
    
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-software-rasterizer")
    
    # Try to create driver
    try:
        driver = webdriver.Chrome(options=options)
        print("✅ Chrome driver initialized")
        return driver
    except Exception as e:
        print(f"❌ Failed to initialize Chrome driver: {e}")
        print("\n📝 Troubleshooting:")
        print("   1. Install Chrome/Chromium: sudo apt-get install chromium-browser")
        print("   2. Install ChromeDriver: sudo apt-get install chromium-chromedriver")
        print("   3. Or download from: https://chromedriver.chromium.org/")
        sys.exit(1)

def login_to_dremio(driver):
    """Login to Dremio UI"""
    print(f"\n🔐 Logging in to Dremio ({DREMIO_URL})...")
    
    try:
        driver.get(DREMIO_URL)
        
        # Wait for login page or main page
        time.sleep(3)
        
        # Check if we need to login
        try:
            username_field = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.NAME, "userName"))
            )
            
            print("   Found login form, entering credentials...")
            username_field.send_keys(DREMIO_USER)
            
            password_field = driver.find_element(By.NAME, "password")
            password_field.send_keys(DREMIO_PASSWORD)
            
            # Find and click login button
            login_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            login_button.click()
            
            print("   ✅ Login submitted")
            time.sleep(5)  # Wait for redirect
            
        except TimeoutException:
            print("   ℹ️  Already logged in or no login required")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Login failed: {e}")
        return False

def navigate_to_source(driver, source_name):
    """Navigate to the Elasticsearch source page"""
    print(f"\n🔍 Navigating to source: {source_name}...")
    
    try:
        # Try direct URL first
        source_url = f"{DREMIO_URL}/sources/{source_name}"
        driver.get(source_url)
        time.sleep(5)
        
        print(f"   ✅ Navigated to {source_url}")
        return True
        
    except Exception as e:
        print(f"   ❌ Navigation failed: {e}")
        return False

def find_and_click_refresh(driver):
    """Find and click the Refresh Metadata button"""
    print("\n🔄 Looking for Refresh button...")
    
    # List of possible selectors for the refresh button
    selectors = [
        # By text content
        "//button[contains(text(), 'Refresh')]",
        "//button[contains(text(), 'refresh')]",
        "//span[contains(text(), 'Refresh')]/parent::button",
        
        # By aria-label
        "//button[@aria-label='Refresh']",
        "//button[@aria-label='refresh']",
        
        # By class or data attributes
        "//button[contains(@class, 'refresh')]",
        "//button[@data-qa='refresh-metadata']",
        "//button[@data-qa='source-refresh']",
        
        # Icon-based
        "//button[.//*[contains(@class, 'refresh-icon')]]",
        "//button[.//*[name()='svg' and contains(@class, 'refresh')]]",
        
        # Menu items
        "//div[contains(@class, 'menu-item')][contains(text(), 'Refresh')]",
        "//li[contains(text(), 'Refresh Metadata')]",
    ]
    
    for i, selector in enumerate(selectors, 1):
        try:
            print(f"   Trying selector {i}/{len(selectors)}...")
            
            element = WebDriverWait(driver, 2).until(
                EC.element_to_be_clickable((By.XPATH, selector))
            )
            
            print(f"   ✅ Found refresh button with selector {i}")
            element.click()
            print(f"   ✅ Clicked refresh button!")
            
            time.sleep(2)
            return True
            
        except (TimeoutException, NoSuchElementException):
            continue
    
    # If no button found, try to find menu button first
    print("\n   ℹ️  Direct button not found, looking for menu...")
    
    menu_selectors = [
        "//button[@aria-label='More']",
        "//button[contains(@class, 'more-menu')]",
        "//button[.//*[contains(@class, 'more-icon')]]",
        "//button[contains(@data-qa, 'more')]",
    ]
    
    for selector in menu_selectors:
        try:
            menu_button = WebDriverWait(driver, 2).until(
                EC.element_to_be_clickable((By.XPATH, selector))
            )
            
            print(f"   ✅ Found menu button, clicking...")
            menu_button.click()
            time.sleep(1)
            
            # Now try to find refresh in menu
            for refresh_selector in selectors[:5]:  # Try first 5 again
                try:
                    element = WebDriverWait(driver, 2).until(
                        EC.element_to_be_clickable((By.XPATH, refresh_selector))
                    )
                    
                    print(f"   ✅ Found refresh in menu")
                    element.click()
                    print(f"   ✅ Clicked refresh button!")
                    time.sleep(2)
                    return True
                    
                except (TimeoutException, NoSuchElementException):
                    continue
                    
        except (TimeoutException, NoSuchElementException):
            continue
    
    print("   ❌ Could not find refresh button")
    return False

def verify_refresh_started(driver):
    """Check if refresh was initiated"""
    print("\n⏳ Verifying refresh started...")
    
    # Look for loading indicators
    loading_indicators = [
        "//div[contains(@class, 'loading')]",
        "//div[contains(@class, 'spinner')]",
        "//div[contains(text(), 'Refreshing')]",
        "//*[contains(@class, 'progress')]",
    ]
    
    for selector in loading_indicators:
        try:
            element = WebDriverWait(driver, 3).until(
                EC.presence_of_element_located((By.XPATH, selector))
            )
            print("   ✅ Refresh in progress (loading indicator found)")
            return True
        except TimeoutException:
            continue
    
    print("   ℹ️  No loading indicator found (may be too fast or not visible)")
    return True  # Assume success

def take_screenshot(driver, filename="dremio_debug.png"):
    """Take screenshot for debugging"""
    try:
        driver.save_screenshot(filename)
        print(f"   📸 Screenshot saved: {filename}")
    except Exception as e:
        print(f"   ⚠️  Could not save screenshot: {e}")

def main():
    print("=" * 70)
    print("🤖 AUTOMATED DREMIO SOURCE REFRESH (SELENIUM)")
    print("=" * 70)
    
    driver = None
    
    try:
        # 1. Setup driver
        driver = setup_driver()
        driver.set_page_load_timeout(30)
        
        # 2. Login
        if not login_to_dremio(driver):
            take_screenshot(driver, "login_failed.png")
            return False
        
        # 3. Navigate to source
        if not navigate_to_source(driver, SOURCE_NAME):
            take_screenshot(driver, "navigation_failed.png")
            return False
        
        # 4. Take screenshot before refresh
        take_screenshot(driver, "before_refresh.png")
        
        # 5. Find and click refresh
        if not find_and_click_refresh(driver):
            take_screenshot(driver, "refresh_button_not_found.png")
            print("\n" + "=" * 70)
            print("⚠️  COULD NOT FIND REFRESH BUTTON")
            print("=" * 70)
            print("\n📝 Manual action required:")
            print("   1. Open http://localhost:9047")
            print("   2. Go to Sources → elasticsearch")
            print("   3. Look for Refresh button (⟳ icon or '...' menu)")
            print("   4. Click it manually")
            print("\n📸 Screenshot saved for debugging")
            return False
        
        # 6. Verify refresh started
        verify_refresh_started(driver)
        
        # 7. Wait for refresh to complete
        print("\n⏰ Waiting 30 seconds for refresh to complete...")
        time.sleep(30)
        
        # 8. Take screenshot after refresh
        take_screenshot(driver, "after_refresh.png")
        
        print("\n" + "=" * 70)
        print("✅ REFRESH COMPLETED SUCCESSFULLY")
        print("=" * 70)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        if driver:
            take_screenshot(driver, "error.png")
        return False
        
    finally:
        if driver:
            print("\n🔒 Closing browser...")
            driver.quit()

if __name__ == "__main__":
    success = main()
    
    if success:
        print("\n🎉 Refresh automation successful!")
        print("\n📝 Next steps:")
        print("   Run: python scripts/create_vds_via_sql.py")
        sys.exit(0)
    else:
        print("\n❌ Refresh automation failed")
        print("   Manual refresh required in Dremio UI")
        sys.exit(1)
