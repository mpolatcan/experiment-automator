import matplotlib

matplotlib.use('Agg')

from typing import Any, AnyStr
from matplotlib.figure import Figure
from datetime import datetime
from matplotlib.pyplot import title
from experiment_automator.constants import ExperimentConstants, SlackConstants
from textwrap import wrap


class ResultContainer(dict):
    def __init__(self, attrs):
        super().__init__({
            ExperimentConstants.KEY_EXPERIMENT_RESULTS: {},
            SlackConstants.KEY_SLACK_PAYLOAD: {
                ExperimentConstants.KEY_EXPERIMENT_RESULTS: {},
            }
        })
        self.attrs = attrs

    def add_model_result(self, result_label: AnyStr, value: Any):
        self.get_experiment_results_payload().update({result_label: value})
        self.get_slack_payload().get(ExperimentConstants.KEY_EXPERIMENT_RESULTS).update({result_label: value})

    def __save_figure(self, image_label: AnyStr, figure: Figure):
        path = "%s-%s.png" % (image_label, datetime.now().strftime("%H:%M:%S"))
        title("\n".join(wrap("%s" % list(self.attrs.values()))))
        figure.savefig(path)
        figure.clear()

        return path

    def __add_slack_attachment_image(self, image_label, image_path):
        if self.get_slack_payload().get(SlackConstants.KEY_SLACK_IMAGE_ATTACHMENTS, None) is None:
            self.get_slack_payload()[SlackConstants.KEY_SLACK_IMAGE_ATTACHMENTS] = []

        self.get_slack_payload()[SlackConstants.KEY_SLACK_IMAGE_ATTACHMENTS].append((image_label, image_path))

    def __add_to_storage(self, path: AnyStr):
        # TODO Drive result will be added when Drive integration completed
        pass

    def add_figure(self, image_label: AnyStr, figure: Figure):
        path = self.__save_figure(image_label, figure)

        # Add figure to Slack as additional attachment
        self.__add_slack_attachment_image(image_label, path)

        # Add figure to storage
        # TODO Adding figure to storage

    def set_slack_main_figure(self, image_label: AnyStr, figure: Figure):
        self.get_slack_payload()[SlackConstants.KEY_SLACK_MAIN_IMAGE] = self.__save_figure(image_label, figure)

    def get_experiment_results_payload(self):
        return self.get(ExperimentConstants.KEY_EXPERIMENT_RESULTS)

    def get_slack_payload(self):
        return self.get(SlackConstants.KEY_SLACK_PAYLOAD)

    def __repr__(self):
        return super().__repr__()
