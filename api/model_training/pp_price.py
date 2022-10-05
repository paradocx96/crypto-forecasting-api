import pandas as pd
from sklearn.preprocessing import StandardScaler

from model_training.helper import model_training


def pp_price(file_path):
    df = pd.read_csv(file_path, delimiter=',', parse_dates=True, squeeze=True)
    df.drop(['total_volume', 'market_cap'], axis=1, inplace=True)
    df['price'] = df['price'].fillna(0)
    df['snapped_at'] = df['snapped_at'].apply(lambda x: x.split(' ')[0].strip())
    df['snapped_at'] = pd.to_datetime(df['snapped_at'], infer_datetime_format=True)
    scaler = StandardScaler()
    df[['price']] = scaler.fit_transform(df[['price']])
    training_data = df['price'].values
    return model_training(training_data, scaler)
