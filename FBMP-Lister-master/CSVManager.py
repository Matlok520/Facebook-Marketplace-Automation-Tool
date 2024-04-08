import csv
import logging
import os
import Utils

class CSVManager:
    def __init__(self, settingsManager):
        self.baseDir = "Products Directory"
        self.settingsManager = settingsManager
        self.settings = self.settingsManager.settings
        self.fieldNames = self.generateFieldNames()
        self.currentBatch = Utils.getNextBatchNumber(self.baseDir)

    def generateFieldNames(self):
        baseFields = ['TITLE', 'PRICE'] # These are dynamic fields that we get from the products so we add these seperately
        additionalFields = list(self.settings.get('csvHeaders', {}).keys())
        return baseFields + [field for field in additionalFields if field not in baseFields]

    def saveProducts(self, products):
        productCount = 0  # Track the number of products processed in the current batch

        try:
            for product in products:
                if productCount % 50 == 0 and productCount > 0:
                    self.currentBatch += 1  # Move to the next batch after every 50 products (FB only allows 50 per CSV)

                directory = os.path.join(self.settingsManager.getBaseDir(), f"Products Directory {self.currentBatch}")
                if not os.path.exists(directory):
                    os.makedirs(directory)

                csvFile = os.path.join(directory, f'Products{self.currentBatch}.csv')
                self.writeProductToCsv(csvFile, product)

                productCount += 1  # Increment the count after processing each product

                print(f"Products successfully saved to {csvFile}.")

        except Exception as e:
            logging.error(f"Error saving products to CSV: {e}", exc_info=True)

    def writeProductToCsv(self, filePath, product):
        fileExists = os.path.isfile(filePath)
        with open(filePath, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=self.fieldNames)
            if not fileExists:
                writer.writeheader()

            # Start with default values from settings
            row = {field: self.settings.get('csvHeaders', {}).get(field, '') for field in self.fieldNames}

            # Update row with product data for title and price
            row['TITLE'] = getattr(product, 'title', '')
            row['PRICE'] = getattr(product, 'price', '')
            writer.writerow(row)
