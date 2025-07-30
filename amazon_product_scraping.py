import pandas as pd
import psycopg2
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By

def create_connection():
    return psycopg2.connect(
        user="postgres",
        password="Raghul@04",
        host="127.0.0.1",
        port="5432",
        database="Players"
    )

def insert_record(p_name, p_seller, p_price, p_ratings, img_url, link, channel, user_id):
    try:
        connection = create_connection()
        cursor = connection.cursor()
        
        p_price = float(p_price.replace(',', '')) if p_price not in ['N/A', ''] else None
        
        p_ratings = float(p_ratings) if p_ratings not in ['N/A', ''] else None

        insert_query = "INSERT INTO inventry (PRODUCT_NAME, SELLER, PRICE, RATINGS, IMAGE_URL, PRODUCT_LINK, CHANNEL, user_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        cursor.execute(insert_query, (p_name, p_seller, p_price, p_ratings, img_url, link,channel, user_id ))
        
        connection.commit()
        print("Record inserted successfully.")
    except psycopg2.Error as error:
        print("Error inserting record:", error)
    finally:
        cursor.close()
        connection.close()



def scrape_amazon_product(urls, user_id):
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(options=options, service=Service(ChromeDriverManager().install()))
    
    data = []
    
    try:
        for web in urls:
            try:
                driver.get(web)
                driver.refresh()
                driver.implicitly_wait(5)
                
                name = driver.find_element(By.ID, 'productTitle').text.strip() if driver.find_elements(By.ID, 'productTitle') else 'N/A'
                seller = driver.find_element(By.ID, 'sellerProfileTriggerId').text.strip() if driver.find_elements(By.ID, 'sellerProfileTriggerId') else 'N/A'
                img = driver.find_element(By.ID, 'landingImage').get_attribute('src') if driver.find_elements(By.ID, 'landingImage') else 'N/A'
                
                price_elements = driver.find_elements(By.CLASS_NAME, 'a-price-whole')
                fraction_elements = driver.find_elements(By.CLASS_NAME, 'a-size-large a-color-price savingPriceOverride aok-align-center reinventPriceSavingsPercentageMargin savingsPercentage')
                
                if price_elements and fraction_elements:
                    price = f"{price_elements[0].text}.{fraction_elements[0].text}"
                elif price_elements:
                    price = price_elements[0].text
                else:
                    price = 'N/A'
                    
                ratings_element = driver.find_elements(By.CLASS_NAME, 'a-size-base a-color-base')
                ratings = ratings_element[0].text.strip() if ratings_element else 'N/A'
                
                insert_record(name, seller, price, ratings, img, web, 'Amazon', user_id)

                data.append({
                    "Product Name": name,
                    "Seller": seller,
                    "Price": price,
                    "Ratings": ratings,
                    "Image URL": img,
                    "Product Link": web,
                    "Channel": "Amazon"                
                })
                
            except Exception as e:
                print(f"Error Scraping {web}: {e}")
    finally:
        driver.quit()
    
    df = pd.DataFrame(data)
    df.to_csv('amazon_products.csv', index=False)
    print("CSV file saved as amazon_products.csv")

file_path = "urls.csv"  
df_urls = pd.read_csv(file_path, header=None)
url_list = df_urls[0].tolist()
# scrape_amazon_product(url_list)
