import pandas as pd
from sklearn.preprocessing import StandardScaler

from model_training.helper import model_training


def pp_volume(file_path):
    df = pd.read_csv(file_path, delimiter=',', parse_dates=True, squeeze=True)
    df.drop(['price', 'market_cap'], axis=1, inplace=True)
    df['total_volume'] = df['total_volume'].fillna(0)
    df['snapped_at'] = df['snapped_at'].apply(lambda x: x.split(' ')[0].strip())
    df['snapped_at'] = pd.to_datetime(df['snapped_at'], infer_datetime_format=True)
    scaler = StandardScaler()
    df[['total_volume']] = scaler.fit_transform(df[['total_volume']])
    training_data = df['total_volume'].values
    return model_training(training_data, scaler)
