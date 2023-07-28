import time
from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
import json
from flask import Flask, jsonify
from waitress import serve
import json

app = Flask(__name__)

# main variables
url = "https://www.etsy.com/"


def find_current_page(pagination_element: list):
    try:
        pag_list = list(
            map(lambda pg: pagination_element[pagination_element.index(pg) + 1].text if pg.text == 'Current page' else None, pagination_element))
        cur_page_try = list(filter(lambda fpg: fpg is not None, pag_list))[0]
        cur_p = int(cur_page_try.split("Page ")[1]) - 1
    except ValueError:
        pag_list = list(
            map(lambda pg: pagination_element[pagination_element.index(pg) - 1].text if pg.text == 'Current page' else None, pagination_element))
        cur_page_try = list(filter(lambda fpg: fpg is not None, pag_list))[0]
        cur_p = int(cur_page_try.split("Page ")[1]) + 1

    return cur_p,


@app.route('/')
def bot():
    return "OK"


@app.route('/test')
def test():
    # main variables
    s = Service('./chromedriver/chromedriver')
    url_ws = "https://www.etsy.com/"
    options = Options()
    options.add_experimental_option('detach', True)
    driver = webdriver.Chrome(service=s, options=options)
    a = ActionChains(driver)
    # params
    driver.get(url_ws)
    driver.maximize_window()

    category = driver.find_element(By.XPATH, "//span[@id='catnav-primary-link-10923']")
    category.click()
    time.sleep(3)
    pagination = driver.find_elements(By.XPATH, '//span[@class="screen-reader-only"]')
    print(f'page len:\t{len(pagination)}')
    # sellers = driver.find_elements(By.XPATH, '//span[@data-ad-label="Ad by Etsy seller"]')
    # sellers = driver.find_elements(By.XPATH, '//span[@class="wt-text-title-small"]')  # big page
    # phrase = 'Personalized camera strap with blue world map design. Comfortable and safe strap - Best gift for photographer. Purple and padded strap'
    # seller_name = 'InTePro'
    items = driver.find_elements(By.XPATH, "//div[@class='wt-height-full']")
    items = list(filter(lambda fit: json.loads(str(fit.get_attribute('data-appears-batch-options')))['total_items'] > 16, items))
    item_title_list = list(map(lambda fit: {
        'title': str(fit.find_element(By.TAG_NAME, "a").get_attribute('title')),
        # 'element': fit,
        'data-listing-id': str(fit.find_element(By.TAG_NAME, "a").get_attribute('data-listing-id'))
    }, items))
    print(f'\nList:\n--------------------\n{item_title_list}\n--------------------\n')
    print(f'items quota: {len(items)}')
    wanted_product_list = [
        {
            "data-listing-id": "1264737415"
        }
    ]
    list(map(lambda wl: list(filter), wanted_product_list))
    return jsonify(item_title_list)


if __name__ == '__main__':
    serve(app, host='localhost', port=5000)
