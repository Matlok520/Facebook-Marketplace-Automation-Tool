import sys
import logging

from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtWidgets import QApplication, QMessageBox
from CSVManager import CSVManager
from DatabaseManager import DatabaseManager
from Scraper import Scraper
from SettingsManager import SettingsManager
from UIManager import UIManager

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

def setupPalette(app):
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(51, 51, 51))
    palette.setColor(QPalette.WindowText, QColor(255, 255, 255))
    palette.setColor(QPalette.Base, QColor(85, 85, 85))
    palette.setColor(QPalette.AlternateBase, QColor(85, 85, 85))
    palette.setColor(QPalette.ToolTipBase, QColor(255, 255, 255))
    palette.setColor(QPalette.ToolTipText, QColor(255, 255, 255))
    palette.setColor(QPalette.Text, QColor(255, 255, 255))
    palette.setColor(QPalette.Button, QColor(85, 85, 85))
    palette.setColor(QPalette.ButtonText, QColor(255, 255, 255))
    palette.setColor(QPalette.BrightText, QColor(255, 0, 0))
    palette.setColor(QPalette.Highlight, QColor(66, 130, 240))
    palette.setColor(QPalette.HighlightedText, QColor(0, 0, 0))
    app.setPalette(palette)

def main():
    app = QApplication(sys.argv)
    setupPalette(app)

    try:
        settingsManager = SettingsManager()
        dbManager = DatabaseManager()
        scraper = Scraper(dbManager, settingsManager)
        csvManager = CSVManager(settingsManager)
        uiManager = UIManager(settingsManager, scraper, csvManager)

        uiManager.show()
        sys.exit(app.exec_()) # allows graceful exit of the app

    except Exception as e:
        logging.error(f"Error starting application: {e}", exc_info=True)
        QMessageBox.critical(None, "Application Error", "An error occurred while starting the application. Check the logs for more details.")

if __name__ == "__main__":
    main()
