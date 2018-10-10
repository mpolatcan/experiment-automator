from experiment_automator.experiment_automator import ExperimentAutomator
import pandas as pd
from statsmodels.tsa.arima_model import ARIMA
from sklearn.metrics import mean_squared_error
from math import sqrt


def pipeline(attrs):
    print(attrs)

    data = pd.read_csv(attrs["data_path"], header=0, parse_dates=[0], index_col=0)

    cpu_usage_data = data[["cpu_usage"]]

    train_data_percentage = attrs["train_data_percentage"]
    train_data_count = int((len(cpu_usage_data) * train_data_percentage)/100)

    train_data, test_data = cpu_usage_data[:train_data_count], cpu_usage_data[train_data_count:]

    model = ARIMA(train_data, order=(attrs["arima_p_value"], attrs["arima_d_value"], attrs["arima_q_value"]))
    model_fit = model.fit(disp=-1)

    predictions = model_fit.predict(start=train_data_count, end=len(cpu_usage_data)-1)

    mse = mean_squared_error(test_data, predictions)
    rmse = sqrt(mse)

    return {"mse": mse, "rmse": rmse}


if __name__ == "__main__":
    # Write your logic to here !!! :)
    ExperimentAutomator("arima_config.yml").run(pipeline)
