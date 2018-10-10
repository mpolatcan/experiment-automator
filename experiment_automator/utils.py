from datetime import datetime


class DebugLogCat:
    @staticmethod
    def log(debug, class_name, message):
        if debug:
            print("[%s - %s] -> %s" % (datetime.now().__str__(), class_name, message))
