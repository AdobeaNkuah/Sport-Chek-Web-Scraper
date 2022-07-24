# Sport-Chek-Web-Scraper
A web scraper which navigates Sport Chek's product category web pages, extracts product information, and exports the data to a SQL database

## Installation 
This script is compatible with python3 and Windows. To run this script the following prerequisites MUST be met.

### Prerequisites

```python
pip install bs4
pip install sqllite3
pip install pandas
pip install selenium
```

An installation of Chrome Beta, the python script will update it automatically.
Chrome Beta download available here: https://www.google.com/intl/en_ca/chrome/beta/
The Chrome Beta application should be saved to the file path "C:\Program Files\Google\Chrome Beta\Application"

## How to Use
Paste the URLs of the Sport Chek categories to be scraped in the "urls.txt" file line by line. Here are some examples:

```text
https://www.sportchek.ca/categories/women/footwear/hiking-outdoor-shoes.html?page=1
https://www.sportchek.ca/categories/shop-by-sport/training/mens-training/mens-training-long-sleeves.html?page=1
https://www.sportchek.ca/categories/electronics/headphones-speakers/headphones.html?page=1
```

Please note that the URLs used in this script MUST contain the producr page number at the end.

```python
c.execute('''CREATE TABLE product_information(product_number INTEGER PRIMARY KEY, product_name TEXT,
            price TEXT, product_on_sale TEXT, product_categories TEXT, product_description TEXT, image_address TEXT)''')
```

To overrite the information saved to the database uncomment the statement below and run the script again.

```python
c.execute('''DROP TABLE product_information''')  # Include after table creation to delete table for next testing round
```

## Results
