from requests_oauthlib import OAuth1Session
from experiment_automator.constants import OAuthConstants
from experiment_automator.exceptions import OAuthException
from experiment_automator.utils import DebugLogCat
from os.path import exists


class OAuthClient:
    def __init__(self, debug, oauth_config):
        self.debug = debug
        self.oauth_config = oauth_config

        self.__check_config(OAuthConstants.KEY_OAUTH_SERVICE_NAME)
        self.__check_config(OAuthConstants.KEY_OAUTH_CLIENT_KEY)
        self.__check_config(OAuthConstants.KEY_OAUTH_CLIENT_SECRET)
        self.__check_config(OAuthConstants.KEY_OAUTH_REQUEST_TOKEN_URL)
        self.__check_config(OAuthConstants.KEY_OAUTH_ACCESS_TOKEN_URL)
        self.__check_config(OAuthConstants.KEY_OAUTH_AUTHORIZATION_URL)
        self.__check_config(OAuthConstants.KEY_OAUTH_BASE_URL)
        self.__check_config(OAuthConstants.KEY_OAUTH_ACCESS_TOKEN_PATH)

    def __class_name(self):
        return self.__class__.__name__

    def __check_config(self, config):
        if self.oauth_config.get(config, None) is None:
            raise OAuthException("%s - OAuth config %s is None. Please set in config!" % (self.__class_name(), config))

    def connect(self, callback, **params):
        global resource_owner_key
        global resource_owner_secret

        DebugLogCat.log(self.debug, self.__class_name(), "Getting authentication...")

        # If persist read oauth tokens from file
        if exists(self.oauth_config.get(OAuthConstants.KEY_OAUTH_ACCESS_TOKEN_PATH)):
            DebugLogCat.log(self.debug, self.__class_name(), "User already authenticated. Read tokens from file...")

            with open(self.oauth_config.get(OAuthConstants.KEY_OAUTH_ACCESS_TOKEN_PATH), "r") as key_file:
                resource_owner_key = key_file.readline().strip()
                resource_owner_secret = key_file.readline().strip()
        else:
            DebugLogCat.log(self.debug, self.__class_name(), "Getting request tokens from request token url...")

            oauth = OAuth1Session(client_key=self.oauth_config.get(OAuthConstants.KEY_OAUTH_CLIENT_KEY),
                                  client_secret=self.oauth_config.get(OAuthConstants.KEY_OAUTH_CLIENT_SECRET),
                                  callback_uri=callback)
            tokens = oauth.fetch_request_token(self.oauth_config.get(OAuthConstants.KEY_OAUTH_REQUEST_TOKEN_URL))
            resource_owner_key = tokens.get(OAuthConstants.KEY_OAUTH_TOKEN)
            resource_owner_secret = tokens.get(OAuthConstants.KEY_OAUTH_TOKEN_SECRET)

            DebugLogCat.log(self.debug, self.__class_name(), "User will be redirected to authorize the application...")

            authorization_url = oauth.authorization_url(self.oauth_config.get(OAuthConstants.KEY_OAUTH_AUTHORIZATION_URL), **params)
            print("Visit this URL in your browser for service \"{service_name}\": {url}".format(
                    service_name=self.oauth_config.get(OAuthConstants.KEY_OAUTH_SERVICE_NAME),
                    url=authorization_url))
            oauth_verifier = input("Enter PIN from browser: ")

            DebugLogCat.log(self.debug, self.__class_name(), "Getting access tokens from access token url...")

            oauth = OAuth1Session(client_key=self.oauth_config.get(OAuthConstants.KEY_OAUTH_CLIENT_KEY),
                                  client_secret=self.oauth_config.get(OAuthConstants.KEY_OAUTH_CLIENT_SECRET),
                                  resource_owner_key=resource_owner_key,
                                  resource_owner_secret=resource_owner_secret,
                                  verifier=oauth_verifier)

            oauth_tokens = oauth.fetch_access_token(self.oauth_config.get(OAuthConstants.KEY_OAUTH_ACCESS_TOKEN_URL))
            resource_owner_key = oauth_tokens.get(OAuthConstants.KEY_OAUTH_TOKEN)
            resource_owner_secret = oauth_tokens.get(OAuthConstants.KEY_OAUTH_TOKEN_SECRET)

            DebugLogCat.log(self.debug, self.__class_name(), "Persist tokens in specified path...")

            # Persist OAuth key and secret
            with open(self.oauth_config.get(OAuthConstants.KEY_OAUTH_ACCESS_TOKEN_PATH), "w") as key_file:
                key_file.write(resource_owner_key + "\n")
                key_file.write(resource_owner_secret + "\n")

            DebugLogCat.log(self.debug, self.__class_name(), "Session established!")

        return OAuth1Session(client_key=self.oauth_config.get(OAuthConstants.KEY_OAUTH_CLIENT_KEY),
                             client_secret=self.oauth_config.get(OAuthConstants.KEY_OAUTH_CLIENT_SECRET),
                             resource_owner_key=resource_owner_key,
                             resource_owner_secret=resource_owner_secret)


