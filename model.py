import os
import ssl
from urllib.request import Request, urlopen
import certifi
from model_training.pp_market_cap import pp_market_cap
from model_training.pp_price import pp_price
from model_training.pp_volume import pp_volume
from web_scrapping import start_web_scrapping, set_sentiment
from pymongo import MongoClient
from dotenv import load_dotenv
import requests
import csv
import time

load_dotenv()

try:
    mongodb_url_without_db = os.getenv('mongodb_url_without_db')
except BaseException:
    mongodb_url_without_db = os.environ['mongodb_url_without_db']

# Mongo Config
myClient = MongoClient(mongodb_url_without_db)
db = myClient["de_db"]

DATABASE_DIR = f"database{os.sep}"

TRAINING = False
THRESHOLD = 1000000

CURRENCIES = {
    "BTC_USD": {
        "url": "https://coingecko.com/price_charts/export/1/usd.csv",
        "url_two": "https://api.coinmarketcap.com/data-api/v3/cryptocurrency/historical?id=1&convertId=2781&timeStart=1657001454&timeEnd=1665641454",
        "available_data": False,
        "path": None,
        "enable": True,
        "price": {
            "today": 0,
            "tomorrow": 0,
            "score": 0,
            "exceeded": False
        },
        "volume": {
            "today": 0,
            "tomorrow": 0,
            "score": 0,
            "exceeded": False
        },
        "market_cap": {
            "today": 0,
            "tomorrow": 0,
            "score": 0,
            "exceeded": False
        }
    },
    "ETH_USD": {
        "url": "https://www.coingecko.com/price_charts/export/279/usd.csv",
        "url_two": "https://api.coinmarketcap.com/data-api/v3/cryptocurrency/historical?id=1&convertId=2781&timeStart=1657001454&timeEnd=1665641454",
        "available_data": False,
        "path": None,
        "enable": True,
        "price": {
            "today": 0,
            "tomorrow": 0,
            "score": 0,
            "exceeded": False
        },
        "volume": {
            "today": 0,
            "tomorrow": 0,
            "score": 0,
            "exceeded": False
        },
        "market_cap": {
            "today": 0,
            "tomorrow": 0,
            "score": 0,
            "exceeded": False
        }
    },
    "PKEX_USD": {
        "url": "https://www.coingecko.com/price_charts/export/18616/usd.csv",
        "url_two": "https://api.coinmarketcap.com/data-api/v3/cryptocurrency/historical?id=1&convertId=2781&timeStart=1657001454&timeEnd=1665641454",
        "available_data": False,
        "path": None,
        "enable": True,
        "price": {
            "today": 0,
            "tomorrow": 0,
            "score": 0,
            "exceeded": False
        },
        "volume": {
            "today": 0,
            "tomorrow": 0,
            "score": 0,
            "exceeded": False
        },
        "market_cap": {
            "today": 0,
            "tomorrow": 0,
            "score": 0,
            "exceeded": False
        }
    },
    "SHIB_USD": {
        "url": "https://www.coingecko.com/price_charts/export/11939/usd.csv",
        "url_two": "https://api.coinmarketcap.com/data-api/v3/cryptocurrency/historical?id=1&convertId=2781&timeStart=1657001454&timeEnd=1665641454",
        "available_data": False,
        "path": None,
        "enable": True,
        "price": {
            "today": 0,
            "tomorrow": 0,
            "score": 0,
            "exceeded": False
        },
        "volume": {
            "today": 0,
            "tomorrow": 0,
            "score": 0,
            "exceeded": False
        },
        "market_cap": {
            "today": 0,
            "tomorrow": 0,
            "score": 0,
            "exceeded": False
        }
    },
    "DOGE_USD": {
        "url": "https://www.coingecko.com/price_charts/export/5/usd.csv",
        "url_two": "https://api.coinmarketcap.com/data-api/v3/cryptocurrency/historical?id=1&convertId=2781&timeStart=1657001454&timeEnd=1665641454",
        "available_data": False,
        "path": None,
        "enable": True,
        "price": {
            "today": 0,
            "tomorrow": 0,
            "score": 0,
            "exceeded": False
        },
        "volume": {
            "today": 0,
            "tomorrow": 0,
            "score": 0,
            "exceeded": False
        },
        "market_cap": {
            "today": 0,
            "tomorrow": 0,
            "score": 0,
            "exceeded": False
        }
    },
    "TRON_USD": {
        "url": "https://www.coingecko.com/price_charts/export/1094/usd.csv",
        "url_two": "https://api.coinmarketcap.com/data-api/v3/cryptocurrency/historical?id=1&convertId=2781&timeStart=1657001454&timeEnd=1665641454",
        "available_data": False,
        "path": None,
        "enable": True,
        "price": {
            "today": 0,
            "tomorrow": 0,
            "score": 0,
            "exceeded": False
        },
        "volume": {
            "today": 0,
            "tomorrow": 0,
            "score": 0,
            "exceeded": False
        },
        "market_cap": {
            "today": 0,
            "tomorrow": 0,
            "score": 0,
            "exceeded": False
        }
    },
    "BNB_USD": {
        "url": "https://www.coingecko.com/price_charts/export/825/usd.csv",
        "url_two": "https://api.coinmarketcap.com/data-api/v3/cryptocurrency/historical?id=1&convertId=2781&timeStart=1657001454&timeEnd=1665641454",
        "available_data": False,
        "path": None,
        "enable": True,
        "price": {
            "today": 0,
            "tomorrow": 0,
            "score": 0,
            "exceeded": False
        },
        "volume": {
            "today": 0,
            "tomorrow": 0,
            "score": 0,
            "exceeded": False
        },
        "market_cap": {
            "today": 0,
            "tomorrow": 0,
            "score": 0,
            "exceeded": False
        }
    },
    "SOL_USD": {
        "url": "https://www.coingecko.com/price_charts/export/4128/usd.csv",
        "url_two": "https://api.coinmarketcap.com/data-api/v3/cryptocurrency/historical?id=1&convertId=2781&timeStart=1657001454&timeEnd=1665641454",
        "available_data": False,
        "path": None,
        "enable": True,
        "price": {
            "today": 0,
            "tomorrow": 0,
            "score": 0,
            "exceeded": False
        },
        "volume": {
            "today": 0,
            "tomorrow": 0,
            "score": 0,
            "exceeded": False
        },
        "market_cap": {
            "today": 0,
            "tomorrow": 0,
            "score": 0,
            "exceeded": False
        }
    }
}


def download_data_sources():
    for currency in list(CURRENCIES.keys()):
        CURRENCIES[currency]["available_data"] = False
        CURRENCIES[currency]["path"] = None
    for currency in list(CURRENCIES.keys()):
        request = Request(
            url=CURRENCIES[currency]["url"],
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        print(f"download data source for {currency}")
        with urlopen(request, context=ssl.create_default_context(cafile=certifi.where())) as file:
            downloaded_file = file.read().decode('utf-8')
            csv_file = open(f'{DATABASE_DIR}{currency}.csv', "w+")
            csv_file.write(downloaded_file)
            csv_file.close()
            CURRENCIES[currency]["available_data"] = True
            CURRENCIES[currency]["path"] = f'{DATABASE_DIR}{currency}.csv'
            print(f"successfully downloaded data source for {currency}")


def is_data_sources_configured():
    for currency in list(CURRENCIES.keys()):
        if CURRENCIES[currency]["enable"] and not CURRENCIES[currency]["available_data"]:
            return False
    return True


def set_training(_flag):
    global TRAINING
    TRAINING = _flag


def is_training():
    return TRAINING


# Secondary Data Source Downloading
def secondary_download_data_sources():
    # Check CURRENCIES data source
    for currency in list(CURRENCIES.keys()):
        CURRENCIES[currency]["available_data"] = False
        CURRENCIES[currency]["path"] = None

    # Attempt by Currency
    for currency in list(CURRENCIES.keys()):
        # condition_one = CURRENCIES[currency]["available_data"]
        # condition_two = CURRENCIES[currency]["path"]
        # if condition_one is False & condition_two is None:

        # Header for request
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

        # Config for Request
        response = requests.request(
            "GET",
            url=CURRENCIES[currency]["url_two"],
            headers=headers,
            data={}
        )

        # Get response data from JSON
        data_json = response.json()
        capture_data = []
        table_headers = ['snapped_at', 'price', 'market_cap', 'total_volume']

        # Put data into Array
        for x in data_json['data']['quotes']:
            listing = [x['timeOpen'], x['quote']['open'], x['quote']['marketCap'], x['quote']['volume']]
            capture_data.append(listing)

        # Write new data in CSV files
        with open(f'{DATABASE_DIR}{currency}.csv', 'w', encoding='UTF8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(table_headers)
            writer.writerows(capture_data)
            CURRENCIES[currency]["available_data"] = True
            CURRENCIES[currency]["path"] = f'{DATABASE_DIR}{currency}.csv'
            print(f"Successfully downloaded secondary data source for {currency}")


# Save Trained Data in Database
def save_data():
    # Save data by Currency
    for currency in list(CURRENCIES.keys()):
        # Getting local date time
        local_time = time.localtime()
        time_format = time.strftime("%Y-%m-%d %H:%M:%S", local_time)

        # Define collection name for currency
        collection_name = "data_" + currency.lower()
        collection = db[collection_name]

        # Define Colum data from CURRENCIES
        _price_data = CURRENCIES[currency]["price"]
        _volume_data = CURRENCIES[currency]["volume"]
        _market_cap_data = CURRENCIES[currency]["market_cap"]

        # Create document data
        record = {'date_time': time_format,
                  'currency': currency,
                  'price': _price_data,
                  'volume': _volume_data,
                  'market_cap': _market_cap_data}

        # Create Currency data in database
        response = collection.insert_one(record)
        print(f"{currency} data saved in database")


def schedule_model_training():
    set_training(True)
    print("start model training")
    retry_count = 0
    while retry_count < 3:
        print("downloading data sources")
        retry_count += 1
        print(f"attempting - {retry_count}")
        download_data_sources()
        if is_data_sources_configured():
            print("data sources successfully downloaded")
            break

    # Attempt Second Round Downloading Data Source if 1st source failed
    retry_count_second = 0
    if retry_count == 3:
        while retry_count_second < 3:
            print("downloading secondary data sources")
            retry_count_second += 1
            print(f"secondary attempting - {retry_count_second}")

            # Calling Secondary Download Method
            secondary_download_data_sources()
            if is_data_sources_configured():
                print("data sources successfully downloaded")
                break

    # model training
    for currency in list(CURRENCIES.keys()):
        if CURRENCIES[currency]["enable"] and CURRENCIES[currency]["available_data"]:
            file_path = CURRENCIES[currency]["path"]
            today_price, pred_price = pp_price(file_path)
            today_volume, pred_volume = pp_volume(file_path)
            today_market_cap, pred_market_cap = pp_market_cap(file_path)
            # price
            CURRENCIES[currency]["price"]["today"] = today_price
            CURRENCIES[currency]["price"]["tomorrow"] = pred_price
            score = ((pred_price - today_price) / today_price) * 100
            if score < 0:
                score = 0
            CURRENCIES[currency]["price"]["score"] = score
            flag = False
            if pred_price >= THRESHOLD:
                flag = True
            CURRENCIES[currency]["price"]["exceeded"] = flag

            # volume
            CURRENCIES[currency]["volume"]["today"] = today_volume
            CURRENCIES[currency]["volume"]["tomorrow"] = pred_volume
            score = ((pred_volume - today_volume) / today_volume) * 100
            if score < 0:
                score = 0
            CURRENCIES[currency]["volume"]["score"] = score
            flag = False
            if pred_volume >= THRESHOLD:
                flag = True
            CURRENCIES[currency]["volume"]["exceeded"] = flag

            # market cap
            CURRENCIES[currency]["market_cap"]["today"] = today_market_cap
            CURRENCIES[currency]["market_cap"]["tomorrow"] = pred_market_cap
            score = ((pred_market_cap - today_market_cap) / today_market_cap) * 100
            if score < 0:
                score = 0
            CURRENCIES[currency]["market_cap"]["score"] = score
            flag = False
            if pred_market_cap >= THRESHOLD:
                flag = True
            CURRENCIES[currency]["market_cap"]["exceeded"] = flag

    print("end model training")
    set_training(False)
    save_data()

    print(CURRENCIES)

    set_sentiment('Not Available')
    start_web_scrapping()
