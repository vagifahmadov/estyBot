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
from datetime import datetime
from flask_mysqldb import MySQL
from helper.methods import *
from pandas import *
from werkzeug.utils import secure_filename
import os
import uuid
import ipaddress


UPLOAD_FOLDER = 'upload'
ALLOWED_EXTENSIONS = {'xls', 'xlsx', 'py'}

app = Flask(__name__, static_folder='static', template_folder='templates')
# app.config['UPLOAD_FOLDER'] = upload_folder
app.secret_key = "etsybot"
# mysql.init_app(app)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'etsy'
app.config['MYSQL_PASSWORD'] = '0ze2Qc]zb57YTPCi'
app.config['MYSQL_DB'] = 'etsy'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
mysql = MySQL(app)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def is_ipv4(string):
    try:
        ipaddress.IPv4Network(string)
        return True
    except ValueError:
        return False


@app.route('/', methods=["GET"])
def home():
    # main variables
    cursor = mysql.connection.cursor()
    list_id_table_data_sql = """SELECT list_id, search_text FROM `id_list`"""
    log_table_data_sql = """SELECT list_id, title, found_page, date FROM `products_log`"""
    proxy_list_sql = """SELECT `ip`, `desc` FROM `proxy_list`"""
    # TO DO LIST
    cursor.execute(list_id_table_data_sql)
    mysql.connection.commit()
    result_all_datas = cursor.fetchall()
    row_headers = list(map(lambda x: x[0], cursor.description))
    json_data = list(map(lambda r: dict(zip(row_headers, r)), result_all_datas))

    # id_list = list(map(lambda id_s: str(id_s['list_id']), json_data))
    # result = json_data
    data_table = list(map(lambda dt: list(dt.values()), json_data))
    dt_js = json_data
    # print(f'jd: {json_data}\t|\tdt: {data_table}')
    # LOG
    cursor.execute(log_table_data_sql)
    mysql.connection.commit()
    result_log_datas = cursor.fetchall()
    row_headers = list(map(lambda x: x[0], cursor.description))
    json_data = list(map(lambda r: dict(zip(row_headers, r)), result_log_datas))

    # id_list = list(map(lambda id_s: str(id_s['list_id']), json_data))
    # result = json_data
    log_data_table = list(map(lambda dt: list(dt.values()), json_data))
    lg_js = json_data
    log_data_table = list(map(lambda dt: list([dt[0], dt[1], dt[2], dt[3].strftime('%d.%m.%Y %M:%H')]), log_data_table))
    # list(map(lambda dt: print(dt[0:-2], '\t', dt[-1].strftime('%d.%m.%Y %M:%H')), log_data_table))

    # Proxy
    cursor.execute(proxy_list_sql)
    mysql.connection.commit()
    proxy_data_list = cursor.fetchall()
    row_headers = list(map(lambda x: x[0], cursor.description))
    json_data = list(map(lambda r: dict(zip(row_headers, r)), proxy_data_list))

    # id_list = list(map(lambda id_s: str(id_s['list_id']), json_data))
    # result = json_data
    proxy_data_table = list(map(lambda dt: list(dt.values()), json_data))
    px_js = json_data

    result = {
        'logTable': log_data_table,
        'dataTable': data_table,
        'proxyListData': proxy_data_table,
        'dtJSON': dt_js,
        'lgJSON': lg_js,
        'pxJSON': px_js
    }
    cursor.close()
    return render_template('index.html', data=result)


@app.route('/run', methods=["POST"])
def insert_item():
    # id_element = request.json['id']
    # category = request.json['category']
    request_data = request.json
    # limit = request.args.get('limit')
    limit = request_data['limit']
    limit = None if limit == '' else limit
    # proxy = request.args.get('proxy')
    proxy = request_data['proxy']
    proxy = None if proxy == '' else proxy
    id_list = request_data['idList']
    count_id = len(id_list)
    id_list = f"list_id in {tuple(id_list)}" if len(id_list) > 1 else f"list_id={id_list[0]}"
    print(f'limit: {limit} \t proxy: {proxy} \t idList: {id_list}')
    cursor = mysql.connection.cursor()
    cursor.execute(f"""SELECT list_id, search_text FROM `id_list` WHERE {id_list}""")
    mysql.connection.commit()
    result_all_datas = cursor.fetchall()
    row_headers = list(map(lambda x: x[0], cursor.description))
    json_data = list(map(lambda r: dict(zip(row_headers, r)), result_all_datas))
    result = list(map(lambda item: selenium_method(item['list_id'], item['search_text'], limit, proxy), json_data))
    result = list(filter(lambda r: r is not None, result))
    print(f'\n-----------------------------------------\nresult: {result}')
    if len(result) > 0:
        sql = """INSERT INTO products_log (list_id, title, found_page, screenshot, search_text, date) VALUES (%s, %s, %s, %s, %s, %s)"""
        values = list(map(lambda dc: (dc['list_id'], dc['title'], dc['found_page'], dc['screenshot'], dc['search_text'], dc['date']), result))
        cursor.executemany(sql, values)
        mysql.connection.commit()
    cursor.close()
    result = list(map(lambda r: {'idItem': r['list_id'], 'title': r['title']}, result))
    # print(result)
    result = {
        "message": f'Total logged {len(result)} of {count_id}.' if len(result) > 0 else f'0 logged  of {count_id}',
        "status": True if len(result) > 0 else False,
        'title': f'{len(result)} result found' if len(result) > 0 else 'Found nothing'
    }
    return result


@app.route('/insertItem', methods=["POST"])
def insert_element():
    # main variables
    req = request.json
    id_item = req["idItem"]
    search_item = req["search"]
    print(f'id: {id_item}\tsearch: {search_item}')
    cursor = mysql.connection.cursor()
    sql = "INSERT INTO id_list (list_id, search_text) VALUES (%s, %s)"
    val = (id_item, search_item)
    cursor.execute(sql, val)
    mysql.connection.commit()
    cursor.execute("""SELECT list_id, search_text FROM `id_list`""")
    mysql.connection.commit()
    result_all_datas = cursor.fetchall()
    row_headers = list(map(lambda x: x[0], cursor.description))
    json_data = list(map(lambda r: dict(zip(row_headers, r)), result_all_datas))
    # id_list = list(map(lambda id_s: str(id_s['id']), json_data))
    # result = json_data
    cursor.close()
    data_table = list(map(lambda dt: list(dt.values()), json_data))
    print(f'jd: {json_data}\t|\tdt: {data_table}')
    result = {
        'dataTable': data_table
    }
    return jsonify(result)


@app.route('/insertProxy', methods=["POST"])
def insert_proxy():
    # main variables
    req = request.json
    proxy_ip = req["ip"]
    desc = req["desc"]
    cursor = mysql.connection.cursor()
    sql = "INSERT INTO proxy_list (`ip`, `desc`) VALUES (%s, %s)"
    val = (proxy_ip, desc)
    cursor.execute(sql, val)
    mysql.connection.commit()
    cursor.execute("""SELECT `ip`, `desc` FROM `proxy_list`""")
    mysql.connection.commit()
    result_all_datas = cursor.fetchall()
    row_headers = list(map(lambda x: x[0], cursor.description))
    json_data = list(map(lambda r: dict(zip(row_headers, r)), result_all_datas))
    # id_list = list(map(lambda id_s: str(id_s['id']), json_data))
    # result = json_data
    cursor.close()
    proxy_list_data = list(map(lambda dt: list(dt.values()), json_data))
    print(f'jd: {json_data}\t|\tdt: {proxy_list_data}')
    result = {
        'proxyListData': proxy_list_data
    }
    return jsonify(result)


@app.route('/deleteItem', methods=["POST"])
def delete_item():
    # main variables
    req = request.json
    id_item = req["idItem"]
    cursor = mysql.connection.cursor()
    sql = f"DELETE FROM id_list WHERE list_id = '{id_item}'"
    cursor.execute(sql)
    mysql.connection.commit()
    cursor.execute("""SELECT list_id, search_text FROM `id_list`""")
    mysql.connection.commit()
    result_all_datas = cursor.fetchall()
    row_headers = list(map(lambda x: x[0], cursor.description))
    json_data = list(map(lambda r: dict(zip(row_headers, r)), result_all_datas))
    # id_list = list(map(lambda id_s: str(id_s['id']), json_data))
    # result = json_data
    cursor.close()
    data_table = list(map(lambda dt: list(dt.values()), json_data))
    result = {
        'dataTable': data_table
    }
    return jsonify(result)


@app.route('/deleteProxy', methods=["POST"])
def delete_proxy():
    # main variables
    req = request.json
    id_item = req["ip"]
    cursor = mysql.connection.cursor()
    sql = f"DELETE FROM proxy_list WHERE `ip` = '{id_item}'"
    cursor.execute(sql)
    mysql.connection.commit()
    cursor.execute("""SELECT `ip`, `desc` FROM `proxy_list`""")
    mysql.connection.commit()
    proxy_data_list = cursor.fetchall()
    row_headers = list(map(lambda x: x[0], cursor.description))
    json_data = list(map(lambda r: dict(zip(row_headers, r)), proxy_data_list))
    # id_list = list(map(lambda id_s: str(id_s['id']), json_data))
    # result = json_data
    cursor.close()
    proxy_list_table = list(map(lambda dt: list(dt.values()), json_data))
    result = {
        'proxyListData': proxy_list_table
    }
    return jsonify(result)


# /importExel
@app.route('/importExel', methods=["POST"])
def import_exel():
    result = False
    if request.method == 'POST':
        # check if the post request has the file part
        file = request.files.get('file')
        print(f'files:\t{file.filename}')
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file and allowed_file(file.filename):
            type_file = str(file.filename).split(".")[-1]
            file.filename = f'{uuid.uuid4().hex}.{type_file}'
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            path = f"upload/{file.filename}"
            # pandas
            xls = ExcelFile(path)
            df = xls.parse(xls.sheet_names[0])
            ip_list = list(df['iplist'])
            ip_list = list(map(lambda f: f if is_ipv4(f) else None, ip_list))
            ip_list = list(filter(lambda f: f is not None, ip_list))
            print(f'\n\n\n\n---------------\n{df.to_dict()}\t{ip_list}\n-----------------\n\n\n\n\n')

    cursor = mysql.connection.cursor()
    sql = (f"INSERT INTO `proxy_list` (`ip`) SELECT 'stuff for value1', 'stuff for value2' FROM DUAL WHERE NOT EXISTS (SELECT * FROM `table`"
           f"WHERE `value1`='stuff for value1' AND `value2`='stuff for value2' LIMIT 1)")

    # cursor.execute(sql)
    # mysql.connection.commit()
    # cursor.execute("""SELECT `ip`, `desc` FROM `proxy_list`""")
    # mysql.connection.commit()
    # proxy_data_list = cursor.fetchall()
    # row_headers = list(map(lambda x: x[0], cursor.description))
    # json_data = list(map(lambda r: dict(zip(row_headers, r)), proxy_data_list))
    # # id_list = list(map(lambda id_s: str(id_s['id']), json_data))
    # # result = json_data
    # cursor.close()
    # proxy_list_table = list(map(lambda dt: list(dt.values()), json_data))
    # result = {
    #     'proxyListData': proxy_list_table
    # }
    return jsonify(result)


if __name__ == '__main__':
    app.run(debug=True)
