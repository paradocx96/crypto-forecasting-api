import os
from bson.json_util import dumps
from bson.objectid import ObjectId
from datetime import datetime
from flask import Flask, jsonify, request
from flask_apscheduler import APScheduler
from flask_cors import CORS
from flask_pymongo import PyMongo
from dotenv import load_dotenv
from pymongo import MongoClient
import pprint

from model import schedule_model_training, is_training, CURRENCIES
from web_scrapping import get_sentiment, get_sentiment_score

app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "*"}})
app.config['CORS_HEADERS'] = 'Content-Type'
scheduler = APScheduler()
load_dotenv()

# Mongo Config
try:
    mongodb_url_with_db = os.getenv('mongodb_url_with_db')
    mongodb_url_without_db = os.getenv('mongodb_url_without_db')
except BaseException:
    mongodb_url_with_db = os.environ['mongodb_url_with_db']
    mongodb_url_without_db = os.environ['mongodb_url_without_db']

app.config["MONGO_URI"] = mongodb_url_with_db
mongo = PyMongo(app)

myClient = MongoClient(mongodb_url_without_db)
db = myClient["de_db"]

schedule_model_training()
'''
    schedule model re-training
'''
scheduler.add_job(id='Scheduled Task', func=schedule_model_training, trigger="interval", seconds=3600)
scheduler.start()


@app.route('/', methods=['GET'])
def index():
    return jsonify({'server': 'active', 'message': 'Crypto Currency Forecasting Sever is Active'})


@app.route("/crypto-currency/predict", methods=['GET'])
def predict():
    if is_training():
        response = jsonify({
            "message": "all forecasting models are training now!",
            "code": 100
        })
    else:
        data = dict()
        for currency in list(CURRENCIES.keys()):
            if CURRENCIES[currency]["enable"] and CURRENCIES[currency]["available_data"]:
                data[currency] = {
                    "price": CURRENCIES[currency]["price"],
                    "volume": CURRENCIES[currency]["volume"],
                    "market_cap": CURRENCIES[currency]["market_cap"]
                }

        response = jsonify({
            "code": 200,
            "message": "Success",
            "data": data
        })
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response, 200


@app.route("/crypto-currency/sentiment", methods=['GET'])
def sentiment():
    response = jsonify({
        "code": 200,
        "message": "Success",
        "sentiment": get_sentiment(),
        "score": get_sentiment_score()
    })
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response, 200


@app.route('/crypto-currency/predict/<name>')
def predict_currency(name=None):
    if is_training():
        response = jsonify({
            "message": "all forecasting models are training now!",
            "code": 100
        })
    else:
        data = dict()

        if CURRENCIES[name]["enable"] and CURRENCIES[name]["available_data"]:
            data = {
                "price": CURRENCIES[name]["price"],
                "volume": CURRENCIES[name]["volume"],
                "market_cap": CURRENCIES[name]["market_cap"]
            }

        response = jsonify({
            "code": 200,
            "message": "Success",
            "data": data
        })
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response, 200


@app.route('/crypto-currency/predict/<name>/<value>')
def predict_currency_action(name=None, value=None):
    if is_training():
        response = jsonify({
            "message": "all forecasting models are training now!",
            "code": 100
        })
    else:
        data = dict()

        if CURRENCIES[name]["enable"] and CURRENCIES[name]["available_data"]:
            data = {
                "exceeded": round(CURRENCIES[name][value]["exceeded"], 2),
                "score": round(CURRENCIES[name][value]["score"], 5),
                "today": round(CURRENCIES[name][value]["today"], 2),
                "tomorrow": round(CURRENCIES[name][value]["tomorrow"], 2)
            }

        response = jsonify({
            "code": 200,
            "message": "Success",
            "data": data
        })
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response, 200


'''
Auth Endpoints

@auth_signin()
/auth/signin - User SignIn

@auth_signup()
/auth/signup - User SignUp
'''


# User SignIn method
@app.route('/auth/signin', methods=['POST'])
def auth_signin():
    _json = request.json
    _username = _json['username']
    _password = _json['password']

    # validate the received values
    if _username and _password and request.method == 'POST':
        check_user = mongo.db.user.find_one({"username": _username})

        if check_user is None:
            response = jsonify({
                "code": 200,
                "message": "Unsuccessful",
                "data": 'Username Incorrect!'
            })
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response, 200
        else:
            if check_user['password'] != _password:
                response = jsonify({
                    "code": 200,
                    "message": "Unsuccessful",
                    "data": 'Password Incorrect!'
                })
                response.headers.add('Access-Control-Allow-Origin', '*')
                return response, 200
            elif check_user['password'] == _password:
                res = {
                    "full_name": check_user['full_name'],
                    "username": check_user['username'],
                    "email": check_user['email'],
                    "role": check_user['role'],
                    "image": check_user['image'],
                    'created': check_user['created'],
                    'updated': check_user['updated']
                }
                response = jsonify({
                    "code": 200,
                    "message": "Success",
                    "data": res
                })
                response.headers.add('Access-Control-Allow-Origin', '*')
                return response, 200
            else:
                response = jsonify({
                    "code": 204,
                    "message": "Unsuccessful",
                    "data": 'Something Wrong!'
                })
                response.headers.add('Access-Control-Allow-Origin', '*')
                return response, 204


# User SignUp method
@app.route('/auth/signup', methods=['POST'])
def auth_signup():
    _json = request.json
    _fullName = _json['full_name']
    _username = _json['username']
    _email = _json['email']
    _password = _json['password']
    _role = _json['role']
    _image = _json['image']

    current_date_time = datetime.now()
    _created = current_date_time.strftime("%Y-%m-%d %H:%M:%S")

    # validate the received values
    if _fullName and _username and _email and _password and _role and request.method == 'POST':
        check_username = mongo.db.user.find_one({"username": _username})
        check_email = mongo.db.user.find_one({"email": _email})

        if check_username is not None:
            response = jsonify({
                "code": 200,
                "message": "Unsuccessful",
                "data": 'Username Already Exists!'
            })
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response, 200
        elif check_email is not None:
            response = jsonify({
                "code": 200,
                "message": "Unsuccessful",
                "data": 'Email Already Exists!'
            })
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response, 200
        else:
            res = mongo.db.user.insert_one({
                'full_name': _fullName,
                'username': _username,
                'email': _email,
                'password': _password,
                'role': _role,
                'image': _image,
                'created': _created,
                'updated': "default"
            })

            response = jsonify({
                "code": 201,
                "message": "Success",
                "data": 'User Registration Successfully!'
            })
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response, 201


# News Endpoints
@app.route('/news/add', methods=['POST'])
def add_news():
    _json = request.json
    _title = _json['title']
    _description = _json['description']
    _author = _json['author']
    _image = _json['image']
    _date = datetime.now()

    # validate the received values
    if _title and _description and _author and _image and _date and request.method == 'POST':
        # save details
        res = mongo.db.news.insert_one(
            {'title': _title, 'description': _description, 'author': _author, 'image': _image, 'date': _date})

        response = jsonify({
            "code": 200,
            "message": "Success",
            "data": 'News Create Successfully!'
        })
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response, 200
    else:
        return not_found()


@app.route('/news/all')
def all_news():
    news = mongo.db.news.find()
    resp = dumps(news, indent=2)
    return resp


@app.route('/news/<id>')
def get_news_by_id(id):
    news = mongo.db.news.find_one({'_id': ObjectId(id)})
    resp = dumps(news, indent=2)
    return resp


@app.route('/news/update', methods=['PUT'])
def update_news():
    _json = request.json
    _id = _json['_id']
    _title = _json['title']
    _description = _json['description']
    _author = _json['author']
    _image = _json['image']
    _date = datetime.now()

    # validate the received values
    if _title and _description and _author and _image and _date and _id and request.method == 'PUT':
        # save edits
        res = mongo.db.news.update_one(
            {'_id': ObjectId(_id['$oid']) if '$oid' in _id else ObjectId(_id)},
            {'$set': {'title': _title, 'description': _description, 'author': _author, 'image': _image, 'date': _date}}
        )

        response = jsonify({
            "code": 200,
            "message": "Success",
            "data": 'News Update Successfully!'
        })
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response, 200
    else:
        return not_found()


@app.route('/news/delete/<id>', methods=['DELETE'])
def delete_news(id):
    res = mongo.db.news.delete_one({'_id': ObjectId(id)})

    response = jsonify({
        "code": 200,
        "message": "Success",
        "data": 'News Deleted successfully!'
    })
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response, 200


# Currency Data Endpoints
@app.route('/currency/add', methods=['POST'])
def add_currency():
    _json = request.json
    _name = _json['name']
    _code = _json['code']
    _description = _json['description']
    _image = _json['image']
    _date = datetime.now()

    # validate the received values
    if _name and _code and _description and _image and _date and request.method == 'POST':
        # save details
        res = mongo.db.currency.insert_one(
            {'name': _name, 'code': _code, 'description': _description, 'image': _image, 'date': _date})

        response = jsonify({
            "code": 200,
            "message": "Success",
            "data": 'Currency Create Successfully!'
        })
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response, 200
    else:
        return not_found()


@app.route('/currency/all')
def all_currency():
    currency = mongo.db.currency.find()
    resp = dumps(currency, indent=2)
    return resp


@app.route('/currency/<id>')
def get_currency_by_id(id):
    currency = mongo.db.currency.find_one({'_id': ObjectId(id)})
    resp = dumps(currency, indent=2)
    return resp


@app.route('/currency/update', methods=['PUT'])
def update_currency():
    _json = request.json
    _id = _json['_id']
    _name = _json['name']
    _code = _json['code']
    _description = _json['description']
    _image = _json['image']
    _date = datetime.now()

    # validate the received values
    if _name and _code and _description and _image and _date and request.method == 'PUT':
        # save edits
        res = mongo.db.currency.update_one(
            {'_id': ObjectId(_id['$oid']) if '$oid' in _id else ObjectId(_id)},
            {'$set': {'name': _name, 'code': _code, 'description': _description, 'image': _image, 'date': _date}}
        )

        response = jsonify({
            "code": 200,
            "message": "Success",
            "data": 'Currency Update Successfully!'
        })
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response, 200
    else:
        return not_found()


@app.route('/currency/delete/<id>', methods=['DELETE'])
def delete_currency(id):
    res = mongo.db.currency.delete_one({'_id': ObjectId(id)})

    response = jsonify({
        "code": 200,
        "message": "Success",
        "data": 'Currency Deleted successfully!'
    })
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response, 200


# Saved Coin Data Endpoints
@app.route('/api/coin/<coin>')
def get_save_coin(coin):
    collection_name = "data_" + coin.lower()
    collection = db[collection_name]

    data = collection.find()
    list_data = list(data)
    response = dumps(list_data, indent=2)

    return response, 200


@app.route('/api/coin/<coin>/<id>')
def get_save_coin_data_by_id(coin=None, id=None):
    collection_name = "data_" + coin.lower()
    collection = db[collection_name]

    data = collection.find_one({'_id': ObjectId(id)})
    response = dumps(data, indent=2)

    return response, 200


@app.errorhandler(404)
def not_found(error=None):
    response = jsonify({
        "code": 404,
        "message": "Unsuccessful",
        "url": 'Not Found: ' + request.url
    })
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response, 404


if __name__ == "__main__":
    app.run()
