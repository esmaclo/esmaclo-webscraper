import requests
import os
import json
import time
from flask import Flask, Response, request
from flask_cors import CORS
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from selenium.webdriver.chrome.options import Options

CHROMEDRIVER_PATH = os.environ.get('CHROMEDRIVER_PATH', '/usr/local/bin/chromedriver')
GOOGLE_CHROME_BIN = os.environ.get('GOOGLE_CHROME_BIN', '/usr/bin/google-chrome')
BOT_URL = f'https://api.telegram.org/bot{os.environ["BOT_KEY"]}/'
CHAT_ID = 274429781
DELAY = 60
NUM_OF_TIMES = 10
URL = 'https://www.amazon.es/dp/B07X8CVLRP'

options = Options()
options.binary_location = GOOGLE_CHROME_BIN
options.add_argument('--disable-gpu')
options.add_argument('--no-sandbox')
options.headless = True

print('Building chrome driver...')
driver = webdriver.Chrome(executable_path=CHROMEDRIVER_PATH, chrome_options=options)

print('Starting app...')
app = Flask(__name__)
CORS(app)


def scrape_amazon_price(url):
    driver.get(url)

    try:
        element = driver.find_element_by_id('priceblock_ourprice').text
    except NoSuchElementException:
        element = None
    return element


@app.route("/")
def index():
    return 'Scraper alive!'

@app.route('/', methods=['POST'])
def scrape():
    #data = request.json

    #print(data)
    #chat_id = data['message']['chat']['id']
    #message = data['message']['text']

    i = 0
    price_under = float(30.0)
    while i < NUM_OF_TIMES:
        element = scrape_amazon_price(URL)

        status = 200 if element is not None else 412

        if status == 200:

            element = element.replace(",",".")
            element = element.replace(" €","")
            element = float(element)

            if element < price_under:

                json_data = {
                    "chat_id": CHAT_ID,
                    "text": 'El precio de ' + URL + ' ha bajado de ' + PRICE_UNDER + ' € a ' + element + ' €.',
                }

                message_url = BOT_URL + 'sendMessage'
                requests.post(message_url, json=json_data)

                price_under = element

        time.sleep(DELAY)
        i += 1

    return ''

#@app.route("/api/scrape", methods=['POST'])
#def scrape():
#    if request.json is None:
#        error = {"Error": "Missing url"}
#        return Response(json.dumps(error), status=400, mimetype='application/json')

#    url = request.json.get('url', None)
#    print(url)
#    element = scrape_amazon_price(message)

#    status = 200 if element is not None else 412

#    response = json.dumps({'Price': element})

#    return Response(response=response, status=status, mimetype='application/json')


if __name__ == '__main__':
    app.run(debug=True)
