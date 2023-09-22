from flask import Flask, render_template, request, jsonify, json, session
from datetime import datetime
import time
from selenium import webdriver
from selenium.webdriver import Keys

from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from chromedriver_py import binary_path  # this will get you the path variable

from waitress import serve
import json
import pymongo

def selenium_method(id_element, search_text, limit=None, proxy=None):
    # s = Service('./chromedriver/chromedriver')
    s = Service(executable_path=binary_path)
    url_ws = "https://www.etsy.com/"
    options = Options()
    if proxy is not None: options.add_argument(f'--proxy-server={proxy}')
    options.add_experimental_option('detach', True)
    driver = webdriver.Chrome(service=s, options=options)
    a = ActionChains(driver)
    # params
    driver.get(url_ws)
    driver.maximize_window()
    #
    input_search = driver.find_element(By.XPATH, "//input[@data-id='search-query']")
    input_search.send_keys(search_text)

    search = driver.find_element(By.XPATH, "//button[@data-id='gnav-search-submit-button']")
    search.click()
    result = None
    try:
        while True:
            time.sleep(3)
            # pagination = driver.find_elements(By.XPATH, '//span[@class="screen-reader-only"]')
            pagination = driver.find_elements(By.XPATH, "//li[@class='wt-action-group__item-container']")
            last_pagination = pagination[-2].text
            if last_pagination.isdigit():
                last_pagination = int(last_pagination)
            prev_last_pagination = pagination[-3].text
            print(f'page len:\t{len(pagination)} | last: {last_pagination}')
            items = driver.find_elements(By.XPATH, "//div[@class='wt-height-full']")
            items = list(filter(lambda fit: json.loads(str(fit.get_attribute('data-appears-batch-options')))['total_items'] > 16, items))
            # Ad  by Etsy seller

            item_title_list = list(map(lambda fit: {
                'title': str(fit.find_element(By.TAG_NAME, "a").get_attribute('title')),
                'element': fit,
                'data-listing-id': str(fit.find_element(By.TAG_NAME, "a").get_attribute('data-listing-id'))
            }, items))
            current_page = str(driver.current_url).split("page=")
            current_page = 1 if len(current_page) <= 1 else int(current_page[1])
            item_title_list = list(filter(lambda f: f['data-listing-id'] == id_element, item_title_list))
            result_count = len(item_title_list)
            print(f'\n--------------\n\ncurrent_page: {current_page}\nresult_count: {result_count}\nlast_pagination: {last_pagination}')
            if result_count > 0 and last_pagination != int(current_page):
                print('YEAH!! I found it!!')
                element = item_title_list[0]
                element['element'].click()
                driver.switch_to.window(driver.window_handles[1])
                time.sleep(2)
                screen_shoot = driver.get_screenshot_as_base64()
                result = {
                    'list_id': id_element,
                    'title': element['title'],
                    'search_text': search_text,
                    'screenshot': screen_shoot,
                    'found_page': current_page,
                    'date': datetime.now().isoformat()
                }
                print(result)
                break
            elif result_count == 0 and last_pagination != int(current_page):
                print(f'!!!!!Came here!!!!!\n{last_pagination}!={current_page}')
                next_button = driver.find_elements(By.XPATH, '//a[@class="wt-btn wt-btn--filled wt-action-group__item wt-btn--small wt-btn--icon"]')
                print(next_button[-1].text)
                next_button[-1].click()
            elif result_count == 0 and last_pagination == int(current_page):
                print("end 1")
                break

            if limit is not None and int(current_page) >= int(limit):
                break
    except:
        result = None
    driver.quit()
    return result
