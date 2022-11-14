import os
from bson.json_util import dumps
from bson.objectid import ObjectId
from datetime import datetime
from flask import Flask, jsonify, request, send_file
from flask_apscheduler import APScheduler
from flask_cors import CORS
from flask_pymongo import PyMongo
from dotenv import load_dotenv
from pymongo import MongoClient
import csv

from model import schedule_model_training, is_training, CURRENCIES
from web_scrapping import get_sentiment, get_sentiment_score

# Flask App Configuration
app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "*"}})
app.config['CORS_HEADERS'] = 'Content-Type'
scheduler = APScheduler()
load_dotenv()

# MongoDB Configuration
# Import Connection String from env
try:
    mongodb_url_with_db = os.getenv('mongodb_url_with_db')
    mongodb_url_without_db = os.getenv('mongodb_url_without_db')
except BaseException:
    mongodb_url_with_db = os.environ['mongodb_url_with_db']
    mongodb_url_without_db = os.environ['mongodb_url_without_db']

# Configurate DB URL to Flask App
app.config["MONGO_URI"] = mongodb_url_with_db
mongo = PyMongo(app)

myClient = MongoClient(mongodb_url_without_db)
db = myClient["de_db"]

# Coin File Path
COIN_DIR = f"coin{os.sep}"

# Schedule model Training
schedule_model_training()

# Schedule model re-training
scheduler.add_job(id='Scheduled Task', func=schedule_model_training, trigger="interval", seconds=3600)
scheduler.start()


# Root Endpoint
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


'''
Crypto Currency Endpoints

@predict_currency(name)
/crypto-currency/predict/<name> [GET] - Get details by currency name

@predict_currency_action(name, value)
/crypto-currency/predict/<name>/<value> [GET] - Get details by currency name and action
'''


# Crypto Currency - Get details by currency name method
@app.route('/crypto-currency/predict/<name>')
def predict_currency(name=None):
    # Checking training is over or not
    if is_training():
        # If training is not over, send response for still training
        response = jsonify({
            "message": "all forecasting models are training now!",
            "code": 100
        })
    else:
        # Import trained data
        data = dict()

        # Check data validity
        if CURRENCIES[name]["enable"] and CURRENCIES[name]["available_data"]:
            # Create response data
            data = {
                "price": CURRENCIES[name]["price"],
                "volume": CURRENCIES[name]["volume"],
                "market_cap": CURRENCIES[name]["market_cap"]
            }

        # Create response
        response = jsonify({
            "code": 200,
            "message": "Success",
            "data": data
        })

    # Send response
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response, 200


# Crypto Currency - Get details by currency name and action
@app.route('/crypto-currency/predict/<name>/<value>')
def predict_currency_action(name=None, value=None):
    # Checking training is over or not
    if is_training():
        # If training is not over, send response for still training
        response = jsonify({
            "message": "all forecasting models are training now!",
            "code": 100
        })
    else:
        # Import trained data
        data = dict()

        # Check data validity
        if CURRENCIES[name]["enable"] and CURRENCIES[name]["available_data"]:
            # Create response
            data = {
                "exceeded": round(CURRENCIES[name][value]["exceeded"], 2),
                "score": round(CURRENCIES[name][value]["score"], 5),
                "today": round(CURRENCIES[name][value]["today"], 2),
                "tomorrow": round(CURRENCIES[name][value]["tomorrow"], 2)
            }

        # Create response
        response = jsonify({
            "code": 200,
            "message": "Success",
            "data": data
        })

    # Send response
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response, 200


'''
Auth Endpoints

@auth_signin()
/auth/signin [POST] - User SignIn

@auth_signup()
/auth/signup [POST] - User SignUp
'''


# User SignIn method
@app.route('/auth/signin', methods=['POST'])
def auth_signin():
    # Get JSON data
    _json = request.json
    _username = _json['username']
    _password = _json['password']

    # validate the received values
    if _username and _password and request.method == 'POST':
        # Check username availability in database
        check_user = mongo.db.user.find_one({"username": _username})

        # Check user is available or not
        if check_user is None:
            # Send response for username availability
            response = jsonify({
                "code": 200,
                "message": "Unsuccessful",
                "data": 'Username Incorrect!'
            })
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response, 200
        else:
            # Check password is match with user given
            if check_user['password'] != _password:
                # Send response for password incorrect
                response = jsonify({
                    "code": 200,
                    "message": "Unsuccessful",
                    "data": 'Password Incorrect!'
                })
                response.headers.add('Access-Control-Allow-Origin', '*')
                return response, 200
            # Checking password correction
            elif check_user['password'] == _password:
                # Create JSON response data
                res = {
                    "full_name": check_user['full_name'],
                    "username": check_user['username'],
                    "email": check_user['email'],
                    "role": check_user['role'],
                    "image": check_user['image'],
                    'created': check_user['created'],
                    'updated': check_user['updated']
                }

                # Send response for user signin
                response = jsonify({
                    "code": 200,
                    "message": "Success",
                    "data": res
                })
                response.headers.add('Access-Control-Allow-Origin', '*')
                return response, 200
            else:
                # Send response for error
                response = jsonify({
                    "code": 204,
                    "message": "Unsuccessful",
                    "data": 'Something Wrong!'
                })
                response.headers.add('Access-Control-Allow-Origin', '*')
                return response, 204
    else:
        # Send response for error
        return not_found()


# User SignUp method
@app.route('/auth/signup', methods=['POST'])
def auth_signup():
    # Get JSON data
    _json = request.json
    _fullName = _json['full_name']
    _username = _json['username']
    _email = _json['email']
    _password = _json['password']
    _role = _json['role']
    _image = _json['image']

    # Getting current data time
    current_date_time = datetime.now()
    _created = current_date_time.strftime("%Y-%m-%d %H:%M:%S")

    # validate the received values
    if _fullName and _username and _email and _password and _role and request.method == 'POST':
        # Check username availability in database
        check_username = mongo.db.user.find_one({"username": _username})

        # Check email availability in database
        check_email = mongo.db.user.find_one({"email": _email})

        # Check username availability
        if check_username is not None:
            # Send response for username availability
            response = jsonify({
                "code": 200,
                "message": "Unsuccessful",
                "data": 'Username Already Exists!'
            })
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response, 200

        # Check user availability
        elif check_email is not None:
            # Send response for email availability
            response = jsonify({
                "code": 200,
                "message": "Unsuccessful",
                "data": 'Email Already Exists!'
            })
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response, 200
        else:
            # Creating new user
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

            # Send response for user registration
            response = jsonify({
                "code": 201,
                "message": "Success",
                "data": 'User Registration Successfully!'
            })
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response, 201
    else:
        # Send response for error
        return not_found()


'''
User Management Endpoints

@get_all_users()
/user [GET] - Get all users

@get_user_by_id(uid)
/user/<id> [GET] - Get user by Id

@delete_user(uid)
/user/<id> [DELETE] - Delete user by Id

@update_user()
/user [PUT] - Update user

@update_password()
/user/change/password [PUT] - Update password

@update_username()
/user/change/username [PUT] - Update username
'''


# User - Get All method
@app.route('/user')
def get_all_users():
    # Get all available users
    user = mongo.db.user.find()

    # Convert data to JSON data
    resp = dumps(user, indent=2)
    return resp


# User - Get By Id method
@app.route('/user/<uid>')
def get_user_by_id(uid):
    try:
        # Find user by user id
        user = mongo.db.user.find_one({'_id': ObjectId(uid)})

        # Check user availability
        if user is None:
            # Send response for dose not exists
            response = jsonify({
                "code": 200,
                "message": "Unsuccessful",
                "data": 'User Does Not Exists!'
            })
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response, 200
        else:
            # Create JSON data
            data = {
                "_id": uid,
                "full_name": user['full_name'],
                "username": user['username'],
                "email": user['email'],
                "role": user['role'],
                "image": user['image'],
                'created': user['created'],
                'updated': user['updated']
            }

            # Send response for available user
            response = jsonify({
                "code": 200,
                "message": "Success",
                "data": data
            })
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response, 200
    except:
        # Send response for dose not exists
        response = jsonify({
            "code": 200,
            "message": "Unsuccessful",
            "data": 'User Does Not Exists!'
        })
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response, 200


# User - Delete by Id method
@app.route('/user/<uid>', methods=['DELETE'])
def delete_user(uid):
    # validate the received values
    if uid and request.method == 'DELETE':
        try:
            # Find user by user id
            user = mongo.db.user.find_one({'_id': ObjectId(uid)})

            if user is None:
                # Send response for dose not exists
                response = jsonify({
                    "code": 200,
                    "message": "Unsuccessful",
                    "data": 'User Does Not Exists!'
                })
                response.headers.add('Access-Control-Allow-Origin', '*')
                return response, 200
            else:
                # Delete user form database
                res = mongo.db.user.delete_one({'_id': ObjectId(uid)})

                # Send response for user remove
                response = jsonify({
                    "code": 202,
                    "message": "Success",
                    "data": 'User Delete Successfully!'
                })
                response.headers.add('Access-Control-Allow-Origin', '*')
                return response, 202
        except:
            # Send response for dose not exists
            response = jsonify({
                "code": 200,
                "message": "Unsuccessful",
                "data": 'User Does Not Exists!'
            })
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response, 200
    else:
        # Send response for error
        return not_found()


# User - Update method
@app.route('/user', methods=['PUT'])
def update_user():
    # Get JSON data
    _json = request.json
    _id = _json['_id']
    _fullName = _json['full_name']
    _email = _json['email']
    _role = _json['role']
    _image = _json['image']

    # Getting current data time
    current_date_time = datetime.now()
    _updated = current_date_time.strftime("%Y-%m-%d %H:%M:%S")

    # validate the received values
    if _id and _fullName and _email and _role and request.method == 'PUT':
        try:
            # Find user by user id
            user = mongo.db.user.find_one({'_id': ObjectId(_id)})

            if user is None:
                # Send response for dose not exists
                response = jsonify({
                    "code": 200,
                    "message": "Unsuccessful",
                    "data": 'User Does Not Exists!'
                })
                response.headers.add('Access-Control-Allow-Origin', '*')
                return response, 200
            else:
                # save update updated user data in database
                res = mongo.db.user.update_one(
                    {'_id': ObjectId(_id['$oid']) if '$oid' in _id else ObjectId(_id)},
                    {'$set': {
                        'full_name': _fullName,
                        'email': _email,
                        'role': _role,
                        'image': _image,
                        'updated': _updated
                    }}
                )

                # Send response for user update successful
                response = jsonify({
                    "code": 201,
                    "message": "Success",
                    "data": 'User Update Successfully!'
                })
                response.headers.add('Access-Control-Allow-Origin', '*')
                return response, 201
        except:
            # Send response for dose not exists
            response = jsonify({
                "code": 200,
                "message": "Unsuccessful",
                "data": 'User Does Not Exists!'
            })
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response, 200
    else:
        # Send response for error
        return not_found()


# User - Update Password method
@app.route('/user/change/password', methods=['PUT'])
def update_password():
    # Get JSON data
    _json = request.json
    _id = _json['_id']
    _password = _json['password']

    # Getting current data time
    date_time_password = datetime.now()
    _updated_password_time = date_time_password.strftime("%Y-%m-%d %H:%M:%S")

    # validate the received values
    if _id and _password and request.method == 'PUT':
        try:
            # Find user by user id
            user = mongo.db.user.find_one({'_id': ObjectId(_id)})

            # Check user available
            if user is None:
                # Send response for dose not exists
                response = jsonify({
                    "code": 200,
                    "message": "Unsuccessful",
                    "data": 'User Does Not Exists!'
                })
                response.headers.add('Access-Control-Allow-Origin', '*')
                return response, 200
            else:
                # save new password in database
                res = mongo.db.user.update_one(
                    {'_id': ObjectId(_id['$oid']) if '$oid' in _id else ObjectId(_id)},
                    {'$set': {
                        'password': _password,
                        'updated': _updated_password_time
                    }}
                )

                # Send response for update password in database
                response = jsonify({
                    "code": 201,
                    "message": "Success",
                    "data": 'Password Update Successfully!'
                })
                response.headers.add('Access-Control-Allow-Origin', '*')
                return response, 201
        except:
            # Send response for dose not exists
            response = jsonify({
                "code": 200,
                "message": "Unsuccessful",
                "data": 'User Does Not Exists!'
            })
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response, 200
    else:
        # Send response for error
        return not_found()


# User - Update Username method
@app.route('/user/change/username', methods=['PUT'])
def update_username():
    # Get JSON data
    _json = request.json
    _id = _json['_id']
    _username = _json['username']

    # Getting current data time
    date_time_username = datetime.now()
    _updated_username_time = date_time_username.strftime("%Y-%m-%d %H:%M:%S")

    # validate the received values
    if _id and _username and request.method == 'PUT':
        try:
            # Find user by user id
            user = mongo.db.user.find_one({'_id': ObjectId(_id)})

            if user is None:
                # Send response for dose not exists
                response = jsonify({
                    "code": 200,
                    "message": "Unsuccessful",
                    "data": 'User Does Not Exists!'
                })
                response.headers.add('Access-Control-Allow-Origin', '*')
                return response, 200
            else:
                # Find user by username
                check_username = mongo.db.user.find_one({"username": _username})

                # Check user available
                if check_username is not None:
                    # Send response for username availability
                    response = jsonify({
                        "code": 200,
                        "message": "Unsuccessful",
                        "data": 'Username Already Exists!'
                    })
                    response.headers.add('Access-Control-Allow-Origin', '*')
                    return response, 200
                else:
                    # save new password in database
                    res = mongo.db.user.update_one(
                        {'_id': ObjectId(_id['$oid']) if '$oid' in _id else ObjectId(_id)},
                        {'$set': {
                            'username': _username,
                            'updated': _updated_username_time
                        }}
                    )

                    # Send response for username update success
                    response = jsonify({
                        "code": 201,
                        "message": "Success",
                        "data": 'Username Update Successfully!'
                    })
                    response.headers.add('Access-Control-Allow-Origin', '*')
                    return response, 201
        except:
            # Send response for dose not exists
            response = jsonify({
                "code": 200,
                "message": "Unsuccessful",
                "data": 'User Does Not Exists!'
            })
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response, 200
    else:
        # Send response for error
        return not_found()


'''
News Management Endpoints

@add_news()
/news/add [POST] - Create News

@all_news()
/news/all [GET] - Get all News

@get_news_by_id(nid)
/news/<nid> [GET] - Get News by Id

@update_news()
/news/update [PUT] - Update News

@delete_news(nid)
/news/delete/<nid> [DELETE] - Delete News
'''


# News - Create new news
@app.route('/news/add', methods=['POST'])
def add_news():
    # Get JSON data
    _json = request.json
    _title = _json['title']
    _description = _json['description']
    _author = _json['author']
    _image = _json['image']
    _date = datetime.now()

    # validate the received values
    if _title and _description and _author and _image and _date and request.method == 'POST':
        # create new news in database
        res = mongo.db.news.insert_one(
            {'title': _title, 'description': _description, 'author': _author, 'image': _image, 'date': _date})

        # Send response fot new creation
        response = jsonify({
            "code": 200,
            "message": "Success",
            "data": 'News Create Successfully!'
        })
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response, 200
    else:
        # Send response for error
        return not_found()


# News - Get all News
@app.route('/news/all')
def all_news():
    # Get all available news
    news = mongo.db.news.find()

    # Convert data to JSON data
    resp = dumps(news, indent=2)
    return resp


# News - Get News by id
@app.route('/news/<nid>')
def get_news_by_id(nid):
    # Find news by id in database
    news = mongo.db.news.find_one({'_id': ObjectId(nid)})

    # Convert data to JSON data
    resp = dumps(news, indent=2)
    return resp


# News - Update News
@app.route('/news/update', methods=['PUT'])
def update_news():
    # Get JSON data
    _json = request.json
    _id = _json['_id']
    _title = _json['title']
    _description = _json['description']
    _author = _json['author']
    _image = _json['image']
    _date = datetime.now()

    # validate the received values
    if _title and _description and _author and _image and _date and _id and request.method == 'PUT':
        # Update relevant news data in database
        res = mongo.db.news.update_one(
            {'_id': ObjectId(_id['$oid']) if '$oid' in _id else ObjectId(_id)},
            {'$set': {'title': _title, 'description': _description, 'author': _author, 'image': _image, 'date': _date}}
        )

        # Send response for news update
        response = jsonify({
            "code": 200,
            "message": "Success",
            "data": 'News Update Successfully!'
        })
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response, 200
    else:
        # Send response for error
        return not_found()


# News - Delete News by id
@app.route('/news/delete/<nid>', methods=['DELETE'])
def delete_news(nid):
    # Find and Delete relevant News in database
    res = mongo.db.news.delete_one({'_id': ObjectId(nid)})

    # Send response for new delete
    response = jsonify({
        "code": 200,
        "message": "Success",
        "data": 'News Deleted successfully!'
    })
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response, 200


'''
Currency Management Endpoints

@add_currency()
/currency/add [POST] - Create Currency Details

@all_currency()
/currency/all [GET] - Get all Currency Details

@get_currency_by_id(cid)
/currency/<cid> [GET] - Get Currency by Id

@update_currency()
/currency/update [PUT] - Update Currency details

@delete_currency(nid)
/currency/delete/<id> [DELETE] - Delete Currency details by Id
'''


# Currency - Create new Currency data
@app.route('/currency/add', methods=['POST'])
def add_currency():
    # Get JSON data
    _json = request.json
    _name = _json['name']
    _code = _json['code']
    _description = _json['description']
    _image = _json['image']
    _date = datetime.now()

    # validate the received values
    if _name and _code and _description and _image and _date and request.method == 'POST':
        # Create Currency details in database
        res = mongo.db.currency.insert_one(
            {'name': _name, 'code': _code, 'description': _description, 'image': _image, 'date': _date})

        # Send response for data creation success
        response = jsonify({
            "code": 200,
            "message": "Success",
            "data": 'Currency Create Successfully!'
        })
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response, 200
    else:
        # Send response for error
        return not_found()


# Currency - Get all currency details
@app.route('/currency/all')
def all_currency():
    # Get all available currency details
    currency = mongo.db.currency.find()

    # Convert data to JSON data
    resp = dumps(currency, indent=2)
    return resp


# Currency - Get currency details by id
@app.route('/currency/<cid>')
def get_currency_by_id(cid):
    # Get currency details by id
    currency = mongo.db.currency.find_one({'_id': ObjectId(cid)})

    # Convert data to JSON data
    resp = dumps(currency, indent=2)
    return resp


# Currency - Update currency details
@app.route('/currency/update', methods=['PUT'])
def update_currency():
    # Get JSON data
    _json = request.json
    _id = _json['_id']
    _name = _json['name']
    _code = _json['code']
    _description = _json['description']
    _image = _json['image']
    _date = datetime.now()

    # validate the received values
    if _name and _code and _description and _image and _date and request.method == 'PUT':
        # Update Currency details in relevant Currency
        res = mongo.db.currency.update_one(
            {'_id': ObjectId(_id['$oid']) if '$oid' in _id else ObjectId(_id)},
            {'$set': {'name': _name, 'code': _code, 'description': _description, 'image': _image, 'date': _date}}
        )

        # Send response for data update success
        response = jsonify({
            "code": 200,
            "message": "Success",
            "data": 'Currency Update Successfully!'
        })
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response, 200
    else:
        # Send response for error
        return not_found()


# Currency - Delete Currency details
@app.route('/currency/delete/<cid>', methods=['DELETE'])
def delete_currency(cid):
    # Check the available currency details and remove
    res = mongo.db.currency.delete_one({'_id': ObjectId(cid)})

    # Send response for data creation success
    response = jsonify({
        "code": 200,
        "message": "Success",
        "data": 'Currency Deleted successfully!'
    })
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response, 200


'''
Saved Trained Coin Data - Endpoints

@get_save_coin(coin)
/api/coin/<coin> [GET] - Get Saved Coin data by Coin Name

@get_save_coin_data_by_id(coin, cid)
/api/coin/<coin>/<id> [GET] - Get Saved Coin data by Coin Name and item id

@get_coin_csv(coin)
/api/csv/<coin> [GET] - Get Saved Coin data as CSV file by Coin Name 
'''


# Coin Data - Get Coin data by coin name
@app.route('/api/coin/<coin>')
def get_save_coin(coin):
    # Get Collection Data from database
    collection_name = "data_" + coin.lower()
    collection = db[collection_name]

    # Get all coin data by coin name
    data = collection.find()
    list_data = list(data)

    # Convert data to JSON data and send response
    response = dumps(list_data, indent=2)
    return response, 200


# Coin Data - Get Coin data by coin name and item id
@app.route('/api/coin/<coin>/<cid>')
def get_save_coin_data_by_id(coin=None, cid=None):
    # Get Collection Data from database
    collection_name = "data_" + coin.lower()
    collection = db[collection_name]

    # Find coin data by coin id
    data = collection.find_one({'_id': ObjectId(cid)})

    # Convert data to JSON data and send response
    response = dumps(data, indent=2)
    return response, 200


# Coin Data - Get Coin data as CSV file by coin name
@app.route('/api/csv/<coin>')
def get_coin_csv(coin):
    # Get Collection Data from database
    collection_name = "data_" + coin.lower()
    collection = db[collection_name]

    # Get all coin data by coin name
    data = collection.find()
    list_data = list(data)

    # Getting current data time
    # file_date_time = datetime.now()
    # _updated_file_date_time = file_date_time.strftime("%Y_%m_%d_%H_%M_%S")

    # File name and Path
    # file_name = f'{coin.lower()}_{_updated_file_date_time}.csv'
    file_name_path = f'{COIN_DIR}{coin.lower()}.csv'

    # Get response data from JSON
    capture_data = []
    table_headers = ['date_time', 'currency',
                     'Today Price', 'Forecasted Tomorrow Price', 'Price Score',
                     'Today Volume', 'Forecasted Tomorrow Volume', 'Volume Score',
                     'Today Market Cap', 'Forecasted Tomorrow Market Cap', 'Market Cap Score',
                     'Sentiment', 'Sentiment Score']

    # Put data into Array
    for x in list_data:
        price_score = round(x['price']['score'], 2)
        volume_score = round(x['volume']['score'], 2)
        market_cap_score = round(x['market_cap']['score'], 2)

        try:
            sentiment_data = x['sentiment']
            sentiment_data_score = x['sentiment_score']
        except:
            sentiment_data = None
            sentiment_data_score = None

        listing = [x['date_time'], x['currency'],
                   x['price']['today'], x['price']['tomorrow'], str(price_score) + '%',
                   x['volume']['today'], x['volume']['tomorrow'], str(volume_score) + '%',
                   x['market_cap']['today'], x['market_cap']['tomorrow'], str(market_cap_score) + '%',
                   sentiment_data, sentiment_data_score]
        capture_data.append(listing)

    # Write new data in CSV files
    with open(file_name_path, 'w', encoding='UTF8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(table_headers)
        writer.writerows(capture_data)

    # Send File response
    return send_file(
        file_name_path,
        mimetype='text/csv',
        download_name='coin.csv',
        as_attachment=True
    )


# Endpoint Error Response
@app.errorhandler(404)
def not_found(error=None):
    # Send response for Endpoint error
    response = jsonify({
        "code": 404,
        "message": "Unsuccessful",
        "url": 'Not Found: ' + request.url
    })
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response, 404


if __name__ == "__main__":
    app.run()
