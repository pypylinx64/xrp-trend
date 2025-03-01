import time
import pandas as pd
import ml.pipeline as pipeline
import ml.dataflow as dataflow


def get_datasets():
    pass

def search_best_param(
        api_key,
        max_days,
        max_coef,
        ):
        
    days_lst = [i for i in range(1, max_days+1)]
    coef_lst = [i/10 for i in range(1, max_coef+1)]
    
    test_params = []

    for days in days_lst:

        for coef in coef_lst:
            data, rmse, adf = pipeline.prediction_week_crypto(
                api_key=api_key,
                ndays=days,
                size_coef=coef,
                )
                
            test_params.append({'days': days, 'coef': coef, 'size_prediction': data.shape[0], 'rmse': rmse})

    df_test_params = pd.DataFrame(test_params)
    return df_test_params


if __name__ == '__main__':
    df = search_best_param(
        api_key='test',
        max_days=5,
        max_coef=4,
        )
    
    df.to_csv('report/search_best_params.csv', index=False)
