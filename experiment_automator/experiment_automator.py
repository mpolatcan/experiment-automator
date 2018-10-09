# TODO Migrate module from Test PyPi to original PyPi
# TODO Find image upload service and get link of image
# TODO HTTP Communication
# TODO Add logging mechanism for Automator
# TODO Write warnings for debugging and info user
# TODO Parallel model training

from itertools import product
from numpy import arange

# ---------------------------------------------------------------
from experiment_automator.constants import Constants
from experiment_automator.slack_notifier import SlackNotifier
from experiment_automator.csv_reporter import CSVReporter
from experiment_automator.utils import DebugLogCat
from experiment_automator.config import Config
from experiment_automator.exceptions import *


class ExperimentAutomator:
    def __init__(self, config_filename):
        self.config_filename = config_filename
        self.experiment_params = []

        try:
            self.config = Config(config_filename)
            self.debug = self.config.get(Constants.KEY_DEBUG)
            self.slack_notifier = SlackNotifier(self.debug,
                                                self.config.get_dict(Constants.KEY_SLACK))
            self.csv_logger = CSVReporter(self.debug,
                                          self.config.get_dict(Constants.KEY_EXPERIMENT),
                                          self.config.get_dict(Constants.KEY_CSV))
            self.__prepare_experiment_params()
            self.__gen_experiment_param_combinations()
        except ConfigNotFoundException as ex:
            print(ex)

    def __prepare_experiment_params(self):
        DebugLogCat.log(self.debug, "Preparing experiment parameters for training...!")

        experiment_config = self.config.get_dict(Constants.KEY_EXPERIMENT)

        if experiment_config is None:
            raise ConfigNotFoundException("Experiment configuration not found in config \"%s\"" % self.config_filename)

        experiment_params = experiment_config.get(Constants.KEY_EXPERIMENT_PARAMS, None)

        if experiment_params is None:
            raise ConfigNotFoundException("Experiment parameters configurations not found in config \"%s\"" % self.config_filename)

        for (experiment_param_name, experiment_param_val) in experiment_params.items():
            # If parameter types includes range specification, generate from that range specification
            if isinstance(experiment_param_val, dict) and experiment_param_val.get(Constants.KEY_EXPERIMENT_PARAM_RANGE, None) is not None:
                range_spec = experiment_param_val.get(Constants.KEY_EXPERIMENT_PARAM_RANGE)

                # Generating values from range specification
                gen_values = []
                for val in arange(range_spec[0], range_spec[1] + range_spec[2], range_spec[2]):
                    gen_values.append(val)

                experiment_params[experiment_param_name] = gen_values

    def __gen_experiment_param_combinations(self):
        DebugLogCat.log(self.debug, "Generating experiment parameters combinations for training...!")

        experiment_params = self.config.get_dict(Constants.KEY_EXPERIMENT).get(Constants.KEY_EXPERIMENT_PARAMS)
        experiment_param_vals = []

        for (_, experiment_param_val) in experiment_params.items():
            experiment_param_vals.append(experiment_param_val)

        # Generating combinations of experiment attributes
        for experiment_attr_combination in product(*experiment_param_vals):
            self.experiment_params.append(dict(zip(experiment_params.keys(), experiment_attr_combination)))

    # Driver of the program
    def run(self, fn):
        for attrs in self.experiment_params:
            try:
                # TODO Calculate elapsed time
                results = fn(self, attrs)

                results.update(attrs)

                DebugLogCat.log(self.debug, ("Model training is completed successfully. Sending notification to Slack channel!"))

                # If model training completes successfully send notification to Slack channel, save result to log file
                # and send them to Drive
                self.slack_notifier.notify(Constants.KEY_SLACK_NOTIFICATION_SUCCESS)
                self.csv_logger.save_results_to_csv(results)
            except ConfigNotFoundException as ex:
                print(ex)
                break
            except WorkdirDoesNotExistException as ex:
                print(ex)
                break
            except Exception as ex:
                print(ex)
                DebugLogCat.log(self.debug, ("Model training couldn't completed successfully. Sending notification to Slack channel!"))

                # If model training and evaluation terminates with error status send notification
                self.slack_notifier.notify(Constants.KEY_SLACK_NOTIICATION_FAIL)
