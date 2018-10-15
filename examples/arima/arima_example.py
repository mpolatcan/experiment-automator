from experiment_automator.experiment_automator import ExperimentAutomator
from experiment_automator.result_container import ResultContainer
from statsmodels.tsa.arima_model import ARIMA
from sklearn.metrics import mean_squared_error
from matplotlib.pylab import figure
from matplotlib.pyplot import plot
from math import sqrt
import pandas as pd


def pipeline(attrs: dict, results: ResultContainer):
    data = pd.read_csv(attrs["data_path"], header=0, parse_dates=[0], index_col=0)

    cpu_usage_data = data[["cpu_usage"]]

    train_data_percentage = attrs["train_data_percentage"]
    train_data_count = int((len(cpu_usage_data) * train_data_percentage)/100)

    train_data, test_data = cpu_usage_data[:train_data_count], cpu_usage_data[train_data_count:]

    model = ARIMA(train_data, order=(attrs["arima_p_value"], attrs["arima_d_value"], attrs["arima_q_value"]))
    model_fit = model.fit(disp=-1)

    predictions = model_fit.predict(start=train_data_count, end=len(cpu_usage_data)-1)

    # Saving figure
    fig_result = figure(figsize=(10, 6))
    plot(test_data[:100])
    plot(predictions[:100])

    fig_predict = figure(figsize=(10, 6))
    plot(predictions[:100])

    mse = mean_squared_error(test_data, predictions)
    rmse = sqrt(mse)

    # Add your model results
    results.add_model_result("mse", mse)
    results.add_model_result("rmse", rmse)

    # Add your prediction plot to Slack attachment
    results.set_slack_main_figure(image_label="result", figure=fig_result)
    results.add_figure(image_label="only-prediction", figure=fig_predict)


if __name__ == "__main__":
    ExperimentAutomator("arima_config.yml").run(pipeline)
