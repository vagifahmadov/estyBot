from flask import Flask, render_template, request, jsonify, json, session
import time
from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from waitress import serve
import json

app = Flask(__name__, static_folder='static', template_folder='templates')
# app.config['UPLOAD_FOLDER'] = upload_folder
app.secret_key = "etsybot"


@app.route('/')
def home():
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
    wanted_product_list = ["398801525"]
    print(f'items quota: {len(items)}')
    item_title_list = list(filter(lambda f: f['data-listing-id'] in wanted_product_list, item_title_list))

    return render_template('index.html', data=item_title_list)


if __name__ == '__main__':
    app.run(debug=True)
