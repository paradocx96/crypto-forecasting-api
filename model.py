import os
import ssl
from urllib.request import Request, urlopen
import certifi
from model_training.pp_market_cap import pp_market_cap
from model_training.pp_price import pp_price
from model_training.pp_volume import pp_volume
from web_scrapping import start_web_scrapping, set_sentiment

DATABASE_DIR = f"database{os.sep}"

TRAINING = False
THRESHOLD = 1000000

CURRENCIES = {
    "BTC_USD": {
        "url": "https://coingecko.com/price_charts/export/1/usd.csv",
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

    print(CURRENCIES)

    set_sentiment('Not Available')
    start_web_scrapping()
