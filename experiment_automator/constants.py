import time


class Constants:
    # -------------------- Default Notifications ----------------
    # TODO Edit default Slack notifications
    DEFAULT_NOTIFICATIONS = {
        "success": {
            "pretext": "",
            "title": "SUCCESS",
            "text": "",
            "thumb_url": "",
            "color": "",
            "footer": "Experiment Automator",
            "time": time.time()
        },
        "fail": {
            "pretext": "",
            "title": "FAIL",
            "text": "",
            "thumb_url": "",
            "color": "",
            "footer": "Experiment Automator",
            "time": time.time()
        }
    }

    # ------------------------- Experiment Constants ----------------
    KEY_EXPERIMENT = "experiment"
    KEY_EXPERIMENT_NAME = "name"
    KEY_EXPERIMENT_PARAMS = "params"
    KEY_EXPERIMENT_PARAM_RANGE = "range"
    KEY_EXPERIMENT_WORKDIR = "workdir"
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
    KEY_CSV_FORMAT = "csv_format"
    KEY_CSV_FORMAT_SEPARATOR = "separator"
    KEY_CSV_FORMAT_COLUMNS = "columns"
    KEY_CSV_STATUS = "status"
    VALUE_CSV_ENABLED = "enabled"
    VALUE_CSV_DISABLED = "disabled"
    # -------------------------- Drive Constants -------------------
    KEY_DRIVE = "drive"
    # --------------------------- Other Constants ------------------
    KEY_DEBUG = "debug"
