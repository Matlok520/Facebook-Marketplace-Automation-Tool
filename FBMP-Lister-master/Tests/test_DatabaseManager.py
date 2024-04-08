import unittest
import sqlite3
from unittest.mock import patch

from DatabaseManager import DatabaseManager

class TestDatabaseManager(unittest.TestCase):

    def setUp(self):
        self.db_manager = DatabaseManager(dbPath='test_products.db')
        self.initialize_test_db()

    def tearDown(self):
        # Clean up the test database file after each test
        conn = sqlite3.connect('test_products.db')
        c = conn.cursor()
        c.execute("DROP TABLE IF EXISTS products")
        conn.commit()
        conn.close()

    def initialize_test_db(self):
        # Initialize the test database with a products table
        with sqlite3.connect('test_products.db') as conn:
            cursor = conn.cursor()
            cursor.execute('''CREATE TABLE IF NOT EXISTS products (
                                id INTEGER PRIMARY KEY,
                                url TEXT UNIQUE,
                                title TEXT
                              )''')

    def test_addProduct(self):
        # Add a product to the database
        self.db_manager.addProduct('https://www.example.com/product1', 'Product 1')

        # Verify that the product was added by checking if it exists in the database
        conn = sqlite3.connect('test_products.db')
        c = conn.cursor()
        c.execute("SELECT * FROM products WHERE url=? AND title=?", ('https://www.example.com/product1', 'Product 1'))
        result = c.fetchone()
        conn.close()

        # Verify that the product exists in the database
        self.assertIsNotNone(result)

    def test_productAlreadyExistsInDatabase(self):
        # Add a product to the database
        self.db_manager.addProduct('https://www.example.com/product2', 'Product 2')

        # Check if the added product is detected as existing in the database
        product_exists = self.db_manager.productAlreadyExistsInDatabase('https://www.example.com/product2', 'Product 2')

        # Verify that the product is detected as existing in the database
        self.assertTrue(product_exists)

    @patch('builtins.print')
    def test_addProduct_existingUrl(self, mock_print):
        # Add a product with an existing URL to the database
        self.db_manager.addProduct('https://www.example.com/product3', 'Product 3')
        self.db_manager.addProduct('https://www.example.com/product3', 'Product 3 Duplicate')

        # Verify that the print function is called with the appropriate message for existing URL
        mock_print.assert_called_once_with("Product with URL https://www.example.com/product3 already exists.")

if __name__ == '__main__':
    unittest.main()
