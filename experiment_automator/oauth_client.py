from requests_oauthlib import OAuth1Session
from experiment_automator.constants import Constants
from experiment_automator.exceptions import OAuthException
from os.path import exists


class OAuthClient:
    def __init__(self, oauth_config):
        self.oauth_config = oauth_config

        self.__check_config(Constants.KEY_OAUTH_NAME)
        self.__check_config(Constants.KEY_OAUTH_CLIENT_KEY)
        self.__check_config(Constants.KEY_OAUTH_CLIENT_SECRET)
        self.__check_config(Constants.KEY_OAUTH_REQUEST_TOKEN_URL)
        self.__check_config(Constants.KEY_OAUTH_ACCESS_TOKEN_URL)
        self.__check_config(Constants.KEY_OAUTH_AUTHORIZE_URL)
        self.__check_config(Constants.KEY_OAUTH_BASE_URL)
        self.__check_config(Constants.KEY_OAUTH_ACCESS_TOKEN_PATH)

    def __class_name(self):
        return self.__class__.__name__

    def __check_config(self, config):
        if self.oauth_config.get(config, None) is None:
            raise OAuthException("%s - OAuth config %s is None. Please set in config!" % (self.__class_name(), config))

    def connect(self, callback, **params):
        global resource_owner_key
        global resource_owner_secret

        # If persist read oauth tokens from file
        if exists(self.oauth_config.get(Constants.KEY_OAUTH_ACCESS_TOKEN_PATH)):
            with open(self.oauth_config.get(Constants.KEY_OAUTH_ACCESS_TOKEN_PATH), "r") as key_file:
                resource_owner_key = key_file.readline().strip()
                resource_owner_secret = key_file.readline().strip()
        else:
            oauth = OAuth1Session(client_key=self.oauth_config.get(Constants.KEY_OAUTH_CLIENT_KEY),
                                  client_secret=self.oauth_config.get(Constants.KEY_OAUTH_CLIENT_SECRET),
                                  callback_uri=callback)
            tokens = oauth.fetch_request_token(self.oauth_config.get(Constants.KEY_OAUTH_REQUEST_TOKEN_URL))
            resource_owner_key = tokens.get(Constants.KEY_OAUTH_TOKEN)
            resource_owner_secret = tokens.get(Constants.KEY_OAUTH_TOKEN_SECRET)

            authorization_url = oauth.authorization_url(self.oauth_config.get(Constants.KEY_OAUTH_AUTHORIZE_URL), **params)
            print("Visit this URL in your browser for service \"{service_name}\": {url}".format(
                    service_name=self.oauth_config.get(Constants.KEY_OAUTH_NAME),
                    url=authorization_url))
            oauth_verifier = input("Enter PIN from browser: ")

            oauth = OAuth1Session(client_key=self.oauth_config.get(Constants.KEY_OAUTH_CLIENT_KEY),
                                  client_secret=self.oauth_config.get(Constants.KEY_OAUTH_CLIENT_SECRET),
                                  resource_owner_key=resource_owner_key,
                                  resource_owner_secret=resource_owner_secret,
                                  verifier=oauth_verifier)

            oauth_tokens = oauth.fetch_access_token(self.oauth_config.get(Constants.KEY_OAUTH_ACCESS_TOKEN_URL))
            resource_owner_key = oauth_tokens.get(Constants.KEY_OAUTH_TOKEN)
            resource_owner_secret = oauth_tokens.get(Constants.KEY_OAUTH_TOKEN_SECRET)

            # Persist OAuth key and secret
            with open(self.oauth_config.get(Constants.KEY_OAUTH_ACCESS_TOKEN_PATH), "w") as key_file:
                key_file.write(resource_owner_key + "\n")
                key_file.write(resource_owner_secret + "\n")

        return OAuth1Session(client_key=self.oauth_config.get(Constants.KEY_OAUTH_CLIENT_KEY),
                             client_secret=self.oauth_config.get(Constants.KEY_OAUTH_CLIENT_SECRET),
                             resource_owner_key=resource_owner_key,
                             resource_owner_secret=resource_owner_secret)


