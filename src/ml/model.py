import numpy as np
from sklearn.linear_model import LinearRegression
from statsmodels.tsa import stattools


def stationarity_test(
        series,
    ):

    result = stattools.adfuller(series)
    statistic = result[0]
    p_value = result[1]
    critical_1 = result[4]['1%']
    critical_5 = result[4]['5%']
    critical_10 = result[4]['10%']

    adfuller_stats = {
        'statistic': float(statistic), 
        'p_value': float(p_value), 
        'critical_1': float(critical_1), 
        'critical_5': float(critical_5), 
        'critical_10': float(critical_10), 
        }

    return adfuller_stats

def get_rmse(
        forecast,
        actual,
    ):

    rmse = np.mean((forecast - actual)**2)**.5 
    return float(rmse)

def predict(
        x_train, 
        y_train, 
        x_test,
        ):
    
    reg = LinearRegression().fit(x_train, y_train)
    y_pred = reg.predict(x_test)

    return y_pred


if __name__ == '__main__':
    pass
