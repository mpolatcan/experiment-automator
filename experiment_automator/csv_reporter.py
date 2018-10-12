from experiment_automator.constants import ExperimentConstants, CSVReporterConstants
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
        self.column_names = None
        self.header_written = False
        self.experiment_config = experiment_config
        self.csv_config = csv_config

    def __class_name(self):
        return self.__class__.__name__

    def __initialize_csv_report(self):
        DebugLogCat.log(self.debug, self.__class_name(), "Creating working directory for reporting results!")

        work_dir = self.experiment_config.get(ExperimentConstants.KEY_EXPERIMENT_WORKDIR, None)
        experiment_name = self.experiment_config.get(ExperimentConstants.KEY_EXPERIMENT_NAME, None)

        if experiment_name is None:
            raise ConfigNotFoundException("%s - Experiment name not found in config!" % self.__class_name())

        if not exists(work_dir):
            raise WorkingDirectoryDoesNotExistException("%s - Working directory \"%s\" does not exist! Set appropriate working directory!" % (self.__class_name(), work_dir))

        report_dir_path = experiment_name + "/"

        if not (work_dir is None):
            report_dir_path = work_dir + experiment_name + "/"

        if not exists(report_dir_path):
            makedirs(report_dir_path)

        self.report_dir = report_dir_path

        DebugLogCat.log(self.debug, self.__class_name(), "Working directory \"%s\" is created!" % self.report_dir)

        now = datetime.now()
        self.report_filename = "%s%s-%s_%s.csv" % (self.report_dir, experiment_name, now.date(), now.time().strftime("%H:%M:%S"))

        DebugLogCat.log(self.debug, self.__class_name(), "Report file for experiment \"%s\" is created!" % self.report_filename)

    def __write_values_with_separator(self, report_file, values, separator, fn):
        index = 0

        for column_name in self.column_names:
            fn(report_file, column_name, values)

            if index < len(self.column_names) - 1:
                report_file.write(separator)

            index += 1

        report_file.write("\n")

    def __write_to_csv(self, message, columns=None, separator=","):
        with open(self.report_filename, "a+") as report_file:
            if columns is not None:
                message = {key: message[key] for key in message.keys() if key in columns}

            DebugLogCat.log(self.debug, self.__class_name(), "Writing message \"%s\" to file \"%s\"" % (str(message), self.report_filename))

            # If header is not written, write header
            if not self.header_written:
                self.column_names = message.keys()
                self.__write_values_with_separator(report_file,
                                                   None,
                                                   separator,
                                                   fn=lambda file, column_name, values: report_file.write(str(column_name)))
                self.header_written = True

            self.__write_values_with_separator(report_file,
                                               message,
                                               separator,
                                               fn=lambda file, column_name, values: report_file.write(str(values.get(column_name,"-"))))

    def save_results_to_csv(self, results):
        csv_log_status = self.csv_config.get(CSVReporterConstants.KEY_CSV_STATUS, None)

        if not (self.csv_config is None) and (csv_log_status == CSVReporterConstants.VALUE_CSV_ENABLED):
            DebugLogCat.log(self.debug, self.__class_name(), "CSV is configured properly. Logging results...!")

            if self.report_dir is None:
                self.__initialize_csv_report()

            csv_format_config = self.csv_config.get(CSVReporterConstants.KEY_CSV_FORMAT, None)

            if not (csv_format_config is None):
                DebugLogCat.log(self.debug, self.__class_name(), "Founded csv format defined by user!")

                self.__write_to_csv(results,
                                    columns=csv_format_config.get(CSVReporterConstants.KEY_CSV_FORMAT_COLUMNS),
                                    separator=csv_format_config.get(CSVReporterConstants.KEY_CSV_FORMAT_SEPARATOR))
            else:
                DebugLogCat.log(self.debug, self.__class_name(), "There is no csv format defined by user. Writing with default csv format!")
                self.__write_to_csv(results)
        else:
            DebugLogCat.log(self.debug, self.__class_name(), "CSV is not configured so CSV logging is disabled!")
