from typing import Any, AnyStr
from experiment_automator.constants import ExperimentConstants, SlackConstants


class ResultContainer(dict):
    def __init__(self):
        super().__init__({ExperimentConstants.KEY_EXPERIMENT_RESULTS: {}, SlackConstants.KEY_SLACK_PAYLOAD: {}})

    def add_model_result(self, result_label: AnyStr, value: Any):
        self.get(ExperimentConstants.KEY_EXPERIMENT_RESULTS).update({result_label: value})
        self.get(SlackConstants.KEY_SLACK_PAYLOAD).update({result_label: value})

    def add_to_storage(self, path: AnyStr):
        # TODO Drive result will be added when Drive integration completed
        pass

    def set_slack_attachment_image(self, path: AnyStr):
        self.get(SlackConstants.KEY_SLACK_PAYLOAD).update({SlackConstants.KEY_SLACK_NOTIFICATION_IMAGE_PATH: path})

    def get_model_results_payload(self):
        return self.get(ExperimentConstants.KEY_EXPERIMENT_RESULTS)

    def get_slack_payload(self):
        return self.get(SlackConstants.KEY_SLACK_PAYLOAD)

    def __repr__(self):
        return super().__repr__()