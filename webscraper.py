from bs4 import BeautifulSoup as Soup
import sqlite3
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# Create database
connect = sqlite3.connect('sportchek.db')
c = connect.cursor()

# c.execute('''DROP TABLE product_information''')  # Include after table creation to delete table for next testing round

# Run table creation
c.execute('''CREATE TABLE product_information(product_number INTEGER PRIMARY KEY, product_name TEXT,
            price TEXT, product_on_sale TEXT, product_categories TEXT, product_description TEXT, image_address TEXT)''')


def load_driver_path():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.binary_location = "C:\Program Files\Google\Chrome Beta\Application\chrome.exe"
    # Update Chrome Beta to most recent driver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager(version='104.0.5112.20').install()),
                              options=chrome_options)
    return driver


def read_category_url_file():
    url_file = open('urls.txt', 'r')
    category_urls = url_file.readlines()
    return category_urls


def page_navigate(category_url):
    # Increment the page number, ex: "......html?page=1" --> ".....html?page=2"
    page_number = str(int(category_url[-1]) + 1)
    next_url = category_url[:-1] + page_number
    return next_url


# Method to load product URLS on category webpage to list
def load_product_urls(driver, category_url):
    driver.get(category_url)

    # Create list of product page urls
    product_urls = []
    product_elements = driver.find_elements(By.XPATH, "//*[contains(@class, 'product-details')]//*[contains(@class, "
                                                      "'product-grid__link')]")

    for product in product_elements:
        product_urls.append(product.get_attribute("href"))
    return product_urls


# Method to export webscraping data to SQL database
def export_to_database(number, name, price, sale, categories, description, image):
    # Insert scrapped data into table
    c.execute('''INSERT INTO product_information VALUES(?,?,?,?,?,?,?)''',
              (number, name, price, sale, categories, description, image))
    connect.commit()


# Method to acquire
#     1. Product number
#     2. Product name
#     3. Price
#     4. Is product on sale?
#     5. Product categories
#     6. Product description
#     7. Embedded Images (Image address)


def get_product_information(driver, product_urls, category_url):
    driver.get(category_url)

    # Stop if there are no more pages/products in category
    if not driver.find_elements(By.CLASS_NAME, "product-grid__link"):
        return

    # Iterate through product url list
    for url in product_urls:
        # Extract webpage html data
        driver.get(url)
        product_data = driver.find_element(By.TAG_NAME, "html").get_attribute('innerHTML')
        soup = Soup(product_data, features="html.parser")

        # Get product number
        number_element = soup.find("em", class_="product-detail__description-item-num")
        product_number = int(number_element.find("span", id="product-detail__description-style-num").getText())

        # Get product name
        name_element = soup.find("div", class_="product-detail__title")
        product_name = name_element.find("h1", class_="global-page-header__title").getText()

        # Get price
        # If product is on clearance find the sale element and load sale price
        if soup.find("div", class_="product-detail__price-wrap bundles-sidebar__item_out"):
            price_element = soup.find("div", class_="product-detail__price-wrap bundles-sidebar__item_out")
            product_price = price_element.find("div", class_="product-detail__now-price-text").getText()
            product_on_sale = 'YES'
        else:
            price_element = soup.find("div", class_="product-detail__price-wrap")
            product_price = price_element.find("span", class_="product-detail__price-text").getText()
            product_on_sale = 'NO'

        # Get product category
        product_categories = []  # list for all 4 categories associated with product
        category_elements = soup.find_all("a", class_="page-breadcrumb__link")
        for element in category_elements:
            product_categories.append(element.find("span").getText().strip())
        product_category = str(', '.join(product_categories))

        # Get product description
        description_element = soup.find("div", class_="product-description-blurb__text")

        if description_element.find("p"):  # Check Sport Chek devs used 'p' tag to contain product description
            product_description = description_element.find("p").getText()
        else:
            product_description = description_element.getText().strip()

        # Get image addresses
        product_detail_element = soup.find("div", class_="product-detail__mobile-gallery-item")
        image_element = product_detail_element.select('div img')
        image_address = str(image_element[0]['src'])

        # Load scraped data to database after each iteration
        export_to_database(product_number, product_name, product_price, product_on_sale, product_category,
                           product_description, image_address)

    # Recursively call information extraction method to get product information of next the page
    next_url = page_navigate(category_url)
    product_urls = load_product_urls(driver, next_url)
    get_product_information(driver, product_urls, next_url)


def main():
    driver = load_driver_path()
    category_urls = read_category_url_file()

    for url in category_urls:
        product_urls = load_product_urls(driver, url.strip())
        get_product_information(driver, product_urls, url.strip())

    # Display results using pandas framework
    results = pd.read_sql_query("SELECT * FROM product_information", connect)
    print(results.to_string())

    driver.close()
    driver.quit()


if __name__ == "__main__":
    main()