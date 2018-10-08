# TODO Sending notifications (success, fail statuses)
# TODO Enable/disable CSV logging for results
# TODO Migrate module from Test PyPi to original PyPi
# TODO Configurable log format
# TODO Send CSV to storage  (Google Drive etc.)
# TODO Create default Slack and CSV format
# TODO Find image upload service and get link of image

import requests
import yaml
from numpy import arange
import itertools


class ExperimentAutomator:
    def __init__(self, filename):
        self.config = yaml.load(open(filename))
        self.experiment_attrs = []
        self.__prepare_experiment_params()
        self.__gen_experiment_param_combinations()

    def __prepare_experiment_params(self):
        experiment_params = self.get_dict("experiment").get("params")

        for (experiment_param_name, experiment_param_val) in experiment_params.items():
            # If parameter types includes range specification, generate from that range specification
            if isinstance(experiment_param_val, dict) and experiment_param_val.get("range", None) is not None:
                range_spec = experiment_param_val.get("range")

                # Generating values from range specification
                gen_values = []
                for val in arange(range_spec[0], range_spec[1] + range_spec[2], range_spec[2]):
                    gen_values.append(val)

                experiment_params[experiment_param_name] = gen_values

    def __gen_experiment_param_combinations(self):
        experiment_params = self.get_dict("experiment").get("params")
        experiment_param_vals = []

        for (_, experiment_param_val) in experiment_params.items():
            experiment_param_vals.append(experiment_param_val)

        # Generating combinations of experiment attributes
        for experiment_attr_combination in itertools.product(*experiment_param_vals):
            self.experiment_attrs.append(dict(zip(experiment_params.keys(), experiment_attr_combination)))

    def notify_to_slack(self, message):
        print(message)

    def log_to_csv(self):
        pass

    def store_to_drive(self,):
        pass

    def notify(self):
        pass

    def run(self, fn):
        for attrs in self.experiment_attrs:
            fn(self, attrs)

    def get_int(self, key):
        return int(self.config[key])

    def get_float(self, key):
        return float(self.config[key])

    def get_str(self, key):
        return str(self.config[key])

    def get_dict(self, key):
        return dict(self.config[key])

    def get(self, key):
        return self.config[key]
