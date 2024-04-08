import unittest
from unittest.mock import patch, Mock

from PyQt5.QtWidgets import QApplication, QListWidget, QStackedWidget, QLabel, QLineEdit, QFileDialog, QMessageBox
from UIManager import UIManager

app = QApplication([])  # Create a QApplication instance for GUI tests

class TestUIManager(unittest.TestCase):
    def setUp(self):
        self.settingsManager = Mock()
        self.settingsManager.settings = {
            'baseDir': '/path/to/directory',
            'csvHeaders': {
                'facebookFee': '5',
                'salesTax': '10',
                'additionalProfit': '15',
                'OFFER FREE SHIPPING': 'Yes',
                'SHIPPING PRICE': '10',
                'CONDITION': 'New',
                'DESCRIPTION': 'Sample description',
                'AVAILABLE INVENTORY': '100',
                'AVAILABLE FOR LOCAL PICKUP': 'Yes'
            }
        }
        self.settingsManager.getBaseDir.return_value = "/path/to/directory"  # mocking the expected base directory
        self.scraper = Mock()
        self.csvManager = Mock()
        self.uiManager = UIManager(self.settingsManager, self.scraper, self.csvManager)
        self.uiManager.baseDirLabel = QLabel()
        self.uiManager.urlEntry = QLineEdit()
        self.patcher = patch.object(QMessageBox, 'information')
        self.mock_information = self.patcher.start()
        self.addCleanup(self.patcher.stop)

        self.patcher = patch.object(QFileDialog, 'getExistingDirectory', return_value=None)
        self.mock_getExistingDirectory = self.patcher.start()
        self.addCleanup(self.patcher.stop)

    def tearDown(self):
        app.quit()

    def testInitUI(self):
        # test if the UI elements are initialized correctly
        self.assertIsInstance(self.uiManager.sidebarList, QListWidget)
        self.assertIsInstance(self.uiManager.stackedWidget, QStackedWidget)
        self.assertEqual(self.uiManager.sidebarList.count(), 2)  # check if sidebar items are added

    def testChooseBaseDirectoryCancelled(self):
        # Change the return value of QFileDialog.getExistingDirectory to simulate directory selection
        with patch.object(QFileDialog, 'getExistingDirectory', return_value="/path/to/selected/directory"):
            self.uiManager.chooseBaseDirectory()

        # Assert that QMessageBox.information was not called since directory selection was simulated
        self.assertFalse(self.mock_information.called)

        # Assert that settingsManager.updateBaseDir was called with the selected directory
        self.settingsManager.updateBaseDir.assert_called_once_with("/path/to/selected/directory")

        # Assert the baseDirLabel text
        self.assertEqual(self.uiManager.baseDirLabel.text(), 'Current Directory: /path/to/selected/directory')

    @patch('UIManager.QMessageBox.critical')
    def testInitiateScrapingInvalidUrl(self, mock_critical):
        # Test initiating scraping with an invalid URL
        self.uiManager.urlEntry.setText('invalid-url')
        self.uiManager.initiateScraping()
        mock_critical.assert_called_once_with(self.uiManager, "Error", "Please enter a valid URL.")
        self.assertFalse(self.scraper.scrapeEbayStore.called)

    @patch('UIManager.QMessageBox.critical')
    def testInitiateScrapingValidUrl(self, mock_critical):
        # Test initiating scraping with a valid URL
        self.uiManager.urlEntry.setText('https://www.ebay.com/itm/example-listing')
        self.uiManager.initiateScraping()
        self.assertTrue(self.scraper.scrapeEbayStore.called)

if __name__ == '__main__':
    unittest.main()
