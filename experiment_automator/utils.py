from experiment_automator.constants import Constants
from datetime import datetime


class DebugLogCat:
    @staticmethod
    def log(debug, message):
        if debug:
            print("[%s] -> %s" % (datetime.now().__str__(), message))
