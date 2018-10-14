from experiment_automator.constants import SlackConstants, OtherConstants, FlickrConstants, ExperimentConstants
from experiment_automator.utils import DebugLogCat
from experiment_automator.image_uploader import FlickrImageUploader
from experiment_automator.exceptions import ImageUploaderException
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

    def __create_slack_attachment(self, attachments, status, pretext=None, title=None, main_image=None, fields=None, footer=SlackConstants.VALUE_SLACK_NOTIFICATION_FOOTER):
        # Default attributes of attachments
        attachment = {
            SlackConstants.KEY_SLACK_NOTIFICATION_COLOR: SlackConstants.VALUE_SLACK_NOTIFICATION_COLORS[status],
            SlackConstants.KEY_SLACK_NOTIFICATION_FOOTER: footer
        }

        # Set pretext of attachment if you want
        if not (pretext is None):
            attachment[SlackConstants.KEY_SLACK_NOTIFICATION_PRETEXT] = SlackConstants.VALUE_SLACK_NOTIFICATION_PRETEXTS[status]

        # Set title of attachment if you want
        if not (title is None):
            attachment[SlackConstants.KEY_SLACK_NOTIFICATION_TITLE] = title

        # Set main image of notification if it is available
        if not (main_image is None):
            image_url = self.image_uploader.upload_image(image_path=main_image, image_type=FlickrConstants.FLICKR_IMAGE_TYPE_ORIGINAL)
            DebugLogCat.log(self.debug, self.__class_name(), "Retrieved url of figure: %s" % image_url)
            attachment[SlackConstants.KEY_SLACK_NOTIFICATION_IMAGE_URL] = image_url

        # Adding notification fields
        if not (fields is None):
            attachment[SlackConstants.KEY_SLACK_FIELDS] = []

            for (title, value) in fields.items():
                if (title in [OtherConstants.KEY_EXEC_STATUS, SlackConstants.KEY_SLACK_MAIN_IMAGE,SlackConstants.KEY_SLACK_IMAGE_ATTACHMENTS]) or \
                   (status == SlackConstants.KEY_SLACK_NOTIFICATION_SUCCESS and title == OtherConstants.KEY_ERROR_CAUSE):
                    continue

                attachment[SlackConstants.KEY_SLACK_FIELDS].append({
                    SlackConstants.KEY_SLACK_FIELD_TITLE: title,
                    SlackConstants.KEY_SLACK_FIELD_VALUE: str(value),
                    SlackConstants.KEY_SLACK_FIELD_SHORT: True
                })

        attachments.append(attachment)

    def __create_slack_image_attachments(self, attachments, status, images):
        if not (images is None) and status == SlackConstants.KEY_SLACK_NOTIFICATION_SUCCESS:
            DebugLogCat.log(self.debug, self.__class_name(), "There is a figures in Slack payload named \"%s\"!" % images)

            for (label, image_path) in images:
                image_url = self.image_uploader.upload_image(image_path=image_path, image_type=FlickrConstants.FLICKR_IMAGE_TYPE_ORIGINAL)

                DebugLogCat.log(self.debug, self.__class_name(), "Retrieved url of figure: %s" % image_url)

                attachments.append({
                    SlackConstants.KEY_SLACK_NOTIFICATION_TITLE: label,
                    SlackConstants.KEY_SLACK_NOTIFICATION_TITLE_LINK: image_url,
                    SlackConstants.KEY_SLACK_NOTIFICATION_THUMB_URL: image_url,
                    SlackConstants.KEY_SLACK_NOTIFICATION_COLOR: SlackConstants.VALUE_SLACK_NOTIFICATION_COLORS[status]
                })
        else:
            DebugLogCat.log(self.debug, self.__class_name(), "There is no figure in Slack payload!")

    def __generate_notification_data(self, status, payload):
        notification_data = {SlackConstants.KEY_SLACK_ATTACHMENTS: []}

        attachments = notification_data.get(SlackConstants.KEY_SLACK_ATTACHMENTS)

        # Create attachment for model results
        self.__create_slack_attachment(attachments=attachments,
                                       status=status,
                                       pretext=SlackConstants.VALUE_SLACK_NOTIFICATION_PRETEXTS[status],
                                       title=SlackConstants.VALUE_SLACK_NOTIFICATION_TITLE_RESULTS,
                                       main_image=payload.get(SlackConstants.KEY_SLACK_MAIN_IMAGE, None),
                                       fields=payload.get(ExperimentConstants.KEY_EXPERIMENT_RESULTS, None))

        # Create attachment for additional figures
        self.__create_slack_image_attachments(attachments=attachments,
                                              status=status,
                                              images=payload.get(SlackConstants.KEY_SLACK_IMAGE_ATTACHMENTS, None))

        # Create attachment for model parameters
        self.__create_slack_attachment(attachments=attachments,
                                       status=status,
                                       title=SlackConstants.VALUE_SLACK_NOTIFICATION_TITLE_PARAMS,
                                       fields=payload.get(ExperimentConstants.KEY_EXPERIMENT_PARAMS, None))

        DebugLogCat.log(self.debug, self.__class_name(), "Generated notification is \"%s\"" % str(notification_data))

        return notification_data

    def notify(self, status, payload):
        if not (self.slack_config is None) and not (self.slack_config.get(SlackConstants.KEY_SLACK_WEBHOOK_URL) is None):
            DebugLogCat.log(self.debug, self.__class_name(), "Slack configured properly. We send notification to Slack channel!")

            post(str(self.slack_config.get(SlackConstants.KEY_SLACK_WEBHOOK_URL)), json=self.__generate_notification_data(status, payload))
        else:
            DebugLogCat.log(self.debug, self.__class_name(), "There is no configuration for Slack. So we can't send notification to Slack channel!")
