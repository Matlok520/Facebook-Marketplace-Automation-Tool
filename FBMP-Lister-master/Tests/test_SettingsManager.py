import unittest
import json
from SettingsManager import SettingsManager

class TestSettingsManager(unittest.TestCase):

    def setUp(self):
        self.settings_manager = SettingsManager(settingsFile='test_settings.json')

    def tearDown(self):
        # Clean up the test settings file after each test
        with open('test_settings.json', 'w') as file:
            json.dump({}, file)

    def test_loadSettings_existingFile(self):
        test_settings = {
            "baseDir": "",
            "facebookFee": 5.0,
            "salesTax": 7.5,
            "additionalProfit": 10.0,
            "csvHeaders": {
                "CONDITION": "New",
                "DESCRIPTION": "Good Condition",
                "AVAILABLE INVENTORY": 5,
                "AVAILABLE FOR LOCAL PICKUP": "Yes",
                "SHIPPING PRICE": 10,
                "OFFER FREE SHIPPING": "No"
            }
        }
        with open('test_settings.json', 'w') as file:
            json.dump(test_settings, file)

        # Initialize settings manager
        settings_manager = SettingsManager(settingsFile='test_settings.json')

        # load settings from the test file
        loaded_settings = settings_manager.loadSettings()

        # Verify that the loaded settings match the test settings
        self.assertDictEqual(loaded_settings, test_settings)

    def test_loadSettings_nonExistingFile(self):
        settings_manager = SettingsManager(settingsFile='non_existing_settings.json')
        loaded_settings = settings_manager.loadSettings()
        expected_settings = {
            "baseDir": "",
            "facebookFee": 5.0,
            "salesTax": 7.5,
            "additionalProfit": 10.0,
            "csvHeaders": {
                "CONDITION": "Used - Like New",
                "DESCRIPTION": "Good Condition, ships for free with Economy Shipping",
                "AVAILABLE INVENTORY": 3,
                "AVAILABLE FOR LOCAL PICKUP": "No",
                "SHIPPING PRICE": 0,
                "OFFER FREE SHIPPING": "Yes"
            }
        }

        # verify that the loaded settings match the expected default settings
        self.assertDictEqual(loaded_settings, expected_settings)

    def test_saveSettings(self):
        initial_settings = {
            "baseDir": "",
            "facebookFee": 5.0,
            "salesTax": 7.5,
            "additionalProfit": 10.0,
            "csvHeaders": {
                "CONDITION": "New",
                "DESCRIPTION": "Good Condition",
                "AVAILABLE INVENTORY": 5,
                "AVAILABLE FOR LOCAL PICKUP": "Yes",
                "SHIPPING PRICE": 10,
                "OFFER FREE SHIPPING": "No"
            }
        }

        self.settings_manager.settings = initial_settings
        self.settings_manager.saveSettings()

        # Load the saved settings from the file
        with open('test_settings.json', 'r') as file:
            saved_settings = json.load(file)

        # Verify that the saved settings match the initial settings
        self.assertDictEqual(saved_settings, initial_settings)

    def test_updateCsvHeader_existingKey(self):
        initial_settings = {
            "baseDir": "",
            "facebookFee": 5.0,
            "salesTax": 7.5,
            "additionalProfit": 10.0,
            "csvHeaders": {
                "CONDITION": "New",
                "DESCRIPTION": "Good Condition",
                "AVAILABLE INVENTORY": 5,
                "AVAILABLE FOR LOCAL PICKUP": "Yes",
                "SHIPPING PRICE": 10,
                "OFFER FREE SHIPPING": "No"
            }
        }

        self.settings_manager.settings = initial_settings
        self.settings_manager.updateCsvHeader('CONDITION', 'Used - Like New')

        # Verify that the updated key value is reflected in the settings
        self.assertEqual(self.settings_manager.settings['csvHeaders']['CONDITION'], 'Used - Like New')

    def test_updateCsvHeader_nonExistingKey(self):
        initial_settings = {
            "baseDir": "",
            "facebookFee": 5.0,
            "salesTax": 7.5,
            "additionalProfit": 10.0,
            "csvHeaders": {
                "CONDITION": "New",
                "DESCRIPTION": "Good Condition",
                "AVAILABLE INVENTORY": 5,
                "AVAILABLE FOR LOCAL PICKUP": "Yes",
                "SHIPPING PRICE": 10,
                "OFFER FREE SHIPPING": "No"
            }
        }

        self.settings_manager.settings = initial_settings
        self.settings_manager.updateCsvHeader('NON_EXISTING_KEY', 'value')

        # Verify that the settings remain unchanged for the non-existing key
        self.assertNotIn('NON_EXISTING_KEY', self.settings_manager.settings['csvHeaders'])

if __name__ == '__main__':
    unittest.main()
