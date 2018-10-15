# TODO Write warnings for debugging and info user
# TODO Parallel model training
# TODO Distributed task queue (Celery) integration for async tasks

# ---------------------- Next features ----------------------
# TODO Different notification channels
# TODO HTTP Communication
# TODO Web based dashboard (Plotly visualization)


from itertools import product
from numpy import arange
from datetime import datetime
from typing import Callable
from time import time, gmtime, strftime
import traceback

# ---------------------------------------------------------------
from experiment_automator.constants import ExperimentConstants, SlackConstants, CSVReporterConstants, OtherConstants, MongoDBConstants
from experiment_automator.slack_notifier import SlackNotifier
from experiment_automator.csv_reporter import CSVReporter
from experiment_automator.db_storage import DBStorage
from experiment_automator.utils import DebugLogCat
from experiment_automator.config import Config
from experiment_automator.result_container import ResultContainer
from experiment_automator.exceptions import *


class ExperimentAutomator:
    def __init__(self, config_filename):
        self.config_filename = config_filename
        self.experiment_params = []

        try:
            self.config = Config(config_filename)
            self.debug = self.config.get(OtherConstants.KEY_DEBUG)
            self.debug_traceback = self.config.get(OtherConstants.KEY_DEBUG_TRACEBACK)
            self.slack_notifier = SlackNotifier(self.debug,
                                                self.config.get_dict(SlackConstants.KEY_SLACK))
            self.csv_logger = CSVReporter(self.debug,
                                          self.config.get_dict(ExperimentConstants.KEY_EXPERIMENT),
                                          self.config.get_dict(CSVReporterConstants.KEY_CSV))
            self.db_storage = DBStorage(self.debug,
                                        self.config.get_dict(ExperimentConstants.KEY_EXPERIMENT).get(ExperimentConstants.KEY_EXPERIMENT_NAME),
                                        self.config.get_dict(MongoDBConstants.KEY_MONGODB))
            self.__prepare_experiment_params()
            self.__gen_experiment_param_combinations()
        except ConfigNotFoundException as ex:
            print(ex)
            self.__print_stacktrace()
        except ImageUploaderException as ex:
            print(ex)
            self.__print_stacktrace()

    def __print_stacktrace(self):
        if self.debug_traceback:
            traceback.print_exc()

    def __class_name(self):
        return self.__class__.__name__
    
    def __prepare_experiment_params(self):
        DebugLogCat.log(self.debug, self.__class_name(), "Preparing experiment parameters for training...!")

        experiment_config = self.config.get_dict(ExperimentConstants.KEY_EXPERIMENT)

        if experiment_config is None:
            raise ConfigNotFoundException("%s - Experiment configuration not found in config \"%s\"" % (self.__class_name(), self.config_filename))

        experiment_params = experiment_config.get(ExperimentConstants.KEY_EXPERIMENT_PARAMS, None)

        if experiment_params is None:
            raise ConfigNotFoundException("%s - Experiment parameters configurations not found in config \"%s\"" % (self.__class_name(), self.config_filename))

        for (experiment_param_name, experiment_param_val) in experiment_params.items():
            # If parameter types includes range specification, generate from that range specification
            if isinstance(experiment_param_val, dict) and experiment_param_val.get(ExperimentConstants.KEY_EXPERIMENT_PARAM_RANGE, None) is not None:
                range_spec = experiment_param_val.get(ExperimentConstants.KEY_EXPERIMENT_PARAM_RANGE)

                # Generating values from range specification
                gen_values = []
                for val in arange(range_spec[0], range_spec[1] + range_spec[2], range_spec[2]):
                    gen_values.append(val.item())

                experiment_params[experiment_param_name] = gen_values

    def __gen_experiment_param_combinations(self):
        DebugLogCat.log(self.debug, self.__class_name(), "Generating experiment parameters combinations for training...!")

        experiment_params = self.config.get_dict(ExperimentConstants.KEY_EXPERIMENT).get(ExperimentConstants.KEY_EXPERIMENT_PARAMS)
        experiment_param_vals = []

        for (_, experiment_param_val) in experiment_params.items():
            experiment_param_vals.append(experiment_param_val)

        # Generating combinations of experiment attributes
        for experiment_attr_combination in product(*experiment_param_vals):
            self.experiment_params.append(dict(zip(experiment_params.keys(), experiment_attr_combination)))

    # Driver of the program
    def run(self, fn: Callable[[dict, ResultContainer], None]):
        for attrs in self.experiment_params:
            try:
                start = time()
                start_time = datetime.now().strftime("%m/%d/%y %H:%M:%S")

                results = ResultContainer(attrs)

                # Execute ML pipeline given by user
                fn(attrs, results)

                end = time()

                completion_time = datetime.now().strftime("%m/%d/%y %H:%M:%S")
                elapsed_time = strftime("%H:%M:%S", gmtime(end - start))

                common_data = {
                    OtherConstants.KEY_START_TIME: start_time,
                    OtherConstants.KEY_COMPLETION_TIME: completion_time,
                    OtherConstants.KEY_ELAPSED_TIME: elapsed_time,
                    OtherConstants.KEY_ERROR_CAUSE: "-"
                }

                experiment_results_payload = results.get_experiment_results_payload()
                slack_payload = results.get_slack_payload()

                # Merge parameters with Slack payload
                slack_payload.update({ExperimentConstants.KEY_EXPERIMENT_PARAMS: attrs})
                # Merge other infos with Slack payload
                slack_payload.get(ExperimentConstants.KEY_EXPERIMENT_RESULTS).update(common_data)

                # Merge parameters with experiment results payload
                experiment_results_payload.update(attrs)
                # Merge other infos with experiment results payload
                experiment_results_payload.update(common_data)
                # Additional exec status added to experiment results payload
                experiment_results_payload.update({OtherConstants.KEY_EXEC_STATUS: OtherConstants.EXECUTION_STATUS_SUCCESS})

                DebugLogCat.log(self.debug, self.__class_name(), "Model training is completed successfully. Sending notification to Slack channel!")

                DebugLogCat.log(self.debug, self.__class_name(), "Slack payload: %s" % slack_payload)
                DebugLogCat.log(self.debug, self.__class_name(), "Model results payload: %s" % experiment_results_payload)

                # If model training completes successfully send notification to Slack channel, save result to log file
                # and send them to Drive
                self.slack_notifier.notify(SlackConstants.KEY_SLACK_NOTIFICATION_SUCCESS, slack_payload)
                self.csv_logger.save_results_to_csv(experiment_results_payload)
                self.db_storage.insert_model_results(experiment_results_payload)
            except ConfigNotFoundException as ex:
                print(ex)
                self.__print_stacktrace()
                break
            except WorkingDirectoryDoesNotExistException as ex:
                print(ex)
                self.__print_stacktrace()
                break
            except Exception as ex:
                print(ex)
                self.__print_stacktrace()

                end = time()

                common_data = {
                    OtherConstants.KEY_START_TIME: start_time,
                    OtherConstants.KEY_COMPLETION_TIME: datetime.now().strftime("%m/%d/%y %H:%M:%S"),
                    OtherConstants.KEY_ELAPSED_TIME: strftime("%H:%M:%S", gmtime(end - start)),
                    OtherConstants.KEY_ERROR_CAUSE: "\"%s\"" % str(ex).replace("\n", " ")
                }

                # Merge parameters and other infos with experiment results payload
                experiment_results_payload = {}
                experiment_results_payload.update(attrs)
                experiment_results_payload.update(common_data)
                experiment_results_payload.update({OtherConstants.KEY_EXEC_STATUS: OtherConstants.EXECUTION_STATUS_FAILED})

                # Merge parameters and other infos with Slack payload
                slack_payload = {
                    ExperimentConstants.KEY_EXPERIMENT_PARAMS: attrs,
                    ExperimentConstants.KEY_EXPERIMENT_RESULTS: common_data
                }

                DebugLogCat.log(self.debug, self.__class_name(), "Model training couldn't completed successfully. Sending notification to Slack channel!")

                # If model training and evaluation terminates with error status send notification
                self.slack_notifier.notify(SlackConstants.KEY_SLACK_NOTIFICATION_FAIL, slack_payload)
                self.csv_logger.save_results_to_csv(experiment_results_payload)
                self.db_storage.insert_model_results(experiment_results_payload)
            finally:
                self.experiment_params.pop()
