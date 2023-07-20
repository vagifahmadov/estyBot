import time
from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains

# main variables
s = Service('./chromedriver/chromedriver')
url = "https://www.etsy.com/"
options = Options()
options.add_experimental_option('detach', True)
driver = webdriver.Chrome(service=s, options=options)
a = ActionChains(driver)
# params
driver.get(url)
driver.maximize_window()

category = driver.find_element(By.XPATH, "//span[@id='catnav-primary-link-10923']")
category.click()
# seller XPATH: //span[@data-ad-label="Ad by Etsy seller"]

# item = driver.find_element(By.XPATH, "searchbox-searchbutton")


def print_hi(name):
    print(f'Height: {name}')  # Press Ctrl+F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi("Hi")
