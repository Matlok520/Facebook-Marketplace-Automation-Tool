import unittest
from unittest.mock import patch

import main


class TestMainFunction(unittest.TestCase):
    @patch('main.QApplication')
    @patch('main.SettingsManager')
    @patch('main.DatabaseManager')
    @patch('main.Scraper')
    @patch('main.CSVManager')
    @patch('main.UIManager')
    def test_initialization(self, UIManagerMock, CSVManagerMock, ScraperMock, DatabaseManagerMock, SettingsManagerMock, QApplicationMock):
        # Mock sys.exit to prevent the test from exiting
        with patch('sys.exit') as exit_mock:
            main.main()  # Execute the main function

            # Assert that each component is initialized once
            SettingsManagerMock.assert_called_once()
            DatabaseManagerMock.assert_called_once()
            ScraperMock.assert_called_once()
            CSVManagerMock.assert_called_once()
            UIManagerMock.assert_called_once()

            # Assert that the UI Manager is displayed
            UIManagerMock.return_value.show.assert_called_once()


if __name__ == '__main__':
    unittest.main()
