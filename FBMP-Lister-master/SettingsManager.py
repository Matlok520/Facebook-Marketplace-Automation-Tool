import json
import os
import shutil


class SettingsManager:
    def __init__(self, settingsFile='settings.json'):
        self.settingsFile = settingsFile
        self.settings = self.loadSettings()

    def loadSettings(self):
        try:
            with open(self.settingsFile, 'r') as file:
                settings = json.load(file)
                # Check for required keys and nested keys
                if 'baseDir' not in settings or 'csvHeaders' not in settings:
                    raise KeyError("Missing required keys in settings file.")
                # Convert relevant values to float type
                for key in ['facebookFee', 'salesTax', 'additionalProfit']:
                    if key in settings:
                        settings[key] = float(settings[key])
                return settings
        except (FileNotFoundError, json.JSONDecodeError, KeyError):
            return self.getFallbackSettings()

    def getFallbackSettings(self):
        default_settings = {
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
        # Create the settings.json file with default settings if it doesn't exist
        if not os.path.exists(self.settingsFile):
            with open(self.settingsFile, 'w') as file:
                json.dump(default_settings, file, indent=4)
        return default_settings

    def saveSettings(self):
        try:
            # Create a backup of the settings file before saving
            backup_file = self.settingsFile + '.bak'
            shutil.copy(self.settingsFile, backup_file)
            with open(self.settingsFile, 'w') as file:
                json.dump(self.settings, file, indent=4)
        except Exception as e:
            # Restore the backup file if an error occurs during saving
            shutil.move(backup_file, self.settingsFile)
            raise e

    def updateCsvHeader(self, key, value):
        if 'csvHeaders' in self.settings and key in self.settings['csvHeaders']:
            self.settings['csvHeaders'][key] = value
            self.saveSettings()

    def updateBaseDir(self, baseDir):
        self.settings['baseDir'] = baseDir
        self.saveSettings()

    def getBaseDir(self):
        return self.settings.get('baseDir', "")
