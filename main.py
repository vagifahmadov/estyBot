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
time.sleep(3)
pagination = driver.find_elements(By.XPATH, '//span[@class="screen-reader-only"]')
print(f'page len:\t{len(pagination)} | {pagination[3].text}')
# seller XPATH: //span[@data-ad-label="Ad by Etsy seller"]

# item = driver.find_element(By.XPATH, "searchbox-searchbutton")


def find_current_page(pagination_element: list):
    try:
        pag_list = list(map(lambda pg: pagination_element[pagination_element.index(pg)+1].text if pg.text == 'Current page' else None, pagination_element))
        cur_page_try = list(filter(lambda fpg: fpg is not None, pag_list))[0]
        print(f'cr+1:\t{cur_page_try}')
        cur_p = int(cur_page_try.split("Page ")[1])-1
    except ValueError:
        pag_list = list(map(lambda pg: pagination_element[pagination_element.index(pg)-1].text if pg.text == 'Current page' else None, pagination_element))
        cur_page_try = list(filter(lambda fpg: fpg is not None, pag_list))[0]
        print(f'cr-1:\t{cur_page_try}')
        cur_p = int(cur_page_try.split("Page ")[1])+1

    return cur_p


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print(f'current page is:\t{find_current_page(pagination_element=pagination)}')
