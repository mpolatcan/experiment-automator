# TODO Slack integration
# TODO Getting parameters and sending notifications
# TODO Enable disable csv logging for results
# TODO Add module to PyPi
# TODO Configurable log format
# TODO Send to storage csv (Google Drive etc.)


class MLNotifier:
    def __init__(self, slack_webhook_url=None, csv_filename=None):
        self.slack_webhook_url = slack_webhook_url
        self.csv_filename = csv_filename

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def __notify_to_slack(self):
        pass

    def __log_to_csv(self):
        if self.csv_filename is not None:
            # TODO logging to experiments to CSV
            pass

    def notify(self):
        if self.slack_webhook_url is not None:
            self.__notify_to_slack()
        else:
            pass
