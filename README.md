## How to set up and run

### Create virtual environment

##### Windows

    py -3 -m venv venv

##### Linux/MaxOS

    python3 -m venv venv

### Activate virtual environment

##### Windows

    venv\Scripts\activate

##### Linux/MaxOS

    . venv/bin/activate

### Install required libraries

    pip3 install -r requirements.txt

### Run app locally

    flask run

## Endpoints

### Ping Check

    http://127.0.0.1:5000/

### Crypto Currency

##### Get Prediction

    http://127.0.0.1:5000/crypto-currency/predict

##### Get Prediction By Currency

    http://127.0.0.1:5000/crypto-currency/predict/<name>

    Ex: http://127.0.0.1:5000/crypto-currency/predict/BTC_USD

##### Get Prediction By Currency and Action

    http://127.0.0.1:5000/crypto-currency/predict/<name>/<value>

    Ex: http://127.0.0.1:5000/crypto-currency/predict/BTC_USD/price

### News Endpoints

##### News Create

    http://127.0.0.1:5000/news/add

    {
    "title": "", 
    "description": "", 
    "author": ""
    }

##### News Get All

    http://127.0.0.1:5000/news/all

##### News Get By id

    http://127.0.0.1:5000/news/<id>

    Ex: http://127.0.0.1:5000/news/633b563a98178d25528e4ca5

##### News Update

    http://127.0.0.1:5000/news/update

    {
    "_id":"",
    "title": "", 
    "description": "", 
    "author": ""
    }

##### News Delete
    http://127.0.0.1:5000/news/delete/<id>

    Ex: http://127.0.0.1:5000/news/delete/633b563a98178d25528e4ca5

