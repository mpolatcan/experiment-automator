from experiment_automator.experiment_automator import ExperimentAutomator
from experiment_automator.result_container import ResultContainer
# -------------------------------------------------------------
import pandas as pd
from math import sqrt
from statsmodels.tsa.holtwinters import Holt
from matplotlib.pylab import plot, figure
from sklearn.metrics import mean_squared_error


def pipeline(attrs: dict, results: ResultContainer):
    data = pd.read_csv(attrs["data_path"], header=0, index_col=0, parse_dates=[0])

    cpu_usage_data = data[["cpu_usage"]]

    train_data_percentage = attrs["train_data_percentage"]
    train_data_count = int((len(cpu_usage_data) * train_data_percentage) / 100)

    train_data, test_data = cpu_usage_data[:train_data_count], cpu_usage_data[train_data_count:]

    model = Holt(train_data).fit(smoothing_level=attrs["smoothing_level"], smoothing_slope=attrs["smoothing_slope"], damping_slope=attrs["damping_slope"], optimized=attrs["optimized"])

    predictions = model.predict(start=train_data_count, end=len(cpu_usage_data)-1)

    figure_train = figure(figsize=(10, 6))
    plot(train_data[:200])
    plot(model.fittedvalues[:200])

    figure_predictions = figure(figsize=(10, 6))
    plot(predictions[:200])

    figure_result = figure(figsize=(10, 6))
    plot(test_data[:200])
    plot(predictions[:200])

    mse = mean_squared_error(test_data, predictions)
    rmse = sqrt(mse)

    results.add_model_result("mse", mse)
    results.add_model_result("rmse", rmse)

    results.set_slack_main_figure(image_label="final-result", figure=figure_result)
    results.add_figure(image_label="train-plot", figure=figure_train)
    results.add_figure(image_label="predictions-plot", figure=figure_predictions)


if __name__ == "__main__":
    ExperimentAutomator("holt_config.yml").run(pipeline)