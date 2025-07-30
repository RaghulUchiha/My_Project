import pandas as pd
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, StaleElementReferenceException
from webdriver_manager.chrome import ChromeDriverManager

def read_dataset(file_path):
    df = pd.read_csv(file_path)
    df.columns = df.columns.str.lower()  
    print("Dataset Loaded Successfully.")
    return df

def apply_pincode(driver, pincode):
    try:
        for _ in range(3):  
            try:
                location_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CLASS_NAME, "LocationBar__SubtitleContainer-sc-x8ezho-9"))
                )
                location_button.click()
                break
            except StaleElementReferenceException:
                print("Retrying location button due to stale reference...")
                time.sleep(2)

        time.sleep(2)

        # Retry finding the search bar
        for _ in range(3):
            try:
                search_bar = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CLASS_NAME, "LocationSearchBox__InputSelect-sc-1k8u6a6-0"))
                )
                search_bar.click()
                break
            except StaleElementReferenceException:
                print("Retrying search bar due to stale reference...")
                time.sleep(2)

        time.sleep(1)
        search_bar.clear()

        # Enter pincode
        for digit in str(pincode):
            search_bar = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CLASS_NAME, "LocationSearchBox__InputSelect-sc-1k8u6a6-0"))
            )
            search_bar.send_keys(digit)
            time.sleep(0.5)

        time.sleep(1)

        # Confirm button
        try:
            confirm_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.CLASS_NAME, "LocationSearchList__LocationListContainer-sc-93rfr7-0"))
            )
            confirm_button.click()
        except TimeoutException:
            print("No confirm button found, pressing Enter.")
            search_bar.send_keys(Keys.RETURN)

        time.sleep(3)

        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.TAG_NAME, "body"))
        ).click()
        time.sleep(2)

        print(f"Pincode {pincode} applied successfully.")

    except (NoSuchElementException, TimeoutException, StaleElementReferenceException) as e:
        print(f"Error applying pincode {pincode}: {e}")

def scrape_product_details(driver, product_url, pincode):
    driver.get(product_url)
    time.sleep(2)

    apply_pincode(driver, pincode)

    try:
        try:
            product_name = driver.find_element(By.XPATH, '//h1[contains(@class, "ProductInfoCard__ProductName-sc-113r60q-10 dsuWXl")]').text
        except NoSuchElementException:
            product_name = "N/A"

        try:
            price_text = driver.find_element(By.XPATH, '//div[contains(@class, "ProductVariants__PriceContainer")]').text

            price_parts = price_text.split()

            cleaned_prices = [part for part in price_parts if "MRP" not in part and "%" not in part and "OFF" not in part]

            price = cleaned_prices[0] if cleaned_prices else "N/A"

        except NoSuchElementException:
            price = "N/A"

        try:
            seller = driver.find_element(By.XPATH, '//div[contains(@class, "ProductAttribute__ProductAttributesDescription-sc-dyoysr-6 jJVAqC")]').text
        except NoSuchElementException:
            seller = "N/A"

        return {
            "Product Name": product_name,
            "Price": price,
            "Seller": seller
        }
    
    except (NoSuchElementException, TimeoutException) as e:
        print(f"Error scraping {product_url}: {e}")
        return None

def main():
    file_path = "BlinkIT_items.csv"
    df = read_dataset(file_path)

    required_columns = {"product_id", "pincode"}
    if not required_columns.issubset(df.columns):
        print(f"Error: CSV file must contain columns {required_columns}")
        return

    product_url_template = "https://blinkit.com/prn/hatsun-curd/prid/{}"

    # Set up WebDriver options
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")  # Increase window size
    options.add_argument("--disable-blink-features=AutomationControlled")  # Avoid detection
    options.add_argument("--ignore-certificate-errors")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    output_data = []
    
    for _, row in df.iterrows():
        product_id = row['product_id']
        pincode = row['pincode']
        product_url = product_url_template.format(product_id)

        product_details = scrape_product_details(driver, product_url, pincode)
        if product_details:
            output_data.append({
                "Product ID": product_id,
                "Pincode": pincode,
                **product_details  
            })
    
    driver.quit()
    
    # Save to CSV
    output_df = pd.DataFrame(output_data)
    output_df.to_csv("BlinkIT_scraped_data.csv", index=False)
    print("Data saved successfully to BlinkIT_scraped_data.csv")

if __name__ == "__main__":
    main()
