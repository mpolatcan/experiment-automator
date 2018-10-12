from experiment_automator.constants import SlackConstants, OtherConstants, FlickrConstants
from experiment_automator.utils import DebugLogCat
from experiment_automator.image_uploader import FlickrImageUploader
from experiment_automator.exceptions import ImageUploaderException
from copy import deepcopy
from time import time
from requests import post


class SlackNotifier:
    def __init__(self, debug, slack_config):
        self.debug = debug
        self.slack_config = slack_config

        if self.slack_config.get(SlackConstants.KEY_SLACK_IMAGE_SERVICE, None) is None:
            raise ImageUploaderException("%s - Image service configuration is None. Please specify image service informations in config!" % self.__class_name())

        self.image_uploader = FlickrImageUploader(self.debug, self.slack_config.get(SlackConstants.KEY_SLACK_IMAGE_SERVICE))

    def __class_name(self):
        return self.__class__.__name__
    
    def __generate_notification_data(self, status, message):
        notification_data = {}
        notification_format = self.slack_config.get(SlackConstants.KEY_SLACK_NOTIFICATION_FORMAT, None)

        if not (notification_format is None) and (notification_format != SlackConstants.VALUE_DEFAULT_SLACK_NOTIFICATION_FORMAT):
            if notification_format.get(status, None) is not None:
                notification_custom_formatted = deepcopy(notification_format.get(status, None))

                DebugLogCat.log(self.debug, self.__class_name(), "Founded notification format is defined by user for status \"%s\"!" % status)

                footer_timestamp_add = notification_custom_formatted.get(SlackConstants.KEY_SLACK_NOTIFICATION_TS, None)

                if not (footer_timestamp_add is None) and footer_timestamp_add is True:
                    notification_custom_formatted[SlackConstants.KEY_SLACK_NOTIFICATION_TS] = time()
                else:
                    notification_custom_formatted.pop(SlackConstants.KEY_SLACK_NOTIFICATION_TS, None)

                if notification_image_link is not None:
                    notification_custom_formatted[SlackConstants.KEY_SLACK_NOTIFICATION_IMAGE_URL] = notification_image_link

                notification_data[SlackConstants.KEY_SLACK_ATTACHMENTS] = [notification_custom_formatted]
            else:
                DebugLogCat.log(self.debug, self.__class_name(), "There is no notification format defined by user for status \"%s\".Getting default notification" % status)

                notification_data[SlackConstants.KEY_SLACK_ATTACHMENTS] = [SlackConstants.DEFAULT_NOTIFICATIONS.get(status)]
        else:
            DebugLogCat.log(self.debug, self.__class_name(), "There is no notification format defined by user. Getting default notification format!")
            notification_data[SlackConstants.KEY_SLACK_ATTACHMENTS] = [SlackConstants.DEFAULT_NOTIFICATIONS.get(status)]

        notification_data[SlackConstants.KEY_SLACK_ATTACHMENTS][0][SlackConstants.KEY_SLACK_FIELDS] = []

        # Adding notification fields
        for (title, value) in message.items():
            if (title in [OtherConstants.KEY_EXEC_STATUS, SlackConstants.KEY_SLACK_NOTIFICATION_IMAGE_PATH]) or \
               (status == SlackConstants.KEY_SLACK_NOTIFICATION_SUCCESS and title == OtherConstants.KEY_ERROR_CAUSE):
                continue

            notification_data[SlackConstants.KEY_SLACK_ATTACHMENTS][0][SlackConstants.KEY_SLACK_FIELDS].append({
                SlackConstants.KEY_SLACK_FIELD_TITLE: title,
                SlackConstants.KEY_SLACK_FIELD_VALUE: str(value),
                SlackConstants.KEY_SLACK_FIELD_SHORT: True
            })

        if SlackConstants.KEY_SLACK_NOTIFICATION_IMAGE_PATH in message.keys() and message[OtherConstants.KEY_EXEC_STATUS] == OtherConstants.EXECUTION_STATUS_SUCCESS:
            DebugLogCat.log(self.debug, self.__class_name(), "There is a figure in Slack payload named \"%s\"!" % message[SlackConstants.KEY_SLACK_NOTIFICATION_IMAGE_PATH])

            image_url = self.image_uploader.upload_image(image_path=message[SlackConstants.KEY_SLACK_NOTIFICATION_IMAGE_PATH], image_type=FlickrConstants.FLICKR_IMAGE_TYPE_ORIGINAL)
            notification_data[SlackConstants.KEY_SLACK_ATTACHMENTS][0][SlackConstants.KEY_SLACK_NOTIFICATION_IMAGE_URL] = image_url

            DebugLogCat.log(self.debug, self.__class_name(), "Retrieved url of figure: %s" % image_url)
        else:
            DebugLogCat.log(self.debug, self.__class_name(), "There is no figure in Slack payload!")

        DebugLogCat.log(self.debug, self.__class_name(), "Generated notification is \"%s\"" % str(notification_data))

        return notification_data

    def notify(self, status, message):
        if not (self.slack_config is None) and not (self.slack_config.get(SlackConstants.KEY_SLACK_WEBHOOK_URL) is None):
            DebugLogCat.log(self.debug, self.__class_name(), "Slack configured properly. We send notification to Slack channel!")

            post(str(self.slack_config.get(SlackConstants.KEY_SLACK_WEBHOOK_URL)), json=self.__generate_notification_data(status, message))
        else:
            DebugLogCat.log(self.debug, self.__class_name(), "There is no configuration for Slack. So we can't send notification to Slack channel!")
