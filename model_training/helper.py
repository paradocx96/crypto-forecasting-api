import statsmodels.api as sm
import warnings

warnings.filterwarnings('ignore')


def model_training(training_data, scaler):
    history = [x for x in training_data]
    model = sm.tsa.arima.ARIMA(history, order=(5, 1, 0))
    model_fit = model.fit()
    output = model_fit.forecast()
    return scaler.inverse_transform([[history[-1]]])[0][0], scaler.inverse_transform([[output[0]]])[0][0]
