import time

from autoit import autoit
from selenium.common import NoSuchElementException
from selenium.webdriver.chrome import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait


def createDriver():
    # Set Chrome options to use the specified profile
    options = webdriver.ChromeOptions()
    options.add_argument(f'--user-data-dir=C:/Users/Shaffe City/AppData/Local/Google/Chrome/User Data')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)

    options.add_argument("--disable-extensions")
    options.add_argument('profile-directory=Profile 3')
    options.add_argument('--disable-blink-features=AutomationControlled')

    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 20)
    return driver, wait


# open facebook page with driver
def openFacebook(driver):
    driver.get("https://www.facebook.com/marketplace/create/bulk")
    time.sleep(2)
    # driver.maximize_window()
    time.sleep(2)


def selectFile(driver):
    # Wait until the element is clickable
    waitSpreadsheet = WebDriverWait(driver, 500)
    # Find the element using XPath and the text value
    element = waitSpreadsheet.until(
        expected_conditions.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Upload a spreadsheet')]")))
    # element.send_keys("C:/Users/Shaffe City/PycharmProjects/FbMarketplaceAutomation/products.csv")
    # Click on the element
    element.click()

    autoit.win_wait_active("Open")  # Wait for the file selection dialog to appear
    time.sleep(3)

    autoit.control_send("Open", "Edit1",
                        "C:\\Users\\Shaffe City\\PycharmProjects\\FbMarketplaceAutomation\\products.csv")  # Replace with the path of the file you want to select
    autoit.control_send("Open", "Edit1", "{ENTER}")  # Press the Enter key to confirm the file selection

    # # Wait for 10 seconds
    time.sleep(3)
    #

    # photo_input = driver.find_elements(By.XPATH, "//div[contains(@class, 'x6s0dn4')][contains(@class, 'x443n21')][contains(@class, 'x78zum5')][contains(@class, 'x1lq5wgf')]/i")


JS_DROP_FILE = """
    var target = arguments[0],
        offsetX = arguments[1],
        offsetY = arguments[2],
        document = target.ownerDocument || document,
        window = document.defaultView || window;

    var input = document.createElement('INPUT');
    input.type = 'file';
    input.onchange = function () {
      var rect = target.getBoundingClientRect(),
          x = rect.left + (offsetX || (rect.width >> 1)),
          y = rect.top + (offsetY || (rect.height >> 1)),
          dataTransfer = { files: this.files };

      ['dragenter', 'dragover', 'drop'].forEach(function (name) {
        var evt = document.createEvent('MouseEvent');
        evt.initMouseEvent(name, !0, !0, window, 0, 0, 0, x, y, !1, !1, !1, !1, 0, null);
        evt.dataTransfer = dataTransfer;
        target.dispatchEvent(evt);
      });

      setTimeout(function () { document.body.removeChild(input); }, 25);
    };
    document.body.appendChild(input);
    return input;
"""


def drag_and_drop_file(drop_target, path):
    driver = drop_target.parent
    file_input = driver.execute_script(JS_DROP_FILE, drop_target, 0, 0)
    file_input.send_keys(path)


time.sleep(2)
# for i in range(len(imageDict)):
import os


# download_images(imageDict)

def send_pictures_with_selenium(dictionary, driver, wait):
    # driver = webdriver.Chrome()  # Replace with the appropriate driver for your browser
    productCounter = 0
    counter = 0
    photo_input = wait.until(expected_conditions.presence_of_all_elements_located((By.XPATH,
                                                                                   "//div[contains(@class, 'x6s0dn4')][contains(@class, 'x443n21')][contains(@class, 'x78zum5')][contains(@class, 'x1lq5wgf')]/i")))

    for product_key, _ in dictionary.items():
        if productCounter == 50:
            return  # Exit out of the function

        folder_name = str(product_key)
        print("product counter: " + str(productCounter))
        for file_name in os.listdir(folder_name):
            file_path = "C:\\Users\\Shaffe City\\PycharmProjects\\FbMarketplaceAutomation\\" + os.path.join(folder_name,
                                                                                                            file_name)
            if counter == 0:
                try:
                    drag_and_drop_file(photo_input[productCounter], file_path)

                except NoSuchElementException:
                    print("Element not found. File drag and drop failed.")

                counter += 1
            else:
                try:
                    # driver.get(upload_url)
                    file_input = wait.until(
                        expected_conditions.presence_of_element_located((By.XPATH, "//input[@type='file']")))

                    file_input.send_keys(file_path)

                    print(f"Uploaded {file_name} for product key {product_key}")
                    counter += 1
                except Exception as e:
                    print(f"Error uploading {file_name} for product key {product_key}: {e}")
        counter = 0
        productCounter += 1


import shutil


def delete_folders(dictionary):
    for product_key, _ in dictionary.items():
        folder_name = str(product_key)
        shutil.rmtree(folder_name)

        print(f"Deleted folder {folder_name}")


# send_pictures_with_selenium(imageDict,driver,wait)
# delete_folders(imageDict)
# addCategoriesifMissing(driver)
def addCategoriesIfMissing(driver):
    # Find all the target div elements
    div_elements = driver.find_elements(By.XPATH, '//div[@class="x78zum5 x1q0g3np xpl7v76 x1dcmaf5"]')
    counter = 0
    # Iterate through each element
    for div_element in div_elements:
        # Check if the text "Movies & TV Shows" or "Books" exists in the DOM tree
        text_found = False
        if div_element.find_elements(By.XPATH,
                                     './/*[contains(text(), "Movies & TV Shows")] | .//*[contains(text(), "Books")]'):
            text_found = True

        # Click on the element if the text is not found
        if not text_found and counter > 0:
            div_element.click()
            time.sleep(2)
            # Find the input element
            input_element = driver.find_element(By.XPATH, '//input[@id=":r4l:"]')

            # Click on the element
            input_element.click()
            time.sleep(2)
            # Find the div element containing the desired text
            div_element = driver.find_element(By.XPATH, '//div[contains(text(), "Books, Movies & Music")]')

            # Click on the div element
            div_element.click()

            time.sleep(600)