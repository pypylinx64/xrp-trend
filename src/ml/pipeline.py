import ml.dataflow as dataflow
import ml.transform as transform
import ml.model as model


# TODO
#   rewrite class and evaluation in self.args
def prediction_week_crypto(
        api_key,
        type_interval,
        ndays,
        size_coef,
        ):
    
    df = dataflow.get_data(
        key=api_key,
        days=ndays,
        interval=type_interval,
        )

    data = dataflow.processing(
        raw_df=df,
        )
    
    data.to_csv('data/raw_months.csv')

    normal_data = transform.logarithmic_scale(
        series=data[dataflow.COL_OUT_PRICE],
        )
    
    data[transform.COL_OUT_NORMAL] = normal_data

    X_train, X_test, y_train, y_test = transform.split_df(data, coef=size_coef)

    adfuller_stats = model.stationarity_test(
        series=data[transform.COL_OUT_NORMAL],
        )

    y_result = model.predict(
        x_train=X_train,
        y_train=y_train,
        x_test=X_test,
        )

    index_prediction_start = X_train.size
    data_slice = dataflow.preparation(
        data=data,
        y_data=y_result,
        index_start=index_prediction_start,
        )
        
    predict_series_denormal = transform.delogarithmic_scale(
        series_norm=data_slice[dataflow.COL_OUT_PREDICT],
        shift_value=data[dataflow.COL_OUT_PRICE].iloc[index_prediction_start-1],
        )
        
    data_slice[transform.COL_OUT_PREDICT_DENORMAL] = predict_series_denormal
    data_drop = data_slice.drop(columns=[dataflow.COL_OUT_PREDICT])
    data_drop = data_drop.drop(columns=[transform.COL_OUT_NORMAL])

    accuracy = model.get_rmse(
        forecast=data_drop[transform.COL_OUT_PREDICT_DENORMAL],
        actual=data_drop[dataflow.COL_OUT_PRICE],
        )
    
    data_drop.to_csv('data/prediction_week.csv')

    return data_drop, accuracy, adfuller_stats


if __name__ == '__main__':
    pass
