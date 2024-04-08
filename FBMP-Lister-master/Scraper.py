from collections import defaultdict
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
import math
import threading
import os
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

import Utils
from Product import Product

products = []  # List of products
imageDict = defaultdict(list)  # Dictionary of images
dictionaryId = 0  # ID of the product in the dictionary

# Default values
defaultFacebookFee = 5.0
defaultSalesTax = 7.5
defaultAdditionalProfit = 10.0

# try to set up a cleaner session for fault tolerance
def setup_session():
    session = requests.Session()
    retries = Retry(total=5, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
    adapter = HTTPAdapter(max_retries=retries)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session

class Scraper:
    def __init__(self, dbManager, settingsManager):
        self.dbManager = dbManager
        self.settingsManager = settingsManager
        self.productDirectoryName = "Products Directory"
        self.batchNumber = Utils.getNextBatchNumber(self.productDirectoryName)
        self.session = setup_session()

    def calculateFinalPrice(self, price):
        try:
            currentFacebookFee = self.settingsManager.settings.get('facebookFee', defaultFacebookFee)
            currentSalesTax = self.settingsManager.settings.get('salesTax', defaultSalesTax)
            currentAdditionalProfit = self.settingsManager.settings.get('additionalProfit', defaultAdditionalProfit)

            priceWithFee = price + (price * currentFacebookFee / 100)
            priceWithTax = priceWithFee + (priceWithFee * currentSalesTax / 100)
            priceWithProfit = priceWithTax + (priceWithTax * currentAdditionalProfit / 100)
            finalPrice = math.ceil(priceWithProfit)
            return finalPrice
        except Exception as e:
            print(f"Error calculating final price: {e}")
            return price  # Fallback to original price if calculation fails

    def getTitle(self, soup):
        h1Element = soup.find('h1', class_='x-item-title__mainTitle')
        if h1Element:
            spanElement = h1Element.find('span', class_='ux-textspans ux-textspans--BOLD')
            if spanElement:
                return spanElement.get_text()
            else:
                print("Nested <span> element not found.")
        else:
            print("<h1> element not found.")

    def getPrice(self, soup):
        priceDiv = soup.find('div', class_='x-price-primary')
        if priceDiv:
            priceSpan = priceDiv.find('span', class_='ux-textspans')
            if priceSpan:
                price = priceSpan.get_text()
                strippedPrice = price.replace("US $", "").replace("/ea", "")
                print(strippedPrice)
                try:
                    return self.calculateFinalPrice(float(strippedPrice))
                except ValueError:
                    print("Could not convert price to float.")
            else:
                print("Inner <span> element not found.")
        else:
            print("Outer <span> element not found.")

    def getImages(self, soup):
        print("Getting images")
        divClass = "ux-image-carousel-item"
        imgTags = soup.find("div", class_=divClass)
        imageSources = []
        if imgTags:
            imgTags = imgTags.find_all(["img", "button"])
            for tag in imgTags:
                source = tag.get("src") if tag.name == "img" else tag.find("img").get("src") if tag.find("img") else None
                if source:
                    imageSources.append(source)
        else:
            activeImg = soup.find("div", class_="ux-image-carousel-item active image")
            if activeImg and activeImg.find("img"):
                imageSources.append(activeImg.find("img")["src"])
        return imageSources


    # I consider a product being "Available" when there are more than 10 in stock. This way, there is a way
    # better chance that it will still be in stock by the time the user would have to order it from their customer.
    def isAvailable(self, soup):
        divElement = soup.find('div', class_='d-quantity__availability')
        if divElement:
            spanElements = divElement.find_all('span', class_='ux-textspans')
            if spanElements and spanElements[0].get_text() == "More than 10 available":
                return True
        else:
            print("Availability information not found")
        return False

    # Facebook has an awful variations system and they make it very difficult to input.
    # Variations also have a way higher chance of going out of stock unexpectedly so for now, we will exclude
    # the products that have them.
    def hasVariations(self, soup):
        if soup.find('div', class_='vim x-msku'):
            print("Product skipped: Div class 'vim x-msku' found")
            return True
        return False

    def scrapeProductDetails(self, url):
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')

            title = self.getTitle(soup)
            price = self.getPrice(soup)
            images = self.getImages(soup)
            productAlreadyInDb = self.dbManager.productAlreadyExistsInDatabase(url, title)

            # if valid title, price, image(s) and not in db already
            # (meaning the product was added on a previous run of the app): include these products.
            if title and price and images and not productAlreadyInDb:
                product = Product(title, price, images)
                global dictionaryId
                imageDict[str(dictionaryId)] = images
                dictionaryId += 1
                products.append(product)
                self.dbManager.addProduct(url, title)
                print(f"Scraped: {title}")
        except requests.RequestException as e:
            print(f"Request error for {url}: {e}")
        except Exception as e:
            print(f"Error scraping {url}: {e}")

    def scrapeEbayStore(self, url):
        try:
            response = self.session.get(url)
            soup = BeautifulSoup(response.content, 'html.parser')
            productLinks = soup.find_all('a', class_='s-item__link')

            with ThreadPoolExecutor(max_workers=10) as executor:
                futures = {executor.submit(self.scrapeProductDetails, link['href']): link for link in
                           productLinks[:100]}
                for future in as_completed(futures):
                    try:
                        future.result()  # Retrieve the result to raise any exceptions
                    except Exception as e:
                        print(f"Error in scraping task: {e}")
        except Exception as e:
            print(f"Error scraping eBay store: {e}")

        self.downloadImagesSynchronously()

    def downloadImagesSynchronously(self):
        threads = []
        for product in products:
            thread = threading.Thread(target=self.downloadImages, args=(product,))
            threads.append(thread)
            thread.start()
        for thread in threads:
            thread.join()

    def downloadImages(self, product):
        productIndex = products.index(product)

        # only do 50 products before starting the next batch (fb has a 50 product limit for CSV uploads)
        if productIndex % 50 == 0 and productIndex > 0:
            self.batchNumber += 1

        batchNumber = self.batchNumber
        productFolder = os.path.join(self.settingsManager.getBaseDir(), f"Products Directory {batchNumber}", str(productIndex + 1))
        if not os.path.exists(productFolder):
            os.makedirs(productFolder)
        for index, url in enumerate(product.images, start=1):
            try:
                response = requests.get(url)
                fileName = f"{index}_{os.path.basename(url)}"
                filePath = os.path.join(productFolder, fileName)
                with open(filePath, 'wb') as file:
                    file.write(response.content)
                print(f"Downloaded {fileName} for product {product.title}")
            except requests.exceptions.RequestException as e:
                print(f"Error downloading image from {url}: {e}")

