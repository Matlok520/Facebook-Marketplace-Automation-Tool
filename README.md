# Facebook Marketplace Automation Tool

This project automates tasks on Facebook Marketplace, such as listing items, managing data, and handling interactions. It includes a GUI, web scraping capabilities, data management, and testing.

## Table of Contents
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Components](#components)
  - [GUI with PyQt5](#gui-with-pyqt5)
  - [Web Scraping](#web-scraping)
  - [Data Management with Pandas and SQLite](#data-management-with-pandas-and-sqlite)
  - [Automated Testing with unittest](#automated-testing-with-unittest)
- [Contributing](#contributing)

## Features
- User-friendly GUI for managing automation tasks.
- Scraping and managing listings including titles, prices, and locations.
- Data storage using Pandas and SQLite.
- Automated tests to ensure script reliability.

## Installation

1. **Clone the repository:**
    ```bash
    git clone https://github.com/ShaffeCity/Facebook-Marketplace-Automation-Tool.git
    cd Facebook-Marketplace-Automation-Tool
    ```

2. **Install required packages:**
    ```bash
    pip install -r requirements.txt
    ```

## Usage

1. **Run the main script:**
    ```bash
    python main.py
    ```

2. **Interact with the GUI:**
    - Enter your Facebook credentials.
    - Click "Login" to authenticate.
    - Click "Start Scraping" to begin scraping Marketplace listings.

3. **View results:**
    - Scraped data will be saved in an SQLite database (`marketplace_listings.db`).

## Components

### GUI with PyQt5

The PyQt5-based GUI allows users to input credentials, start scraping, and view results.

```python
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QLineEdit, QPushButton, QMessageBox
from PyQt5.QtGui import QPalette, QColor

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Facebook Marketplace Automation Tool")

        layout = QVBoxLayout()

        self.email_label = QLabel('Email')
        self.email_input = QLineEdit()
        layout.addWidget(self.email_label)
        layout.addWidget(self.email_input)

        self.password_label = QLabel('Password')
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_input)

        self.login_button = QPushButton('Login')
        self.login_button.clicked.connect(self.login)
        layout.addWidget(self.login_button)

        self.scrape_button = QPushButton('Start Scraping')
        self.scrape_button.clicked.connect(self.start_scraping)
        layout.addWidget(self.scrape_button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def login(self):
        email = self.email_input.text()
        password = self.password_input.text()
        # Implement login functionality here

    def start_scraping(self):
        # Implement scraping functionality here
        pass

app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec_())

### Web Scraping
The scraping functionality parses HTML content to extract Marketplace listings.

python
Copy code
import requests
from bs4 import BeautifulSoup

def scrape_listings():
    url = "https://www.facebook.com/marketplace"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    listings = []
    for item in soup.select('div._1fwi'):
        title = item.select_one('span._2tga').text
        price = item.select_one('span._2tga').text
        location = item.select_one('span._2vjp').text
        listings.append({"title": title, "price": price, "location": location})
        
    return listings
### Data Management with Pandas and SQLite
The scraped data is stored in a Pandas DataFrame and saved to an SQLite database for persistent storage.

python
Copy code
import pandas as pd
import sqlite3

def save_to_database(listings):
    df = pd.DataFrame(listings)
    conn = sqlite3.connect('marketplace_listings.db')
    df.to_sql('listings', conn, if_exists='replace', index=False)
    conn.close()
### Automated Testing with unittest
Unit tests ensure the reliability of the functions and the overall script.

python
Copy code
import unittest

class TestFacebookMarketplaceAutomation(unittest.TestCase):
    
    def test_scrape_listings(self):
        listings = scrape_listings()
        self.assertGreater(len(listings), 0)

    def test_save_to_database(self):
        listings = [{"title": "Test Item", "price": "$10", "location": "Test Location"}]
        save_to_database(listings)
        conn = sqlite3.connect('marketplace_listings.db')
        df = pd.read_sql('SELECT * FROM listings', conn)
        self.assertEqual(len(df), 1)
        conn.close()

if __name__ == '__main__':
    unittest.main()
## Contributing
Contributions are welcome! Please submit a pull request or open an issue to discuss your ideas.
