from typing import Any, AnyStr
from experiment_automator.constants import ExperimentConstants, SlackConstants


class ResultContainer(dict):
    def __init__(self):
        super().__init__({
            ExperimentConstants.KEY_EXPERIMENT_RESULTS: {},
            SlackConstants.KEY_SLACK_PAYLOAD: {
                ExperimentConstants.KEY_EXPERIMENT_RESULTS: {},
            }
        })

    def add_model_result(self, result_label: AnyStr, value: Any):
        self.get_model_results_payload().update({result_label: value})
        self.get_slack_payload().get(ExperimentConstants.KEY_EXPERIMENT_RESULTS).update({result_label: value})

    def add_to_storage(self, path: AnyStr):
        # TODO Drive result will be added when Drive integration completed
        pass

    def add_slack_attachment_image(self, image_label: AnyStr, path: AnyStr):
        if self.get_slack_payload().get(SlackConstants.KEY_SLACK_IMAGE_ATTACHMENTS, None) is None:
            self.get_slack_payload()[SlackConstants.KEY_SLACK_IMAGE_ATTACHMENTS] = []

        self.get_slack_payload()[SlackConstants.KEY_SLACK_IMAGE_ATTACHMENTS].append((image_label, path))

    def set_main_slack_attachment_image(self, path: AnyStr):
        self.get_slack_payload()[SlackConstants.KEY_SLACK_MAIN_IMAGE] = path

    def get_model_results_payload(self):
        return self.get(ExperimentConstants.KEY_EXPERIMENT_RESULTS)

    def get_slack_payload(self):
        return self.get(SlackConstants.KEY_SLACK_PAYLOAD)

    def __repr__(self):
        return super().__repr__()
