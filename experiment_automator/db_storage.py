from pymongo import MongoClient
from datetime import datetime

# ---------------------------------------------------------------
from experiment_automator.exceptions import ConfigNotFoundException
from experiment_automator.constants import MongoDBConstants
from experiment_automator.utils import DebugLogCat

# TODO Extend DBStorage class capabilities


class DBStorage:
    def __init__(self, debug, experiment_name, dbstorage_config):
        self.debug = debug
        self.experiment_name = experiment_name
        self.dbstorage_config = dbstorage_config

        if self.experiment_name is None:
            raise ConfigNotFoundException("%s - Experiment name not defined in config!" % (self.__class_name()))

        if self.dbstorage_config.get(MongoDBConstants.KEY_MONGODB_HOST, None) is None:
            raise ConfigNotFoundException("%s - MongoDB hostname is not defined in config!" % (self.__class_name()))

        if self.dbstorage_config.get(MongoDBConstants.KEY_MONGODB_PORT, None) is None:
            raise ConfigNotFoundException("%s - MongoDB port is not defined in config!" % (self.__class_name()))

        # Connect to MongoDB
        self.client = MongoClient("mongodb://%s:%s@%s:%s" % (self.dbstorage_config.get(MongoDBConstants.KEY_MONGODB_USERNAME),
                                                             self.dbstorage_config.get(MongoDBConstants.KEY_MONGODB_PASSWORD),
                                                             self.dbstorage_config.get(MongoDBConstants.KEY_MONGODB_HOST),
                                                             self.dbstorage_config.get(MongoDBConstants.KEY_MONGODB_PORT)))

        DebugLogCat.log(self.debug, self.__class_name(), "Connection established with MongoDB!")

        # If not exist create db named with experiment name
        self.db = self.client[self.experiment_name]

        DebugLogCat.log(self.debug, self.__class_name(), "Database created with name %s on MongoDB" % self.experiment_name)

        collection_name = "%s-%s" % (self.experiment_name, datetime.now().strftime("%m/%d/%y %H:%M:%S"))

        # Creating collection on opened database
        self.experiment_results_collection = self.db[collection_name]

        DebugLogCat.log(self.debug, self.__class_name(), "Collection created with name %s on MongoDB" % collection_name)

    def __class_name(self):
        return self.__class__.__name__

    def insert_model_results(self, experiment_result_payload):
        DebugLogCat.log(self.debug, self.__class_name(), "Experiment result payload inserted with id %s!" % self.experiment_results_collection.insert_one(dict(experiment_result_payload)).inserted_id)



