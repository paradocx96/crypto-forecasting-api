from bson.json_util import dumps
from bson.objectid import ObjectId
from datetime import datetime
from flask import Flask, jsonify, request
from flask_apscheduler import APScheduler
from flask_cors import CORS
from flask_pymongo import PyMongo

from model import schedule_model_training, is_training, CURRENCIES
from web_scrapping import get_sentiment, get_sentiment_score

app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "*"}})
app.config['CORS_HEADERS'] = 'Content-Type'
scheduler = APScheduler()

# Mongo Config
app.config["MONGO_URI"] = 'mongodb+srv://ssd:root@ead.vuzt9we.mongodb.net/de_db?retryWrites=true&w=majority'
mongo = PyMongo(app)

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
        response = mongo.db.news.insert_one(
            {'title': _title, 'description': _description, 'author': _author, 'image': _image, 'date': _date})

        resp = jsonify('News Create Successfully!')
        resp.status_code = 200
        return resp
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
        news = mongo.db.news.update_one(
            {'_id': ObjectId(_id['$oid']) if '$oid' in _id else ObjectId(_id)},
            {'$set': {'title': _title, 'description': _description, 'author': _author, 'image': _image, 'date': _date}}
        )

        resp = jsonify('News Update Successfully!')
        resp.status_code = 200
        return resp
    else:
        return not_found()


@app.route('/news/delete/<id>', methods=['DELETE'])
def delete_news(id):
    mongo.db.news.delete_one({'_id': ObjectId(id)})
    resp = jsonify('News Deleted successfully!')
    resp.status_code = 200
    return resp


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
        response = mongo.db.currency.insert_one(
            {'name': _name, 'code': _code, 'description': _description, 'image': _image, 'date': _date})

        resp = jsonify('Currency Create Successfully!')
        resp.status_code = 200
        return resp
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
        currency = mongo.db.currency.update_one(
            {'_id': ObjectId(_id['$oid']) if '$oid' in _id else ObjectId(_id)},
            {'$set': {'name': _name, 'code': _code, 'description': _description, 'image': _image, 'date': _date}}
        )

        resp = jsonify('Currency Update Successfully!')
        resp.status_code = 200
        return resp
    else:
        return not_found()


@app.route('/currency/delete/<id>', methods=['DELETE'])
def delete_currency(id):
    mongo.db.currency.delete_one({'_id': ObjectId(id)})
    resp = jsonify('Currency Deleted successfully!')
    resp.status_code = 200
    return resp


@app.errorhandler(404)
def not_found(error=None):
    message = {
        'status': 404,
        'message': 'Not Found: ' + request.url,
    }
    resp = jsonify(message)
    resp.status_code = 404
    return resp


if __name__ == "__main__":
    app.run()
