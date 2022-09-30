import pandas as pd
from sklearn.preprocessing import StandardScaler

from model_training.helper import model_training


def pp_market_cap(file_path):
    df = pd.read_csv(file_path, delimiter=',', parse_dates=True, squeeze=True)
    df.drop(['total_volume', 'price'], axis=1, inplace=True)
    df['market_cap'] = df['market_cap'].fillna(0)
    df['snapped_at'] = df['snapped_at'].apply(lambda x: x.split(' ')[0].strip())
    df['snapped_at'] = pd.to_datetime(df['snapped_at'], infer_datetime_format=True)
    scaler = StandardScaler()
    df[['market_cap']] = scaler.fit_transform(df[['market_cap']])
    training_data = df['market_cap'].values
    return model_training(training_data, scaler)
