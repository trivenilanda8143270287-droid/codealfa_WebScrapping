from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time

# Start Chrome
options = webdriver.ChromeOptions()
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option("useAutomationExtension", False)

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=options
)

try:
    driver.get("https://www.flipkart.com/search?q=mobiles&sort=popularity")
    print("Website Opened")

    # Close login popup if it appears
    try:
        close_btn = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button._2KpZ6l._2doB4z"))
        )
        close_btn.click()
        print("Login popup closed")
    except:
        pass

    # Wait for products to load
    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-id]"))
    )
    time.sleep(2)

    data = []

    # Get all 24 product cards on the page
    product_cards = driver.find_elements(By.CSS_SELECTOR, "div[data-id]")
    print(f"Total Product Cards Found: {len(product_cards)}")

    for i, card in enumerate(product_cards):
        title = ""
        price = ""
        rating = ""
        link = ""

        # --- Title: try known classes + fallback to anchor tag text ---
        for cls in ["RG5Slk","KzDlHZ", "WKTcLC", "IRpwTa", "s1Q9rs", "_4rR01T", "col col-7-12"]:
            try:
                elems = card.find_elements(By.CLASS_NAME, cls)
                if elems and elems[0].text.strip():
                    title = elems[0].text.strip()
                    break
            except:
                pass

        if not title:
            try:
                # Fallback: first anchor tag with meaningful text
                anchors = card.find_elements(By.TAG_NAME, "a")
                for a in anchors:
                    t = a.get_attribute("title") or a.text.strip()
                    if t and len(t) > 10:
                        title = t
                        break
            except:
                pass

        # --- Price: try known classes ---
        for cls in ["hZ3P6w","Nx9bqj", "_30jeq3", "hl05eU", "_1vC4OE", "price"]:
            try:
                elems = card.find_elements(By.CLASS_NAME, cls)
                if elems and elems[0].text.strip():
                    price = elems[0].text.strip()
                    break
            except:
                pass

        # --- Rating ---
        for cls in ["MKiFS6","XQDdHH", "_3LWZlK", "gUuXy-"]:
            try:
                elems = card.find_elements(By.CLASS_NAME, cls)
                if elems and elems[0].text.strip():
                    rating = elems[0].text.strip()
                    break
            except:
                pass

        # --- Product Link ---
        try:
            a_tag = card.find_element(By.TAG_NAME, "a")
            link = a_tag.get_attribute("href")
        except:
            pass

        if title or price:
            print(f"[{i+1}] {title} | {price} | Rating: {rating}")
            data.append({
                "Product": title,
                "Price": price,
                "Rating": rating,
                "Link": link
            })

    print(f"\nTotal Records Collected: {len(data)}")

    if data:
        df = pd.DataFrame(data)
        print(df.to_string())
        df.to_excel("flipkart_data.xlsx", index=False)
        print("\nExcel File Saved: flipkart_data.xlsx")
    else:
        print("\nNo data found — Flipkart may have updated class names.")
        print("Run this to inspect live class names:")
        print('  cards = driver.find_elements(By.CSS_SELECTOR, "div[data-id]")')
        print('  print(cards[0].get_attribute("innerHTML"))')

finally:
    driver.quit()
