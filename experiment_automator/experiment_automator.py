# TODO Sending notifications (success, fail statuses)
# TODO Migrate module from Test PyPi to original PyPi
# TODO Configurable log format
# TODO Create default Slack and CSV format
# TODO Find image upload service and get link of image
# TODO HTTP Communication
# TODO Add logging mechanism for Automator
# TODO Write warnings for debugging and info user

import requests
import yaml
import time
from datetime import datetime
from itertools import product
from numpy import arange
from copy import deepcopy


class ExperimentAutomator:
    def __init__(self, filename):
        try:
            self.config_filename = filename
            self.config = yaml.load(open(filename))
            self.experiment_params = []
            self.__prepare_experiment_params()
            self.__gen_experiment_param_combinations()
        except self.__ConfigNotFoundException as ex:
            print(ex)

    def __prepare_experiment_params(self):
        experiment_config = self.get_dict(self.__Constants.KEY_EXPERIMENT)

        if experiment_config is None:
            raise self.__ConfigNotFoundException("Experiment configuration not found in config \"%s\"" % self.config_filename)

        experiment_params = experiment_config.get(self.__Constants.KEY_EXPERIMENT_PARAMS, None)

        if experiment_params is None:
            raise self.__ConfigNotFoundException("Experiment parameters configurations not found in config \"%s\"" % self.config_filename)

        for (experiment_param_name, experiment_param_val) in experiment_params.items():
            # If parameter types includes range specification, generate from that range specification
            if isinstance(experiment_param_val, dict) and experiment_param_val.get(self.__Constants.KEY_EXPERIMENT_PARAM_RANGE, None) is not None:
                range_spec = experiment_param_val.get(self.__Constants.KEY_EXPERIMENT_PARAM_RANGE)

                # Generating values from range specification
                gen_values = []
                for val in arange(range_spec[0], range_spec[1] + range_spec[2], range_spec[2]):
                    gen_values.append(val)

                experiment_params[experiment_param_name] = gen_values

    def __gen_experiment_param_combinations(self):
        experiment_params = self.get_dict(self.__Constants.KEY_EXPERIMENT).get(self.__Constants.KEY_EXPERIMENT_PARAMS)
        experiment_param_vals = []

        for (_, experiment_param_val) in experiment_params.items():
            experiment_param_vals.append(experiment_param_val)

        # Generating combinations of experiment attributes
        for experiment_attr_combination in product(*experiment_param_vals):
            self.experiment_params.append(dict(zip(experiment_params.keys(), experiment_attr_combination)))

    def __debug_logcat(self, message):
        if self.get(self.__Constants.KEY_DEBUG):
            print("[%s] -> %s" % (datetime.now().__str__(), message))

    def __generate_notification_data(self, status, slack_config):
        notification_data = {}
        notification_format = slack_config.get(self.__Constants.KEY_SLACK_NOTIFICATION_FORMAT, None)

        if not (notification_format is None) and (notification_format != self.__Constants.VALUE_SLACK_NOTIFICATION_FORMAT):
            if notification_format.get(status, None) is not None:
                notification_custom_formatted = deepcopy(notification_format.get(status, None))

                self.__debug_logcat("Founded notification format is defined by user for status \"%s\"!" % status)

                footer_timestamp_add = notification_custom_formatted.get(self.__Constants.KEY_SLACK_NOTIFICATION_TS, None)

                if not (footer_timestamp_add is None) and footer_timestamp_add is True:
                    notification_custom_formatted[self.__Constants.KEY_SLACK_NOTIFICATION_TS] = time.time()
                else:
                    notification_custom_formatted.pop(self.__Constants.KEY_SLACK_NOTIFICATION_TS, None)

                notification_data[self.__Constants.KEY_SLACK_ATTACHMENTS] = [notification_custom_formatted]
            else:
                self.__debug_logcat("There is no notification format defined by user for status \"%s\".Getting default notification" % status)
                notification_data[self.__Constants.KEY_SLACK_ATTACHMENTS] = [self.__Constants.DEFAULT_NOTIFICATIONS.get(status)]
        else:
            self.__debug_logcat("There is no notification format defined by user. Getting default notification format!")
            notification_data[self.__Constants.KEY_SLACK_ATTACHMENTS] = [self.__Constants.DEFAULT_NOTIFICATIONS.get(status)]

        self.__debug_logcat("Generated notification is \"%s\"" % str(notification_data))

        return notification_data

    def notify_to_slack(self, status):
        slack_config = self.get_dict(self.__Constants.KEY_SLACK)

        if not (slack_config is None) and not (slack_config.get(self.__Constants.KEY_SLACK_WEBHOOK_URL) is None):
            self.__debug_logcat("Slack configured properly. We send notification to Slack channel!")

            requests.post(str(slack_config.get(self.__Constants.KEY_SLACK_WEBHOOK_URL)),json=self.__generate_notification_data(status, slack_config))
        else:
            self.__debug_logcat("There is no configuration for Slack. So we can't send notification to Slack channel!")

    def log_to_csv(self):
        # TODO Enable/disable CSV logging for results
        pass

    def store_to_drive(self):
        # TODO Send CSV and figures to storage  (Google Drive etc.)
        pass

    # Driver of the program
    def run(self, fn):
        for attrs in self.experiment_params:
            try:
                # TODO Calculate elapsed time
                return_vals = fn(self, attrs)

                self.__debug_logcat("Model training is completed successfully. Sending notification to Slack channel!")

                # If model training completes successfully send notification
                self.notify_to_slack(self.__Constants.KEY_SLACK_NOTIFICATION_SUCCESS)
            except Exception:
                self.__debug_logcat("Model training couldn't completed successfully. Sending notification to Slack channel!")

                # If model training and evaluation terminates with error status send notification
                self.notify_to_slack(self.__Constants.KEY_SLACK_NOTIICATION_FAIL)

    def get_int(self, key):
        val = self.get(key)

        if not (val is None):
            return int(val)

        return val

    def get_float(self, key):
        val = self.get(key)

        if not (val is None):
            return float(val)

        return val

    def get_str(self, key):
        val = self.get(key)

        if not (val is None):
            return str(val)

        return val

    def get_dict(self, key):
        val = self.get(key)

        if not (val is None):
            return dict(val)

        return val

    def get(self, key):
        return self.config.get(key, None)

    class __Constants:
        # -------------------- Default Notifications ----------------
        DEFAULT_NOTIFICATIONS = {
            "success": {
                "pretext": "",
                "title": "",
                "text": "",
                "thumb_url": "",
                "color": "",
                "footer": "",
                "time": time.time()
            },
            "fail": {
                "pretext": "",
                "title": "",
                "text": "",
                "thumb_url": "",
                "color": "",
                "footer": "",
                "time": time.time()
            }
        }

        # ------------------------- Experiment Constants ----------------
        KEY_EXPERIMENT = "experiment"
        KEY_EXPERIMENT_NAME = "name"
        KEY_EXPERIMENT_PARAMS = "params"
        KEY_EXPERIMENT_PARAM_RANGE = "range"
        # ------------------------- Slack Constants --------------------
        KEY_SLACK = "slack"
        KEY_SLACK_NOTIFICATION_FORMAT = "notification_format"
        KEY_SLACK_WEBHOOK_URL = "webhook_url"
        KEY_SLACK_NOTIFICATION_SUCCESS = "success"
        KEY_SLACK_NOTIICATION_FAIL = "fail"
        KEY_SLACK_NOTIFICATION_PRETEXT = "pretext"
        KEY_SLACK_NOTIFICATION_TITLE = "title"
        KEY_SLACK_NOTIFICATION_THUMB_URL = "thumb_url"
        KEY_SLACK_NOTIFICATION_IMAGE = "image"
        KEY_SLACK_NOTIFICATION_COLOR = "color"
        KEY_SLACK_NOTIFICATION_FOOTER = "footer"
        KEY_SLACK_NOTIFICATION_TS = "ts"
        KEY_SLACK_ATTACHMENTS = "attachments"
        VALUE_SLACK_NOTIFICATION_FORMAT = "default"
        # ------------------------- CSV Constants ----------------------
        KEY_CSV = "csv"
        KEY_CSV_FILENAME = "filename"
        KEY_CSV_FORMAT = "format"
        # -------------------------- Drive Constants -------------------
        KEY_DRIVE = "drive"
        # --------------------------- Other Constants ------------------
        KEY_DEBUG = "debug"

    class __ConfigNotFoundException(Exception):
        def __init__(self, message):
            super().__init__(message)