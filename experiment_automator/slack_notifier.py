from experiment_automator.constants import Constants
from experiment_automator.utils import DebugLogCat
from copy import deepcopy
from time import time
from requests import post


class SlackNotifier:
    def __init__(self, debug, slack_config):
        self.debug = debug
        self.slack_config = slack_config

    def __generate_notification_data(self, status):
        notification_data = {}
        notification_format = self.slack_config.get(Constants.KEY_SLACK_NOTIFICATION_FORMAT, None)

        if not (notification_format is None) and (notification_format != Constants.VALUE_SLACK_NOTIFICATION_FORMAT):
            if notification_format.get(status, None) is not None:
                notification_custom_formatted = deepcopy(notification_format.get(status, None))

                DebugLogCat.log(self.debug, "Founded notification format is defined by user for status \"%s\"!" % status)

                footer_timestamp_add = notification_custom_formatted.get(Constants.KEY_SLACK_NOTIFICATION_TS, None)

                if not (footer_timestamp_add is None) and footer_timestamp_add is True:
                    notification_custom_formatted[Constants.KEY_SLACK_NOTIFICATION_TS] = time()
                else:
                    notification_custom_formatted.pop(Constants.KEY_SLACK_NOTIFICATION_TS, None)

                notification_data[Constants.KEY_SLACK_ATTACHMENTS] = [notification_custom_formatted]
            else:
                DebugLogCat.log(self.debug, "There is no notification format defined by user for status \"%s\".Getting default notification" % status)
                notification_data[Constants.KEY_SLACK_ATTACHMENTS] = [Constants.DEFAULT_NOTIFICATIONS.get(status)]
        else:
            DebugLogCat.log(self.debug, "There is no notification format defined by user. Getting default notification format!")
            notification_data[Constants.KEY_SLACK_ATTACHMENTS] = [Constants.DEFAULT_NOTIFICATIONS.get(status)]

        DebugLogCat.log(self.debug, "Generated notification is \"%s\"" % str(notification_data))

        return notification_data

    def notify(self, status):
        if not (self.slack_config is None) and not (self.slack_config.get(Constants.KEY_SLACK_WEBHOOK_URL) is None):
            DebugLogCat.log(self.debug, "Slack configured properly. We send notification to Slack channel!")

            post(str(self.slack_config.get(Constants.KEY_SLACK_WEBHOOK_URL)), json=self.__generate_notification_data(status))
        else:
            DebugLogCat.log(self.debug, "There is no configuration for Slack. So we can't send notification to Slack channel!")
