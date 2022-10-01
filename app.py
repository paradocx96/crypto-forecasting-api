from flask import Flask, jsonify
from flask_cors import CORS
from flask_apscheduler import APScheduler

from model import schedule_model_training, is_training, CURRENCIES

app = Flask(__name__)
cors = CORS(app, resources={r"/crypto-currency/*": {"origins": "*"}})
app.config['CORS_HEADERS'] = 'Content-Type'
scheduler = APScheduler()

schedule_model_training()
'''
    schedule model re-training
'''
scheduler.add_job(id='Scheduled Task', func=schedule_model_training, trigger="interval", seconds=3600)
scheduler.start()


@app.route('/crypto-currency', methods=['GET'])
def index():
    return f"<div align='center'><h2>Crypto Currency Forecasting Sever is Active</h2></div>"


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


if __name__ == "__main__":
    app.run(port=5000)
