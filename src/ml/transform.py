import numpy as np
from sklearn.model_selection import train_test_split
import ml.dataflow as dataflow


COL_OUT_NORMAL = 'price_normal'
COL_OUT_DENORMAL = 'price_denormal'
COL_OUT_PREDICT_DENORMAL = 'price_prediction_denormal'


def split_data(
        x,
        coef,
        ):

    train_size = int(x.size * coef)
    train_data, test_data = x[0:train_size], x[train_size:]
    
    train = train_data.iloc[:, 0].reset_index(drop=True)
    test = test_data.iloc[:, 0].reset_index(drop=True)

    return train, test

# TODO
#   rewrite function (top up)
def split_df(df):
    
    X = df[[dataflow.COL_OUT_PRICE]].values
    y = df[COL_OUT_NORMAL].values
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.15, shuffle=False)

    return X_train, X_test, y_train, y_test


def logarithmic_scale(
        series,
        shift_number=None,
        ):
    
    series_log = np.log(series)
    series_na = series_log - series_log.shift()
    series_norm = series_na.fillna(0)

    return series_norm

def delogarithmic_scale(
        series_norm,
        shift_value,
        ):
        
    series_exp = series_norm.cumsum() + np.log(shift_value)
    series_na = np.exp(series_exp)
    series_denorm = series_na.dropna()

    return series_denorm


if __name__ == '__main__':
    pass
