from experiment_automator.constants import Constants
from experiment_automator.exceptions import *
from experiment_automator.utils import DebugLogCat
from os.path import exists
from os import makedirs
from datetime import datetime


class CSVReporter:
    def __init__(self, debug, experiment_config, csv_config):
        self.debug = debug
        self.report_dir = None
        self.report_filename = None
        self.header_written = False
        self.experiment_config = experiment_config
        self.csv_config = csv_config

    def __initialize_csv_report(self):
        DebugLogCat.log(self.debug, "Creating working directory for reporting results!")

        work_dir = self.experiment_config.get(Constants.KEY_EXPERIMENT_WORKDIR, None)
        experiment_name = self.experiment_config.get(Constants.KEY_EXPERIMENT_NAME, None)

        if experiment_name is None:
            raise ConfigNotFoundException("Experiment name not found in config!")

        if not exists(work_dir):
            raise WorkdirDoesNotExistException("Working directory \"%s\" does not exist! Set appropriate working directory!" % work_dir)

        report_dir_path = experiment_name + "/"

        if not (work_dir is None):
            report_dir_path = work_dir + experiment_name + "/"

        if not exists(report_dir_path):
            makedirs(report_dir_path)

        self.report_dir = report_dir_path

        DebugLogCat.log(self.debug, "Working directory \"%s\" is created!" % self.report_dir)

        now = datetime.now()
        self.report_filename = "%s%s-%s_%s.csv" % (self.report_dir, experiment_name, now.date(), now.time().strftime("%H:%M:%S"))

        DebugLogCat.log(self.debug, "Report file for experiment \"%s\" is created!" % self.report_filename)

    def __write_values_with_separator(self, report_file, values, separator):
        index = 0

        for value in values:
            report_file.write(str(value))

            if index < len(values) - 1:
                report_file.write(separator)

            index += 1

        report_file.write("\n")

    def __write_to_csv(self, message, columns=None, separator=","):
        with open(self.report_filename, "a+") as report_file:
            if columns is not None:
                message = {key: message[key] for key in columns}

            DebugLogCat.log(self.debug, "Writing message \"%s\" to file \"%s\"" % (str(message), self.report_filename))

            # If header is not written, write header
            if not self.header_written:
                self.__write_values_with_separator(report_file, message.keys(), separator)
                self.header_written = True

            self.__write_values_with_separator(report_file, message.values(), separator)

    def save_results_to_csv(self, results):
        csv_log_status = self.csv_config.get(Constants.KEY_CSV_STATUS, None)

        if not (self.csv_config is None) and (csv_log_status == Constants.VALUE_CSV_ENABLED):
            DebugLogCat.log(self.debug, "CSV is configured properly. Logging results...!")

            if self.report_dir is None:
                self.__initialize_csv_report()

            csv_format_config = self.csv_config.get(Constants.KEY_CSV_FORMAT, None)

            if not (csv_format_config is None):
                DebugLogCat.log(self.debug, "Founded csv format defined by user!")

                self.__write_to_csv(results,
                                    columns=csv_format_config.get(Constants.KEY_CSV_FORMAT_COLUMNS),
                                    separator=csv_format_config.get(Constants.KEY_CSV_FORMAT_SEPARATOR))
            else:
                DebugLogCat.log(self.debug, "There is no csv format defined by user. Writing with default csv format!")
                self.__write_to_csv(results)
        else:
            DebugLogCat.log(self.debug, "CSV is not configured so CSV logging is disabled!")
