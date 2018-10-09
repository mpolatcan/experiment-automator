import yaml


class Config:
    def __init__(self, config_filename):
        self.config = yaml.load(open(config_filename))

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
