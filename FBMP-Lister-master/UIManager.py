import os
import logging
import re
from urllib.parse import urlparse

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout,
    QHBoxLayout, QComboBox, QMessageBox, QGroupBox, QStackedWidget, QListWidget, QFileDialog,
)

# The resolution was super bad between my devices. I found that putting these next two lines makes it more
# consistent across devices.
QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

from PyQt5.QtGui import QIntValidator, QDoubleValidator, QIcon, QColor
from Scraper import products
from PyQt5.QtGui import QFont

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class UIManager(QMainWindow):
    def __init__(self, settingsManager, scraper, csvManager):
        super().__init__()
        self.settingsManager = settingsManager
        self.scraper = scraper
        self.csvManager = csvManager
        self.baseDir = ""
        self.conditionOptions = ["New", "Used - Like New", "Used - Good", "Used - Fair"]
        self.csvHeaderEntries = {}
        self.financialSettingsEntries = {}
        self.settingsWidget = None

        self.setWindowTitle("eBay Scraper Application")
        self.setGeometry(100, 100, 800, 600)

        self.setupUI()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("eBay Scraper Application")
        self.setWindowIcon(QIcon("FBMPAuto.png"))
        self.setStyleSheet("""
                   QMainWindow {
                       background-color: #2c3e50; /* Dark blue color */
                   }
                   QListWidget {
                       background-color: #34495e; /* Darker blue color */
                       border: none;
                   }
                   QListWidget::item {
                       color: white;
                       padding: 10px;
                       border-radius: 5px;
                   }
                   QListWidget::item:selected {
                       background-color: #2980b9; /* Highlight color */
                   }
                   QLabel, QLineEdit, QComboBox, QPushButton, QGroupBox {
                       font: 14px 'Arial';
                       color: white;
                   }
                   QLineEdit, QComboBox {
                       background-color: #ecf0f1; /* Light grey background */
                       color: #2c3e50; /* Dark blue text */
                       border: 1px solid #bdc3c7; /* Grey border */
                       padding: 5px;
                       border-radius: 4px;
                   }
                   QPushButton {
                       background-color: #3498db; /* Blue */
                       border: none;
                       padding: 10px 20px;
                       border-radius: 4px;
                   }
                   QPushButton:hover {
                       background-color: #2980b9; /* Darker blue */
                   }
                   QPushButton:pressed {
                       background-color: #1f5a7a; /* Even darker blue */
                   }
                   QPushButton:disabled {
                       background-color: #7f8c8d; /* Grey out when disabled */
                   }
                   QGroupBox {
                       margin-top: 2ex; /* Space out group boxes */
                   }
                   QGroupBox::title {
                       subcontrol-origin: margin;
                       left: 10px; /* Move title text to the right */
                       padding: 0 3px 0 3px;
                   }
                   QMessageBox {
                       background-color: #34495e;
                   }
               """)

        # Central widget and layout
        centralWidget = QWidget()
        self.setCentralWidget(centralWidget)

        # Sidebar for navigation
        self.sidebarList = QListWidget()
        self.sidebarList.setStyleSheet("QListWidget { background-color: #222; border: none; }"
                                        "QListWidget::item { color: white; padding: 10px; }")
        self.sidebarList.setFont(QFont("Arial", 12))
        self.sidebarList.setFixedWidth(200)
        self.sidebarList.addItem("Scrape")
        self.sidebarList.addItem("Settings")

        # Stacked widget for different pages
        self.stackedWidget = QStackedWidget()
        self.stackedWidget.addWidget(self.createScrapePage())
        self.stackedWidget.addWidget(self.createSettingsPage())

        # Main layout with sidebar and stacked widget
        mainLayout = QHBoxLayout(centralWidget)
        mainLayout.addWidget(self.sidebarList)
        mainLayout.addWidget(self.stackedWidget)

        self.sidebarList.currentRowChanged.connect(self.stackedWidget.setCurrentIndex)

        # Apply the initial selection
        self.sidebarList.setCurrentRow(0)

    def setupUI(self):
        centralWidget = QWidget()
        self.setCentralWidget(centralWidget)

        mainLayout = QVBoxLayout()
        centralWidget.setLayout(mainLayout)

        urlLayout = QHBoxLayout()
        mainLayout.addLayout(urlLayout)

        urlLabel = QLabel("Enter URL to Scrape:")
        urlLabel.setFont(QFont("Arial", 16))
        urlLayout.addWidget(urlLabel)

        self.urlEntry = QLineEdit()
        self.urlEntry.setFont(QFont("Arial", 14))
        urlLayout.addWidget(self.urlEntry)

        scrapeButton = QPushButton("Scrape")
        scrapeButton.setFont(QFont("Arial", 14))
        scrapeButton.setStyleSheet(
            "QPushButton { background-color: #4CAF50; color: white; border: none; padding: 10px 20px; }"
            "QPushButton:hover { background-color: #45a049; }"
            "QPushButton:pressed { background-color: #3c9039; }"
        )
        scrapeButton.clicked.connect(self.initiateScraping)
        mainLayout.addWidget(scrapeButton)

        settingsButton = QPushButton("Settings")
        settingsButton.setFont(QFont("Arial", 14))
        settingsButton.setStyleSheet(
            "QPushButton { background-color: #008CBA; color: white; border: none; padding: 10px 20px; }"
            "QPushButton:hover { background-color: #0073a9; }"
            "QPushButton:pressed { background-color: #006396; }"
        )
        settingsButton.clicked.connect(self.openSettings)
        mainLayout.addWidget(settingsButton)

    def createScrapePage(self):
        scrapePage = QWidget()
        layout = QVBoxLayout(scrapePage)

        # TItle bar
        titleLabel = QLabel("New Scraping Task")
        titleLabel.setFont(QFont("Arial", 22, QFont.Bold))
        titleLabel.setAlignment(Qt.AlignCenter)
        titleLabel.setStyleSheet("color: #3498db; margin-bottom: 5px;")  # blue color for title
        layout.addWidget(titleLabel)

        # label for the URL box
        subtitleLabel = QLabel("Paste your eBay listing URL below.")
        subtitleLabel.setFont(QFont("Arial", 16, QFont.Normal))
        subtitleLabel.setAlignment(Qt.AlignCenter)
        subtitleLabel.setStyleSheet("color: #ecf0f1; margin-bottom: 30px;")  # light grey color for subtitle
        layout.addWidget(subtitleLabel)

        # URL input with placeholder text
        self.urlEntry = QLineEdit()
        self.urlEntry.setFont(QFont("Arial", 14))
        self.urlEntry.setPlaceholderText("https://www.ebay.com/itm/example-listing")
        self.urlEntry.setStyleSheet("""
            padding: 12px;
            border: 2px solid #3498db;  # Blue border color
            border-radius: 8px;
            color: #2c3e50;
            background-color: #ecf0f1;
            margin-bottom: 20px;
        """)
        layout.addWidget(self.urlEntry)

        # Scrape button
        scrapeButton = self.createButton("Start Scraping", "#2ecc71")  # Green button color
        scrapeButton.setFont(QFont("Arial", 16, QFont.Bold))
        scrapeButton.setStyleSheet("""
            QPushButton {
                padding: 15px 30px;
                margin-top: 10px;
                border-radius: 8px;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
            QPushButton:pressed {
                background-color: #229954;
            }
        """)
        scrapeButton.clicked.connect(self.initiateScraping)
        layout.addWidget(scrapeButton)

        # Additional spacing at the bottom
        layout.addStretch()

        return scrapePage

    def createSettingsPage(self):

        # this is a mapping list for tooltips and their corresponding settings.json entries
        tooltipMapping = {
            'baseDir': "The base directory where the scraped data will be saved.",
            'facebookFee': "This is the percentage that you want to factor into each product's price to cover the fee that Facebook charges for every order.",
            'salesTax': "This is the percentage that you want to factor into each product's price to cover the Sales Tax for every order.",
            'additionalProfit': "This is the percentage of profit that you want to make on top of the other fees that are factored in to the product's price.",
            'OFFER FREE SHIPPING': "Select 'Yes' if you want to offer free shipping for your products.",
            'SHIPPING PRICE': "The fixed shipping price for your products. This will not be editable if Offer Free Shipping is set to 'Yes'.",
            'CONDITION': "The condition of the product (New, Used - Like New, Used - Good, Used - Fair).",
            'DESCRIPTION': "The description of the product.",
            'AVAILABLE INVENTORY': "The available inventory quantity for the product.",
            'AVAILABLE FOR LOCAL PICKUP': "Select 'Yes' if the product is available for local pickup.",
        }

        settingsPage = QWidget()
        layout = QVBoxLayout(settingsPage)

        financialGroupbox = QGroupBox("Financial Settings")
        financialLayout = QVBoxLayout(financialGroupbox)

        csvGroupbox = QGroupBox("CSV Headers")
        csvLayout = QVBoxLayout(csvGroupbox)

        # mapping list just for quicker resolution of settings.json names to UI names
        labelMapping = {
            'facebookFee': 'Facebook Fee',
            'salesTax': 'Sales Tax',
            'additionalProfit': 'Additional Profit'
        }

        for setting in ['facebookFee', 'salesTax', 'additionalProfit']:
            labelText = labelMapping.get(setting, setting)  # Get the mapped label or use the setting as is
            label = QLabel(f"{labelText} (%):")  # Add percent sign to label
            label.setToolTip(tooltipMapping.get(setting, "No tooltip available."))

            entry = QLineEdit(str(self.settingsManager.settings.get(setting, '')))
            entry.setFont(QFont("Arial", 14))
            entry.setValidator(QDoubleValidator(0, 100, 2))
            entry.setToolTip(label.toolTip())

            financialLayout.addWidget(label)
            financialLayout.addWidget(entry)
            self.financialSettingsEntries[setting] = entry

        for key, default in self.settingsManager.settings.get('csvHeaders', {}).items():
            if key not in ["OFFER FREE SHIPPING", "SHIPPING PRICE"]:  # There is other logic that will add these fields
                label = QLabel(f"{key.replace('_', ' ').title()}:")
                label.setToolTip(tooltipMapping.get(key, "No tooltip available."))
                label.setFont(QFont("Arial", 14))
                if key == "CONDITION":
                    combobox = QComboBox()
                    combobox.setFont(QFont("Arial", 14))
                    combobox.addItems(self.conditionOptions)
                    combobox.setCurrentText(default)
                    combobox.setToolTip(label.toolTip())
                    csvLayout.addWidget(label)
                    csvLayout.addWidget(combobox)
                    self.csvHeaderEntries[key] = combobox
                elif key == "AVAILABLE FOR LOCAL PICKUP":
                    combobox = QComboBox()
                    combobox.setFont(QFont("Arial", 14))
                    combobox.addItems(["Yes", "No"])
                    combobox.setCurrentText(default)
                    combobox.setToolTip(label.toolTip())
                    csvLayout.addWidget(label)
                    csvLayout.addWidget(combobox)
                    self.csvHeaderEntries[key] = combobox
                else:
                    entry = QLineEdit(str(default))
                    entry.setFont(QFont("Arial", 14))
                    entry.setValidator(QIntValidator(0, 1000) if key == "AVAILABLE INVENTORY" else None)
                    entry.setToolTip(label.toolTip())
                    csvLayout.addWidget(label)
                    csvLayout.addWidget(entry)
                    self.csvHeaderEntries[key] = entry

        # "Offer Free Shipping" combobox
        offerFreeShippingLabel = QLabel("Offer Free Shipping:")
        offerFreeShippingLabel.setFont(QFont("Arial", 14))
        offerFreeShippingLabel.setToolTip(tooltipMapping.get('OFFER FREE SHIPPING', "No tooltip available."))
        csvLayout.addWidget(offerFreeShippingLabel)

        self.offerFreeShippingCombobox = QComboBox()
        self.offerFreeShippingCombobox.setFont(QFont("Arial", 14))
        self.offerFreeShippingCombobox.addItems(["Yes", "No"])
        offerFreeShippingValue = str(self.settingsManager.settings.get('OFFER FREE SHIPPING'))
        if offerFreeShippingValue is None or offerFreeShippingValue == 'No':
            print(offerFreeShippingValue)
            self.offerFreeShippingCombobox.setCurrentText('No')
        else:
            self.offerFreeShippingCombobox.setCurrentText('Yes')

        self.offerFreeShippingCombobox.currentIndexChanged.connect(self.handleFreeShippingChanged)
        self.offerFreeShippingCombobox.setToolTip(
            offerFreeShippingLabel.toolTip())
        csvLayout.addWidget(self.offerFreeShippingCombobox)

        # Add "Shipping Price" entry
        shippingPriceLabel = QLabel("Shipping Price ($):")  # title with dollar sign
        shippingPriceLabel.setFont(QFont("Arial", 14))
        shippingPriceLabel.setToolTip(tooltipMapping.get('SHIPPING PRICE', "No tooltip available."))
        csvLayout.addWidget(shippingPriceLabel)

        self.shippingPriceEntry = QLineEdit()
        self.shippingPriceEntry.setFont(QFont("Arial", 14))
        self.shippingPriceEntry.setValidator(QIntValidator(0, 9999))
        self.shippingPriceEntry.setText(str(self.settingsManager.settings.get('SHIPPING PRICE', 0)))
        self.shippingPriceEntry.setToolTip(
                shippingPriceLabel.toolTip())
        csvLayout.addWidget(self.shippingPriceEntry)

        # Ensure the Shipping Price field is disabled if Free Shipping is offered
        self.handleFreeShippingChanged(self.offerFreeShippingCombobox.currentIndex())

        # Directory Settings GroupBox
        directoryGroupbox = QGroupBox("Directory Settings")
        directoryLayout = QVBoxLayout(directoryGroupbox)

        # Current Directory Label
        self.baseDirLabel = QLabel(f"Current Directory: {self.settingsManager.getBaseDir()}")
        self.baseDirLabel.setToolTip(tooltipMapping.get('baseDir', "No tooltip available."))

        directoryLayout.addWidget(self.baseDirLabel)

        # Choose Directory Button
        chooseDirButton = QPushButton("Choose Directory")
        chooseDirButton.setToolTip(self.baseDirLabel.toolTip())
        chooseDirButton.clicked.connect(self.chooseBaseDirectory)
        directoryLayout.addWidget(chooseDirButton)

        layout.addWidget(directoryGroupbox)
        layout.addWidget(financialGroupbox)
        layout.addWidget(csvGroupbox)

        saveButton = self.createButton("Save Settings", "#008CBA")
        saveButton.clicked.connect(self.saveSettings)
        layout.addWidget(saveButton)

        return settingsPage

    def chooseBaseDirectory(self):
        chosenDir = QFileDialog.getExistingDirectory(self, "Select Base Directory", self.settingsManager.getBaseDir())
        if chosenDir:
            self.settingsManager.updateBaseDir(chosenDir)
            self.baseDirLabel.setText(f"Current Directory: {chosenDir}")

    def handleFreeShippingChanged(self, index):
        # If "Yes" is selected for free shipping
        if self.offerFreeShippingCombobox.currentText() == "Yes":
            self.shippingPriceEntry.setText("0")
            self.shippingPriceEntry.setDisabled(True)
            self.shippingPriceEntry.setStyleSheet("background-color: #7f8c8d; color: #ecf0f1;")  # disabled style
            self.shippingPriceEntry.setToolTip(  # Grrr This is the only way I could figure out to get the tooltip to not be grayed out when the textbox is.
                "<font color='#2c3e50'>The fixed shipping price for your products. This will not be editable if Offer Free Shipping is set to 'Yes'.</font>"
            )
        else:
            self.shippingPriceEntry.setDisabled(False)
            self.shippingPriceEntry.setStyleSheet("background-color: #ecf0f1; color: #2c3e50;")  # enabled style

    def openDirectory(self, directory):
        if os.path.exists(directory):
            os.startfile(directory)
        else:
            QMessageBox.warning(self, "Open Directory", "The directory does not exist.")

    def createButton(self, text, color):
        button = QPushButton(text)
        button.setFont(QFont("Arial", 14))
        button.setStyleSheet(f"""
               QPushButton {{
                   background-color: {color};
                   color: white;
                   border: none;
                   padding: 10px 20px;
                   margin-top: 10px;
                   border-radius: 5px;
               }}
               QPushButton:hover {{
                   background-color: {QColor(color).darker(120).name()};
               }}
               QPushButton:pressed {{
                   background-color: {QColor(color).darker(150).name()};
               }}
           """)
        return button

    def initiateScraping(self):
        url = self.urlEntry.text().strip()

        if not url or not self.validateUrl(url):
            QMessageBox.critical(self, "Error", "Please enter a valid URL.")
            return

            # Check if the base directory is set, prompt for directory if not
        baseDir = self.settingsManager.settings.get('baseDir')
        if not baseDir:
            chosenDir = QFileDialog.getExistingDirectory(self, "Choose a Directory to Save Product Data")
            if not chosenDir:
                QMessageBox.warning(self, "Warning", "Scraping cancelled. No directory selected.")
                return
            self.settingsManager.updateBaseDir(chosenDir)
            baseDir = chosenDir

            # Update the settings page right away with the selected directory
            self.baseDirLabel.setText(f"Current Directory: {chosenDir}")

            # Prompt the user to click the Scrape button again if the directory wasn't set the first time
            QMessageBox.information(self, "Info", "Directory selected successfully. Please click the Start Scraping button again to start scraping.")
            return  # Exit the method to wait for the user to click the Scrape button again

        try:
            logging.info(f"Starting scraping for URL: {url}")
            self.scraper.scrapeEbayStore(url)
            self.csvManager.saveProducts(products)
            # Fetch the base directory from settings when the button is clicked
            baseDir = self.settingsManager.getBaseDir()  # Get the actual base directory from settings

            directoryMessage = f"Scraping completed successfully.\nProducts saved in {baseDir}."

            customMessagebox = QMessageBox(self)
            customMessagebox.setWindowTitle("Scraping Status")
            customMessagebox.setText(directoryMessage)
            openButton = QPushButton("Open Exported Products")

            # Connect the button click to open the directory from settings
            openButton.clicked.connect(lambda: self.openDirectory(baseDir))

            customMessagebox.addButton(openButton, QMessageBox.ActionRole)
            customMessagebox.exec_()

        except Exception as e:
            logging.error(f"Failed to scrape: {e}", exc_info=True)
            QMessageBox.critical(self, "Error", f"Failed to scrape: {e}")

    def validateUrl(self, url):
        try:
            parsedUrl = urlparse(url)
            domain = parsedUrl.netloc
            if domain.endswith('.ebay.com') and domain.count('.') >= 2:
                return True
            else:
                return False
        except Exception as e:
            logging.error(f"Error validating URL: {e}")
            return False

    def openSettings(self):
        if not self.settingsWidget:  # Check if settingsWidget is already open
            self.settingsWidget = QWidget()
            self.settingsWidget.setWindowTitle("Settings")
            self.settingsWidget.setGeometry(200, 200, 600, 400)

            mainLayout = QVBoxLayout()
            self.settingsWidget.setLayout(mainLayout)

            financialGroupbox = QGroupBox("Financial Settings")
            financialLayout = QVBoxLayout()
            financialGroupbox.setLayout(financialLayout)

            csvGroupbox = QGroupBox("CSV Headers")
            csvLayout = QVBoxLayout()
            csvGroupbox.setLayout(csvLayout)

            mainLayout.addWidget(financialGroupbox)
            mainLayout.addWidget(csvGroupbox)

            for setting in ['facebookFee', 'salesTax', 'additionalProfit']:
                labelText = setting.capitalize().replace('_', ' ')
                label = QLabel(f"{labelText}:")
                entry = QLineEdit(str(self.settingsManager.settings.get(setting, '')))
                entry.setFont(QFont("Arial", 14))
                entry.setValidator(QDoubleValidator())
                financialLayout.addWidget(label)
                financialLayout.addWidget(entry)
                self.financialSettingsEntries[setting] = entry

            saveButton = QPushButton("Save Settings")
            saveButton.clicked.connect(self.saveSettings)
            mainLayout.addWidget(saveButton)

            self.settingsWidget.show()
        else:
            self.settingsWidget.raise_()  # Bring the settingsWidget to the front if already open

    def validateWholeNumber(self, text):
        if text.isdigit() or text == "":
            return True
        return False

    def validatePositiveFloat(self, text):
        if re.match(r"^\d*\.?\d*$", text) or text == "":
            return True
        return False

    def saveSettings(self):
        try:
            for setting, entry in self.financialSettingsEntries.items():
                self.settingsManager.settings[setting] = float(entry.text())
            for key, entry in self.csvHeaderEntries.items():
                if isinstance(entry, QLineEdit):  # Check if entry is a QLineEdit object
                    self.settingsManager.settings['csvHeaders'][key] = entry.text()
                else:  # Handle QComboBox objects differently
                    self.settingsManager.settings['csvHeaders'][key] = entry.currentText() if key != 'condition' else entry.currentText()

            # Update the 'OFFER FREE SHIPPING' setting based on the current state of the combobox
            offerFreeShippingValue = "Yes" if self.offerFreeShippingCombobox.currentText() == "Yes" else "No"
            self.settingsManager.settings['csvHeaders']['OFFER FREE SHIPPING'] = offerFreeShippingValue

            self.settingsManager.saveSettings()
            QMessageBox.information(self, "Success", "Settings saved successfully.")
        except Exception as e:
            logging.error(f"Error saving settings: {e}", exc_info=True)
            QMessageBox.critical(self, "Error", f"Error saving settings: {e}")

